"""AgentBeats-compatible task wrapper for GAIA problems."""

from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class AgentBeatsTask:
    """AgentBeats-compatible task definition.
    
    This follows the AgentBeats A2A protocol for task management.
    """
    task_id: str
    task_type: str
    prompt: str
    metadata: Dict[str, Any]
    ground_truth: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentBeatsTask':
        """Create from dictionary."""
        return cls(**data)


class GAIATask:
    """Wrapper to convert GAIA problems to AgentBeats tasks."""
    
    @staticmethod
    def from_gaia(gaia_task: Dict[str, Any]) -> AgentBeatsTask:
        """Convert a GAIA task to an AgentBeats task.
        
        Args:
            gaia_task: GAIA task dictionary from GAIALoader
            
        Returns:
            AgentBeatsTask instance
        """
        return AgentBeatsTask(
            task_id=gaia_task.get('task_id', ''),
            task_type='gaia_math',  # Can be extended for other types
            prompt=gaia_task.get('question', ''),
            metadata={
                'level': gaia_task.get('level', ''),
                'file_name': gaia_task.get('file_name', ''),
                'file_path': gaia_task.get('file_path', ''),
                'original_metadata': gaia_task.get('metadata', {})
            },
            ground_truth=gaia_task.get('final_answer', '')
        )
    
    @staticmethod
    def to_agentbeats_response(agent_result: Dict[str, Any]) -> Dict[str, Any]:
        """Convert agent execution result to AgentBeats response format.
        
        Args:
            agent_result: Result from GAIAAgent.execute()
            
        Returns:
            AgentBeats-compatible response dictionary
        """
        return {
            'task_id': agent_result.get('task_id', ''),
            'answer': agent_result.get('answer', ''),
            'verified': agent_result.get('verified', False),
            'metadata': {
                'plan': agent_result.get('plan', {}),
                'steps_count': len(agent_result.get('steps', [])),
                'verification_message': agent_result.get('verification_message', ''),
                'execution_log': agent_result.get('log', [])
            }
        }
    
    @staticmethod
    def evaluate_response(response: Dict[str, Any], ground_truth: Optional[str] = None) -> Dict[str, Any]:
        """Evaluate an agent response against ground truth with multi-dimensional metrics.
        
        This evaluation goes beyond binary pass/fail to provide nuanced assessment
        across multiple dimensions: accuracy, execution quality, format quality, and efficiency.
        
        Args:
            response: AgentBeats response dictionary
            ground_truth: Ground truth answer (if not in response metadata)
            
        Returns:
            Evaluation result with:
            - 'correct' (bool): Whether answer matches ground truth
            - 'score' (float): Overall score (0.0-1.0)
            - 'message' (str): Evaluation message
            - 'dimensions' (dict): Multi-dimensional metrics
        """
        answer = response.get('answer', '').strip()
        if ground_truth is None:
            # Try to extract from metadata
            ground_truth = response.get('metadata', {}).get('ground_truth', '')
        
        if not ground_truth:
            return {
                'correct': None,
                'score': 0.0,
                'message': 'No ground truth available',
                'dimensions': {}
            }
        
        ground_truth = str(ground_truth).strip()
        
        # Normalize answers for comparison
        answer_norm = GAIATask._normalize_for_comparison(answer)
        gt_norm = GAIATask._normalize_for_comparison(ground_truth)
        
        # Calculate accuracy dimension
        accuracy_score = 0.0
        accuracy_message = 'No match'
        
        # Exact match
        if answer_norm == gt_norm:
            accuracy_score = 1.0
            accuracy_message = 'Exact match'
        # Numeric comparison (if both are numbers)
        elif GAIATask._is_numeric(answer_norm) and GAIATask._is_numeric(gt_norm):
            try:
                answer_num = float(answer_norm)
                gt_num = float(gt_norm)
                if abs(answer_num - gt_num) < 1e-6:
                    accuracy_score = 1.0
                    accuracy_message = 'Numeric match'
            except (ValueError, TypeError):
                pass
        # Partial match (contains)
        if accuracy_score == 0.0:
            if gt_norm in answer_norm or answer_norm in gt_norm:
                accuracy_score = 0.5
                accuracy_message = 'Partial match'
        
        is_correct = accuracy_score >= 0.5
        
        # Calculate execution quality dimension
        metadata = response.get('metadata', {})
        steps = metadata.get('execution_log', [])
        step_results = [s for s in steps if s.get('phase') == 'step']
        
        execution_quality = 1.0
        if step_results:
            successful_steps = sum(1 for s in step_results 
                                if s.get('verification', {}).get('valid', False))
            execution_quality = successful_steps / len(step_results) if step_results else 1.0
        
        # Calculate answer format quality dimension
        format_quality = 1.0
        if not answer or len(answer) > 1000:
            format_quality = 0.0
        elif GAIATask._is_numeric(answer_norm):
            format_quality = 1.0
        elif len(answer_norm.strip()) > 0:
            format_quality = 0.7
        
        # Calculate efficiency metrics
        efficiency = {
            'step_count': metadata.get('steps_count', 0),
            'tool_invocations': sum(1 for s in step_results 
                                  if s.get('step', {}).get('tool') == 'calculator'),
            'retry_count': sum(1 for s in steps if s.get('phase') == 'retry')
        }
        
        # Calculate robustness metrics
        robustness = {
            'completion': True,  # If we got here, task completed
            'step_success_rate': execution_quality,
            'retry_count': efficiency['retry_count'],
            'verified': response.get('verified', False)
        }
        
        # Composite score (weighted combination)
        composite_score = (
            accuracy_score * 0.5 +
            execution_quality * 0.2 +
            format_quality * 0.15 +
            (1.0 if response.get('verified', False) else 0.0) * 0.15
        )
        
        return {
            'correct': is_correct,
            'score': composite_score,
            'message': accuracy_message,
            'dimensions': {
                'accuracy': accuracy_score,
                'execution_quality': execution_quality,
                'answer_format_quality': format_quality,
                'efficiency': efficiency,
                'robustness': robustness
            }
        }
    
    @staticmethod
    def _is_numeric(value: str) -> bool:
        """Check if a string represents a number."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _normalize_for_comparison(text: str) -> str:
        """Normalize text for comparison (lowercase, remove punctuation, etc.)."""
        import re
        # Lowercase
        text = text.lower()
        # Remove common prefixes
        text = re.sub(r'^(the answer is|answer|result|solution):?\s*', '', text)
        # Remove punctuation (except decimal points and minus signs)
        text = re.sub(r'[^\d.\-]', '', text)
        return text.strip()
