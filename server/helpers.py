import time
from random import randint
import requests
import zeep
from zeep import Client, Plugin
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from requests import Session

from .models import BankDetail, KycDetail

class MyLoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        http_headers['Content-Type'] = 'text/xml; charset=utf-8;'
        return envelope, http_headers


def random_num_with_N_digits(n):

    from random import randint

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def create_username():
    import time

    username = str(random_num_with_N_digits(6)) + str(time.time())[:4]

    return username


def save_kyc_data_to_db(user, data):
    user.first_name = data.get("first_name") or user.first_name
    user.middle_name = data.get("middle_name") or user.middle_name
    user.last_name = data.get("last_name") or user.last_name
    user.save()

    kyc_data = {
        "user": user,
        "pan": data["pan"],
        "tax_status": data["tax_status"],
        "occ_code": data["occ_code"],
        "dob": data["dob"],
        "gender": data["gender"],
        "address": data["address"],
        "city": data["city"],
        "state": data["state"],
        "country": data["country"].upper(),
        "pincode": data["pincode"],
        "phone": data["phone"],
        "paperless_flag": data["paperless_flag"],
        "nominee_name": data["nominee_name"],
        "nominee_relation": data["nominee_relation"].lower(),
        "kyc_type": data["kyc_type"],
        "ckyc_number": data["ckyc_number"],
    }
    kyc_detail = KycDetail(**kyc_data)
    kyc_detail.save()
    bank_detail_data = {
        "user": user,
        "bank": data["bank"],
        "ifsc_code": data["ifsc_code"],
        "account_number": data["account_number"],
        "account_type": data["account_type"],
    }
    bank_detail = BankDetail(**bank_detail_data)
    bank_detail.save()


