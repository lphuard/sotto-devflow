# store.py - State store for task and workflow state

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class TaskStore:
    """JSON-backed persistent task store for sotto-devflow."""
    
    def __init__(self, storage_path: str = "runtime/tasks/tasks.json"):
        """Initialize the task store.
        
        Args:
            storage_path: Path to the JSON file for task storage
        """
        self.storage_path = Path(storage_path)
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Ensure the storage directory and file exist."""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.storage_path.exists():
            self.storage_path.write_text("[]")
    
    def _load_raw_tasks(self) -> List[Dict[str, Any]]:
        """Load raw task data from storage file."""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    def _save_raw_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Save raw task data to storage file."""
        with open(self.storage_path, 'w') as f:
            json.dump(tasks, f, indent=2)
    
    def _validate_task(self, task: Dict[str, Any]) -> bool:
        """Validate a task against the required schema."""
        required_fields = ["id", "title", "objective", "status", "branch"]
        
        # Check required fields exist
        for field in required_fields:
            if field not in task:
                return False
        
        # Check status is valid
        valid_statuses = ["queued", "executing", "openhands_report_ready", "todo", "in_progress", "done", "failed"]
        if task["status"] not in valid_statuses:
            return False
        
        return True
    
    def load_tasks(self) -> List[Dict[str, Any]]:
        """Load all tasks from storage.
        
        Returns:
            List of task dictionaries
        """
        raw_tasks = self._load_raw_tasks()
        # Filter out invalid tasks
        return [task for task in raw_tasks if self._validate_task(task)]
    
    def save_tasks(self, tasks: List[Dict[str, Any]]) -> None:
        """Save all tasks to storage.
        
        Args:
            tasks: List of task dictionaries to save
        """
        # Validate all tasks before saving
        valid_tasks = [task for task in tasks if self._validate_task(task)]
        self._save_raw_tasks(valid_tasks)
    
    def get_next_task(self) -> Optional[Dict[str, Any]]:
        """Get the next queued task (first task with status 'queued' sorted by ID for deterministic selection).
        
        Returns:
            Task dictionary or None if no tasks available
        """
        tasks = self.load_tasks()
        # "todo" is kept in valid_statuses for backwards compatibility but is not picked up here;
        # new tasks must use "queued" to enter the execution pipeline.
        queued_tasks = [task for task in tasks if task["status"] == "queued"]
        queued_tasks.sort(key=lambda x: x["id"])
        return queued_tasks[0] if queued_tasks else None
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific task by ID.
        
        Args:
            task_id: ID of the task to retrieve
            
        Returns:
            Task dictionary or None if not found
        """
        tasks = self.load_tasks()
        for task in tasks:
            if task["id"] == task_id:
                return task
        return None
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task by ID.
        
        Args:
            task_id: ID of the task to update
            updates: Dictionary of field updates
            
        Returns:
            True if task was found and updated, False otherwise
        """
        tasks = self.load_tasks()
        for i, task in enumerate(tasks):
            if task["id"] == task_id:
                # Apply updates
                tasks[i] = {**task, **updates}
                # Validate the updated task
                if self._validate_task(tasks[i]):
                    self.save_tasks(tasks)
                    return True
                else:
                    # Revert if validation fails
                    return False
        return False
    
    def add_task(self, task: Dict[str, Any]) -> bool:
        """Add a new task to the store.
        
        Args:
            task: Task dictionary to add
            
        Returns:
            True if task was added successfully, False otherwise
        """
        if not self._validate_task(task):
            return False
            
        tasks = self.load_tasks()
        # Check for duplicate ID
        for existing_task in tasks:
            if existing_task["id"] == task["id"]:
                return False
                
        tasks.append(task)
        self.save_tasks(tasks)
        return True
