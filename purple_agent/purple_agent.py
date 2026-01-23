"""Baseline Purple Agent - A2A-compatible participant agent.

This is a simple purple agent that demonstrates how the Green Agent
evaluates participant agents. It implements the A2A protocol and can
be used as a baseline for evaluation.
"""

import json
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class A2ATask:
    """A2A protocol task structure."""
    task_id: str
    task_type: str
    prompt: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2ATask':
        """Create from dictionary."""
        return cls(**data)


@dataclass
class A2AResponse:
    """A2A protocol response structure."""
    task_id: str
    answer: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class PurpleAgent:
    """Baseline Purple Agent for GAIA evaluation.
    
    This is a simple participant agent that:
    - Accepts tasks via A2A protocol
    - Processes them (can delegate to Green Agent or use simple logic)
    - Returns answers in A2A format
    
    Used to demonstrate how the Green Agent evaluates participant agents.
    """
    
    def __init__(self, use_green_agent: bool = True):
        """Initialize purple agent.
        
        Args:
            use_green_agent: If True, delegates to Green Agent for processing
        """
        self.use_green_agent = use_green_agent
        self.logger = logging.getLogger(__name__)
        
        if use_green_agent:
            # Import Green Agent for delegation
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from agent.agent import GAIAAgent
            self.green_agent = GAIAAgent(seed=42)
        else:
            self.green_agent = None
    
    def process_task(self, task: A2ATask) -> A2AResponse:
        """Process an A2A task and return response.
        
        Args:
            task: A2A protocol task
            
        Returns:
            A2A protocol response
        """
        self.logger.info(f"Processing task: {task.task_id}")
        
        if self.use_green_agent and self.green_agent:
            # Delegate to Green Agent for actual processing
            result = self.green_agent.execute(task.prompt, task_id=task.task_id)
            answer = result.get('answer', '')
            
            metadata = {
                'processed_by': 'green_agent',
                'verified': result.get('verified', False),
                'steps_count': len(result.get('steps', []))
            }
        else:
            # Simple baseline: just echo the prompt (for testing)
            answer = f"Processed: {task.prompt[:50]}..."
            metadata = {
                'processed_by': 'simple_baseline',
                'note': 'This is a minimal baseline agent'
            }
        
        return A2AResponse(
            task_id=task.task_id,
            answer=answer,
            metadata=metadata
        )
    
    def process_task_dict(self, task_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Process task from dictionary format.
        
        Args:
            task_dict: Task as dictionary
            
        Returns:
            Response as dictionary
        """
        task = A2ATask.from_dict(task_dict)
        response = self.process_task(task)
        return response.to_dict()


def create_purple_agent_endpoint():
    """Create a simple HTTP endpoint for A2A protocol (example).
    
    This demonstrates how a purple agent would expose an A2A endpoint.
    In production, this would be a proper web server.
    """
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    agent = PurpleAgent(use_green_agent=True)
    
    @app.route('/a2a/task', methods=['POST'])
    def handle_task():
        """Handle A2A task request."""
        task_data = request.json
        task = A2ATask.from_dict(task_data)
        response = agent.process_task(task)
        return jsonify(response.to_dict())
    
    return app
