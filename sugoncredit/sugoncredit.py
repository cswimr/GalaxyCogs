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
        output_bal = (f'{bal:,}')
        if bal == 1 or bal == -1:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {output_bal} {currency_name}.")
        else:
            embed=discord.Embed(title=f"{bank_name} - Balance", color=await self.bot.get_embed_color(None), description=f"{target.mention} has {output_bal} {currency_name}s.")
        await ctx.send(embed=embed)

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
        bank_name = await bank.get_bank_name(ctx.guild)
        currency_name = await bank.get_currency_name(ctx.guild)
        current_bal = await bank.get_balance(target)
        max_bal = await bank.get_max_balance(ctx.guild)
        new_bal = current_bal + amount
        output_amount = (f'{val:,}')
        output_new_bal = (f'{new_bal:,}')
        output_max_bal = (f'{max_bal:,}')
        if new_bal > max_bal:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to above {output_max_bal}. Please try again!")
            return
        elif new_bal < 0:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to below 0. Please try again!")
            return
        elif ctx.guild.id == 204965774618656769:
            logging_channel = self.bot.get_channel(1082495815878189076)
            await bank.deposit_credits(target, amount=amount)
            await ctx.send(content=f"{target.mention} now has {output_amount} more SugonCredit, with a total of {output_new_bal}!")
            if amount == 1 or amount == -1:
                await target.send(content=f"You gained {output_amount} SugonCredit! Good work community member! You now have {output_new_bal} SugonCredits.")
            else:
                await target.send(content=f"You gained {output_amount} SugonCredits! Good work community member! You now have {output_new_bal} SugonCredits.")
            await target.send(content="https://cdn.discordapp.com/attachments/932790367043063818/1016032836576362556/social-credit-positive.png")
            logging_embed=discord.Embed(title="SugonCredit Added", color=await self.bot.get_embed_color(None), description=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) added {amount} SugonCredit to {target.name}#{target.discriminator} ({target.id})! They now have {new_bal} SugonCredit.")
            await logging_channel.send(embed=logging_embed)
        elif ctx.guild.id != 204965774618656769:
            embed=discord.Embed(title=f"{bank_name} - Add", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been increased by {output_amount}.\nCurrent balance is {output_new_bal}.")
            await bank.deposit_credits(target, amount=amount)
            await ctx.send(embed=embed)

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
        bank_name = await bank.get_bank_name(ctx.guild)
        currency_name = await bank.get_currency_name(ctx.guild)
        current_bal = await bank.get_balance(target)
        new_bal = current_bal - amount
        output_amount = (f'{val:,}')
        output_new_bal = (f'{new_bal:,}')
        if new_bal < 0:
            await ctx.send(content=f"You are attempting to set {target.mention}'s balance to below 0. Please try again!")
            return
        elif ctx.guild.id == 204965774618656769:
            await bank.withdraw_credits(target, amount=amount)
            logging_channel = self.bot.get_channel(1082495815878189076)
            await ctx.send(content=f"{target.mention} now has {output_amount} less SugonCredit, with a total of {output_new_bal}!\nIf this is a punishment, do better Galaxy Player! Re-education mods will be sent to your DM's if your SugonCredit drops to a substantially low amount!")
            if amount == 1 or amount == -1:
                await target.send(content=f"__MESSAGE FROM THE MINISTRY OF THE MEGA BASE__\n\n(我们的) {output_amount} SugonCredit has been taken from your account. Citizen, do not continue to preform bad actions! Glory to the Galaxy Communist Party!")
            else:
                await target.send(content=f"__MESSAGE FROM THE MINISTRY OF THE MEGA BASE__\n\n(我们的) {output_amount} SugonCredits have been taken from your account. Citizen, do not continue to preform bad actions! Glory to the Galaxy Communist Party!")
            await target.send(content="https://cdn.discordapp.com/attachments/408777890222571530/909534123004133497/MEGA_BASE.mp4")
            logging_embed=discord.Embed(title="SugonCredit Removed", color=await self.bot.get_embed_color(None), description=f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id}) removed {output_amount} SugonCredit from {target.name}#{target.discriminator} ({target.id})! They now have {output_new_bal} SugonCredit.")
            await logging_channel.send(embed=logging_embed)
        elif ctx.guild.id != 204965774618656769:
            embed=discord.Embed(title=f"{bank_name} - Remove", color=await self.bot.get_embed_color(None), description=f"{target.mention}'s {currency_name} balance has been decreased by {output_amount}.\nCurrent balance is {output_new_bal}.")
            await ctx.send(embed=embed)
            await bank.withdraw_credits(target, amount=val)