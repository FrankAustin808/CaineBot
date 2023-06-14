from __future__ import annotations

from typing import Optional, Callable, Any
from humanfriendly import parse_timespan, InvalidTimespan
from datetime import timedelta, datetime
from .. import Plugin
from core import Bot, Embed
from discord import (app_commands,
                     Interaction,
                     Member,
                     User,
                     utils as Utils,
                     CategoryChannel,
                     ForumChannel,
                     PartialMessageable,
                     Object,
                     TextChannel,
                     Message,
                     Permissions,
                     StageChannel,
                     VoiceChannel,
                     Role,
                     Attachment,
                     Forbidden,
                     Color
                     )
from discord.ext import commands
from discord.ui import View, Select
from pytz import UTC
import discord
import asyncio
import time
import re
import sqlite3
import aiohttp

now = datetime.now()

current_time = now.strftime("%H:%M:%S")

class ModHelp(Select):
    def __init__(self, bot: commands.bot):
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name, description=cog.__doc__
                ) for cog_name, cog in bot.cogs.items() if cog.__cog_commands__ and cog_name not in ['Jishaku']
            ]
        )

        self.bot = bot

    async def callback(
            self,
            interaction: Interaction
    ) -> None:
        cog = self.bot.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_commands():
            commands_mixer.append(i)

        for i in cog.walk_app_commands():
            commands_mixer.append(i)

        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description='\n'.join(
                f"**{command.name}**: `{command.description}`"
                for command in commands_mixer
            )
        )
        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


def can_moderate():
    async def predicate(interaction: Interaction):
        target: Member = interaction.namespace.member or interaction.namespace.target
        target: User = interaction.namespace.member or interaction.namespace.target
        if not target:
            return True
        assert interaction.guild is not None and isinstance(
            interaction.user, Member)

        if (
            target.top_role.position > interaction.user.top_role.position
            or target.guild_permissions.kick_members
            or target.guild_permissions.ban_members
            or target.guild_permissions.administrator
            or target.guild_permissions.manage_guild
        ):
            raise app_commands.CheckFailure(f"You cannot moderate *{target}**")
        return True
    return app_commands.check(predicate)


