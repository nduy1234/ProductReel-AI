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
        """Evaluate an agent response against ground truth.
        
        Args:
            response: AgentBeats response dictionary
            ground_truth: Ground truth answer (if not in response metadata)
            
        Returns:
            Evaluation result with 'correct' (bool) and 'score' (float)
        """
        answer = response.get('answer', '').strip()
        if ground_truth is None:
            # Try to extract from metadata
            ground_truth = response.get('metadata', {}).get('ground_truth', '')
        
        if not ground_truth:
            return {
                'correct': None,
                'score': 0.0,
                'message': 'No ground truth available'
            }
        
        ground_truth = str(ground_truth).strip()
        
        # Normalize answers for comparison
        answer_norm = GAIATask._normalize_for_comparison(answer)
        gt_norm = GAIATask._normalize_for_comparison(ground_truth)
        
        # Exact match
        if answer_norm == gt_norm:
            return {
                'correct': True,
                'score': 1.0,
                'message': 'Exact match'
            }
        
        # Numeric comparison (if both are numbers)
        try:
            answer_num = float(answer_norm)
            gt_num = float(gt_norm)
            if abs(answer_num - gt_num) < 1e-6:
                return {
                    'correct': True,
                    'score': 1.0,
                    'message': 'Numeric match'
                }
        except ValueError:
            pass
        
        # Partial match (contains)
        if gt_norm in answer_norm or answer_norm in gt_norm:
            return {
                'correct': True,
                'score': 0.5,
                'message': 'Partial match'
            }
        
        return {
            'correct': False,
            'score': 0.0,
            'message': 'No match'
        }
    
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
