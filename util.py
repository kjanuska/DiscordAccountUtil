import requests
import time
import random
from cryptography.fernet import Fernet
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

ENTRY = "https://discordapp.com/api/v9"

CONNECTION_STRING = f'mongodb+srv://kjanuska:{os.environ["MONGO_PASSWORD"]}@cluster0.7zdns.mongodb.net/accounts?retryWrites=true&w=majority'
client = MongoClient(CONNECTION_STRING)
tokens_db = client.accounts.tokens

encryptor = Fernet(os.environ["ENCRYPTION_KEY"])
tokens = []

def init():
    for token_obj in tokens_db.find():
        token = encryptor.decrypt(token_obj["token"]).decode()
        tokens.append(token)

def num_available():
    return len(tokens)

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
    guildID = message_components[0]
    channelID = message_components[1]
    messageID = message_components[2]

    for token in tokens:
        header = {"authorization": token}
        # join server
        invite_resp = requests.post(
            f"{ENTRY}/invites/{INVITE_CODE}", headers=header
        )
        invite_resp_json = invite_resp.json()
        inviter = invite_resp_json["inviter"]["username"] + "#" + invite_resp_json["inviter"]["discriminator"]
        server = invite_resp_json["guild"]["name"]
        time.sleep(5)

        # ======================================================================
        # need to verify server rules first
        resp = requests.get(f"{ENTRY}/guilds/{guildID}/member-verification?with_guild=false&invite_code={INVITE_CODE}", headers=header)
        resp_json = resp.json()
        time.sleep(3)
        if not "code" in resp_json.keys():
            verify_header = {
                "authorization": header["authorization"],
                "content-type": "application/json"
            }
            resp = requests.put(f"{ENTRY}/guilds/{guildID}/requests/@me", headers=verify_header, json=resp_json)
            time.sleep(5)

        if verification_message == True:
            # ======================================================================
            # get message top emoji
            resp = requests.get(
                f"{ENTRY}/channels/{channelID}/messages?limit=50",
                headers=header,
            )
            message_list = resp.json()
            for message in message_list:
                if message["id"] == messageID:
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
                f"{ENTRY}/channels/{channelID}/messages/{messageID}/reactions/{emoji['name'] + emoji['id']}/%40me",
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
        requests.delete(f"{ENTRY}/users/@me/guilds/{server_ID}", headers=header)
        time.sleep(10)

def leave_all_servers():
    for token in tokens:
        header = {"authorization": token}
        resp = requests.get(f"{ENTRY}/users/@me/guilds", headers=header)
        time.sleep(2)
        for server in resp.json():
            guild_id = server["id"]
            requests.delete(f"{ENTRY}/users/@me/guilds/{guild_id}", headers=header)
            time.sleep(2)
        time.sleep(10)

def create_account():
    token_doc = {
        "token" : encryptor.encrypt(token.encode())
    }
    tokens.insert_one(token_doc)