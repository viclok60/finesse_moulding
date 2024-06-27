// Copyright (c) 2024, Victor and contributors
// For license information, please see license.txt

// -------------------- Fetch branch employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
  branch: function(frm) {
    if (frm.doc.branch) {
      // Query to fetch all employees from the selected branch
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Employee',
          filters: {
            branch: frm.doc.branch,
            status: 'Active' // Filter employees with status "Active"
          },
          fields: ['employee_name', 'employee_number'],
          limit_page_length: null, // Fetch all records without pagination
          order_by: 'employee_name' // Order by employee_name column
        },
        callback: function(response) {
          if (response.message) {
            frm.clear_table('branch_employee1'); // Clear existing rows in the table
            response.message.forEach(function(employee) {
              var row = frm.add_child('branch_employee1');
              row.employee_name = employee.employee_name;
              row.employee_number = employee.employee_number;
            });
            frm.refresh_field('branch_employee1'); // Refresh the table to display the updated rows
          }
        }
      });
    }
  }
});
// -------------------------------------------------------------------------

// -------------------- Fetch branch employees ----------------------------
frappe.ui.form.on('Daily Workforce', {
  branch: function(frm) {
    if (frm.doc.branch) {
      // Query to fetch all employees from the selected branch
      frappe.call({
        method: 'frappe.client.get_list',
        args: {
          doctype: 'Employee',
          filters: {
            branch: frm.doc.branch,
            status: 'Active' // Filter employees with status "Active"
          },
          fields: ['employee_name', 'employee_number'],
          limit_page_length: null, // Fetch all records without pagination
          order_by: 'employee_name' // Order by employee_name column
        },
        callback: function(response) {
          if (response.message) {
            frm.clear_table('branch_employee'); // Clear existing rows in the table
            response.message.forEach(function(employee) {
              var row = frm.add_child('branch_employee');
              row.employee_name = employee.employee_name;
              row.employee_number = employee.employee_number;
            });
            frm.refresh_field('branch_employee'); // Refresh the table to display the updated rows
          }
        }
      });
    }
  }
});
// -------------------------------------------------------------------------

// -------------------- Remove delete button on branch employees ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh(frm) {
        $('[data-fieldname="branch_employee"]').find('.grid-remove-all-rows').hide();
        $('[data-fieldname="branch_employee"]').find('.grid-delete-row').hide();
        $('*[data-fieldname="branch_employee"]').find('.grid-remove-rows').hide();
    },
    
});

frappe.ui.form.on('Daily Workforce', {
	refresh(frm) {
		// your code here
		
	},
	
    form_render(frm, cdt, cdn){
        frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
    }
});
// -------------------------------------------------------------------------

// -------------------- Remove delete button on branch employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh(frm) {
        $('[data-fieldname="branch_employee1"]').find('.grid-remove-all-rows').hide();
        $('[data-fieldname="branch_employee1"]').find('.grid-delete-row').hide();
        $('*[data-fieldname="branch_employee1"]').find('.grid-remove-rows').hide();
    },
    
});

frappe.ui.form.on('Daily Workforce', {
	refresh(frm) {
		// your code here
		
	},
	
    form_render(frm, cdt, cdn){
        frm.fields_dict.items.grid.wrapper.find('.grid-delete-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-duplicate-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-move-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-append-row').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row-below').hide();
        frm.fields_dict.items.grid.wrapper.find('.grid-insert-row').hide();
    }
});
// -------------------------------------------------------------------------

