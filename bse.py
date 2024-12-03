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
from sbnribanking.logging import custom_slack_logging
from investment_tracker.models import Mutual_Fund_Tracker


BSE_URL = "https://bsestarmf.in/"
BSE_PASSWORD = "Sbnri@2pass"
BSE_USER_ID = "5972901"
BSE_MEMBER_ID = "59729"
BSE_PASS_KEY = "Freedom"

INCOME_SLAB_MAP = {
    "Below Rs. 1 Lac": "31",
    "Rs. 1-5 Lac": "32",
    "Rs. 5-10 Lacs": "33",
    "Rs. 10-25 Lacs": "34",
    "Rs. 25 Lacs to 1 Crore": "35",
    "Above Rs. 1 Crore": "36"
}

TAX_STATUS_MAP = {
    "individual": "01",
    "company": "04",
}

STATE_CODE_MAP = {
    "andaman and nicobar": "AN",
    "arunachal pradesh": "AR",
    "andhra pradesh": "AP",
    "assam": "AS",
    "bihar": "BH",
    "chandigarh": "CH",
    "chhattisgarh": "CG",
    "delhi": "DL",
    "goa": "GO",
    "gujarat": "GU",
    "haryana": "HA",
    "himachal pradesh": "HP",
    "jammu and kashmir": "JM",
    "jharkhand": "JK",
    "karnataka": "KA",
    "kerala": "KE",
    "madhya pradesh": "MP",
    "maharashtra": "MA",
    "manipur": "MN",
    "meghalaya": "ME",
    "mizoram": "MI",
    "nagaland": "NA",
    "new delhi": "ND",
    "orissa": "OR",
    "others": "OH",
    "pondicherry": "PO",
    "punjab": "PU",
    "rajasthan": "RA",
    "sikkim": "SI",
    "telangana": "TG",
    "tamil nadu": "TN",
    "tripura": "TR",
    "uttar pradesh": "UP",
    "uttarakhand": "UL",
    "west bengal": "WB",
    "dadra and nagar haveli": "DN",
    "daman and diu": "DD",
    "lakshadweep": "LD"
}

OCCUPATION_CODE_MAP = {
    "business": "01",
    "service": "02",
    "professional": "03",
    "agriculturist": "04",
    "retired": "05",
    "housewife": "06",
    "student": "07",
    "others": "08",
    "doctor": "09",
    "private_sector_service": "41",
    "public_sector_service": "42",
    "forex_dealer": "43",
    "government_service": "44",
    "unknown_not_applicable": "99"
}

GENDER_MAP = {
    "Male": "M",
    "Female": "F",
    "Other": "O",
}


def create_zeep_client(wsdl_url: str, secure_url: str):
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
        "{http://bsestarmf.in/}Action",
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


def random_num_with_N_digits(n):

    from random import randint

    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def create_username():
    import time

    username = str(random_num_with_N_digits(6)) + str(time.time())[:4]

    return username


def prepare_fatca_param(kyc_tracker, kyc_detail):
    # extract the records from the table
    user = kyc_tracker.user
    # some fields require processing
    inv_name = user.first_name
    if user.last_name != "":
        inv_name = inv_name + " " + user.last_name
    inv_name = inv_name[:70]

    kyc_detail["tax_status_code"] = TAX_STATUS_MAP.get(kyc_detail.get("type", "individual"), "01")
    kyc_detail["occ_code"] = OCCUPATION_CODE_MAP.get(kyc_detail.get("income_source").lower(), "")
    kyc_detail["income_slab"] = INCOME_SLAB_MAP.get(kyc_detail.get("income_slab"), "34")

    if kyc_detail["occ_code"] == "01":
        srce_wealt = "02"
        occ_type = "B"
    else:
        srce_wealt = "01"
        occ_type = "S"

    # make the list that will be used to create param
    param_list = [
        ("PAN_RP", kyc_tracker.pan),
        ("PEKRN", ""),
        ("INV_NAME", inv_name),
        ("DOB", ""),
        ("FR_NAME", ""),
        ("SP_NAME", ""),
        ("TAX_STATUS", kyc_detail.get("tax_status_code")),
        ("DATA_SRC", "E"),
        ("ADDR_TYPE", "1"),
        ("PO_BIR_INC", "IN"),
        ("CO_BIR_INC", "IN"),
        ("TAX_RES1", "IN"),
        ("TPIN1", kyc_tracker.pan),
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
        ("INC_SLAB", kyc_detail.get("income_slab")),
        ("NET_WORTH", ""),
        ("NW_DATE", ""),
        ("PEP_FLAG", "N"),
        ("OCC_CODE", kyc_detail.get("occ_code")),
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
        ("NEW_CHANGE", "N"),
        ("LOG_NAME", inv_name),
        ("DOC1", ""),
        ("DOC2", ""),
    ]

    # prepare the param field to be returned
    fatca_param = ""
    for param in param_list:
        fatca_param = fatca_param + "|" + str(param[1])
    # print fatca_param
    return fatca_param[1:]


