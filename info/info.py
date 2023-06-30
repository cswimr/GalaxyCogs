from datetime import datetime
import discord
from redbot.core import commands, checks, Config
from redbot.core.bot import Red
from redbot.core.i18n import Translator, cog_i18n
import re
from redbot.core.utils.chat_formatting import (
    bold,
    humanize_number,
    humanize_timedelta,
)
from redbot.core.utils.common_filters import (
    filter_invites,
    escape_spoilers_and_mass_mentions
)


_ = T_ = Translator("General", __file__)

@cog_i18n(_)
class Info(commands.Cog):
    """Provides information on Discord objects."""

    default_member_settings = {"past_nicks": [], "perms_cache": {}}

    default_user_settings = {"past_names": []}

    def __init__(self, bot: Red):
        super().__init__()
        self.bot = bot

        self.config = Config.get_conf(self, 2657117654, force_registration=True)
        self.config.register_member(**self.default_member_settings)
        self.config.register_user(**self.default_user_settings)
        self.cache: dict = {}

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
                data.set_author(name=guild.name, icon_url=str(guild.icon_url_as(format='png')))
                data.set_thumbnail(url=str(guild.icon_url_as(format='png')))
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
            if "VERIFIED" in guild.features:
                data.set_author(
                    name=guild.name,
                    icon_url="https://cdn.discordapp.com/emojis/457879292152381443.png"
                )
            elif "PARTNERNED" in guild.features:
                data.set_author(
                    name=guild.name,
                    icon_url="https://cdn.discordapp.com/emojis/508929941610430464.png"
                )
            else:
                data.set_author(
                    name=guild.name
                )
            if guild.icon:
                data.set_thumbnail(url=str(guild.icon_url))
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
                data.set_image(url=str(guild.splash_url_as(format='png')))
            data.set_footer(text=joined_on)

        await ctx.send(embed=data)

    def handle_custom(self, user):
        a = [c for c in user.activities if c.type == discord.ActivityType.custom]
        if not a:
            return None, discord.ActivityType.custom
        a = a[0]
        c_status = None
        if not a.name and not a.emoji:
            return None, discord.ActivityType.custom
        elif a.name and a.emoji:
            c_status = _("Custom: {emoji} {name}").format(emoji=a.emoji, name=a.name)
        elif a.emoji:
            c_status = _("Custom: {emoji}").format(emoji=a.emoji)
        elif a.name:
            c_status = _("Custom: {name}").format(name=a.name)
        return c_status, discord.ActivityType.custom

    def handle_playing(self, user):
        p_acts = [c for c in user.activities if c.type == discord.ActivityType.playing]
        if not p_acts:
            return None, discord.ActivityType.playing
        p_act = p_acts[0]
        act = _("Playing: {name}").format(name=p_act.name)
        return act, discord.ActivityType.playing

    def handle_streaming(self, user):
        s_acts = [c for c in user.activities if c.type == discord.ActivityType.streaming]
        if not s_acts:
            return None, discord.ActivityType.streaming
        s_act = s_acts[0]
        if isinstance(s_act, discord.Streaming):
            act = _("Streaming: [{name}{sep}{game}]({url})").format(
                name=discord.utils.escape_markdown(s_act.name),
                sep=" | " if s_act.game else "",
                game=discord.utils.escape_markdown(s_act.game) if s_act.game else "",
                url=s_act.url,
            )
        else:
            act = _("Streaming: {name}").format(name=s_act.name)
        return act, discord.ActivityType.streaming

    def handle_listening(self, user):
        l_acts = [c for c in user.activities if c.type == discord.ActivityType.listening]
        if not l_acts:
            return None, discord.ActivityType.listening
        l_act = l_acts[0]
        if isinstance(l_act, discord.Spotify):
            act = _("Listening: [{title}{sep}{artist}]({url})").format(
                title=discord.utils.escape_markdown(l_act.title),
                sep=" | " if l_act.artist else "",
                artist=discord.utils.escape_markdown(l_act.artist) if l_act.artist else "",
                url=f"https://open.spotify.com/track/{l_act.track_id}",
            )
        else:
            act = _("Listening: {title}").format(title=l_act.name)
        return act, discord.ActivityType.listening

    def handle_watching(self, user):
        w_acts = [c for c in user.activities if c.type == discord.ActivityType.watching]
        if not w_acts:
            return None, discord.ActivityType.watching
        w_act = w_acts[0]
        act = _("Watching: {name}").format(name=w_act.name)
        return act, discord.ActivityType.watching

    def handle_competing(self, user):
        w_acts = [c for c in user.activities if c.type == discord.ActivityType.competing]
        if not w_acts:
            return None, discord.ActivityType.competing
        w_act = w_acts[0]
        act = _("Competing in: {competing}").format(competing=w_act.name)
        return act, discord.ActivityType.competing

    def get_status_string(self, user):
        string = ""
        for a in [
            self.handle_custom(user),
            self.handle_playing(user),
            self.handle_listening(user),
            self.handle_streaming(user),
            self.handle_watching(user),
            self.handle_competing(user),
        ]:
            status_string, status_type = a
            if status_string is None:
                continue
            string += f"{status_string}\n"
        return string

    async def get_names_and_nicks(self, user):
        names = await self.config.user(user).past_names()
        nicks = await self.config.member(user).past_nicks()
        if names:
            names = [escape_spoilers_and_mass_mentions(name) for name in names if name]
        if nicks:
            nicks = [escape_spoilers_and_mass_mentions(nick) for nick in nicks if nick]
        return names, nicks

    @commands.command()
    @commands.guild_only()
    @commands.bot_has_permissions(embed_links=True)
    async def userinfo(self, ctx, *, member: discord.Member = None):
        """Show information about a member.
        This includes fields for status, discord join date, server
        join date, voice state and previous names/nicknames.
        If the member has no roles, previous names or previous nicknames,
        these fields will be omitted.
        """
        author = ctx.author
        guild = ctx.guild

        if not member:
            member = author

        roles = member.roles[-1:0:-1]
        names, nicks = await self.get_names_and_nicks(member)

        joined_at = member.joined_at
        voice_state = member.voice
        member_number = (
            sorted(guild.members, key=lambda m: m.joined_at or ctx.message.created_at).index(
                member
            )
            + 1
        )

        created_on = (
            f"<t:{int(datetime.timestamp(member.created_at))}>\n"
            f"<t:{int(datetime.timestamp(member.created_at))}:R>"
        )
        if joined_at is not None:
            joined_on = (
                f"<t:{int(datetime.timestamp(joined_at))}>\n"
                f"<t:{int(datetime.timestamp(joined_at))}:R>"
            )
        else:
            joined_on = _("Unknown")

        if any(a.type is discord.ActivityType.streaming for a in member.activities):
            statusemoji = "\N{LARGE PURPLE CIRCLE}"
        elif member.status.name == "online":
            statusemoji = "\N{LARGE GREEN CIRCLE}"
        elif member.status.name == "offline":
            statusemoji = "\N{MEDIUM WHITE CIRCLE}\N{VARIATION SELECTOR-16}"
        elif member.status.name == "dnd":
            statusemoji = "\N{LARGE RED CIRCLE}"
        elif member.status.name == "idle":
            statusemoji = "\N{LARGE ORANGE CIRCLE}"
        activity = _("Chilling in {} status").format(member.status)
        status_string = self.get_status_string(member)

        if roles:
            role_str = ", ".join([x.mention for x in roles])
            # 400 BAD REQUEST (error code: 50035): Invalid Form Body
            # In embed.fields.2.value: Must be 1024 or fewer in length.
            if len(role_str) > 1024:
                # Alternative string building time.
                # This is not the most optimal, but if you're hitting this, you are losing more time
                # to every single check running on users than the occasional user info invoke
                # We don't start by building this way, since the number of times we hit this should be
                # infinitesimally small compared to when we don't across all uses of Red.
                continuation_string = _(
                    "and {numeric_number} more roles not displayed due to embed limits."
                )
                available_length = 1024 - len(continuation_string)  # do not attempt to tweak, i18n

                role_chunks = []
                remaining_roles = 0

                for r in roles:
                    chunk = f"{r.mention}, "
                    chunk_size = len(chunk)

                    if chunk_size < available_length:
                        available_length -= chunk_size
                        role_chunks.append(chunk)
                    else:
                        remaining_roles += 1

                role_chunks.append(continuation_string.format(numeric_number=remaining_roles))

                role_str = "".join(role_chunks)

        else:
            role_str = None

        data = discord.Embed(description=status_string or activity, colour=member.colour)

        data.add_field(name=_("Joined Discord on"), value=created_on)
        data.add_field(name=_("Joined this server on"), value=joined_on)
        if role_str is not None:
            data.add_field(
                name=_("Roles") if len(roles) > 1 else _("Role"), value=role_str, inline=False
            )
        if names:
            # May need sanitizing later, but mentions do not ping in embeds currently
            val = filter_invites(", ".join(names))
            data.add_field(
                name=_("Previous Names") if len(names) > 1 else _("Previous Name"),
                value=val,
                inline=False,
            )
        if nicks:
            # May need sanitizing later, but mentions do not ping in embeds currently
            val = filter_invites(", ".join(nicks))
            data.add_field(
                name=_("Previous Nicknames") if len(nicks) > 1 else _("Previous Nickname"),
                value=val,
                inline=False,
            )
        if voice_state and voice_state.channel:
            data.add_field(
                name=_("Current voice channel"),
                value="{0.mention} ID: {0.id}".format(voice_state.channel),
                inline=False,
            )
        data.set_footer(text=_("Member #{} | User ID: {}").format(member_number, member.id))

        if member.discriminator == "0":
            name = str(member.name)
        else:
            name = str(member)
        name = " - ".join((name, member.nick)) if member.nick else name
        name = filter_invites(name)

        avatar = member.avatar_url_as(format='png')
        data.set_author(name=f"{statusemoji} {name}", url=avatar)
        data.set_thumbnail(url=avatar)

        await ctx.send(embed=data)

    @commands.command()
    @commands.guild_only()
    async def roleinfo(self, ctx, role: discord.Role, list_permissions: bool = False):
        """Gives information on a specific role.
        `list_permissions` is ignored if the role you're checking has the `Administrator` permission."""
        permissions = role.permissions
        if role.color.value == 0:
            colorint = 10070709
            color = "99aab5"
        else:
            colorint = role.color.value
            color = re.sub('#',"",str(role.color))
        colorcodelink = f"https://www.color-hex.com/color/{color}"
        timestamp = int(datetime.timestamp(role.created_at))
        embed = discord.Embed(title=f"{role.name}", color=colorint, description=f"**ID:** {role.id}\n**Mention:** {role.mention}\n**Creation Date:** <t:{timestamp}>\n**Color:** [#{color}]({colorcodelink})\n**Hoisted:** {role.hoist}\n**Position:** {role.position}\n**Managed:** {role.managed}\n**Mentionable:** {role.mentionable}\n**Administrator:** {permissions.administrator}")
        if permissions.administrator == False and list_permissions == True:
            embed.add_field(name="Permissions", value=f"**Manage Server:** {permissions.manage_guild}\n**Manage Webhooks:** {permissions.manage_webhooks}\n**Manage Channels:** {permissions.manage_channels}\n**Manage Roles:** {permissions.manage_roles}\n**Manage Emojis:** {permissions.manage_emojis}\n**Manage Messages:** {permissions.manage_messages}\n**Manage Nicknames:** {permissions.manage_nicknames}\n**Mention @everyone**: {permissions.mention_everyone}\n**Ban Members:** {permissions.ban_members}\n**Kick Members:** {permissions.kick_members}")
        await ctx.send(embed=embed)
