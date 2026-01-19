frappe.query_reports["Technician Performance"] = {
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
            "fieldname": "technician",
            "label": __("Technician"),
            "fieldtype": "Link",
            "options": "Employee"
        },
        {
            "fieldname": "industry",
            "label": __("Industry"),
            "fieldtype": "Link",
            "options": "Industry Type"
        }
    ],
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        if (column.fieldname == "completion_rate") {
            if (data.completion_rate >= 80) {
                value = "<span style='color:green'>" + value + "</span>";
            } else if (data.completion_rate >= 60) {
                value = "<span style='color:orange'>" + value + "</span>";
            } else {
                value = "<span style='color:red'>" + value + "</span>";
            }
        }

        return value;
    }
};
