import os
from random import randint
import requests
from zeep import Client, Plugin, xsd
from zeep.plugins import HistoryPlugin
from zeep.transports import Transport
from zeep.helpers import serialize_object
from requests import Session
from lxml import etree
from datetime import datetime
import base64

from .models import BankDetail, KycDetail, Transaction, MutualFundList, BSERequest


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

    kyc_detail = KycDetail.objects.filter(user=user).first()
    bank_detail = BankDetail.objects.filter(user=user).first()

    if not kyc_detail:
        kyc_data = {
            "user": user,
            "client_code": "T"
            + str(user.pk)[:10],  # TODO: Prepare a better client code
            "pan": data["pan"],
            "tax_status": data["tax_status"],
            "income_slab": data["income_slab"],
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
            "ckyc_number": data.get("ckyc_number", ""),
        }
        kyc_detail = KycDetail(**kyc_data)
        kyc_detail.save()

    if not bank_detail:
        bank_detail_data = {
            "user": user,
            "bank": data["bank"],
            "ifsc_code": data["ifsc_code"],
            "account_number": data["account_number"],
            "account_type": data["account_type"],
        }
        bank_detail = BankDetail(**bank_detail_data)
        bank_detail.save()

    return kyc_detail, bank_detail


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
        ("UCC", kyc.client_code),
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


def prepare_fatca_param(client_code):
    # extract the records from the table
    kyc = KycDetail.objects.get(client_code=client_code)
    user = kyc.user
    # some fields require processing
    inv_name = user.first_name
    if user.middle_name != "":
        inv_name = inv_name + " " + user.middle_name
    if user.last_name != "":
        inv_name = inv_name + " " + user.last_name
    inv_name = inv_name[:70]
    if kyc.occ_code == "01":
        srce_wealt = "02"
        occ_type = "B"
    else:
        srce_wealt = "01"
        occ_type = "S"

    # make the list that will be used to create param
    param_list = [
        ("PAN_RP", kyc.pan),
        ("PEKRN", ""),
        ("INV_NAME", inv_name),
        ("DOB", ""),
        ("FR_NAME", ""),
        ("SP_NAME", ""),
        ("TAX_STATUS", kyc.tax_status),
        ("DATA_SRC", "E"),
        ("ADDR_TYPE", "1"),
        ("PO_BIR_INC", "IN"),
        ("CO_BIR_INC", "IN"),
        ("TAX_RES1", "IN"),
        ("TPIN1", kyc.pan),
        ("ID1_TYPE", "C"),
        ("TAX_RES2", ""),
        ("TPIN2", ""),
        ("ID2_TYPE", ""),
        ("TAX_RES3", ""),
        ("TPIN3", ""),
        ("ID3_TYPE", ""),
        ("TAX_RES4", ""),
        ("TPIN4", ""),
        ("ID4_TYPE", ""),
        ("SRCE_WEALT", srce_wealt),
        ("CORP_SERVS", ""),
        ("INC_SLAB", kyc.income_slab),
        ("NET_WORTH", ""),
        ("NW_DATE", ""),
        ("PEP_FLAG", "N"),
        ("OCC_CODE", kyc.occ_code),
        ("OCC_TYPE", occ_type),
        ("EXEMP_CODE", ""),
        ("FFI_DRNFE", ""),
        ("GIIN_NO", ""),
        ("SPR_ENTITY", ""),
        ("GIIN_NA", ""),
        ("GIIN_EXEMC", ""),
        ("NFFE_CATG", ""),
        ("ACT_NFE_SC", ""),
        ("NATURE_BUS", ""),
        ("REL_LISTED", ""),
        ("EXCH_NAME", "O"),
        ("UBO_APPL", "N"),
        ("UBO_COUNT", ""),
        ("UBO_NAME", ""),
        ("UBO_PAN", ""),
        ("UBO_NATION", ""),
        ("UBO_ADD1", ""),
        ("UBO_ADD2", ""),
        ("UBO_ADD3", ""),
        ("UBO_CITY", ""),
        ("UBO_PIN", ""),
        ("UBO_STATE", ""),
        ("UBO_CNTRY", ""),
        ("UBO_ADD_TY", ""),
        ("UBO_CTR", ""),
        ("UBO_TIN", ""),
        ("UBO_ID_TY", ""),
        ("UBO_COB", ""),
        ("UBO_DOB", ""),
        ("UBO_GENDER", ""),
        ("UBO_FR_NAM", ""),
        ("UBO_OCC", ""),
        ("UBO_OCC_TY", ""),
        ("UBO_TEL", ""),
        ("UBO_MOBILE", ""),
        ("UBO_CODE", ""),
        ("UBO_HOL_PC", ""),
        ("SDF_FLAG", ""),
        ("UBO_DF", "N"),  # TODO: logic for individual and non-individuals
        ("AADHAAR_RP", ""),
        ("NEW_CHANGE", "C"),
        ("LOG_NAME", kyc.user_id),
        ("DOC1", ""),
        ("DOC2", ""),
    ]

    # prepare the param field to be returned
    fatca_param = ""
    for param in param_list:
        fatca_param = fatca_param + "|" + str(param[1])
    # print fatca_param
    return fatca_param[1:]


