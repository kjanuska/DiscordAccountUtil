import requests
import time
import random

def join():
    token_file = open('tokens.txt', 'r')
    tokens = token_file.readlines()

    INVITE_CODE = input("Invite code/link: ")
    INVITE_CODE = INVITE_CODE.replace('https://discord.gg/', '')
    # for token in tokens:
    header = {
        "authorization": "ODk0MDUxMDI0MTY2MzIyMTk2.YYlvtA.sKDcDN1UUOxsN1d3jQgoNp9HbZo"
    }
    requests.post(f"https://discordapp.com/api/v9/invites/{INVITE_CODE}", headers=header)
    time.sleep(random.randint(5, 10))

def react():
    message_components = input("Link to verify message: ")
    # 0 = server ID
    # 1 = channel ID
    # 2 = message ID
    message_components = message_components.replace('https://discord.com/channels/', '').split('/')
    channelID = message_components[1]
    messageID = message_components[2]

    resp = requests.get(f"https://discord.com/api/v9/channels/{channelID}/messages?limit=50", headers={"authorization": "ODk0MDUxMDI0MTY2MzIyMTk2.YYlvtA.sKDcDN1UUOxsN1d3jQgoNp9HbZo"})
    message_list = resp.json()
    for message in message_list:
        if message["id"] == messageID:
            emoji = message["reactions"][0]["emoji"]
            break
    
    # if the emoji is a unicode emoji
    if not emoji["id"]:
        emoji["id"] = ""
        # convert emoji from unicode to string version of hex
        emoji["name"] = emoji["name"].encode('utf-8').hex().upper()
        # add % signs for correct url form
        emoji["name"] = '%' + '%'.join(emoji["name"][i:i + 2] for i in range(0, len(emoji["name"]), 2))
    else:
        emoji["id"] = "%3A" + emoji["id"]

    time.sleep(2)
    requests.put(f"https://discord.com/api/v9/channels/{channelID}/messages/{messageID}/reactions/{emoji['name'] + emoji['id']}/%40me", headers={"authorization": "ODk0MDUxMDI0MTY2MzIyMTk2.YYlvtA.sKDcDN1UUOxsN1d3jQgoNp9HbZo"})

react()