def bse_get_upload_password(client):
    # Define the headers
    wsa = "{http://www.w3.org/2005/08/addressing}"
    header = xsd.Element(
        "{https://bsestarmfdemo.bseindia.com/}Action",
        xsd.ComplexType(
            [
                xsd.Element(wsa + "Action", xsd.String()),
                xsd.Element(wsa + "To", xsd.String()),
            ]
        ),
    )
    header_value = header(
        Action=f"{BSE_URL}IStarMFWebService/getPassword",
        To=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure",
    )

    body = {
        "UserId": "5972901",
        "MemberId": "59729",
        "Password": BSE_PASSWORD,
        "PassKey": "12345"
    }
    response = client.service.getPassword(_soapheaders=[header_value], **body).split(
        "|"
    )
    if response[0] == "101":
        raise Exception(response[1])

    # Return the password
    return response[1]


def bse_mf_api_request(flag: str, param: str):
    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    password = bse_get_upload_password(client=client)

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}IStarMFWebService/MFAPI",
        secure_url=f"{BSE_URL}StarMFWebService/StarMFWebService.svc/Secure"
    )

    body = {
        "Flag": flag,
        "UserId": "5972901",
        "EncryptedPassword": password,
        "param": param,
    }

    response = client.service.MFAPI(_soapheaders=[header_value], **body).split("|")
    if response[0] != "100":
        raise Exception(response[1])

    return response[1]


def bse_upload_fatca(kyc_tracker, kyc_detail):
    param = prepare_fatca_param(kyc_tracker, kyc_detail)
    response = bse_mf_api_request("01", param)

    return response


