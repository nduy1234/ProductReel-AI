"""End-to-end evaluation runner for GAIA Green Agent on AgentBeats."""

import argparse
import json
import logging
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.agent import GAIAAgent
from tasks.gaia_loader import GAIALoader
from tasks.gaia_task import GAIATask, AgentBeatsTask


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None):
    """Setup logging configuration."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config


def run_single_task(agent: GAIAAgent, task: AgentBeatsTask) -> Dict[str, Any]:
    """Run a single task through the agent.
    
    Args:
        agent: Initialized GAIAAgent
        task: AgentBeats task to execute
        
    Returns:
        Complete execution result with evaluation
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Executing task: {task.task_id}")
    
    # Execute agent
    result = agent.execute(task.prompt, task_id=task.task_id)
    
    # Convert to AgentBeats response format
    response = GAIATask.to_agentbeats_response(result)
    response['metadata']['ground_truth'] = task.ground_truth
    
    # Evaluate
    evaluation = GAIATask.evaluate_response(response, task.ground_truth)
    
    return {
        'task_id': task.task_id,
        'response': response,
        'evaluation': evaluation,
        'agent_result': result
    }


def run_batch(
    agent: GAIAAgent,
    tasks: List[AgentBeatsTask],
    output_dir: Optional[str] = None,
    max_tasks: Optional[int] = None
) -> Dict[str, Any]:
    """Run a batch of tasks.
    
    Args:
        agent: Initialized GAIAAgent
        tasks: List of tasks to execute
        output_dir: Directory to save results
        max_tasks: Maximum number of tasks to run (None for all)
        
    Returns:
        Summary statistics and results
    """
    logger = logging.getLogger(__name__)
    
    if max_tasks:
        tasks = tasks[:max_tasks]
    
    results = []
    correct_count = 0
    total_count = len(tasks)
    
    for i, task in enumerate(tasks, 1):
        logger.info(f"Processing task {i}/{total_count}: {task.task_id}")
        
        try:
            result = run_single_task(agent, task)
            results.append(result)
            
            if result['evaluation'].get('correct'):
                correct_count += 1
            
            # Save individual result if output_dir specified
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                result_file = os.path.join(output_dir, f"{task.task_id}.json")
                with open(result_file, 'w') as f:
                    json.dump(result, f, indent=2)
        
        except Exception as e:
            logger.error(f"Error processing task {task.task_id}: {e}")
            results.append({
                'task_id': task.task_id,
                'error': str(e),
                'evaluation': {'correct': False, 'score': 0.0}
            })
    
    accuracy = correct_count / total_count if total_count > 0 else 0.0
    
    summary = {
        'total_tasks': total_count,
        'correct': correct_count,
        'incorrect': total_count - correct_count,
        'accuracy': accuracy,
        'results': results
    }
    
    # Save summary
    if output_dir:
        summary_file = os.path.join(output_dir, 'summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Summary saved to {summary_file}")
    
    return summary


def main():
    """Main entry point for evaluation runner."""
    parser = argparse.ArgumentParser(
        description='Run GAIA Green Agent evaluation on AgentBeats'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='configs/gaia_agent.yaml',
        help='Path to configuration file'
    )
    parser.add_argument(
        '--data-source',
        type=str,
        help='Override data source from config'
    )
    parser.add_argument(
        '--data-format',
        type=str,
        choices=['json', 'jsonl', 'parquet', 'huggingface'],
        help='Override data format from config'
    )
    parser.add_argument(
        '--task-id',
        type=str,
        help='Run a single task by ID'
    )
    parser.add_argument(
        '--max-tasks',
        type=int,
        help='Maximum number of tasks to run'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Directory to save results'
    )
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Log file path'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level, args.log_file)
    logger = logging.getLogger(__name__)
    
    # Load config
    if not os.path.exists(args.config):
        logger.error(f"Config file not found: {args.config}")
        sys.exit(1)
    
    config = load_config(args.config)
    logger.info(f"Loaded config from {args.config}")
    
    # Initialize agent
    agent_config = config.get('agent', {})
    agent = GAIAAgent(
        seed=agent_config.get('seed'),
        max_retries=agent_config.get('max_retries', 3),
        calculator_precision=agent_config.get('calculator_precision', 50)
    )
    logger.info("Initialized GAIA Agent")
    
    # Load tasks
    data_config = config.get('data', {})
    data_source = args.data_source or data_config.get('source')
    data_format = args.data_format or data_config.get('format', 'json')
    
    if not data_source:
        logger.error("No data source specified in config or command line")
        sys.exit(1)
    
    loader = GAIALoader()
    
    try:
        if data_format == 'huggingface':
            tasks_raw = loader.load_from_huggingface(data_source, split=data_config.get('split', 'validation'))
        else:
            tasks_raw = loader.load(data_source, format=data_format)
        
        logger.info(f"Loaded {len(tasks_raw)} tasks from {data_source}")
    except Exception as e:
        logger.error(f"Error loading tasks: {e}")
        sys.exit(1)
    
    # Filter math tasks if specified
    if config.get('filter_math_only', False):
        tasks_raw = loader.filter_math_tasks()
        logger.info(f"Filtered to {len(tasks_raw)} math tasks")
    
    # Filter by level if specified
    level = config.get('level')
    if level:
        tasks_raw = loader.filter_by_level(str(level))
        logger.info(f"Filtered to {len(tasks_raw)} tasks at level {level}")
    
    # Convert to AgentBeats tasks
    agentbeats_tasks = [GAIATask.from_gaia(task) for task in tasks_raw]
    
    # Determine output directory
    output_dir = args.output_dir or config.get('output_dir', 'results')
    
    # Run evaluation
    if args.task_id:
        # Run single task
        task = next((t for t in agentbeats_tasks if t.task_id == args.task_id), None)
        if not task:
            logger.error(f"Task not found: {args.task_id}")
            sys.exit(1)
        
        result = run_single_task(agent, task)
        print(json.dumps(result, indent=2))
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            result_file = os.path.join(output_dir, f"{args.task_id}.json")
            with open(result_file, 'w') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Result saved to {result_file}")
    else:
        # Run batch
        summary = run_batch(
            agent,
            agentbeats_tasks,
            output_dir=output_dir,
            max_tasks=args.max_tasks
        )
        
        print("\n" + "="*50)
        print("EVALUATION SUMMARY")
        print("="*50)
        print(f"Total tasks: {summary['total_tasks']}")
        print(f"Correct: {summary['correct']}")
        print(f"Incorrect: {summary['incorrect']}")
        print(f"Accuracy: {summary['accuracy']:.2%}")
        print("="*50)
        
        if output_dir:
            logger.info(f"Results saved to {output_dir}")


if __name__ == '__main__':
    main()
