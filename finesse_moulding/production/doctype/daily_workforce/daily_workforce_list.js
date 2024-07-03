// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// -------------------- Remove likes ----------------------------
frappe.listview_settings['Daily Workforce'] = {
	refresh: function(listview) {
	   	$("use.like-icon").hide();
	}
};
// -------------------------------------------------------------------------

// -------------------- Remove bulk edit ----------------------------
frappe.listview_settings['Daily Workforce'] = {
    refresh: function(listview) {
        listview.page.actions.find('[data-label="Edit"],[data-label="Assign To"]').parent().parent().remove();
    }
};
// -------------------------------------------------------------------------
