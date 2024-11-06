// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// -------------------- Hide sidebar ----------------------------
frappe.ui.form.on('FJ Job List', {
	refresh: function(me) {
    		me.page.sidebar.remove(); // this removes the sidebar
    		me.page.wrapper.find(".layout-main-section-wrapper").removeClass("col-md-10"); // this removes class "col-md-10" from content block, which sets width to 83%
    	} 
}
);
// -------------------------------------------------------------------------

// -------------------- Remove new email button ----------------------------
frappe.ui.form.on('FJ Job List', {
	refresh(frm) {
		document.getElementsByClassName("timeline-items timeline-actions")[0].style.display = "none";
	}
});
// -------------------------------------------------------------------------

// -------------------- Remove comment button ----------------------------
frappe.ui.form.on('FJ Job List', {
    refresh: function(frm) {
        frm.page.wrapper.find(".comment-box").css({'display':'none'});
    }
});
// -------------------------------------------------------------------------
