from datetime import datetime
import random

import discord
from discord.ext import commands

class FishingOld(commands.Cog):
    def __init__(self, bot, cur, conn):
        self.bot = bot
        self.cur = cur
        self.conn = conn

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

    def fish_update(self, iD, time, size, points, gifted_from):
        #Create log entry
        log_query = "insert into fishlog (id, time, size, points) values ({0}, TIMESTAMP '{1}', '{2}', {3});"\
            .format(iD, time, size, points)
        self.cur.execute(log_query)
        self.conn.commit()
        print("Fish log inserted successfully for user of id {0}".format(iD))

        #Add user if new
        self.cur.execute("select id from fishuser where id='{0}';".format(iD))
        if len(self.cur.fetchall()) == 0:
            add_user_query = "insert into fishuser (id, times, trash, tiny, small, medium, large,"\
                        " huge, monster, biggest, average, giftedfish, giftedpoints, points) values"\
                        " ({0}, {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}, {11}, {12}, {13});"\
                        .format(iD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ,0, 0)
            self.cur.execute(add_user_query)
            self.conn.commit()
            print("{0} added".format(iD))
        
        #Update users
        
        #Update giftedfish
        if gifted_from:
            self.cur.execute("update fishuser set giftedfish=giftedfish+1 where id={0}".format(gifted_from))
            self.cur.execute("update fishuser set giftedpoints=giftedpoints+{0} where id={1}".format(points, gifted_from))
            #Look at comments below
            self.cur.execute("update fishuser set times=times+1 where id={0}".format(gifted_from))
            self.cur.execute("update fishuser set {0}={0}+1 where id={1}".format(size, iD))
            self.cur.execute("update fishuser set biggest={0} where id={1} and {0}>biggest".format(points, iD))
            self.cur.execute("update fishuser set points=points+{0} where id={1}".format(points, iD))
            self.cur.execute("update fishuser set average=points/times where times>0 and id={0}".format(iD))
        else:
            #Update times
            self.cur.execute("update fishuser set times=times+1 where id={0}".format(iD))
            #Update size count
            self.cur.execute("update fishuser set {0}={0}+1 where id={1}".format(size, iD))
            #Update biggest
            self.cur.execute("update fishuser set biggest={0} where id={1} and {0}>biggest".format(points, iD))
            #Update points
            self.cur.execute("update fishuser set points=points+{0} where id={1}".format(points, iD))
            #Update average
            self.cur.execute("update fishuser set average=points/times where times>0 and id={0}".format(iD))

        self.conn.commit()
        print("{0} updated".format(iD))

    @commands.command()
    async def fs(self, ctx, other_user: discord.User=None):
        user = other_user if other_user else ctx.author
        self.cur.execute("select * from fishuser where id={0}".format(user.id))
        stats_row = self.cur.fetchall()
        if len(stats_row) == 0:
            await ctx.send("{0} has not fished yet!".format(user.display_name))
            return
        stats_row = stats_row[0]
        
        #Create embed
        embed = discord.Embed(title="{0}'s fishing stats".format(user.display_name), color=discord.Color.blue())
        embed.add_field(name="Total points", value=str(stats_row[13]))
        embed.add_field(name="Times fished", value=str(stats_row[1]))
        embed.add_field(name="Biggest fish", value=str(stats_row[9]))
        embed.add_field(name="Average fish", value=str(stats_row[10]))
        embed.add_field(name="Fish gifted", value=str(stats_row[11]))
        embed.add_field(name="Points gifted", value=str(stats_row[12]))
        embed.add_field(name="_________________", value='\u200b', inline=False)
        if (stats_row[1] > 0):
            embed.add_field(name="Trash", value=str(stats_row[2]) + " (" + str((stats_row[2]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Tiny", value=str(stats_row[3]) + " (" + str((stats_row[3]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Small", value=str(stats_row[4]) + " (" + str((stats_row[4]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Medium", value=str(stats_row[5]) + " (" + str((stats_row[5]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Large", value=str(stats_row[6]) + " (" + str((stats_row[6]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Huge", value=str(stats_row[7]) + " (" + str((stats_row[7]/stats_row[1])*100)[:5] + "%)")
            embed.add_field(name="Monster", value=str(stats_row[8]) + " (" + str((stats_row[8]/stats_row[1])*100)[:5] + "%)")
        await ctx.send(embed=embed)
