import json
import frappe
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.sms.v20210111 import sms_client, models
from frappe import _
from frappe.model.document import Document
from frappe.utils.password import get_decrypted_password




class TencentSMSLog(Document):
    def on_submit(self):
        # Fetch the secret information from the TencentIntegrationSecurity DocType
        secret_info = frappe.get_all('Tencent Integration Security', filters={'company': self.company, 'action':'SendSms', 'docstatus':1}, limit_page_length=1)
        if secret_info:
            secret_info_doc = frappe.get_doc('Tencent Integration Security', secret_info[0].name)
        else:
            frappe.throw(_("No Tencent Integration Security for SMS found for the company {0}").format(self.company))
        
        api_info = frappe.get_all('Tencent Integration Settings', filters={'company': self.company, 'action':'SendSms', 'docstatus':1}, limit_page_length=1)
        if api_info:
            api_info_doc = frappe.get_doc('Tencent Integration Settings', api_info[0].name)
        else:
            frappe.throw(_("No Tencent Integration Setting for SMS found for the company {0}").format(self.company))
                
             
        try:
            cred = credential.Credential(secret_info_doc.secret_id, get_decrypted_password('Tencent Integration Security', secret_info_doc.name, "secret_key"))
            httpProfile = HttpProfile()
            httpProfile.endpoint = api_info_doc.end_point

            clientProfile = ClientProfile()
            clientProfile.httpProfile = httpProfile
            client = sms_client.SmsClient(cred, api_info_doc.region, clientProfile)

            req = models.SendSmsRequest()
            params = {
                "PhoneNumberSet": json.loads(self.phone_number_set),
                "SmsSdkAppId": api_info_doc.sdk_app_id,
                "SignName": api_info_doc.sign_name,
                "TemplateId": self.template_id,
                "TemplateParamSet": json.loads(self.template_param_set)
            }
            req.from_json_string(json.dumps(params))

            resp = client.SendSms(req)
            self.response = resp.to_json_string()
            print(resp.to_json_string())
            if resp.SendStatusSet[0].Code == "Ok":
                self.status = "Success"
                
            else:
                self.status = "Failed"
                frappe.log_error('SMS send failed', _(resp.SendStatusSet[0].Code + resp.SendStatusSet[0].Message))  
            self.save(ignore_permissions=True)

        except TencentCloudSDKException as err:
            frappe.log_error(_("Failed to create SMS Log"),_(str(err)))


def create_sms_log(company, sms_template_usage, phone_number_set, template_param_set):
    #get template id from doctype Tencent SMS Template using company and sms_template_usage
    try:
        template_id = frappe.get_value("Tencent SMS Template", {"company": company, "sms_template_usage": sms_template_usage,"docstatus":1}, "sms_template_id")
        if template_id:
            sms_log = frappe.new_doc("Tencent SMS Log")
            sms_log.company = company
            sms_log.phone_number_set = phone_number_set
            sms_log.template_id = template_id
            sms_log.template_param_set = template_param_set
            sms_log.save(ignore_permissions=True)
            sms_log.submit()
        else:
            frappe.log_error('Template Id not found',_("No template found for the company {0} and sms_template_usage {1}").format(company, sms_template_usage))
    except Exception as e:
        frappe.log_error( _("Failed to create SMS Log"),frappe.get_traceback())
        