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

// -------------------- Hide add row on branch employees 1 ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function(frm) {
        frm.get_field('branch_employee1').grid.cannot_add_rows = true;
        
        // Refresh the form after hiding the "Add Row" button
        if (!frm._refreshed) {
            frm._refreshed = true;
            frm.refresh();
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Hide add row on branch employees ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function(frm) {
        frm.get_field('branch_employee').grid.cannot_add_rows = true;
        
        // Refresh the form after hiding the "Add Row" button
        if (!frm._refreshed) {
            frm._refreshed = true;
            frm.refresh();
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Set off when no touch card ----------------------------
frappe.ui.form.on("Daily Workforce", {
  date: function(frm, cdt, cdn) {
    // Get the selected date from the 'date' field in Daily Workforce
    const selectedDate = frm.doc.date;
    
    // Loop through the 'branch_employee' child table rows
    frm.doc.branch_employee.forEach(row => {
      const employee = row.employee_number;
      let employeeOff = 1; // Default to 1 (employee is off)

      frappe.call({
        method: "frappe.client.get_list",
        args: {
          doctype: "Employee Checkin",
          filters: [
            ['time', '>=', selectedDate + ' 00:00:00'], // Start of selected date
            ['time', '<', selectedDate + ' 23:59:59'],   // End of selected date
            ['employee', '=', employee]
          ]
        },
        callback: function(response) {

          if (response.message && response.message.length > 0) {
            // If there are check-ins for this employee on the selected date, set employeeOff to 0 (employee is not off)
            employeeOff = 0;
          }

          // Set the 'employee_off' field in the 'branch_employee' child table
          frappe.model.set_value(row.doctype, row.name, 'employee_off', employeeOff);

        }
      });
    });
  }
});
// -------------------------------------------------------------------------

// -------------------- Auto set pending ----------------------------
frappe.ui.form.on('Daily Workforce', {
    after_save: function(frm) {
        const workflowState = frm.doc.workflow_state;
        const previousWorkflowState = frm.doc.__last_workflow_state || 'Pending';

        if (workflowState === 'Approved' && workflowState !== previousWorkflowState) {
            // Set the workflow_state to 'Pending' and reload the document
            frappe.db.set_value('Daily Workforce', frm.doc.name, 'workflow_state', 'Pending')
                .then(() => {
                    // Save the current workflow_state as the previous state
                    frm.doc.__last_workflow_state = workflowState;
                    frm.save_or_update();
                });
        }
    },
    onload: function(frm) {
        // Initialize the __last_workflow_state field when the form is loaded
        frm.doc.__last_workflow_state = frm.doc.workflow_state;
    }
});
// -------------------------------------------------------------------------

// -------------------- Clear rows when off ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function(frm) {
        frm.fields_dict['branch_employee'].grid.get_field('employee_off').get_query = function(doc, cdt, cdn) {
            return {
                filters: [
                    // Add any additional filters if needed
                ]
            };
        };
    }
});

frappe.ui.form.on('Branch Employee', {
    employee_off: function(frm, cdt, cdn) {
        var child = locals[cdt][cdn];
        
        if (child.employee_off === 1) {
            frappe.model.set_value(cdt, cdn, 'time_in', '');
            frappe.model.set_value(cdt, cdn, 'time_out', '');
            frappe.model.set_value(cdt, cdn, 'transfer_department', '');
            frappe.model.set_value(cdt, cdn, 'transfer_start', '');
            frappe.model.set_value(cdt, cdn, 'transfer_end', '');
        }
    }
});

frappe.ui.form.on('Daily Workforce', {
    validate: function(frm) {
        frm.doc.branch_employee.forEach(function(row) {
            if (row.employee_off === 1) {
                frappe.model.set_value(row.doctype, row.name, 'time_in', '');
                frappe.model.set_value(row.doctype, row.name, 'time_out', '');
                frappe.model.set_value(row.doctype, row.name, 'transfer_department', '');
                frappe.model.set_value(row.doctype, row.name, 'transfer_start', '');
                frappe.model.set_value(row.doctype, row.name, 'transfer_end', '');
            }
        });
    }
});
// -------------------------------------------------------------------------

