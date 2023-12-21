from frappe.model.document import Document
import frappe
from frappe import _

class TencentIntegrationSecurity(Document):
    def before_submit(self):
        secret_info = frappe.get_all('Tencent Integration Security', filters={'company': self.company, 'action':self.action, 'docstatus':1}, limit_page_length=1)
        if secret_info:
            frappe.throw(_("Tencent Integration Security for {1} already exists for the company {0}").format(self.company, self.action)) 
            