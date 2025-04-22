from typing import ClassVar

from pygments.lexer import RegexLexer
from pygments.token import Comment, Literal, Name, Punctuation, Text, Token

__all__ = ["AsmLexer"]


class AsmLexer(RegexLexer):
    name = "AsmLexer"
    aliases: ClassVar[list[str]] = ["asm"]
    filenames: ClassVar[list[str]] = ["*.asm"]

    tokens: ClassVar[dict[str, list[tuple[str, Token | str]]]] = {
        "root": [
            (r"\.[a-zA-Z_][a-zA-Z_0-9]*", Name.Label),
            (r";.*\n", Comment),
            (r"[&$][0-9a-fA-F]+", Literal.Number.Hex),
            (r"-?[0-9]+", Literal.Number.Integer),
            (r"(\[|\])", Punctuation),
            (r"[-,{}!:()#=?.+%]", Punctuation),
            (r'"[^"]+"', Literal.String),
            (
                r"(LD[AXY]|ST[AXY]|CMP|CP[XY]|IN[CXY]|RT[SI]|ADC|SBC|SE[IC]|CL[IC]|T[AXY][AXY]|RO[LR]|JSR|JMP|DIV|MOD|ASL|P[HL][AXY]|BIT|DE[CXY]|ORA|EOR)",
                Token.Keyword,
            ),
            (
                r"(STR|LDR|ADD|SUB|SWI|AND|ORR|CMP|BIC|MOVS?|LDM|STM|B)"
                r"(NE|EQ|GT|GE|LT|LE|VC|VS|PL|MI|CC|CS)?"
                r"(FD)?",
                Token.Keyword,
            ),
            (r"(R[0-9]+|PC|X|Y|A|P)", Name.Variable),
            (r"[a-zA-Z_][a-zA-Z_0-9]*", Name.Label),
            (r" +", Text),
        ]
    }
