from datetime import datetime
import random

import discord
from discord.ext import commands

class Fishin(commands.Cog):
    def __init__(self, bot, cur, conn):
        self.bot = bot
        #Database cursor and connection
        self.cur = cur
        self.conn = conn

    #Commands

    @commands.command()
    async def fish(self, ctx, gift_to: discord.User=None):
        user = gift_to if gift_to else ctx.author
        weight, size = self.fish_from_pond()
        self.fish_update(user.id, datetime.now(), size, weight, ctx.author.id if gift_to else None)
        if gift_to:
            await ctx.send("{0} fished a {1} fish for {2} worth {3} points!"\
                .format(ctx.author.mention, size, user.mention, weight))
        else:
            await ctx.send("{0} fished a {1} fish worth {2} points!"\
                .format(ctx.author.mention, size, weight))

    @commands.command()
    async def fs(self, ctx, other_user: discord.User=None):
        return

    #Helper funcitons

    def fish_from_pond(self):
        return

    def fish_update(self, iD, time, size, points, gifted_from):
        return