def prepare_user_param(user, kyc, bank):
    add1 = kyc.address[:30]
    if len(kyc.address) > 30:
        add2 = kyc.address[30:60]
        if len(kyc.address) > 60:
            add3 = kyc.address[60:90]
        else:
            add3 = ""
    else:
        add2 = add3 = ""

    # make the list that will be used to create param
    param_list = [
        ("UCC", "T" + str(user.pk)[:10]),
        ("FIRSTNAME", user.first_name),
        ("MIDDLENAME", user.middle_name),
        ("LASTNAME", user.last_name),
        ("TAX_STATUS", kyc.tax_status),
        ("GENDER", kyc.gender),
        ("DOB", kyc.dob),
        ("OCCUPATION_CODE", kyc.occ_code),
        ("HOLDING", "SI"),
        ("S_FIRSTNAME", ""),
        ("S_MIDDLENAME", ""),
        ("S_LASTNAME", ""),
        ("T_FIRSTNAME", ""),
        ("T_MIDDLENAME", ""),
        ("T_LASTNAME", ""),
        ("S_DOB", ""),
        ("T_DOB", ""),
        ("GFIRSTNAME", ""),
        ("GMIDDLENAME", ""),
        ("GLASTNAME", ""),
        ("G_DOB", ""),
        ("PAN_EXEMPT", "N"),
        ("S_PAN_EXEMPT", ""),
        ("T_PAN_EXEMPT", ""),
        ("G_EXEMPT_CATEGORY", ""),
        ("PAN", kyc.pan),
        ("S_PAN", ""),
        ("T_PAN", ""),
        ("G_PAN", ""),
        ("EXEMPT_CATEGORY", ""),
        ("S_EXEMPT_CATEGORY", ""),
        ("T_EXEMPT_CATEGORY", ""),
        ("G_EXEMPT_CATEGORY", ""),
        ("CLIENT_TYPE", "P"),
        ("PMS", ""),
        ("DEFAULT_DP", ""),
        ("CDSLDPID", ""),
        ("CDSLCLTID", ""),
        ("CMBPID", ""),
        ("NSDLDPID", ""),
        ("NSDLCLTID", ""),
        ("ACCOUNT_TYPE", bank.account_type),
        ("ACCOUNT_NO", bank.account_number),
        ("MICR_NO", ""),
        ("IFSC", bank.ifsc_code),
        ("DEFAULT_BANK", "Y"),
        ("ACCOUNT_TYPE_2", ""),
        ("ACCOUNT_NO_2", ""),
        ("MICR_NO_2", ""),
        ("IFSC_CODE_2", ""),
        ("DEFAULT_BANK", ""),
        ("ACCOUNT_TYPE_3", ""),
        ("ACCOUNT_NO_3", ""),
        ("MICR_NO_3", ""),
        ("IFSC_CODE_3", ""),
        ("DEFAULT_BANK", ""),
        ("ACCOUNT_TYPE_4", ""),
        ("ACCOUNT_NO_4", ""),
        ("MICR_NO_4", ""),
        ("IFSC_CODE_4", ""),
        ("DEFAULT_BANK", ""),
        ("ACCOUNT_TYPE_5", ""),
        ("ACCOUNT_NO_5", ""),
        ("MICR_NO_5", ""),
        ("IFSC_CODE_5", ""),
        ("DEFAULT_BANK", ""),
        ("CHEQUE_NAME", ""),
        ("DIV_PAY_MODE", "02"),
        ("ADDRESS_1", add1),
        ("ADDRESS_2", add2),
        ("ADDRESS_3", add3),
        ("CITY", kyc.city),
        ("STATE", kyc.state),
        ("PINCODE", kyc.pincode),
        ("COUNTRY", kyc.country),
        ("RESI_PHONE", ""),
        ("RESI_FAX", ""),
        ("OFFICE_PHONE", ""),
        ("OFFICE_FAX", ""),
        ("EMAIL", user.email),
        ("COMM_MODE", "E"),
        ("FOREIGN_ADD_1", ""),
        ("FOREIGN_ADD_2", ""),
        ("FOREIGN_ADD_3", ""),
        ("FOREIGN_CITY", ""),
        ("FOREIGN_PINCODE", ""),
        ("FOREIGN_STATE", ""),
        ("FOREIGN_COUNTRY", ""),
        ("FOREIGN_PHONE", ""),
        ("FOREIGN_FAX", ""),
        ("FOREIGN_OFF_PHONE", ""),
        ("FOREIGN_OFF_FAX", ""),
        ("INDIAN_MOB_NO", kyc.phone),
        ("NOMINEE_NAME", kyc.nominee_name),
        ("NOMINEE_RELATION", kyc.nominee_relation.lower()),
        ("NOMINEE_APPLICABLE", "100"),
        ("MINOR_FLAG", "N"),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),  # Nominee
        ("KYC_TYPE", kyc.kyc_type),
        ("CKYC_NUMBER", kyc.ckyc_number),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("", ""),
        ("PAPERLESS_FLAG", kyc.paperless_flag),
        ("", ""),
        ("", ""),
        ("MOBILE_FLAG", "SE"),
        ("EMAIL_FLAG", "SE"),
        ("", ""),
    ]

    # prepare the param field to be returned
    user_param = ""
    for param in param_list:
        user_param = user_param + "|" + str(param[1])

    return user_param[1:]


def prepare_payload_for_bse_call(user):
    kyc = KycDetail.objects.filter(user=user).first()
    bank = BankDetail.objects.filter(user=user).first()

    payload = {
        "UserId": "5972901",
        "MemberCode": "59729",
        "Password": "Abc@1234",
        "RegnType": "NEW",
        "Param": prepare_user_param(user, kyc, bank),
    }
    print(payload)
    return payload


def register_client_on_bse(payload):
    url = "https://bsestarmfdemo.bseindia.com/StarMFCommonAPI/ClientMaster/Registration"

    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    response = requests.post(url=url, headers=header, json=payload)

    return response


def authenticate_nominee(user):
    url = "https://bsestarmfdemo.bseindia.com/BSEMFWEBAPI/api/mfupload/Registation/w"

    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    params = [
        {"ClientCode": f"T{user.pk}", "NominationOpt": "Y", "NominationAuthMode": "O"}
    ]

    payload = {
        "Type": "NOMINEE",
        "UserId": "5972901",
        "MemberCode": "59729",
        "Password": "Abc@1234",
        "RegnType": "NEW",
        "Param": params,
    }

    response = requests.post(url=url, headers=header, json=payload)

    return response

