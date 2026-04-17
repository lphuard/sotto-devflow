
# builder.py - Builder adapter interface for task execution

from abc import ABC, abstractmethod
from typing import Dict, Any

class BuilderAdapter(ABC):
    """Abstract base class for builder adapters."""

    @abstractmethod
    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the builder adapter.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the execution report
        """
        pass
