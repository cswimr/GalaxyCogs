import discord
from datetime import datetime
from redbot.core.bot import Red
from redbot.core import commands, checks, Config

class Podcast(commands.Cog):
    """Provides a questions submission system for podcasts.
    Developed by SeaswimmerTheFsh."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=27548165)
        self.config.register_guild(
            submission_channel = 0
        )