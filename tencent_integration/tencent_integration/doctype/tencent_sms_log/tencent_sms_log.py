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
            print(resp.to_json_string())

        except TencentCloudSDKException as err:
            frappe.throw(_(str(err)))
