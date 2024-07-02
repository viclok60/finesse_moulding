// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Supervisor OT Hours"] = {
    "filters": [
        {
            "fieldname": "from_selected_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_start(),
            "reqd": 1,
        },
        {
            "fieldname": "to_selected_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.month_end(),
            "reqd": 1,
        },
        {
            "fieldname": "designation",
            "label": __("Position"),
            "fieldtype": "MultiSelect",
            "options": ["", "Chief Supervisor", "Supervisor", "Assistant Supervisor", "Junior Supervisor", "General Worker"],
            "on_change": function() {
                // Trigger the report refresh when the 'branch' filter changes
                frappe.query_report.refresh();
            }
        },
    ],
    // Add a custom method to get the selected 'branch' value and date range
    get_query: function (filters) {
        return {
            filters: [
                {
                    fieldname: 'designation',
                    operator: 'like',
                    value: filters.designation
                },
                {
                    fieldname: 'date',
                    operator: 'between',
                    value: [
                        filters.from_selected_date,
                        filters.to_selected_date
                    ]
                }
            ]
        };
    }
};

