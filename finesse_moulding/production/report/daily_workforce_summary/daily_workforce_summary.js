// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Daily Workforce Summary"] = {
    "filters": [
        {
            "fieldname": "from_selected_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
        },
        {
            "fieldname": "to_selected_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
        },
        {
            "fieldname": "branch",
            "label": __("Branch"),
            "fieldtype": "Link",
            "options": "Branch",
            "on_change": function() {
                // Trigger the report refresh when the 'branch' filter changes
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "custom_weekend_dates",
            "label": __("Custom Weekend Dates"),
            "fieldtype": "MultiSelect",
            "options": [],
            "description": "Select specific dates to be treated as weekends."
        }
    ],
    get_query: function (filters) {
        return {
            filters: [
                {
                    fieldname: 'branch',
                    operator: 'like',
                    value: filters.branch
                },
                {
                    fieldname: 'date',
                    operator: 'between',
                    value: [
                        filters.from_selected_date,
                        filters.to_selected_date
                    ]
                },
                {
                    fieldname: 'custom_weekend_dates',
                    operator: 'in',
                    value: filters.custom_weekend_dates
                }
            ]
        };
    }
};

