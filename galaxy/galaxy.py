from redbot.core import commands, checks, Config
import discord
from datetime import datetime
import re
import subprocess

class Galaxy(commands.Cog):
    """Custom cog intended for use on the Galaxy discord server.
    Developed by SeaswimmerTheFsh."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=6621962)
        self.config.register_guild(
            cocotarget = 0,
            cocoemoji = 1028535684757209118
        )

    @commands.command(aliases=["pxc", "pc", "polarisconvert", "tatsutopolaris", "ttp"])
    @commands.guild_only()
    async def polarisxpconvert(self, ctx, *, tatsu_studs: str):
        """Converts Tatsu Studs to Polaris XP."""
        try:
            tatsu_studs_int = int(f"{tatsu_studs}".replace(",", ""))
        except ValueError:
            await ctx.send(content="Please input a number!")
            return
        math  = round((tatsu_studs_int/25)*10)
        output_from = f'{tatsu_studs_int:,}'
        output_to = f'{math:,}'
        embed = discord.Embed(color=await self.bot.get_embed_color(None))
        embed.add_field(name="Tatsu Studs", value=f"{output_from}", inline=False)
        embed.add_field(name="Polaris XP", value=f"{output_to}", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    @checks.is_owner()
    async def nslookup(self, ctx: commands.Context, *, website: str):
        """This command uses `nslookup` to check the IP Address of any given website."""
        try:
            result = subprocess.run(['nslookup', website], capture_output=True, text=True, check=True)
            await ctx.send(f"```\n{result.stdout}\n```")
        except subprocess.CalledProcessError as e:
            await ctx.send(f"Error executing `nslookup`: `{e}`")
        except FileNotFoundError:
            await ctx.send("`nslookup` command not found. Make sure you have `nslookup` installed and it's in your system PATH.")


    @commands.command()
    async def galaxyissues(self, ctx, target: discord.Member = None):
        if ctx.me.id == 1070819799254438039:
            embed = discord.Embed(title="Issue Reporting & Suggestions", color=await self.bot.get_embed_color(None), description="Have a problem or a suggestion for the Galaxy bot or GalaxyCogs? Read this!")
            embed.add_field(name="Bot Issues & Suggestions", value="If you'd like to submit a suggestion or a bug report to the developers of the Galaxy bot, please do so [here](https://github.com/SeaswimmerTheFsh/GalaxyCogs/issues/new/choose).\n**Please make sure whatever you're suggesting or reporting doesn't have an existing issue! If it does, you can comment on that issue with additional details if necessary.**")
        else:
            embed = discord.Embed(title="Issue Reporting & Suggestions", color=await self.bot.get_embed_color(None), description="Have a problem or a suggestion for GalaxyCogs? Read this!")
        embed.add_field(name="Cog Issues & Suggestions", value="If you'd like to submit a suggestion or a bug report to the developers of GalaxyCogs, please do so [here](https://github.com/SeaswimmerTheFsh/GalaxyCogs/issues/new/choose).\n**Please make sure whatever you're suggesting or reporting doesn't have an existing issue! If it does, you can comment on that issue with additional details if necessary.**")
        if target:
            await ctx.send(embed=embed, content=f"{target.mention}")
        else:
            await ctx.send(embed=embed)

    @commands.command()
    async def carnagerefund(self, ctx, message_id: str):
        """This command generates a link to refund carnage of killed ships."""
        output = f"https://info.galaxy.casa/kills/{message_id}"
        await ctx.send(f"Output link: {output}")

    @commands.Cog.listener('on_message')
    async def cocoreact(self, message):
        emoji = self.bot.get_emoji(await self.config.guild(message.guild).cocoemoji())
        cocotarget = await self.config.guild(message.guild).cocotarget()
        if cocotarget == 0:
            return
        if not message.author.id == cocotarget:
            return
        await message.add_reaction(emoji)

    @commands.group(autohelp=False, invoke_without_command=True)
    @commands.guild_only()
    async def coco(self, ctx):
        """Checks who Coco is currently set to."""
        emoji = self.bot.get_emoji(await self.config.guild(ctx.guild).cocoemoji())
        cocotarget = await self.config.guild(ctx.guild).cocotarget()
        embed = discord.Embed(color=await self.bot.get_embed_color(None), description=f"Coco is currently set to <@{cocotarget}> ({cocotarget}).\nCoco's emoji is currently set to {emoji} ({await self.config.guild(ctx.guild).cocoemoji()}).")
        await ctx.send(embed=embed)

    @coco.command(name="emoji")
    async def coco_emoji(self, ctx, emoji: discord.Emoji = None):
        """Sets Coco's emoji."""
        if emoji:
            await self.config.guild(ctx.guild).cocoemoji.set(emoji.id)
            embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"Coco's emoji has been set to {emoji} ({emoji.id}).")
            await ctx.send(embed=embed)
        else:
            await self.config.guild(ctx.guild).cocoemoji.set(1028535684757209118)
            emoji = self.bot.get_emoji(1028535684757209118)
            embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"Coco's emoji has been set to {emoji} (1028535684757209118).")
            await ctx.send(embed=embed)

    @coco.command(name="set")
    async def coco_set(self, ctx, member: discord.Member):
        """Sets Coco's target."""
        if member:
            await self.config.guild(ctx.guild).cocotarget.set(member.id)
            embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"Coco has been set to {member.mention} ({member.id}).")
            await ctx.send(embed=embed)
        else:
            await ctx.send(content="That is not a valid argument!")

    @coco.command(name="reset")
    async def coco_reset(self, ctx):
        """Resets Coco's target."""
        await self.config.guild(ctx.guild).cocotarget.set(0)
        embed=discord.Embed(color=await self.bot.get_embed_color(None), description=f"Coco has been reset.")
        await ctx.send(embed=embed)

    @commands.command()
    async def unix(self, ctx):
        """Posts the current Unix timestamp."""
        timestamp = int(datetime.timestamp(datetime.now()))
        embed=discord.Embed(title="Current Time", url="https://www.unixtimestamp.com/", color=await self.bot.get_embed_color(None), description=f"<t:{timestamp}>")
        embed.set_footer(text=f"{timestamp}")
        embed.set_image(url="https://cdn.discordapp.com/attachments/1047347377348030494/1080048421127335956/image.png")
        await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.group(autohelp=True)
    async def insurance(self, ctx: commands.Context):
        """Calculates insurance.
        Please only use the value of a ship (from ``/shipinfo``) to calculate insurance and **not** ship cost. Decimals do not work properly with this command, just remove them."""

    async def _insurance(self, ship_class: str, value: str):
        """This function does the actual math and configures the embed.

        Attributes
        -----------
        ship_class: Required[:class:`str`]
            The class of the ship whose insurance you're checking.

        value: Required[:class:`int`]
            The value of the ship you're checking. This should be supplied by `/shipinfo`. Not the same as ship cost!"""
        cleaned_value = int(''.join(char for char in value if char.isdigit()))
        insurance_dict = {
            "miner": 0.7,
            "freighter": 0.65,
            "frigate": 0.6,
            "destroyer": 0.55,
            "cruiser": 0.5,
            "battlecruiser": 0.4,
            "battleship": 0.35,
            "dreadnought": 0.3,
            "carrier": 0.3,
            "super_capital": 0.25
        }
        try:
            insurance_dict[f'{ship_class}']
        except KeyError:
            raise ValueError("Received value is not a valid ship class!")
        if ship_class == "super_capital":
            humanized_class = ship_class.replace("_", " ").title()
        else:
            humanized_class = ship_class.capitalize()
        insurance_amount = (f"{round(cleaned_value * insurance_dict[f'{ship_class}']):,}")
        value_output = (f'{cleaned_value:,}')
        embed = discord.Embed(title="Insurance Payout", color=await self.bot.get_embed_color(None))
        embed.add_field(name="Ship Class", value=f"{humanized_class}", inline=False)
        embed.add_field(name="Ship Value", value=f"{value_output}", inline=False)
        embed.add_field(name="Insurance Amount", value=f"{insurance_amount}", inline=False)
        return embed

    @insurance.command()
    async def miner(self, ctx: commands.Context, value):
        """Calculates insurance for miners. (70%)"""
        await ctx.send(embed=await self._insurance('miner', value))

    @insurance.command()
    async def freighter(self, ctx: commands.Context, value):
        """Calculates insurance for freighters. (65%)"""
        await ctx.send(embed=await self._insurance('freighter', value))

    @insurance.command()
    async def frigate(self, ctx: commands.Context, value):
        """Calculates insurance for frigates. (60%)"""
        await ctx.send(embed=await self._insurance('frigate', value))

    @insurance.command()
    async def destroyer(self, ctx: commands.Context, value):
        """Calculates insurance for destroyers. (55%)"""
        await ctx.send(embed=await self._insurance('destroyer', value))

    @insurance.command()
    async def cruiser(self, ctx: commands.Context, value):
        """Calculates insurance for cruisers. (50%)"""
        await ctx.send(embed=await self._insurance('cruiser', value))

    @insurance.command()
    async def battlecruiser(self, ctx: commands.Context, value):
        """Calculates insurance for battlecruisers. (40%)"""
        await ctx.send(embed=await self._insurance('battlecruiser', value))

    @insurance.command()
    async def battleship(self, ctx: commands.Context, value):
        """Calculates insurance for battleships. (35%)"""
        await ctx.send(embed=await self._insurance('battleship', value))

    @insurance.command()
    async def dreadnought(self, ctx: commands.Context, value):
        """Calculates insurance for dreadnoughts. (30%)"""
        await ctx.send(embed=await self._insurance('dreadnought', value))

    @insurance.command()
    async def carrier(self, ctx: commands.Context, value):
        """Calculates insurance for carriers. (30%)"""
        await ctx.send(embed=await self._insurance('carrier', value))

    @insurance.command()
    async def supercapital(self, ctx: commands.Context, value):
        """Calculates insurance for super capitals. (25%)"""
        await ctx.send(embed=await self._insurance('super_capital', value))

    @commands.command(aliases=["wh"])
    async def warehouse(self, ctx:  commands.Context,  lvlfrom: int = 1, lvlto: int = 38):
        """Calculates the total cost to upgrade your warehouse from a level to a level."""
        warehouse_levels = {1:0, 2:1000,3:2500,4:4500,5:7500,6:12500,7:20000,8:31500,9:46500,10:65500,11:87500,12:113500,13:143500,14:178500,15:218500,16:263500,17:313500,18:373500,19:443500,20:523500,21:613500,22:713500,23:823500,24:943500,25:1073500,26:1223500,27:1398500,28:1598500,29:1823500,30:2073500,31:2353500, 32:2663500, 33:3003500, 34:3373500, 35:3773500, 36:4193500, 37:4644500, 38:5093500}
        total_from = (f'{warehouse_levels[lvlfrom]:,}')
        total_to = (f'{warehouse_levels[lvlto]:,}')
        output = warehouse_levels[lvlto] - warehouse_levels[lvlfrom]
        total = (f'{output:,}')
        embed = discord.Embed(title="Warehouse Cost", color=await self.bot.get_embed_color(None))
        embed.add_field(name="From:", value=f"Warehouse Level: {lvlfrom}\nTotal Cost: {total_from} Credits", inline=False)
        embed.add_field(name="To:", value=f"Warehouse Level: {lvlto}\nTotal Cost: {total_to} Credits", inline=False)
        embed.add_field(name="Output:", value=f"{total} Credits", inline=False)
        if lvlfrom == lvlto:
            await ctx.send(contents="``lvlfrom`` cannot be the same as ``lvlto``.")
        elif lvlfrom > lvlto:
            await ctx.send(contents="``lvlfrom`` cannot be a higher value than ``to``.")
        elif lvlfrom < 1 or lvlfrom > 37:
            await ctx.send(contents="``lvlfrom`` must be higher than 0 and lower than 38")
        elif lvlto < 1 or lvlto > 38:
            await ctx.send(contents="``lvlto`` must be higher than 1 and lower than 39")
        else:
            await ctx.send(embed=embed)
        await ctx.message.delete()

    @commands.group(autohelp=True)
    async def faq(self, ctx):
        """Posts answers to frequently asked questions."""

    @faq.command(name="test")
    @checks.admin()
    async def faq_test(self, ctx, member: discord.Member = None):
        """Testing FAQ"""
        embed=discord.Embed(title="Test Embed", color=await self.bot.get_embed_color(None), description="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer in faucibus odio, at mollis metus.")
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar_url_as(format="png", size=512))
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="dps")
    async def faq_dps(self, ctx, member: discord.Member = None):
        """DPS Calculations/Inaccuracy"""
        embed=discord.Embed(title="DPS Calculations", color=await self.bot.get_embed_color(None), description="The ``/info`` command (and by extention ``/shipinfo`` from Odin) misreports DPS, due to it calculating DPS disregarding the turret's type (kinetic, laser), causing it to assume the target ship is both hulled and has shield simultaneously. It also ignores turret overrides, custom reloads, and custom damage values. If you'd like to check ship stats accurately, you can either use the ``/ship`` command in this channel or you can use the [Galaxy Info Website](https://info.galaxy.casa/ships). Alternatively, to check turret stats, you can use the [Galaxy Info Turrets Page](https://info.galaxy.casa/turrets).")
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="links")
    async def faq_links(self, ctx, member: discord.Member = None):
        """Posts important links, primarily invite links."""
        embed=discord.Embed(title="Important Links", color=await self.bot.get_embed_color(None))
        embed.add_field(name="Galaxy", value="[Galaxy Discord](https://discord.com/invite/robloxgalaxy)\n[Galaxy Support](https://discord.com/invite/ShWshkhYhZ)")
        embed.add_field(name="Galaxypedia", value="[Galaxypedia Website](https://robloxgalaxy.wiki/wiki/Main_Page)\n[Galaxypedia Discord](https://discord.robloxgalaxy.wiki/)")
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="ropro")
    async def faq_ropro(self, ctx, member: discord.Member = None):
        """Posts a link to RoPro"""
        embed=discord.Embed(title="RoPro", url="https://ropro.io", color=await self.bot.get_embed_color(None), description="""[RoPro](https://ropro.io) is a browser extension that tracks ROBLOX playtime, enhances your profile, and provides other useful utilities. **Please keep in mind that RoPro only tracks playtime from AFTER you install the extension.**""")
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="polaris_ranks")
    async def faq_polaris_ranks(self, ctx, member: discord.Member = None):
        """Lists required levels for certain roles."""
        embed=discord.Embed(title="Polaris Ranks", color=await self.bot.get_embed_color(None))
        embed.add_field(name="Picture Perms", value="Level 7", inline=False)
        embed.add_field(name="Suggestions", value="Level 9", inline=False)
        embed.add_field(name="DJ", value="Level 11", inline=False)
        embed.add_field(name="Reaction Perms", value="Level 30", inline=False)
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="polaris_switch")
    @checks.admin()
    async def faq_polaris_switch(self, ctx, member: discord.Member = None):
        """Posts an embed on the switch to the Polaris bot."""
        embed=discord.Embed(title="Polaris FAQ", color=await self.bot.get_embed_color(None), description="As you probably know, we've decided to switch to the Polaris bot for leveling/xp, as opposed to Tatsu.\nThere are many reasons for this, which will be explained below.")
        embed.add_field(name="Problems with Tatsu", value="1: Tatsu does not provide nearly as much configuration potential as Polaris does. An example of this is Polaris' customizable Level Curve.\n\n2: Tatsu does not have channel/role modifiers.\n\n3: Tatsu does not have actual levels, instead it has unconfigurable \"Global XP\", which gives \"Global Levels\". You cannot do anything with Global XP aside from blacklisting channels where people can gain it, like a bot-commands channel or something like that.\n\n4: Tatsu's leaderboard sucks, and only shows the top 10 on the web version.\n\n5: Tatsu has no XP management commands.\n\n6: Tatsu has TONS of bloat/useless commands, making the bot harder to configure.", inline=False)
        embed.add_field(name="Polaris' Features", value="1: Polaris allows you to customize the level curve of your server, and provides presets to make the transition easier.\n\n2: Polaris has XP management commands.\n\n3: Polaris has way more configuration in terms of Reward Roles.\n\n4: Polaris allows you to customize the level-up message shown whenever people achieve the next level.\n\n5: Polaris has both role and channel modifiers.\n\n6: Polaris' leaderboard is excellent, showing the top 1,000 ranked users on the same webpage, and allowing you to see your own stats, progress towards your next reward role, and all 350 levels and your progress towards them.\n\n7: Polaris is **just** a leveling bot. You don't have to deal with any of the bloat of multi-purpose bots like Tatsu or MEE6, you only get what you actually need.", inline=False)
        embed.add_field(name="Conclusion",value="With all of that said, you're probably wondering why we're putting so much effort into transferring peoples' data to the new bot.\n\nWell, Tatsu has been going since 2020, and I don't particularly favor the idea of clearing everyone's XP, especially when people have built up reward roles from Tatsu already, like Picture Perms, Suggestions access, and DJ.\n\nWith all this in mind, I hope this isn't too much of an inconvenience for you all, as I tried to make the process as seamless as possible without having to update all 10,000 people in the server.", inline=False)
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="npc_intervals")
    async def faq_npc_intervals(self, ctx, member: discord.Member = None):
        """Posts an embed containing NPC spawn intervals."""
        embed=discord.Embed(title="NPC Spawn Intervals", color=await self.bot.get_embed_color(None), description="*Disclaimer: Spawn times may be different if EventID is active!*")
        embed.add_field(name="Every 6.7 Minutes", value="[Dragoon](https://robloxgalaxy.wiki/wiki/Dragoon) *(80% Chance)*")
        embed.add_field(name="Every 8.3 Minutes", value="[Swarmer](https://robloxgalaxy.wiki/wiki/Swarmer) *(33% Chance)*")
        embed.add_field(name="Every 10 Minutes", value="[Jormungand](https://robloxgalaxy.wiki/wiki/Jormungand) *(75% Chance)*")
        embed.add_field(name="Every 12.5 Minutes", value="[Bruiser](https://robloxgalaxy.wiki/wiki/Bruiser) *(50% Chance)*")
        embed.add_field(name="Every 16.7 Minutes", value="[Outrider](https://robloxgalaxy.wiki/wiki/Outrider) *(50% Chance)*")
        embed.add_field(name="Every 28.3 Minutes", value="[Punisher](https://robloxgalaxy.wiki/wiki/Punisher)")
        embed.add_field(name="Every 60 Minutes", value="[X-0](https://robloxgalaxy.wiki/wiki/X-0) *(45% Chance)*\n[Decimator](https://robloxgalaxy.wiki/wiki/Decimator)")
        embed.add_field(name="Every 70 Minutes", value="[Galleon](https://robloxgalaxy.wiki/wiki/Galleon)")
        embed.add_field(name="Every 120 Minutes", value="[Kodiak](https://robloxgalaxy.wiki/wiki/Kodiak)")
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.message.delete()

    @faq.command(name="linked_role")
    async def faq_linked_role(self, ctx, member: discord.Member = None):
        """Posts an embed containing FAQ about Linked Role."""
        color=await self.bot.get_embed_color(None)
        embed=discord.Embed(title="Linked Role", color=color, description="**Before reading this, please make sure your Discord client is updated! On Mobile, you can do this by going to your app store of choice and updating Discord manually. On the desktop app you can do this by clicking the green update button in the top right.**")
        embed_desktop=discord.Embed(title="Desktop / Web", color=color, description="**Step 1:** Open the Server Dropdown menu in the top-left by clicking on the server's name.\n\n**Step 2:** Click the \"*Linked Roles*\" button.\n\n**Step 3:** Click on \"*Linked*.\"\n\n**Step 4:** Click \"*Finish*.\" You're done!\n*Note: You should already be Verified on Bloxlink. If you are not, go to the verification channel to verify.*")
        embed_desktop.set_thumbnail(url="https://cdn.discordapp.com/attachments/1070838419212738621/1079927564421836930/image.png")
        embed_mobile=discord.Embed(title="Mobile", color=color, description="**Step 1:** Open the Server menu on the top of the channel list by tapping the server's name.\n\n**Step 2:** Scroll down and tap the \"*Linked Roles*\" button.\n\n**Step 3:** Tap on \"*Linked*.\"\n\n**Step 4:** Tap \"*Finish*.\" You're done!\n*Note: You should already be Verified on Bloxlink. If you are not, go to the verification channel to verify.*")
        embed_mobile.set_thumbnail(url="https://cdn.discordapp.com/attachments/1047347377348030494/1079930169562771576/Screenshot_20230227_195338_Discord.jpg")
        if member:
            await ctx.channel.send(embed=embed, content=member.mention)
        else:
            await ctx.channel.send(embed=embed)
        await ctx.channel.send(embed=embed_desktop)
        await ctx.channel.send(embed=embed_mobile)
        await ctx.message.delete()

    @warehouse.error
    @unix.error
    @faq_test.error
    @faq_linked_role.error
    @faq_npc_intervals.error
    @faq_links.error
    @faq_dps.error
    @faq_ropro.error
    @faq_polaris_ranks.error
    @faq_polaris_switch.error
    async def faq_handler(self, ctx, error):
        """Error Handler for Galaxy."""
        if isinstance(error, discord.NotFound):
            return
