// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// ---------------- Hide Edit Button ----------------------------
frappe.listview_settings['Car Usage'] = {
    refresh: function(listview) {
        listview.page.actions.find('[data-label="Edit"],[data-label="Assign To"]').parent().parent().remove();
	
	// Hide Sidebar
	$('span.sidebar-toggle-btn').hide();
        $('.col-lg-2.layout-side-section').hide();

    }
};
// ------------------------------------------------------------
