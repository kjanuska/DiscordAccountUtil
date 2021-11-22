import requests
import time

import phone_verify
import environment

def init():
    phone_verify.get_bearer_token()

def get_captcha_key(url_endpoint):
    SITE_KEY = "f5561ba9-8f1e-40ca-9b5b-a0b3f719ef34"
    resp = requests.post(
        f"http://2captcha.com/in.php?key={environment.CAP_API_KEY}&method=hcaptcha&sitekey={SITE_KEY}&pageurl=https://discord.com/{url_endpoint}&json=1"
    ).json()
    if resp["status"] != 1:
        print("Error sending catpcha to provider:\n" + resp)
        return
    captcha_id = resp["request"]
    time.sleep(20)
    resp = requests.get(
        f"http://2captcha.com/res.php?key={environment.CAP_API_KEY}&action=get&id={captcha_id}&json=1"
    ).json()
    while resp["status"] == 0:
        time.sleep(5)
        resp = requests.get(
            f"http://2captcha.com/res.php?key={environment.CAP_API_KEY}&action=get&id={captcha_id}&json=1"
        ).json()

    return resp["request"]