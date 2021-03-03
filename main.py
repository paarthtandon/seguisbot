import os
from os.path import join, dirname

import discord
from discord.ext import commands
from dotenv import load_dotenv
import psycopg2

from cogs.fishing import Fishing

#Retrieve secret keys
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)
BOT_KEY = os.environ.get("BOT_KEY")
DATABASE_PASS = os.environ.get("DATABASE_PASS")

#Connect to database
conn = psycopg2.connect(database="seguis", user = "seguis",\
     password = DATABASE_PASS, host = "192.168.1.222", port = "5432")
cur = conn.cursor()
print("Connection to database successful")

#Create bot
seguis = commands.Bot(command_prefix="$")
seguis.add_cog(Fishing(seguis, cur, conn))

@seguis.command()
async def repeat(ctx, m):
    await ctx.send(m)

print("Bot started")
seguis.run(BOT_KEY)