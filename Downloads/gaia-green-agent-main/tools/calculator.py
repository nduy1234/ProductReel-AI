"""Deterministic calculator tool for mathematical operations."""

import decimal
import re
from typing import Any, Dict, Optional


class Calculator:
    """A deterministic calculator that performs exact arithmetic operations.
    
    Uses Python's decimal module for precise arithmetic and supports
    basic mathematical operations with deterministic results.
    """
    
    def __init__(self, precision: int = 50):
        """Initialize calculator with specified precision.
        
        Args:
            precision: Number of decimal places for calculations (default: 50)
        """
        self.precision = precision
        decimal.getcontext().prec = precision
    
    def evaluate(self, expression: str) -> Dict[str, Any]:
        """Evaluate a mathematical expression with robust error handling.
        
        Uses a safe, custom parser to avoid eval() security vulnerabilities.
        Supports basic arithmetic operations with operator precedence.
        
        Args:
            expression: Mathematical expression as a string (e.g., "2 + 3 * 4")
            
        Returns:
            Dictionary with:
            - 'result' (str): Result as string, or None if failed
            - 'success' (bool): Whether evaluation succeeded
            - 'error' (str): Error message if failed (optional)
            - 'expression' (str): Original expression
            
        Examples:
            >>> calc = Calculator()
            >>> calc.evaluate("2 + 3 * 4")
            {'result': '14', 'success': True, 'expression': '2 + 3 * 4'}
            >>> calc.evaluate("(2 + 3) * 4")
            {'result': '20', 'success': True, 'expression': '(2 + 3) * 4'}
        """
        if not expression or not expression.strip():
            return {
                'result': None,
                'success': False,
                'error': 'Empty expression',
                'expression': expression
            }
        
        try:
            # Sanitize expression - only allow safe characters
            sanitized = self._sanitize_expression(expression)
            
            # Replace common math functions with safe alternatives
            sanitized = self._replace_functions(sanitized)
            
            # Evaluate using decimal for precision
            result = self._safe_eval(sanitized)
            
            # Format result as string with appropriate precision
            if isinstance(result, decimal.Decimal):
                result_str = str(result)
            else:
                result_str = str(result)
            
            return {
                'result': result_str,
                'success': True,
                'expression': expression
            }
        except ValueError as e:
            return {
                'result': None,
                'success': False,
                'error': f'Invalid expression: {str(e)}',
                'expression': expression
            }
        except ZeroDivisionError as e:
            return {
                'result': None,
                'success': False,
                'error': 'Division by zero',
                'expression': expression
            }
        except Exception as e:
            return {
                'result': None,
                'success': False,
                'error': f'Evaluation error: {str(e)}',
                'expression': expression
            }
    
    def _sanitize_expression(self, expr: str) -> str:
        """Remove potentially dangerous characters from expression.
        
        Uses fullmatch() to ensure the entire expression contains only
        allowed characters, preventing code injection or unexpected behavior.
        This is a security-critical function that validates the entire string.
        """
        # Allow: digits, operators, parentheses, decimal points, spaces, and common math symbols
        # Also allow "PREV" placeholder for multi-step operations (will be replaced before evaluation)
        # Remove spaces and PREV for validation, then check entire string
        expr_clean = expr.replace(' ', '').replace('PREV', '')
        allowed = re.compile(r'^[0-9+\-*/().,]+$')
        if not allowed.fullmatch(expr_clean):
            raise ValueError(f"Expression contains invalid characters: {expr}")
        return expr
    
    def _replace_functions(self, expr: str) -> str:
        """Replace common mathematical functions with safe implementations."""
        # For now, we'll handle basic arithmetic
        # More complex functions can be added via sympy wrapper if needed
        return expr
    
    def _safe_eval(self, expr: str) -> decimal.Decimal:
        """Safely evaluate expression using decimal arithmetic.
        
        Uses a simple recursive descent parser to avoid eval() security issues.
        """
        # Remove whitespace
        expr = expr.replace(' ', '')
        
        # Use a simple tokenizer and parser
        tokens = self._tokenize(expr)
        result = self._parse_expression(tokens)
        return result
    
    def _tokenize(self, expr: str) -> list:
        """Tokenize expression into numbers and operators."""
        tokens = []
        i = 0
        while i < len(expr):
            if expr[i].isdigit() or expr[i] == '.':
                # Parse number
                num_str = ''
                while i < len(expr) and (expr[i].isdigit() or expr[i] == '.'):
                    num_str += expr[i]
                    i += 1
                tokens.append(('NUMBER', decimal.Decimal(num_str)))
            elif expr[i] in '+-*/()':
                tokens.append(('OP', expr[i]))
                i += 1
            else:
                raise ValueError(f"Unexpected character: {expr[i]}")
        return tokens
    
    def _parse_expression(self, tokens: list) -> decimal.Decimal:
        """Parse tokens into an expression tree and evaluate."""
        if not tokens:
            raise ValueError("Empty expression")
        
        # Handle parentheses first
        tokens = self._handle_parentheses(tokens)
        
        # Evaluate with operator precedence: */ before +-
        result = self._evaluate_with_precedence(tokens)
        return result
    
    def _handle_parentheses(self, tokens: list) -> list:
        """Handle parentheses by recursively evaluating sub-expressions."""
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i][0] == 'OP' and tokens[i][1] == '(':
                # Find matching closing parenthesis
                depth = 1
                j = i + 1
                while j < len(tokens) and depth > 0:
                    if tokens[j][0] == 'OP' and tokens[j][1] == '(':
                        depth += 1
                    elif tokens[j][0] == 'OP' and tokens[j][1] == ')':
                        depth -= 1
                    j += 1
                
                if depth != 0:
                    raise ValueError("Unmatched parentheses")
                
                # Evaluate sub-expression
                sub_tokens = tokens[i+1:j-1]
                sub_result = self._evaluate_with_precedence(sub_tokens)
                result.append(('NUMBER', sub_result))
                i = j
            else:
                result.append(tokens[i])
                i += 1
        return result
    
    def _evaluate_with_precedence(self, tokens: list) -> decimal.Decimal:
        """Evaluate expression respecting operator precedence (*/ before +-)."""
        if not tokens:
            raise ValueError("Empty expression")
        
        # First pass: handle * and /
        result = []
        i = 0
        while i < len(tokens):
            if tokens[i][0] == 'NUMBER':
                if i + 1 < len(tokens) and tokens[i+1][0] == 'OP' and tokens[i+1][1] in '*/':
                    # Binary operation
                    op = tokens[i+1][1]
                    left = tokens[i][1]
                    right = tokens[i+2][1] if i+2 < len(tokens) and tokens[i+2][0] == 'NUMBER' else None
                    if right is None:
                        raise ValueError(f"Missing operand for {op}")
                    
                    if op == '*':
                        result.append(('NUMBER', left * right))
                    else:  # /
                        if right == 0:
                            raise ValueError("Division by zero")
                        result.append(('NUMBER', left / right))
                    i += 3
                else:
                    result.append(tokens[i])
                    i += 1
            elif tokens[i][0] == 'OP' and tokens[i][1] in '+-':
                result.append(tokens[i])
                i += 1
            else:
                i += 1
        
        # Second pass: handle + and -
        if not result:
            raise ValueError("No result after multiplication/division")
        
        value = result[0][1] if result[0][0] == 'NUMBER' else decimal.Decimal('0')
        i = 1
        while i < len(result):
            if result[i][0] == 'OP':
                op = result[i][1]
                if i + 1 < len(result) and result[i+1][0] == 'NUMBER':
                    right = result[i+1][1]
                    if op == '+':
                        value = value + right
                    else:  # -
                        value = value - right
                    i += 2
                else:
                    raise ValueError(f"Missing operand for {op}")
            else:
                i += 1
        
        return value
    
    def add(self, a: str, b: str) -> Dict[str, Any]:
        """Add two numbers."""
        try:
            result = decimal.Decimal(a) + decimal.Decimal(b)
            return {'result': str(result), 'success': True}
        except Exception as e:
            return {'result': None, 'success': False, 'error': str(e)}
    
    def subtract(self, a: str, b: str) -> Dict[str, Any]:
        """Subtract b from a."""
        try:
            result = decimal.Decimal(a) - decimal.Decimal(b)
            return {'result': str(result), 'success': True}
        except Exception as e:
            return {'result': None, 'success': False, 'error': str(e)}
    
    def multiply(self, a: str, b: str) -> Dict[str, Any]:
        """Multiply two numbers."""
        try:
            result = decimal.Decimal(a) * decimal.Decimal(b)
            return {'result': str(result), 'success': True}
        except Exception as e:
            return {'result': None, 'success': False, 'error': str(e)}
    
    def divide(self, a: str, b: str) -> Dict[str, Any]:
        """Divide a by b."""
        try:
            if decimal.Decimal(b) == 0:
                return {'result': None, 'success': False, 'error': 'Division by zero'}
            result = decimal.Decimal(a) / decimal.Decimal(b)
            return {'result': str(result), 'success': True}
        except Exception as e:
            return {'result': None, 'success': False, 'error': str(e)}
    
    def power(self, a: str, b: str) -> Dict[str, Any]:
        """Raise a to the power of b."""
        try:
            result = decimal.Decimal(a) ** decimal.Decimal(b)
            return {'result': str(result), 'success': True}
        except Exception as e:
            return {'result': None, 'success': False, 'error': str(e)}
