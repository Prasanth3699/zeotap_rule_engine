class Node:
    """
    Represents a node in the Abstract Syntax Tree (AST).
    """
    def __init__(self, node_type, value=None, left=None, right=None):
        self.type = node_type  # 'operator' or 'operand'
        self.value = value     # For 'operand', this is the condition dict
        self.left = left       # Left child Node
        self.right = right     # Right child Node

    def __repr__(self):
        if self.type == 'operand':
            return f"Operand({self.value})"
        return f"Operator({self.value}, left={self.left}, right={self.right})"