def soap_get_password_upload_service(client):
    # Define the headers
    wsa = "{http://www.w3.org/2005/08/addressing}"
    header = xsd.Element(
        "{http://bsestarmf.in/}Action",
        xsd.ComplexType(
            [
                xsd.Element(wsa + "Action", xsd.String()),
                xsd.Element(wsa + "To", xsd.String()),
            ]
        ),
    )
    header_value = header(
        Action="https://bsestarmfdemo.bseindia.com/IStarMFWebService/getPassword",
        To="https://bsestarmfdemo.bseindia.com/StarMFWebService/StarMFWebService.svc/Secure",
    )

    body = {
        "UserId": os.environ.get("USER_ID"),
        "MemberId": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "PassKey": os.environ.get("USER_PASSKEY"),
    }
    response = client.service.getPassword(_soapheaders=[header_value], **body).split(
        "|"
    )
    if response[0] == "101":
        raise Exception(response[1])

    # Return the password
    return response[1]



def soap_star_mf_web_service_mfapi(flag: str, param: str):
    client, history = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    password = soap_get_password_upload_service(client=client)

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/MFAPI",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )
    
    body = {
        "Flag": flag,
        "UserId": os.environ.get("USER_ID"),
        "EncryptedPassword": password,
        "param": param,
    }

    response = client.service.MFAPI(_soapheaders=[header_value], **body).split("|")
    if response[0] != "100":
        raise Exception(response[1])
    
        # Send the SOAP request
    if history.last_sent:
        raw_xml = history.last_sent["envelope"]

        # Pretty-print the XML
        print("Request XML (Formatted):")
        print(etree.tostring(raw_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    # Print the raw response XML
    if history.last_received:
        raw_response_xml = history.last_received["envelope"]
        print("Response XML (Formatted):")
        print(etree.tostring(raw_response_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    return response[1]


def soap_upload_fatca(client_code: str):
    param = prepare_fatca_param(client_code=client_code)
    response = soap_star_mf_web_service_mfapi("01", param)

    return response


def soap_create_mandate(
        client_code:str,
        amount:str,
        bank_account_no:str,
        bank_ifsc_code:str,
        bank_account_type:str,
        start_date:str,
        end_date:str,
        mandate_type: str = "N"
):
    param_list = (
        client_code,
        amount,
        mandate_type,
        bank_account_no,
        bank_account_type,
        bank_ifsc_code,
        "",
        start_date,
        end_date
    )
    user_param = ""
    for param in param_list:
        user_param = user_param + "|" + str(param)

    response = soap_star_mf_web_service_mfapi("06", user_param[1:])

    return response


def soap_order_payment_status(
    client_code: str,
    order_no: str,
    segment: str = "BSEMF",
):
    param = f"{client_code}|{order_no}|{segment}"

    response = soap_star_mf_web_service_mfapi("11", param)
    return response


def soap_payment_gateway(
    client_code: str,
    member_code: str,
    logout_url: str,
):
    param = f"{member_code}|{client_code}|{logout_url}"
    response = soap_star_mf_web_service_mfapi("03", param)
    return response

    
def prepare_payload_for_bse_call(user):
    kyc = KycDetail.objects.filter(user=user).first()
    bank = BankDetail.objects.filter(user=user).first()

    payload = {
        "UserId": os.environ.get("USER_ID"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "RegnType": "NEW",
        "Param": prepare_user_param(user, kyc, bank),
    }

    return payload


def register_client_on_bse(payload):
    url = "https://bsestarmf.in/StarMFCommonAPI/ClientMaster/Registration"

    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}
    response = requests.post(url=url, headers=header, json=payload)
    print(response.json())
    return response


def get_indian_address_parms(kyc):
    if kyc.citizen_type == "RI":
        add1 = kyc.address[:30]
        if len(kyc.address) > 30:
            add2 = kyc.address[30:60]
            if len(kyc.address) > 60:
                add3 = kyc.address[60:90]
            else:
                add3 = ""
        else:
            add2 = add3 = ""
        return [
            ("ADDRESS_1", add1),
            ("ADDRESS_2", add2),
            ("ADDRESS_3", add3),
            ("CITY", kyc.city),
            ("STATE", kyc.state),
            ("PINCODE", kyc.pincode),
            ("COUNTRY", kyc.country),
        ]
    else:
        return [
            ("ADDRESS_1", ""),
            ("ADDRESS_2", ""),
            ("ADDRESS_3", ""),
            ("CITY", ""),
            ("STATE", ""),
            ("PINCODE", ""),
            ("COUNTRY", ""),
        ]
    

def get_foreign_address_parms(kyc):
    if kyc.citizen_type == "NRI":
        add1 = kyc.address[:30]
        if len(kyc.address) > 30:
            add2 = kyc.address[30:60]
            if len(kyc.address) > 60:
                add3 = kyc.address[60:90]
            else:
                add3 = ""
        else:
            add2 = add3 = ""
        return [
            ("FOREIGN_ADD_1", add1),
            ("FOREIGN_ADD_2", add2),
            ("FOREIGN_ADD_3", add3),
            ("FOREIGN_CITY", kyc.city),
            ("FOREIGN_PINCODE", kyc.pincode),
            ("FOREIGN_STATE", kyc.state),
            ("FOREIGN_COUNTRY", kyc.country),
            ("FOREIGN_PHONE", ""),
            ("FOREIGN_FAX", ""),
            ("FOREIGN_OFF_PHONE", ""),
            ("FOREIGN_OFF_FAX", ""),
        ]
    else:
        return [
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
        ]




def prepare_param_for_client_creation(user, kyc, banks):

    bank_params = []
    for i, bank in enumerate(banks[:5], start=1):
        suffix = f"_{i}" if i > 1 else ""
        bank_params.extend([
            (f"ACCOUNT_TYPE{suffix}", bank.account_type),
            (f"ACCOUNT_NO{suffix}", bank.account_number),
            (f"MICR_NO{suffix}", ""),
            (f"IFSC{suffix}", bank.ifsc_code),
            ("DEFAULT_BANK", "Y" if i == 1 else "N"),
        ])
    
    # Fill remaining slots if less than 5 banks
    for i in range(len(banks) + 1, 6):
        suffix = f"_{i}"
        bank_params.extend([
            (f"ACCOUNT_TYPE{suffix}", ""),
            (f"ACCOUNT_NO{suffix}", ""),
            (f"MICR_NO{suffix}", ""),
            (f"IFSC{suffix}", ""),
            ("DEFAULT_BANK", ""),
        ])

    indian_address = get_indian_address_parms(kyc)
    foreign_address = get_foreign_address_parms(kyc)

    param_list = [
        ("UCC", kyc.client_code),
        ("FIRSTNAME", user.first_name),
        ("MIDDLENAME", user.middle_name),
        ("LASTNAME", user.last_name),
        ("TAX_STATUS", kyc.tax_status), # Need to map
        ("GENDER", kyc.gender),
        ("DOB", kyc.dob),
        ("OCCUPATION_CODE", kyc.occ_code), # Need to map
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
        *bank_params,
        ("CHEQUE_NAME", ""),
        ("DIV_PAY_MODE", "02"),
        *indian_address,
        ("RESI_PHONE", ""),
        ("RESI_FAX", ""),
        ("OFFICE_PHONE", ""),
        ("OFFICE_FAX", ""),
        ("EMAIL", user.email),
        ("COMM_MODE", "E"),
        *foreign_address,
        ("INDIAN_MOB_NO", kyc.phone),
        ("NOMINEE_NAME", kyc.nominee_name),
        ("NOMINEE_RELATION", kyc.nominee_relation),
        ("NOMINEE_APPLICABLE", "100"),
        ("MINOR_FLAG", "N"),
        ("NOMINEE_DOB", ""),
        ("NOMINEE_GUARDIAN", ""),
        ("NOMINEE_2_NAME", ""),
        ("NOMINEE_2_RELATION", ""),
        ("NOMINEE_2_APPLICABLE", ""),
        ("NOMINEE_2_DOB", ""),
        ("NOMINEE_2_MINOR_FLAG", ""),
        ("NOMINEE_2_GUARDIAN", ""),
        ("NOMINEE_3_NAME", ""),
        ("NOMINEE_3_RELATION", ""),
        ("NOMINEE_3_APPLICABLE", ""),
        ("NOMINEE_3_DOB", ""),
        ("NOMINEE_3_MINOR_FLAG", ""),
        ("NOMINEE_3_GUARDIAN", ""),
        ("KYC_TYPE", kyc.kyc_type),
        ("CKYC_NUMBER", ""),
        ("S_KYC_TYPE", ""),
        ("S_CKYC_NUMBER", ""),
        ("T_KYC_TYPE", ""),
        ("T_CKYC_NUMBER", ""),
        ("G_KYC_TYPE", ""),
        ("G_CKYC_NUMBER", ""),
        ("KRA_EXEMPT_REF_NO", ""),
        ("S_KRA_EXEMPT_REF_NO", ""),
        ("T_KRA_EXEMPT_REF_NO", ""),
        ("G_KRA_EXEMPT_REF_NO", ""),
        ("AADHAAR_UPDATED", ""),
        ("MAPIN_ID", ""),
        ("PAPERLESS_FLAG", kyc.paperless_flag),
        ("LEI_NO", ""),
        ("LEI_VALIDITY", ""),
        ("MOBILE_DECLARATION", "SE" if kyc.phone else ""),
        ("EMAIL_DECLARATION", "SE"),
        ("NOMINATION_OPT", "Y"),
        ("NOMINATION_AUTH_MODE", "O"),
        ("NOMINEE_PAN1", ""),
        ("NOMINEE_GUARDIAN_PAN1", ""),
        ("NOMINEE_PAN2", ""),
        ("NOMINEE_GUARDIAN_PAN2", ""),
        ("NOMINEE_PAN3", ""),
        ("NOMINEE_GUARDIAN_PAN3", ""),
        ("S_EMAIL", ""),
        ("S_EMAIL_DECLARATION", ""),
        ("S_MOBILE_NO", ""),
        ("S_MOBILE_DECLARATION", ""),
        ("T_EMAIL", ""),
        ("T_EMAIL_DECLARATION", ""),
        ("T_MOBILE_NO", ""),
        ("T_MOBILE_DECLARATION", ""),
    ]
    print(param_list)

    user_param = ""
    for param in param_list:
        user_param = user_param + "|" + str(param[1])

    print(user_param)
    return user_param[1:]


def soap_bse_create_client(user, kyc, bank, regn_type="NEW"):
    url = f"{BSE_URL}BSEMFWEBAPI/api/ClientRegistration/Registration"
    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    payload = {
        "UserId": os.environ.get("USER_ID"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "RegnType": regn_type,
        "Param": prepare_param_for_client_creation(user, kyc, bank),
    }

    response = requests.post(url=url, headers=header, json=payload)

    return response.json()


def rest_bse_authenticate_nominee(client_code):
    url = "https://bsestarmf.in/BSEMFWEBAPI/api/_2FANOMINEEController/_2FANOMINEE/w"

    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    body = {
        "LoginId" : os.environ.get("USER_ID"),
        "Password" : os.environ.get("USER_PASSWORD"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "clientCode" : client_code,
        "InternalRefrenceNo" :" ",
        "AllowLoopBack":"Y",
        "Filler1" :"1",
        "Filler2" :" ",
        "Filler3" :" " ,
        "LoopbackReturnUrl" :"https://sbnri.com/p/banking",
        "type" :"NOMINEE"
    }

    response = requests.post(url, headers=header, json=body)
    return response.json()

def authenticate_nominee(user):
    url = "https://bsestarmf.in/BSEMFWEBAPI/api/mfupload/Registation/w"

    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    params = [
        {"ClientCode": f"T{user.pk}", "NominationOpt": "Y", "NominationAuthMode": "O"}
    ]

    payload = {
        "Type": "NOMINEE",
        "UserId": os.environ.get("USER_ID"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "RegnType": "NEW",
        "Param": params,
    }

    response = requests.post(url=url, headers=header, json=payload)

    return response


def soap_get_password_order(client):
    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/getPassword",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    # Define the body
    body = {
        "UserId": os.environ.get("USER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "PassKey": os.environ.get("USER_PASSKEY"),
    }

    # Call the service method
    response = client.service.getPassword(_soapheaders=[header_value], **body).split(
        "|"
    )
    if response[0] == "101":
        raise Exception(response[1])

    # Return the password
    return response[1]


def prepare_trans_number(transaction):
    """
    The goal is to send a unique transaction code for each order
    I'll do it by combining today's date with the primary key of
    the created transaction.
    """
    today_str = datetime.now().strftime("%Y%m%d")
    trans_code = today_str + "000000" + str(transaction.id)
    return trans_code

BSE_URL = "https://bsestarmf.in/"
def soap_bse_transaction(
    client_code,
    scheme_code,
    mobile_no="",
    email_id="",
    amount="",
    units="",
    order_type="P",
    folio="",
    order_id="",
    all_redeem="N",
    trans_code="NEW",
    remarks="",
):
    # trans_no, trans_code, order_type, client_code, scheme_code, order_value, order_id=None

    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure",
    )

    password = soap_get_password_order(client)

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/orderEntryParam",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    trans_no = random_num_with_N_digits(10)

    # Prepare the payload
    payload = {
        "TransCode": trans_code,
        "TransNo": trans_no,
        "OrderId": order_id,
        "UserID": os.environ.get("USER_ID"),
        "MemberId": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "SchemeCd": scheme_code,
        "BuySell": order_type,
        "BuySellType": "FRESH",  # TODO: We decide the type of it dynamically, based on existing folio.
        "DPTxn": "P",
        "OrderVal": amount,
        "Qty": units,
        "AllRedeem": all_redeem,  # TODO: Not providing this feature for now
        "FolioNo": folio,  # TODO: Would need to put a check for this, if already invested in a fund house(or atleast a fund.), we'll need to send that portfolio.
        "Remarks": remarks,
        "KYCStatus": "Y",
        "RefNo": trans_code,
        "SubBrCode": None,
        "EUIN": None,
        "EUINVal": "N",
        "MinRedeem": "N",
        "DPC": "Y",
        "IPAdd": None,
        "Password": password,
        "PassKey": os.environ.get("USER_PASSKEY"),
        "Parma1": None,
        "Param2": None,
        "Param3": None,
        "MobileNo": mobile_no,
        "EmailID": email_id,
        "MandateID": None,
        "Filler1": None,
        "Filler2": None,
        "Filler3": None,
        "Filler4": None,
        "Filler5": None,
        "Filler6": None,
    }
    print(payload)
    # Send the SOAP request
    response = client.service.orderEntryParam(_soapheaders=[header_value], **payload)
    BSERequest.objects.create(
        payload=payload,
        response=response,
    )
    # save transaction number and order id to the transaction object after successful
    # completion.
    return response


def prepare_transaction(data, user, **kwargs):
    transaction_code = kwargs.get("transaction_code", "NEW")
    if transaction_code not in {"NEW", "CXL"}:
        raise Exception("Transaction code must be either NEW or CXL")

    transaction_type = data.get("transaction_type", "P")
    if transaction_type not in {"P", "R"}:
        raise Exception("Transaction type must be either P or R")

    order_id = data.get("order_id", "")
    prev_transaction = Transaction.objects.filter(order_id=order_id).first()
    if not prev_transaction:
        raise Exception("Invalid order_id")
    prev_transaction.is_deleted = True # soft delete the transaction.

    # Create initial transaction object
    transaction = Transaction(
        transaction_code=transaction_code,
        transaction_type=transaction_type,
        order_id=order_id,
    )

    if transaction_code == "NEW":
        try:
            scheme_code = data["scheme_code"]
            amount = data["amount"]
        except KeyError:
            raise Exception("scheme_code and amount are required!")

        # Validate scheme_code
        scheme = MutualFundList.objects.filter(scheme_code=scheme_code).first()
        if not scheme:
            raise Exception("Invalid scheme_code")

        # Validate amount
        try:
            amount = float(amount)
        except ValueError:
            raise Exception("Amount must be a valid number")
    else:
        scheme = prev_transaction.scheme_plan
        amount = prev_transaction.amount

    # Set validated data to transaction object
    transaction.scheme_plan = scheme
    transaction.amount = amount

    transaction.user = user

    # Save the transaction
    transaction.save()

    return transaction


def create_transaction(data, user, **kwargs):
    # Prepare the transaction object
    transaction = prepare_transaction(data, user, **kwargs)

    # Make the transaction with BSE
    soap_response = soap_bse_transaction(transaction=transaction).split("|")

    order_id = soap_response[2]
    trans_no = soap_response[1]
    message = soap_response[-2]
    if order_id == "0":
        raise Exception(message)

    # Save on succsfull transaction placement # TODO: Also save order date.
    transaction.bse_trans_no = trans_no
    transaction.order_id = order_id
    transaction.save()

    return message


def soap_bse_order_status(
    from_date: str,
    to_date: str,
    client_code: str = "",
    order_no: str = "",
    trans_type: str = "ALL",
    order_status: str = "ALL"
):
    client, history = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/OrderStatus",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    # Prepare the payload
    payload = {
        "Param": {
            "ClientCode": client_code,
            "Filler1": "",
            "Filler2": "",
            "Filler3": "",
            "FromDate": from_date,
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
            "OrderNo": order_no,
            "OrderStatus": order_status,
            "OrderType": "ALL",
            "Password": os.environ.get("USER_PASSWORD"),
            "SettType": "ALL",
            "SubOrderType": "ALL",
            "ToDate": to_date,
            "TransType": trans_type,
            "UserId": os.environ.get("USER_ID"),
        }
    }

    # Send the SOAP request
    response = client.service.OrderStatus(_soapheaders=[header_value], **payload)
    if history.last_sent:
        raw_xml = history.last_sent["envelope"]

        # Pretty-print the XML
        print("Request XML (Formatted):")
        print(etree.tostring(raw_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    # Print the raw response XML
    if history.last_received:
        raw_response_xml = history.last_received["envelope"]
        print("Response XML (Formatted):")
        print(etree.tostring(raw_response_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))
    
    return response


def soap_bse_allotment_statement(
    from_date: str = "",
    to_date: str = "",
    client_code: str = "",
    order_no: str = "",
    order_status: str = "VALID"
):
    client, history = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/AllotmentStatement",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    payload = {
        "Param": {
            "ClientCode": client_code,
            "Filler1": "",
            "Filler2": "",
            "Filler3": "",
            "FromDate": from_date,
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
            "OrderNo": order_no,
            "OrderStatus": order_status,
            "OrderType": "ALL",
            "Password": os.environ.get("USER_PASSWORD"),
            "SettType": "ALL",
            "SubOrderType": "ALL",
            "ToDate": to_date,
            "UserId": os.environ.get("USER_ID")
        }
    }

    response = client.service.AllotmentStatement(_soapheaders=[header_value], **payload)

    # Send the SOAP request
    if history.last_sent:
        raw_xml = history.last_sent["envelope"]

        # Pretty-print the XML
        print("Request XML (Formatted):")
        print(etree.tostring(raw_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    # Print the raw response XML
    if history.last_received:
        raw_response_xml = history.last_received["envelope"]
        print("Response XML (Formatted):")
        print(etree.tostring(raw_response_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))
    

    return response


def soap_bse_redemption_statement(
        from_date, 
        to_date, 
        client_code="",
        order_no="", 
        order_status="ALL", 
        order_type="ALL", 
        sett_type="ALL", 
        sub_order_type="ALL"
):
    client, history = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )
    header_values = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/RedemptionStatement",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    payload = {
        "Param": {
            "ClientCode": client_code,
            "Filler1": "",
            "Filler2": "",
            "Filler3": "",
            "FromDate": from_date,
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
            "OrderNo": order_no,
            "OrderStatus": order_status,
            "OrderType": order_type,
            "Password": os.environ.get("USER_PASSWORD"),
            "SettType": sett_type,
            "SubOrderType": sub_order_type,
            "ToDate": to_date,
            "UserId": os.environ.get("USER_ID")
        }
    }

    response = client.service.RedemptionStatement(_soapheaders=[header_values], **payload)

    # Send the SOAP request
    if history.last_sent:
        raw_xml = history.last_sent["envelope"]

        # Pretty-print the XML
        print("Request XML (Formatted):")
        print(etree.tostring(raw_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    # Print the raw response XML
    if history.last_received:
        raw_response_xml = history.last_received["envelope"]
        print("Response XML (Formatted):")
        print(etree.tostring(raw_response_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    return response


def soap_bse_xsip_order_entry(
    client_code: str,
    scheme_code: str,
    start_date: str,
    mandate_id: str,
    amount: str,
    first_order_today: str = "Y",
    transaction_type: str = "NEW",
    unique_ref_no: str = "",
    xsip_regn_id: str = "",
    frequency_type: str = "MONTHLY"
):
    # can do this via REST as well!!!
    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    password = soap_get_password_order(client=client)

    headers = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/xsipOrderEntryParam",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    if not unique_ref_no:
        unique_ref_no = random_num_with_N_digits(10)

    payload = {
        "TransactionCode": transaction_type,
        "UniqueRefNo": unique_ref_no,
        "SchemeCode": scheme_code,# "8019-GR",
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "UserId": os.environ.get("USER_ID"),
        "InternalRefNo": "",
        "TransMode": "P",
        "DpTxnMode": "P",
        "StartDate": start_date,
        "FrequencyType": frequency_type,
        "FrequencyAllowed": "1",
        "InstallmentAmount": amount,
        "NoOfInstallment": "20", # TODO
        "Remarks": "",
        "FolioNo": "",
        "FirstOrderFlag": first_order_today,
        "Brokerage": "",
        "MandateID": mandate_id,
        "SubberCode": "",
        "Euin": "",
        "EuinVal": "N",
        "DPC": "",
        "XsipRegID": xsip_regn_id,
        "IPAdd": "",
        "Password": password,
        "PassKey": os.environ.get("USER_PASSKEY"),
        "Param1": "",
        "Param2": "",
        "Param3": "",
        "Filler1": "",
        "Filler2": "",
        "Filler3": "",
        "Filler4": "",
        "Filler5": "",
        "Filler6": "",
    }

    response = client.service.xsipOrderEntryParam(_soapheaders=[headers], **payload)
    return response


def soap_get_password_for_child_orders(client):
    headers = create_zeep_headers(
        action_url="http://www.bsestarmf.in/IStarMFWebService/GetPasswordForChildOrder",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure",
    )
    payload = {
        "Param": {
            "RequestType":"CHILDORDER",
            "UserId": os.environ.get("USER_ID"),
            "MemberId": os.environ.get("USER_MEMBER_ID"),
            "Password": os.environ.get("USER_PASSWORD"),
            "PassKey": os.environ.get("USER_PASSKEY")
        }   
    }

    response = client.service.GetPasswordForChildOrder(
        _soapheaders=[headers], **payload
    )
    response_obj = serialize_object(response)

    if not response_obj.get("Status") or response_obj.get("Status") != "100":
        raise Exception(response.get("ResponseString"))

    return response_obj["ResponseString"]


def soap_get_child_order_details(client_code: str, regn_no: str):
    # Giving date is compulsory!

    secure_url = "https://bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
    client, _ = create_zeep_client(
        wsdl_url="https://bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=secure_url
    )

    password = soap_get_password_for_child_orders(client)

    headers = create_zeep_headers(
        action_url="http://www.bsestarmf.in/2016/01/IStarMFWebService/ChildOrderDetails",
        secure_url=secure_url
    )

    payload = {
        "Param": {
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
            "EncryptedPassword": password,
            "ClientCode": client_code,
            "Date": date,
            "RegnNo": regn_no,
            "SystematicPlanType": "XSIP"
        }
    }

    response = client.service.ChildOrderDetails(
        _soapheaders=[headers],
        **payload
    )

    return response


def rest_starmf_xsip_registration(
    scheme_cd: str,
    client_code: str,
    installment_amount: float,
    mandate_id: str,
    no_of_installments: int = 20,
    internal_ref_no: str = "",
    folio_no: str = "",
    euin: str = "",
    first_order_flag: str = "Y",
    start_date: str = None
):
    url = f"{BSE_URL}StarMFAPI/api/XSIP/XSIPRegistration"
    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }
    
    # Use today's date if start_date is not provided
    start_date = start_date if start_date else datetime.today().strftime('%d/%m/%Y')
    
    # Determine EUINDECLARATIONFLAG based on the presence of EUIN
    euin_flag = "Y" if euin else "N"
    
    # Build the payload
    payload = {
        "LoginId": os.environ.get("USER_ID"),         # To be replaced with actual login ID
        "MemberCode": os.environ.get("USER_MEMBER_ID"),     # To be replaced with actual member ID
        "Password": os.environ.get("USER_PASSWORD"),        # To be replaced with actual password
        "SchemeCode": scheme_cd,
        "ClientCode": client_code,
        "IntRefNo": internal_ref_no,
        "TransMode": "P",                   # Constant value for demat/physical
        "DPTransMode": "P",                 # Constant value for CDSL/NSDL/PHYSICAL
        "StartDate": start_date,
        "FrequencyType": "MONTHLY",         # Constant value
        "FrequencyAllowed": "1",            # Constant value
        "InstAmount": str(installment_amount),  # Convert float to string
        "NoOfInst": str(no_of_installments),   # Convert int to string
        "Remarks": "",                      # Default empty string
        "FolioNo": folio_no,                # Empty unless provided
        "FirstOrderFlag": first_order_flag,
        "SubBrCode": "",                    # Default empty string
        "EUIN": euin,
        "EUINFlag": euin_flag,
        "DPC": "Y",                         # Constant value
        "SubBrokerARN": "",                 # Default empty string
        "EndDate": "",                      # Default empty string
        "RegnType": "XSIP",                 # Constant value
        "Brokerage": "",                    # Default empty string
        "MandateId": mandate_id,
        "XSIPType": "01",                   # Constant value
        "TargetScheme": "",                 # Default empty string
        "TargetAmount": "",                 # Default empty string
        "GoalType": "",                     # Default empty string
        "GoalAmount": "",                   # Default empty string
        "Filler1": "",                      # Default empty string
        "Filler2": "",                      # Default empty string
        "Filler3": "",                      # Default empty string
        "Filler4": "",                      # Default empty string
        "Filler5": "",                      # Default empty string
        "Filler6": ""                       # Default empty string
    }

    response = requests.post(url, headers=headers, json=payload)
    
    return response.json()
    

def rest_starmf_cancel_xsip(client_code, regn_no, internal_ref_number:str = ""):
    url = "https://bsestarmf.in/StarMFAPI/api/XSIP/XSIPCancellation"
    
    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }
    
    payload = {
        "LoginId": os.environ.get("USER_ID"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "ClientCode": client_code,
        "RegnNo": regn_no,
        "IntRefNo": internal_ref_number,
        "CeaseBseCode": "07",
        "Remarks": ""
    }

    response = requests.post(url, headers=headers, json=payload)

    return response.json()

def rest_starmf_pause_xsip(
    client_code: str,
    regn_no: str,
    regn_type: str = "XSIP",
    no_of_installment: str = "999",
):
    url=f"{BSE_URL}StarMFAPI/api/Pause/PauseSIP"

    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }

    payload = {
        "LoginId" : os.environ.get("USER_ID"),
        "MemberCode" : os.environ.get("USER_MEMBER_ID"),
        "Password" : os.environ.get("USER_PASSWORD"),
        "ClientCode" : client_code,
        "RegistrationType" : regn_type,
        "RegistrationNumber" : regn_no,
        "ModificationType" : "PAUSE",
        "NoOfInstalments" : no_of_installment,
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.json()

    
def soap_create_switch_order_entry(
    client_code: str,
    folio_no: str,
    from_scheme_code: str,
    to_scheme_code: str,
    amount: str = "",
    trans_code: str = "NEW",
    order_id: str = "",
    all_units_flag: str = "Y",
):
    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )
    password = soap_get_password_order(client=client)

    headers = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/switchOrderEntryParam",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    trans_no = random_num_with_N_digits(10)
    payload = {
        "TransCode": trans_code,
        "TransNo": trans_no,
        "OrderId": order_id,
        "UserId": os.environ.get("USER_ID"),
        "MemberId": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "FromSchemeCd": from_scheme_code,
        "ToSchemeCd": to_scheme_code,
        "BuySell": "SO",
        "BuySellType": "FRESH",
        "DPTxn": "P",
        "OrderVal": amount,
        "SwitchUnits": "",
        "AllUnitsFlag": all_units_flag,
        "FolioNo": folio_no,
        "Remarks": "",
        "KYCStatus": "Y",
        "SubBrCode": "",
        "EUIN": "",
        "EUINVal": "N",
        "MinRedeem": "N",
        "IPAdd": "",
        "Password": password,
        "PassKey": os.environ.get("USER_PASSKEY"),
        "Parma1": "",
        "Param2": "",
        "Param3": "",
        "Filler1": "",
        "Filler2": "",
        "Filler3": "",
        "Filler4": "",
        "Filler5": "",
        "Filler6": ""
    }

    response = client.service.switchOrderEntryParam(_soapheaders=[headers], **payload)
    return response


def soap_get_starmfwebservice_access_token(client):
    headers = create_zeep_headers(
        action_url="https://bsestarmfdemo.bseindia.com/IStarMFWebService/GetAccessToken",
        secure_url="https://bsestarmfdemo.bseindia.com/StarMFWebService/StarMFWebService.svc/Secure",
    )
    payload = {
        "Param": {
            "RequestType":"MANDATE",
            "UserId": os.environ.get("USER_ID"),
            "MemberId": os.environ.get("USER_MEMBER_ID"),
            "Password": os.environ.get("USER_PASSWORD"),
            "PassKey": os.environ.get("USER_PASSKEY")
        }
    }

    response = client.service.GetAccessToken(
        _soapheaders=[headers], **payload
    )
    response_obj = serialize_object(response)

    if not response_obj.get("Status") or response_obj.get("Status") != "100":
        raise Exception(response.get("ResponseString"))

    return response_obj["ResponseString"]


def soap_get_mandate_status(client_code, from_date, to_date, mandate_id=""):
    client, history = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure",
    )
    header_values = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/MandateDetails",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure",
    )

    password = soap_get_starmfwebservice_access_token(client=client)
    #envelope = history.last_sent["envelope"]
    # print(etree.tostring(envelope, pretty_print=True, encoding="unicode"))

    payload = {
        "Param": {
            "EncryptedPassword": password,
            "FromDate": from_date,
            "ToDate": to_date,
            "ClientCode": client_code,
            "MandateId": mandate_id,
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
        }
    }

    response = client.service.MandateDetails(
        _soapheaders=[header_values], **payload
    )

        # Send the SOAP request
    if history.last_sent:
        raw_xml = history.last_sent["envelope"]

        # Pretty-print the XML
        print("Request XML (Formatted):")
        print(etree.tostring(raw_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    # Print the raw response XML
    if history.last_received:
        raw_response_xml = history.last_received["envelope"]
        print("Response XML (Formatted):")
        print(etree.tostring(raw_response_xml, pretty_print=True, encoding='utf-8').decode('utf-8'))

    return response


def soap_get_enach_mandate_auth(client_code: str, mandate_id: str):
    secure_url = f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=secure_url
    )
    headers = create_zeep_headers(
        action_url=f"{BSE_URL}2016/01/IStarMFWebService/EMandateAuthURL",
        secure_url=secure_url
    )

    payload = {
        "Param": {
            "UserId": os.environ.get("USER_ID"),
            "MemberCode": os.environ.get("USER_MEMBER_ID"),
            "Password": os.environ.get("USER_PASSWORD"),
            "ClientCode": client_code,
            "MandateID": mandate_id

        }
    }

    response = client.service.EMandateAuthURL(
        _soapheaders=[headers],
        **payload
    )

    return response


def create_zeep_client(wsdl_url, secure_url):
    session = Session()
    session.headers.update(
        {
            "Content-Type": "application/soap+xml;charset=UTF-8",
            "Accept": "application/soap+xml",
        }
    )

    # Create a transport object with the session
    transport = Transport(session=session)
    history = HistoryPlugin()
    client = Client(
        wsdl=wsdl_url,
        transport=transport,
        plugins=[history]
    )
    client.service._binding_options["address"] = (
        secure_url
    )

    return client, history


def create_zeep_headers(action_url, secure_url):
    wsa = "{http://www.w3.org/2005/08/addressing}"
    header = xsd.Element(
        f"{{BSE_URL}}Action",
        xsd.ComplexType(
            [
                xsd.Element(wsa + "Action", xsd.String()),
                xsd.Element(wsa + "To", xsd.String()),
            ]
        ),
    )
    header_value = header(
        Action=action_url,
        To=secure_url,
    )
    return header_value


def soap_bse_swp_order_entry(
    client_code: str,
    scheme_code: str,
    folio_number: str,
    start_date: str,
    number_of_withdrawals: int,
    installment_amount: float,
    internal_ref_number: str,
    bank_account_no: str,
    installment_units: float = "",
    first_order_today: str = "Y",
    frequency_type: str = "MONTHLY",
    transaction_mode: str = "P",
    sub_broker_code: str = "",
    euin_declaration: str = "N",
    euin_number: str = "",
    remarks: str = "",
    sub_broker_arn: str = "",
    mobile_no: str = "",
    email_id: str = "",
):
    param_list = [
        ("CLIENT_CODE", client_code),
        ("SCHEME_CODE", scheme_code),
        ("TRANS_MODE", transaction_mode),
        ("FOLIO_NO", folio_number),
        ("INTERNAL_REF_NO", internal_ref_number),
        ("START_DATE", start_date),
        ("NUM_WITHDRAWALS", str(number_of_withdrawals)),
        ("FREQ_TYPE", frequency_type),
        ("AMOUNT", str(installment_amount)),
        ("UNITS", str(installment_units)),
        ("FIRST_ORDER_TODAY", first_order_today),
        ("SUB_BR_CODE", sub_broker_code),
        ("EUIN_DECL", euin_declaration),
        ("EUIN", euin_number),
        ("REMARKS", remarks),
        ("SUB_BR_ARN", sub_broker_arn),
        ("MOBILE_NO", mobile_no),
        ("EMAIL", email_id),
        ("BANK_ACC_NO", bank_account_no),
    ]

    swp_param = ""
    for param in param_list:
        swp_param = swp_param + "|" + str(param[1])
    
    param =  swp_param[1:]
    
    response = soap_star_mf_web_service_mfapi("08", param)
    
    return response


def prepare_swp_cancellation_param(swp_registration_no: str, client_code: str, remarks: str):
    param_list = [
        ("SWP_REG_NO", swp_registration_no),
        ("CLIENT_CODE", client_code),
        ("REMARKS", remarks),
    ]

    swp_cancel_param = ""
    for param in param_list:
        swp_cancel_param = swp_cancel_param + "|" + str(param[1])
    
    return swp_cancel_param[1:]


def soap_cancel_swp_order(swp_registration_no: str, client_code: str, remarks: str = ""):
    param = prepare_swp_cancellation_param(swp_registration_no, client_code, remarks)
    
    response = soap_star_mf_web_service_mfapi("10", param)
    
    return response

from xml.dom.minidom import parseString

def pretty_print_xml(xml_string):
    # Parse the XML string
    dom = parseString(xml_string)
    
    # Pretty-print the XML with indentation
    pretty_xml = dom.toprettyxml(indent="  ")
    
    # Remove empty lines
    pretty_xml = '\n'.join([line for line in pretty_xml.split('\n') if line.strip()])
    
    return pretty_xml

def rest_bse_image_upload(client_code: str):
    image_name = os.environ.get("USER_MEMBER_ID") + client_code + ".pdf"
    pdf_path = "user_cheque_images/" + image_name
    url = f"{BSE_URL}StarMFImageUpload/api/ImageUpload/ImageUploadBase64"
    
    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }
    
    # Read the PDF file and convert it to Base64
    try:
        with open(pdf_path, "rb") as pdf_file:
            base64_string = base64.b64encode(pdf_file.read()).decode('utf-8')
    except FileNotFoundError:
        raise Exception(f"PDF file not found at {pdf_path}")
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")
    
    payload = {
        "UserID": os.environ.get("USER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "ImageName": image_name,
        "Base64String": base64_string,
        "Filler1": "",
        "Filler2": ""
    }
    print(payload)
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error making API request: {str(e)}")

def rest_bse_image_upload_byte(client_code: str):
    image_name = os.environ.get("USER_MEMBER_ID") + client_code + ".pdf"
    pdf_path = "user_cheque_images/" + image_name
    url = f"{BSE_URL}StarMFImageUpload/api/ImageUpload/ImageUploadByte"
    
    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }
    
    # Read the PDF file and convert it to an unsigned byte array
    try:
        with open(pdf_path, "rb") as pdf_file:
            byte_array = list(pdf_file.read())
    except FileNotFoundError:
        raise Exception(f"PDF file not found at {pdf_path}")
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")
    
    payload = {
        "UserID": os.environ.get("USER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "ImageName": image_name,
        "ByteArray": byte_array,
        "Filler1": "",
        "Filler2": ""
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error making API request: {str(e)}")

# Example usage:
# response = rest_bse_image_upload_byte("CLIENT001")
# print(response)

from typing import List, Optional
import uuid

def rest_single_payment_gateway(
    client_code: str,
    account_number: str,
    ifsc: str,
    order_ids: List[str],
    total_amount: str,
    mode_of_payment: str,
    bank_code: str,
    vpa_id: Optional[str] = None,
):
    url = f"{BSE_URL}StarMFSinglePaymentAPI/Single/Payment"
    
    headers = {
        "APIKey": "VmxST1UyRkhUbkpOVldNOQ==",
        "Content-Type": "application/json"
    }
    
    order_number = "|".join(order_ids)
    
    payload = {
        "LoginId": os.environ.get("USER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "membercode": os.environ.get("USER_MEMBER_ID"),
        "clientcode": client_code,
        "modeofpayment": mode_of_payment,
        "bankid": bank_code,
        "accountnumber": account_number,
        "ifsc": ifsc,
        "ordernumber": order_number,
        "totalamount": total_amount,
        "internalrefno": str(uuid.uuid4())[:10],  # Generate a unique reference number
        "NEFTreference": "",
        "mandateid": "",
        "vpaid": vpa_id if mode_of_payment == "UPI" else "",
        "loopbackURL": "https://sbnri.com/p/banking",
        "allowloopBack": "Y",
        "filler1": "",
        "filler2": "",
        "filler3": "",
        "filler4": "",
        "filler5": ""
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error making API request: {str(e)}")