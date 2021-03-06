# coding:utf8


import six

from ply import lex

from fastweb.exception import ThriftParserError


__all__ = ['Lexer']


THRIFT_KEYWORDS = (
    'namespace',
    'include',
    'void',
    'bool',
    'byte',
    'i8',
    'i16',
    'i32',
    'i64',
    'double',
    'string',
    'binary',
    'map',
    'list',
    'set',
    'oneway',
    'typedef',
    'struct',
    'union',
    'exception',
    'extends',
    'throws',
    'service',
    'enum',
    'const',
    'required',
    'optional',
    'true',
    'false',
)


class LexerSpec(object):
    """Lexer specification for Thrift IDL files.

    Adapted from thriftpy.parser.lexer."""

    literals = ':;,=*{}()<>[]'

    tokens = (
        'INTCONSTANT',
        'DUBCONSTANT',
        'LITERAL',
        'IDENTIFIER',
    ) + tuple(map(six.text_type.upper, THRIFT_KEYWORDS))

    t_ignore = ' \t\r'  # whitespace

    def t_error(self, t):
        raise ThriftParserError(
            'Illegal characher %r at line %d' % (t.value[0], t.lexer.lineno)
        )

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_ignore_SILLYCOMM(self, t):
        r'\/\*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_MULTICOMM(self, t):
        r'\/\*[^*]\/*([^*/]|[^*]\/|\*[^/])*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_DOCTEXT(self, t):
        r'\/\*\*([^*/]|[^*]\/|\*[^/])*\**\*\/'
        t.lexer.lineno += t.value.count('\n')

    def t_ignore_UNIXCOMMENT(self, t):
        r'\#[^\n]*'

    def t_ignore_COMMENT(self, t):
        r'\/\/[^\n]*'

    def t_DUBCONSTANT(self, t):
        r'-?\d+\.\d*(e-?\d+)?'
        t.value = float(t.value)
        return t

    def t_HEXCONSTANT(self, t):
        r'0x[0-9A-Fa-f]+'
        t.value = int(t.value, 16)
        t.type = 'INTCONSTANT'
        return t

    def t_INTCONSTANT(self, t):
        r'[+-]?[0-9]+'
        t.value = int(t.value)
        return t

    def t_LITERAL(self, t):
        r'(\"([^\\\n]|(\\.))*?\")|\'([^\\\n]|(\\.))*?\''
        s = t.value[1:-1]
        maps = {
            't': '\t',
            'r': '\r',
            'n': '\n',
            '\\': '\\',
            '\'': '\'',
            '"': '\"'
        }
        i = 0
        length = len(s)
        val = ''
        while i < length:
            if s[i] == '\\':
                i += 1
                if s[i] in maps:
                    val += maps[s[i]]
                else:
                    msg = 'Cannot escape character: %s' % s[i]
                    raise ThriftParserError(msg)
            else:
                val += s[i]
            i += 1

        t.value = val
        return t

    def t_IDENTIFIER(self, t):
        r'[a-zA-Z_](\.[a-zA-Z_0-9]|[a-zA-Z_0-9])*'

        if t.value in THRIFT_KEYWORDS:
            # Not an identifier after all.
            t.type = t.value.upper()

        return t


class Lexer(LexerSpec):
    """Lexer for Thrift IDL files."""

    def __init__(self, **kwargs):
        self._lexer = lex.lex(module=self, **kwargs)

    def input(self, data):
        """Reset the lexer and feed in new input.

        :param data:
            String of input data.
        """
        # input(..) doesn't reset the lineno. We have to do that manually.
        self._lexer.lineno = 1
        return self._lexer.input(data)

    def token(self):
        """Return the next token.

        Returns None when the end of the input is reached.
        """
        return self._lexer.token()
