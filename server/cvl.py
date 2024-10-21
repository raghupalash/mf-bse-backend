import base64
import requests
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# CVL configuration
CVL_CONFIG = {
    'dev': {
        'url': "https://krapancheck.cvlindia.com/V3/api/",
        'user_id': "websbnri",
        'password': "Cvlkra@1234",
        'aes_key': "3qygPsdo4w9bv24H3bQmt4asOpI0dwf6",
        'poscode': "SBNRI",
        'api_key': "78ba31fec82b405fb0ea60f85f0a0e95"
    },
    'prod': {
        'url': "https://api.kracvl.com/int/api/",
        'user_id': "webadmin",
        'password': "F1FC851485",
        'aes_key': "4c8c98585cfb425bb8ee3a003d535c8c",
        'poscode': "5100246671",
        'api_key': "79e59ff503f24f58a6cd38b17e94376b"
    }
}

# Set the current environment
CURRENT_ENV = 'prod'  # Change this to 'prod' when needed

# Use the configuration based on the current environment
cvl_url = CVL_CONFIG[CURRENT_ENV]['url']
cvl_user_id = CVL_CONFIG[CURRENT_ENV]['user_id']
cvl_password = CVL_CONFIG[CURRENT_ENV]['password']
cvl_aes_key = CVL_CONFIG[CURRENT_ENV]['aes_key']
cvl_poscode = CVL_CONFIG[CURRENT_ENV]['poscode']
cvl_api_key = CVL_CONFIG[CURRENT_ENV]['api_key']

# Services and codes
PAN_STATUS_SERVICES = {
    "CVLKRA": ["000", "001", "002", "003", "004", "005", "006", "007", "011", "012", "013", "014", "022", "888", "999"],
    "NDML": ["100", "101", "102", "103", "104", "105", "106", "107", "111", "112", "113", "114", "888", "999"],
    "DOTEX": ["200", "201", "202", "203", "204", "205", "206", "207", "211", "212", "213", "214", "888", "999"],
    "CAMS": ["300", "301", "302", "303", "304", "305", "306", "307", "311", "312", "313", "314", "888", "999"],
    "KARVY": ["400", "401", "402", "403", "404", "405", "406", "407", "411", "412", "413", "414", "888", "999"],
}

# Updated messages dictionary
PAN_STATUS_MESSAGES = {
    "00": "Not Checked with respective KRA",
    "01": "Submitted",
    "02": "KRA Verified",
    "03": "Hold",
    "04": "Rejected",
    "05": "Not available",
    "06": "Deactivated",
    "07": "KRA Validated",
    "11": "Existing KYC Submitted",
    "12": "Existing KYC Verified",
    "13": "Existing KYC hold",
    "14": "Existing KYC Rejected",
    "22": "KYC REGISTERED WITH CVLMF",
    "888": "Not Checked with Multiple KRA",
    "999": "Invalid PAN NO Format",
}

MISSING_FIELDS = {
    "00": "All mandatory fields available",
    "01": "Name of the Applicant not available",
    "02": "Fathers / Spouse Name not available",
    "03": "Gender not available",
    "04": "Marital Status not available",
    "05": "DOB not available",
    "06": "Nationality not available",
    "07": "Residential Status not available",
    "08": "Proof of Identity not available",
    "09": "Correspondence Address not available",
    "10": "Proof of Correspondence Address not available",
    "11": "Permanent Address not available",
    "12": "Proof of Permanent Address not available",
    "13": "Applicants Signature not available",
    "14": "IPV details not available",
    "15": "Date of Incorporation not available",
    "16": "Place of Incorporation not available",
    "17": "Date of commencement of business not available",
    "18": "Status (Non-Individual) not available",
    "19": "Number of Promoters/Partners/Karta/Trustees and whole-time directors not available",
    "20": "Name of related person not available",
    "21": "Relation with Applicant not available",
    "22": "Permanent Address of Related person not available",
    "23": "KYC Image is incomplete",
    "24": "Contact details are not available",
}

MODIFICATION_STATUS_SERVICES = {
    "CVLKRA": ["000", "001", "002", "003", "004", "005", "006", "007", "888"],
    "NDML": ["100", "101", "102", "103", "104", "105", "106", "107", "888"],
    "DOTEX": ["200", "201", "202", "203", "204", "205", "206", "207", "888"],
    "CAMS": ["300", "301", "302", "303", "304", "305", "306", "307", "888"],
    "KARVY": ["400", "401", "402", "403", "404", "405", "406", "407", "888"],
}

