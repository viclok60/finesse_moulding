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
                frappe.query_report.refresh();
            }
        },
        {
            "fieldname": "public_holidays",
            "label": __("Public Holidays"),
            "fieldtype": "Data",
            "description": __("Enter public holidays in YYYY-MM-DD format"),
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
                    fieldname: 'public_holidays',
                    operator: '=',
                    value: filters.public_holidays
                }
            ]
        };
    }
};




