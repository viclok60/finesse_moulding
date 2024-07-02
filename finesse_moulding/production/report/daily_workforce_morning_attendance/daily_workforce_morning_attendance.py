# Copyright (c) 2024, Victor and contributors
# For license information, please see license.txt

import frappe

def execute(filters=None):
    columns = [
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 100},
        {"label": "Total Employee", "fieldname": "total_employee", "fieldtype": "Int", "width": 120},
        {"label": "Total Absent", "fieldname": "total_absent", "fieldtype": "Int", "width": 110},
        {"label": "Total Attend", "fieldname": "total_attend", "fieldtype": "Int", "width": 100},
        {"label": "Total Out", "fieldname": "total_out", "fieldtype": "Int", "width": 100},
        {"label": "Total In", "fieldname": "total_in", "fieldtype": "Int", "width": 80},
        {"label": "Actual Employee", "fieldname": "actual_employee", "fieldtype": "Int", "width": 140},
    ]

    data = get_data(filters.get("date"))
    return columns, data

def get_data(selected_date):
    # Get unique branch values from tabDaily Workforce for the selected date
    branches = frappe.get_all("Daily Workforce", filters={"date": selected_date}, distinct=True, pluck="branch")
    branches.sort()

    data = []
    for branch in branches:
        total_employee = frappe.db.count("Employee", filters={"branch": branch, "status": "Active"})

        total_absent = frappe.db.sql("""
            SELECT SUM(`employee_off`)
            FROM `tabBranch Employee`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `branch` = %s AND `date` = %s
            )
        """, (branch, selected_date))[0][0]

        # Handle the case where total_absent is None
        total_absent = total_absent or 0

        total_attend = total_employee - total_absent

        total_out1 = frappe.db.sql("""
            SELECT COUNT(`name`)
            FROM `tabBranch Employee`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `branch` = %s AND `date` = %s
            ) AND `transfer_department` != ''
        """, (branch, selected_date))[0][0]

        total_out2 = frappe.db.sql("""
            SELECT COUNT(`name`)
            FROM `tabBranch Employee 1`
            WHERE `parent` IN (
                SELECT `name`
                FROM `tabDaily Workforce`
                WHERE `branch` = %s AND `date` = %s
            ) AND `transfer_department2` != ''
        """, (branch, selected_date))[0][0]

        total_out = total_out1 + total_out2

        # Updated query for total_in to count occurrences of the branch in transfer_department
        total_in1 = frappe.db.sql("""
            SELECT COUNT(`name`)
                FROM `tabBranch Employee`
                WHERE `transfer_department` = %s
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` = %s
                )
            """, (branch, selected_date))[0][0]
        
        total_in2 = frappe.db.sql("""
            SELECT COUNT(`name`)
                FROM `tabBranch Employee 1`
                WHERE `transfer_department2` = %s
                AND `parent` IN (
                    SELECT `name`
                    FROM `tabDaily Workforce`
                    WHERE `date` = %s
                )
            """, (branch, selected_date))[0][0]
        
        total_in = total_in1 + total_in2
        
        actual_employee = total_attend - total_out + total_in

        data.append({
            "branch": branch,
            "total_employee": total_employee,
            "total_absent": total_absent,
            "total_attend": total_attend,
            "total_out": total_out,
            "total_in": total_in,
            "actual_employee": actual_employee
        })

    return data
