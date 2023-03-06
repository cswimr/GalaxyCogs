import discord
from redbot.core import commands, bank, checks

class SugonCredit(commands.Cog):
    """Implements a way for moderators to give out social-credit like points, dubbed 'sugoncredits' by the community."""
    def __init__(self, bot):
        self.bot = bot

    @commands.group(autohelp=True, aliases=["sugoncredit"])
    @commands.guild_only()
    async def credit(self, ctx):
        """Simple points system."""

    @credit.command()
    @commands.guild_only()
    async def balance(self, ctx, user: discord.Member = None):
        """Checks an account's balance."""
        bank_name = await bank.get_bank_name(ctx.guild)
        currency_name = await bank.get_currency_name(ctx.guild)
        if user == None:
            bal = await bank.get_balance(ctx.author)
            target = ctx.author
        else:
            bal = await bank.get_balance(user)
            target = user
        if bal == 1 or bal == -1:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {bal} {currency_name}.")
        else:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {bal} {currency_name}s.")
        await ctx.send(embed=embed)

    @credit.command()
    @commands.guild_only()
    @commands.mod()
    async def add(self, ctx, target: discord.Member, amount: int):
        """Adds credits to an account."""
        bank_name = await bank.get_bank_name(ctx.guild)
        currency_name = await bank.get_currency_name(ctx.guild)
        current_bal = await bank.get_balance(target)
        max_bal = await bank.get_max_balance(ctx.guild)
        new_bal = current_bal + amount
        if new_bal > max_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to above {max.bal}. Please try again!")
            return
        else:
            embed=discord.Embed(title=f"{bank_name} - Add", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been increased by {amount}.\nCurrent balance is {new_bal}.")
            bank.deposit_credits(target, amount=amount)
            await ctx.send(embed=embed)

    @credit.command()
    @commands.guild_only()
    @commands.mod()
    async def remove(self, ctx, target: discord.Member, amount: int):
        """Removes credits from an account."""
        bank_name = await bank.get_bank_name(ctx.guild)
        currency_name = await bank.get_currency_name(ctx.guild)
        current_bal = await bank.get_balance(target)
        new_bal = current_bal - amount
        if new_bal < 1:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to below 1. Please try again!")
            return
        else:
            embed=discord.Embed(title=f"{bank_name} - Remove", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been decreased by {amount}.\nCurrent balance is {new_bal}.")
            bank.withdraw_credits(target, amount=amount)
            await ctx.send(embed=embed)