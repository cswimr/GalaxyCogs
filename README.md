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
## Galaxy
Utility cog designed specifically for use on the Galaxy Discord server. 

Includes:
* Warehouse command
* FAQ command
* Coco command (Autoreacting to a specific user)
* Unix command
## Info
Combination of a few built-in Red cogs + some custom code to provide commands that show information of specific Discord objects.
Currently supports:
* Users
* Servers/Guilds
* Roles[^dpy_notice]
[^dpy_notice]:
    Due to Red's use of Discord.py 1.7.3, the ``[p]roleinfo`` command in the Info cog does not show all permissions. This is due to the outdated Discord.py version not supporting checking for all permissions.