from __future__ import annotations
from core import Bot, Embed, AfkModel
from .. import Plugin
from db import database
from typing import Optional
from discord import Member, Message, User, Embed, Interaction, app_commands
from discord.ext import commands
from discord.ui import View, Select
from config import VERSION
from random import randint
from discord.ext import commands, tasks
from logging import getLogger
from datetime import datetime, timedelta
from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions


class Leveling(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def process_xp(self, message: Message):
        xp, lvl, xplock = database.record(
            "SELECT XP, Level, XPLock FROM exp WHERE UserID = ?", message.author.id)

        if datetime.utcnow > datetime.fromisoformat(xplock):
            await self.add_xp(message, xp, lvl)

    async def add_xp(self, interaction: Interaction, message: Message, xp, lvl):
        xp_to_add = randint(10, 30)
        new_level = int(((xp+xp_to_add)//42) ** 0.55)

        database.execute("UPDATE exp SET XP = XP + ?, Level = ?, XPLock = ? WHERE UserID = ?",
                         xp_to_add, new_level, (datetime.utcnow()+timedelta(seconds=60)).isoformat(), message.author.id)

        if new_level > lvl:
            await interaction.response.send_message(f"Congrats {message.author.mention} - you've reached level {new_level:,}!")
            await self.check_lvl_rewards(message, new_level)

    async def check_lvl_rewards(self, message: Message, lvl):
        if lvl >= 50:  # Red
            if (new_role := message.guild.get_role(653940117680947232)) not in message.author.roles:
                await message.author.add_roles(new_role)
                await message.author.remove_roles(message.guild.get_role(653940192780222515))

        elif 40 <= lvl < 50:  # Yellow
            if (new_role := message.guild.get_role(653940192780222515)) not in message.author.roles:
                await message.author.add_roles(new_role)
                await message.author.remove_roles(message.guild.get_role(653940254293622794))

        elif 30 <= lvl < 40:  # Green
            if (new_role := message.guild.get_role(653940254293622794)) not in message.author.roles:
                await message.author.add_roles(new_role)
                await message.author.remove_roles(message.guild.get_role(653940277761015809))

        elif 20 <= lvl < 30:  # Blue
            if (new_role := message.guild.get_role(653940277761015809)) not in message.author.roles:
                await message.author.add_roles(new_role)
                await message.author.remove_roles(message.guild.get_role(653940305300815882))

        elif 10 <= lvl < 20:  # Purple
            if (new_role := message.guild.get_role(653940305300815882)) not in message.author.roles:
                await message.author.add_roles(new_role)
                await message.author.remove_roles(message.guild.get_role(653940328453373952))

        elif 5 <= lvl < 9:  # Black
            if (new_role := message.guild.get_role(653940328453373952)) not in message.author.roles:
                await message.author.add_roles(new_role)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Leveling(bot))
