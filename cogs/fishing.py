from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

import discord
from discord.ext import commands

class Fishing(commands.Cog):
    def __init__(self, bot, db, superdb):
        self.bot = bot
        self.db = db
        self.superdb = superdb

    #Commands

    @commands.command()
    async def fish(self, ctx, gift_to: discord.User=None):
        users = self.db['users']
        user = gift_to if gift_to else ctx.author

        if ctx.channel.id != 932090786466644028:
            cur_data = users.find({'id': ctx.author.id})[0]
            penalty = cur_data['points'] * 0.05
            users.find_one_and_update({'id': ctx.author.id}, {
                "$set": {
                    'points': cur_data['points'] - penalty
                }
            })

            bank = self.superdb['bank']
            cur_amount = bank.find({'id': 0})[0]
            bank.find_one_and_update({'id': 0}, {
                "$set": {
                    'amount': cur_amount['amount'] + penalty
                }
            })
            await ctx.send('You\'re not allowed to fish around these parts, {0}. The Seguis authority has confiscated your fish and you have incurred a penalty worth 5% of your total bank account.'.format(cur_data['name']))
            return

        weight, size = self.fish_from_pond()

        if ctx.author.id != 842785433624903690 and users.find({'id': ctx.author.id}).count() > 0:
            last_time = users.find({'id': ctx.author.id})[0]['last_fished']
            if last_time != None:
                if datetime.utcnow() < last_time + timedelta(minutes=60):
                    diff = (last_time + timedelta(minutes=60)) - datetime.utcnow()
                    diff = str(diff).split(':')
                    await ctx.send("You need to wait {0} minutes and {1} seconds until you can fish again!".format(diff[1], diff[2][:2]))
                    return

        self.fish_update(user, datetime.utcnow(), size, weight, ctx.author if gift_to else None)
        if gift_to:
            await ctx.send("{0} fished a {1} fish for {2} worth ${3}!"\
                .format(ctx.author.mention, size, user.mention, weight))
        else:
            await ctx.send("{0} fished a {1} fish worth ${2}!"\
                .format(ctx.author.mention, size, weight))

    @commands.command()
    async def fs(self, ctx, other_user: discord.User=None):
        users = self.db['users']
        user = other_user if other_user else ctx.author
        username = await ctx.guild.fetch_member(user.id)

        if users.find({'id': user.id}).count() == 0:
            await ctx.send("User not found!")
            return

        data = users.find({'id': user.id})[0]
        out = '{0}\'s fishing stats\ntimes: {1}\nMoney: ${2}\ngifted: ${3}\nsizes: {4}'.format(
            username, data['count'], data['points'], data['gifted_points'], str(data['sizes']))
        image = self.fish_graph(user)
        await ctx.send(out, file=image)

    @commands.command()
    async def top(self, ctx):
        users = self.db['users'].find({})
        t = []
        for user in users:
            if user['id'] != 842785433624903690:
                t.append((user['name'], user['points']))
        t = sorted(t, key=lambda x: x[1], reverse=True)[:15]
        out = ''
        for i, user in enumerate(t):
            out += '{0}. {1} - {2} points\n'.format(i + 1, user[0], user[1])
        await ctx.send(out)

    #Helper funcitons

    def fish_graph(self, user):
        users = self.db['users']
        data = users.find({'id': user.id})[0]['times']
        plt.plot(*zip(*data))
        plt.xlabel('time')
        plt.ylabel('points')
        plt.savefig('temp/' + str(user.id) + '.png')
        plt.clf()
        return discord.File('temp/' + str(user.id) + '.png')

    def fish_from_pond(self):
        trash_gen = random.random()
        trash = True if trash_gen < .1 else False
        monster_gen = random.random()
        monster = True if monster_gen < .1 else False
        if trash:
            weight = 0
            size = 'trash'
        elif monster:
            weight = 100
            if monster_gen < .01:
                weight = 1000
            if monster_gen < .001:
                weight = 10000
            if monster_gen < .0001:
                weight = 100000
            size = 'monster'
        else:
            gen = random.random()
            weight = gen * 100
            if weight < 1:
                size = 'tiny'
            elif weight < 20:
                size = 'small'
            elif weight < 70:
                size = 'medium'
            elif weight < 90:
                size = 'large'
            else:
                size = 'huge'
        return (int(weight), size)

    def fish_update(self, user, time, size, points, gifted_from):
        users = self.db['users']

        id = user.id
        name = user.name

        if users.find({'id': id}).count() == 0:
            users.insert_one({
                'id': id,
                'name': name,
                'sizes': {'trash': 0, 'tiny': 0, 'small': 0, 'medium': 0, 'large': 0, 'huge': 0, 'monster': 0},
                'points': 0,
                'count': 0,
                'gifted_points': 0,
                'last_fished': None,
                'times': []
            })
            print('Created fishing data for user', name)

        if gifted_from:
            gid = gifted_from.id
            gname = gifted_from.name

            if users.find({'id': gid}).count() == 0:
                users.insert_one({
                    'id': gid,
                    'name': gname,
                    'sizes': {'trash': 0, 'tiny': 0, 'small': 0, 'medium': 0, 'large': 0, 'huge': 0, 'monster': 0},
                    'points': 0,
                    'count': 0,
                    'gifted_points': 0,
                    'last_fished': None,
                    'times': []
                })
                print('Created fishing data for user', name)

            cur_data = users.find({'id': id})[0]
            users.find_one_and_update({'id': id}, {
                "$set": {
                    'name': name,
                    'points': cur_data['points'] + points
                }
            })
            users.find_one_and_update({'id': id}, {
                "$push": {
                    'times': (time, cur_data['points'] + points)
                }
            })
            m = 'sizes.' + size
            users.find_one_and_update({'id': id}, {
                "$set": {
                    m: cur_data['sizes'][size] + 1
                }
            })
            cur_data = users.find({'id': gid})[0]
            users.find_one_and_update({'id': gid}, {
                "$set": {
                    'name': gname,
                    'gifted_points': cur_data['gifted_points'] + points,
                    'last_fished': time
                }
            })
        else:
            cur_data = users.find({'id': id})[0]
            users.find_one_and_update({'id': id}, {
                "$set": {
                    'name': name,
                    'points': cur_data['points'] + points,
                    'count': cur_data['count'] + 1,
                    'last_fished': time
                }
            })
            users.find_one_and_update({'id': id}, {
                "$push": {
                    'times': (time, cur_data['points'] + points)
                }
            })
            m = 'sizes.' + size
            users.find_one_and_update({'id': id}, {
                "$set": {
                    m: cur_data['sizes'][size] + 1
                }
            })
        return
