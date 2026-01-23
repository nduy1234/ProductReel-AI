"""Loader for GAIA benchmark dataset."""

import json
import os
from typing import Dict, List, Optional, Any
from pathlib import Path


class GAIALoader:
    """Loads GAIA benchmark problems from various formats.
    
    Supports:
    - JSON/JSONL files
    - Parquet files (via pandas if available)
    - Hugging Face datasets (if available)
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """Initialize GAIA loader.
        
        Args:
            data_path: Path to GAIA dataset directory or file
        """
        self.data_path = data_path
        self.tasks: List[Dict[str, Any]] = []
    
    def load_from_json(self, file_path: str) -> List[Dict[str, Any]]:
        """Load GAIA tasks from a JSON file.
        
        Args:
            file_path: Path to JSON file
            
        Returns:
            List of task dictionaries
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle both single object and list formats
        if isinstance(data, list):
            tasks = data
        elif isinstance(data, dict):
            # If it's a dict, check for common keys
            if 'tasks' in data:
                tasks = data['tasks']
            elif 'data' in data:
                tasks = data['data']
            else:
                tasks = [data]
        else:
            tasks = []
        
        return self._normalize_tasks(tasks)
    
    def load_from_jsonl(self, file_path: str) -> List[Dict[str, Any]]:
        """Load GAIA tasks from a JSONL file.
        
        Args:
            file_path: Path to JSONL file
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    tasks.append(json.loads(line))
        
        return self._normalize_tasks(tasks)
    
    def load_from_parquet(self, file_path: str) -> List[Dict[str, Any]]:
        """Load GAIA tasks from a Parquet file.
        
        Args:
            file_path: Path to Parquet file
            
        Returns:
            List of task dictionaries
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError("pandas is required to load Parquet files. Install with: pip install pandas pyarrow")
        
        df = pd.read_parquet(file_path)
        tasks = df.to_dict('records')
        return self._normalize_tasks(tasks)
    
    def load_from_huggingface(self, dataset_name: str = "gaia-benchmark/GAIA", split: str = "validation") -> List[Dict[str, Any]]:
        """Load GAIA tasks from Hugging Face datasets.
        
        Args:
            dataset_name: Hugging Face dataset identifier
            split: Dataset split to load (e.g., 'validation', 'test')
            
        Returns:
            List of task dictionaries
        """
        try:
            from datasets import load_dataset
        except ImportError:
            raise ImportError("datasets library is required. Install with: pip install datasets")
        
        dataset = load_dataset(dataset_name, split=split)
        tasks = [item for item in dataset]
        return self._normalize_tasks(tasks)
    
    def _normalize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize task format to standard structure.
        
        Args:
            tasks: Raw task data
            
        Returns:
            Normalized task list
        """
        normalized = []
        for task in tasks:
            normalized_task = {
                'task_id': task.get('task_id') or task.get('Task_id') or task.get('id', ''),
                'question': task.get('Question') or task.get('question') or task.get('prompt', ''),
                'level': task.get('Level') or task.get('level', ''),
                'final_answer': task.get('Final answer') or task.get('final_answer') or task.get('answer', ''),
                'file_name': task.get('file_name', ''),
                'file_path': task.get('file_path', ''),
                'metadata': task.get('Annotator Metadata') or task.get('metadata', {})
            }
            normalized.append(normalized_task)
        
        return normalized
    
    def filter_by_level(self, level: str) -> List[Dict[str, Any]]:
        """Filter tasks by difficulty level.
        
        Args:
            level: Level to filter by (e.g., '1', '2', '3')
            
        Returns:
            Filtered task list
        """
        return [task for task in self.tasks if str(task.get('level', '')) == str(level)]
    
    def filter_math_tasks(self) -> List[Dict[str, Any]]:
        """Filter tasks that appear to be math-related.
        
        This is a heuristic filter based on keywords.
        
        Returns:
            Filtered task list
        """
        math_keywords = [
            'calculate', 'compute', 'solve', 'equation', 'formula',
            'number', 'sum', 'product', 'difference', 'quotient',
            'multiply', 'divide', 'add', 'subtract', 'plus', 'minus',
            'percent', 'fraction', 'decimal', 'integer'
        ]
        
        math_tasks = []
        for task in self.tasks:
            question = task.get('question', '').lower()
            if any(keyword in question for keyword in math_keywords):
                math_tasks.append(task)
        
        return math_tasks
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID.
        
        Args:
            task_id: Task identifier
            
        Returns:
            Task dictionary or None if not found
        """
        for task in self.tasks:
            if task.get('task_id') == task_id:
                return task
        return None
    
    def load(self, source: Optional[str] = None, format: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load tasks from a source (auto-detect format if not specified).
        
        Args:
            source: File path, dataset name, or None to use self.data_path
            format: Format type ('json', 'jsonl', 'parquet', 'huggingface') or None for auto-detect
            
        Returns:
            List of normalized tasks
        """
        if source is None:
            source = self.data_path
        
        if source is None:
            raise ValueError("No data source specified")
        
        # Auto-detect format
        if format is None:
            if source.endswith('.json'):
                format = 'json'
            elif source.endswith('.jsonl'):
                format = 'jsonl'
            elif source.endswith('.parquet'):
                format = 'parquet'
            elif '/' in source and not os.path.exists(source):
                format = 'huggingface'
            else:
                raise ValueError(f"Could not auto-detect format for: {source}")
        
        if format == 'json':
            self.tasks = self.load_from_json(source)
        elif format == 'jsonl':
            self.tasks = self.load_from_jsonl(source)
        elif format == 'parquet':
            self.tasks = self.load_from_parquet(source)
        elif format == 'huggingface':
            self.tasks = self.load_from_huggingface(source)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return self.tasks
