import frappe
from frappe import _
from frappe.utils import flt

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data, filters)
    return columns, data, None, chart

def get_columns():
    return [
        {
            "fieldname": "technician",
            "label": _("Technician"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 180
        },
        {
            "fieldname": "total_assigned",
            "label": _("Total Assigned"),
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "completed",
            "label": _("Completed"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "in_progress",
            "label": _("In Progress"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "completion_rate",
            "label": _("Completion Rate %"),
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "avg_turnaround_days",
            "label": _("Avg Turnaround (Days)"),
            "fieldtype": "Float",
            "precision": 2,
            "width": 150
        },
        {
            "fieldname": "total_revenue",
            "label": _("Total Revenue"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "avg_order_value",
            "label": _("Avg Order Value"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "urgent_repairs",
            "label": _("Urgent Repairs"),
            "fieldtype": "Int",
            "width": 100
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            IFNULL(ro.technician, 'Unassigned') as technician,
            COUNT(ro.name) as total_assigned,
            SUM(CASE WHEN ro.status = 'Completed' THEN 1 ELSE 0 END) as completed,
            SUM(CASE WHEN ro.status IN ('Repair in Progress', 'Diagnostic Pending', 'Diagnostic Completed', 'Quoted') THEN 1 ELSE 0 END) as in_progress,
            AVG(CASE WHEN ro.status = 'Completed' THEN ro.turnaround_time_days END) as avg_turnaround_days,
            SUM(IFNULL(ro.total_amount, 0)) as total_revenue,
            SUM(CASE WHEN ro.priority = 'Urgent' THEN 1 ELSE 0 END) as urgent_repairs
        FROM
            `tabRepair Order` ro
        WHERE
            ro.docstatus < 2
            {conditions}
        GROUP BY
            ro.technician
        ORDER BY
            completed DESC, total_revenue DESC
    """.format(conditions=conditions), filters, as_dict=1)

    # Calculate derived fields
    for row in data:
        if flt(row.total_assigned) > 0:
            row.completion_rate = (flt(row.completed) / flt(row.total_assigned)) * 100
            row.avg_order_value = flt(row.total_revenue) / flt(row.total_assigned)
        else:
            row.completion_rate = 0
            row.avg_order_value = 0

    return data

def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("DATE(ro.creation) >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("DATE(ro.creation) <= %(to_date)s")

    if filters.get("technician"):
        conditions.append("ro.technician = %(technician)s")

    if filters.get("industry"):
        conditions.append("ro.industry = %(industry)s")

    return " AND " + " AND ".join(conditions) if conditions else ""

def get_chart_data(data, filters):
    # Filter out 'Unassigned' for better visualization
    chart_data = [d for d in data if d.get("technician") != "Unassigned"][:10]  # Top 10 technicians

    labels = [d.get("technician") for d in chart_data]
    completed_values = [d.get("completed") for d in chart_data]
    revenue_values = [d.get("total_revenue") for d in chart_data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Completed Repairs",
                    "values": completed_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#29CD42"]
    }
