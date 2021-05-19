import discord
from discord.ext import commands
import pymongo
from pymongo.message import update


class Surveilence(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    def update_user(self, message=None, voice=None):
        if message:
            self.update_text_data(message)
        if voice:
            self.update_voice_data(voice[0], voice[1], voice[2])

    def update_text_data(self, message):
        users = self.db['users']

        id = message.author.id
        name = message.author.name
        print('Message from', id, name)

        if users.find({'id': id}).count() == 0:
            users.insert_one({
                'id': id,
                'name': name,
                'mentions': {},
                'pinned': 0,
                'count': 0,
                'total_len': 0,
                'times': []
            })
            print('Created data for user', name)

        content = message.content
        created_at = message.created_at
        mentions = message.mentions
        pinned = message.pinned

        cur_data = users.find({'id': id})[0]

        users.find_one_and_update({'id': id}, {
            "$set": {
                'name': name,
                'pinned': cur_data['pinned'] + (1 if pinned else 0),
                'count': cur_data['count'] + 1,
                'total_len': cur_data['total_len'] + len(content)
            }
        })

        users.find_one_and_update({'id': id}, {
            "$push": {
                'times': created_at
            }
        })

        for mention in mentions:
            m = 'mentions.' + str(mention.id)
            if str(mention.id) not in cur_data['mentions']:
                users.find_one_and_update({'id': id}, {
                    "$set": {
                        m: 1
                    }
                })
            else:
                users.find_one_and_update({'id': id}, {
                    "$set": {
                        m: cur_data['mentions'][str(mention.id)] + 1
                    }
                })

    def update_voice_data(self, member, before, after):
        pass

    @commands.Cog.listener()
    async def on_message(self, message):
        self.update_user(message=message)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        self.update_user(voice=(member, before, after))

    @commands.command()
    async def stats(self, ctx, other_user: discord.User = None):
        users = self.db['users']
        user = other_user if other_user else ctx.author
        username = await ctx.guild.fetch_member(user.id)

        if users.find({'id': user.id}).count() == 0:
            await ctx.send("User not found!")
            return

        data = users.find({'id': user.id})[0]
        user_mentions = {}
        for key, val in data['mentions'].items():
            name = await ctx.guild.fetch_member(int(key))
            user_mentions[name.nick] = val

        out = '{0}\'s stats\nmessages: {1}\npins: {2}\ntotal len: {3}\nmentions: {4}'.format(
            username, data['count'], data['pinned'], data['total_len'], str(user_mentions))
        await ctx.send(out)
