from __future__ import annotations

import datetime
import discord
import aiosqlite
import sqlite3
from .. import Plugin
from typing import Optional
from discord import Member, User
from discord.ext import commands
from core import Bot, Embed, AfkModel
from discord import Interaction, app_commands
from discord.ui import View, Select
from config import VERSION
from typing import Optional
from discord.ext import commands, tasks
from logging import getLogger
from tortoise import Tortoise


class Leveling(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot


async def setup(bot: Bot) -> None:
    await bot.add_cog(Leveling(bot))
