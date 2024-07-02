# Copyright (c) 2024, Victor and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def execute(filters=None):
    selected_designation = filters.get("designation")
    from_selected_date = filters.get("from_selected_date")
    to_selected_date = filters.get("to_selected_date")
    columns = [
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 80},
        {"label": "Position", "fieldname": "designation", "fieldtype": "Data", "width": 150},
        {"label": "Emp. No", "fieldname": "employee_number", "fieldtype": "Data", "width": 80},
        {"label": "Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": "Total Off", "fieldname": "total_off", "fieldtype": "Int", "width": 80},
        {"label": "TWH", "fieldname": "total_work_hours", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": "TWH Norm", "fieldname": "total_work_hours_norm", "fieldtype": "Float", "precision": 1, "width": 100},
        {"label": "TWH OT", "fieldname": "total_work_hours_ot", "fieldtype": "Data", "width": 100, "align": "right"},
    ]

    data = get_data(from_selected_date, to_selected_date, selected_designation)
    
	# Sort data based on total_work_hours_ot (now a float)
    data.sort(key=lambda x: x["total_work_hours_ot"], reverse=True)

    return columns, data

def get_data(from_date, to_date, selected_designation):
    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")
    
    data = []

	# Specify the list of branches to exclude
    excluded_branches = ["SC", "HR", "IT", "CLEANER", "ED", "E_MKT", "FIN", "OPERATION", "PM", "QA_OFFICE", "SAFETY", "PE", "BIDOR"]
    
    if selected_designation:
        # If selected_branch is specified, fetch employees for the selected branch
        employees = frappe.get_all(
            "Employee",
            filters={
                "designation": ("in", selected_designation),  # Filter by selected_branch
                "status": "Active" # Add the status filter for active employees
            },
            fields=["employee_name", "employee_number", "designation", "branch"],
            order_by="employee_name"  # Order by employee_name
        )
    else:
        # If selected_branch is not specified, fetch all employees and populate branch from the employee's record
        employees = frappe.get_all(
            "Employee",
            filters={"branch": ("not in", excluded_branches), "status": "Active"}, # Add the status filter for active employees
            fields=["employee_name", "employee_number", "designation", "branch"],  # Include the branch field
            order_by="employee_name"
        )

    for employee in employees:
        designation = employee.get("designation")
        employee_number = employee.get("employee_number")
        employee_name = employee.get("employee_name")
        branch = employee.get("branch")

        # Your additional SQL query to retrieve time_in and time_out for weekdays
        time_in_out_weekday = frappe.db.sql("""
            SELECT `time_in`, `time_out`
            FROM `tabBranch Employee`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `date` BETWEEN %s AND %s
                AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
            ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != '' AND `employee_number` = %s
            ORDER BY `time_in`, `time_out`
        """, (from_date, to_date, employee_number))

        time_in_out_weekend = frappe.db.sql("""
            SELECT `time_in`, `time_out`
            FROM `tabBranch Employee`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `date` BETWEEN %s AND %s
                AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
            ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != '' AND `employee_number` = %s
            ORDER BY `time_in`, `time_out`
        """, (from_date, to_date, employee_number))
                                      

        total_off = frappe.db.sql("""
            SELECT COUNT(`employee_number`)
            FROM `tabBranch Employee`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `date` BETWEEN %s AND %s
                AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)    
            ) AND `employee_number` = %s AND `employee_off` = 1
        """, (from_date, to_date, employee_number))[0][0]	

        total_work_hours_norm = 0.0
        total_work_hours_ot = 0.0
        total_work_hours_weekdays = 0.0 
        total_work_hours_weekends = 0.0
        total_work_hours = 0.0
        
        for record in time_in_out_weekend:
            time_in = record[0]
            time_out = record[1]

            # Convert time_in and time_out to datetime objects
            datetime_in = frappe.utils.get_datetime(time_in)
            datetime_out = frappe.utils.get_datetime(time_out)

            # Calculate the time difference between time_in and time_out for each employee
            if datetime_in and datetime_out:
                # Calculate the work hours excluding the 1-hour break
                work_hours_weekends = (datetime_out - datetime_in).total_seconds() / 3600.0
                # Add a condition to exclude the "GUARD" branch
                if branch != "GUARD":
                    if datetime_in.hour <= 12 and datetime_out.hour > 18: # Exclude 1.5-hour break if start time before 12:00 and end time is after 18:00
                        work_hours_weekends -= 1.5
                    elif datetime_in.hour <= 12 and datetime_out.hour >= 13: # Exclude 1.0-hour break if start time before 12:00 and end time is at 18:00
                        work_hours_weekends -= 1.0
                    elif datetime_in.hour >= 13 and datetime_in.hour < 18 and datetime_out.hour > 18: # Exclude 0.5-hour break if start time before 18:00 and end time is after 18:00
                        work_hours_weekends -= 0.5
                total_work_hours_weekends += work_hours_weekends

        for record in time_in_out_weekday:
            time_in = record[0]
            time_out = record[1]

            # Convert time_in and time_out to datetime objects
            datetime_in = frappe.utils.get_datetime(time_in)
            datetime_out = frappe.utils.get_datetime(time_out)

            # Calculate the time difference between time_in and time_out for each employee
            if datetime_in and datetime_out:
                # Calculate the work hours excluding the 1-hour break
                work_hours_weekdays = (datetime_out - datetime_in).total_seconds() / 3600.0
                # Add a condition to exclude the "GUARD" branch
                if branch != "GUARD":
                    if datetime_in.hour <= 12 and datetime_out.hour > 18: # Exclude 1.5-hour break if start time before 12:00 and end time is after 18:00
                        work_hours_weekdays -= 1.5
                    elif datetime_in.hour <= 12 and datetime_out.hour >= 13: # Exclude 1.0-hour break if start time before 12:00 and end time is at 18:00
                        work_hours_weekdays -= 1.0
                    elif datetime_in.hour >= 13 and datetime_in.hour < 18 and datetime_out.hour > 18: # Exclude 0.5-hour break if start time before 18:00 and end time is after 18:00
                        work_hours_weekdays -= 0.5
                total_work_hours_weekdays += work_hours_weekdays

                # Calculate the normalized work hours (TWH (Norm)) if time_out is after 18:00
                if branch != "GUARD":  # Check if the branch is not "GUARD"
                    if datetime_out.hour > 18:
                        work_hours_norm = work_hours_weekdays - (datetime_out.hour - 18)
                    else:
                        work_hours_norm = work_hours_weekdays
                else:
                    # For the "GUARD" branch, limit total_work_hours_norm to a maximum of 9 hours
                    if datetime_out.hour > 18:
                        work_hours_norm = min(work_hours_weekdays - (datetime_out.hour - 18), 9.0)
                    else:
                        work_hours_norm = min(work_hours_weekdays, 9.0)

                total_work_hours_norm += work_hours_norm
                
            # Calculate TWH (OT) for the branch
            total_work_hours_ot = total_work_hours_weekdays - total_work_hours_norm + total_work_hours_weekends

            total_work_hours = total_work_hours_weekdays + total_work_hours_weekends

        data.append({
            "branch": branch,
            "designation": designation,
            "employee_number": employee_number,
            "employee_name": employee_name,
            "total_off": total_off,
            "total_work_hours": total_work_hours,
            "total_work_hours_norm": total_work_hours_norm,
            "total_work_hours_ot": total_work_hours_ot,
        })

    return data
