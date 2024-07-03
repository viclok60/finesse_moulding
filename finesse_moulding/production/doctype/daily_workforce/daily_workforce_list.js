// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// -------------------- Remove likes ----------------------------
frappe.listview_settings['Daily Workforce'] = {
    refresh: function(listview) {
        // Remove likes
        $("use.like-icon").hide();
        
        // Remove bulk edit
        listview.page.actions.find('[data-label="Edit"],[data-label="Assign To"]').parent().parent().remove();

        // Hide sidebar
        $('span.sidebar-toggle-btn').hide();
        $('.col-lg-2.layout-side-section').hide();
    }
};
// -------------------------------------------------------------------------
