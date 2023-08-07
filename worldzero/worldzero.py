from redbot.core import commands
import discord

class WorldZero(commands.Cog):
    """This cog is meant to provide random functions for my crippling World Zero addiction!
    Developed by SeaswimmerTheFsh."""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="worldzero", invoke_without_command=True, aliases=['wz'])
    async def worldzero(self, ctx: commands.Context):
        """Tells the user that this command doesn't do anything currently."""
        await ctx.send("This command doesn't do anything currently, have you tried a subcommand?\nCurrent subcommands:\n`-worldzero upgrade` - Checks what the Attack Power/Health of an item will be after upgrading it.\n- See `-help worldzero upgrade` for more information.")

    @worldzero.command(name="upgrade")
    async def worldzero_upgrade(self, ctx: commands.Context, power_amount: str, upgrade_amount: str):
        """Checks what the Attack Power/Health of an item will be after upgrading it.
        **Arguments**

        - The `power_amount` argument is the Attack Power/Health of the item you're looking to upgrade.

        - The `upgrade_amount` argument is the number of times your item can be upgraded."""
        try:
            stat_int = int(f"{power_amount}".replace(",", ""))
            upgrade_int = int(f"{upgrade_amount}".replace(",", ""))
        except ValueError:
            await ctx.send(content="Please input a number!")
            return
        math  = round(stat_int + ((stat_int/15)*upgrade_int))
        output_from = f'{stat_int:,}'
        output_to = f'{math:,}'
        embed = discord.Embed(color=await self.bot.get_embed_color(None))
        embed.add_field(name="Default Power", value=f"{output_from}", inline=False)
        embed.add_field(name="Upgraded Power", value=f"{output_to}", inline=False)
        await ctx.send(embed=embed)
