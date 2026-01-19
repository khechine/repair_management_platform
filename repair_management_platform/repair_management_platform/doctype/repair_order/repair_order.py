import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.utils import flt, getdate, date_diff, now_datetime, time_diff_in_hours

class RepairOrder(Document):
    def validate(self):
        self.validate_diagnostic_completion()
        self.calculate_spare_parts_totals()
        self.calculate_total_amount()
        self.update_completion_tracking()
        self.auto_assign_sla()
        self.update_sla_status()

    def on_submit(self):
        if self.status == "Completed":
            self.create_stock_entry()

    def calculate_spare_parts_totals(self):
        for item in self.spare_parts:
            item.amount = flt(item.qty) * flt(item.rate)

    def calculate_total_amount(self):
        """Calculate total amount from tasks and spare parts"""
        total = 0

        # Sum up task costs
        if self.tasks:
            for task in self.tasks:
                total += flt(task.cost)

        # Sum up spare parts costs
        if self.spare_parts:
            for part in self.spare_parts:
                total += flt(part.amount)

        self.total_amount = total

    def update_completion_tracking(self):
        """Update completion date and turnaround time when status changes to Completed"""
        if self.status == "Completed" and not self.actual_completion_date:
            self.actual_completion_date = getdate()

            # Calculate turnaround time from creation to completion
            if self.creation:
                self.turnaround_time_days = date_diff(self.actual_completion_date, getdate(self.creation))

        # Clear completion data if status changed from Completed to something else
        if self.status != "Completed" and self.actual_completion_date:
            self.actual_completion_date = None
            self.turnaround_time_days = None

    def validate_diagnostic_completion(self):
        """
        Prevent moving to 'Quoted' or 'Repair in Progress' if mandatory checklist items are not OK.
        """
        if self.status in ["Quoted", "Repair in Progress"]:
            # Check for linked reports and checklists
            reports = frappe.get_all("Diagnostic Report", filters={"repair_order": self.name})
            if not reports:
                frappe.throw(_("A Diagnostic Report is required before moving to {0}").format(self.status))
            
            for report in reports:
                report_doc = frappe.get_doc("Diagnostic Report", report.name)
                if not report_doc.checklist:
                    frappe.throw(_("A completed Diagnostic Checklist is required for Report {0}").format(report.name))
                
                checklist = frappe.get_doc("Diagnostic Checklist", report_doc.checklist)
                for item in checklist.results:
                    if item.mandatory and item.status != "OK":
                        frappe.throw(_("Mandatory checklist item '{0}' must be marked as OK in checklist {1}")
                            .format(item.item_name, checklist.name))

    def create_stock_entry(self):
        """
        Automatically create a Stock Entry (Material Issue) for spare parts used.
        """
        if not self.spare_parts:
            return

        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.stock_entry_type = "Material Issue"
        stock_entry.repair_order = self.name # Assuming we add this field to Stock Entry via custom field or just reference in remarks
        
        for item in self.spare_parts:
            stock_entry.append("items", {
                "item_code": item.item_code,
                "s_warehouse": item.warehouse,
                "qty": item.qty,
                "basic_rate": item.rate,
                "t_warehouse": None
            })
        
        stock_entry.insert()
        stock_entry.submit()
        msgprint(_("Stock Entry {0} created for spare parts usage.").format(stock_entry.name))

    def auto_assign_sla(self):
        """Automatically assign SLA based on industry and priority"""
        if self.sla:
            return  # Already has SLA assigned

        # Find matching SLA
        filters = {}
        if self.industry:
            filters["industry"] = self.industry
        if self.priority:
            filters["priority"] = self.priority

        filters["is_active"] = 1

        sla = frappe.db.get_value("Repair SLA", filters, "name")

        if sla:
            self.sla = sla
        else:
            # Try to find a default SLA for the industry
            sla = frappe.db.get_value("Repair SLA", {
                "industry": self.industry,
                "is_active": 1,
                "priority": ""
            }, "name")
            if sla:
                self.sla = sla

    def update_sla_status(self):
        """Update SLA status based on elapsed time"""
        if not self.sla or self.status in ["Completed", "Cancelled"]:
            return

        sla_doc = frappe.get_doc("Repair SLA", self.sla)
        creation_time = self.creation
        current_time = now_datetime()

        hours_elapsed = time_diff_in_hours(current_time, creation_time)

        # Check SLA breach based on status
        if self.status in ["Draft", "Diagnostic Pending"]:
            target_hours = sla_doc.response_time_hours
        elif self.status in ["Diagnostic Completed", "Quoted"]:
            target_hours = sla_doc.diagnostic_time_hours
        elif self.status in ["Repair in Progress", "Ready for Collection"]:
            target_hours = sla_doc.repair_time_hours
        else:
            return

        # Calculate SLA status
        if hours_elapsed >= target_hours:
            self.sla_status = "Breached"
        elif hours_elapsed >= (target_hours * 0.8):  # 80% threshold
            self.sla_status = "At Risk"
        else:
            self.sla_status = "Within SLA"
