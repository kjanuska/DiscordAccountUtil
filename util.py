import requests
import time
import random
from cryptography.fernet import Fernet
import string
import secrets
from pymongo import MongoClient
import base64

import globals
from phone_verify import verify_phone, available_verifications
from email_verify import verify_email
import verification

CONNECTION_STRING = f'mongodb+srv://kjanuska:{globals.MONGO_PASSWORD}@cluster0.7zdns.mongodb.net/accounts?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
tokens_db = client.accounts.tokens

names = open('words/names.txt','r').read().splitlines()
nouns = open('words/nouns.txt','r').read().splitlines()
adjectives = open('words/adjectives.txt','r').read().splitlines()
adverbs = open('words/adverbs.txt','r').read().splitlines()
alphabet = []
for c in string.ascii_letters:
    alphabet.append(c)
vowels = ["a", "e", "i", "o", "u", "y"]

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
        time.sleep(5)

def leave_all_servers():
    for token in tokens:
        header = {"authorization": token}
        resp = requests.get(f"{globals.ENTRY}/users/@me/guilds", headers=header)
        time.sleep(2)
        for server in resp.json():
            guild_id = server["id"]
            requests.delete(f"{globals.ENTRY}/users/@me/guilds/{guild_id}", headers=header)
            time.sleep(2)
        time.sleep(5)

def gen_username():
    choice = random.randint(0, 6)
    separator = random.randint(0, 4)
    match choice:
        case 0: # adjective + name
            username = random.choice(adjectives) + " " + random.choice(names).lower()
        case 1: # name + name
            username = random.choice(names).lower() + " " + random.choice(names).lower()
        case 2: # adverb + adjective
            username = random.choice(adverbs).lower() + " " + random.choice(adjectives).lower()
        case 3: # adjective + noun
            match separator:
                case 4: # use parentheses
                    username = "(" + random.choice(adjectives).lower() + ")" + random.choice(nouns).lower()
                case _: # separate with space
                    username = random.choice(adjectives).lower() + " " + random.choice(nouns).lower()
        case 4: # adverb + name
            match separator:
                case 4: # use parentheses
                    username = "(" + random.choice(adverbs).lower() + ")" + random.choice(names).lower()
                case _: # separate with space
                    username = random.choice(adverbs).lower() + " " + random.choice(names).lower()
        case 5: # random ascii
            username = ""
            for i in range(random.randint(3, 6)):
                username += random.choice(alphabet)
        case 6: # noun + noun
            username = random.choice(nouns) + " " + random.choice(nouns)
        case 6: # noun + random vowel
            username = random.choice(nouns) + random.choice(vowels)
    
    return username

def set_profile_picture(token):
    header = {
        "authorization" : token,
        "content-type": "application/json",
    }
    # get random image from collection
    with open(f"images/{random.randint(1, 1815)}.png", "rb") as image:
        base64_image = base64.b64encode(image.read()).decode("utf-8") 
    data = {
        "avatar" : f"data:image/png;base64,{base64_image}"
    }
    PROFILE_ENDPOINT = "/users/@me"
    resp = requests.patch(f"{globals.ENTRY}{PROFILE_ENDPOINT}", json=data, headers=header)

def create_account():
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
    # Generate username
    username = gen_username()
    # ==========================================================================

    # ==========================================================================
    # Generate email using username + catchall
    email_user = username.replace(" ", "_").replace("(", "").replace(")", "_")
    email = f"{email_user}@{globals.CATCHALL}"
    # ==========================================================================

    # ==========================================================================
    # Generate fingerprint
    # ==========================================================================

    # ==========================================================================
    # Generate 20 character password
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(20))
    # ==========================================================================

    REGISTER_ENDPOINT = "/auth/register"
    header = {
        "content-type": "application/json",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36"
    }
    captcha_key = verification.get_captcha_key("register")
    data = {
        "captcha_key": captcha_key,
        "consent": True,
        "date_of_birth": date,
        "email": email,
        # "fingerprint": fingerprint,
        "password": password,
        "username": username
    }

    resp = requests.post(f"{globals.ENTRY}{REGISTER_ENDPOINT}", json=data, headers=header).json()
    token = resp["token"]
    token_doc = {
        "token" : encryptor.encrypt(token.encode())
    }
    tokens_db.insert_one(token_doc)

    verify_email(token)
    verify_phone(token)
    set_profile_picture(token)