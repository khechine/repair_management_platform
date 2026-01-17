import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime

class DiagnosticChecklist(Document):
    def validate(self):
        self.calculate_completion()
        self.update_timestamps()

    def calculate_completion(self):
        if not self.results:
            self.completion_percentage = 0
            return

        total_items = len(self.results)
        completed_items = len([d for d in self.results if d.status in ["OK", "KO"]])
        
        self.completion_percentage = (completed_items / total_items) * 100
        
        if completed_items == total_items:
            self.completed_on = now_datetime()

    def update_timestamps(self):
        for row in self.results:
            if row.status in ["OK", "KO"] and not row.timestamp:
                row.timestamp = now_datetime()