class Moderation(Plugin):
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

    async def clean_message(self, interaction: Interaction, amount: int, check: Callable) -> Any:
        if isinstance((channel := interaction.channel), (CategoryChannel, ForumChannel, PartialMessageable)):
            return
        assert channel is not None
        try:
            msgs = [
                m async for m in channel.history(
                    limit=30000000,
                    before=Object(id=interaction.id),
                    after=None
                ) if check(m) == True and UTC.localize((datetime.now() - timedelta(days=100))) <= m.created_at  # default 14
            ][:amount]
            await channel.delete_messages(msgs)
        except Exception as e:
            msg = await self.bot.error(
                f"I'm sorry, I am unable to purge **{amount}** messages in **{channel}**!", interaction
            )
            if msg:
                await msg.delete(delay=5)
        else:
            if len(msgs) < 0:
                msg = await self.bot.error(
                    f"No messages found in **{channel}**!", interaction
                )
                if msg:
                    await msg.delete(delay=5)
            else:
                msg = await self.bot.success(
                    f"Succesfully purged **{len(msgs)}** messages from **{channel}**!", interaction
                )
                if msg:
                    await msg.delete(delay=5)

    @app_commands.command(
        name='kick',
        description="Kick a user"
    )
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(
        member="Select a user to kick.",
        reason="Reason for kicking user."
    )
    @app_commands.guild_only()
    @can_moderate()
    async def kick_command(self, interaction: Interaction, member: Member, reason: Optional[str]):
        if not reason:
            reason = "No reason."
        try:
            await member.kick(reason=reason)
        except:
            await self.bot.error(f"I'm sorry, I am unable to kick {member} from the server.", interaction)
        else:
            await self.bot.success(
                f"**{member}** has been kicked from the server for **{reason}**!",
                interaction,
                ephemeral= False
            )

    @app_commands.command(
        name='ban',
        description="Ban a user"
    )
    @app_commands.default_permissions(kick_members=True)
    @app_commands.describe(
        member="Select a user to ban.",
        reason="Reason for banning user."
    )
    @app_commands.guild_only()
    @can_moderate()
    async def ban_command(self, interaction: Interaction, member: Member, reason: Optional[str]):
        if not reason:
            reason = "No reason."
        try:
            await member.ban(reason=reason)
        except:
            await self.bot.error(f"I'm sorry, I am unable to ban {member} from the server.", interaction)
        else:
            await self.bot.success(
                f"**{member}** has been banned from the server for **{reason}**!",
                interaction,
                ephemeral= False
            )

    @app_commands.command(
        name='unban',
        description="unban user from server"
    )
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(
        user="Select a user to unban",
        reason="Reason for unbanning user"
    )
    @app_commands.guild_only()
    @can_moderate()
    async def unban_command(self, interaction: Interaction, user: User, reason: Optional[str]):
        if not reason:
            reason = "No reason."
            assert interaction.guild is not None
        try:
            await interaction.guild.fetch_ban(user)
        except:
            await self.bot.error(f"{user} is not banned!", interaction)
        else:
            try:
                await interaction.guild.unban(user, reason=reason)
            except:
                await self.bot.error(
                    f"I'm sorry, I am unable to unban {user} from the server.", interaction
                )
            else:
                await self.bot.success(
                    f"**{user}** has been unbanned from the server!", interaction
                )

    @app_commands.command(
        name="mute",
        description="Mute a user"
    )
    @app_commands.commands.default_permissions(moderate_members=True)
    @can_moderate()
    @app_commands.describe(
        target="Please select a user",
        duration="Provide a mute duration. (Example: 'id', '30m', '10s')",
        reason="Provide a reason for muting user"
    )
    async def mute_command(self, interaction: Interaction, target: Member, duration: Optional[str], reason: Optional[str]):
        if not duration:
            duration = "1d"
        try:
            real_duration = parse_timespan(duration)
        except InvalidTimespan:
            await self.bot.error(f"`{duration}` is not a valid duration. Please provide a correct duration (Example: 'id', '30m', '10s')", interaction)
        else:
            try:
                await target.timeout(Utils.utcnow()+timedelta(seconds=real_duration), reason=reason)
            except:
                await self.bot.error(
                    f"I'm sorry but I am unable to mute **{target}** for `{duration}`", interaction
                )
            else:
                await self.bot.success(
                    f"**{target}** has been muted for `{duration}` for **{reason}**", interaction
                )

    @app_commands.command(
        name='unmute',
        description="unmute a user"
    )
    @app_commands.commands.default_permissions(moderate_members=True)
    @can_moderate()
    @app_commands.describe(
        target="Select a user to unmute",
        reason="Reason for unmuting user"
    )
    async def unmute_command(self, interaction: Interaction, target: Member, reason: Optional[str]):
        if not target.is_timed_out():
            return await self.bot.error(f"**{target}** is not muted!", interaction)
        try:
            await target.timeout(None, reason=reason)
        except:
            await self.bot.error(
                f"I'm sorry, but I'm unable to unmute **{target}**",
                interaction
            )
        else:
            await self.bot.success(
                f"Successfully unmuted **{target}**",
                interaction
            )

    @app_commands.command(
        name='purge',
        description="Purges messages in channel"
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.describe(
        amount='Amount of messages to purge (Default: 30)',
        user='Only purge messages by user',
        content='Only purge messages by content'
    )
    async def purge_command(self, interaction: Interaction, amount: Optional[int], user: Optional[User], content: Optional[str]):
        if not amount:
            amount = 30
        if amount < 1:
            return await self.bot.error("Can't purge messages! Amount too small!", interaction)
        if amount > 3000:
            return await self.bot.error("Can't purge messages! Amount too Large!", interaction)

        if user == None and content == None:
            def check(x): return x.pinned == False
        else:
            if user != None and content != None:
                def check(x): return x.author.id == user.id and x.content.lower(
                ) == content.lower() and x.pinned == False
            elif user != None and content == None:
                def check(x): return x.author.id == user.id and x.pinned == False
            else:
                assert content is not None
                def check(x): return x.conetent.lower(
                ) == content.lower() and x.pinned == False
        await interaction.response.defer()
        await self.clean_message(
            interaction=interaction,
            amount=amount,
            check=check
        )

    @app_commands.command(
        name='lock',
        description="Lock a text channel"
    )
    @app_commands.describe(
        channel='Select a channel'
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_channels=True)
    async def lock_command(self, interaction: Interaction, channel: Optional[TextChannel]):
        target = channel or interaction.channel
        assert interaction.guild is not None and isinstance(
            target, TextChannel)
        try:
            await target.set_permissions(interaction.guild.default_role, send_messages=False)
        except:
            await self.bot.error(
                f"I'm sorry, I am unable to lock **{target}**", interaction
            )
        else:
            await self.bot.success(
                f"Successfully locked **{target}**", interaction
            )

    @app_commands.command(
        name='unlock',
        description="Unlock a text channel"
    )
    @app_commands.describe(
        channel='Select a channel',
        reset="If true, only target permissions will be reset."
    )
    @app_commands.guild_only()
    @app_commands.default_permissions(manage_channels=True)
    async def unlock_command(self, interaction: Interaction, channel: Optional[TextChannel], reset: Optional[bool]):
        target = channel or interaction.channel
        assert interaction.guild is not None and isinstance(
            target, TextChannel)
        try:
            await target.set_permissions(interaction.guild.default_role, send_messages=None if reset else True)
        except:
            await self.bot.error(
                f"I'm sorry, I am unable to unlock **{target}**", interaction
            )
        else:
            await self.bot.success(
                f"Successfully unlocked **{target}**!", interaction
            )

    _role = app_commands.Group(
        name='role',
        description="Manage server roles.",
        default_permissions=Permissions(manage_roles=True),
        guild_only=True
    )

    @_role.command(
        name='create',
        description="Create a  new role!"
    )
    @can_moderate()
    async def role_create(
        self,
        interaction: Interaction,
        name: str,
        hoist: Optional[bool],
        mentionable: Optional[bool],
        color: Optional[str],
        display_icon: Optional[Attachment]
    ):
        assert interaction.guild is not None
        try:
            hoist, mentionable, color_obj, display_icon_bytes = (
                hoist or Utils.MISSING,
                mentionable or Utils.MISSING,
                Color.from_str(color) if color else Utils.MISSING,
                await display_icon.read() if display_icon else Utils.MISSING
            )

            role = await interaction.guild.create_role(
                name=name,
                hoist=hoist,
                mentionable=mentionable,
                color=color_obj,
                display_icon=display_icon_bytes  # Needs Server Boosts
            )
        except Forbidden as e:  # This handles errors if the server doesnt have boosts
            await self.bot.error(
                e.text,
                interaction
            )
        except:
            await self.bot.error(
                f"I'm sorry, but i am unable to create the **{name}** role.",
                interaction,
            )
        else:
            await self.bot.success(
                f"Successfully created a new role: **{role}** ", interaction
            )

    @_role.command(
        name='delete',
        description="Delete a role."
    )
    @can_moderate()
    async def role_delete(
        self,
        interaction: Interaction,
        role: Role,
        reason: Optional[str]
    ):
        try:
            await role.delete(reason=reason)
        except:
            await self.bot.error(
                f"I'm sorry, I am unable to delete the **{role}** role.", interaction
            )
        else:
            await self.bot.success(
                f"Successfully deleted: **{role}**.", interaction
            )

    @_role.command(
        name='give',
        description="Give role to a user."
    )
    @can_moderate()
    async def role_give(self, interaction: Interaction, member: Member, role: Role):
        assert interaction.guild is not None
        try:
            await member.add_roles(role)
        except:
            await self.bot.error(
                f"I'm sorry, I am unable to give **{member.mention}** the **{role.mention}** role.", interaction
            )
        else:
            await self.bot.success(
                f"Successfully given **{member.mention}** the **{role.mention}** role!", interaction
            )

    @_role.command(
        name='remove',
        description="Remove a role from a user."
    )
    @can_moderate()
    async def role_remove(self, interaction: Interaction, member: Member, role: Role):
        assert interaction.guild is not None
        try:
            await member.remove_roles(role)
        except:
            await self.bot.error(
                f"I'm sorry, I am unable to remove **{role.mention}** from **{member.mention}**", interaction
            )
        else:
            await self.bot.success(
                f"Successfully removed **{role.mention}** from **{member.mention}**!", interaction
            )

    @app_commands.command(
        name='dm',
        description="Sends user a DM as Caine."
    )
    @app_commands.describe(
        user='Select a user.'
    )
    @can_moderate()
    async def senduserdm_command(self, interaction: Interaction, user: User, *, message: str):
        message = message + f" - From Server: **{interaction.guild}**, Sent By: **{interaction.user}**"
        try:
            await user.send(message)
            await self.bot.success(
                f"Sent DM to **{user}** ✉️", interaction
            )
        except discord.Forbidden:
            await self.bot.error(
                f"I'm sorry, I was unable to DM **{user}**. They may have their DMs blocked.", interaction
            )

    @app_commands.command(
        name='cainename',
        description="Changes Caine's server nickname."
    )
    @can_moderate()
    async def change_nickname(self, interaction: Interaction, *, name: str = None):
        try:
            await interaction.guild.me.edit(nick=name)
            if name:
                return await self.bot.success(
                    f"Successfully changed Caine's nickname to **{name}**", interaction
                )
            await self.bot.success("Successfully removed nickname", interaction)
        except Exception as errormsg:
            await  self.bot.error(errormsg, interaction)

    @app_commands.command(
        name='nickname',
        description="Changes members server nickname."
    )
    @app_commands.describe(
        member= "Select a member",
        name="Change Nickname",
        reason="Reason for changing members nickname"
    )
    @can_moderate()
    async def nickname_command(self, interaction: Interaction, member: Member, *, name: str = None, reason: Optional[str]):
        try:
            await member.edit(nick=name, reason=reason)
            await self.bot.success(
                f"Successfully changed **{member.name}**'s nickname to **{name}** {reason}!", interaction
            )
            if name is None:
                await self.bot.success(
                    f"Successfully reset **{member.name}**'s nickname!", interaction
                )
        except Exception as e:
            await self.bot.error(
                f"I'm sorry, I am unable to change **{member.name}**'s nickname to **{name}**."
            )
        
    @app_commands.command(
        name="lockdown",
        description="Lockdown a text channel"
    )
    @app_commands.describe(
        channel="Select a channel"
    )
    @can_moderate()
    async def lockdown_command(self, interaction: Interaction, channel: TextChannel = None):
        channel = channel or interaction.channel
        role = interaction.guild.default_role

        if role not in channel.overwrites:
            overwrites = {
                role: discord.PermissionOverwrite(send_messages=False)
            }
            await channel.edit(overwrites=overwrites)
            if interaction.channel != channel:
                await self.bot.success(
                    f"I have sucessfully put **{channel.mention}** on lockdown.", 
                    interaction
                )
            else:
                await interaction.message.delete()
                await channel.send(embed=discord.Embed(title="**This channel is now under lockdown**",color=discord.Colour.red()))
        elif channel.overwrites[role].send_messages is True or \
                channel.overwrites[role].send_messages is None:
            overwrites = channel.overwrites[role]
            overwrites.send_messages = False
            await channel.set_permissions(role, overwrite=overwrites)
            if interaction.channel != channel:
                await self.bot.success(
                    f"I have sucessfully put **{channel.mention}** on lockdown.", 
                    interaction
                )
            else:
                await interaction.message.delete()
            await channel.send(embed=discord.Embed(title="**This channel is now under lockdown**",color=discord.Colour.red()))
        else:
            overwrites = channel.overwrites[role]
            overwrites.send_messages = True
            await channel.set_permissions(role, overwrite=overwrites)
            if interaction.channel != channel:
                await self.bot.success(
                    f"I have sucessfully removed **{channel.mention}** from lockdown.", interaction
                )
            else:
                await interaction.message.delete()
            await channel.send(embed=discord.Embed(title="**This channel is no longer under lockdown!**",color=discord.Colour.green()))


    @app_commands.command(
        name="checkmsg",
        description="Check how many messages a user has sent in a channel."
    )
    @app_commands.describe(
        user = "Select a user",
        channel="Select a channel"
    )
    async def checkspam_command(self, interaction: Interaction,user: Member = None, *,  channel: TextChannel = None):
        timeframe=7
        if timeframe > 1968:
            await self.bot.error("I'm sorry, the maximum amount of days you can check is **1968**.", interaction)
        elif timeframe <= 0:
            await self.bot.error("I'm sorry, the minimum amount of days you can check is **one**.", interaction)

        else:
            if not channel:
                channel = interaction.channel
            if not user:
                user = interaction.message.author

            async with interaction.channel.typing():

                counter = 0
                async for message in channel.history(limit=5000, after=datetime.now() - timedelta(days=timeframe)):
                    if message.author.id == user.id:
                        counter += 1

                if counter >= 5000:
                    await self.bot.success(
                        f'**{user}** has sent over 5000 messages in "**{channel}**" within the last **{timeframe}** days!', interaction
                    )
                else:
                    await self.bot.success(
                        f'**{user}** has sent **{str(counter)}** messages in "**{channel}**" within the last **{timeframe}** days.', interaction
                    )

    @app_commands.command(
        name="invites",
        description="Lets you see how many server invites a user has sent"
    )
    @app_commands.describe(
        user = "Select a user"
    )
    async def invites_command(self, interaction: Interaction, user: Member = None):
        if user is None:
            total_invites = 0
            for i in await interaction.guild.invites():
                if i.inviter == interaction.message.author:
                    total_invites += i.uses
            await self.bot.success(
                f"You've invited **{total_invites} member{'' if total_invites == 1 else 's'}** to **{interaction.guild.name}**!", interaction
            )
        else:
            total_invites = 0
            for i in await interaction.guild.invites():
                if i.inviter == user:
                    total_invites += i.uses

            await self.bot.success(
                f"**{user}** has invited **{total_invites} member{'' if total_invites == 1 else 's'}** to **{interaction.guild.name}**!", interaction
            )
                    
    @app_commands.command(
        name="whois",
        description="Gives all available user information"
    )
    @app_commands.describe(
        member = "Select a member"
    )
    async def whois(self, interaction: Interaction, member: Member = None):
        if not member:
            member = interaction.user

        roles = [role for role in member.roles]
        embed = discord.Embed(colour=discord.Colour.random(), title=str(member))
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}")
        embed.add_field(name="Display Name:", value=member.display_name, inline=False)
        embed.add_field(name="User ID:", value=f"{member.id}", inline=False)
        embed.add_field(name="Account Made On:", value=member.created_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        embed.add_field(name="Joined Server On:", value=member.joined_at.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        #embed.add_field(name="Server Boosting Since:", value=member.premium_since.strftime("%a, %#d %B %Y, %I:%M %p UTC"), inline=False)
        #need to figure out how to make this work without crashing, It works if user is server boosting :P
        embed.add_field(name="Highest Role:", value=member.top_role.mention, inline=False)
        embed.add_field(name="All Roles:", value="\n".join([role.mention for role in roles[1:]]), inline=False)
        embed.timestamp = datetime.utcnow()
        await interaction.response.send_message(embed=embed, ephemeral=True)
        


async def setup(bot: Bot):
    await bot.add_cog(Moderation(bot))
