from pygments.lexer import RegexLexer
from pygments.token import Token
class MyExtendedLexer(RegexLexer):
    tokens = {
        'root': [
            (r'\{', Token.Punctuation, 'nested'),
        ],
        'nested': [
            (r'\}', Token.Punctuation, '#pop'),
        ]
    }

lexer = MyExtendedLexer()
tokens = list(lexer.get_tokens_unprocessed("{ }", stack=('root','nested')))
