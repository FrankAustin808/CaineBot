from __future__ import annotations

import discord
from tortoise.models import Model
from tortoise import fields


__all__ = (
    "AfkModel",
)


class AfkModel(Model):
    id = fields.BigIntField(pk=True, unique=True)
    guild_id = fields.BigIntField()
    reason = fields.CharField(max_length=1000)
    since = fields.DatetimeField(auto_now=True)

    @property
    def mention(self) -> str:
        return f"<@{self.id}>"

    @property
    def formated_since(self) -> str:
        return discord.utils.format_dt(self.since)

    class Meta:
        table = "afks"
