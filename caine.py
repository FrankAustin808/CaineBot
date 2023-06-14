from __future__ import annotations
import os
import asyncio
import discord
import random
from core import Bot
from config import TOKEN
from discord.ext import commands

client = commands.Bot(
    command_prefix="^", intents=discord.Intents.all())


async def main():
    discord.utils.setup_logging()
    async with Bot() as bot:
        await bot.start(TOKEN, reconnect=True)


if __name__ == '__main__':
    asyncio.run(main())
