from __future__ import annotations
from core import Bot, Embed, AfkModel
from .. import Plugin
from db import database
from typing import Optional
from discord import Member, Message, User, Embed, Interaction, app_commands, SelectMenu
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
from discord.ext.menus import MenuPages, ListPageSource


class HelpMenu(ListPageSource):
    def __init__(self, interaction: Interaction, data):
        super().__init__(data, per_page=10)

    async def write_page(self, interaction: Interaction, menu: MenuPages, offset, fields=[]):
        len_data = len(self.entries)

        embed = Embed(title="XP Leaderboard",
                      color=interaction.user.accent_color)
        embed.set_thumbnail(url=interaction.guild.icon.url)
        embed.set_footer(
            text=f"{offset:,} - {min(len_data, offset+self.per_page-1):,} members.")

        for name, value in fields:
            embed.add_field(name=name, value=value, inline=False)

        return embed

    async def format_page(self, interaction: Interaction, menu: MenuPages, entries):
        offset = (menu.current_page*self.per_page) + 1

        fields = []
        table = ("\n".join(f"{idx+offset}. {interaction.guild.get_member(entry[0]).display_name} (XP: {entry[1]} | level: {entry[2]})"
                           for idx, entry in enumerate(entries)))

        fields.append(("Ranks", table))

        return await self.write_page(menu, offset, fields)


class exp(Plugin):
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

    @app_commands.command(name='level', description="Shows selected targets current level")
    async def display_user_level(self, interaction: Interaction, target: Optional[Member]):
        target = target or interaction.user

        xp, lvl = database.record(
            "SELECT XP, Level FROM exp WHERE UserID = ?", target.id) or (None, None)

        if lvl is not None:
            await interaction.response.send_message(f"{target.display_name} is on level {lvl:,} with {xp:,} XP.", ephemeral=True)
        else:
            await self.bot.error(f"{target.display_name} is not tracked by the XP System.", interaction)

    @app_commands.command(name='rank', description="Shows selected targets current rank")
    async def display_rank(self, interaction: Interaction, target: Optional[Member]):
        target = target or interaction.user

        ids = database.column("SELECT UserID FROM exp ORDER BY XP DESC")
        try:
            await interaction.response.send_message(f"{target.display_name} is rank {ids.index(target.id)+1} of {len(ids)}.", ephemeral=True)
        except ValueError:
            await self.bot.error(f"{target.display_name} is not tracked by the XP System.", interaction)

    @Cog.listener()
    async def on_ready(self):
        if not self.bot._ready:
            self.levelup_channel = self.bot.get_channel(759432499221889034)
            self.bot.add_cog("exp")

    @Cog.listener()
    async def on_message(self, message: Message):
        if not message.author.bot:
            await self.process_xp(message)


async def setup(bot: Bot) -> None:
    await bot.add_cog(exp(bot))
