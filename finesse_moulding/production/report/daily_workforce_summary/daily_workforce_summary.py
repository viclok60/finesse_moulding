# Copyright (c) 2024, Victor and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    selected_branch = filters.get("branch")
    from_selected_date = filters.get("from_selected_date")
    to_selected_date = filters.get("to_selected_date")
    public_holidays = filters.get("public_holidays")  # Get the public holidays list from filters
    columns = [
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 90},
        {"label": "Total Days", "fieldname": "total_work_days", "fieldtype": "Data", "width": 90},
        {"label": "Off", "fieldname": "total_off", "fieldtype": "Int", "width": 50},
        {"label": "Total", "fieldname": "total_employee", "fieldtype": "Data", "width": 60},
        {"label": "TWH", "fieldname": "total_work_hours", "fieldtype": "Float", "precision": 1, "width": 60},
        {"label": "<span style='color: green;'>Total Staff Normal (PPL)</span>", "fieldname": "total_staff_norm", "fieldtype": "Int", "width": 150},
        {"label": "<span style='color: green;'>TWH Normal (W.H)</span>", "fieldname": "total_work_hours_norm", "fieldtype": "Float", "precision": 1, "width": 120},
        {"label": "<span style='color: red;'>Total Staff OT (PPL)</span>", "fieldname": "total_staff_ot", "fieldtype": "Int", "width": 125},
        {"label": "<span style='color: red;'>TWH OT (W.H)</span>", "fieldname": "total_work_hours_ot", "fieldtype": "Float", "precision": 1, "width": 90},
        {"label": "<span style='color: green;'>Transfer Normal IN (PPL)</span>", "fieldname": "in_people_norm", "fieldtype": "Int", "width": 180}, 
        {"label": "<span style='color: green;'>Transfer Normal IN (W.H)</span>", "fieldname": "in_work_hours_norm", "fieldtype": "Float", "precision": 1, "width": 180},
        {"label": "<span style='color: green;'>Transfer Normal OUT (PPL)</span>", "fieldname": "out_people_norm", "fieldtype": "Int", "width": 200},
        {"label": "<span style='color: green;'>Transfer Normal OUT (W.H)</span>", "fieldname": "out_work_hours_norm", "fieldtype": "Float", "precision": 1, "width": 200},
        {"label": "<span style='color: red;'>Transfer OT IN (PPL)</span>", "fieldname": "in_people_ot", "fieldtype": "Int", "width": 160},
        {"label": "<span style='color: red;'>Transfer OT IN (W.H)</span>", "fieldname": "in_work_hours_ot", "fieldtype": "Float", "precision": 1, "width": 160},
        {"label": "<span style='color: red;'>Transfer OT OUT (PPL)</span>", "fieldname": "out_people_ot", "fieldtype": "Int", "width": 180}, 
        {"label": "<span style='color: red;'>Transfer OT OUT (W.H)</span>", "fieldname": "out_work_hours_ot", "fieldtype": "Float", "precision": 1, "width": 180},
        {"label": "<span style='color: green;'>Actual Normal (PPL)</span>", "fieldname": "norm_people", "fieldtype": "Int", "width": 150}, 
        {"label": "<span style='color: green;'>Actual Normal (W.H)</span>", "fieldname": "norm_work_hours", "fieldtype": "Float", "precision": 1, "width": 150},
        {"label": "<span style='color: red;'>Actual OT (PPL)</span>", "fieldname": "ot_people", "fieldtype": "Int", "width": 130}, 
        {"label": "<span style='color: red;'>Actual OT (W.H)</span>", "fieldname": "ot_work_hours", "fieldtype": "Float", "precision": 1, "width": 130},
    ]

    # Check if from_selected_date and to_selected_date are the same
    hide_time_columns = from_selected_date != to_selected_date

    if not hide_time_columns:
        # Add "Time In" and "Time Out" columns
        columns.insert(1, {"label": "Time In", "fieldname": "time_in", "fieldtype": "Data", "width": 140})
        columns.insert(2, {"label": "Time Out", "fieldname": "time_out", "fieldtype": "Data", "width": 150})

    data = get_data(from_selected_date, to_selected_date, selected_branch, public_holidays)
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

    # Get a list of all branches
    branches = frappe.get_all("Branch", fields=["branch"])

    branches = sorted(branches, key=lambda x: x.get("branch"))
    
    data = []
            
    for branch in branches:
        branch = branch.get("branch")
        
        # Check if the branch should be excluded
        if branch in ["SC", "HR", "IT", "CLEANER", "ED", "E_MKT", "FIN", "OPERATION", "PM", "QA_OFFICE", "SAFETY", "PE", "BIDOR"]:
            continue  # Skip this branch and move to the next iteration

        # Check if a tabDaily Workforce record exists for the selected date and branch
        workforce_exists = frappe.db.exists("Daily Workforce", {"date": ("between", [from_date, to_date]), "branch": branch})

        # Add a condition to filter by selected 'branch'
        if selected_branch and selected_branch != branch:
            continue
    
        if workforce_exists:
            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                total_employee_weekday = frappe.db.sql("""
                    SELECT COUNT(`employee_name`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND `date` NOT IN %s  -- Exclude public holidays
                        AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                total_employee_weekday = frappe.db.sql("""
                    SELECT COUNT(`employee_name`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                    )
                """, (branch, from_date, to_date))[0][0]

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                total_off = frappe.db.sql("""
                SELECT SUM(`employee_off`)
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND `date` NOT IN %s  -- Exclude public holidays
                    AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                total_off = frappe.db.sql("""
                SELECT SUM(`employee_off`)
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                )
            """, (branch, from_date, to_date))[0][0]

            total_employee_off = frappe.db.sql("""
                SELECT SUM(`be`.`employee_off`)
                FROM `tabBranch Employee` AS `be`
                JOIN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s
                    AND `date` BETWEEN %s AND %s
                    AND `name` IN (
                        SELECT DISTINCT `parent`
                        FROM `tabBranch Employee`
                        WHERE `time_in` IS NOT NULL AND `time_in` != ''
                    )
                ) AS `dw`
                ON `be`.`parent` = `dw`.`name`
                WHERE `be`.`parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                )
            """, (branch, from_date, to_date, branch, from_date, to_date))[0][0]

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                total_weekend_employee = frappe.db.sql("""
                    SELECT COUNT(`employee_name`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND `date` = %s
                        AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                # Total Employees on Weekends
                total_weekend_employee = frappe.db.sql("""
                    SELECT COUNT(`employee_name`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                    )
                """, (branch, from_date, to_date))[0][0]

            
            total_employee = frappe.db.sql("""
                SELECT COUNT(`be`.`employee_name`)
                FROM `tabBranch Employee` AS `be`
                JOIN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s
                    AND `date` BETWEEN %s AND %s
                    AND `name` IN (
                        SELECT DISTINCT `parent`
                        FROM `tabBranch Employee`
                        WHERE `time_in` IS NOT NULL AND `time_in` != ''
                    )
                ) AS `dw`
                ON `be`.`parent` = `dw`.`name`
                WHERE `be`.`parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                )
            """, (branch, from_date, to_date, branch, from_date, to_date))[0][0]

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                total_weekend_off = frappe.db.sql("""
                    SELECT SUM(`employee_off`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND `date` = %s
                        AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                # Total Off on Weekends
                total_weekend_off = frappe.db.sql("""
                    SELECT SUM(`employee_off`)
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                    )
                """, (branch, from_date, to_date))[0][0]
                       

            # Handle the case where total_off is None
            total_off = total_off or 0
            
            # Handle the case where total_weekend_off is None
            total_weekend_off = total_weekend_off or 0

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                total_staff_ot_weekdays = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `time_out` > '18:00'
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE branch = %s AND `date` BETWEEN %s AND %s
                    AND `date` != %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                total_staff_ot_weekdays = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `time_out` > '18:00'
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE branch = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                )
            """, (branch, from_date, to_date))[0][0]

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                time_in_out_weekday = frappe.db.sql("""
                    SELECT `time_in`, `time_out`
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND `date` != %s
                        AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                    ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != ''
                    ORDER BY `time_in`, `time_out`
                """, (branch, from_date, to_date, public_holidays_list))
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                # Get Time In and Time Out for the branch on the selected date from tabBranch Employee
                time_in_out_weekday = frappe.db.sql("""
                    SELECT `time_in`, `time_out`
                    FROM `tabBranch Employee`
                    WHERE `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                        AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                    ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != ''
                    ORDER BY `time_in`, `time_out`
                """, (branch, from_date, to_date))
                

            # Get Time In and Time Out for the branch on the selected date from tabBranch Employee
            time_in_out_weekend = frappe.db.sql("""
                SELECT `time_in`, `time_out`
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                ) AND `time_in` IS NOT NULL AND `time_out` IS NOT NULL AND `time_in` != '' AND `time_out` != ''
                ORDER BY `time_in`, `time_out`
            """, (branch, from_date, to_date))

            # Fetch the count of tabDaily Workforce entries for the specified branch where time_in is not null
            tw_days_count = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabDaily Workforce`
                WHERE `branch` = %s
                AND `date` BETWEEN %s AND %s
                AND `name` IN (
                    SELECT DISTINCT `parent`
                    FROM `tabBranch Employee`
                    WHERE `time_in` IS NOT NULL AND `time_in` != ''
                )
            """, (branch, from_date, to_date))[0][0]

            # Fetch the count of tabDaily Workforce entries for the GL and VEN branch
            tw_days_count_gl_ven = frappe.db.sql("""
                SELECT COUNT(DISTINCT `date`)
                FROM `tabDaily Workforce`
                WHERE `date` BETWEEN %s AND %s
                AND `name` IN (
                    SELECT DISTINCT `parent`
                    FROM `tabBranch Employee`
                    WHERE `transfer_department` = %s
                )
            """, (from_date, to_date, branch))[0][0]

            # Next, set tw_days_count_gl_ven to 0 for all branches except 'GL' and 'VEN'
            if branch not in ['GL', 'VEN']:
                tw_days_count_gl_ven = 0

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                in_people_norm1 = frappe.db.sql("""
                    SELECT COUNT(`name`)
                    FROM `tabBranch Employee`
                    WHERE `transfer_department` = %s AND `transfer_start` < '18:00'
                    AND `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `date` BETWEEN %s AND %s
                        AND `date` != %s
                        AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                # Calculate the total number of employees transferred into their department with transfer_start < 18:00
                in_people_norm1 = frappe.db.sql("""
                    SELECT COUNT(`name`)
                    FROM `tabBranch Employee`
                    WHERE `transfer_department` = %s AND `transfer_start` < '18:00'
                    AND `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `date` BETWEEN %s AND %s
                        AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
                """, (branch, from_date, to_date))[0][0]

            if public_holidays_list:
                # Modify query to exclude public holidays if list is not empty
                in_people_norm2 = frappe.db.sql("""
                    SELECT COUNT(`name`)
                    FROM `tabBranch Employee 1`
                    WHERE `transfer_department2` = %s AND `transfer_start2` < '18:00'
                    AND `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `date` BETWEEN %s AND %s
                        AND `date` != %s
                        AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
                """, (branch, from_date, to_date, public_holidays_list))[0][0]
            else:
                # If public_holidays_list is empty (None or []), exclude no dates
                # Calculate the total number of employees transferred into their department with transfer_start < 18:00
                in_people_norm2 = frappe.db.sql("""
                    SELECT COUNT(`name`)
                    FROM `tabBranch Employee 1`
                    WHERE `transfer_department2` = %s AND `transfer_start2` < '18:00'
                    AND `parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `date` BETWEEN %s AND %s
                        AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
                """, (branch, from_date, to_date))[0][0]
                

            in_people_norm = in_people_norm1 + in_people_norm2

            # Calculate the total number of employees transferred into their department with transfer_end > 18:00 during weekdays
            in_people_ot_weekday1 = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `transfer_department` = %s AND `transfer_end` > '18:00'
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                )
            """, (branch, from_date, to_date))[0][0]

            in_people_ot_weekday2 = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee 1`
                WHERE `transfer_department2` = %s AND `transfer_end2` > '18:00'
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) BETWEEN 2 AND 6  -- Monday (2) to Friday (6)
                )
            """, (branch, from_date, to_date))[0][0]

            in_people_ot_weekday = in_people_ot_weekday1 + in_people_ot_weekday2

            # Calculate the total number of employees transferred into their department during weekends
            in_people_ot_weekend = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `transfer_department` = %s
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                )
            """, (branch, from_date, to_date))[0][0]

            # Calculate the total number of employees transferred out of their department with transfer_start < 18:00
            out_people_norm = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                ) AND `transfer_department` != '' AND `transfer_start` < '18:00'
            """, (branch, from_date, to_date))[0][0]

            # Calculate the total number of employees transferred out of their department with transfer_end > 18:00 and is weekday
            out_people_ot_weekday1 = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                ) AND `transfer_department` != '' AND `transfer_end` > '18:00' 
            """, (branch, from_date, to_date))[0][0]

            out_people_ot_weekday2 = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee 1`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                ) AND `transfer_department2` != '' AND `transfer_end2` > '18:00' 
            """, (branch, from_date, to_date))[0][0]

            out_people_ot_weekday = out_people_ot_weekday1 + out_people_ot_weekday2

            # Calculate the total number of employees transferred out of their department and is weekend
            out_people_ot_weekend = frappe.db.sql("""
                SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                ) AND `transfer_department` != '' 
            """, (branch, from_date, to_date))[0][0]

            # Get Transfer Start and Transfer End for the branch that transfered employees out with transfer_start < 18:00
            branch_employees_out = frappe.db.sql("""
                SELECT `be`.`transfer_start`, `be`.`transfer_end`, `be1`.`transfer_end2`
                FROM `tabBranch Employee` AS `be`
                INNER JOIN `tabBranch Employee 1` AS `be1` ON `be`.`employee_number` = `be1`.`employee_number` AND `be`.`parent` = `be1`.`parent`                                
                WHERE `be`.`parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                ) AND `be`.`transfer_department` != '' AND `be`.`transfer_start` < '18:00'
            """, (branch, from_date, to_date), as_dict=True)       

            out_work_hours_norm = 0.0
            for employee in branch_employees_out:
                transfer_start = employee.get("transfer_start")
                transfer_end = employee.get("transfer_end")
                transfer_end2 = employee.get("transfer_end2")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_end = frappe.utils.get_datetime(transfer_end)
                datetime_end2 = frappe.utils.get_datetime(transfer_end2)

                if datetime_end.hour >= 18:
                    end_of_day = datetime_end.replace(hour=18, minute=0, second=0)
                    datetime_end = end_of_day
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    out_work_hours_norm += work_hours
                elif datetime_end.hour < 18 and datetime_end2 is not None:
                    end_of_day = datetime_end2.replace(hour=18, minute=0, second=0)
                    datetime_end2 = end_of_day
                    work_hours = (datetime_end2 - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end2.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    out_work_hours_norm += work_hours
                elif datetime_end.hour < 18:   
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    out_work_hours_norm += work_hours

            # Get Transfer Start and Transfer End for the branch that transfered employees out with transfer_end > 18:00 and during weekdays
            branch_employees_out_ot_weekday = frappe.db.sql("""
                SELECT `be`.`transfer_start`, `be`.`transfer_end`, `be1`.`transfer_end2`
                FROM `tabBranch Employee` AS `be`
                INNER JOIN `tabBranch Employee 1` AS `be1` ON `be`.`employee_number` = `be1`.`employee_number` AND `be`.`parent` = `be1`.`parent`
                WHERE `be`.`parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                ) AND `be`.`transfer_department` != '' AND `be`.`time_out` > '18:00'
            """, (branch, from_date, to_date), as_dict=True)       

            out_work_hours_ot_weekday = 0.0
            for employee in branch_employees_out_ot_weekday:
                transfer_start = employee.get("transfer_start")
                transfer_end = employee.get("transfer_end")
                transfer_end2 = employee.get("transfer_end2")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_end = frappe.utils.get_datetime(transfer_end)
                datetime_end2 = frappe.utils.get_datetime(transfer_end2)

                if datetime_end.hour > 18:
                    end_of_day = datetime_end.replace(hour=18, minute=30, second=0)
                    datetime_start = end_of_day
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    out_work_hours_ot_weekday += work_hours
                elif datetime_end2 is not None:
                    if datetime_end2.hour > 18:   # This condition is separate from the previous one
                        end_of_day = datetime_end2.replace(hour=18, minute=30, second=0)
                        datetime_start = end_of_day
                        work_hours = (datetime_end2 - datetime_start).total_seconds() / 3600.0
                        out_work_hours_ot_weekday += work_hours

            # Get Transfer Start and Transfer End for the branch that transfered employees out during weekends
            branch_employees_out_ot_weekend = frappe.db.sql("""
                SELECT `transfer_start`, `transfer_end`
                FROM `tabBranch Employee`
                WHERE `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `branch` = %s AND `date` BETWEEN %s AND %s
                    AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                ) AND `transfer_department` != ''
            """, (branch, from_date, to_date), as_dict=True)       

            out_work_hours_ot_weekend = 0.0
            for employee in branch_employees_out_ot_weekend:
                transfer_start = employee.get("transfer_start")
                transfer_end = employee.get("transfer_end")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_end = frappe.utils.get_datetime(transfer_end)

                if datetime_start and datetime_end:
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 18: # Exclude 1.5-hour break if start time before 12:00 and end time is after 18:00
                        work_hours -= 1.5
                    elif datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    elif datetime_start.hour >= 13 and datetime_start.hour < 18 and datetime_end.hour > 18: # Exclude 0.5-hour break if start time before 18:00 and end time is after 18:00
                        work_hours -= 0.5
                    out_work_hours_ot_weekend += work_hours

            # Get Transfer Start and Transfer End for the branch that got employees transferred in 
            branch_employees_in = frappe.db.sql("""
                SELECT `be`.`transfer_start`, `be`.`transfer_end`, `be`.`transfer_department`, `be1`.`transfer_start2`, `be1`.`transfer_end2`, `be1`.`transfer_department2`
                FROM `tabBranch Employee` AS `be`
                INNER JOIN `tabBranch Employee 1` AS `be1` ON `be`.`employee_number` = `be1`.`employee_number` AND `be`.`parent` = `be1`.`parent`
                WHERE (`be1`.`transfer_department2` = %s OR `be`.`transfer_department` = %s) AND `be`.`transfer_start` < '18:00'
                AND `be`.`parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                )
            """, (branch, branch, from_date, to_date), as_dict=True)  

            in_work_hours_norm = 0.0
            for employee in branch_employees_in:
                transfer_start = employee.get("transfer_start")
                transfer_start2 = employee.get("transfer_start2")
                transfer_end = employee.get("transfer_end")
                transfer_end2 = employee.get("transfer_end2")
                transfer_department = employee.get("transfer_department")
                transfer_department2 = employee.get("transfer_department2")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_start2 = frappe.utils.get_datetime(transfer_start2)
                datetime_end = frappe.utils.get_datetime(transfer_end)
                datetime_end2 = frappe.utils.get_datetime(transfer_end2)

                if datetime_end.hour >= 18 and transfer_department == branch:
                    end_of_day = datetime_end.replace(hour=18, minute=0, second=0)
                    datetime_end = end_of_day
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    in_work_hours_norm += work_hours
                elif datetime_end.hour < 18 and transfer_department == branch:
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    in_work_hours_norm += work_hours    
                elif datetime_end.hour < 18 and transfer_department2 == branch and datetime_end2 is not None:
                    end_of_day = datetime_end2.replace(hour=18, minute=0, second=0)
                    datetime_end2 = end_of_day
                    work_hours = (datetime_end2 - datetime_start2).total_seconds() / 3600.0
                    in_work_hours_norm += work_hours
                                       
                                       
            # Get Transfer Start and Transfer End for the branch that got employees transferred in for OT
            branch_employees_in_ot_weekday = frappe.db.sql("""
                SELECT `be`.`transfer_start`, `be`.`transfer_end`, `be1`.`transfer_end2`, `be1`.`transfer_department2`
                FROM `tabBranch Employee` AS `be`
                INNER JOIN `tabBranch Employee 1` AS `be1` ON `be`.`employee_number` = `be1`.`employee_number` AND `be`.`parent` = `be1`.`parent`
                WHERE (`be1`.`transfer_department2` = %s OR `be`.`transfer_department` = %s) AND `be`.`time_out` > '18:00'
                    AND `be`.`parent` IN (
                        SELECT `name`
                        FROM `tabDaily Workforce`
                        WHERE `date` BETWEEN %s AND %s
                        AND DAYOFWEEK(`date`) NOT IN (1, 7)  -- Exclude Sundays (1) and Saturdays (7)
                    )
            """, (branch, branch, from_date, to_date), as_dict=True)

            in_work_hours_ot_weekday = 0.0
            for employee in branch_employees_in_ot_weekday:
                transfer_start = employee.get("transfer_start")
                transfer_end = employee.get("transfer_end")
                transfer_end2 = employee.get("transfer_end2")
                transfer_department2 = employee.get("transfer_department2")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_end = frappe.utils.get_datetime(transfer_end)
                datetime_end2 = frappe.utils.get_datetime(transfer_end2)

                if transfer_department2 == branch and datetime_end2 is not None and datetime_end2.hour > 18:
                    end_of_day = datetime_end2.replace(hour=18, minute=30, second=0)
                    datetime_start = end_of_day
                    work_hours = (datetime_end2 - datetime_start).total_seconds() / 3600.0
                    in_work_hours_ot_weekday += work_hours
                elif datetime_end.hour > 18:
                    end_of_day = datetime_end.replace(hour=18, minute=30, second=0)
                    datetime_start = end_of_day
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    in_work_hours_ot_weekday += work_hours

            
            # Get Transfer Start and Transfer End for the branch that got employees transferred in for OT
            branch_employees_in_ot_weekend = frappe.db.sql("""
                SELECT `transfer_start`, `transfer_end`
                FROM `tabBranch Employee`
                WHERE `transfer_department` = %s
                    AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` BETWEEN %s AND %s
                    AND (DAYOFWEEK(`date`) = 1 OR DAYOFWEEK(`date`) = 7)  -- Sunday (1) or Saturday (7)
                )
            """, (branch, from_date, to_date), as_dict=True)

            in_work_hours_ot_weekend = 0.0
            for employee in branch_employees_in_ot_weekend:
                transfer_start = employee.get("transfer_start")
                transfer_end = employee.get("transfer_end")

                datetime_start = frappe.utils.get_datetime(transfer_start)
                datetime_end = frappe.utils.get_datetime(transfer_end)

                if datetime_start and datetime_end:
                    work_hours = (datetime_end - datetime_start).total_seconds() / 3600.0
                    if datetime_start.hour < 12 and datetime_end.hour > 18: # Exclude 1.5-hour break if start time before 12:00 and end time is after 18:00
                        work_hours -= 1.5
                    elif datetime_start.hour < 12 and datetime_end.hour > 12: # Exclude 1-hour break if start time before 12:30 and end time is before 18:00
                        work_hours -= 1.0
                    elif datetime_start.hour >= 13 and datetime_start.hour < 18 and datetime_end.hour > 18: # Exclude 0.5-hour break if start time before 18:00 and end time is after 18:00
                        work_hours -= 0.5
                    in_work_hours_ot_weekend += work_hours
            
            total_work_hours = 0.0 # Calculate total work hours (TWH) for the branch
            total_work_hours_norm = 0.0  # Initialize the total work hours within 8:00 to 18:00
            total_work_hours_ot = 0.0
            norm_people = 0
            norm_work_hours = 0.0
            ot_people = 0
            ot_work_hours = 0.0
            in_people_ot = 0

            # Calculate the transfer out people for OT 
            out_people_ot = out_people_ot_weekday + out_people_ot_weekend

            # Calculate the transfer out working hours for OT 
            out_work_hours_ot = out_work_hours_ot_weekday + out_work_hours_ot_weekend


            # Calculate the transfer in working hours for OT
            in_work_hours_ot = in_work_hours_ot_weekday + in_work_hours_ot_weekend

            

            # Initialize total_staff_norm
            total_staff_norm = 0
            total_staff_ot = 0
            # Initialize variables to track overtime for weekdays and weekends
            
            total_staff_ot_weekends = 0
            ot_people_weekdays = 0
            ot_people_weekends = 0
            ot_work_hours_weekdays = 0.0
            ot_work_hours_weekends = 0.0
            total_work_hours_ot_weekdays = 0.0
            total_work_hours_ot_weekends = 0.0
            total_work_hours_ot = 0.0
            total_work_hours_weekdays = 0.0
            total_work_hours_weekends = 0.0
          

            # Iterate over dates from from_date to to_date
            current_date = from_date
            while current_date <= to_date:
                # Check if the current date is a weekend
                if not is_weekend(current_date):
                    # Calculate total staff norm when not weekend
                    total_staff_norm = total_employee_weekday - total_off

                    total_work_hours_weekdays = 0.0
                    total_work_hours_norm = 0.0
                    

                    # Calculate work_hours_norm for non-weekend days
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


                    # Calculate OT (PPL) for the branch
                    ot_people_weekdays = total_staff_ot_weekdays + in_people_ot_weekday - out_people_ot_weekday

                    # Calculate TWH (OT) for the branch
                    total_work_hours_ot_weekdays = total_work_hours_weekdays - total_work_hours_norm

                    # Calculate OT (W.H) for the branch
                    ot_work_hours_weekdays = total_work_hours_ot_weekdays + in_work_hours_ot_weekday - out_work_hours_ot_weekday

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

                    # Count the number of employees during weekends
                    total_staff_ot_weekends = total_weekend_employee - total_weekend_off

                    # Calculate OT (PPL) for the branch
                    ot_people_weekends = total_staff_ot_weekends + in_people_ot_weekend - out_people_ot_weekend

                    # Calculate TWH (OT) for the branch
                    total_work_hours_ot_weekends = total_work_hours_weekends

                    # Calculate the ot work hours for the branch
                    ot_work_hours_weekends = total_work_hours_ot_weekends - out_work_hours_ot_weekend + in_work_hours_ot_weekend

                # Move to the next day
                current_date += timedelta(days=1)
                
            # Calculate the total staff overtime by adding weekday and weekend overtime
            total_staff_ot = total_staff_ot_weekdays + total_staff_ot_weekends

            #Calculate the ot people for branch 
            ot_people = ot_people_weekdays + ot_people_weekends

            #Calculate total work hours for branch 
            total_work_hours = total_work_hours_weekdays + total_work_hours_weekends

            #Calculate ot work hours for the branch
            ot_work_hours = ot_work_hours_weekdays + ot_work_hours_weekends

            #Calculate the total off for branch
            total_off = total_off + total_weekend_off

            # Calculate TWH (OT) for the branch
            total_work_hours_ot = total_work_hours_ot_weekdays + total_work_hours_ot_weekends

            # Calculate Norm (PPL) for the branch 
            norm_people = total_staff_norm + in_people_norm - out_people_norm

            # Calculate Norm (W.H) for the branch 
            norm_work_hours = total_work_hours_norm - out_work_hours_norm + in_work_hours_norm

            # Calculate the Total Working Days for a branch
            tw_days_count = tw_days_count + tw_days_count_gl_ven

            # Calculate the transfer in people for OT 
            in_people_ot = in_people_ot_weekday + in_people_ot_weekend

            time_in_weekday_count = {}
            time_out_weekday_count = {}
            time_in_weekend_count = {}
            time_out_weekend_count = {}

            for record in time_in_out_weekday:
                time_in = record[0]
                time_out = record[1]
    
                time_in_weekday_count[time_in] = time_in_weekday_count.get(time_in, 0) + 1
                time_out_weekday_count[time_out] = time_out_weekday_count.get(time_out, 0) + 1

            for record in time_in_out_weekend:
                time_in = record[0]
                time_out = record[1]
    
                time_in_weekend_count[time_in] = time_in_weekend_count.get(time_in, 0) + 1
                time_out_weekend_count[time_out] = time_out_weekend_count.get(time_out, 0) + 1

        else:
            # If no workforce data exists, initialize default values
            total_employee = 0
            total_off = 0
            total_employee_off = 0
            total_staff_norm = 0   
            total_work_hours = 0.0 # Calculate total work hours (TWH) for the branch
            total_work_hours_norm = 0.0  # Initialize the total work hours within 8:00 to 18:00
            total_staff_ot = 0  # New column for counting employees with time_out after 18:00
            total_work_hours_ot = 0.0
            norm_people = 0
            norm_work_hours = 0.0
            ot_people = 0
            ot_work_hours = 0.0
            in_work_hours_ot = 0.0
            in_work_hours_norm = 0.0
            out_work_hours_norm = 0.0
            out_work_hours_ot = 0.0
            in_people_norm = 0
            in_people_ot = 0
            out_people_norm = 0
            out_people_ot = 0
            tw_days_count = 0
            time_in_weekday_count = {}
            time_out_weekday_count = {}
            time_in_weekend_count = {}
            time_out_weekend_count = {}

        data.append({
            "branch": branch,
            "time_in": ", ".join([f"{time} - {count}" for time, count in sorted(time_in_weekday_count.items())] + [f"{time} - {count}" for time, count in sorted(time_in_weekend_count.items())]),
            "time_out": ", ".join([f"{time} - {count}" for time, count in sorted(time_out_weekday_count.items())] + [f"{time} - {count}" for time, count in sorted(time_out_weekend_count.items())]),
            "total_work_days": tw_days_count,
            "total_off": total_employee_off,
            "total_employee": total_employee,
            "total_work_hours": total_work_hours,  # Add the calculated total work hours to the data
            "total_staff_norm": total_staff_norm,
            "total_work_hours_norm": total_work_hours_norm,  # Add the calculated normalized work hours to the data
            "total_staff_ot": total_staff_ot,  # Add the calculated count of employees with time_out after 18:00
            "total_work_hours_ot": total_work_hours_ot,  # Add the calculated TWH (OT) to the data
            "in_people_norm": in_people_norm,  # Add the calculated total number of employees transferred into their department
            "in_work_hours_norm": in_work_hours_norm,
            "out_people_norm": out_people_norm,
            "out_work_hours_norm": out_work_hours_norm,
            "in_people_ot": in_people_ot,
            "in_work_hours_ot": in_work_hours_ot,
            "out_people_ot": out_people_ot,
            "out_work_hours_ot": out_work_hours_ot,
            "norm_people": norm_people,
            "norm_work_hours": norm_work_hours,
            "ot_people": ot_people,
            "ot_work_hours": ot_work_hours,
        })

    return data
