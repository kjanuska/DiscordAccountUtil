import requests
import time
import random

from requests.api import head

def join_and_verify():
    token_file = open("tokens.txt", "r")
    tokens = token_file.readlines()

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
        header = {"authorization": token.strip()}
        # join server
        print("Joining server")
        requests.post(
            f"https://discordapp.com/api/v9/invites/{INVITE_CODE}", headers=header
        )
        time.sleep(7)
        print("Verifying")
        # need to verify server rules first
        resp = requests.get(f"https://discord.com/api/v9/guilds/{guildID}/member-verification?with_guild=false&invite_code={INVITE_CODE}", headers=header)
        print(resp.content)
        time.sleep(2)
        verify_header = {
            "authorization": header["authorization"],
            "content-type": "application/json"
        }
        resp = requests.put(f"https://discord.com/api/v9/guilds/{guildID}/requests/@me", headers=verify_header, json=resp.json())
        print(resp.content)
        time.sleep(7)
        # get message top emoji
        print("Getting emoji")
        resp = requests.get(
            f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50",
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
        # react to emoji
        print("Reacting")
        requests.put(
            f"https://discord.com/api/v9/channels/{channelID}/messages/{messageID}/reactions/{emoji['name'] + emoji['id']}/%40me",
            headers=header,
        )
        time.sleep(random.randint(10, 30))

join_and_verify()
