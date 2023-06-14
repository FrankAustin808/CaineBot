from __future__ import annotations

from typing import Optional, Union

from discord import Colour, Embed as OriginalEmbed
from typing_extensions import Self

__all__ = ("Embed")

class Embed(OriginalEmbed):
    def __init__(self, color: Optional[Union[int, Colour]] = Colour.og_blurple(), **kwargs):
        super().__init__(color=color, **kwargs)

    def credits(self) -> Self:
        super().set_footer(text="Made with ❤️ by FrankIsDank#6141")
        return self