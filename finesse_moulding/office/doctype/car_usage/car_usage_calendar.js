// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

frappe.views.calendar["Car Usage"] = {
	field_map: {
		start: "time_out",
		end: "time_in",
		id: "name",
		title: "car_model",
	},
	get_events_method: "frappe.desk.calendar.get_events",
};