# Messages dictionary that maps each code to its respective message for all services
MODIFICATION_STATUS_MESSAGES = {
    "00": "Not Checked with Respective KRA",
    "01": "Modification Under Process",
    "02": "Modification Registered",
    "03": "Modification Hold",
    "04": "Modification Rejected",
    "05": "Not available (will not be displayed)",
    "06": "Deactivated",
    "07": "Modification Validated",
    "888": "Not Checked with Multiple KRA",
}

KYC_MODES = {
    "0": "Normal KYC",
    "1": "e-KYC with OTP",
    "2": "e-KYC with Biometric",
    "3": "Online Data Entry and IPV",
    "4": "Offline KYC - Aadhaar",
    "5": "Digi locker",
    "6": "Saral",
}

ADDRESS_PROOF = {
    "01": "PASSPORT",
    "02": "DRIVING LICENSE",
    "03": "LATEST BANK PASSBOOK",
    "04": "LATEST BANK ACCOUNT STATEMENT",
    "05": "LATEST DEMAT ACCOUNT STATEMENT",
    "06": "VOTER IDENTITY CARD",
    "07": "RATION CARD",
    "08": "REGISTERED LEASE / SALE AGREEMENT OF RESIDENCE",
    "09": "LATEST LAND LINE TELEPHONE BILL",
    "10": "LATEST ELECTRICITY BILL",
    "11": "GAS BILL",
    "12": "REGISTRATION CERTIFICATE ISSUED UNDER SHOPS AND ESTABLISHMENTS ACT",
    "13": "FLAT MAINTENANCE BILL",
    "14": "INSURANCE COPY",
    "15": "SELF DECLARATION BY HIGH COURT / SUPREME COURT JUDGE",
    "16": "POWER OF ATTORNEY GIVEN BY FII/SUB-ACCOUNT TO THE CUSTODIANS (WHICH ARE DULY NOTARISED AND/OR APOSTILED OR CONSULARISED) GIVING REGISTERED ADDRESS.",
    "17": "PROOF OF ADDRESS ISSUED BY SCHEDULED COMMERCIAL BANKS / SCHEDULED CO-OPERATIVE BANKS / MULTINATIONAL FOREIGN BANKS.",
    "18": "PROOF OF ADDRESS ISSUED BY ELECTED REPRESENTATIVES TO THE LEGISLATIVE ASSEMBLY",
    "19": "PROOF OF ADDRESS ISSUED BY PARLIAMENT",
    "20": "PROOF OF ADDRESS ISSUED BY ANY GOVERNMENT / STATUTORY AUTHORITY",
    "21": "PROOF OF ADDRESS ISSUED BY NOTARY PUBLIC",
    "22": "PROOF OF ADDRESS ISSUED BY GAZETTED OFFICER",
    "23": "ID CARD WITH ADDRESS ISSUED BY CENTRAL / STATE GOVERNMENT",
    "24": "ID CARD WITH ADDRESS ISSUED BY STATUTORY / REGULATORY AUTHORITIES",
    "25": "ID CARD WITH ADDRESS ISSUED BY PUBLIC SECTOR UNDERTAKINGS",
    "26": "ID CARD WITH ADDRESS ISSUED BY SCHEDULED COMMERCIAL BANKS",
    "27": "ID CARD WITH ADDRESS ISSUED BY PUBLIC FINANCIAL INSTITUTIONS",
    "28": "ID CARD WITH ADDRESS ISSUED BY COLLEGES AFFILIATED TO UNIVERSITIES",
    "29": "ID CARD ISSUED BY PROFESSIONAL BODIES SUCH AS ICAI, ICWAI, ICSI, BAR COUNCIL, ETC. TO THEIR MEMBERS",
    "31": "AADHAAR",
    "32": "ANY OTHER PROOF OF ADDRESS",
}


