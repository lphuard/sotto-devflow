# engine.py - Task orchestration engine

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.integrations.builder import BuilderAdapter
from src.integrations.mock_builder import MockBuilder
from src.state.store import TaskStore


class TaskEngine:
    """Task orchestration engine that uses the persistent task store."""

    def __init__(
        self,
        builder: Optional[BuilderAdapter] = None,
        store: Optional[TaskStore] = None,
        reports_dir: str = "runtime/reports",
    ):
        """Initialize the task engine."""
        self.builder = builder or MockBuilder()
        self.store = store or TaskStore()
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def mark_task_executing(self, task_id: str) -> Dict[str, Any]:
        """Persist the task transition into the executing state."""
        if not self.store.update_task(task_id, {"status": "executing"}):
            raise ValueError(f"Failed to update task '{task_id}' to 'executing'")

        return {
            "task_id": task_id,
            "status": "executing",
            "timestamp": datetime.now().isoformat(),
            "state": "task_execution_started",
        }

    def persist_report(self, task_id: str, report: Dict[str, Any]) -> str:
        """Persist the raw builder report to runtime/reports/<task_id>.json."""
        report_file = self.reports_dir / f"{task_id}.json"

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        return str(report_file)

    def mark_report_ready(self, task_id: str, report_file: str) -> Dict[str, Any]:
        """Persist the final openhands_report_ready task state."""
        if not self.store.update_task(task_id, {"status": "openhands_report_ready"}):
            raise ValueError(f"Failed to update task '{task_id}' to 'openhands_report_ready'")

        return {
            "task_id": task_id,
            "status": "openhands_report_ready",
            "timestamp": datetime.now().isoformat(),
            "state": "openhands_report_ready",
            "report_file": report_file,
        }

    def mark_task_failed(self, task_id: str, report_file: str) -> Dict[str, Any]:
        """Persist the final failed task state."""
        if not self.store.update_task(task_id, {"status": "failed"}):
            raise ValueError(f"Failed to update task '{task_id}' to 'failed'")

        return {
            "task_id": task_id,
            "status": "failed",
            "timestamp": datetime.now().isoformat(),
            "state": "failed",
            "report_file": report_file,
        }

    def execute_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task through the configured builder adapter."""
        executing_state = self.mark_task_executing(task_id)
        report = self.builder.execute(task_id, task_data)
        report_file = self.persist_report(task_id, report)

        # Determine final state based on builder report status
        if report.get("status") == "success":
            final_state = self.mark_report_ready(task_id, report_file)
        else:
            final_state = self.mark_task_failed(task_id, report_file)

        return {
            "executing_state": executing_state,
            "report": report,
            "report_file": report_file,
            "final_state": final_state,
        }

    def process_next_task(self) -> bool:
        """Process the next queued task from persistent storage."""
        next_task = self.store.get_next_task()
        if not next_task:
            print("No queued tasks")
            return False

        print(f"Running next task: {next_task['title']} (ID: {next_task['id']})")
        print(f"Objective: {next_task['objective']}")
        print(f"Status: {next_task['status']}")
        print(f"Branch: {next_task['branch']}")

        try:
            result = self.execute_task(next_task["id"], next_task)
        except (OSError, ValueError) as exc:
            print(f"Task execution failed: {exc}")
            self.store.update_task(next_task["id"], {"status": "failed"})
            return False

        report = result["report"]
        final_state = result["final_state"]
        print(f"Task status updated to '{final_state['status']}'")
        print(f"Report written to: {result['report_file']}")
        print("\n=== EXECUTION RESULT ===")
        print(f"Task ID: {next_task['id']}")
        print(f"Task Title: {next_task['title']}")
        print(f"Final Status: {final_state['status']}")
        print(f"Execution Time: {report.get('timestamp', 'N/A')}")
        print(f"Result: {report.get('summary', 'Execution completed')}")
        return True

    def get_task_status(self, task_id: str) -> str:
        """Get the current status of a task."""
        task = self.store.get_task(task_id)
        return task["status"] if task else "not_found"


class OrchestratorEngine(TaskEngine):
    """Backward-compatible alias for the previous engine name."""


if __name__ == "__main__":
    engine = OrchestratorEngine()
    engine.process_next_task()
