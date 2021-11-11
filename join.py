import requests
import time
import random

token_file = open("tokens.txt", "r")
tokens = token_file.read().splitlines()
BASE = "https://discordapp.com/api/v9"

def join_and_verify():
    INVITE_CODE = input("Invite code/link: ")
    INVITE_CODE = INVITE_CODE.replace("https://discord.gg/", "")

    message_components = input("Link to verify message: ")
    # 0 = server ID
    # 1 = channel ID
    # 2 = message ID
    message_components = message_components.replace(
        "https://discord.com/channels/", ""
    ).split("/")
    guildID = message_components[0]
    channelID = message_components[1]
    messageID = message_components[2]

    for token in tokens:
        header = {"authorization": token}
        # join server
        print("Joining server")
        invite_resp = requests.post(
            f"{BASE}/invites/{INVITE_CODE}", headers=header
        )
        invite_resp_json = invite_resp.json()
        print("Invited by " + invite_resp_json["inviter"]["username"] + "#" + invite_resp_json["inviter"]["discriminator"] + " to " + invite_resp_json["guild"]["name"])
        time.sleep(5)

        # ======================================================================
        print("Checking for server rules")
        # need to verify server rules first
        resp = requests.get(f"{BASE}/guilds/{guildID}/member-verification?with_guild=false&invite_code={INVITE_CODE}", headers=header)
        resp_json = resp.json()
        time.sleep(3)
        if not "code" in resp_json.keys():
            print("Verifying")
            verify_header = {
                "authorization": header["authorization"],
                "content-type": "application/json"
            }
            resp = requests.put(f"{BASE}/guilds/{guildID}/requests/@me", headers=verify_header, json=resp_json)
            time.sleep(5)
        else:
            print("No rules to verify")

        # ======================================================================
        # get message top emoji
        print("Getting emoji")
        resp = requests.get(
            f"{BASE}/channels/{channelID}/messages?limit=50",
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
        print("Reacting")
        requests.put(
            f"{BASE}/channels/{channelID}/messages/{messageID}/reactions/{emoji['name'] + emoji['id']}/%40me",
            headers=header,
        )
        sleep_time = random.randint(5, 15)
        print("Sleeping until next invite")
        time.sleep(sleep_time)

def leave_all_guilds():
    for token in tokens:
        header = {"authorization": token}
        resp = requests.get(f"{BASE}/users/@me/guilds", headers=header)
        time.sleep(2)
        for server in resp.json():
            guild_id = server["id"]
            requests.delete(f"{BASE}/users/@me/guilds/{guild_id}", headers=header)
            time.sleep(2)
        time.sleep(100)

leave_all_guilds()
