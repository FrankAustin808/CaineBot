from __future__ import annotations

import discord
import time
import core

from .. import Plugin
from typing import Optional
from discord.ext import commands
from core import Bot, Embed, AfkModel
from discord import Interaction, app_commands, TextChannel
from discord.ui import View, Select
from config import VERSION
from typing import Optional
from logging import getLogger
from datetime import datetime, timedelta

start_time = time.time()


class Utility(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @app_commands.command(
        name='caine-info',
        description="Information about Caine!"
    )
    async def botinfo_comand(self, interaction: Interaction):
        members = 0
        for guild in self.bot.guilds:
            members += guild.member_count - 1

        synced_commands = await self.bot.tree.sync()
        embed = Embed(color=discord.Colour.random())
        embed.set_author(name=f"Caine",
                         icon_url=self.bot.user.avatar)
        embed.add_field(name='Hello, I am Caine', value=f'''
                        
            I Am In Version [***{VERSION}***] :gear:
            
            I Have **{len(synced_commands)} Commands**! :smiling_imp:

            I'm In **{len(self.bot.guilds)} Servers**! :partying_face:

            I Am Protecting **{members} Users**! :muscle:

            **__[I'm Open Source!](https://github.com/FrankIsDank/Caine)__** :information_source: 

            Library: **[discord.py](https://discordpy.readthedocs.io/en/stable/index.html#)** :books:

            Join My Discord Server **[Here!!](https://discord.gg/7xp23Ceuak)** :warning~1:

            Created by: **__FrankIsDank#6141__** :blue_heart:

            ''')
        embed.timestamp = datetime.now()
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='invite',
        description="Invite me to your server!"
    )
    async def invite_command(self, interaction: Interaction):
        await self.bot.success(
            f"**Hello! Use this to [Invite Me!](https://discord.com/api/oauth2/authorize?client_id=1108032171060502580&permissions=8&redirect_uri=https%3A%2F%2Fdiscordapp.com%2Foauth2%2Fauthorize%3F%26client_id%3D1108032171060502580%26scope%3Dbot&response_type=code&scope=bot) to your server!**",
            interaction
        )

    @app_commands.command(
        name='ping',
        description="Shows Caine's latency."
    )
    async def ping_command(self, interaction: Interaction):
        embed = Embed(
            description=f"My ping is {round(self.bot.latency*1000)}ms")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='channelhealth',
        description="Check the health of a channel"
    )
    @app_commands.describe(
        channel="Select a channel."
    )
    async def channel_status(self, interaction: Interaction, channel: TextChannel = None):
        if not channel:
            channel = interaction.channel

        server_id = self.bot.get_guild(self.bot.guilds[0].id)

        embed = discord.Embed(color=discord.Colour.random())
        embed.set_author(name=f"{channel} Channel Health")

        async with interaction.channel.typing():
            count = 0
            async for message in channel.history(limit=500000, after=datetime.today() - timedelta(days=100)):
                count += 1

            if count >= 500:
                average = "OVER 5000!"
                healthiness = "Very Healthy! 🥳"

            else:
                try:
                    average = round(count / 100, 2)

                    if 0 > server_id.member_count / average:
                        healthiness = "Very Healthy 🥳"
                    elif server_id.member_count / average <= 5:
                        healthiness = "Healthy 🙂"
                    elif server_id.member_count / average <= 10:
                        healthiness = "NORMAL 🤨"
                    elif server_id.member_count / average <= 20:
                        healthiness = "Unhealthy 😟"
                    else:
                        healthiness = "Very Unhealthy   "

                except ZeroDivisionError:
                    average = 0
                    healthiness = "Very Unhealthy 😞"

            embed.add_field(
                name="­", value=f"Number of members: **{server_id.member_count}**", inline=False)
            embed.add_field(
                name="­", value=f'Number of messages per day on average in "**{channel}**" is: **{average}**', inline=False)
            embed.add_field(
                name="­", value=f"Channel health: **{healthiness}**", inline=False)

            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='caine-uptime',
        description="Check Caine's Uptime"
    )
    async def uptime_command(self, interaction: Interaction):
        uptime = str(datetime.now() - timedelta(
            hours=int(round(time.time()-start_time))))

        embed = Embed(color=discord.Color.random())
        embed.set_thumbnail(url=interaction.user.avatar.url)
        embed.set_author(name="Caine Uptime!")
        embed.add_field(name="Current Uptime:", value=uptime)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='server-status',
        description="Shows current server status"
    )
    async def server_status(self, interaction: Interaction):
        guild = interaction.guild
        voice_channels = len(guild.voice_channels)
        text_channels = len(guild.text_channels)
        roles = [role for role in guild.roles]

        emoji_string = ""
        for e in guild.emojis:
            if e.is_usable():
                emoji_string += str(e)

        embed = Embed(color=discord.Colour.random())

        embed.set_author(
            name=self.bot.user.name
        )
        embed.set_thumbnail(
            url=interaction.user.avatar.url
        )
        embed.set_image(
            url=guild.icon
        )
        embed.add_field(
            name="Server Name",
            value=guild.name,
            inline=False
        )
        embed.add_field(
            name="Server Owner",
            value=guild.owner.mention
        )
        embed.add_field(
            name="Custom Emojies",
            value=emoji_string or "No custom emojies detected",
            inline=False
        )
        embed.add_field(
            name="Voice Channels",
            value=voice_channels
        )
        embed.add_field(
            name="Text Channels",
            value=text_channels
        )
        embed.add_field(
            name="AFK Channel",
            value=guild.afk_channel,
            inline=False
        )
        embed.add_field(
            name="Member Count",
            value=f"{guild.member_count} Members",
            inline=False
        )
        embed.add_field(
            name="Server Roles",
            value="\n".join([role.mention for role in roles[1:]]),
            inline=False
        )
        embed.add_field(
            name="Server Boosts",
            value=guild.premium_subscription_count
        )
        embed.set_footer(
            text=datetime.now()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Utility(bot))
