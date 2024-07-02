# Copyright (c) 2024, Victor and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    columns = [
        {"label": "Name", "fieldname": "name", "fieldtype": "Data", "width": 200},
        {"label": "Branch", "fieldname": "branch", "fieldtype": "Data", "width": 80},
        {"label": "Emp. No", "fieldname": "emp_no", "fieldtype": "Data", "width": 80},
        {"label": "Time Out", "fieldname": "time_out", "fieldtype": "Data", "width": 80}, 
        {"label": "Tarms", "fieldname": "tarms", "fieldtype": "Data", "width": 70},
        {"label": "Match", "fieldname": "match", "fieldtype": "Int", "width": 70},
        {"label": "Remarks", "fieldname": "remark", "fieldtype": "Text", "width": 150},
    ]

    data = get_data(filters.get("date"))
    
    return columns, data

def get_data(selected_date):
    data = frappe.db.sql("""
        SELECT 
            b.employee_name AS name,
            dw.branch AS branch,
            CASE
                WHEN be.time_out IS NULL OR be.time_out = '' THEN 'off'
                ELSE be.time_out
            END AS time_out,
            b.employee_number AS emp_no,
            (
                SELECT ec.time
                FROM `tabEmployee Checkin` ec
                WHERE ec.employee = b.employee_number
                AND DATE(ec.time) = %s
                ORDER BY ec.time DESC
                LIMIT 1
            ) AS checkin_time,
            be.remark AS remark
        FROM 
            `tabDaily Workforce` dw
        INNER JOIN
            `tabBranch Employee` b ON dw.name = b.parent
        LEFT JOIN
            `tabBranch Employee` be ON dw.name = be.parent AND be.employee_number = b.employee_number
        WHERE
            dw.date = %s
        GROUP BY
            b.employee_name;
    """, (selected_date, selected_date), as_dict=True)
    
    # Format checkin_time using Python's datetime library
    for entry in data:
        if entry.checkin_time:
            entry.tarms = entry.checkin_time.strftime('%H:%M')
        else:
            entry.tarms = 'off'
            
        entry.match = calculate_match(entry.tarms, entry.time_out)
            
    return data

def calculate_match(tarms, time_out):
    if tarms == 'off' and time_out == 'off':
        return 1
    
    if tarms != 'off' and time_out != 'off':
        tarms_time = datetime.strptime(tarms, '%H:%M')
        time_out_time = datetime.strptime(time_out, '%H:%M')
        
        if timedelta(minutes=0) <= (time_out_time - tarms_time) <= timedelta(minutes=10) or timedelta(minutes=0) <= (tarms_time - time_out_time) <= timedelta(minutes=30):
            return 1
    
    return 0
