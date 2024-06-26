// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// ----------------------------- Validate mileage -----------------------------------
frappe.ui.form.on('Car Usage', {
    validate: function (frm) {
        var currentMileage = frm.doc.mileage;
        var selectedModel = frm.doc.car_model;
        
        // Skip validation if currentMileage is 0
        if (currentMileage === 0) {
            return;
        }
        
        // Check if another Car Usage entry exists with the same car model and later mileage
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Car Usage',
                fields: ['name', 'mileage'],
                filters: {
                    car_model: selectedModel,
                    mileage: ['>', currentMileage],
                    name: ['!=', frm.doc.name]
                }
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    // Get the mileage value from the first record in the returned list
                    var previousMileage = r.message[0].mileage;

                    // Show an error message and prevent saving the form
                    frappe.msgprint({
                        title: __('Mileage Error'),
                        indicator: 'red',
                        message: __('The previous mileage is {0}. Please change your mileage to a higher value.', [previousMileage])
                    });
                    frappe.validated = false;
                }
            }
        });
    }
});
// ----------------------------------------------------------------------------------

// ----------------------------- Validate model -----------------------------------
frappe.ui.form.on('Car Usage', {
    validate: function (frm) {
        // Get the selected date and branch from the form
        var selectedOut = frm.doc.time_out;
        var selectedIn = frm.doc.time_in;
        var selectedModel = frm.doc.car_model;
        
        // Check if another Car Usage entry exists with the same car model and later time_in
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Car Usage',
                fields: ['name', 'time_in'],
                filters: {
                    car_model: selectedModel,
                    time_in: ['>', selectedOut],
                    time_out: ['<', selectedIn],
                    name: ['!=', frm.doc.name]
                }
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    // Get the time_in value from the first record in the returned list
                    var timeIn = r.message[0].time_in;

                    // Show an error message and prevent saving the form
                    frappe.msgprint({
                        title: __('Car In Use'),
                        indicator: 'red',
                        message: __('This Car is in use until {0}, please select another Car Model or change your time.', [timeIn]),
                        raise: true
                    });
                    frappe.validated = false;
                }
            }
        });
    }
});
// ---------------------------------------------------------------------------------

// ----------------------------- Calculate distance travelled -----------------------------------
frappe.ui.form.on('Car Usage', {
    before_save: function (frm) {
        var currentMileage = frm.doc.mileage;
        var selectedModel = frm.doc.car_model;

        // Calculate the distance if validation passes
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Car Usage',
                fields: ['name', 'mileage'],
                filters: {
                    car_model: selectedModel,
                    mileage: ['<', currentMileage],
                    name: ['!=', frm.doc.name]
                },
                order_by: 'mileage desc',
                limit: 1
            },
            callback: function (res) {
                if (res.message && res.message.length > 0) {
                    var previousMileage = res.message[0].mileage;
                    var distance = currentMileage - previousMileage;
                    frm.set_value('distance', distance);
                } else {
                    // If no previous record is found, set distance to zero or handle as needed
                    frm.set_value('distance', 0);
                }
            }
        });
    }
});
// ---------------------------------------------------------------------------------

// ----------------------------- Hide sidebar -----------------------------------
frappe.ui.form.on('Car Usage', {
	refresh: function(me) {
    		me.page.sidebar.remove(); // this removes the sidebar
    		me.page.wrapper.find(".layout-main-section-wrapper").removeClass("col-md-10"); // this removes class "col-md-10" from content block, which sets width to 83%
    	} 
}
);
// ---------------------------------------------------------------------------------

// ----------------------------- Remove new email button -----------------------------------
frappe.ui.form.on('Car Usage', {
	refresh(frm) {
		document.getElementsByClassName("timeline-items timeline-actions")[0].style.display = "none";
	}
})
// ---------------------------------------------------------------------------------

// ----------------------------- Validate time -----------------------------------
frappe.ui.form.on('Car Usage', {
    validate: function (frm) {
        var selectedOut = frm.doc.time_out;
        var selectedIn = frm.doc.time_in;
        
        if (selectedIn < selectedOut) {
            frappe.msgprint({
                title: __('Data Entry Error'),
                indicator: 'red',
                message: __('Time In must be later than Time Out'),
            });
            frappe.validated = false;
        }
    }
});
// ---------------------------------------------------------------------------------

// ----------------------------- Remove comment button -----------------------------------
frappe.ui.form.on('Car Usage', {
	refresh: function(frm) {
        frm.page.wrapper.find(".comment-box").css({'display':'none'});
    }
});
// ---------------------------------------------------------------------------------

// ----------------------------- Hide edit button -----------------------------------

// ---------------------------------------------------------------------------------

