// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// ---------------- Validate department ----------------------------
frappe.ui.form.on('Conference Room', {
    validate: function (frm) {
        var all = frm.doc.all_department;
        var pm = frm.doc.pm;
        var fin = frm.doc.fin;
        var mkt = frm.doc.mkt;
        var pe = frm.doc.pe;
        var hr = frm.doc.hr;
        var it = frm.doc.it;
        var sc = frm.doc.sc;
        var esh = frm.doc.esh;
        var qa = frm.doc.qa;
        var dir = frm.doc.dir;
	var om = frm.doc.om;

        // Check if at least one field is checked
        if (!(all || pm || fin || mkt || pe || hr || it || sc || esh || qa || dir || om)) {
            frappe.msgprint({
                title: __('Data Entry Error'),
                indicator: 'red',
                message: __('At least one department must be selected'),
            });
            frappe.validated = false;
            return;
        }

        // Check if "all" is checked then no other field should be checked
        if (all && (pm || fin || mkt || pe || hr || it || sc || esh || qa || dir || om)) {
            frappe.msgprint({
                title: __('Data Entry Error'),
                indicator: 'red',
                message: __('If "All Departments" is selected, no other department should be selected'),
            });
            frappe.validated = false;
        }
    }
});
// ------------------------------------------------------------

// ---------------- Validate conference room booking ----------------------------
frappe.ui.form.on('Conference Room', {
    validate: function (frm) {
        // Get the selected date and branch from the form
        var selectedIn = frm.doc.time_in;
        var selectedOut = frm.doc.time_out;
	var selectedRoom = frm.doc.room;
        
        // Check if another Conference room entry exists with the room and later time_in
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Conference Room',
                fields: ['name', 'time_in', 'time_out'],
                filters: {
		    room: selectedRoom,	
                    time_in: ['<', selectedOut],
                    time_out: ['>', selectedIn],
                    name: ['!=', frm.doc.name]
                }
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    var overlappingBooking = r.message[0];

                    // Show an error message and prevent saving the form
                    frappe.msgprint({
                        title: __('Conference Room in Use'),
                        indicator: 'red',
                        message: __('The Conference Room is already booked from {0} to {1}. Please select another time range.', [overlappingBooking.time_in, overlappingBooking.time_out]),
                        raise: true
                    });
                    frappe.validated = false;
                }
            }
        });
    }
});
// ------------------------------------------------------------

// ---------------- Validate time conference room ----------------------------
frappe.ui.form.on('Conference Room', {
    validate: function (frm) {
        var selectedOut = frm.doc.time_out;
        var selectedIn = frm.doc.time_in;
        
        if (selectedIn > selectedOut) {
            frappe.msgprint({
                title: __('Data Entry Error'),
                indicator: 'red',
                message: __('Time Out must be later than Time In'),
            });
            frappe.validated = false;
        }
    }
});
// ------------------------------------------------------------

// ---------------- Hide sidebar conference room ----------------------------
frappe.ui.form.on('Conference Room', {
	refresh: function(me) {
    		me.page.sidebar.remove(); // this removes the sidebar
    		me.page.wrapper.find(".layout-main-section-wrapper").removeClass("col-md-10"); // this removes class "col-md-10" from content block, which sets width to 83%
    	} 
}
);
// ------------------------------------------------------------

// ---------------- Remove new email ----------------------------
frappe.ui.form.on('Conference Room', {
	refresh(frm) {
		document.getElementsByClassName("timeline-items timeline-actions")[0].style.display = "none";
	}
});
// ------------------------------------------------------------

// ---------------- Remove comment ----------------------------
frappe.ui.form.on('Conference Room', {
	refresh: function(frm) {
        frm.page.wrapper.find(".comment-box").css({'display':'none'});
    }
});
// ------------------------------------------------------------
