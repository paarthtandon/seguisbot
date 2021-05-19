import os
from os.path import join, dirname

import discord
from discord.ext import commands
from dotenv import load_dotenv
import pymongo

from cogs.surveilence import Surveilence
from cogs.sheldon import Sheldon
from cogs.fishing import Fishing

#Retrieve secret keys
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
BOT_KEY = os.environ.get("DISCORD_TOKEN")

#Connect to database
client = pymongo.MongoClient("mongodb+srv://ptandon:vikrant00@cluster0.d7gwd.mongodb.net/test?retryWrites=true&w=majority")

survDB = client['surveilence']
fishDB = client['fishing']

#Create bot
seguis = commands.Bot(command_prefix="$")
seguis.add_cog(Surveilence(seguis, survDB))
seguis.add_cog(Sheldon(seguis))
seguis.add_cog(Fishing(seguis, fishDB))

@seguis.command()
async def repeat(ctx, m):
    await ctx.send(m)

print("Bot started")
seguis.run(BOT_KEY)