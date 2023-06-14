from __future__ import annotations

from typing import Optional, Callable, Any
from humanfriendly import parse_timespan, InvalidTimespan
from datetime import timedelta, datetime
from .. import Plugin
from core import Bot, Embed
from discord import (app_commands,
                     Interaction,
                     utils as Utils,
                     TextChannel,
                     Color
                     )
from discord.ext import commands
from discord.ui import View, Select
from pytz import UTC
import re
import sqlite3

Caine_ID = 1108032171060502580

dt_format = '%Y-%m-%d %H:%M:%S (UTC+0)'

DEGENERATE_CHANNELS = [
    327671109551915018,
    218148472262492161,
    218148510527127552,
    218169083600961547,
    218546616561434634
]


def clean_string(string):
    string = re.sub('@', '@\u200b', string)
    string = re.sub('#', '#\u200b', string)
    return string


class AutoMod(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.conn = sqlite3.connect('database.db')
        self.c = self.conn.cursor()
        self.website_regex = re.compile("https?:\/\/[^\s]*")
        self.c.execute('''CREATE TABLE IF NOT EXISTS servers
                         (id text, log_channel text, twitch_channel text,
                          welcome_message text, bot_channel text, prefix text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS logging
             (server text, message_edit boolean, message_deletion boolean,
             role_changes boolean, name_update boolean, member_movement boolean,
             avatar_changes boolean, bans boolean, ignored_channels text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS greetings
                       (guild_id text UNIQUE NOT NULL, greet_channel text, greet_message text, farewell_message text, ban_message text)
                        ''')

    @app_commands.command(
        name='set-twitch',
        description="Sets Twitch Channel"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def set_twitch(self, interaction: Interaction, *, channel: TextChannel = None):
        if channel is None:
            return await self.bot.error("You need to mention a channel!", interaction)
        self.c.execute('''UPDATE servers
                          SET twitch_channel=?
                          WHERE id=?''',
                       (channel.id, interaction.channel.id))
        self.conn.commit()
        await self.bot.success(f"Twitch channel successfully set to <#{channel.id}>".format(channel.id), interaction)

    @app_commands.command(
        name='set-log',
        description="Sets Log Channel"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def set_log(self, interaction: Interaction, *, channel: TextChannel = None):
        if channel is None:
            return await self.bot.error("You need to mention a channel!", interaction)
        self.c.execute('''UPDATE servers
                          SET log_channel=?
                          WHERE id=?''',
                       (channel.id, interaction.channel.id))
        self.conn.commit()
        await self.bot.success(f"Log channel successfully set to <#{channel.id}>".format(channel.id), interaction)

    @app_commands.command(
        name="set-welcomechannel",
        description="Set Welcome Channel"
    )
    @app_commands.describe(
        channel="Select a channel"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def welcomechannel_command(self, interaction: Interaction, *, channel: TextChannel = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (str(interaction.guild.id), None, None, None, None))
        self.conn.commit()
        if channel is None:
            self.c.execute('''UPDATE greetings
                              SET greet_channel=?
                              WHERE guild_id=?''',
                           (None, interaction.guild.id))
            self.conn.commit()
            return await self.bot.success("Welcome channel removed!", interaction)
        self.c.execute('''UPDATE greetings
                          SET greet_channel=?
                          WHERE guild_id=?''',
                       (channel.id, interaction.guild.id))
        self.conn.commit()
        await self.bot.success(
            f"Welcome channel successfully set to **{channel.name}**!", interaction
        )

    @app_commands.command(
        name="set-welcomemsg",
        description="Set Welcome Message"
    )
    @app_commands.describe(
        message="Set a Welcome Message"
    )
    @app_commands.default_permissions(moderate_members=True)
    async def greet(self, interaction: Interaction, *, message: str = None):
        self.c.execute('''INSERT OR IGNORE INTO greetings (guild_id, greet_channel, greet_message, farewell_message, ban_message)
                          VALUES (?, ?, ?, ?, ?)''',
                       (interaction.guild.id, None, None, None, None))
        self.conn.commit()
        if message is None:
            self.c.execute('''UPDATE greetings
                              SET greet_message=?
                              WHERE guild_id=?''',
                           (None, interaction.message.guild.id))
            self.conn.commit()
            return await self.bot.success("Welcome message removed!", interaction)
        message = clean_string(message)
        self.c.execute('''UPDATE greetings
                          SET greet_message=?
                          WHERE guild_id=?''',
                       (message, interaction.guild.id))
        self.conn.commit()
        return await self.bot.success("Welcome message updated!", interaction)


async def setup(bot: Bot) -> None:
    await bot.add_cog(AutoMod(bot))
