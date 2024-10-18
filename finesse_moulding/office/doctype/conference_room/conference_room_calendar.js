// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

frappe.views.calendar["Conference Room"] = {
	field_map: {
		start: "time_in",
		end: "time_out",
		id: "name",
		title: "room",
	},
	get_events_method: "frappe.desk.calendar.get_events",
};
