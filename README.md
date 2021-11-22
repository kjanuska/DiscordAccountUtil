# **Discord Account Utilities**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Table of contents
=================
<!--ts-->
* [Requirements](#requirements)
* [Installation](#installation)
* [Commands](#commands)
    * [Account Utilities](#account-util)
    * [Server Management](#server-management)
* [Appendix](#appendix)
<!--te-->

A collection of scripts written in Python that allow you to create and control your Discord accounts in various ways. 
> ⚠️ **This repo is for educational purposes only!** Using the Discord API to control accounts (aka selfbots) is [forbidden](https://support.discord.com/hc/en-us/articles/115002192352-Automated-user-accounts-self-bots-).

Developed with `Python 3.10.0` but any version above `3.6.0` should work. The follwing features are currently supported:
- Account creation with automatic phone and email verification[^1]
- Joining a server and agreeing to server rules
- Reacting to a specific emoji on a message in a server
- Leaving a specific server
- Leaving all servers an account is currently in

[^1]: Currently, as soon as an account is created, it is detected by Discord's anti-bot and gets instantly disabled. I am currently looking for a solution to this issue.  

**Requirements**
=================
The items listed below are required in the current version of the program. In later versions, these requirements may change to be more flexible.
- For ease-of-use, the way of interacting with these utilities is done via a Discord bot. This requires setting up a [Discord application](https://discord.com/developers/applications) and creating a [bot](https://discordpy.readthedocs.io/en/stable/discord.html).
- A MongoDB cluster is required to store tokens.
- A Fernet key is used to encrypt/decrypt the tokens in the cloud.
- 2Captcha is required to solve HCaptchas.
- TextVerified is used to verify phone numbers.
- A catchall with email forwarding is used to route emails to one Gmail address and verify accounts.

**Installation**
=================
The following environmental variables are required to gain access to all functionality. Case and spelling matter!
```python
# The Discord bot token
BOT_TOKEN

# The ID of the guild you wish to launch the bot in
GUILD_ID

# Your MongoDB password. Make sure to change the connection string in util.py
MONGO_PASSWORD

# A Fernet key used to encrypt and decrypt tokens
ENCRYPTION_KEY

# textverified.com Simple Access Token
TEXT_API_KEY

# 2captcha.com API key
CAP_API_KEY

# A catchall (without the @) used for email creation. Make sure that email forwarding to a Gmail account is setup.
CATCHALL

# Your Gmail's username/email address
GMAIL_USER

# Your 16-character Gmail App Password, see https://support.google.com/mail/answer/185833?hl=en
GMAIL_PASS
```

**Commands**
=================
## **Account Utilities**
`/create [amount]`

amount
: The number of Discord accounts you can create. Limited by the number provided by `/balance`.

Create an *amount* number of Discord accounts. The program will generate random usernames, passwords, emails using a catchall, set a profile picture, and upload an encrypted version of the token to a database. See the [appendix](#appendix) for more information on usernames and profile pictures.

`/balance`

Get the number of Discord accounts you can create. This is calculated using the current price of 1 Discord phone verification from TextVerified and your current balance.

`/available`

Get the number of Discord accounts you currently have created. Gets the number of documents (tokens) that are stored in your MongoDB cluster.

`/react [message] (emoji-position)`

message
: The link to the message you wish to react to

emoji-position
: A parameter to specify the index of the emoji if there are multiple emojis on one message. Defaults to the first emoji if left blank.

React to an existing emoji on a message in a server that your accounts are currently in. The accounts must already be in the server in which are you trying to react to.

## **Server Management**
`/join [invite] [message] [emoji] (emoji-position)`

invite
: A Discord invite code or link

message
: The link to the message you wish to react to

emoji
: A boolean asking if there is an emoji to react to in order to get access to the server.

emoji-position
: A parameter to specify the index of the emoji if there are multiple emojis on one message. Defaults to the first emoji if left blank.

Invite all of your current Discord accounts to a server, accept the server rules if they are exist, and optionally react to an emoji to gain access to the rest of the server.

`/leave-server [server-id]`

server-id
: The ID of the server that your accounts should leave.

Make all accounts leave a specific server if they are in it.

`/leave-all-servers`

Make all accounts leave every server they are currently in.

**Appendix**
=================
- Make sure that when a Discord verification email is forwarded to your catchall it automatically has the label 'discord_verifications' applied to it. See [here](https://support.google.com/a/users/answer/9308833?hl=en) on how to apply labels to incoming mail based on filters.
- The files `adjectives.txt`, `adverbs.txt`, `names.txt`, and `nouns.txt` are used to create semi-realistic usernames and can be changed for custom name generation.
- The `/images` folder contains a lot of images that are used to set a profile picture for each newly created account. Currently, it contains images from various NFT collections but can be replaced with any set of images.
- `x-super-properties.txt` contains a base64 encoded string that may potentially be useful in avoiding Discord's antibot.