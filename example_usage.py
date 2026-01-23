"""Example usage of the GAIA Green Agent.

This script demonstrates how to use the agent with a simple example problem.
"""

import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.agent import GAIAAgent
from tasks.gaia_task import GAIATask


def main():
    """Run example with a simple math problem."""
    
    # Initialize agent
    print("Initializing GAIA Agent...")
    agent = GAIAAgent(seed=42, max_retries=3)
    
    # Example GAIA-style math problem
    problem = "Calculate 15 multiplied by 7, then add 23. What is the result?"
    
    print(f"\nProblem: {problem}\n")
    
    # Execute
    print("Executing agent...")
    result = agent.execute(problem, task_id="example_1")
    
    # Display results
    print("\n" + "="*60)
    print("EXECUTION RESULTS")
    print("="*60)
    print(f"Final Answer: {result['answer']}")
    print(f"Verified: {result['verified']}")
    print(f"Verification Message: {result['verification_message']}")
    print(f"\nPlan: {result['plan']['reasoning']}")
    print(f"\nSteps Executed: {len(result['steps'])}")
    
    for i, step in enumerate(result['steps'], 1):
        print(f"\n  Step {i}: {step.get('type', 'unknown')}")
        if step.get('success'):
            step_result = step.get('result', {})
            if isinstance(step_result, dict):
                print(f"    Result: {step_result.get('result', 'N/A')}")
        else:
            print(f"    Status: Failed")
    
    print("\n" + "="*60)
    print("Full Result (JSON):")
    print("="*60)
    print(json.dumps(result, indent=2, default=str))
    
    # Test with AgentBeats task format
    print("\n" + "="*60)
    print("Testing AgentBeats Task Format")
    print("="*60)
    
    gaia_task_dict = {
        'task_id': 'example_2',
        'question': 'What is 42 divided by 6?',
        'level': '1',
        'final_answer': '7',
        'file_name': '',
        'file_path': '',
        'metadata': {}
    }
    
    agentbeats_task = GAIATask.from_gaia(gaia_task_dict)
    print(f"Task ID: {agentbeats_task.task_id}")
    print(f"Prompt: {agentbeats_task.prompt}")
    print(f"Ground Truth: {agentbeats_task.ground_truth}")
    
    # Execute
    agent_result = agent.execute(agentbeats_task.prompt, task_id=agentbeats_task.task_id)
    response = GAIATask.to_agentbeats_response(agent_result)
    evaluation = GAIATask.evaluate_response(response, agentbeats_task.ground_truth)
    
    print(f"\nAgent Answer: {response['answer']}")
    print(f"Correct: {evaluation['correct']}")
    print(f"Score: {evaluation['score']}")
    print(f"Message: {evaluation['message']}")


if __name__ == '__main__':
    main()
