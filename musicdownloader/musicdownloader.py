import asyncio
import re
import discord
import os
from yt_dlp import YoutubeDL
from redbot.core import commands, checks, Config, data_manager

class MusicDownloader(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=475728338)
        self.config.register_global(
            save_directory = str(data_manager.cog_data_path()) + f"{os.sep}MusicDownloader"
        )

    @commands.command()
    @checks.is_owner()
    async def change_data_path(self, ctx: commands.Context, *, data_path: str = None):
        """This command changes the data path this cog outputs to."""
        old_path = await self.config.save_directory()
        if not data_path:
            await ctx.send(f"The current data path is `{old_path}`.")
            return
        if os.path.isdir(data_path):
            await self.config.save_directory.set(data_path)
            embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"The save directory has been set to `{data_path}`.\n It was previously set to `{old_path}`.")
            await ctx.send(embed=embed)
        elif os.path.isfile(data_path):
            await ctx.send("The path you've provided leads to a file, not a directory!")
        elif os.path.exists(data_path) is False:
            await ctx.send("The path you've provided doesn't exist!")

    @commands.command(aliases=["dl"])
    async def download(self, ctx: commands.Context, url: str, delete: bool = False, subfolder: str = None):
        """This command downloads a YouTube Video as an MP3 to the local music directory."""
        def youtube_download(self, url: str, path: str, message: discord.Message):
            """This function does the actual downloading of the YouTube Video."""
            class Logger:
                def debug(self, msg):
                    if msg.startswith('[debug] '):
                        pass
                    else:
                        self.info(msg)
                def info(self, msg):
                    pass
                def warning(self, msg):
                    pass
                def error(self, msg):
                    print(msg)
                    message.edit(msg)
            ydl_opts = {
            'logger': Logger(),
            'format': 'm4a/bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'm4a',}],
            'paths': {'home': path},
            'verbose': True
            }
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url=url, download=False)
                title = info['title']
                id = info['id']
            filename = title + f' [{id}].m4a'
            full_filename = os.path.join(data_path, filename)
            if os.path.isfile(full_filename):
                previously_existed = True
            else:
                with YoutubeDL(ydl_opts) as ydl:
                    error_code = ydl.download(url)
                    previously_existed = False
            return filename, previously_existed
        data_path = await self.config.save_directory()
        if subfolder and await self.bot.is_owner(ctx.author):
            data_path = os.path.join(data_path, subfolder)
            illegal_chars = r'<>:"/\|?*'
            if any(char in illegal_chars for char in subfolder):
                pattern = "[" + re.escape(illegal_chars) + "]"
                modified_subfolder = re.sub(pattern, r'__**\g<0>**__', subfolder)
                await ctx.send(f"Your subfolder contains illegal characters: `{modified_subfolder}`")
                return
            elif os.path.isfile(data_path):
                await ctx.send("Your 'subfolder' is a file, not a directory!")
                return
            elif os.path.exists(data_path) is False:
                message = await ctx.send("Your subfolder does not exist yet, would you like to continue? It will be automatically created.")
                def check(message):
                    return message.author == ctx.author and message.content.lower() in ['yes', 'ye', 'y']
                try:
                    await self.bot.wait_for('message', check=check, timeout=60) # Timeout after 60 seconds
                except asyncio.TimeoutError:
                    await message.edit("You took too long to respond.")
                else:
                    await message.edit("Confirmed!")
                    try:
                        os.makedirs(data_path)
                    except OSError as e:
                        await message.edit(f"Encountered an error attempting to create the subfolder!\n`{e}`")
                    msg = message.edit
        else:
            msg = ctx.send
        message = await msg("YouTube Downloader started!")
        ytdlp_output = youtube_download(self, url, data_path, message)
        full_filename = os.path.join(data_path, ytdlp_output[0])
        while not os.path.isfile(full_filename):
            await asyncio.sleep(0.5)
        if os.path.isfile(full_filename):
            with open(full_filename, 'rb') as file:
                complete_message = await ctx.send(content="YouTube Downloader completed!\nDownloaded file:", file=discord.File(file, ytdlp_output[0]))
            file.close()
            if delete is True or await self.bot.is_owner(ctx.author) is False:
                if ytdlp_output[1] is False:
                    os.remove(full_filename)
                    await complete_message.edit(content="YouTube Downloader completed!\nFile has been deleted from Galaxy.\nDownloaded file:")
