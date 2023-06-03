from frappe.model.document import Document
import frappe
from frappe import _

class TencentIntegrationSettings(Document):
    def before_submit(self):
        api_info = frappe.get_all('Tencent Integration Settings', filters={'company': self.company, 'action':'SendSms', 'docstatus':1}, limit_page_length=1)
        if api_info:
            frappe.throw(_("Tencent Integration Settings for SMS already exists for the company {0}, Docname {1}").format(self.company, api_info[0].name)) 
