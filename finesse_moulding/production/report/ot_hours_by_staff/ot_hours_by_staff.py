# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def execute(filters=None):
    selected_branch = filters.get("branch")
    from_selected_date = filters.get("from_selected_date")
    to_selected_date = filters.get("to_selected_date")
    public_holidays = filters.get("public_holidays")
    columns = [
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 80},
        {"label": "Emp. No", "fieldname": "employee_number", "fieldtype": "Data", "width": 80},
        {"label": "Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 200},
        {"label": "Total Off", "fieldname": "total_off", "fieldtype": "Int", "width": 80},
        {"label": "TWH", "fieldname": "total_work_hours", "fieldtype": "Float", "precision": 1, "width": 80},
        {"label": "TWH Norm", "fieldname": "total_work_hours_norm", "fieldtype": "Float", "precision": 1, "width": 100},
        {"label": "TWH OT", "fieldname": "total_work_hours_ot", "fieldtype": "Data", "width": 100, "align": "right"},
    ]

    data = get_data(from_selected_date, to_selected_date, selected_branch, public_holidays)
    
	# Sort data based on total_work_hours_ot (now a float)
    data.sort(key=lambda x: x["total_work_hours_ot"], reverse=True)
    
	# Format the data for "total_work_hours_ot" column based on the condition
    for item in data:
        if item["total_work_hours_ot"] > 90:
            item["total_work_hours_ot"] = '<span style="color:red; font-weight:bold;">' + str(item["total_work_hours_ot"]) + '</span>'

    return columns, data

def is_weekend(date_obj):
    # Check if the day of the week is Saturday (5) or Sunday (6)
    return date_obj.weekday() in [5, 6]

def get_data(from_date, to_date, selected_branch, public_holidays):
    # Convert date strings to datetime objects
    from_date = datetime.strptime(from_date, "%Y-%m-%d")
    to_date = datetime.strptime(to_date, "%Y-%m-%d")

    # Parse public holidays list
    if public_holidays:
        public_holidays_list = public_holidays.split(",")
        public_holidays_list = [datetime.strptime(date_str.strip(), "%Y-%m-%d").date() for date_str in public_holidays_list]
    else:
        public_holidays_list = []
    
    data = []

    # Specify the list of branches to exclude
    excluded_branches = ["SC", "HR", "IT", "CLEANER", "ED", "E_MKT", "FIN", "OPERATION", "PM", "QA_OFFICE", "SAFETY", "PE", "BIDOR"]

    if selected_branch:
        # If selected_branch is specified, fetch employees for the selected branch
        employees = frappe.get_all(
            "Employee",
            filters={
                "branch": ("not in", excluded_branches),  # Exclude specified branches
                "branch": selected_branch,  # Filter by selected_branch
                "status": "Active" # Add the status filter for active employees
            },
            fields=["employee_name", "employee_number"],
            order_by="employee_name"  # Order by employee_name
        )
    else:
        # If selected_branch is not specified, fetch all employees and populate branch from the employee's record
        employees = frappe.get_all(
            "Employee",
            filters={"branch": ("not in", excluded_branches), "status": "Active"}, # Add the status filter for active employees
            fields=["employee_name", "employee_number", "branch"],  # Include the branch field
            order_by="employee_name"
        )

    for employee in employees:
        branch = employee.get("branch") if employee.get("branch") else selected_branch  # Use employee's branch or selected_branch
        employee_number = employee.get("employee_number")
        employee_name = employee.get("employee_name")

        if public_holidays_list:
        # Your additional SQL query to retrieve time_in and time_out for weekdays
            time_in_out_weekday = frappe.db.sql("""
                SELECT `time_in`, `time_out`
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND `date` NOT IN %s
                    AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != '' AND `employee_number` = %s
                ORDER BY `time_in`, `time_out`
            """, (from_date, to_date, public_holidays_list, employee_number))
        else:
            # If public_holidays_list is empty (None or []), exclude no dates
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
        

        if public_holidays_list:
        # Your additional SQL query to retrieve time_in and time_out for weekdays
            time_in_out_weekend = frappe.db.sql("""
                SELECT `time_in`, `time_out`
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND (
                            DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7  -- Sunday (1) or Saturday (7)
                            OR `date` IN %s 
                    )     
                ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != '' AND `employee_number` = %s
                ORDER BY `time_in`, `time_out`
            """, (from_date, to_date, public_holidays_list, employee_number))
        else:
            # If public_holidays_list is empty (None or []), exclude no dates
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

        total_work_hours_weekends = 0.0
        total_work_hours_norm = 0.0
        total_work_hours_weekdays = 0.0
        total_ot_weekday = 0.0 

        # Iterate over dates from from_date to to_date
        current_date = from_date
        while current_date <= to_date:
            # Check if the current date is a weekend
            if not is_weekend(current_date):

                total_work_hours_norm = 0.0
                total_work_hours_weekdays = 0.0
                total_ot_weekday = 0.0 

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
                        
                # Calculate TWH (OT) for the employee
                total_ot_weekday = total_work_hours_weekdays - total_work_hours_norm

            else:

                total_work_hours_weekends = 0.0

                # Calculate work_hours_norm for weekend days
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

            # Move to the next day
            current_date += timedelta(days=1)


        data.append({
            "branch": branch,
            "employee_number": employee_number,
            "employee_name": employee_name,
            "total_off": total_off,
            "total_work_hours": total_work_hours_weekdays + total_work_hours_weekends,
            "total_work_hours_norm": total_work_hours_norm,
            "total_work_hours_ot": total_ot_weekday + total_work_hours_weekends,
        })

    return data