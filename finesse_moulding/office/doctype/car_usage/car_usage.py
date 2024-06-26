# Copyright (c) 2024, Victor and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class CarUsage(Document):
    def before_insert(self):
        # Fetch current user session IP address
        user = frappe.session.user
        session_data = frappe.db.sql("""
            SELECT 
                REPLACE(
                    REPLACE(
                        substring_index(substring_index(sessiondata, 'session_ip', -1), ',', 1), ':', ''), "'", "") AS ip
            FROM tabSessions
            WHERE user = %s
            ORDER BY lastupdate DESC
            LIMIT 1
        """, (user,), as_dict=True)
        
        if session_data:
            self.ip_address = session_data[0].get('ip')

