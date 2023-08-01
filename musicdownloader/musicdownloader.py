import discord
import yt_dlp
from os import path
from redbot.core import commands, checks, Config, data_manager

class MusicDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=475728338)
        self.config.register_global(
            save_directory = data_manager.cog_data_path()
        )

    @commands.command()
    async def change_data_path(self, ctx: commands.Context, data_path: str = None):
        """This command changes the data path this cog outputs to."""
        old_path = await self.config.save_directory()
        if path.isdir(data_path):
            await self.config.save_directory.set(data_path)
            embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"The save directory has been set to `{data_path}`.\n It was previously set to `{old_path}`.")
            await ctx.send(embed=embed)
        elif path.isfile(data_path):
            await ctx.send("The path you've provided leads to a file, not a directory!")
        elif path.exists(data_path) is False:
            await ctx.send("The path you've provided doesn't exist!")
