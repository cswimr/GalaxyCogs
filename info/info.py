from datetime import datetime
import time
from enum import Enum
from random import randint, choice
from typing import Final
import urllib.parse
import aiohttp
import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n
from redbot.core.utils.menus import menu
import re
from redbot.core.utils.chat_formatting import (
    bold,
    escape,
    italics,
    humanize_number,
    humanize_timedelta,
)


_ = T_ = Translator("General", __file__)

@cog_i18n(_)
class Info(commands.Cog):
    """Provides information on Discord objects."""

    def __init__(self, bot: Red) -> None:
        super().__init__()
        self.bot = bot

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def serverinfo(self, ctx, details: bool = False):
        """
        Show server information.

        `details`: Shows more information when set to `True`.
        Default to False.
        """
        guild = ctx.guild
        timestamp = int(datetime.timestamp(guild.created_at))
        created_at = _("Created on {date_and_time}. That's {relative_time}!").format(
            date_and_time=f"<t:{timestamp}>",
            relative_time=f"<t:{timestamp}:R>",
        )
        online = humanize_number(
            len([m.status for m in guild.members if m.status != discord.Status.offline])
        )
        total_users = guild.member_count and humanize_number(guild.member_count)
        text_channels = humanize_number(len(guild.text_channels))
        voice_channels = humanize_number(len(guild.voice_channels))
        stage_channels = humanize_number(len(guild.stage_channels))
        if not details:
            data = discord.Embed(description=created_at, colour=await ctx.embed_colour())
            data.add_field(
                name=_("Users online"),
                value=f"{online}/{total_users}" if total_users else _("Not available"),
            )
            data.add_field(name=_("Text Channels"), value=text_channels)
            data.add_field(name=_("Voice Channels"), value=voice_channels)
            data.add_field(name=_("Roles"), value=humanize_number(len(guild.roles)))
            data.add_field(name=_("Owner"), value=str(guild.owner))
            data.set_footer(
                text=_("Server ID: ")
                + str(guild.id)
                + _("  •  Use {command} for more info on the server.").format(
                    command=f"{ctx.clean_prefix}serverinfo 1"
                )
            )
            if guild.icon:
                data.set_author(name=guild.name, url=guild.icon)
                data.set_thumbnail(url=guild.icon)
            else:
                data.set_author(name=guild.name)
        else:

            def _size(num: int):
                for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
                    if abs(num) < 1024.0:
                        return "{0:.1f}{1}".format(num, unit)
                    num /= 1024.0
                return "{0:.1f}{1}".format(num, "YB")

            def _bitsize(num: int):
                for unit in ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]:
                    if abs(num) < 1000.0:
                        return "{0:.1f}{1}".format(num, unit)
                    num /= 1000.0
                return "{0:.1f}{1}".format(num, "YB")

            shard_info = (
                _("\nShard ID: **{shard_id}/{shard_count}**").format(
                    shard_id=humanize_number(guild.shard_id + 1),
                    shard_count=humanize_number(ctx.bot.shard_count),
                )
                if ctx.bot.shard_count > 1
                else ""
            )
            # Logic from: https://github.com/TrustyJAID/Trusty-cogs/blob/master/serverstats/serverstats.py#L159
            online_stats = {
                _("Humans: "): lambda x: not x.bot,
                _(" • Bots: "): lambda x: x.bot,
                "\N{LARGE GREEN CIRCLE}": lambda x: x.status is discord.Status.online,
                "\N{LARGE ORANGE CIRCLE}": lambda x: x.status is discord.Status.idle,
                "\N{LARGE RED CIRCLE}": lambda x: x.status is discord.Status.do_not_disturb,
                "\N{MEDIUM WHITE CIRCLE}\N{VARIATION SELECTOR-16}": lambda x: (
                    x.status is discord.Status.offline
                ),
                "\N{LARGE PURPLE CIRCLE}": lambda x: any(
                    a.type is discord.ActivityType.streaming for a in x.activities
                ),
                "\N{MOBILE PHONE}": lambda x: x.is_on_mobile(),
            }
            member_msg = _("Users online: **{online}/{total_users}**\n").format(
                online=online, total_users=total_users
            )
            count = 1
            for emoji, value in online_stats.items():
                try:
                    num = len([m for m in guild.members if value(m)])
                except Exception as error:
                    print(error)
                    continue
                else:
                    member_msg += f"{emoji} {bold(humanize_number(num))} " + (
                        "\n" if count % 2 == 0 else ""
                    )
                count += 1

            verif = {
                "none": _("0 - None"),
                "low": _("1 - Low"),
                "medium": _("2 - Medium"),
                "high": _("3 - High"),
                "highest": _("4 - Highest"),
            }

            joined_on = _(
                "{bot_name} joined this server on {bot_join}. That's over {since_join} days ago!"
            ).format(
                bot_name=ctx.bot.user.name,
                bot_join=guild.me.joined_at.strftime("%d %b %Y %H:%M:%S"),
                since_join=humanize_number((ctx.message.created_at - guild.me.joined_at).days),
            )

            data = discord.Embed(
                description=(f"{guild.description}\n\n" if guild.description else "") + created_at,
                colour=await ctx.embed_colour(),
            )
            data.set_author(
                name=guild.name,
                icon_url="https://cdn.discordapp.com/emojis/457879292152381443.png"
                if "VERIFIED" in guild.features
                else "https://cdn.discordapp.com/emojis/508929941610430464.png"
                if "PARTNERED" in guild.features
                else None,
            )
            if guild.icon:
                data.set_thumbnail(url=guild.icon)
            data.add_field(name=_("Members:"), value=member_msg)
            data.add_field(
                name=_("Channels:"),
                value=_(
                    "\N{SPEECH BALLOON} Text: {text}\n"
                    "\N{SPEAKER WITH THREE SOUND WAVES} Voice: {voice}\n"
                    "\N{STUDIO MICROPHONE} Stage: {stage}"
                ).format(
                    text=bold(text_channels),
                    voice=bold(voice_channels),
                    stage=bold(stage_channels),
                ),
            )
            data.add_field(
                name=_("Utility:"),
                value=_(
                    "Owner: {owner}\nVerif. level: {verif}\nServer ID: {id}{shard_info}"
                ).format(
                    owner=bold(str(guild.owner)),
                    verif=bold(verif[str(guild.verification_level)]),
                    id=bold(str(guild.id)),
                    shard_info=shard_info,
                ),
                inline=False,
            )
            data.add_field(
                name=_("Misc:"),
                value=_(
                    "AFK channel: {afk_chan}\nAFK timeout: {afk_timeout}\nCustom emojis: {emoji_count}\nRoles: {role_count}"
                ).format(
                    afk_chan=bold(str(guild.afk_channel))
                    if guild.afk_channel
                    else bold(_("Not set")),
                    afk_timeout=bold(humanize_timedelta(seconds=guild.afk_timeout)),
                    emoji_count=bold(humanize_number(len(guild.emojis))),
                    role_count=bold(humanize_number(len(guild.roles))),
                ),
                inline=False,
            )

            excluded_features = {
                # available to everyone since forum channels private beta
                "THREE_DAY_THREAD_ARCHIVE",
                "SEVEN_DAY_THREAD_ARCHIVE",
                # rolled out to everyone already
                "NEW_THREAD_PERMISSIONS",
                "TEXT_IN_VOICE_ENABLED",
                "THREADS_ENABLED",
                # available to everyone sometime after forum channel release
                "PRIVATE_THREADS",
            }
            custom_feature_names = {
                "VANITY_URL": "Vanity URL",
                "VIP_REGIONS": "VIP regions",
            }
            features = sorted(guild.features)
            if "COMMUNITY" in features:
                features.remove("NEWS")
            feature_names = [
                custom_feature_names.get(feature, " ".join(feature.split("_")).capitalize())
                for feature in features
                if feature not in excluded_features
            ]
            if guild.features:
                data.add_field(
                    name=_("Server features:"),
                    value="\n".join(
                        f"\N{WHITE HEAVY CHECK MARK} {feature}" for feature in feature_names
                    ),
                )

            if guild.premium_tier != 0:
                nitro_boost = _(
                    "Tier {boostlevel} with {nitroboosters} boosts\n"
                    "File size limit: {filelimit}\n"
                    "Emoji limit: {emojis_limit}\n"
                    "VCs max bitrate: {bitrate}"
                ).format(
                    boostlevel=bold(str(guild.premium_tier)),
                    nitroboosters=bold(humanize_number(guild.premium_subscription_count)),
                    filelimit=bold(_size(guild.filesize_limit)),
                    emojis_limit=bold(str(guild.emoji_limit)),
                    bitrate=bold(_bitsize(guild.bitrate_limit)),
                )
                data.add_field(name=_("Nitro Boost:"), value=nitro_boost)
            if guild.splash:
                data.set_image(url=guild.splash.replace(format="png"))
            data.set_footer(text=joined_on)

        await ctx.send(embed=data)

    @commands.command()
    @commands.guild_only()
    async def userinfo(self, ctx, member: discord.Member):
        """Gives information on a specific person."""
        if member.color.value == 0:
            colorint = 10070709
        else:
            colorint = member.color.value
        avatarurl = str(member.avatar_url)
        timestamp_create = int(datetime.timestamp(member.created_at))
        timestamp_join = int(datetime.timestamp(member.joined_at))
        embed = discord.Embed(title=f"{member.name}#{member.discriminator}", color=colorint)
        embed.add_field(name="Joined At", value=f"<t:{timestamp_join}>")
        embed.add_field(name="Created At", value=f"<t:{timestamp_create}>")
        embed.add_field(name="Avatar", value=f"[Click Here]({avatarurl})")
        embed.add_field(name="Roles", value=f"{member.roles}")
        embed.set_thumbnail(url=f"{avatarurl}")
        embed.set_footer(text=f"ID: {member.id}")
        await ctx.send(embed=embed)

    @commands.command()
    @commands.guild_only()
    async def roleinfo(self, ctx, role: discord.Role):
        """Gives information on a specific role."""
        permissions = role.permissions
        if role.color.value == 0:
            colorint = 10070709
            color = "99aab5"
        else:
            colorint = role.color.value
            color = re.sub('#',"",str(role.color))
        colorcodelink = f"https://www.color-hex.com/color/{color}"
        timestamp = int(datetime.timestamp(role.created_at))
        if permissions.administrator:
            embed = discord.Embed(title=f"{role.name}", color=colorint, description=f"**ID:** {role.id}\n**Mention:** {role.mention}\n**Creation Date:** <t:{timestamp}>\n**Color:** [#{color}]({colorcodelink})\n**Hoisted:** {role.hoist}\n**Position:** {role.position}\n**Managed:** {role.managed}\n**Mentionable:** {role.mentionable}\n**Administrator:** {role.permissions.administrator}")
        else:
            embed = discord.Embed(title=f"{role.name}", color=colorint, description=f"**ID:** {role.id}\n**Mention:** {role.mention}\n**Creation Date:** <t:{timestamp}>\n**Color:** [#{color}]({colorcodelink})\n**Hoisted:** {role.hoist}\n**Position:** {role.position}\n**Managed:** {role.managed}\n**Mentionable:** {role.mentionable}\n**Administrator:** {role.permissions.administrator}")
            embed.add_field(name="Permissions", value=f"**Manage Server:** {permissions.manage_guild}\n**Manage Webhooks:** {permissions.manage_webhooks}\n**Manage Channels:** {permissions.manage_channels}\n**Manage Roles:** {permissions.manage_roles}\n**Manage Emojis:** {permissions.manage_emojis}\n**Manage Messages:** {permissions.manage_messages}\n**Manage Nicknames:** {permissions.manage_nicknames}\n**Mention @everyone**: {permissions.mention_everyone}\n**Ban Members:** {permissions.ban_members}\n**Kick Members:** {permissions.kick_members}")
        await ctx.send(embed=embed)