import frappe

def get_context(context):
    query = frappe.form_dict.get("q")
    if query:
        # Search for Repair Order by name or Serial/IMEI of linked device
        orders = frappe.get_all("Repair Order", 
            filters=[
                ["name", "=", query],
                "or",
                ["device", "in", frappe.get_all("Repair Device", filters={"serial_no_imei": query}, pluck="name")]
            ],
            fields=["name", "status", "customer", "device", "estimated_completion_date"]
        )
        if orders:
            order = orders[0]
            context.repair_order = order
            context.device = frappe.get_doc("Repair Device", order.device)
        else:
            context.error = "No repair order found with the provided ID or Serial/IMEI."
    return context
