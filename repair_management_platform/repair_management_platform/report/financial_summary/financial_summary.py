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
            "fieldname": "industry",
            "label": _("Industry"),
            "fieldtype": "Link",
            "options": "Industry Type",
            "width": 150
        },
        {
            "fieldname": "total_orders",
            "label": _("Total Orders"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "completed_orders",
            "label": _("Completed"),
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "total_revenue",
            "label": _("Total Revenue"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "parts_cost",
            "label": _("Parts Cost"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "labor_revenue",
            "label": _("Labor Revenue"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "gross_margin",
            "label": _("Gross Margin"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "margin_percentage",
            "label": _("Margin %"),
            "fieldtype": "Percent",
            "width": 100
        },
        {
            "fieldname": "collected_amount",
            "label": _("Collected"),
            "fieldtype": "Currency",
            "width": 150
        },
        {
            "fieldname": "outstanding_amount",
            "label": _("Outstanding"),
            "fieldtype": "Currency",
            "width": 150
        }
    ]

def get_data(filters):
    conditions = get_conditions(filters)

    data = frappe.db.sql("""
        SELECT
            IFNULL(ro.industry, 'Not Specified') as industry,
            COUNT(ro.name) as total_orders,
            SUM(CASE WHEN ro.status = 'Completed' THEN 1 ELSE 0 END) as completed_orders,
            SUM(IFNULL(ro.total_amount, 0)) as total_revenue,
            SUM(
                (SELECT SUM(IFNULL(rsp.amount, 0))
                 FROM `tabRepair Spare Part` rsp
                 WHERE rsp.parent = ro.name)
            ) as parts_cost,
            SUM(
                (SELECT SUM(IFNULL(rt.cost, 0))
                 FROM `tabRepair Task` rt
                 WHERE rt.parent = ro.name)
            ) as labor_revenue,
            (SUM(IFNULL(ro.total_amount, 0)) -
             SUM(
                (SELECT SUM(IFNULL(rsp.amount, 0))
                 FROM `tabRepair Spare Part` rsp
                 WHERE rsp.parent = ro.name)
            )) as gross_margin,
            SUM(IFNULL(ro.paid_amount, 0)) as collected_amount,
            (SUM(IFNULL(ro.total_amount, 0)) - SUM(IFNULL(ro.paid_amount, 0))) as outstanding_amount
        FROM
            `tabRepair Order` ro
        WHERE
            ro.docstatus < 2
            {conditions}
        GROUP BY
            ro.industry
        ORDER BY
            total_revenue DESC
    """.format(conditions=conditions), filters, as_dict=1)

    # Calculate margin percentage
    for row in data:
        if flt(row.total_revenue) > 0:
            row.margin_percentage = (flt(row.gross_margin) / flt(row.total_revenue)) * 100
        else:
            row.margin_percentage = 0

    return data

def get_conditions(filters):
    conditions = []

    if filters.get("from_date"):
        conditions.append("DATE(ro.creation) >= %(from_date)s")

    if filters.get("to_date"):
        conditions.append("DATE(ro.creation) <= %(to_date)s")

    if filters.get("industry"):
        conditions.append("ro.industry = %(industry)s")

    return " AND " + " AND ".join(conditions) if conditions else ""

def get_chart_data(data, filters):
    labels = [d.get("industry") for d in data]
    revenue_values = [d.get("total_revenue") for d in data]
    margin_values = [d.get("gross_margin") for d in data]

    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": "Total Revenue",
                    "values": revenue_values
                },
                {
                    "name": "Gross Margin",
                    "values": margin_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#29CD42", "#FFA00A"]
    }
