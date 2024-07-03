// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// -------------------- Remove likes ----------------------------
frappe.listview_settings['Daily Workforce'] = {
	refresh: function(listview) {
	   	$("use.like-icon").hide();
	}
};
// -------------------------------------------------------------------------


