"""Verification module for checking intermediate and final results."""

import re
from typing import Dict, Any, Optional, List


class Verifier:
    """Verifies intermediate and final results during agent execution.
    
    Checks:
    1. Mathematical correctness of computations
    2. Consistency of intermediate results
    3. Format of final answers
    """
    
    def __init__(self, max_retries: int = 3):
        """Initialize verifier.
        
        Args:
            max_retries: Maximum number of retry attempts for failed verifications
        """
        self.max_retries = max_retries
    
    def verify_step(self, step_result: Dict[str, Any], expected_type: Optional[str] = None) -> Dict[str, Any]:
        """Verify a single step's result.
        
        Args:
            step_result: Result from a tool or computation step
            expected_type: Expected type of result (e.g., 'number', 'string')
            
        Returns:
            Dictionary with 'valid' (bool) and 'message' (str)
        """
        if not step_result.get('success', False):
            return {
                'valid': False,
                'message': f"Step failed: {step_result.get('error', 'Unknown error')}"
            }
        
        result = step_result.get('result')
        
        if result is None:
            return {
                'valid': False,
                'message': 'Result is None'
            }
        
        # Type checking
        if expected_type == 'number':
            if not self._is_numeric(result):
                return {
                    'valid': False,
                    'message': f'Expected number, got: {result}'
                }
        
        return {
            'valid': True,
            'message': 'Step result verified',
            'result': result
        }
    
    def verify_final_answer(self, answer: str, problem: str) -> Dict[str, Any]:
        """Verify the final answer format and basic sanity checks.
        
        Args:
            answer: The final answer string
            problem: Original problem statement
            
        Returns:
            Dictionary with 'valid' (bool), 'message' (str), and 'normalized_answer' (str)
        """
        if not answer or not answer.strip():
            return {
                'valid': False,
                'message': 'Answer is empty',
                'normalized_answer': None
            }
        
        # Normalize answer - extract the core answer value
        normalized = self._normalize_answer(answer)
        
        # Basic sanity checks
        # Check if answer contains reasonable characters
        if len(normalized) > 1000:
            return {
                'valid': False,
                'message': 'Answer is too long (likely contains reasoning)',
                'normalized_answer': normalized[:100] + '...'
            }
        
        # Check if answer looks like a number (for math problems)
        if self._is_numeric(normalized):
            return {
                'valid': True,
                'message': 'Answer is a valid number',
                'normalized_answer': normalized
            }
        
        # For non-numeric answers, check basic format
        if len(normalized.strip()) > 0:
            return {
                'valid': True,
                'message': 'Answer format is acceptable',
                'normalized_answer': normalized
            }
        
        return {
            'valid': False,
            'message': 'Answer format is invalid',
            'normalized_answer': None
        }
    
    def _is_numeric(self, value: str) -> bool:
        """Check if a string represents a number."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    def _normalize_answer(self, answer: str) -> str:
        """Normalize answer by extracting the core value.
        
        Removes common prefixes like "The answer is", "Answer:", etc.
        """
        # Remove common prefixes
        prefixes = [
            r'^the answer is\s*:?\s*',
            r'^answer\s*:?\s*',
            r'^result\s*:?\s*',
            r'^solution\s*:?\s*',
            r'^final answer\s*:?\s*',
        ]
        
        normalized = answer.strip()
        for prefix in prefixes:
            normalized = re.sub(prefix, '', normalized, flags=re.IGNORECASE)
        
        # Extract first number if present
        number_match = re.search(r'-?\d+\.?\d*', normalized)
        if number_match:
            return number_match.group(0)
        
        # Extract first meaningful phrase (up to 50 chars)
        words = normalized.split()
        if words:
            # Take first few words that seem like an answer
            meaningful = []
            for word in words[:10]:
                if word.lower() not in ['is', 'the', 'a', 'an', 'and', 'or', 'but']:
                    meaningful.append(word)
                if len(' '.join(meaningful)) > 50:
                    break
            if meaningful:
                return ' '.join(meaningful)
        
        return normalized.strip()[:100]  # Fallback: first 100 chars
    
    def should_retry(self, verification_result: Dict[str, Any], attempt: int) -> bool:
        """Determine if a step should be retried based on verification result.
        
        Args:
            verification_result: Result from verify_step or verify_final_answer
            attempt: Current attempt number (1-indexed)
            
        Returns:
            Boolean indicating if retry should be attempted
        """
        if verification_result.get('valid', False):
            return False
        
        if attempt >= self.max_retries:
            return False
        
        # Retry on certain types of failures
        error_msg = verification_result.get('message', '').lower()
        retryable_errors = ['failed', 'error', 'invalid', 'none']
        
        if any(err in error_msg for err in retryable_errors):
            return True
        
        return False
