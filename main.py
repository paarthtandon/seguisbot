import os
from os.path import join, dirname

import discord
from discord.ext import commands
from dotenv import load_dotenv
import pymongo
import ssl

from cogs.sheldon import Sheldon
from cogs.fishing import Fishing
from cogs.quinn import Quinn

#Retrieve secret keys
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
BOT_KEY = os.environ.get("DISCORD_TOKEN")
MONGO = os.environ.get("MONGO")

#Connect to databases
client = pymongo.MongoClient(MONGO, ssl_cert_reqs=ssl.CERT_NONE)

fishDB = client['fishing']
superDB = client['bot']

#Create bot
seguis = commands.Bot(command_prefix="$")
seguis.add_cog(Sheldon(seguis))
seguis.add_cog(Fishing(seguis, fishDB, superDB))
seguis.add_cog(Quinn(seguis))

@seguis.command()
async def repeat(ctx, m):
    await ctx.send(m)

print("Bot started")
seguis.run(BOT_KEY)