import json
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
    update_bearer_token()
    USER_ENDPOINT = "/Users"
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    resp = requests.get(f"{TEXT_ENTRY}{USER_ENDPOINT}", headers=header).json()
    return resp["credit_balance"]


def get_cost():
    update_bearer_token()
    header = {
        "Authorization": f"Bearer {bearer_token}"
    }
    resp = requests.get(f"{TEXT_ENTRY}/Targets/19", headers=header).json()
    return resp["cost"]


def max_available():
    return math.floor(get_balance() / get_cost())


def get_code():
    update_bearer_token()
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
        


def get_captcha_key(url_endpoint):
    SITE_KEY = "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"
    resp = requests.post(
        f"http://2captcha.com/in.php?key={globals.CAP_API_KEY}&method=hcaptcha&sitekey={SITE_KEY}&pageurl=https://discord.com/{url_endpoint}&json=1"
    ).json()
    if resp["status"] != 1:
        print("Error sending catpcha to provider:\n" + resp)
        return
    captcha_id = resp["request"]
    time.sleep(20)
    resp = requests.get(
        f"http://2captcha.com/res.php?key={globals.CAP_API_KEY}&action=get&id={captcha_id}&json=1"
    ).json()
    while resp["status"] == 0:
        time.sleep(5)
        resp = requests.get(
            f"http://2captcha.com/res.php?key={globals.CAP_API_KEY}&action=get&id={captcha_id}&json=1"
        ).json()

    return resp["request"]


def verify_email(token):
    # create account using catchall and then access verification link from main gmail

    VERIFY_ENDPOINT = "/auth/verify"
    # use gmail API to fetch emails and post a request to the verification URL
    header = {
        "authorization": token,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    }
    data = {"token": verification_token}

    resp = requests.post(f"{globals.ENTRY}{VERIFY_ENDPOINT}", headers=header, json=data)
    if resp.status_code == 400:
        catpcha_key = get_captcha_key("verify")
        data["captcha_key"] = catpcha_key
        resp = requests.post(
            f"{globals.ENTRY}{VERIFY_ENDPOINT}", headers=header, json=data
        )


def verify_phone(token):
    # verify phone number
    PHONE_ENDPOINT = "/users/@me/phone"
    header = {
        "authorization": token,
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    }
    data = {"phone": phone}

    # send code to phone number
    resp = requests.post(f"{globals.ENTRY}{PHONE_ENDPOINT}", headers=header, json=data)

    # get code from Text Verified

    # send verification code
    CODE_ENDPOINT = "/phone-verifications/verify"
    data["code"] = code

    resp = requests.post(f"{globals.ENTRY}{CODE_ENDPOINT}", headers=header, json=data)
    if resp.status_code == 400:
        print("Verification code incorrect")
