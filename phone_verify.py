import requests
import time
import math

import globals
import errors

TEXT_ENTRY = "https://www.textverified.com/api"
TEXT_ACCESS_TOKEN = globals.TEXT_API_KEY

bearer_token = ""
last_call = time.time()

def get_bearer_token():
    global bearer_token
    global last_call
    AUTHENTICATION_ENDPOINT = "/SimpleAuthentication"
    header = {"X-SIMPLE-API-ACCESS-TOKEN": TEXT_ACCESS_TOKEN}
    resp = requests.post(
        f"{TEXT_ENTRY}{AUTHENTICATION_ENDPOINT}", headers=header
    ).json()
    last_call = time.time()
    bearer_token = resp["bearer_token"]


def update_bearer_token():
    # token expires in 1 hour
    hours = (time.time() - last_call) / (60 * 60)
    # check if roughly 50 minutes have passed
    if (hours + 0.16) > 1:
        get_bearer_token()


def get_balance():
    USER_ENDPOINT = "/Users"
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    resp = requests.get(f"{TEXT_ENTRY}{USER_ENDPOINT}", headers=header).json()
    return resp["credit_balance"]


def get_cost():
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    resp = requests.get(f"{TEXT_ENTRY}/Targets/19", headers=header).json()
    return resp["cost"]


def available_verifications():
    update_bearer_token()
    return math.floor(get_balance() / get_cost())


def request_phone_number():
    VERIFICATION_ENDPOINT = "/Verifications"
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    data = {
        "id": 19
    }
    resp = requests.post(f"{TEXT_ENTRY}{VERIFICATION_ENDPOINT}", json=data, headers=header)

    if resp.status_code == 402:
        raise errors.InsufficientCredits

    request_id = resp.json()["id"]
    phone_number = resp.json()["number"]
    return [phone_number, request_id]

def get_code(request_id):
    VERIFICATION_ENDPOINT = f"/Verifications/{request_id}"
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    resp = requests.get(f"{TEXT_ENTRY}{VERIFICATION_ENDPOINT}", headers=header).json()
    while resp["status"] == "Pending":
        time.sleep(5)
        resp = requests.get(f"{TEXT_ENTRY}{VERIFICATION_ENDPOINT}", headers=header).json()
    
    return resp["code"]


def verify_phone(token):
    # verify phone number
    PHONE_ENDPOINT = "/users/@me/phone"
    header = {
        "authorization": token,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    }
    update_bearer_token()
    verification_info = request_phone_number()
    data = {"phone": verification_info[0]}

    # send code to phone number
    resp = requests.post(f"{globals.ENTRY}{PHONE_ENDPOINT}", headers=header, json=data)
    time.sleep(5)
    CODE_ENDPOINT = "/phone-verifications/verify"
    # get code from Text Verified
    code = get_code(verification_info[1])
    data["code"] = code

    # send verification code
    resp = requests.post(f"{globals.ENTRY}{CODE_ENDPOINT}", headers=header, json=data)
    if resp.status_code == 400:
        print("Verification code incorrect")
