# engine.py - Task orchestration engine

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
from ..integrations.mock_builder import MockBuilder
from ..integrations.builder import BuilderAdapter

class TaskEngine:
    """Task orchestration engine that uses builder adapters."""

    def __init__(self, builder: BuilderAdapter = None):
        """
        Initialize the task engine.

        Args:
            builder: Builder adapter instance. If None, uses MockBuilder.
        """
        self.builder = builder or MockBuilder()
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist."""
        reports_dir = "/workspace/sotto-devflow/runtime/reports"
        os.makedirs(reports_dir, exist_ok=True)

    def mark_task_executing(self, task_id: str) -> Dict[str, Any]:
        """
        Mark a task as executing.

        Args:
            task_id: The unique identifier for the task

        Returns:
            Dictionary containing the execution state
        """
        state = {
            "task_id": task_id,
            "status": "executing",
            "timestamp": datetime.now().isoformat(),
            "state": "task_execution_started"
        }
        return state

    def persist_report(self, task_id: str, report: Dict[str, Any]) -> str:
        """
        Persist the execution report to file.

        Args:
            task_id: The unique identifier for the task
            report: The execution report dictionary

        Returns:
            Path to the saved report file
        """
        reports_dir = "/workspace/sotto-devflow/runtime/reports"
        report_file = os.path.join(reports_dir, f"{task_id}.json")

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        return report_file

    def mark_report_ready(self, task_id: str) -> Dict[str, Any]:
        """
        Mark the final state as openhands_report_ready.

        Args:
            task_id: The unique identifier for the task

        Returns:
            Dictionary containing the final state
        """
        state = {
            "task_id": task_id,
            "status": "completed",
            "timestamp": datetime.now().isoformat(),
            "state": "openhands_report_ready",
            "report_file": f"/workspace/sotto-devflow/runtime/reports/{task_id}.json"
        }
        return state

    def execute_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the builder adapter.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the complete execution result
        """
        # Mark task as executing
        executing_state = self.mark_task_executing(task_id)

        # Execute task using builder adapter
        report = self.builder.execute(task_id, task_data)

        # Persist the report
        report_file = self.persist_report(task_id, report)

        # Mark final state
        final_state = self.mark_report_ready(task_id)

        return {
            "executing_state": executing_state,
            "report": report,
            "report_file": report_file,
            "final_state": final_state
        }