// -------------------- Prevent blank form ----------------------------
frappe.ui.form.on('Daily Workforce', {
    validate: function (frm) {
        let invalidRows = [];

        frm.doc.branch_employee.forEach(function (row, index) {
            if (row.employee_off !== 1 && (!row.time_in || !row.time_out)) {
                invalidRows.push(index + 1); // Adding 1 to index to display row number starting from 1 instead of 0
            }
        });

        if (invalidRows.length > 0) {
            let errorMessage = 'Form cannot save with empty rows: ' + invalidRows.join(', ');

            frappe.msgprint({
                message: errorMessage,
                indicator: 'red',
            });

            frappe.validated = false; // Prevent form submission
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Prevent duplicate form ----------------------------
frappe.ui.form.on('Daily Workforce', {
    validate: function (frm) {
        // Get the selected date and branch from the form
        var selectedDate = frm.doc.date;
        var selectedBranch = frm.doc.branch;

        // Check if another Daily Workforce entry exists with the same date and branch
        frappe.call({
            method: 'frappe.client.get_list',
            args: {
                doctype: 'Daily Workforce',
                fields: ['name'],
                filters: {
                    date: selectedDate,
                    branch: selectedBranch,
                    name: ['!=', frm.doc.name] // Exclude the current document if being updated
                }
            },
            callback: function (r) {
                if (r.message && r.message.length > 0) {
                    // Show an error message and prevent saving the form
                    frappe.msgprint({
                        title: __('Duplicate Entry'),
                        indicator: 'red',
                        message: __('Another Daily Workforce entry with the same date and branch already exists.'),
                        raise: true
                    });
                    frappe.validated = false;
                }
            }
        });
    }
});
// -------------------------------------------------------------------------

// -------------------- Validate all columns when off ----------------------------
frappe.ui.form.on('Daily Workforce', {
    validate: function (frm) {
        var error_occurred = false;
        var error_rows = [];

        frm.doc.branch_employee.forEach(function (row) {
            if (row.employee_off === 1) {
                if (row.time_in || row.time_out || row.transfer_department || row.transfer_start || row.transfer_end) {
                    error_occurred = true;
                    error_rows.push(row.idx);
                }
            }
        });

        if (error_occurred) {
            frappe.msgprint({
                title: __('Input Error'),
                message: __('If Off is tick, all other fields in rows {0} must be empty.', [error_rows.join(', ')]),
                indicator: 'red'
            });
            frappe.validated = false;
        }
    }
});
// -------------------------------------------------------------------------

// -------------------- Validate row data, prevent missing data ----------------------------
frappe.ui.form.on('Daily Workforce', {
  validate: function(frm) {
    // Get the child table data
    var branchEmployees = frm.doc.branch_employee || [];

    var errorRows = []; // Array to store row numbers with errors

    // Loop through each row in the child table
    for (var i = 0; i < branchEmployees.length; i++) {
      var child = branchEmployees[i];

      // Check if any of the fields have data in the row
      if (child.transfer_department || child.transfer_start || child.transfer_end) {
        // Check if all the fields are filled in the row
        if (
          (!child.transfer_department && child.transfer_department !== 0) ||
          !child.transfer_start ||
          !child.transfer_end
        ) {
          errorRows.push(i + 1); // Store the row number with error
        }
      }
    }

    // Check if there are any errors
    if (errorRows.length > 0) {
      frappe.msgprint({
        title: __('Data Entry Error'),
        indicator: 'red',
        message: __('Transfer Dept., Transfer Start and Transfer End must be filled at rows: ') + errorRows.join(', '),
      });
      frappe.validated = false;
      return;
    }
  }
});
// -------------------------------------------------------------------------

// -------------------- Validate time data, prevent missing data ----------------------------
frappe.ui.form.on('Daily Workforce', {
  validate: function(frm) {
    var errorRows = []; // Array to store row numbers with errors

    // Loop through each row in the child table
    frm.doc.branch_employee.forEach(function(child, index) {
      // Check if any of the fields have data in the row
      if (child.time_in || child.time_out) {
        // Check if both "time_in" and "time_out" are filled in the row
        if (!child.time_in || !child.time_out) {
          errorRows.push(index + 1); // Store the row number with error
        }
      }
    });

    // If there are rows with errors, display the error message with the row numbers
    if (errorRows.length > 0) {
      frappe.msgprint({
        title: __('Data Entry Error'),
        indicator: 'red',
        message: __('Time In and Time Out must be filled at rows ') + errorRows.join(', '),
      });
      frappe.validated = false;
    }
  }
});
// -------------------------------------------------------------------------

// -------------------- Hide sidebar ----------------------------
frappe.ui.form.on('Daily Workforce', {
	refresh: function(me) {
    		me.page.sidebar.remove(); // this removes the sidebar
    		me.page.wrapper.find(".layout-main-section-wrapper").removeClass("col-md-10"); // this removes class "col-md-10" from content block, which sets width to 83%
    	} 
}
);
// -------------------------------------------------------------------------

// -------------------- Remove new email button ----------------------------
frappe.ui.form.on('Daily Workforce', {
	refresh(frm) {
		document.getElementsByClassName("timeline-items timeline-actions")[0].style.display = "none";
	}
});
// -------------------------------------------------------------------------

// -------------------- Remove comment button ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function(frm) {
        frm.page.wrapper.find(".comment-box").css({'display':'none'});
    }
});
// -------------------------------------------------------------------------

// -------------------- Tick all off ----------------------------
frappe.ui.form.on('Daily Workforce', {
  refresh: function(frm) {
    frm.add_custom_button('Tick All Off', function() {
      frm.doc.branch_employee.forEach(function(row) {
        // Set the value of the checkbox field to 1 (checked)
        frappe.model.set_value(row.doctype, row.name, 'employee_off', 1);
      });

      // Refresh the child table to reflect the changes
      frm.refresh_field('branch_employee');
    }, __("Set Off"))

    frm.add_custom_button(__('Set Off for Selected Rows'), function() {
      // Set the 'time_in' field value to 1 for selected rows
      var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
      selectedRows.forEach(function(row) {
        frappe.model.set_value(row.doctype, row.name, 'employee_off', 1);
      });

      // Refresh all selected rows at once
      frm.fields_dict.branch_employee.grid.refresh_selected(); 
    }, __("Set Off"))
  }
});
// -------------------------------------------------------------------------

// -------------------- All time in 08:00 ----------------------------
frappe.ui.form.on('Daily Workforce', {
  refresh: function(frm) {
    frm.add_custom_button('All Time In 08:00', function() {
      frm.doc.branch_employee.forEach(function(row) {
        if (row.employee_off === 0) {
          // Set the value of the time field to '08:00' for rows with 'employee_off' = 0
          frappe.model.set_value(row.doctype, row.name, 'time_in', '08:00');
        }
      });

      // Refresh the child table to reflect the changes
      frm.refresh_field('branch_employee');
    }, __("Set Time In"));

    frm.add_custom_button(__('Set Time In for Selected Rows'), function() {
      frappe.prompt([
        {
          label: __('Select Time'),
          fieldname: 'time_in',
          fieldtype: 'Select',
          options: [
            '07:00', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30',
            '11:00', '11:30', '13:30', '14:00', '14:30', '15:00', '15:30',
            '16:00', '16:30', '17:00', '17:30', '18:00'
          ],
          reqd: 1
        }
      ], function(values) {
        // Get the user-selected time value
        var selectedTime = values.time_in;

        // Iterate through selected rows in the child table
        var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
        selectedRows.forEach(function(row) {
          frappe.model.set_value(row.doctype, row.name, 'time_in', selectedTime);
        });

        // Refresh all selected rows at once
        frm.fields_dict.branch_employee.grid.refresh_selected(); 
      }, __('Set Time In for Selected Rows'), __('Set Time'));
    }, __("Set Time In"));
  }
});
// -------------------------------------------------------------------------

// -------------------- All time out 18:00 ----------------------------
frappe.ui.form.on('Daily Workforce', {
  refresh: function(frm) {
    frm.add_custom_button('All Time Out 18:00', function() {
      frm.doc.branch_employee.forEach(function(row) {
        if (row.employee_off === 0) {
          // Set the value of the time field to 18:00' for rows with 'employee_off' = 0
          frappe.model.set_value(row.doctype, row.name, 'time_out', '18:00');
        }
      });

      // Refresh the child table to reflect the changes
      frm.refresh_field('branch_employee');
    }, __("Set Time Out"));

    frm.add_custom_button(__('Set Time Out for Selected Rows'), function() {
      frappe.prompt([
        {
          label: __('Select Time'),
          fieldname: 'time_out',
          fieldtype: 'Select',
          options: [
            '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00',
            '12:30', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00',
            '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30',
            '20:00', '20:30', '21:00', '21:30', '22:00', '22:30'
          ],
          reqd: 1
        }
      ], function(values) {
        // Get the user-selected time value
        var selectedTime = values.time_out;

        // Iterate through selected rows in the child table
        var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
        selectedRows.forEach(function(row) {
          frappe.model.set_value(row.doctype, row.name, 'time_out', selectedTime);
        });

        // Refresh all selected rows at once
        frm.fields_dict.branch_employee.grid.refresh_selected(); 
      }, __('Set Time Out for Selected Rows'), __('Set Time'));
    }, __("Set Time Out"));
  }
});
// -------------------------------------------------------------------------

// -------------------- Set transfer dept for rows ----------------------------
frappe.ui.form.on('Daily Workforce', {
  refresh: function(frm) {
     frm.add_custom_button(__('Set Transfer Dept for Selected Rows'), function() {
      frappe.prompt([
        {
          label: __('Select Department'),
          fieldname: 'transfer_department',
          fieldtype: 'Select',
          options: [
            'CUT', 'EMB', 'FINAL', 'FJ', 'FL', 'FOIL', 'GESSO', 'MD', 'MTN',
            'OIL', 'PACK', 'PALLET', 'RIP', 'SD11', 'SD12', 'SM', 'SP11', 'SP12',
            'T_MAKING', 'TFL', 'WHS12', 'WHS41', 'VEN', 'GL'
          ],
          reqd: 1
        }
      ], function(values) {
        // Get the user-selected time value
        var selectedDept = values.transfer_department;

        // Iterate through selected rows in the child table
        var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
        selectedRows.forEach(function(row) {
          frappe.model.set_value(row.doctype, row.name, 'transfer_department', selectedDept);
        });

        // Refresh all selected rows at once
        frm.fields_dict.branch_employee.grid.refresh_selected(); 
      }, __('Set Transfer Dept for Selected Rows'), __('Set Department'));
    }, __("Set Transfer Dept"));
    

    frm.add_custom_button(__('Set Transfer Start for Selected Rows'), function() {
      frappe.prompt([
        {
          label: __('Select Time'),
          fieldname: 'transfer_start',
          fieldtype: 'Select',
          options: [
            '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00',
            '11:30', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00',
            '16:30', '17:00', '17:30', '18:30'
          ],
          reqd: 1
        }
      ], function(values) {
        // Get the user-selected time value
        var selectedTime = values.transfer_start;

        // Iterate through selected rows in the child table
        var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
        selectedRows.forEach(function(row) {
          frappe.model.set_value(row.doctype, row.name, 'transfer_start', selectedTime);
        });

        // Refresh all selected rows at once
        frm.fields_dict.branch_employee.grid.refresh_selected(); 
      }, __('Set Transfer Start for Selected Rows'), __('Set Time'));
    }, __("Set Transfer Dept"));
    
    
     frm.add_custom_button(__('Set Transfer End for Selected Rows'), function() {
      frappe.prompt([
        {
          label: __('Select Time'),
          fieldname: 'transfer_end',
          fieldtype: 'Select',
          options: [
            '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:30',
            '14:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00',
            '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30',
            '21:00', '21:30', '22:00', '22:30'
          ],
          reqd: 1
        }
      ], function(values) {
        // Get the user-selected time value
        var selectedTime = values.transfer_end;

        // Iterate through selected rows in the child table
        var selectedRows = frm.fields_dict.branch_employee.grid.get_selected_children();
        selectedRows.forEach(function(row) {
          frappe.model.set_value(row.doctype, row.name, 'transfer_end', selectedTime);
        });

        // Refresh all selected rows at once
        frm.fields_dict.branch_employee.grid.refresh_selected(); 
      }, __('Set Transfer End for Selected Rows'), __('Set Time'));
    }, __("Set Transfer Dept"));
  }
});
// -------------------------------------------------------------------------

// -------------------- Clear Table ----------------------------
frappe.ui.form.on('Daily Workforce', {
    refresh: function(frm) {
        frm.add_custom_button(__('Clear Table'), function() {
            frappe.confirm(__('Are you sure you want to clear the table?'), function() {
                frm.doc.branch_employee.forEach(function(row) {
                    row.employee_off = 0;
                    row.time_in = '';
                    row.time_out = '';
                    row.transfer_department = '';
                    row.transfer_start = '';
                    row.transfer_end = '';
                });

                // Clear branch_employee1 table
                frm.doc.branch_employee1.forEach(function(row) {
                    row.transfer_department2 = '';
                    row.transfer_start2 = '';
                    row.transfer_end2 = '';
                    row.transfer_department3 = '';
                    row.transfer_start3 = '';
                    row.transfer_end3 = '';
                });

                // Refresh both tables to update the view
                frm.refresh_field('branch_employee');
                frm.refresh_field('branch_employee1');
            });
        }).addClass('btn-danger'); // Add a class for red background color
    }
});
// -------------------------------------------------------------------------
