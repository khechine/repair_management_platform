import frappe
from frappe.model.document import Document

class DiagnosticReport(Document):
    def after_insert(self):
        self.create_diagnostic_checklist()

    def create_diagnostic_checklist(self):
        """
        Automatically create a Diagnostic Checklist based on the Repair Order's industry/device type.
        """
        repair_order = frappe.get_doc("Repair Order", self.repair_order)
        device = frappe.get_doc("Repair Device", repair_order.device)
        
        # Find a suitable template
        template_name = frappe.db.get_value("Diagnostic Checklist Template", 
            {"industry": device.industry, "active": 1}, "name")
        
        if not template_name:
            # Fallback to any active template if industry-specific one is not found
            template_name = frappe.db.get_value("Diagnostic Checklist Template", 
                {"active": 1}, "name")

        if template_name:
            template = frappe.get_doc("Diagnostic Checklist Template", template_name)
            
            checklist = frappe.new_doc("Diagnostic Checklist")
            checklist.repair_order = self.repair_order
            checklist.template = template_name
            checklist.technician = self.technician
            
            for item in template.items:
                checklist.append("results", {
                    "item_name": item.item_name,
                    "mandatory": item.mandatory,
                    "status": "N/A"
                })
            
            checklist.insert()
            
            # Link checklist back to report
            self.db_set("checklist", checklist.name)
            frappe.msgprint(f"Diagnostic Checklist {checklist.name} created from template {template_name}")
