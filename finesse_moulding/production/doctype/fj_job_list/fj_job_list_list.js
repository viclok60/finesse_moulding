// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt


frappe.listview_settings['FJ Job List'] = {
    refresh: function(listview) {	
	// Hide Sidebar
	$('span.sidebar-toggle-btn').hide();
        $('.col-lg-2.layout-side-section').hide();
        
        // Remove likes
        $("use.like-icon").hide();

    }
};
// ------------------------------------------------------------
