// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
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
            "fieldname": "public_holidays",
            "label": __("Public Holidays, YYYY-MM-DD format"),
            "fieldtype": "Data",
            "description": __("Enter a comma-separated list of dates in YYYY-MM-DD format."),
        }
    ],
    // Add a custom method to get the selected 'branch' value, date range, and public holidays
    get_query: function (filters) {
        var public_holidays_list = [];
        if (filters.public_holidays) {
            public_holidays_list = filters.public_holidays.split(",").map(function(dateStr) {
                return dateStr.trim();
            });
        }
        
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
                    fieldname: 'public_holiday',
                    operator: 'in',
                    value: public_holidays_list
                }
            ]
        };
    }
};
