import frappe
from frappe import _
from frappe.utils import flt, getdate

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {
            "fieldname": "repair_order",
            "label": _("Repair Order"),
            "fieldtype": "Link",
            "options": "Repair Order",
            "width": 150
        },
        {
            "fieldname": "creation_date",
            "label": _("Creation Date"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "customer",
            "label": _("Customer"),
            "fieldtype": "Link",
            "options": "Customer",
            "width": 150
        },
        {
            "fieldname": "device",
            "label": _("Device"),
            "fieldtype": "Link",
            "options": "Repair Device",
            "width": 150
        },
        {
            "fieldname": "industry",
            "label": _("Industry"),
            "fieldtype": "Link",
            "options": "Industry Type",
            "width": 120
        },
        {
            "fieldname": "status",
            "label": _("Status"),
            "fieldtype": "Data",
            "width": 120
        },
        {
            "fieldname": "priority",
            "label": _("Priority"),
            "fieldtype": "Data",
            "width": 80
        },
        {
            "fieldname": "technician",
            "label": _("Technician"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 150
        },
        {
            "fieldname": "total_amount",
            "label": _("Total Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "paid_amount",
            "label": _("Paid Amount"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "balance",
            "label": _("Balance"),
            "fieldtype": "Currency",
            "width": 120
        },
        {
            "fieldname": "turnaround_time_days",
            "label": _("Turnaround (Days)"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "estimated_completion_date",
            "label": _("Est. Completion"),
            "fieldtype": "Date",
            "width": 100
        },
        {
            "fieldname": "actual_completion_date",
            "label": _("Actual Completion"),
            "fieldtype": "Date",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            ro.name as repair_order,
            DATE(ro.creation) as creation_date,
            ro.customer,
            ro.device,
            ro.industry,
            ro.status,
            ro.priority,
            ro.technician,
            ro.total_amount,
            ro.paid_amount,
            (ro.total_amount - IFNULL(ro.paid_amount, 0)) as balance,
            ro.turnaround_time_days,
            ro.estimated_completion_date,
            ro.actual_completion_date
        FROM
            `tabRepair Order` ro
        WHERE
            ro.docstatus < 2
            {conditions}
        ORDER BY
            ro.creation DESC
    """.format(conditions=conditions), filters, as_dict=1)

    return data

def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("DATE(ro.creation) >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("DATE(ro.creation) <= %(to_date)s")

    if filters.get("status"):
        conditions.append("ro.status = %(status)s")

    if filters.get("industry"):
        conditions.append("ro.industry = %(industry)s")

    if filters.get("technician"):
        conditions.append("ro.technician = %(technician)s")

    if filters.get("customer"):
        conditions.append("ro.customer = %(customer)s")

    if filters.get("priority"):
        conditions.append("ro.priority = %(priority)s")

    return " AND " + " AND ".join(conditions) if conditions else ""
