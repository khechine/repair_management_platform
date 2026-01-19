import frappe
from frappe.model.document import Document

class CustomerFeedback(Document):
    def validate(self):
        # Ensure the repair order is completed before feedback
        if self.repair_order:
            repair_order = frappe.get_doc("Repair Order", self.repair_order)
            if repair_order.status != "Completed":
                frappe.throw("Feedback can only be submitted for completed repairs")

    def after_insert(self):
        # Link feedback to the repair order
        if self.repair_order:
            frappe.db.set_value("Repair Order", self.repair_order, "has_feedback", 1)
