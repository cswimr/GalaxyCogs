from typing import Union
import discord
from redbot.core import commands, checks, app_commands

class Say(commands.Cog):
    """Allows you to send messages as the bot account."""

    def __init__(self, bot):
        self.bot = bot

    async def send_to_target(self, target: Union[discord.Member, discord.TextChannel], interaction: discord.Interaction, message: str, secondary_message: str = None):
        if isinstance(target, discord.Member):
            target_type = "member"
        elif isinstance(target, discord.TextChannel):
            target_type = "textchannel"
        try:
            await target.send(message)
            if secondary_message is not None:
                await target.send(secondary_message)
                await interaction.response.send_message(content=f"Message sent to {target.mention}!\nMessage contents:\n```{message}```\n```{secondary_message}```", ephemeral=True)
            else:
                await interaction.response.send_message(content=f"Message sent to {target.mention}!\nMessage contents:\n```{message}```", ephemeral=True)
        except (discord.HTTPException, discord.Forbidden) as error:
            if target_type == "member":
                await interaction.response.send_message(content="That user has their direct messages closed!", ephemeral=True)
            elif target_type == "textchannel":
                await interaction.response.send_message(content="I cannot access that channel!", ephemeral=True)

    class MessageModal(discord.ui.Modal, title="Sending message..."):
        def __init__(self, target):
            super().__init__()
            self.target = target
        message = discord.ui.TextInput(
            label="Message Content",
            placeholder="I'm contacting you about your cars extended warranty...",
            style=discord.TextStyle.paragraph,
            max_length=1750
        )
        secondary_message = discord.ui.TextInput(
            label="Secondary Message Content",
            placeholder="Typically used for images/image links.",
            style=discord.TextStyle.short,
            required=False,
            max_length=200
        )

        async def on_submit(self, interaction: discord.Interaction):
            await Say.send_to_target(self, self.target, interaction, self.message, self.secondary_message)

    send = app_commands.Group(name="send", description="Send a message as the bot user!")

    @send.command(name="user", description="Sends a direct message to a user.")
    async def user(self, interaction: discord.Interaction, member: discord.Member, message: str = None):
        """Sends a direct message to a user."""
        if message:
            await Say.send_to_target(self, member, interaction, message)
        else:
            await interaction.response.send_modal(Say.MessageModal(member))

    @send.command(name="channel", description="Sends a message to a channel.")
    async def channel(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str = None):
        """Sends a message to a channel."""
        if message:
            await Say.send_to_target(self, channel, interaction, message)
        else:
            await interaction.response.send_modal(Say.MessageModal(channel))
