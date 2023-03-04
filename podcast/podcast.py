import discord
from datetime import datetime
from redbot.core.bot import Red
from redbot.core import commands, checks, Config, bot

class Podcast(commands.Cog):
    """Provides a questions submission system for podcasts.
    Developed by SeaswimmerTheFsh."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=27548165)
        self.config.register_global(
            global_submission_channel = 0,
            global_blacklisted_users = {}
        )
        self.config.register_guild(
            submission_channel = 0,
            blacklisted_users = {},
            global_mode = True
        )

    @commands.command()
    async def podcast(self, ctx, question: str):
        """Submits a question to the Podcast."""
        if await self.config.guild(ctx.guild).global_mode(True):
            submission_channel = bot.get_channel(await self.config.global_submission_channel())
            blacklisted_users = await self.config.global_blacklisted_users()
        elif await self.config.guild(ctx.guild).global_mode(False):
            submission_channel = bot.get_channel(await self.config.guild(ctx.guild).submission_channel())
            blacklisted_users = await self.config.guild(ctx.guild).blacklisted_users()
        else:
            return
        await submission_channel.send(content=f"{question}")
        await ctx.send(content="Question submitted!")

        @commands.group(autohelp=True)
        @checks.is_admin_or_superior()
        async def podcastset(self):
            """Commands to configure the Podcast cog."""