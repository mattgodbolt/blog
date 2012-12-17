from pygments.lexer import RegexLexer
from pygments.token import *

class AsmLexer(RegexLexer):
    name = 'AsmLexer'
    aliases = ['asm']
    filenames = ['*.asm']

    tokens = {
        'root': [
            (r'\.[a-zA-Z_]+', Name.Label),
            (r';.*\n', Comment),
            (r'&[0-9a-fA-F]+', Literal.Number.Hex),
            (r'-?[0-9]+', Literal.Number.Integer),
            (r'(\[|\])', Punctuation),
            (r'[-#,{}!:]', Punctuation),
            (r'(R[0-9]+|PC)', Name.Variable),
            (r'"[^"]+"', Literal.String),
            (r'(STR|LDR|ADD|SUB|SWI|AND|ORR|CMP|BIC|MOVS?|LDM|STM|B)'
                r'(NE|EQ|GT|GE|LT|LE|VC|VS)?'
                r'(FD)?'
                , Token.Keyword),
            (r'[a-zA-Z_]+',Name.Label),
            (r' +', Text),
        ]
    }
