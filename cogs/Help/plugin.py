from __future__ import annotations

import discord
import datetime
import discord
from .. import Plugin
from typing import Optional
from discord import Member, User, Message
from discord.ext import commands
from core import Bot, Embed, AfkModel
from discord import Interaction, app_commands
from discord.ui import View, Select
from config import VERSION
from typing import Optional
from discord.ext import commands, tasks
from logging import getLogger
from tortoise import Tortoise
from cogs import *


class Help(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name='help',
        description="Help for Caine!"
    )
    async def help_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())

        embed.set_author(name="Caine's Help Command", url=self.bot.user.avatar)

        embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(name="Basic", value="/basic")
        embed.add_field(name="Utility", value="/utility")
        embed.add_field(name="Moderation", value="/admin", inline=False)
        embed.add_field(name="AutoMod", value="/automod", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="basic",
        description="Gives all available commands for Everyone"
    )
    async def basic_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())

        embed.set_author(name="Basic Commands", url=self.bot.user.avatar)

        embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(name="bug",
                        value="Report a bug you have found within Caine!")

        embed.add_field(name="feature",
                        value="Request a feature you would like to see in Caine!")

        embed.add_field(name="membercount",
                        value="Shows the amount of members in the server!")

        embed.add_field(name="afk <reason>",
                        value="Set yourself AFK with a reason!")

        embed.add_field(name="embed <message>",
                        value="Create a custom embed message!")

        embed.add_field(name="msg-formatting",
                        value="Shows Discord's message formatting!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="utility",
        description="Gives all available commands for Utility"
    )
    async def utility_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())

        embed.set_author(name="Utility Commands", url=self.bot.user.avatar)

        embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(name="caine-info",
                        value="Information about Caine!")

        embed.add_field(name="caine-uptime",
                        value="Shows Caine's uptime!")

        embed.add_field(name="invite",
                        value="Invite Caine to your server!")

        embed.add_field(name="ping",
                        value="Shows Caine's latency")

        embed.add_field(name="channelhealth <channel>",
                        value="Check the health of a specific channel!")

        embed.add_field(name="server-stats",
                        value="Shows all information and stats about the server!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="automod",
        description="Gives all available commands for Admins - AutoMod"
    )
    async def automod_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())

        embed.set_author(name="AutoMod Commands", url=self.bot.user.avatar)

        embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(name="set-twitch <channel>",
                        value="Sets server twitch channel to specific channel")

        embed.add_field(name="set-log <channel>",
                        value="Sets server log channel to specific channel")

        embed.add_field(name="set-welcomechannel <channel>",
                        value="Sets server welcome channel to specific channel")

        embed.add_field(name="set-welcomemsg <message>",
                        value="Sets server welcome message")

        embed.add_field(name="Note",
                        value="All AutoMod commands are still being developed and updated. Expect updates to these commands weekly!")

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name="admin",
        description="Gives all available commands for Admins"
    )
    async def moderation_help(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())

        embed.set_author(name="Moderation Commands", url=self.bot.user.avatar)

        embed.set_thumbnail(url=interaction.user.avatar.url)

        embed.add_field(name="kick <user> <reason>",
                        value="Kicks a specfic user from the server with optional reason")

        embed.add_field(name="ban <user> <reason>",
                        value="Bans a specific user from the server with optional reason")

        embed.add_field(name="unban <user> <reason>",
                        value="Unbans a specific user from the server with optional reason")

        embed.add_field(name="mute <user> <duration> <reason>",
                        value="Mutes a specific user in both voice and text channels with optional reason")

        embed.add_field(name="unmute <user> <reason>",
                        value="Unmutes a specific user from both voice and text channels")

        embed.add_field(name="purge <amount> <user> <content>",
                        value="Purges messages in channel by specific user or content")

        embed.add_field(name="lockdown <channel>",
                        value="Locks down a text channel with alert")

        embed.add_field(name="lock <channel>",
                        value="Quietly locks a given text channel")

        embed.add_field(name="unlock <channel> <reset>",
                        value="Quietly unlocks a given text channel with an option to reset perms")

        embed.add_field(name="role create <name> <hoist> <mentionable> <color> <display_icon>",
                        value="Creates a role for the server!")

        embed.add_field(name="role delete <role> <reason>",
                        value="Deletes a specific role from the server with optional reason")

        embed.add_field(name="role give <user> <role>",
                        value="Gives a specific role to a user")

        embed.add_field(name="role remove <user> <role>",
                        value="Removes a specific role from a user")

        embed.add_field(name="dm <user> <message>",
                        value="Direct Messages a specific user as Caine [ DO NOT attempt to troll Caine shows who sent the DM ]")

        embed.add_field(name="cainename <name>",
                        value="Changes Caine's server nickname")

        embed.add_field(name="nickname <user> <name> <reason>",
                        value="Changes a users server nickname with optional reason")

        embed.add_field(name="checkmsg <user> <channel>",
                        value="Checks how many messages a user has sent in a channel")

        embed.add_field(name="invites <user>",
                        value="Lets you see how many server invites a user has sent")

        embed.add_field(name="whois <user>",
                        value="Shows all public user information.")
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Help(bot))
