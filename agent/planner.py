"""Planning module for decomposing GAIA tasks into executable steps."""

import re
from typing import Dict, List, Optional, Any


class Planner:
    """Decomposes GAIA problems into ordered reasoning steps.
    
    The planner analyzes the problem statement and determines:
    1. What information needs to be extracted
    2. What computations are required
    3. What tools should be used
    4. The order of operations
    """
    
    def __init__(self, seed: Optional[int] = None):
        """Initialize planner.
        
        Args:
            seed: Random seed for deterministic behavior (if needed)
        """
        self.seed = seed
    
    def plan(self, problem: str) -> Dict[str, Any]:
        """Create an execution plan for a GAIA problem.
        
        Args:
            problem: The GAIA problem statement
            
        Returns:
            Dictionary containing:
            - steps: List of ordered execution steps
            - requires_tools: Boolean indicating if tools are needed
            - reasoning: Brief explanation of the plan
        """
        steps = []
        requires_tools = False
        
        # Analyze problem to identify mathematical operations
        math_patterns = self._identify_math_operations(problem)
        
        if math_patterns:
            requires_tools = True
            
            # Create steps for each mathematical operation
            for i, pattern in enumerate(math_patterns):
                step = {
                    'step_id': i + 1,
                    'type': 'computation',
                    'description': f"Compute: {pattern['expression']}",
                    'tool': 'calculator',
                    'expression': pattern['expression'],
                    'context': pattern.get('context', ''),
                    'use_previous_result': pattern.get('use_previous_result', False)
                }
                steps.append(step)
        
        # Check if problem requires extraction of numbers
        numbers = self._extract_numbers(problem)
        if numbers and not steps:
            # If we found numbers but no explicit operations, create a step to identify them
            step = {
                'step_id': 1,
                'type': 'extraction',
                'description': f"Extract and identify numbers: {', '.join(numbers)}",
                'numbers': numbers
            }
            steps.append(step)
        
        # If no clear mathematical operations, create a reasoning step
        if not steps:
            step = {
                'step_id': 1,
                'type': 'reasoning',
                'description': 'Analyze problem and determine solution approach',
                'requires_tools': False
            }
            steps.append(step)
        
        return {
            'steps': steps,
            'requires_tools': requires_tools,
            'reasoning': self._generate_reasoning(problem, steps),
            'problem': problem
        }
    
    def _identify_math_operations(self, problem: str) -> List[Dict[str, Any]]:
        """Identify mathematical operations in the problem text.
        
        Returns:
            List of dictionaries with 'expression', 'context', and 'use_previous_result' keys
        """
        operations = []
        
        # First, try to identify sequential operations (multi-step problems)
        sequential_ops = self._identify_sequential_operations(problem)
        if sequential_ops:
            return sequential_ops
        
        # Look for explicit mathematical expressions
        # Pattern: numbers with operators (+, -, *, /, ^, etc.)
        math_expr_pattern = r'(\d+(?:\.\d+)?)\s*([+\-*/^]|plus|minus|times|divided by|multiplied by)\s*(\d+(?:\.\d+)?)'
        matches = re.finditer(math_expr_pattern, problem, re.IGNORECASE)
        
        for match in matches:
            num1 = match.group(1)
            op = match.group(2)
            num2 = match.group(3)
            
            # Convert word operators to symbols
            op_map = {
                'plus': '+',
                'minus': '-',
                'times': '*',
                'multiplied by': '*',
                'divided by': '/'
            }
            op_symbol = op_map.get(op.lower(), op)
            
            expression = f"{num1} {op_symbol} {num2}"
            operations.append({
                'expression': expression,
                'context': match.group(0),
                'use_previous_result': False
            })
        
        # Look for more complex expressions with parentheses
        complex_pattern = r'\([^)]*\d+[^)]*\)'
        complex_matches = re.finditer(complex_pattern, problem)
        for match in complex_matches:
            expr = match.group(0).strip('()')
            # Try to parse as mathematical expression
            if re.search(r'\d+\s*[+\-*/]\s*\d+', expr):
                operations.append({
                    'expression': expr,
                    'context': match.group(0),
                    'use_previous_result': False
                })
        
        # Look for "calculate", "compute", "find" followed by expressions
        calc_patterns = [
            r'(?:calculate|compute|find|what is|evaluate)\s+([^?.!]+)',
            r'([\d\s+\-*/()]+)\s*=\s*\?'
        ]
        
        for pattern in calc_patterns:
            matches = re.finditer(pattern, problem, re.IGNORECASE)
            for match in matches:
                expr = match.group(1).strip()
                if re.search(r'\d', expr) and re.search(r'[+\-*/]', expr):
                    operations.append({
                        'expression': expr,
                        'context': match.group(0),
                        'use_previous_result': False
                    })
        
        return operations
    
    def _identify_sequential_operations(self, problem: str) -> List[Dict[str, Any]]:
        """Identify sequential operations like 'X then Y', 'X and then Y', etc.
        
        Returns:
            List of operations with 'use_previous_result' flag set appropriately
        """
        operations = []
        
        # Patterns for sequential operations
        # Examples: "15 multiplied by 7, then add 23"
        #           "calculate 10 + 5, then multiply by 2"
        #           "find 20 divided by 4, and then subtract 3"
        
        sequential_patterns = [
            # Pattern: "X, then Y" or "X then Y"
            r'([^,]+?)\s*,\s*then\s+([^?.!]+)',
            r'([^,]+?)\s+then\s+([^?.!]+)',
            # Pattern: "X, and then Y"
            r'([^,]+?)\s*,\s*and\s+then\s+([^?.!]+)',
            # Pattern: "X, after that Y"
            r'([^,]+?)\s*,\s*after\s+that\s+([^?.!]+)',
            # Pattern: "first X, then Y"
            r'first\s+([^,]+?)\s*,\s*then\s+([^?.!]+)',
        ]
        
        for pattern in sequential_patterns:
            match = re.search(pattern, problem, re.IGNORECASE)
            if match:
                first_part = match.group(1).strip()
                second_part = match.group(2).strip()
                
                # Extract first operation
                first_op = self._extract_single_operation(first_part)
                if first_op:
                    first_op['use_previous_result'] = False
                    operations.append(first_op)
                
                # Extract second operation (may use result from first)
                second_op = self._extract_single_operation(second_part, use_previous=True)
                if second_op:
                    operations.append(second_op)
                
                if operations:
                    return operations
        
        return []
    
    def _extract_single_operation(self, text: str, use_previous: bool = False) -> Optional[Dict[str, Any]]:
        """Extract a single mathematical operation from text.
        
        Args:
            text: Text containing the operation
            use_previous: Whether this operation should use the previous result
            
        Returns:
            Dictionary with operation details or None
        """
        # Remove common prefixes
        text = re.sub(r'^(then|and then|after that|next)\s+', '', text, flags=re.IGNORECASE)
        text = text.strip()
        
        # Pattern for word-based operations: "add 23", "multiply by 2", "subtract 5"
        word_op_patterns = [
            (r'add\s+(\d+(?:\.\d+)?)', '+', use_previous),
            (r'subtract\s+(\d+(?:\.\d+)?)', '-', use_previous),
            (r'multiply\s+by\s+(\d+(?:\.\d+)?)', '*', use_previous),
            (r'divide\s+by\s+(\d+(?:\.\d+)?)', '/', use_previous),
            (r'divided\s+by\s+(\d+(?:\.\d+)?)', '/', use_previous),
        ]
        
        for pattern, op_symbol, use_prev in word_op_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                num = match.group(1)
                if use_prev:
                    # This will use previous result, so expression is just the operation
                    expression = f"PREV {op_symbol} {num}"
                else:
                    # Need to find the first number in context
                    first_num_match = re.search(r'(\d+(?:\.\d+)?)', text)
                    if first_num_match:
                        first_num = first_num_match.group(1)
                        expression = f"{first_num} {op_symbol} {num}"
                    else:
                        expression = f"PREV {op_symbol} {num}"
                
                return {
                    'expression': expression,
                    'context': match.group(0),
                    'use_previous_result': use_prev
                }
        
        # Pattern for explicit operations: "15 * 7", "10 + 5"
        explicit_pattern = r'(\d+(?:\.\d+)?)\s*([+\-*/]|plus|minus|times|multiplied by|divided by)\s*(\d+(?:\.\d+)?)'
        match = re.search(explicit_pattern, text, re.IGNORECASE)
        if match:
            num1 = match.group(1)
            op = match.group(2)
            num2 = match.group(3)
            
            op_map = {
                'plus': '+',
                'minus': '-',
                'times': '*',
                'multiplied by': '*',
                'divided by': '/'
            }
            op_symbol = op_map.get(op.lower(), op)
            
            if use_previous:
                expression = f"PREV {op_symbol} {num2}"
            else:
                expression = f"{num1} {op_symbol} {num2}"
            
            return {
                'expression': expression,
                'context': match.group(0),
                'use_previous_result': use_previous
            }
        
        return None
    
    def _extract_numbers(self, problem: str) -> List[str]:
        """Extract all numbers from the problem text."""
        # Find all numbers (integers and decimals)
        number_pattern = r'\d+\.?\d*'
        numbers = re.findall(number_pattern, problem)
        return list(set(numbers))  # Return unique numbers
    
    def _generate_reasoning(self, problem: str, steps: List[Dict]) -> str:
        """Generate a brief explanation of the plan."""
        if not steps:
            return "No clear plan identified."
        
        step_descriptions = [f"Step {s['step_id']}: {s['description']}" for s in steps]
        return "Plan: " + " -> ".join([s['description'] for s in steps])
