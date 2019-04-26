from pygments.lexer import RegexLexer
from pygments.token import *

__all__ = ['BasicLexer']

tokens = [
    'OTHERWISE',
    'AND', 'DIV', 'EOR', 'MOD', 'OR', 'ERROR', 'LINE', 'OFF',
    'STEP', 'SPC', 'TAB(', 'ELSE', 'THEN', '<line>', 'OPENIN', 'PTR',
    'PAGE', 'TIME', 'LOMEM', 'HIMEM', 'ABS', 'ACS', 'ADVAL', 'ASC',
    'ASN', 'ATN', 'BGET', 'COS', 'COUNT', 'DEG', 'ERL', 'ERR',
    'EVAL', 'EXP', 'EXT', 'FALSE', 'FN', 'GET', 'INKEY', 'INSTR(',
    'INT', 'LEN', 'LN', 'LOG', 'NOT', 'OPENUP', 'OPENOUT', 'PI',
    'POINT(', 'POS', 'RAD', 'RND', 'SGN', 'SIN', 'SQR', 'TAN',
    'TO', 'TRUE', 'USR', 'VAL', 'VPOS', 'CHR$', 'GET$', 'INKEY$',
    'LEFT$(', 'MID$(', 'RIGHT$(', 'STR$', 'STRING$(', 'EOF',
    'WHEN', 'OF', 'ENDCASE', 'ELSE', 'ENDIF', 'ENDWHILE', 'PTR',
    'PAGE', 'TIME', 'LOMEM', 'HIMEM', 'SOUND', 'BPUT', 'CALL', 'CHAIN',
    'CLEAR', 'CLOSE', 'CLG', 'CLS', 'DATA', 'DEF', 'DIM', 'DRAW',
    'END', 'ENDPROC', 'ENVELOPE', 'FOR', 'GOSUB', 'GOTO', 'GCOL', 'IF',
    'INPUT', 'LET', 'LOCAL', 'MODE', 'MOVE', 'NEXT', 'ON', 'VDU',
    'PLOT', 'PRINT', 'PROC', 'READ', 'REM', 'REPEAT', 'REPORT', 'RESTORE',
    'RETURN', 'RUN', 'STOP', 'COLOUR', 'TRACE', 'UNTIL', 'WIDTH', 'OSCLI',
    'SUM', 'BEAT',
    'APPEND', 'AUTO', 'CRUNCH', 'DELET', 'EDIT', 'HELP', 'LIST', 'LOAD',
    'LVAR', 'NEW', 'OLD', 'RENUMBER', 'SAVE', 'TEXTLOAD', 'TEXTSAVE', 'TWIN',
    'TWINO', 'INSTALL',
    'CASE', 'CIRCLE', 'FILL', 'ORIGIN', 'PSET', 'RECT', 'SWAP', 'WHILE',
    'WAIT', 'MOUSE', 'QUIT', 'SYS', 'INSTALL', 'LIBRARY', 'TINT', 'ELLIPSE',
    'BEATS', 'TEMPO', 'VOICES', 'VOICE', 'STEREO', 'OVERLAY']


def escape(tok):
    return tok.replace("$", "\$").replace("(", "\(").replace(")", "\)")


tokenRe = "|".join(escape(token) for token in tokens)


class BasicLexer(RegexLexer):
    name = 'BasicLexer'
    aliases = ['basic']
    filenames = ['*.basic']

    tokens = {
        'root': [
            (r'\.[a-zA-Z_][a-zA-Z_0-9]*', Name.Label),
            (r'REM;.*\n', Comment),
            (r'[&$][0-9a-fA-F]+', Literal.Number.Hex),
            (r'-?[0-9]+', Literal.Number.Integer),
            (r'(\[|\])', Punctuation),
            (r'[-,{}!:()#=?.+%@]', Punctuation),
            (r'"[^"]+"', Literal.String),
            (tokenRe, Token.Keyword),
            (r'[a-zA-Z_][a-zA-Z_0-9]*', Name.Variable),
            (r' +', Text),
        ]
    }
