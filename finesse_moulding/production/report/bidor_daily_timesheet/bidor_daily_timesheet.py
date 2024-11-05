# Copyright (c) 2023, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from datetime import datetime

def execute(filters=None):
    columns = [
        {"label": "ID", "fieldname": "employee_id", "fieldtype": "Data", "width": 60},
        {"label": "Name", "fieldname": "employee_name", "fieldtype": "Data", "width": 250},
        {"label": "TIME IN", "fieldname": "time_in", "fieldtype": "Data", "width": 100},
        {"label": "TIME OUT", "fieldname": "time_out", "fieldtype": "Data", "width": 100},
        {"label": "TIME IN2", "fieldname": "time_in2", "fieldtype": "Data", "width": 100},
        {"label": "TIME OUT2", "fieldname": "time_out2", "fieldtype": "Data", "width": 100},
        {"label": "TIME IN3", "fieldname": "time_in3", "fieldtype": "Data", "width": 100},
        {"label": "TIME OUT3", "fieldname": "time_out3", "fieldtype": "Data", "width": 100},
    ]

    selected_date = filters.get("date")
    
    data = get_data(selected_date)
    
    formatted_data = []
    
    for row in data:
        formatted_row = {}
        
        # Apply formatting based on time_in and time_in2
        for time_column in ["time_in", "time_out", "time_in2", "time_out2", "time_in3", "time_out3"]:
            formatted_times = []
            if row[time_column] is not None:  # Check for None value
                time_entries = row[time_column].split(',')
                for entry in time_entries:
                    formatted_time = datetime.strptime(entry.split('-')[0].strip(), "%H:%M:%S.%f").strftime("%H:%M")
                    location_id = entry.split('-')[1].strip() if '-' in entry else ""
                    formatted_time_with_location = f"{formatted_time} - {location_id}"
                    # Apply formatting conditions
                    if (time_column == "time_in" and datetime.strptime(entry.split('-')[0].strip(), "%H:%M:%S.%f").time() > datetime.strptime("08:01:00", "%H:%M:%S").time()) or \
                       (time_column == "time_in2" and datetime.strptime(entry.split('-')[0].strip(), "%H:%M:%S.%f").time() > datetime.strptime("13:31:00", "%H:%M:%S").time()):
                        formatted_time_with_location = f'<b><font color="red">{formatted_time_with_location}</font></b>'
                    formatted_times.append(formatted_time_with_location)
                formatted_row[time_column] = ', '.join(formatted_times)
            else:
                formatted_row[time_column] = None
        
        # Check if there is a second entry in the "time_out" column and move it to "time_in2"
        if formatted_row["time_out"] is not None:
            time_out_entries = formatted_row["time_out"].split(', ')
            if len(time_out_entries) > 1:
                formatted_row["time_in2"] = time_out_entries[1]  # Set the second entry to "time_in2"

        # Ensure only one ec.time is allowed in the "time_out" column
        if formatted_row["time_out"] is not None:
            time_out_entries = formatted_row["time_out"].split(', ')
            if len(time_out_entries) > 1:
                formatted_row["time_out"] = time_out_entries[0]  # Keep only the first entry
        
        # Copy the rest of the data
        formatted_row["employee_id"] = row["employee_id"]
        formatted_row["employee_name"] = row["employee_name"]
        
        formatted_data.append(formatted_row)

    return columns, formatted_data

def get_data(selected_date):
    data = frappe.db.sql("""
        SELECT
            e.employee_number AS employee_id,
            e.employee_name AS employee_name,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '06:00:00' AND '12:00:30' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_in,
            (CASE
                WHEN COUNT(CASE WHEN TIME(ec.time) BETWEEN '06:00:00' AND '12:00:30' THEN 1 ELSE NULL END) > 1
                THEN GROUP_CONCAT(
                    CONCAT(
                        CASE
                            WHEN TIME(ec.time) BETWEEN '06:00:00' AND '12:00:30' THEN TIME(ec.time)
                            ELSE NULL
                        END,
                        ' - ',
                        ec.device_id
                    )
                    ORDER BY ec.time
                    LIMIT 1, 1
                )
                ELSE NULL
            END) AS time_in2,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '12:00:31' AND '12:50:30' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_out,
            (CASE
                WHEN COUNT(CASE WHEN TIME(ec.time) BETWEEN '12:00:31' AND '12:50:30' THEN 1 ELSE NULL END) > 1
                THEN GROUP_CONCAT(
                    CONCAT(
                        CASE
                            WHEN TIME(ec.time) BETWEEN '12:00:31' AND '12:50:30' THEN TIME(ec.time)
                            ELSE NULL
                        END,
                        ' - ',
                        ec.device_id
                    )
                    ORDER BY ec.time
                    LIMIT 1, 1
                )
                ELSE NULL
            END) AS time_out2,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '12:50:31' AND '17:00:30' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_in2,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '17:00:31' AND '18:20:30' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_out2,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '18:20:31' AND '19:00:30' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_in3,
            GROUP_CONCAT(
                CONCAT(
                    CASE
                        WHEN TIME(ec.time) BETWEEN '19:00:31' AND '23:00:00' THEN TIME(ec.time)
                        ELSE NULL
                    END,
                    ' - ',
                    ec.device_id
                )
                ORDER BY ec.time
            ) AS time_out3
        FROM
            `tabEmployee` e
        LEFT JOIN
            `tabEmployee Checkin` ec ON e.employee_number = ec.employee AND DATE(ec.time) = %s
        WHERE
            e.branch = 'BIDOR' AND e.status = 'Active'
        GROUP BY
            e.employee, e.employee_name
        ORDER BY
            CASE 
                WHEN ec.time IS NOT NULL THEN 0
                ELSE 1
            END,
            CASE 
                WHEN e.employee_number IN (279, 399) AND ec.time IS NOT NULL THEN 1
                ELSE 0
            END,
            e.employee_number
    """, selected_date, as_dict=1)

    return data
