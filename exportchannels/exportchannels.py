import discord
import subprocess
import os
from redbot.core import Config, checks, commands, bot, data_manager

class ExportChannels(commands.Cog):
    """Custom cog to export channels to Json and HTML formats using Discord Chat Exporter.
    Developed by SeaswimmerTheFsh and yname."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=48258471944753312)
        self.config.register_global(
            bot_token = "0"
        )


    def export(self, ctx, channel, token):
        self.data_path = data_manager.cog_data_path(self)
        self.bundled_data_path = data_manager.bundled_data_path(self)
        out = f'{self.data_path}/Exported Channels'
        try:
            os.mkdir(out)
        except FileExistsError:
            pass
        args = [
            'dotnet',
            'DiscordChatExporter.Cli.dll',
            'export',
            '--format', 'HtmlDark',
            '--output', f'/{out}/%G (%g)/%C (%c)/Export.html',
            '--token', f'{token}',
            '--channel', {channel},
            '--media',
            '--fuck_russia', 'true',
        ]
        if bot:
            args += '--bot'
        os.chdir(self.bundled_data_path)
        subprocess.call(args)
        args = [
            'dotnet',
            'DiscordChatExporter.Cli.dll',
            'export',
            '--format', 'Json',
            '--output', f'/{out}/%G (%g)/%C (%c)/DCE-f.json',
            '--token', f'{token}',
            '--channel', {channel},
            '--reuse_media',
            '--media',
            '--fuck_russia', 'true',
        ]
        if bot:
            args += '--bot'
        os.chdir(self.bundled_data_path)
        subprocess.call(args)

    @commands.group()
    @checks.is_owner()
    async def exportset(self, ctx):
        """Configuration options for the ExportChannels cog."""

    @exportset.command()
    @checks.is_owner()
    async def token(self, ctx, token: str):
        """Sets the bot token used for Discord Chat Exporter."""
        await self.config.bot_token.set({token})
        await ctx.send(content="Token set!")
        await ctx.delete()
    
    @exportset.command()
    @checks.is_owner()
    async def checkoutputpath(self, ctx):
        """Checks what file path DCE is outputting to."""
        self.data_path = data_manager.cog_data_path(self)
        await ctx.send(content=f"{self.data_path}")

    @commands.command()
    @commands.admin()
    async def exportchannel(self, ctx, channel: discord.Channel):
        """Exports a channel using Discord Chat Exporter."""
        token = await self.config.bot_token
        dce_install = data_manager.bundled_data_path(self)
        if token == 0:
            await ctx.send(content="Please set your token with the ``exportset token`` command!")
            return
        else:
            await self.export(channel.id, token)
