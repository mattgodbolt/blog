from typing import ClassVar

from pygments.lexer import RegexLexer, bygroups, using
from pygments.lexers import GasLexer
from pygments.token import Number, Text, Whitespace

__all__ = ["HexasmLexer"]


class HexasmLexer(RegexLexer):
    """
    Lexer for hexadecimal disassembly format with GAS syntax.

    Expects format like:
        aa bb cc dd       mov eax, 0x10

    Hex bytes are separated by single spaces, then multiple spaces
    separate the instruction which is highlighted using GAS syntax.
    """

    name = "HexasmLexer"
    aliases: ClassVar[list[str]] = ["hexasm"]
    filenames: ClassVar[list[str]] = ["*.hexasm"]

    tokens: ClassVar[dict] = {
        "root": [
            # Match hex bytes (pairs separated by single spaces), then multiple spaces, then GAS instruction
            (
                r"((?:[0-9a-fA-F]{2} )*[0-9a-fA-F]{2})( {2,})(.*?)$",
                bygroups(Number.Hex, Whitespace, using(GasLexer)),
            ),
            # Fallback for any other line
            (r".+$", Text),
        ]
    }
