from .tokenizer import tokenize, TokenizationError
from .parser import Parser, ParseError, VALID_ATTRIBUTES
from .ast_node import Node
from typing import List, Optional, Dict, Any, Tuple

class EvaluationError(Exception):
    """Custom exception for evaluation errors."""
    pass

# def create_rule(rule_string: str) -> Optional[Node]:
#     tokens = tokenize(rule_string)
#     print(f"Tokens generated: {tokens}")
#     parser = Parser(tokens)
#     try:
#         ast = parser.parse()
#         return ast
#     except (ParseError, TokenizationError) as e:
#         raise ParseError(f"Error parsing rule: {e}")

def create_rule(rule_string: str) -> Optional[Node]:
    print(f"Creating rule with string: {rule_string}")  # Debugging line
    
    # Handle empty or whitespace strings
    if not rule_string.strip():
        raise ParseError("Rule string cannot be empty or just whitespace.")
    
    try:
        tokens = tokenize(rule_string)
        print(f"Tokens: {tokens}")  # Debugging line
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if ast is None:
            raise ParseError("AST generation failed; rule string might be invalid.")
        
        print(f"Generated AST: {ast}")  # Debugging line
        return ast
    
    except (ParseError, TokenizationError) as e:
        print(f"Error parsing rule: {e}")  # Debugging line
        raise ParseError(f"Error parsing rule: {e}")


def combine_rules(rule_strings: List[str], operator: str = 'OR') -> Optional[Node]:
    if operator not in {'AND', 'OR'}:
        raise ValueError(f"Invalid operator '{operator}'. Only 'AND' and 'OR' are supported.")
    
    # Create ASTs from rule strings
    asts = [create_rule(rs) for rs in rule_strings]
    print(f"Generated ASTs: {asts}")  # Debugging line
    
    if not asts:
        return None

    # Combine ASTs using the provided operator
    combined_ast = asts[0]
    for ast in asts[1:]:
        combined_ast = Node('operator', value=operator, left=combined_ast, right=ast)
    
    print(f"Combined AST: {combined_ast}")  # Debugging line
    return combined_ast


def ast_to_json(node: Optional[Node]) -> Optional[Dict[str, Any]]:
    if node is None:
        return None
    return {
        'type': node.type,
        'value': node.value,
        'left': ast_to_json(node.left),
        'right': ast_to_json(node.right)
    }

def json_to_ast(data: Optional[Dict[str, Any]]) -> Optional[Node]:
    if data is None:
        return None
    node = Node(
        node_type=data['type'],
        value=data['value'],
        left=json_to_ast(data.get('left')),
        right=json_to_ast(data.get('right'))
    )
    return node


def evaluate_node_with_details(node: Node, data: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    details = {}
    if node.type == 'operator':
        left_result, left_details = evaluate_node_with_details(node.left, data)
        right_result, right_details = evaluate_node_with_details(node.right, data)
        if node.value == 'AND':
            result = left_result and right_result
        elif node.value == 'OR':
            result = left_result or right_result
        details.update(left_details)
        details.update(right_details)
        return result, details
    elif node.type == 'operand':
        identifier = node.value['identifier']
        operator = node.value['operator']
        expected_value = node.value['value']
        condition = f"{identifier} {operator} {repr(expected_value)}"
        if identifier not in data:
            details[condition] = False
            return False, details
        data_value = data[identifier]
        # Type checking and conversion
        if isinstance(expected_value, str):
            data_value = str(data_value)
            compare_value = expected_value
        elif isinstance(expected_value, (int, float)):
            try:
                compare_value = float(expected_value)
                data_value = float(data_value)
            except (ValueError, TypeError):
                details[condition] = False
                return False, details
        else:
            details[condition] = False
            return False, details
        # Define comparison operations
        if operator == '>':
            result = data_value > compare_value
        elif operator == '>=':
            result = data_value >= compare_value
        elif operator == '<':
            result = data_value < compare_value
        elif operator == '<=':
            result = data_value <= compare_value
        elif operator in {'==', '='}:
            result = data_value == compare_value
        elif operator == '!=':
            result = data_value != compare_value
        else:
            result = False
        details[condition] = result
        return result, details
    
    else:
        return False, {}

def evaluate_rule_with_details(ast: Node, data: Dict[str, Any]) -> Tuple[bool, Dict[str, bool]]:
    try:
        result, details = evaluate_node_with_details(ast, data)
        return result, details
    except EvaluationError as e:
        raise EvaluationError(f"Error during evaluation: {e}")




def evaluate_rule(ast: Node, data: Dict[str, Any]) -> bool:
    try:
        return evaluate_node(ast, data)
    except EvaluationError as e:
        raise EvaluationError(f"Error during evaluation: {e}")