def bse_create_mandate(
        client_code:str,
        amount:str,
        bank_account_no:str,
        bank_ifsc_code:str,
        bank_account_type:str,
        start_date:str,
        end_date:str
):
    param_list = (
        client_code,
        amount,
        "N",
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

    response = bse_mf_api_request("06", user_param[1:])

    return response


def bse_get_order_payment_status(
    client_code: str,
    order_no: str,
    segment: str = "BSEMF",
):
    param = f"{client_code}|{order_no}|{segment}"

    response = bse_mf_api_request("11", param)
    return response


def prepare_param_for_client_creation(kyc_tracker, user_details, nominee, bank):
    # TODO: Rename the kyc_detail function
    kyc_tracker.bse_client_id = "SB" + str(kyc_tracker.user.pk)
    kyc_tracker.save()
    user = kyc_tracker.user

    address = user_details.get("address")
    add1 = address[:30]
    if len(address) > 30:
        add2 = address[30:60]
        if len(address) > 60:
            add3 = address[60:90]
        else:
            add3 = ""
    else:
        add2 = add3 = ""

    user_details["tax_status_code"] = TAX_STATUS_MAP.get(user_details.get("type", "individual"), "01")
    user_details["state_code"] = STATE_CODE_MAP.get(user_details.get("state", "").strip().lower())
    user_details["occ_code"] = OCCUPATION_CODE_MAP.get(user_details.get("income_source").lower(), "")
    user_details["gender"] = GENDER_MAP.get(user_details.get("gender"), "")

    param_list = [
        ("UCC", kyc_tracker.bse_client_id),
        ("FIRSTNAME", user.firstname), # TODO
        ("MIDDLENAME", ""), # Need to think about this from app perspective
        ("LASTNAME", user.lastname),
        ("TAX_STATUS", user_details.get("tax_status_code")),
        ("GENDER", user_details.get("gender")),
        ("DOB", user_details.get("dob")),
        ("OCCUPATION_CODE", user_details.get("occ_code")),
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
        ("PAN", kyc_tracker.pan),
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
        ("ACCOUNT_TYPE", "SB"), # TODO
        ("ACCOUNT_NO", bank.get("account_number")),
        ("MICR_NO", ""),
        ("IFSC", bank.get("ifsc_code")),
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
        ("CITY", user_details.get("city")),
        ("STATE", user_details.get("state_code")),
        ("PINCODE", user_details.get("pincode")),
        ("COUNTRY", "India"),
        ("RESI_PHONE", ""),
        ("RESI_FAX", ""),
        ("OFFICE_PHONE", ""),
        ("OFFICE_FAX", ""),
        ("EMAIL", user.emailid),
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
        ("INDIAN_MOB_NO", user.mobile_no),
        ("NOMINEE_NAME", nominee.nominee_name),
        ("NOMINEE_RELATION", nominee.nominee_relation),
        ("NOMINEE_APPLICABLE", nominee.nominee_share),
        ("MINOR_FLAG", "Y" if nominee.is_nominee_minor else "N"),
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
        ("KYC_TYPE", "E"),
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
        ("PAPERLESS_FLAG", "Z"),
        ("LEI_NO", ""),
        ("LEI_VALIDITY", ""),
        ("MOBILE_DECLARATION", "SE"),
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


    user_param = ""
    for param in param_list:
        user_param = user_param + "|" + str(param[1])

    from sbnribanking.logging import custom_slack_logging
    custom_slack_logging(channel_name="core-dev-logs", data=user_param)
    print(user_param)
    return user_param[1:]


def bse_create_client(kyc_tracker, kyc_details, nominee_details, bank_details):
    from sbnribanking.logging import custom_slack_logging

    custom_slack_logging(channel_name="core-dev-logs", data="Inside soap_bse_create_client")
    # url = "https://bsestarmf.in/BSEMFWEBAPI/api/ClientRegistration/Registration"
    url = f"{BSE_URL}BSEMFWEBAPI/api/ClientRegistration/Registration"
    header = {"APIKey": "VmxST1UyRkhUbkpOVldNOQ==", "Content-Type": "application/json"}

    payload = {
        "UserId": "5972901",
        "MemberCode": "59729",
        "Password": BSE_PASSWORD,
        "RegnType": "NEW",
        "Param": prepare_param_for_client_creation(kyc_tracker, kyc_details, nominee_details, bank_details)
    }
    try:
        response = requests.post(url=url, headers=header, json=payload)
    except Exception as e:
        custom_slack_logging(channel_name="core-dev-logs", data=f"Something went wrong: {str(e)}")

    try:
        response = response.json()
    except:
        response = response.text
    custom_slack_logging(channel_name="core-dev-logs", data=response)
    return response

def bse_get_order_password(client):
    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/getPassword",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    # Define the body
    body = {
        "UserId": "5972901",
        "Password": BSE_PASSWORD,
        "PassKey": '8569519126'
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


class BSETransactionResponse:
    def __init__(self, status, transaction_no, message, order_id=""):
        self.status = status
        self.transaction_no = transaction_no
        self.message = message
        self.order_id = order_id


def get_mutual_fund_tracker_email(user):
    """
    Retrieve the investor email from Mutual Fund Tracker.
    """
    tracker = Mutual_Fund_Tracker.objects.filter(user=user).first()
    if tracker:
        return tracker.investor_email
    return None


def prepare_bse_order_payload(
    trans_no, client_code, scheme_code, amount, units, order_type, folio, 
    order_id, all_redeem, trans_code, password, mobile_no, email_id, additional_buy
):
    """
    Prepare the payload for the BSE order entry API call.
    """
    return {
        "TransCode": trans_code,
        "TransNo": trans_no,
        "OrderId": order_id,
        "UserID": BSE_USER_ID,
        "MemberId": BSE_MEMBER_ID,
        "ClientCode": client_code,
        "SchemeCd": scheme_code,
        "BuySell": order_type,
        "BuySellType": "FRESH" if not additional_buy else "ADDITIONAL",
        "DPTxn": "P",
        "OrderVal": amount,
        "Qty": units,
        "AllRedeem": all_redeem,
        "FolioNo": folio,
        "Remarks": None,
        "KYCStatus": "Y",
        "RefNo": None,
        "SubBrCode": None,
        "EUIN": None,
        "EUINVal": "N",
        "MinRedeem": "N",
        "DPC": "Y",
        "IPAdd": None,
        "Password": password,
        "PassKey": BSE_PASS_KEY,
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


def bse_order_entry(
    user,
    client_code,
    scheme_code,
    amount,
    units="",
    order_type="P",
    folio="",
    order_id="",
    all_redeem="N",
    trans_code="NEW",
    additional_buy=False,
):
    """
    Function to create a new Buy/Redeem order in BSE.
    """
    try:
        client, _ = create_zeep_client(
            wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
            secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure",
        )
        password = bse_get_order_password(client)
        header_value = create_zeep_headers(
            action_url=f"{BSE_URL}MFOrderEntry/orderEntryParam",
            secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
        )

        trans_no = random_num_with_N_digits(10)

        mobile_no = user.mobile_no
        email_id = user.emailid

        # Redeem order checks
        if order_type == "R":
            amount = None
            if all_redeem == "Y":
                units = None

            tracker_email = get_mutual_fund_tracker_email(user)
            if tracker_email:
                email_id = tracker_email
                mobile_no = None

        payload = prepare_bse_order_payload(
            trans_no, client_code, scheme_code, amount, units, order_type, folio, 
            order_id, all_redeem, trans_code, password, mobile_no, email_id, additional_buy
        )

        custom_slack_logging(f"Sending BSE order with TransNo {trans_no} and payload: {payload}")

        response = client.service.orderEntryParam(_soapheaders=[header_value], **payload)
        response_parts = response.split("|")

        custom_slack_logging(f"BSE order successful with response: {response}")

        response_obj = BSETransactionResponse(
            status=response_parts[-1],
            transaction_no=response_parts[1],
            message=response_parts[-2],
            order_id=response_parts[2]
        )

        return response_obj

    except Exception as e:
        # Log the error for debugging purposes
        custom_slack_logging(f"Error while processing BSE order: {str(e)}", level="error")
        return None

def bse_order_entry(
    user,
    client_code,
    scheme_code,
    amount,
    units="",
    order_type="P",
    folio="",
    order_id="",
    all_redeem="N",
    trans_code="NEW",
    additional_buy=False,
):
    '''
        This function is used to create a new Buy/Redeem order entry
    '''
    # trans_no, trans_code, order_type, client_code, scheme_code, order_value, order_id=None

    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure",
    )

    password = bse_get_order_password(client)

    header_value = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/orderEntryParam",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    trans_no = random_num_with_N_digits(10)

    # Some checks for redeem order
    mobile_no = user.mobile_no
    email_id = user.emailid
    if order_type == "R":
        amount = None
        if all_redeem == "Y":
            units = None

        # TODO: I think the investor email should be given with args.
        # Wrong logic, btw.
        tracker = Mutual_Fund_Tracker.objects.filter(user=user).first()
        if tracker:
            email_id = tracker.investor_email
            mobile_no = None

    # Prepare the payload
    payload = {
        "TransCode": trans_code,
        "TransNo": trans_no,
        "OrderId": order_id,
        "UserID": "5972901",
        "MemberId": "59729",
        "ClientCode": client_code,
        "SchemeCd": scheme_code,
        "BuySell": order_type,
        "BuySellType": "FRESH" if not additional_buy else "ADDITIONAL",  # TODO: We decide the type of it dynamically, based on existing folio.
        "DPTxn": "P",
        "OrderVal": amount,
        "Qty": units,
        "AllRedeem": all_redeem,  # TODO: Not providing this feature for now
        "FolioNo": folio,  # TODO: Would need to put a check for this, if already invested in a fund house(or atleast a fund.), we'll need to send that portfolio.
        "Remarks": None,
        "KYCStatus": "Y",
        "RefNo": None,
        "SubBrCode": None,
        "EUIN": None,
        "EUINVal": "N",
        "MinRedeem": "N",
        "DPC": "Y",
        "IPAdd": None,
        "Password": password,
        "PassKey": "8569519126",
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
    # Send the SOAP request
    custom_slack_logging(channel_name="core-dev-logs", data=f"payload: {payload}")
    response = client.service.orderEntryParam(_soapheaders=[header_value], **payload)
    response_parts = response.split("|")

    response_obj = BSETransactionResponse(
        status=response_parts[-1],
        transaction_no=response_parts[1],
        message=response_parts[-2],
        order_id=response_parts[2]
    )

    # save transaction number and order id to the transaction object after successful
    # completion.
    return response_obj


def bse_order_status(
    from_date: str,
    to_date: str,
    client_code: str = "",
    order_no: str = "",
    trans_type: str = "ALL",
    order_status: str = "ALL"
):
    client, _ = create_zeep_client(
        wsdl_url="https://bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url="https://bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
    )

    header_value = create_zeep_headers(
        action_url="https://bsestarmf.in/IStarMFWebService/OrderStatus",
        secure_url="https://bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
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

    return response


def bse_allotment_statement(
    from_date: str = "",
    to_date: str = "",
    client_code: str = "",
    order_no: str = "",
    order_status: str = "VALID"
):
    client, _ = create_zeep_client(
        wsdl_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
    )

    header_value = create_zeep_headers(
        action_url="http://www.bsestarmf.in/IStarMFWebService/AllotmentStatement",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
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
    return response


def bse_redemption_statement(
        from_date, 
        to_date, 
        client_code="",
        order_no="", 
        order_status="ALL", 
        order_type="ALL", 
        sett_type="ALL", 
        sub_order_type="ALL"
):
    client, _ = create_zeep_client(
        wsdl_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
    )
    header_values = create_zeep_headers(
        action_url="http://www.bsestarmf.in/IStarMFWebService/RedemptionStatement",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
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
    return response


def bse_xsip_order_entry(
    client_code: str,
    scheme_code: str,
    start_date: str,
    mandate_id: str,
    amount: str,
    first_order_today: str = "Y",
):
    # can do this via REST as well!!!
    client, _ = create_zeep_client(
        wsdl_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    password = bse_get_order_password(client=client)

    headers = create_zeep_headers(
        action_url=f"{BSE_URL}MFOrderEntry/xsipOrderEntryParam",
        secure_url=f"{BSE_URL}MFOrderEntry/MFOrder.svc/Secure"
    )

    unique_ref_no = random_num_with_N_digits(10)

    payload = {
        "TransactionCode": "NEW",
        "UniqueRefNo": unique_ref_no,
        "SchemeCode": scheme_code,# "8019-GR",
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": client_code,
        "UserId": os.environ.get("USER_ID"),
        "InternalRefNo": "",
        "TransMode": "P",
        "DpTxnMode": "P",
        "StartDate": start_date,
        "FrequencyType": "MONTHLY",
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
        "XsipRegID": "",
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


def bse_get_child_order_password(client):
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


def bse_get_child_order_details(client_code: str, regn_no: str):
    # Giving date is compulsory!

    secure_url = "https://bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure"
    client, _ = create_zeep_client(
        wsdl_url="https://bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=secure_url
    )

    password = bse_get_child_order_password(client)

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

def bse_cancel_xsip(client_code, regn_no, internal_ref_number:str = ""):
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


def bse_create_switch_order_entry(
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
        wsdl_url="https://bsestarmf.in/MFOrderEntry/MFOrder.svc?singleWsdl",
        secure_url="https://bsestarmf.in/MFOrderEntry/MFOrder.svc/Secure"
    )
    password = bse_get_order_password(client=client)

    headers = create_zeep_headers(
        action_url="http://bsestarmf.in/MFOrderEntry/switchOrderEntryParam",
        secure_url="https://bsestarmf.in/MFOrderEntry/MFOrder.svc/Secure"
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


def bse_get_starmfwebservice_access_token(client):
    headers = create_zeep_headers(
        action_url="http://www.bsestarmf.in/IStarMFWebService/GetAccessToken",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure",
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


def bse_get_mandate_status(client_code, from_date, to_date, mandate_id=""):
    client, history = create_zeep_client(
        wsdl_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure",
    )
    header_values = create_zeep_headers(
        action_url="http://www.bsestarmf.in/IStarMFWebService/MandateDetails",
        secure_url="https://www.bsestarmf.in/StarMFWebService/StarMFWebService.svc/Secure",
    )

    password = bse_get_starmfwebservice_access_token(client=client)
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

    return response


def bse_get_enach_mandate_auth_url(client_code: str, mandate_id: str):
    secure_url = "https://bsestarmfdemo.bseindia.com/StarMFWebService/StarMFWebService.svc/Secure"
    client, _ = create_zeep_client(
        wsdl_url="https://bsestarmfdemo.bseindia.com/StarMFWebService/StarMFWebService.svc?singleWsdl",
        secure_url=secure_url
    )
    headers = create_zeep_headers(
        action_url="https://bsestarmfdemo.bseindia.com/2016/01/IStarMFWebService/EMandateAuthURL",
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
        "{http://bsestarmf.in/}Action",
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