def encrypt_string(aes_key, data):
    # Convert the key to bytes if it's a string
    if isinstance(aes_key, str):
        aes_key = base64.b64decode(aes_key)
    
    # 1. Generate a random Initialization Vector (IV) for AES encryption
    iv = get_random_bytes(AES.block_size)
    
    # 2. Encrypt the plaintext string using AES/CBC/PKCS5 Padding
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    padded_data = pad(data.encode(), AES.block_size)
    encrypted_data = cipher.encrypt(padded_data)
    
    # 3. Create a string with IV and encrypted data separated by a colon ":"
    iv_str = base64.b64encode(iv).decode('utf-8')
    encrypted_str = base64.b64encode(encrypted_data).decode('utf-8')
    result = f"{iv_str}:{encrypted_str}"
    
    return result

def decrypt_string(aes_key, encrypted_string):
    try:
        # Convert the key to bytes if it's a string
        if isinstance(aes_key, str):
            aes_key = base64.urlsafe_b64decode(aes_key)
        
        # 1. Split response string by colon ":"
        iv_str, encrypted_str = encrypted_string.split(':')
        
        print(f"IV string: {iv_str}")
        print(f"IV string length: {len(iv_str)}")
        
        # 2. Get the IV and encrypted data
        try:
            iv = base64.urlsafe_b64decode(iv_str + '=' * (4 - len(iv_str) % 4))
            encrypted_data = base64.urlsafe_b64decode(encrypted_str + '=' * (4 - len(encrypted_str) % 4))
        except Exception as e:
            print(f"Error decoding IV or encrypted data: {str(e)}")
            return None
        
        # 3. Decrypt encrypted data using IV and Client's private key
        cipher = AES.new(aes_key, AES.MODE_CBC, iv)
        decrypted_data = cipher.decrypt(encrypted_data)
        unpadded_data = unpad(decrypted_data, AES.block_size)

        return unpadded_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {str(e)}")
        return None
    
import json
def dict_to_string(data_dict):
    return json.dumps(data_dict)

def string_to_dict(data_string):
    return json.loads(data_string)

def fetch_token():
    data_to_encrypt = dict_to_string({
        "username": cvl_user_id,
        "password": cvl_password,
        "poscode": cvl_poscode
    })
    encrypted_data = f'"{encrypt_string(cvl_aes_key, data_to_encrypt)}"'

    headers = {
        'api_key': cvl_api_key,
        'Content-Type': 'application/json'
    }

    url = cvl_url + "GetToken"
    response = requests.post(url, headers=headers, data=encrypted_data)

    try:
        response_data = response.json()

        try:
            response_data = string_to_dict(response_data)
            return response_data
        except:
            pass

        decrypted_data = decrypt_string(cvl_aes_key, response_data)
        return string_to_dict(decrypted_data)
    except Exception as e:
        return {"error": "Unexpected error", "message": str(e)}
    

def fetch_pan_status(pan_number: str):
    token = fetch_token().get("token")
    if not token:
        return {"error": "Token not found", "message": "Failed to generate token"}
    
    url = cvl_url + "GetPanStatus"
    headers = {
        "token": token,
        "Content-Type": "application/json"
    }
    payload = {
        "pan": pan_number,
        "poscode": cvl_poscode
    }

    encrypted_data = f'"{encrypt_string(cvl_aes_key, json.dumps(payload))}"'
    response = requests.post(url, headers=headers, data=encrypted_data)
    try:
        response_data = response.json()
        try:
            response_data = string_to_dict(response_data)
            return response_data
        except:
            pass

        decrypted_data = decrypt_string(cvl_aes_key, response_data)
        return string_to_dict(decrypted_data)
    except Exception as e:
        return {"error": "Unexpected error", "message": str(e)}


# Add messages for other services
def decode_pan_app_status(status_code: str): #-> Tuple[str, str]:
    if status_code == "":
        return "", ""

    if len(status_code) != 3:
        return "", "Invalid status code length"

    if status_code in PAN_STATUS_MESSAGES:
        return "", PAN_STATUS_MESSAGES[status_code]
    else:
        for service, codes in PAN_STATUS_SERVICES.items():
            if status_code in codes:
                return service, PAN_STATUS_MESSAGES[status_code[1:]]
    return "", "Message not found for this code"


def decode_missing_fields(status_code: str):
    if status_code == "":
        return ""

    if len(status_code) != 2:
        return "Invalid status code length"

    if status_code in MISSING_FIELDS:
        return MISSING_FIELDS[status_code]
    else:
        return "Message not found for this code"
    

