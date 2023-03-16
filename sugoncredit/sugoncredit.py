import discord
from redbot.core import commands, checks, data_manager, Config
import sqlite3
from sqlite3 import Error

class SugonCredit(commands.Cog):
    """Implements a way for moderators to give out social-credit like points, dubbed 'sugoncredits' by the community."""
    
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=47252584)
        self.config.register_guild(
            bank_name = "Social Credit Enforcement Agency",
            currency_name = "Social Credit",
            max_bal = 1000000000,
            min_bal = -1000000000
        )
        self.data_path = data_manager.cog_data_path(self) / "credit.db"
        con = sqlite3.connect(f'{self.data_path}')
        con.commit()
        con.close()

    def new_guild_generation(self, guild_id):
        """Adds a new table for a guild to the SQLite databse."""
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        exist_check = cur.execute(f'''IF EXISTS 
            (SELECT object_id FROM sys.tables
            WHERE name = '{guild_id}'
            AND SCHEMA_NAME(schema_id) = 'dbo')
            PRINT 'False'
        ELSE 
            PRINT 'True';''')
        if exist_check == False:
            cur.execute(f'''CREATE TABLE '{guild_id}' (username text, user_id text, balance real)''')
            con.commit()
        con.close()
        
    def new_user_generation(self, guild_id, target):
        """Adds a new user to the SQLite database."""
        username = str(target)
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        cur.execute(f'''INSERT INTO {guild_id}
        VALUES ('{username}', {target.id}, 250);''')
        con.commit()
        con.close()
    
    def username_updater(self, guild_id, target):
        """Updates a users' username in the SQLite database."""
        new_username = str(target)
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        cur.execute(f'''UPDATE {guild_id}
        SET username = '{new_username}'
        WHERE user_id = {target.id};''')
        con.commit()
        con.close()
    
    @commands.group(autohelp=True, aliases=["sugoncredit"])
    @commands.guild_only()
    async def credit(self, ctx):
        """Simple points system."""

    @credit.command()
    @commands.guild_only()
    async def leaderboard(self, ctx, page: int = 1):
        """Shows the individuals with the highest balances."""
        await ctx.send(content="This command isn't done yet!")
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        await self.new_guild_generation(self, ctx.guild.id)
        bank_name = await self.config.guild(ctx.guild).bank_name()
        currency_name = await self.config.guild(ctx.guild).currency_name()
        offset = (page - 1) * 10
        raw_list = cur.execute(f'''SELECT user_id, balance FROM {ctx.guild.id}
        ORDER BY balance DESC
        LIMIT 10 OFFSET {offset};''')
        await ctx.send(content=f"{raw_list}")

    @credit.command()
    @commands.guild_only()
    async def balance(self, ctx, user: discord.Member = None):
        """Checks an account's balance."""
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        await self.new_guild_generation({ctx.guild.id})
        bank_name = await self.config.guild(ctx.guild).bank_name()
        currency_name = await self.config.guild(ctx.guild).currency_name()
        if user == None:
            target = ctx.author
        else:
            target = user
        if cur.execute(f'''SELECT user_id FROM {ctx.guild.id}
        WHERE EXISTS (SELECT user_id FROM {ctx.guild.id} WHERE {target.id});''')=="FALSE":
            await self.new_user_generation({ctx.guild.id}, target)
        stored_username = cur.execute(f'''SELECT username FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        if str(target) != stored_username:
            await self.username_updater({ctx.guild.id}, target)
        bal = cur.execute(f'''SELECT balance FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        output_bal = (f'{bal:,}')
        if bal == 1 or bal == -1:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {output_bal} {currency_name}.")
        else:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {output_bal} {currency_name}s.")
        await ctx.send(embed=embed)
        con.close()

    @credit.command()
    @commands.guild_only()
    @commands.mod()
    async def add(self, ctx, target: discord.Member, amount: int):
        """Adds credits to an account."""
        try:
            val = int(amount)
        except ValueError:
            await ctx.send(content="``amount`` must be a number! Please try again.")
            return
        con = sqlite3.connect(f'{self.data_path}')
        cur = con.cursor()
        await self.new_guild_generation({ctx.guild.id})
        image = discord.File(fp=data_manager.bundled_data_path(self) / "add.png", filename="Add.png")
        bank_name = await self.config.bank_name()
        currency_name = await self.config.currency_name()
        max_bal = await self.config.max_bal()
        min_bal = await self.config_min_bal()
        if cur.execute(f'''SELECT user_id FROM {ctx.guild.id}
        WHERE EXISTS (SELECT user_id FROM {ctx.guild.id} WHERE {target.id});''')=="FALSE":
            await self.new_user_generation({ctx.guild.id}, target)
        stored_username = cur.execute(f'''SELECT username FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        if str(target) != stored_username:
            await self.username_updater({ctx.guild.id}, target)
        current_bal = cur.execute(f'''SELECT balance FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        new_bal = current_bal + amount
        output_amount = (f'{val:,}')
        output_new_bal = (f'{new_bal:,}')
        output_max_bal = (f'{max_bal:,}')
        output_min_bal = (f'{min_bal:,}')
        if new_bal > max_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to above {output_max_bal}. Please try again!")
            return
        elif new_bal < min_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to below {output_min_bal}. Please try again!")
        elif ctx.guild.id == 204965774618656769:
            logging_channel = self.bot.get_channel(1082495815878189076)
            cur.execute(f'''UPDATE {ctx.guild.id}
            SET balance = {new_bal}
            WHERE user_id = {target.id};''')
            await ctx.send(content=f"{target.mention} now has {output_amount} more SugonCredit, with a total of {output_new_bal}!")
            if amount == 1 or amount == -1:
                await target.send(content=f"You gained {output_amount} SugonCredit! Good work community member! You now have {output_new_bal} SugonCredits.", file=image)
            else:
                await target.send(content=f"You gained {output_amount} SugonCredits! Good work community member! You now have {output_new_bal} SugonCredits.", file=image)
            logging_embed=discord.Embed(title="SugonCredit Added", color=await self.bot.get_embed_color(None), description=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) added {amount} SugonCredit to {target.name}#{target.discriminator} ({target.id})! They now have {new_bal} SugonCredit.")
            await logging_channel.send(embed=logging_embed)
        elif ctx.guild.id != 204965774618656769:
            embed=discord.Embed(title=f"{bank_name} - Add", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been increased by {output_amount}.\nCurrent balance is {output_new_bal}.")
            cur.execute(f'''UPDATE {ctx.guild.id}
            SET balance = {new_bal}
            WHERE user_id = {target.id};''')
            await ctx.send(embed=embed)
            con.commit()
            con.close()

    @credit.command()
    @commands.guild_only()
    @commands.mod()
    async def remove(self, ctx, target: discord.Member, amount: int):
        """Removes credits from an account."""
        try:
            val = int(amount)
        except ValueError:
            await ctx.send(content="``amount`` must be a number. Please try again!")
            return
        image = discord.File(fp=data_manager.bundled_data_path(self) / "remove.mp4", filename="MEGA_BASE.mp4")
        data_path = data_manager.cog_data_path(self) / "credit.db"
        con = sqlite3.connect(f'{data_path}')
        cur = con.cursor()
        await self.new_guild_generation({ctx.guild.id})
        bank_name = await self.config.bank_name()
        currency_name = await self.config.currency_name()
        max_bal = await self.config.max_bal()
        min_bal = await self.config_min_bal()
        if cur.execute(f'''SELECT user_id FROM {ctx.guild.id}
        WHERE EXISTS (SELECT user_id FROM {ctx.guild.id} WHERE {target.id});''')=="FALSE":
            await self.new_user_generation({ctx.guild.id}, target)
        stored_username = cur.execute(f'''SELECT username FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        if str(target) != stored_username:
            await self.username_updater({ctx.guild.id}, target)
        current_bal = cur.execute(f'''SELECT balance FROM {ctx.guild.id}
        WHERE user_id = {target.id};''')
        new_bal = current_bal - amount
        output_amount = (f'{val:,}')
        output_new_bal = (f'{new_bal:,}')
        output_max_bal = (f'{max_bal:,}')
        output_min_bal = (f'{min_bal:,}')
        if new_bal > max_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to above {output_max_bal}. Please try again!")
        elif new_bal < min_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to below {output_min_bal}. Please try again!")
        elif ctx.guild.id == 204965774618656769:
            cur.execute(f'''UPDATE {ctx.guild.id}
            SET balance = {new_bal}
            WHERE user_id = {target.id};''')
            logging_channel = self.bot.get_channel(1082495815878189076)
            await ctx.send(content=f"{target.mention} now has {output_amount} less SugonCredit, with a total of {output_new_bal}!\nIf this is a punishment, do better Galaxy Player! Re-education mods will be sent to your DM's if your SugonCredit drops to a substantially low amount!")
            if amount == 1 or amount == -1:
                await target.send(content=f"__MESSAGE FROM THE MINISTRY OF THE MEGA BASE__\n\n(我们的) {output_amount} SugonCredit has been taken from your account. Citizen, do not continue to preform bad actions! Glory to the Galaxy Communist Party!", file=image)
            else:
                await target.send(content=f"__MESSAGE FROM THE MINISTRY OF THE MEGA BASE__\n\n(我们的) {output_amount} SugonCredits have been taken from your account. Citizen, do not continue to preform bad actions! Glory to the Galaxy Communist Party!", file=image)
            logging_embed=discord.Embed(title="SugonCredit Removed", color=await self.bot.get_embed_color(None), description=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) removed {output_amount} SugonCredit from {target.name}#{target.discriminator} ({target.id})! They now have {output_new_bal} SugonCredit.")
            await logging_channel.send(embed=logging_embed)
        elif ctx.guild.id != 204965774618656769:
            embed=discord.Embed(title=f"{bank_name} - Remove", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been decreased by {output_amount}.\nCurrent balance is {output_new_bal}.")
            await ctx.send(embed=embed)
            cur.execute(f'''UPDATE {ctx.guild.id}
            SET balance = {new_bal}
            WHERE user_id = {target.id};''')
            con.commit()
            con.close()