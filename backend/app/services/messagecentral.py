import os
import requests
from dotenv import load_dotenv

load_dotenv("/data/data/com.termux/files/home/Delyvo/backend/.env")

BASE_URL = "https://cpaas.messagecentral.com"


def send_otp(mobile_number):
    customer_id = os.getenv("MESSAGE_CENTRAL_CUSTOMER_ID")
    auth_token = os.getenv("MESSAGE_CENTRAL_AUTH_TOKEN")

    if not customer_id or not auth_token:
        raise RuntimeError("Message Central credentials are not configured")

    params = {
        "countryCode": "91",
        "customerId": customer_id,
        "mobileNumber": mobile_number,
        "flowType": "SMS",
        "otpLength": 6,
    }

    response = requests.post(
        f"{BASE_URL}/verification/v3/send",
        params=params,
        headers={
            "authToken": auth_token,
            "Accept": "application/json",
        },
        timeout=15,
    )

    response.raise_for_status()
    data = response.json()

    if data.get("responseCode") != 200:
        raise RuntimeError(
            data.get("message") or "Message Central OTP send failed"
        )

    result = data.get("data") or {}

    verification_id = result.get("verificationId")

    if not verification_id:
        raise RuntimeError("Message Central did not return verificationId")

    return {
        "verification_id": str(verification_id),
        "timeout": result.get("timeout"),
        "mobile_number": result.get("mobileNumber"),
    }


def verify_otp(verification_id, otp):
    auth_token = os.getenv("MESSAGE_CENTRAL_AUTH_TOKEN")

    if not auth_token:
        raise RuntimeError("Message Central auth token is not configured")

    params = {
        "verificationId": verification_id,
        "code": otp,
    }

    response = requests.get(
        f"{BASE_URL}/verification/v3/validateOtp",
        params=params,
        headers={
            "authToken": auth_token,
            "Accept": "application/json",
        },
        timeout=15,
    )

    response.raise_for_status()
    data = response.json()

    result = data.get("data") or {}

    return {
        "verified": result.get("verificationStatus") == "VERIFICATION_COMPLETED",
        "response": data,
    }