class HeaderModifierPlugin(Plugin):
    def egress(self, envelope, http_headers, operation, binding_options):
        http_headers.pop('SOAPAction')
        header = envelope.find('{http://www.w3.org/2003/05/soap-envelope}Header')
        if header is not None:
            # Modify existing elements or add new ones
            for elem in header:
                if elem.tag.endswith('To'):
                    elem.text = 'https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure'
        return envelope, http_headers


def soap_set_wsa_headers(method_url, svc_url):
	header = zeep.xsd.ComplexType([
        zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}Action', zeep.xsd.String()),
        zeep.xsd.Element('{http://www.w3.org/2005/08/addressing}To', zeep.xsd.String())
    ])
	header_value = header(Action=method_url, To=svc_url)
	return header_value


def soap_get_password():
    history = HistoryPlugin()
    client = Client(
        "https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc?wsdl",
        plugins=[HeaderModifierPlugin(), history]
    )
    print(client.transport.session.headers)
    method_url = "http://bsestarmf.in/MFOrderEntry/getPassword"
    svc_url = "https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure"
    header_values = soap_set_wsa_headers(method_url, svc_url)

    with client.settings(strict=False, raw_response=True, force_https=False):
        response = client.service.getPassword(
            UserId="5972901",
            Password="Abc@1234",
            PassKey="59729",
        )
        print(response)
        print(history.last_sent)
        from lxml import etree
        # Assuming 'envelope' is the Envelope object
        envelope_xml = etree.tostring(history.last_sent['envelope'], pretty_print=True, encoding='unicode')
        print(envelope_xml)

import requests

def get_password_with_requests():
    url = "https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure"
    
    headers = {
        'Content-Type': 'application/soap+xml; charset=utf-8',
        'SOAPAction': 'http://bsestarmf.in/MFOrderEntry/getPassword'
    }
    
    body = """
        <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
    xmlns:bses="http://bsestarmf.in/">
        <soap:Header xmlns:wsa="http://www.w3.org/2005/08/addressing">
            <wsa:Action>http://bsestarmf.in/MFOrderEntry/getPassword</wsa:Action>
            <wsa:To>https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc</wsa:To>
        </soap:Header>
        <soap:Body>
            <bses:getPassword>
                <bses:UserId>5972901</bses:UserId>
                <bses:Password>Abc@1234</bses:Password>
                <bses:PassKey>8569519126</bses:PassKey>
            </bses:getPassword>
        </soap:Body>
    </soap:Envelope>
    """
    
    response = requests.post(url, headers=headers, data=body)
    print(response.status_code)
    from lxml import etree
    root = etree.fromstring(response.content)
    # Define the namespaces
    namespaces = {
        's': 'http://www.w3.org/2003/05/soap-envelope',
        'a': 'http://www.w3.org/2005/08/addressing',
        'bses': 'http://bsestarmf.in/'
    }

    # Extract the getPasswordResult
    result = root.xpath('//bses:getPasswordResult/text()', namespaces=namespaces)
    print(result)
    result = result[0]
    # Split the result into status code and password
    status_code, password = result.split('|')

    print(f"Status Code: {status_code}")
    print(f"Password: {password}")

    return password


from zeep import Client, xsd
from zeep.transports import Transport
from requests import Session

def call_get_password_service(user_id, password, pass_key):
    # Create a session object
    session = Session()
    session.headers.update({
        'Content-Type': 'application/soap+xml;charset=UTF-8',
        'Accept': 'application/soap+xml',
    })

    # Create a transport object with the session
    transport = Transport(session=session)

    # Create the client
    client = Client('https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc?wsdl', transport=transport)
    client.service._binding_options['address'] = 'https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure'

    # Define the headers
    wsa = '{http://www.w3.org/2005/08/addressing}'
    header = xsd.Element(
        '{http://bsestarmf.in/}Action',
        xsd.ComplexType([
            xsd.Element(wsa + 'Action', xsd.String()),
            xsd.Element(wsa + 'To', xsd.String()),
        ])
    )
    header_value = header(Action='http://bsestarmf.in/MFOrderEntry/getPassword',To= 'https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure')

    # Define the body
    body = {
        "UserId": user_id,
        "Password": password,
        "PassKey": pass_key
    }

    # Call the service method
    response = client.service.getPassword(_soapheaders=[header_value], **body)

    # Return the response
    return response

# Call the functi