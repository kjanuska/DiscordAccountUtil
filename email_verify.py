import requests
import verification

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
        catpcha_key = verification.get_captcha_key("verify")
        data["captcha_key"] = catpcha_key
        resp = requests.post(
            f"{globals.ENTRY}{VERIFY_ENDPOINT}", headers=header, json=data
        )
