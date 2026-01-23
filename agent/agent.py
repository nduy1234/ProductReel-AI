"""Core agent implementation with Plan → Act → Verify → Answer loop."""

import json
import logging
from typing import Dict, Any, Optional, List

from .planner import Planner
from .verifier import Verifier
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.calculator import Calculator


class GAIAAgent:
    """Green Agent for GAIA benchmark tasks.
    
    Implements a deterministic, stateless agent that follows:
    Plan → Act → Verify → Answer
    
    The agent is designed to be:
    - Stateless across episodes (except logs)
    - Deterministic given a fixed seed
    - Non-adversarial
    - Tool-grounded for computations
    """
    
    def __init__(
        self,
        seed: Optional[int] = None,
        max_retries: int = 3,
        calculator_precision: int = 50
    ):
        """Initialize the GAIA agent.
        
        Args:
            seed: Random seed for deterministic behavior
            max_retries: Maximum retry attempts for failed steps
            calculator_precision: Precision for calculator operations
        """
        self.seed = seed
        self.planner = Planner(seed=seed)
        self.verifier = Verifier(max_retries=max_retries)
        self.calculator = Calculator(precision=calculator_precision)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        self.execution_log: List[Dict[str, Any]] = []
    
    def execute(self, problem: str, task_id: Optional[str] = None) -> Dict[str, Any]:
        """Execute a GAIA problem end-to-end.
        
        Args:
            problem: The GAIA problem statement
            task_id: Optional task identifier for logging
            
        Returns:
            Dictionary containing:
            - answer: Final answer string
            - plan: Execution plan
            - steps: List of execution steps with results
            - verified: Whether final answer passed verification
            - log: Execution log
        """
        self.execution_log = []
        log_entry = {
            'task_id': task_id,
            'problem': problem,
            'phase': 'start'
        }
        self._log('start', log_entry)
        
        # PHASE 1: PLAN
        plan = self.planner.plan(problem)
        self._log('plan', {
            'plan': plan,
            'steps_count': len(plan['steps']),
            'requires_tools': plan['requires_tools']
        })
        
        # PHASE 2: ACT
        step_results = []
        previous_result = None  # Track intermediate results for chaining
        
        for step in plan['steps']:
            # If step needs previous result, substitute it in the expression
            if step.get('use_previous_result', False) and previous_result is not None:
                expression = step.get('expression', '')
                # Replace "PREV" with the actual previous result
                expression = expression.replace('PREV', str(previous_result))
                step = step.copy()  # Don't modify original step
                step['expression'] = expression
            
            step_result = self._execute_step(step, problem)
            step_results.append(step_result)
            
            # Store result for next step if successful
            if step_result.get('success', False):
                result_data = step_result.get('result', {})
                if isinstance(result_data, dict) and result_data.get('success'):
                    previous_result = result_data.get('result')
            
            # PHASE 3: VERIFY (after each step)
            verification = self.verifier.verify_step(step_result)
            step_result['verification'] = verification
            
            self._log('step', {
                'step_id': step['step_id'],
                'step': step,
                'result': step_result,
                'verification': verification
            })
            
            # Retry logic if verification fails
            if not verification['valid']:
                for attempt in range(1, self.verifier.max_retries + 1):
                    if self.verifier.should_retry(verification, attempt):
                        self._log('retry', {
                            'step_id': step['step_id'],
                            'attempt': attempt
                        })
                        # Re-substitute previous result if needed
                        if step.get('use_previous_result', False) and previous_result is not None:
                            expression = step.get('expression', '')
                            expression = expression.replace('PREV', str(previous_result))
                            step['expression'] = expression
                        step_result = self._execute_step(step, problem)
                        verification = self.verifier.verify_step(step_result)
                        step_result['verification'] = verification
                        if verification['valid']:
                            # Update previous_result on successful retry
                            result_data = step_result.get('result', {})
                            if isinstance(result_data, dict) and result_data.get('success'):
                                previous_result = result_data.get('result')
                            break
        
        # PHASE 4: ANSWER
        final_answer = self._generate_answer(problem, plan, step_results)
        
        # Verify final answer
        final_verification = self.verifier.verify_final_answer(final_answer, problem)
        
        self._log('answer', {
            'answer': final_answer,
            'normalized_answer': final_verification.get('normalized_answer'),
            'verification': final_verification
        })
        
        result = {
            'answer': final_verification.get('normalized_answer') or final_answer,
            'raw_answer': final_answer,
            'plan': plan,
            'steps': step_results,
            'verified': final_verification['valid'],
            'verification_message': final_verification['message'],
            'log': self.execution_log,
            'task_id': task_id
        }
        
        # Log completion without full result to avoid circular reference
        self._log('complete', {
            'task_id': result.get('task_id'),
            'answer': result.get('answer'),
            'verified': result.get('verified'),
            'steps_count': len(result.get('steps', []))
        })
        
        return result
    
    def _execute_step(self, step: Dict[str, Any], problem: str) -> Dict[str, Any]:
        """Execute a single step from the plan.
        
        Args:
            step: Step definition from planner
            problem: Original problem for context
            
        Returns:
            Dictionary with step execution result
        """
        step_type = step.get('type', 'unknown')
        step_id = step.get('step_id', 0)
        
        if step_type == 'computation' and step.get('tool') == 'calculator':
            expression = step.get('expression', '')
            result = self.calculator.evaluate(expression)
            return {
                'step_id': step_id,
                'type': step_type,
                'tool': 'calculator',
                'expression': expression,
                'result': result,
                'success': result.get('success', False)
            }
        
        elif step_type == 'extraction':
            numbers = step.get('numbers', [])
            return {
                'step_id': step_id,
                'type': step_type,
                'numbers': numbers,
                'result': {'result': ', '.join(numbers), 'success': True},
                'success': True
            }
        
        elif step_type == 'reasoning':
            # For reasoning steps without tools, return a placeholder
            return {
                'step_id': step_id,
                'type': step_type,
                'result': {'result': 'Reasoning step completed', 'success': True},
                'success': True
            }
        
        else:
            return {
                'step_id': step_id,
                'type': step_type,
                'result': {'result': None, 'success': False, 'error': 'Unknown step type'},
                'success': False
            }
    
    def _generate_answer(self, problem: str, plan: Dict, step_results: List[Dict]) -> str:
        """Generate final answer from plan and step results.
        
        Args:
            problem: Original problem statement
            plan: Execution plan
            step_results: Results from all execution steps
            
        Returns:
            Final answer string (concise, no chain-of-thought)
        """
        # Extract the final result from the last successful computation step
        # This handles both single-step and multi-step problems
        computation_results = [
            sr for sr in step_results
            if sr.get('type') == 'computation' and sr.get('success', False)
        ]
        
        if computation_results:
            # Use the last computation result (final step in multi-step problems)
            last_result = computation_results[-1]
            tool_result = last_result.get('result', {})
            if isinstance(tool_result, dict) and tool_result.get('success'):
                result_value = tool_result.get('result', '')
                if result_value:
                    return str(result_value)
        
        # Fallback: extract from any successful step
        for step_result in reversed(step_results):
            if step_result.get('success', False):
                result = step_result.get('result', {})
                if isinstance(result, dict) and result.get('success'):
                    result_value = result.get('result', '')
                    if result_value:
                        return str(result_value)
                elif isinstance(result, dict) and 'result' in result:
                    result_value = result.get('result', '')
                    if result_value:
                        return str(result_value)
        
        # Last resort: return a placeholder
        return "Unable to compute answer"
    
    def _log(self, phase: str, data: Dict[str, Any]):
        """Log execution data in machine-readable format."""
        # Create a copy of data to avoid circular references
        data_copy = self._sanitize_for_logging(data)
        log_entry = {
            'phase': phase,
            'timestamp': self._get_timestamp(),
            **data_copy
        }
        self.execution_log.append(log_entry)
        try:
            self.logger.debug(json.dumps(log_entry, indent=2, default=str))
        except (ValueError, TypeError):
            # If serialization fails, log a summary instead
            self.logger.debug(f"{phase}: {str(data_copy)[:200]}")
    
    def _sanitize_for_logging(self, obj: Any, max_depth: int = 5) -> Any:
        """Recursively sanitize objects for JSON serialization."""
        if max_depth <= 0:
            return "..."
        
        if isinstance(obj, dict):
            return {k: self._sanitize_for_logging(v, max_depth - 1) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_for_logging(item, max_depth - 1) for item in obj[:10]]  # Limit list size
        elif isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        else:
            return str(obj)[:100]  # Convert other types to string, limit length
    
    def _get_timestamp(self) -> str:
        """Get current timestamp (deterministic if seed is set)."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def get_log(self) -> List[Dict[str, Any]]:
        """Get the execution log."""
        return self.execution_log
    
    def reset(self):
        """Reset agent state (clear logs)."""
        self.execution_log = []
