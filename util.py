import requests
import time
import random
from cryptography.fernet import Fernet
from pymongo import MongoClient

import globals
from phone_verify import verify_phone, get_bearer_token, available_verifications
from email_verify import verify_email
import verification

CONNECTION_STRING = f'mongodb+srv://kjanuska:{globals.MONGO_PASSWORD}@cluster0.7zdns.mongodb.net/accounts?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
tokens_db = client.accounts.tokens

encryptor = Fernet(globals.ENCRYPTION_KEY)
tokens = []

def init():
    for token_obj in tokens_db.find():
        token = encryptor.decrypt(token_obj["token"]).decode()
        tokens.append(token)
    verification.init()

def num_invitable():
    return len(tokens)

def num_creatable():
    return available_verifications()

def join(invite_code, message, emoji):
    invited_num = 0
    verification_message = True
    if emoji == False:
        verification_message = False
    INVITE_CODE = invite_code.replace("https://discord.gg/", "")

    # 0 = server ID
    # 1 = channel ID
    # 2 = message ID
    message_components = message.replace(
        "https://discord.com/channels/", ""
    ).split("/")
    GUILD_ID = message_components[0]
    CHANNEL_ID = message_components[1]
    MESSAGE_ID = message_components[2]

    for token in tokens:
        header = {"authorization": token}
        # join server
        invite_resp = requests.post(
            f"{globals.ENTRY}/invites/{INVITE_CODE}", headers=header
        )
        invite_resp_json = invite_resp.json()
        inviter = invite_resp_json["inviter"]["username"] + "#" + invite_resp_json["inviter"]["discriminator"]
        server = invite_resp_json["guild"]["name"]
        time.sleep(5)

        # ======================================================================
        # need to verify server rules first
        resp = requests.get(f"{globals.ENTRY}/guilds/{GUILD_ID}/member-verification?with_guild=false&invite_code={INVITE_CODE}", headers=header)
        resp_json = resp.json()
        time.sleep(3)
        if not "code" in resp_json.keys():
            verify_header = {
                "authorization": header["authorization"],
                "content-type": "application/json"
            }
            resp = requests.put(f"{globals.ENTRY}/guilds/{GUILD_ID}/requests/@me", headers=verify_header, json=resp_json)
            time.sleep(5)

        if verification_message == True:
            # ======================================================================
            # get message top emoji
            resp = requests.get(
                f"{globals.ENTRY}/channels/{CHANNEL_ID}/messages?limit=50",
                headers=header,
            )
            message_list = resp.json()
            for message in message_list:
                if message["id"] == MESSAGE_ID:
                    emoji = message["reactions"][0]["emoji"]
                    break

            # if the emoji is a unicode emoji
            if not emoji["id"]:
                emoji["id"] = ""
                # convert emoji from unicode to string version of hex
                emoji["name"] = emoji["name"].encode("utf-8").hex().upper()
                # add % signs for correct url form
                emoji["name"] = "%" + "%".join(
                    emoji["name"][i : i + 2] for i in range(0, len(emoji["name"]), 2)
                )
            else:
                emoji["id"] = "%3A" + emoji["id"]
            time.sleep(2)

            # ======================================================================
            # react to emoji
            requests.put(
                f"{globals.ENTRY}/channels/{CHANNEL_ID}/messages/{MESSAGE_ID}/reactions/{emoji['name'] + emoji['id']}/%40me",
                headers=header,
            )
            
        # ======================================================================
        # sleep
        invited_num += 1
        print(inviter + " invited " + str(invited_num) + " accounts to " + server)
        time.sleep(random.randint(5, 15))

def leave_server(server_ID):
    for token in tokens:
        header = {"authorization": token}
        requests.delete(f"{globals.ENTRY}/users/@me/guilds/{server_ID}", headers=header)
        time.sleep(10)

def leave_all_servers():
    for token in tokens:
        header = {"authorization": token}
        resp = requests.get(f"{globals.ENTRY}/users/@me/guilds", headers=header)
        time.sleep(2)
        for server in resp.json():
            guild_id = server["id"]
            requests.delete(f"{globals.ENTRY}/users/@me/guilds/{guild_id}", headers=header)
            time.sleep(2)
        time.sleep(10)

def create_account():
    REGISTER_ENDPOINT = "/auth/register"
    header = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    captcha_key = verification.get_captcha_key("register")

    # ==========================================================================
    # Generate date of bith
    month = random.randint(1, 12)
    if month < 10:
        month = "0" + str(month)
    day = random.randint(1,28)
    if day < 10:
        day = "0" + str(day)
    date = f"{random.randint(1970, 2001)}-{month}-{day}"
    # ==========================================================================

    # ==========================================================================
    # Generate email using catchall
    # ==========================================================================

    # ==========================================================================
    # Generate fingerprint
    # ==========================================================================

    # ==========================================================================
    # Generate password
    # ==========================================================================

    # ==========================================================================
    # Generate username
    # ==========================================================================
    
    data = {
        "captcha_key": captcha_key,
        "consent": True,
        "date_of_birth": date,
        # "email": email,
        # "fingerprint": fingerprint,
        # "password": password,
        # "username": username
    }

    resp = requests.post(f"{globals.ENTRY}{REGISTER_ENDPOINT}", headers=header, json=data).json()
    token = resp["token"]
    token_doc = {
        "token" : encryptor.encrypt(token.encode())
    }
    tokens.insert_one(token_doc)

    verification.verify_email(token)
    verification.verify_phone(token)
