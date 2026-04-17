# run_task.py - CLI entry point for running a specific task by ID

import sys

from src.integrations.mock_builder import MockBuilder
from src.orchestrator.engine import TaskEngine


def run_task(task_id: str) -> bool:
    """Run a specific queued task by ID."""
    engine = TaskEngine(builder=MockBuilder())
    task = engine.store.get_task(task_id)

    if task is None:
        print(f"Error: Task with ID '{task_id}' not found")
        return False

    if task["status"] != "queued":
        print(f"Error: Task '{task_id}' has status '{task['status']}' and cannot be run")
        print("Only tasks with status 'queued' are runnable in v1")
        return False

    print(f"Running task: {task['title']} (ID: {task['id']})")
    print(f"Objective: {task['objective']}")
    print(f"Status: {task['status']}")
    print(f"Branch: {task['branch']}")

    result = engine.execute_task(task_id, task)
    report = result["report"]

    print("Task status updated to 'openhands_report_ready'")
    print("\n=== EXECUTION RESULT ===")
    print(f"Task ID: {task['id']}")
    print(f"Task Title: {task['title']}")
    print("Final Status: openhands_report_ready")
    print(f"Execution Time: {report.get('timestamp', 'N/A')}")
    print(f"Result: {report.get('results', {}).get('output', 'Execution completed')}")

    return True


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m src.cli.run_task <task_id>")
        sys.exit(1)

    sys.exit(0 if run_task(sys.argv[1]) else 1)
