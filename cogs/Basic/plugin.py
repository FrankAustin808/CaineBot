from __future__ import annotations

import discord
import datetime
import discord
from .. import Plugin
from typing import Optional
from discord import Member, User, Message
from discord.ext import commands
from core import Bot, Embed, AfkModel
from discord import Interaction, app_commands, Permissions
from discord.ui import View, Select
from config import VERSION
from typing import Optional
from discord.ext import commands, tasks
from logging import getLogger
from tortoise import Tortoise
from cogs import *


class Basic(Plugin):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @Plugin.listener('on_message')
    async def on_afk(self, message: discord.message):
        if message.author.bot:
            return
        if not message.guild:
            return

        afk = await AfkModel.get_or_none(id=message.author.id, guild_id=message.guild.id)
        if afk:
            await message.reply(
                f"Welcome back {afk.mention}! You were AFK since: {afk.formated_since}"
            )
            return await afk.delete()
        for user in message.mentions:
            afk = await AfkModel.get_or_none(id=user.id, guild_id=message.guild.id)
            if afk:
                await message.reply(
                    f"{afk.mention} has been afk since {afk.formated_since} for: {afk.reason}."
                )

    @app_commands.command(
        name='bug',
        description="Report a bug you have found!"
    )
    async def bug_command(self, interaction: Interaction):
        embed = Embed(
            description=f"Found a bug? Awesome, please report [here](https://github.com/FrankIsDank/Caine/issues/)! :smiley:"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='feature',
        description="Request a feature for Caine!"
    )
    async def feature_command(self, interaction: Interaction):
        embed = Embed(
            description=f"Want to request a feature? Please do! You can request a feature [here!](https://github.com/FrankIsDank/Caine/issues/new?assignees=&labels=&projects=&template=feature-request.md&title=) :smiley:"
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='membercount',
        description="Shows the amount of members in the guild"
    )
    async def membercount_command(self, interaction: Interaction):
        embed = Embed(color=discord.Colour.random())
        embed.set_author(name=f"Caine",
                         icon_url=self.bot.user.avatar)
        embed.add_field(name="Current Member Count: ",
                        value=interaction.guild.member_count)
        embed.set_footer(text=interaction.guild,
                         icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(
        name='afk',
        description="Set your AFK."
    )
    async def set_afk(self, interaction: Interaction, reason: Optional[str]):
        reason = reason or "I'm AFK :)"
        record = await AfkModel.get_or_none(pk=interaction.user.id)
        if not record:
            await AfkModel.create(id=interaction.user.id, guild_id=interaction.guild_id, reason=reason)
            return await self.bot.success(
                f"You're AFK status has been set to: {reason}",
                interaction
            )
        await self.bot.error(
            f"You are already AFK!", interaction
        )

    @app_commands.command(
        name='embed',
        description="Create a custom embed message"
    )
    @app_commands.describe(
        message="Write Your Message"
    )
    async def embed_command(self, interaction: Interaction, message: str = None):
        embed = Embed(color=discord.Colour.random())
        embed.set_author(name=interaction.user, url=interaction.user.avatar)
        embed.add_field(name="", value=message)
        embed.set_footer(text=interaction.guild,
                         icon_url=interaction.guild.icon)
        embed.timestamp = datetime.datetime.now()
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name='msg-formating',
        description="Shows Discord Message Formating!"
    )
    async def message_formating(self, interaction: Interaction):
        await interaction.response.send_message('''
# ***Discord Message Formatting***

## **Headers**

> Add # Before Text For Large Header.

> Add ## Before Text For Medium Header.

> Add ### Before Text For Small Header.

### **Examples**

> # Large Header.
> ## Medium Header.
> ### Small Header.

## Text Formatting

### *Remember Close The Asterisks*

### These Can Be Combined!

### *Italics*
> Italics: - One Asterisk [ * ] Before / After Text.

### **Bold**
> Bold: - Two Asterisks [ * ] Before / After Text.

### ***Bold italics***
> Bold Italics: - Three Asterisks [ * ] Before / After Text.

### __Underline__
> Underline: - Two Underscore Symbols [ _ ] Before / After Text.

### ~~Strikethrough~~
> Strikethrough: - Two Tilde Symbols [ ~ ] Before / After Text.

### ||BOO! Spoiler Message 👻||
> Spoiler: - Two Verticle Bars [ | ] Before / After Text.

## **Lists**

**List Option One: * **

**List Option Two: -**

### **Examples**

> Option One:
> * List Item One
> 
> Option Two:
> - List Item Two

## **Code Blocks**

> Single Line Code Block: Start And End Your Message With A Backtick Symbol [ ` ]
> 
> Multi-Line Code Block: Start And End Your Message With Three Backtick Symbols [ ` ]
> 
> Multi-Line Code Block With Language: Start Your Message With Three Backtick Symbols Then Type The Language Name Then End Your Message With Three Backtick Symbols [ ` ] ( Example: Python = Python or py )

### **Examples**

` Test Single Line Code Block `

```
Test Multi-Line Code Block

```
```python
    async def on_ready(self) -> None:
        log.info("Test Multi-Line Code Block With Language")
        self.tree.sync
```

## **Block Quotes**

**If You Want To Add A Single Block Quote, Just Add (>) Before The First Line. **
***For Example:***

> Test

**If You Want To Add Multiple Lines To A Single Block Quote, Just Add (>>>) Before The First Line. **
***For Example:***

>>> Test
Hello 
How Are Ya?
''', ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Basic(bot))
