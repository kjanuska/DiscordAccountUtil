from discord_slash import SlashCommand
from discord.ext import commands
from dotenv import load_dotenv
from discord_slash.utils.manage_commands import create_option, create_choice
import os

import util

load_dotenv()

TOKEN = os.environ["BOT_TOKEN"]
GUILD_ID = [int(os.environ["GUILD_ID"])]

client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True)

@client.event
async def on_ready():
    util.init()
    print("ready")

@slash.slash(
    name="join",
    description="Invite accounts to a server",
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
        create_option(
            name="emoji-position",
            description="(Optional) Position of reaction emoji if it is not the first one",
            option_type=4,
            required=False
        )
    ],
)
async def _join(ctx, invite, message_link, emoji, emoji_pos=0):
    available_accnts = util.num_invitable()
    await ctx.send(content=f"Inviting {available_accnts} accounts")
    util.join(invite, message_link, emoji, emoji_pos)

@slash.slash(
    name="leave-server",
    description="Make all accounts leave a specific server",
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
    description="Make all accounts leave all servers they are currently in",
    guild_ids=GUILD_ID,
)
async def _leave_all_servers(ctx):
    await ctx.send(content=f"All accounts leaving all servers")
    util.leave_all_servers()

@slash.slash(
    name="creatable",
    description="Get the number of accounts you can create",
    guild_ids=GUILD_ID
)
async def _creatable(ctx):
    max_creatable = util.num_creatable()
    await ctx.send(content=f"You can create {max_creatable} accounts")

@slash.slash(
    name="available",
    description="Number of accounts you currently have",
    guild_ids=GUILD_ID
)
async def _available(ctx):
    max_available = util.num_invitable()
    await ctx.send(content=f"You have {max_available} accounts")

@slash.slash(
    name="react",
    description="Make all accounts in a server react to a specific message",
    guild_ids=GUILD_ID,
    options=[
        create_option(
            name="message",
            description="Link to message in server",
            option_type=3,
            required=True,
        ),
        create_option(
            name="emoji-position",
            description="(Optional) Position of reaction emoji if it is not the first one",
            option_type=4,
            required=False
        )
    ]
)
async def _react(ctx, message_link, emoji_pos):
    util.react(message_link, emoji_pos)

client.run(TOKEN)
