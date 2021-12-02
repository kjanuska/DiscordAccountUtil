import requests
import time
import random
from cryptography.fernet import Fernet

from pymongo import MongoClient

import environment
import verification
from phone_verify import available_verifications
import environment

CONNECTION_STRING = f'mongodb+srv://kjanuska:{environment.MONGO_PASSWORD}@cluster0.7zdns.mongodb.net/accounts?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
tokens_db = client.accounts.tokens

encryptor = Fernet(environment.ENCRYPTION_KEY)
tokens = []

def init():
    for token_obj in tokens_db.find():
        token = encryptor.decrypt(token_obj["token"]).decode()
        tokens.append(token)
    verification.init()

def upload(token):
    token_doc = {
        "token" : encryptor.encrypt(token.encode())
    }
    tokens_db.insert_one(token_doc)

def num_invitable():
    return len(tokens)

def num_creatable():
    return available_verifications()

def react_to_emoji(channel_id, message_id, emoji_pos, token):
    header = {"authorization": token}
    # ======================================================================
    # get messages in channel
    resp = requests.get(
        f"{environment.ENTRY}/channels/{channel_id}/messages?limit=50",
        headers=header,
    )
    message_list = resp.json()
    for message in message_list:
        if message["id"] == message_id:
            # get the correct emoji for the message
            emoji = message["reactions"][emoji_pos - 1]["emoji"]
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
        f"{environment.ENTRY}/channels/{channel_id}/messages/{message_id}/reactions/{emoji['name'] + emoji['id']}/%40me",
        headers=header,
    )

def react(message_link, emoji_pos):
    message_components = message_link.replace(
        "https://discord.com/channels/", ""
    ).split("/")
    CHANNEL_ID = message_components[1]
    MESSAGE_ID = message_components[2]
    for token in tokens:
        react_to_emoji(CHANNEL_ID, MESSAGE_ID, emoji_pos, token)

def join(invite_code, message_link, emoji, emoji_pos):
    invited_num = 0
    INVITE_CODE = invite_code.replace("https://discord.gg/", "")

    # 0 = server ID
    # 1 = channel ID
    # 2 = message ID
    message_components = message_link.replace(
        "https://discord.com/channels/", ""
    ).split("/")
    GUILD_ID = message_components[0]
    CHANNEL_ID = message_components[1]
    MESSAGE_ID = message_components[2]
    for token in tokens:
        header = {"authorization": token}
        # join server
        invite_resp = requests.post(
            f"{environment.ENTRY}/invites/{INVITE_CODE}", headers=header
        )
        invite_resp_json = invite_resp.json()
        inviter = invite_resp_json["inviter"]["username"] + "#" + invite_resp_json["inviter"]["discriminator"]
        server = invite_resp_json["guild"]["name"]
        time.sleep(5)

        # ======================================================================
        # need to verify server rules first
        resp = requests.get(f"{environment.ENTRY}/guilds/{GUILD_ID}/member-verification?with_guild=false&invite_code={INVITE_CODE}", headers=header)
        resp_json = resp.json()
        time.sleep(3)
        if not "code" in resp_json.keys():
            verify_header = {
                "authorization": header["authorization"],
                "content-type": "application/json"
            }
            resp = requests.put(f"{environment.ENTRY}/guilds/{GUILD_ID}/requests/@me", headers=verify_header, json=resp_json)
            time.sleep(5)

        if emoji == True:
            react(CHANNEL_ID, MESSAGE_ID, emoji_pos, token)
            
        # ======================================================================
        # sleep
        invited_num += 1
        print(inviter + " invited " + str(invited_num) + " accounts to " + server)
        time.sleep(random.randint(5, 15))

def leave_server(server_ID):
    for token in tokens:
        header = {"authorization": token}
        requests.delete(f"{environment.ENTRY}/users/@me/guilds/{server_ID}", headers=header)
        time.sleep(5)

def leave_all_servers():
    for token in tokens:
        header = {"authorization": token}
        resp = requests.get(f"{environment.ENTRY}/users/@me/guilds", headers=header)
        time.sleep(2)
        for server in resp.json():
            guild_id = server["id"]
            requests.delete(f"{environment.ENTRY}/users/@me/guilds/{guild_id}", headers=header)
            time.sleep(2)
        time.sleep(5)