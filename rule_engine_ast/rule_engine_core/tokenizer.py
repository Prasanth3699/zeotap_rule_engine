import re
from typing import Iterator, Tuple, Union

class TokenizationError(Exception):
    """Custom exception for tokenizer errors."""
    pass

def tokenize(code: str) -> Iterator[Tuple[str, Union[str, float]]]:
    token_specification = [
        ('NUMBER',     r'\d+(\.\d*)?'),              # Integer or decimal number
        ('STRING',     r"'[^']*'"),                  # String enclosed in single quotes
        ('AND',        r'\bAND\b'),                  # AND operator
        ('OR',         r'\bOR\b'),                   # OR operator
        ('LPAREN',     r'\('),                       # Left Parenthesis
        ('RPAREN',     r'\)'),                       # Right Parenthesis
        ('COMPARISON', r'[><=!]=?'),                 # Comparison operators
        ('IDENTIFIER', r'[A-Za-z_][A-Za-z0-9_]*'),   # Identifiers
        ('SKIP',       r'[ \t\n]+'),                 # Skip over spaces, tabs, and newlines
        ('MISMATCH',   r'.'),                        # Any other character
    ]
    token_regex = '|'.join(f'(?P<{pair[0]}>{pair[1]})' for pair in token_specification)
    get_token = re.compile(token_regex).match
    pos = 0
    mo = get_token(code, pos)
    while mo is not None:
        kind = mo.lastgroup
        value = mo.group()
        if kind == 'NUMBER':
            yield ('NUMBER', float(value))
        elif kind == 'STRING':
            yield ('STRING', value[1:-1])  # Remove the surrounding quotes
        elif kind in ('AND', 'OR', 'LPAREN', 'RPAREN', 'COMPARISON'):
            yield (kind, value)
        elif kind == 'IDENTIFIER':
            yield ('IDENTIFIER', value)
        elif kind == 'SKIP':
            pass  # Ignore whitespace
        elif kind == 'MISMATCH':
            raise TokenizationError(f'Unexpected character: {value} at position {pos}')
        pos = mo.end()
        mo = get_token(code, pos)
    if pos != len(code):
        raise TokenizationError(f'Unexpected character {code[pos]!r} at position {pos}')
