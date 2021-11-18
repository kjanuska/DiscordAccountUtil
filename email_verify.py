import requests
import imaplib, email
from dotenv import load_dotenv
import os
import re
import verification
import quopri

load_dotenv()

USER = os.environ["GMAIL_USER"]
PASSWORD = os.environ["GMAIL_PASS"]
imap_url = "imap.gmail.com"

# this is done to make SSL connection with GMAIL
con = imaplib.IMAP4_SSL(imap_url)

# logging the user in
con.login(USER, PASSWORD)

# calling function to check for email under this label
con.select("discord_verifications")

def get_verification_email():
    # fetching emails from Discord
    data = con.search(None, 'ALL')

    data = con.fetch('1', '(RFC822)')
    arr = data[1][0]
    if isinstance(arr, tuple):
        msg = email.message_from_string(str(arr[1],'utf-8'))
        # decode quoted-printable encoding
        body = quopri.decodestring(msg.get_payload()[0].get_payload()).decode('utf-8')
        match = re.findall("Verify Email:.+", body)[0].strip().replace("Verify Email: ", "")
    
    resp = requests.get(match)
    print(resp.text)

print(get_verification_email())

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
