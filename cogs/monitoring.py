import discord
from discord.ext import commands
from datetime import datetime
import pytz
import pandas as pd

class Monitoring(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    @commands.command()
    async def recentactivity(self, ctx, other_user: discord.User = None):
        def utc_to_local(utc_dt):
            est = pytz.timezone('US/Eastern')
            fmt = '%Y-%m-%d %H:%M:%S %Z'

            utc_dt = utc_dt.replace(tzinfo=pytz.UTC)
            return utc_dt.astimezone(est).strftime(fmt)

        q = "SELECT * FROM actions ORDER BY dt DESC LIMIT 10;"
        if other_user:
            q = "SELECT * FROM actions WHERE user_id={0} ORDER BY dt DESC LIMIT 10;".format(other_user.id)

        r_data = pd.read_sql(q, self.db)
        out = ''
        for _, row in reversed(list(r_data.iterrows())):
            name = row['name']
            active = row['is_active']
            dt = utc_to_local(row['dt'])
            try:
                b_channel = await self.bot.fetch_channel(row['b_channel'])
            except:
                b_channel = None
            try:
                a_channel = await self.bot.fetch_channel(row['a_channel'])
            except:
                a_channel = None

            if row['action'] == 'JOIN':
                out += '\n{0}: {1} joined {2} and is {3}.'.format(dt, name, a_channel, 'active' if active else 'not active')
            if row['action'] == 'LEAVE':
                out += '\n{0}: {1} left {2}.'.format(dt, name, b_channel)
            if row['action'] == 'SWITCH':
                out += '\n{0}: {1} switched to {2} and is {3}.'.format(dt, name, a_channel, 'active' if active else 'not active')
            if row['action'] == 'ACTIVATE':
                out += '\n{0}: {1} is now active in {2}.'.format(dt, name, a_channel)
            if row['action'] == 'DEACTIVATE':
                out += '\n{0}: {1} is no longer active.'.format(dt, name)

        out = '10 most recent events:\n```'+'\n' + out + '```'
        await ctx.send(out)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = member.id
        name = member.nick if member.nick is not None else member.name

        current_time = datetime.utcnow()

        def is_active(v_state):
            is_muted = v_state.mute or v_state.self_mute
            is_deaf = v_state.deaf or v_state.self_deaf
            is_afk = v_state.afk
            return is_muted or is_deaf or is_afk,

        #JOIN
        if before.channel is None and after.channel is not None:
            action_d = {
                'user_id': id,
                'dt': current_time,
                'action': 'JOIN',
                'b_channel': None,
                'a_channel': after.channel.id,
                'name': name,
                'is_active': is_active(after)
            }
            action = pd.DataFrame(action_d, index=[0])
            action.to_sql('actions', self.db, if_exists='append', index=False)

        #LEAVE
        if before.channel is not None and after.channel is None:
            action_d = {
                'user_id': id,
                'dt': current_time,
                'action': 'LEAVE',
                'b_channel': before.channel.id,
                'a_channel': None,
                'name': name,
                'is_active': is_active(after)
            }
            action = pd.DataFrame(action_d, index=[0])
            action.to_sql('actions', self.db, if_exists='append', index=False)

        #SWITCH
        if before.channel is not None and after.channel is not None and before.channel != after.channel:
            action_d = {
                'user_id': id,
                'dt': current_time,
                'action': 'SWITCH',
                'b_channel': before.channel.id,
                'a_channel': after.channel.id,
                'name': name,
                'is_active': is_active(after)
            }
            action = pd.DataFrame(action_d, index=[0])
            action.to_sql('actions', self.db, if_exists='append', index=False)

        #ACTIVATE
        if (not is_active(before)) and is_active(after):
            action_d = {
                'user_id': id,
                'dt': current_time,
                'action': 'ACTIVATE',
                'b_channel': before.channel.id,
                'a_channel': after.channel.id,
                'name': name,
                'is_active': is_active(after)
            }
            action = pd.DataFrame(action_d, index=[0])
            action.to_sql('actions', self.db, if_exists='append', index=False)

        #DEACTIVATE
        if is_active(before) and (not is_active(after)):
            action_d = {
                'user_id': id,
                'dt': current_time,
                'action': 'DEACTIVATE',
                'b_channel': before.channel.id,
                'a_channel': after.channel.id,
                'name': name,
                'is_active': False
            }
            action = pd.DataFrame(action_d, index=[0])
            action.to_sql('actions', self.db, if_exists='append', index=False)

