import time
from random import randint
import requests

from .models import BankDetail, KycDetail


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