def decode_modification_status(status_code: str):
    if status_code == "":
        return ""

    if len(status_code) != 3:
        return "Invalid status code length"

    if status_code in MODIFICATION_STATUS_MESSAGES:
        return "", MODIFICATION_STATUS_MESSAGES[status_code]
    else:
        for service, codes in MODIFICATION_STATUS_SERVICES.items():
            if status_code in codes:
                return service, MODIFICATION_STATUS_MESSAGES[status_code[1:]]
    return "", "Message not found for this code"
    

def decode_kyc_mode(code):
    if code == "":
        return ""

    return KYC_MODES.get(code, "Unknown KYC Mode")


def decode_address_proof(code):
    if code == "":
        return ""

    return ADDRESS_PROOF.get(code, "Unknown Address Proof")  # Default to "Unknown Code" if code is not found


from typing import Dict, Any

def prepare_pan_status_response(pan_status: Dict[str, Any]) -> Dict[str, Any]:
    app_pan_inq = pan_status.get('APP_PAN_INQ', {})
    app_pan_summ = pan_status.get('APP_PAN_SUMM', {})

    pan_status_code = app_pan_inq.get('APP_STATUS', '')
    pan_status_message = decode_pan_app_status(pan_status_code)

    update_status_code = app_pan_inq.get('APP_UPDT_STATUS', '')
    update_status_message = decode_modification_status(update_status_code)

    kyc_mode_code = app_pan_inq.get('APP_KYC_MODE', '')
    kyc_mode = decode_kyc_mode(kyc_mode_code)

    per_add_proof_code = app_pan_inq.get('APP_PER_ADD_PROOF', '')
    per_add_proof = decode_address_proof(per_add_proof_code)

    cor_add_proof_code = app_pan_inq.get('APP_COR_ADD_PROOF', '')
    cor_add_proof = decode_address_proof(cor_add_proof_code)

    missing_fields_code = app_pan_inq.get('APP_STATUS_DELTA', '')
    missing_fields = decode_missing_fields(missing_fields_code)

    return {
        "pan_number": app_pan_inq.get('APP_PAN_NO', ''),
        "name": app_pan_inq.get('APP_NAME', ''),
        "status": {
            "code": pan_status_code,
            "message": pan_status_message
        },
        "update_status": {
            "code": update_status_code,
            "message": update_status_message
        },
        "dates": {
            "status_date": app_pan_inq.get('APP_STATUSDT', ''),
            "entry_date": app_pan_inq.get('APP_ENTRYDT', ''),
            "modification_date": app_pan_inq.get('APP_MODDT', '')
        },
        "kyc_details": {
            "mode": {
                "code": kyc_mode_code,
                "description": kyc_mode
            },
            "ipv_flag": app_pan_inq.get('APP_IPV_FLAG', ''),
            "ubo_flag": app_pan_inq.get('APP_UBO_FLAG', '')
        },
        "address_proof": {
            "permanent": {
                "code": per_add_proof_code,
                "description": per_add_proof
            },
            "correspondence": {
                "code": cor_add_proof_code,
                "description": cor_add_proof
            }
        },
        "missing_fields": {
            "code": missing_fields_code,
            "description": missing_fields
        },
        "remarks": {
            "hold_deactivate": app_pan_inq.get('APP_HOLD_DEACTIVE_RMKS', ''),
            "update": app_pan_inq.get('APP_UPDT_RMKS', '')
        },
        "summary": {
            "batch_id": app_pan_summ.get('BATCH_ID', ''),
            "response_date": app_pan_summ.get('APP_RESPONSE_DATE', ''),
            "total_records": app_pan_summ.get('APP_TOTAL_REC', '')
        }
    }

def get_pan_status(pan_number: str):
    import time
    
    start_time = time.time()
    pan_status = fetch_pan_status(pan_number)
    end_time = time.time()
    
    fetch_time = end_time - start_time
    
    if pan_status.get("error") or pan_status.get("error_message"):
        pan_status['fetch_time'] = f"{fetch_time:.2f} seconds"
        return pan_status
    
    pan_status = string_to_dict(pan_status.get("resdtls"))
    result = prepare_pan_status_response(pan_status)
    result['fetch_time'] = f"{fetch_time:.2f} seconds"
    return result