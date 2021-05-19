import discord
from discord.ext import commands
import random

class Sheldon(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.facts = []
        f = open('data/ysheldon.txt')
        for line in f.readlines():
            self.facts.append(line)
        f.close()

    @commands.command()
    async def fact(self, ctx):
        r = random.randint(0, len(self.facts) - 1)
        await ctx.send('Young Sheldon fact: ' + self.facts[r])