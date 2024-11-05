// Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Bidor Daily Timesheet"] = {
	"filters": [
        {
            "fieldname": "date",
            "label": __("Date"),
            "fieldtype": "Date",
            "reqd": 1,
            "default": frappe.datetime.get_today()
        },
    ]
};
