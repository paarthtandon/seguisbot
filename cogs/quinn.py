import discord
from discord.ext import commands
from time import sleep
import datetime


class Quinn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_call = datetime.datetime.utcnow()

    @commands.command()
    async def quinn(self, ctx):
        now = datetime.datetime.utcnow()
        if (now - self.last_call) < datetime.timedelta(seconds=15):
            await ctx.send('WAIT')
            return

        channel = ctx.author.voice.channel
        if channel is None:
            await ctx.send('Must be in a voice channel!')
            return

        source = discord.FFmpegPCMAudio('data/quinn.mp3', executable='ffmpeg')
        vc = await channel.connect()
        vc.play(source)
        while vc.is_playing():
            sleep(.1)
        await vc.disconnect()
        self.last_call = datetime.datetime.utcnow()
        