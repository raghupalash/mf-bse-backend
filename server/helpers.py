import os
from random import randint
import requests
from zeep import Client, Plugin, xsd
from zeep.transports import Transport
from requests import Session
from lxml import etree
from datetime import datetime

from .models import BankDetail, KycDetail, Transaction, MutualFundList


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
            "client_code": "T" + str(user.pk)[:10],  # TODO: Prepare a better client code
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
        ("NEW_CHANGE", "N"),
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
        Action="http://bsestarmf.in/IMFUploadService/getPassword",
        To="https://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc/Secure",
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


def soap_upload_fatca(client_code):
    session = Session()
    session.headers.update(
        {
            "Content-Type": "application/soap+xml;charset=UTF-8",
            "Accept": "application/soap+xml",
        }
    )

    # Create a transport object with the session
    transport = Transport(session=session)
    client = Client(
        wsdl="https://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc?singleWsdl",
        transport=transport,
    )
    client.service._binding_options["address"] = (
        "https://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc/Secure"
    )

    password = soap_get_password_upload_service(client=client)

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
        Action="http://bsestarmf.in/IMFUploadService",
        To="https://bsestarmfdemo.bseindia.com/MFUploadService/MFUploadService.svc/Secure",
    )

    param = prepare_fatca_param(client_code=client_code)
    body = {
        "Flag": "01",
        "UserId": os.environ.get("USER_ID"),
        "EncryptedPassword": password,
        "param": param,
    }

    response = client.service.MFAPI(_soapheaders=[header_value], **body).split("|")
    if response[0] != "100":
        raise Exception(response[1])

    return response[1]


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
        "UserId": os.environ.get("USER_ID"),
        "MemberCode": os.environ.get("USER_MEMBER_ID"),
        "Password": os.environ.get("USER_PASSWORD"),
        "RegnType": "NEW",
        "Param": params,
    }

    response = requests.post(url=url, headers=header, json=payload)

    return response


def soap_get_password_order(client):
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
        Action="http://bsestarmf.in/MFOrderEntry/getPassword",
        To="https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure",
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


def soap_bse_transaction(transaction):
    # trans_no, trans_code, order_type, client_code, scheme_code, order_value, order_id=None
    # Create a session object
    session = Session()
    session.headers.update(
        {
            "Content-Type": "application/soap+xml;charset=UTF-8",
            "Accept": "application/soap+xml",
        }
    )

    # Create a transport object with the session
    transport = Transport(session=session)
    client = Client(
        wsdl="https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc?singleWsdl",
        transport=transport,
    )
    client.service._binding_options["address"] = (
        "https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure"
    )

    password = soap_get_password_order(client)

    trans_no = prepare_trans_number(transaction)

    # Set up the SOAP headers
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
        Action="http://bsestarmf.in/MFOrderEntry/orderEntryParam",
        To="https://bsestarmfdemo.bseindia.com/MFOrderEntry/MFOrder.svc/Secure",
    )

    # Prepare the payload
    payload = {
        "TransCode": transaction.transaction_code,  # TODO: NEW/CANCELLATION
        "TransNo": trans_no,
        "OrderId": None,
        "UserID": os.environ.get("USER_ID"),
        "MemberId": os.environ.get("USER_MEMBER_ID"),
        "ClientCode": transaction.user.kycdetail.client_code,
        "SchemeCd": transaction.scheme_plan.scheme_code,
        "BuySell": transaction.transaction_type,
        "BuySellType": "FRESH",  # TODO: We decide the type of it dynamically, based on existing folio.
        "DPTxn": "P",
        "OrderVal": transaction.amount,
        "Qty": None,
        "AllRedeem": "N",  # TODO: Not providing this feature for now
        "FolioNo": None,  # TODO: Would need to put a check for this, if already invested in a fund house(or atleast a fund.), we'll need to send that portfolio.
        "Remarks": None,
        "KYCStatus": "Y",
        "RefNo": None,
        "SubBrCode": None,
        "EUIN": None,
        "EUINVal": "N",
        "MinRedeem": "N",
        "DPC": "Y" if transaction.transaction_type == "P" else "N",
        "IPAdd": None,
        "Password": password,
        "PassKey": os.environ.get("USER_PASSKEY"),
        "Parma1": None,
        "Param2": None,
        "Param3": None,
        "MobileNo": None,
        "EmailID": None,
        "MandateID": None,
        "Filler1": None,
        "Filler2": None,
        "Filler3": None,
        "Filler4": None,
        "Filler5": None,
        "Filler6": None,
    }
    # Send the SOAP request
    response = client.service.orderEntryParam(_soapheaders=[header_value], **payload)

    # save transaction number and order id to the transaction object after successful
    # completion.
    return response


def prepare_transaction(data, user):

    # Create initial transaction object
    transaction = Transaction(
        transaction_code=data.get("transaction_code", "NEW"),
        transaction_type=data.get("transaction_type", "P"),
    )

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

    # Set validated data to transaction object
    transaction.scheme_plan = scheme
    transaction.amount = amount
    transaction.user = user

    # Save the transaction
    transaction.save()

    return transaction


def create_transaction(data, user):
    # prepare the transaction object, this function would be called from the view
    # with relavent data.
    # soap_bse_transaction
    # save the successful order to the transaction object and save it
    # will have to do something else fo sip, because sip doesn't have order_id
    # or maybe have a completly different system for sip (api + model) -
    # that would make things much easier for us.
    transaction = prepare_transaction(data, user)
    soap_response = soap_bse_transaction(transaction=transaction).split("|")
    order_id = soap_response[2]
    trans_no = soap_response[1]
    message = soap_response[-2]
    if order_id == "0":
        raise Exception(message)

    transaction.bse_trans_no = trans_no
    transaction.order_id = order_id
    transaction.save()

    return message
