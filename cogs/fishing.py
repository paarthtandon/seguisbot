from datetime import datetime, time, timedelta
import random
import matplotlib.pyplot as plt

import discord
from discord.ext import commands

class Fishing(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db

    #Commands

    @commands.command()
    async def fish(self, ctx, gift_to: discord.User=None):
        users = self.db['users']
        user = gift_to if gift_to else ctx.author
        weight, size = self.fish_from_pond()

        last_time = users.find({'id': user.id})[0]['times']
        if len(last_time) > 0:
            last_time = last_time[-1][0]
            if datetime.now() < last_time + timedelta(minutes=30):
                await ctx.send("You need to wait {0} until you can fish again!".format(str(last_time + timedelta(minutes=30)-datetime.now())))
                return

        self.fish_update(user, datetime.now(), size, weight, ctx.author if gift_to else None)
        if gift_to:
            await ctx.send("{0} fished a {1} fish for {2} worth {3} points!"\
                .format(ctx.author.mention, size, user.mention, weight))
        else:
            await ctx.send("{0} fished a {1} fish worth {2} points!"\
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
        out = '{0}\'s fishing stats\ntimes: {1}\npoints: {2}\ngifted: {3}\nsizes: {4}'.format(
            username, data['count'], data['points'], data['gifted_points'], str(data['sizes']))
        image = self.fish_graph(user)
        await ctx.send(out, file=image)

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
            size = 'monster'
        else:
            gen = random.random()
            print(gen)
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
        print("Fished a {0} of size {1}".format(size, weight))
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
                'times': []
            })
            print('Created data for user', name)

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
                    'times': []
                })
                print('Created data for user', name)

            cur_data = users.find({'id': id})[0]
            users.find_one_and_update({'id': id}, {
                "$set": {
                    'name': name,
                    'points': cur_data['points'] + points,
                    'count': cur_data['count'] + 1
                }
            })
            users.find_one_and_update({'id': id}, {
                "$push": {
                    'times': (time, cur_data['points'])
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
                    'gifted_points': cur_data['gifted_points'] + points
                }
            })
        else:
            cur_data = users.find({'id': id})[0]
            users.find_one_and_update({'id': id}, {
                "$set": {
                    'name': name,
                    'points': cur_data['points'] + points,
                    'count': cur_data['count'] + 1
                }
            })
            users.find_one_and_update({'id': id}, {
                "$push": {
                    'times': (time, cur_data['points'])
                }
            })
            m = 'sizes.' + size
            users.find_one_and_update({'id': id}, {
                "$set": {
                    m: cur_data['sizes'][size] + 1
                }
            })
        return