// -------------------- Validate time out and transfer end ----------------------------
frappe.ui.form.on('Daily Workforce', {
    validate: function (frm) {
        var errorRows = [];
        var errorRows1 = [];
        var errorRows2 = [];
        var errorRows3 = [];
        var errorRows4 = [];

        // First condition
        frm.doc.branch_employee.forEach(function (row, idx) {
            if (row.time_out < row.transfer_end) {
                errorRows.push(idx + 1); // Adding 1 to make it 1-based index
            }
        });

        // Second condition
        frm.doc.branch_employee.forEach(function (row, idx) {
            frm.doc.branch_employee1.forEach(function (row1, idx1) {
                // Check the condition for both fields
                if (idx === idx1 && row1.transfer_start2 !== null && row1.transfer_start2 !== '' && row1.transfer_start2 < row.transfer_end) {
                    errorRows1.push(idx1 + 1);
                }
            });
        });
        
        // Third condition
        frm.doc.branch_employee1.forEach(function (row, idx) {
            if (row.transfer_start3 !== null && row.transfer_start3 !== '' && row.transfer_start3 < row.transfer_end2) {
                errorRows2.push(idx + 1); // Adding 1 to make it 1-based index
            }
        });
        
        // Fourth condition
        frm.doc.branch_employee.forEach(function (row, idx) {
            frm.doc.branch_employee1.forEach(function (row1, idx1) {
                // Check the condition for both fields
                if (idx === idx1 && row.time_out < row1.transfer_end2) {
                    errorRows3.push(idx + 1);
                }
            });
        });
        
        // Fifth condition
        frm.doc.branch_employee.forEach(function (row, idx) {
            frm.doc.branch_employee1.forEach(function (row1, idx1) {
                // Check the condition for both fields
                if (idx === idx1 && row.time_out < row1.transfer_end3) {
                    errorRows4.push(idx + 1);
                }
            });
        });

        // Display messages for both conditions
        if (errorRows.length > 0 || errorRows1.length > 0 || errorRows2.length > 0 || errorRows3.length > 0 || errorRows4.length > 0) {
            var message = '';

            if (errorRows.length > 0) {
                message += __('Time Out must not be earlier than (1)Transfer End in rows: {0}', [errorRows.join(', ')]);
            }

            if (errorRows1.length > 0) {
                if (message !== '') {
                    message += '<br>';
                }
                message += __('(2)Transfer Start must not be earlier than (1)Transfer End in rows: {0}', [errorRows1.join(', ')]);
            }
            
            if (errorRows2.length > 0) {
                if (message !== '') {
                    message += '<br>';
                }
                message += __('(3)Transfer Start must not be earlier than (2)Transfer End in rows: {0}', [errorRows2.join(', ')]);
            }
            
            if (errorRows3.length > 0) {
                if (message !== '') {
                    message += '<br>';
                }
                message += __('Time Out must not be earlier than (2)Transfer End in rows: {0}', [errorRows3.join(', ')]);
            }
            
            if (errorRows4.length > 0) {
                if (message !== '') {
                    message += '<br>';
                }
                message += __('Time Out must not be earlier than (3)Transfer End in rows: {0}', [errorRows4.join(', ')]);
            }

            frappe.msgprint({
                title: __('Time Error'),
                indicator: 'red',
                message: message
            });

            frappe.validated = false;
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Validate transfer start and transfer end ----------------------------
frappe.ui.form.on('Daily Workforce', {
    validate: function (frm) {
        var errorRows = [];
        frm.doc.branch_employee.forEach(function (row, idx) {
            if (row.transfer_end < row.transfer_start) {
                errorRows.push(idx + 1); // Adding 1 to make it 1-based index
            }
        });

        var errorRows1 = [];
        frm.doc.branch_employee1.forEach(function (row, idx) {
            if (row.transfer_end2 < row.transfer_start2) {
                errorRows1.push(idx + 1); // Adding 1 to make it 1-based index
            }
        });

        var errorRows2 = [];
        frm.doc.branch_employee1.forEach(function (row, idx) {
            if (row.transfer_end3 < row.transfer_start3) {
                errorRows2.push(idx + 1); // Adding 1 to make it 1-based index
            }
        });

        if (errorRows.length > 0 || errorRows1.length > 0 || errorRows2.length > 0) {
            var errorMessage = '';

            if (errorRows.length > 0) {
                errorMessage += __('(1)Transfer End must not be earlier than (1)Transfer Start in rows: {0}', [errorRows.join(', ')]);
            }

            if (errorRows1.length > 0) {
                if (errorMessage !== '') {
                    errorMessage += '<br>';
                }
                errorMessage += __('(2)Transfer End must not be earlier than (2)Transfer Start in rows: {0}', [errorRows1.join(', ')]);
            }

            if (errorRows2.length > 0) {
                if (errorMessage !== '') {
                    errorMessage += '<br>';
                }
                errorMessage += __('(3)Transfer End must not be earlier than (3)Transfer Start in rows: {0}', [errorRows2.join(', ')]);
            }

            frappe.msgprint({
                title: __('Time Error'),
                indicator: 'red',
                message: errorMessage
            });
            frappe.validated = false;
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Remove edit wheel on branch employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function (frm, cdt, cdn) {
        // Define the function to apply the CSS rule
        function applyCSSRule() {
            var gridWrapper = frm.fields_dict['branch_employee1'].$wrapper.find('.grid-row>.row .col:last-child, .form-section .grid-row>.section-body .col:last-child, .form-dashboard-section .grid-row>.section-body .col:last-child, .grid-row>.dialog-assignment-row .col:last-child');
            var gridWrapperEdit = frm.fields_dict['branch_employee1'].$wrapper.find('.btn-open-row');
            // Add a CSS rule to disable pointer events
            gridWrapper.css('pointer-events', 'none');
            gridWrapperEdit.css('pointer-events', 'none');
        }

        // Call the function when the page loads
        applyCSSRule();

        // Call the function when the table refreshes
        frm.fields_dict['branch_employee1'].$wrapper.on('change', function () {
            applyCSSRule();
        });
    }
});
// -------------------------------------------------------------------------

// -------------------- Remove edit wheel on branch employees ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function (frm, cdt, cdn) {
        // Define the function to apply the CSS rule
        function applyCSSRule() {
            var gridWrapper = frm.fields_dict['branch_employee'].$wrapper.find('.grid-row>.row .col:last-child, .form-section .grid-row>.section-body .col:last-child, .form-dashboard-section .grid-row>.section-body .col:last-child, .grid-row>.dialog-assignment-row .col:last-child');
            var gridWrapperEdit = frm.fields_dict['branch_employee'].$wrapper.find('.btn-open-row');
            // Add a CSS rule to disable pointer events
            gridWrapper.css('pointer-events', 'none');
            gridWrapperEdit.css('pointer-events', 'none');
        }

        // Call the function when the page loads
        applyCSSRule();

        // Call the function when the table refreshes
        frm.fields_dict['branch_employee'].$wrapper.on('change', function () {
            applyCSSRule();
        });
    }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------

// -------------------- Fetch Branch Employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
	// refresh: function(frm) {

	// }
});
// -------------------------------------------------------------------------
