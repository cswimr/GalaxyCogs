# GalaxyCogs

<p align="center">
  <a href="https://discord.com/invite/robloxgalaxy">
    <img src="https://discordapp.com/api/guilds/204965774618656769/widget.png?style=shield" alt="Galaxy Discord Server">
  </a>
  <a href="https://www.python.org/downloads/">
    <img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/Red-Discordbot">
  </a>
  <a href="https://github.com/Rapptz/discord.py/">
     <img src="https://img.shields.io/badge/discord-py-blue.svg" alt="discord.py">
  </a>
</p>
Repository for Redbot cogs developed by the Galaxy Discord Management team.

## ExportChannels **(WIP)**[^incomplete]

This cog allows you to easily export channels using Discord Chat Exporter.

**THIS COG IS NOT INTENDED FOR EXTERNAL USE. YOU WILL LIKELY HAVE TO RUN THIS COG LOCALLY AND MODIFY CODE SHOULD YOU WISH TO USE IT.**

### **Credit to Tyrrrz for the bundled version of Discord Chat Exporter within this cog. The original repository can be found [here](https://github.com/Tyrrrz/DiscordChatExporter).**

## Galaxy

Utility cog designed specifically for use on the Galaxy Discord server.

Includes:

* Warehouse command
* FAQ command
* Unix command

## Info

Combination of a few built-in Red cogs + some custom code to provide commands that show information of specific Discord objects.

Currently supports:

* Users
* Servers/Guilds
* Roles[^dpy_notice]
[^dpy_notice]:
    Due to Red's use of Discord.py 1.7.3, the ``[p]roleinfo`` command in the Info cog does not show all permissions. This is due to the outdated Discord.py version not supporting checking for all permissions.

## MusicDownloader

Allows users to download **just the audio files** from any YouTube video. Currently only supports YouTube and does not work for video.

## Podcast **(WIP)**[^incomplete]

Allows users to submit questions to a specified channel, intended for use with podcasts.

Also features user blacklists, both configurable per-server and globally.
[^incomplete]:
  This cog currently is non-functional. This notice will be removed once the Cog is completed.

## Shortmutes **(WIP)**[^incomplete]

Allows staff members to shortmute individuals for up to 30 minutes, using Discord's Timeouts feature.

## Suggestions

Allows users to submit suggestions to a specified channel. Highly cut-down modification of [SauriCog's Suggestions Cog](https://github.com/elijabesu/SauriCogs).

Features:

* Separate approved and denied channels
* Custom emoji support

## SugonCredit

Implements a way for moderators to give out social-credit like points, dubbed 'sugoncredits' by the community.

Features:

* Add Credit to people.
* Remove Credit from people.
* Supports custom currency names and bank names.
