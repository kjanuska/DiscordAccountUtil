from discord_slash import SlashCommand
from discord.ext import commands
from dotenv import load_dotenv
from discord_slash.utils.manage_commands import create_option, create_choice
import os

from pymongo import MongoClient

import util

load_dotenv()

CONNECTION_STRING = f'mongodb+srv://kjanuska:{os.environ["MONGO_PASSWORD"]}@cluster0.7zdns.mongodb.net/accounts?retryWrites=true&w=majority'
dbClient = MongoClient(CONNECTION_STRING)
db = dbClient.accounts
tokens = db.tokens

testDoc = {
    "token" : "asdfasdfasdfasdfasdf"
}

tokens.insert_one(testDoc)

token_list = db.tokens.find()
for token in token_list:
    print(token)

TOKEN = os.environ["TOKEN"]
GUILD_ID = [int(os.environ["GUILD_ID"])]

client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True)

@slash.slash(
    name="join",
    guild_ids=GUILD_ID,
    options=[
        create_option(
            name="invite",
            description="Invite link/code",
            option_type=3,
            required=True,
        ),
        create_option(
            name="message",
            description="Link to message in server (optionally for verification)",
            option_type=3,
            required=True,
        ),
        create_option(
            name="emoji",
            description="Need to react to emoji for verification?",
            option_type=5,
            required=True,
        ),
    ],
)
async def _join(ctx, invite, message, emoji):
    available_accnts = util.num_available()
    await ctx.send(content=f"Inviting {available_accnts} accounts")
    util.join(invite, message, emoji)

@slash.slash(
    name="leave-server",
    guild_ids=GUILD_ID,
    options=[
        create_option(
            name="server",
            description="Server ID to leave",
            option_type=3,
            required=True,
        ),
    ]
)
async def _leave_server(ctx, server_ID):
    await ctx.send(content=f"All accounts leaving server {server_ID}")
    util.leave_server(server_ID)

@slash.slash(
    name="leave-all-servers",
    guild_ids=GUILD_ID,
)
async def _leave_all_servers(ctx):
    await ctx.send(content=f"All accounts leaving all servers")
    util.leave_all_servers()

client.run(TOKEN)
