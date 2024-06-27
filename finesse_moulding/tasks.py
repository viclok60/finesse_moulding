from datetime import datetime
import frappe


def daily_workforce():
    branches = ['GL', 'VEN']
    today = datetime.now().strftime('%Y-%m-%d')

    for branch in branches: 
        existing_doc = frappe.get_all('Daily Workforce', filters={'branch': branch, 'date': today})

        if not existing_doc:
            doc = frappe.new_doc('Daily Workforce')
            doc.branch = branch
            doc.date = today
            doc.insert()
        else:
            print("A record for this branch and date already exists.")
