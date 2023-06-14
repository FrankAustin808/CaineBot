from __future__ import annotations
import discord
import os
import sys
import config
import random
import asyncio
import datetime, time

from datetime import timedelta
from typing import Optional
from .embed import Embed
from discord.ext import commands, tasks
from logging import getLogger
import discord
from tortoise import Tortoise
from config import *

log = getLogger("Bot")

__all__ = (
    "Bot",
)

start_time = time.time()

client = discord.Client

class Bot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix="^",
            intents=discord.Intents.all(),
            chunk_guild_at_startup=False,
            help_command=None
        )


    async def setup_hook(self) -> None:

        await Tortoise.init(
            db_url=f"postgres://{config.USER}:{config.PASSWORD}@{config.HOST}:{config.PORT}/{config.DB_NAME}",
            modules= {
                "models": ['core.models']
            }
        )
        await Tortoise.generate_schemas(safe=True)
        for file in os.listdir('cogs'):
            if not file.startswith("_"):
                await self.load_extension(f"cogs.{file}.plugin")



    async def on_ready(self) -> None:
        members = 0
        for guild in self.guilds:
             members += guild.member_count - 1

        await self.change_presence(activity=discord.Game(name=f"On {len(self.guilds)} Servers | Protecting {members} People | {VERSION} | /help"))
        log.info(f"Logged in as {self.user}")
        self.tree.sync
        print(f"Caine Is Supporting {len(self.guilds)} Servers | Protecting {members} People | {VERSION} |")
    
    async def on_connect(self) -> None:
        if '-sync' in sys.argv:
            synced_commands = await self.tree.sync()
            log.info(f"Successfully synced {len(synced_commands)} commands! 🙃")


    async def success(
            self,
            message: str,
            interaction: discord.Interaction,
            *,
            ephemeral: Optional[bool] = True,
            embed: Optional[bool] = True
    ) ->Optional[discord.WebhookMessage]:
            if embed:
                if interaction.response.is_done():
                    return await interaction.followup.send(
                        embed=Embed(description=message, color=discord.Colour.from_rgb(
                         r= 8,
                         g= 255,
                         b= 8
                        )),
                        ephemeral=ephemeral
                    )
                return await interaction.response.send_message(
                    embed=Embed(description=message, color=discord.Colour.from_rgb(
                     r= 8,
                     g= 255,
                     b= 8
                    )),
                    ephemeral=ephemeral
                )
            else:
                if interaction.response.is_done():
                    return await interaction.followup.send(content=f"✔️ | {message}", ephemeral=ephemeral)
                return await interaction.response.send_message(content=f"✔️ | {message}", ephemeral=ephemeral)
            
    async def error(
            self,
            message: str,
            interaction: discord.Interaction,
            *,
            ephemeral: Optional[bool] = True,
            embed: Optional[bool] = True
    ) ->Optional[discord.WebhookMessage]:
            if embed:
                if interaction.response.is_done():
                    return await interaction.followup.send(
                        embed=Embed(description=message, color=discord.Colour.from_rgb(
                         r=255, 
                         g= 49, 
                         b= 49
                        )),
                        ephemeral=ephemeral
                    )
                return await interaction.response.send_message(
                    embed=Embed(description=message, color=discord.Colour.from_rgb(
                     r= 255,
                     g= 49,
                     b= 49
                    )),
                    ephemeral=ephemeral
                )
            else:
                if interaction.response.is_done():
                    return await interaction.followup.send(content=f"✖️ | {message}", ephemeral=ephemeral)
                return await interaction.response.send_message(content=f"✖️ | {message}", ephemeral=ephemeral)
            
    

     
