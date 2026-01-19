frappe.query_reports["Repair Analytics"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -3),
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 0
        },
        {
            "fieldname": "status",
            "label": __("Status"),
            "fieldtype": "Select",
            "options": "\nDraft\nDiagnostic Pending\nDiagnostic Completed\nQuoted\nRepair in Progress\nReady for Collection\nCompleted\nCancelled"
        },
        {
            "fieldname": "industry",
            "label": __("Industry"),
            "fieldtype": "Link",
            "options": "Industry Type"
        },
        {
            "fieldname": "technician",
            "label": __("Technician"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "customer",
            "label": __("Customer"),
            "fieldtype": "Link",
            "options": "Customer"
        },
        {
            "fieldname": "priority",
            "label": __("Priority"),
            "fieldtype": "Select",
            "options": "\nLow\nMedium\nHigh\nUrgent"
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "status") {
            if (value == "Completed") {
                value = "<span class='indicator-pill green'>" + value + "</span>";
            } else if (value == "Cancelled") {
                value = "<span class='indicator-pill red'>" + value + "</span>";
            } else if (value == "Repair in Progress") {
                value = "<span class='indicator-pill blue'>" + value + "</span>";
            } else if (value == "Ready for Collection") {
                value = "<span class='indicator-pill orange'>" + value + "</span>";
            }
        }

        if (column.fieldname == "priority") {
            if (value == "Urgent") {
                value = "<span class='indicator-pill red'>" + value + "</span>";
            } else if (value == "High") {
                value = "<span class='indicator-pill orange'>" + value + "</span>";
            } else if (value == "Medium") {
                value = "<span class='indicator-pill yellow'>" + value + "</span>";
            } else if (value == "Low") {
                value = "<span class='indicator-pill grey'>" + value + "</span>";
            }
        }

        return value;
    }
};
