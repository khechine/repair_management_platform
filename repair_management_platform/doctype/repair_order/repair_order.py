import frappe
from frappe.model.document import Document
from frappe import _, msgprint
from frappe.utils import flt

class RepairOrder(Document):
    def validate(self):
        self.validate_diagnostic_completion()
        self.calculate_spare_parts_totals()

    def on_submit(self):
        if self.status == "Completed":
            self.create_stock_entry()

    def calculate_spare_parts_totals(self):
        for item in self.spare_parts:
            item.amount = flt(item.qty) * flt(item.rate)

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
