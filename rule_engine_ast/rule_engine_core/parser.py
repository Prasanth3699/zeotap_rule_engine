from .ast_node import Node
from typing import Iterator, Tuple, Optional, Union

class ParseError(Exception):
    """Custom exception for parser errors."""
    pass

VALID_ATTRIBUTES = {'age', 'department', 'salary', 'experience','performance_score'}

class Parser:
    """
    Recursive descent parser for the rule language.
    """
    def __init__(self, tokens: Iterator[Tuple[str, Union[str, float]]]):
        self.tokens = iter(tokens)
        self.current_token: Optional[Tuple[str, Union[str, float]]] = None
        self.next_token()
    
    def next_token(self):
        try:
            self.current_token = next(self.tokens)
        except StopIteration:
            self.current_token = None
    
    def parse(self) -> Optional[Node]:
        if self.current_token is None:
            return None
        node = self.expression()
        if self.current_token is not None:
            raise ParseError(f'Unexpected token {self.current_token} at end of expression')
        return node
    
    def match(self, expected_type: str) -> Tuple[str, Union[str, float]]:
        if self.current_token and self.current_token[0] == expected_type:
            token = self.current_token
            self.next_token()
            return token
        else:
            current = self.current_token if self.current_token else 'EOF'
            raise ParseError(f'Expected {expected_type}, got {current}')
    
    def expression(self) -> Node:
        node = self.term()
        while self.current_token and self.current_token[0] == 'OR':
            self.match('OR')
            right = self.term()
            node = Node('operator', value='OR', left=node, right=right)
        return node
    
    def term(self) -> Node:
        node = self.factor()
        while self.current_token and self.current_token[0] == 'AND':
            self.match('AND')
            right = self.factor()
            node = Node('operator', value='AND', left=node, right=right)
        return node
    
    def factor(self) -> Node:
        if self.current_token and self.current_token[0] == 'LPAREN':
            self.match('LPAREN')
            node = self.expression()
            self.match('RPAREN')
            return node
        else:
            return self.comparison()
    
    def comparison(self) -> Node:
        identifier_token = self.match('IDENTIFIER')
        identifier = identifier_token[1]
        if identifier not in VALID_ATTRIBUTES:
            raise ParseError(f'Invalid attribute: {identifier}')
        operator_token = self.match('COMPARISON')
        operator = operator_token[1]
        if self.current_token is None:
            raise ParseError('Unexpected end of input, expected NUMBER or STRING')
        if self.current_token[0] == 'NUMBER':
            value = self.match('NUMBER')[1]
        elif self.current_token[0] == 'STRING':
            value = self.match('STRING')[1]
        else:
            raise ParseError(f"Expected NUMBER or STRING, got {self.current_token[0]}")
        condition = {'identifier': identifier, 'operator': operator, 'value': value}
        return Node('operand', value=condition)
