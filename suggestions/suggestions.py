import discord
import datetime
import typing

from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import humanize_list

from redbot.core.bot import Red


class Suggestions(commands.Cog):
    """
    Per guild, as well as global, suggestion box voting system.
    """

    __version__ = "1.7.1"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=2115656421364, force_registration=True
        )
        self.config.register_guild(
            same=False,
            suggest_id=None,
            approve_id=None,
            denied_id=None,
            next_id=1,
            up_emoji=1071095785455886436,
            down_emoji=1071096039119007804,
            delete_suggest=True,
            delete_suggestion=True,
            anonymous=False,
        )
        self.config.init_custom("SUGGESTION", 2)  # server_id, suggestion_id
        self.config.register_custom(
            "SUGGESTION",
            author=[],  # id, name, discriminator
            guild_id=0,
            msg_id=0,
            finished=False,
            approved=False,
            denied=False,
            reason=False,
            stext=None,
            rtext=None,
        )

    async def red_delete_data_for_user(self, *, requester, user_id):
        # per guild suggestions
        for guild in self.bot.guilds:
            for suggestion_id in range(1, await self.config.guild(guild).next_id()):
                author_info = await self.config.custom(
                    "SUGGESTION", guild.id, suggestion_id
                ).author()
                if user_id in author_info:
                    await self.config.custom(
                        "SUGGESTION", guild.id, suggestion_id
                    ).author.clear()

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f"{context}\n\nVersion: {self.__version__}"

    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(add_reactions=True)
    async def suggest(self, ctx: commands.Context, *, suggestion: str):
        """Suggest something."""
        suggest_id = await self.config.guild(ctx.guild).suggest_id()
        if not suggest_id:
            if not await self.config.toggle():
                return await ctx.send("Uh oh, suggestions aren't enabled.")
            if ctx.guild.id in await self.config.ignore():
                return await ctx.send("Uh oh, suggestions aren't enabled.")
        else:
            channel = ctx.guild.get_channel(suggest_id)
        if not channel:
            return await ctx.send(
                "Uh oh, looks like the Admins haven't added the required channel."
            )
        embed = discord.Embed(color=await ctx.embed_colour(), description=suggestion)
        footer = [f"Suggested by {ctx.author.name}#{ctx.author.discriminator}",
                  ctx.author.avatar_url]
        author = [f"{ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})", ctx.author.avatar_url]
        embed.set_footer(
            text=footer[0],
            icon_url=footer[1]
        )
        embed.set_author(
            name=author[0],
            icon_url=author[1]
        )
        if ctx.message.attachments:
            embed.set_image(url=ctx.message.attachments[0].url)

        s_id = await self.config.guild(ctx.guild).next_id()
        await self.config.guild(ctx.guild).next_id.set(s_id + 1)
        server = ctx.guild.id
        content = f"Suggestion #{s_id}"
        embed.title = content
        msg = await channel.send(embed=embed)

        up_emoji, down_emoji = await self._get_emojis(ctx)
        await msg.add_reaction(up_emoji)
        await msg.add_reaction(down_emoji)

        async with self.config.custom("SUGGESTION", server, s_id).author() as author:
            author.append(ctx.author.id)
            author.append(ctx.author.name)
            author.append(ctx.author.discriminator)
        await self.config.custom("SUGGESTION", server, s_id).guild_id.set(ctx.guild.id)
        await self.config.custom("SUGGESTION", server, s_id).stext.set(suggestion)
        await self.config.custom("SUGGESTION", server, s_id).msg_id.set(msg.id)

        if await self.config.guild(ctx.guild).delete_suggest():
            try:
                await ctx.message.delete()
            except discord.errors.NotFound:
                pass
        else:
            await ctx.tick()

    @checks.admin()
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_messages=True)
    async def approve(
            self,
            ctx: commands.Context,
            suggestion_id: int,
            *,
            reason: typing.Optional[str],
    ):
        """Approve a suggestion."""
        await self._finish_suggestion(ctx, suggestion_id,  True, reason, ctx.author)

    @checks.admin()
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_messages=True)
    async def deny(
            self,
            ctx: commands.Context,
            suggestion_id: int,
            *,
            reason: typing.Optional[str],
    ):
        """Deny a suggestion. Reason is optional."""
        await self._finish_suggestion(ctx, suggestion_id, False, reason, ctx.author)

    @checks.admin()
    @commands.command()
    @commands.guild_only()
    @checks.bot_has_permissions(manage_messages=True)
    async def addreason(
            self,
            ctx: commands.Context,
            suggestion_id: int,
            *,
            reason: str,
    ):
        server = ctx.guild.id
        author = ctx.author
        approved_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).approve_id()
        )
        reject_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).denied_id()
        )

        msg_id = await self.config.custom("SUGGESTION", server, suggestion_id).msg_id()
        try:
            old_msg = await approved_channel.fetch_message(msg_id)
            approve = True
        except discord.NotFound:
            try:
                old_msg = await reject_channel.fetch_message(msg_id)
                approve = False
            except discord.NotFound:
                return await ctx.send("Uh oh, message with this ID doesn't exist.")
        if not old_msg:
            return await ctx.send("Uh oh, message with this ID doesn't exist.")
        embed = old_msg.embeds[0]
        content = old_msg.content
        approved = "Approved" if approve else "Denied"
        embed.title = f"Suggestion {approved} (#{suggestion_id})"
        footer = [f"{approved} by {author.name}#{author.discriminator} ({author.id}",
                  author.avatar_url_as(format="png", size=512)]
        embed.set_footer(
            text=footer[0],
            icon_url=footer[1]
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
            await self.config.custom("SUGGESTION", server, suggestion_id).reason.set(
                True
            )
            await self.config.custom("SUGGESTION", server, suggestion_id).rtext.set(
                reason
            )

        await old_msg.edit(content=content, embed=embed)
        await ctx.tick()

    @checks.admin()
    @checks.bot_has_permissions(
        manage_channels=True, add_reactions=True, manage_messages=True
    )
    @commands.group(autohelp=True, aliases=["suggestion"])
    @commands.guild_only()
    async def suggestset(self, ctx: commands.Context):
        """Various Suggestion settings."""

    @suggestset.command(name="channel")
    async def suggestset_channel(
            self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]
    ):
        """Set the channel for suggestions.

        If the channel is not provided, suggestions will be disabled."""
        if channel:
            await self.config.guild(ctx.guild).suggest_id.set(channel.id)
        else:
            await self.config.guild(ctx.guild).suggest_id.clear()
        await ctx.tick()

    @suggestset.command(name="approved")
    async def suggestset_approved(
            self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]
    ):
        """Set the channel for approved suggestions.

        If the channel is not provided, approved suggestions will not be reposted."""
        old_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).approve_id())
        if channel:
            await self.config.guild(ctx.guild).approve_id.set(channel.id)
            if ctx.guild.get_channel(await self.config.guild(ctx.guild).approve_id()) == \
                    ctx.guild.get_channel(await self.config.guild(ctx.guild).denied_id()):
                await ctx.send("Cannot make approved and denied the same channel!hjo8")
                try:
                    await self.config.guild(ctx.guild).approve_id.set(old_channel.id)
                except AttributeError:
                    await self.config.guild(ctx.guild).approve_id.clear()
                return
        else:
            await self.config.guild(ctx.guild).approve_id.clear()
        await ctx.tick()

    @suggestset.command(name="denied")
    async def suggestset_denied(
            self, ctx: commands.Context, channel: typing.Optional[discord.TextChannel]
    ):
        """Set the channel for denied suggestions.

        If the channel is not provided, denied suggestions will not be reposted."""
        old_channel = ctx.guild.get_channel(await self.config.guild(ctx.guild).denied_id())
        if channel:
            await self.config.guild(ctx.guild).denied_id.set(channel.id)
            if ctx.guild.get_channel(await self.config.guild(ctx.guild).approve_id()) == \
                    ctx.guild.get_channel(await self.config.guild(ctx.guild).denied_id()):
                await ctx.send("Cannot make approved and denied the same channel!")
                try:
                    await self.config.guild(ctx.guild).denied_id.set(old_channel.id)
                except AttributeError:
                    await self.config.guild(ctx.guild).denied_id.clear()
                return
        else:
            await self.config.guild(ctx.guild).denied_id.clear()
        await ctx.tick()

    @suggestset.command(name="same")
    async def suggestset_same(self, ctx: commands.Context, same: bool):
        """Set whether to use the same channel for new and finished suggestions."""
        await ctx.send(
            "Suggestions won't be reposted anywhere, only their title will change accordingly."
            if same
            else "Suggestions will go to their appropriate channels upon approving/denying."
        )
        await self.config.guild(ctx.guild).same.set(same)

    @suggestset.command(name="upemoji")
    async def suggestset_upemoji(
            self, ctx: commands.Context, up_emoji: typing.Optional[discord.Emoji]
    ):
        """Set a custom upvote emoji instead of <:upvote:1071095785455886436>."""
        if not up_emoji:
            await self.config.guild(ctx.guild).up_emoji.clear()
        else:
            try:
                await ctx.message.add_reaction(up_emoji)
            except discord.HTTPException:
                return await ctx.send("Uh oh, I cannot use that emoji.")
            await self.config.guild(ctx.guild).up_emoji.set(up_emoji.id)
        await ctx.tick()

    @suggestset.command(name="downemoji")
    async def suggestset_downemoji(
            self, ctx: commands.Context, down_emoji: typing.Optional[discord.Emoji]
    ):
        """Set a custom downvote emoji instead of <:downvote:1071096039119007804>."""
        if not down_emoji:
            await self.config.guild(ctx.guild).down_emoji.clear()
        else:
            try:
                await ctx.message.add_reaction(down_emoji)
            except discord.HTTPException:
                return await ctx.send("Uh oh, I cannot use that emoji.")
            await self.config.guild(ctx.guild).down_emoji.set(down_emoji.id)
        await ctx.tick()

    @suggestset.command(name="autodelete")
    async def suggestset_autodelete(
            self, ctx: commands.Context, on_off: typing.Optional[bool]
    ):
        """Toggle whether after `[p]suggest`, the bot deletes the command message."""
        target_state = on_off or not (
            await self.config.guild(ctx.guild).delete_suggest()
        )

        await self.config.guild(ctx.guild).delete_suggest.set(target_state)
        await ctx.send(
            "Auto deletion is now enabled."
            if target_state
            else "Auto deletion is now disabled."
        )

    @suggestset.command(name="delete")
    async def suggestset_delete(
            self, ctx: commands.Context, on_off: typing.Optional[bool]
    ):
        """Toggle whether suggestions in the original suggestion channel get deleted after being approved/denied.

        If `on_off` is not provided, the state will be flipped."""
        target_state = on_off or not (
            await self.config.guild(ctx.guild).delete_suggestion()
        )

        await self.config.guild(ctx.guild).delete_suggestion.set(target_state)
        await ctx.send(
            "Suggestions will be deleted upon approving/denying from the original suggestion channel."
            if target_state
            else "Suggestions will stay in the original channel after approving/denying."
        )

    @suggestset.command(name="settings")
    async def suggestset_settings(self, ctx: commands.Context):
        """See current settings."""
        data = await self.config.guild(ctx.guild).all()
        suggest_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).suggest_id()
        )
        suggest_channel = "None" if not suggest_channel else suggest_channel.mention
        approve_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).approve_id()
        )
        approve_channel = "None" if not approve_channel else approve_channel.mention
        reject_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).denied_id()
        )
        reject_channel = "None" if not reject_channel else reject_channel.mention
        up_emoji, down_emoji = await self._get_emojis(ctx)

        embed = discord.Embed(
            colour=await ctx.embed_colour()
        )
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.title = "**__Suggestion settings (guild):__**"

        embed.set_footer(text="*required to function properly")
        embed.add_field(name="Same channel*:", value=str(data["same"]), inline=False)
        embed.add_field(name="Suggest channel*:", value=suggest_channel)
        embed.add_field(name="Approved channel:", value=approve_channel)
        embed.add_field(name="Denied channel:", value=reject_channel)
        embed.add_field(name="Up emoji:", value=up_emoji)
        embed.add_field(name="Down emoji:", value=down_emoji)
        embed.add_field(
            name=f"Delete `{ctx.clean_prefix}suggest` upon use:",
            value=data["delete_suggest"],
            inline=False,
        )
        embed.add_field(
            name="Delete suggestion upon approving/denying:",
            value=data["delete_suggestion"],
            inline=False,
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        message = reaction.message
        if user.id == self.bot.user.id:
            return
        if not message.guild:
            return
        # server suggestions
        if message.channel.id == await self.config.guild(message.guild).suggest_id():
            for message_reaction in message.reactions:
                if (
                        message_reaction.emoji != reaction.emoji
                        and user in await message_reaction.users().flatten()
                ):
                    await message_reaction.remove(user)

    async def _get_results(self, ctx, message):
        up_emoji, down_emoji = await self._get_emojis(ctx)
        up_count = 0
        down_count = 0

        for reaction in message.reactions:
            if reaction.emoji == up_emoji:
                up_count = reaction.count - 1  # minus the bot
            if reaction.emoji == down_emoji:
                down_count = reaction.count - 1  # minus the bot

        return f"{up_count}x {up_emoji}\n{down_count}x {down_emoji}"

    async def _get_emojis(self, ctx):
        up_emoji = self.bot.get_emoji(await self.config.guild(ctx.guild).up_emoji())
        if not up_emoji:
            up_emoji = "âœ…"
        down_emoji = self.bot.get_emoji(await self.config.guild(ctx.guild).down_emoji())
        if not down_emoji:
            down_emoji = "âŽ"
        return up_emoji, down_emoji

    async def _finish_suggestion(self, ctx, suggestion_id, approve, reason, author):
        server = ctx.guild.id
        old_channel = ctx.guild.get_channel(
            await self.config.guild(ctx.guild).suggest_id()
        )
        if approve:
            channel = ctx.guild.get_channel(
                await self.config.guild(ctx.guild).approve_id()
            )
        else:
            channel = ctx.guild.get_channel(
                await self.config.guild(ctx.guild).denied_id()
            )
        msg_id = await self.config.custom("SUGGESTION", server, suggestion_id).msg_id()
        if (
                msg_id != 0
                and await self.config.custom("SUGGESTION", server, suggestion_id).finished()
        ):
            return await ctx.send("This suggestion has been finished already.")
        try:
            old_msg = await old_channel.fetch_message(msg_id)
        except discord.NotFound:
            return await ctx.send("Uh oh, message with this ID doesn't exist.")
        if not old_msg:
            return await ctx.send("Uh oh, message with this ID doesn't exist.")
        embed = old_msg.embeds[0]
        content = old_msg.content

        approved = "Approved" if approve else "Denied"

        embed.title = f"Suggestion {approved} (#{suggestion_id})"
        footer = [f"{approved} by {author.name}#{author.discriminator} ({author.id}",
                  author.avatar_url_as(format="png", size=512)]
        embed.set_footer(
            text=footer[0],
            icon_url=footer[1]
        )
        embed.add_field(
            name="Results", value=await self._get_results(ctx, old_msg), inline=False
        )
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
            await self.config.custom("SUGGESTION", server, suggestion_id).reason.set(
                True
            )
            await self.config.custom("SUGGESTION", server, suggestion_id).rtext.set(
                reason
            )

        if channel:
            if not await self.config.guild(ctx.guild).same():
                if await self.config.guild(ctx.guild).delete_suggestion():
                    await old_msg.delete()
                nmsg = await channel.send(content=content, embed=embed)
                await self.config.custom(
                    "SUGGESTION", server, suggestion_id
                ).msg_id.set(nmsg.id)
            else:
                await old_msg.edit(content=content, embed=embed)
        else:
            if not await self.config.guild(ctx.guild).same():
                if await self.config.guild(ctx.guild).delete_suggestion():
                    await old_msg.delete()
                await self.config.custom(
                    "SUGGESTION", server, suggestion_id
                ).msg_id.set(1)
            else:
                await old_msg.edit(content=content, embed=embed)
        await self.config.custom("SUGGESTION", server, suggestion_id).finished.set(True)
        if approve:
            await self.config.custom("SUGGESTION", server, suggestion_id).approved.set(
                True
            )
        else:
            await self.config.custom("SUGGESTION", server, suggestion_id).denied.set(
                True
            )
        await ctx.tick()