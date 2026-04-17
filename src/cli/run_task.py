

# run_task.py - CLI entry point for running a specific task

import json
import sys
from ..orchestrator.engine import TaskEngine
from ..integrations.mock_builder import MockBuilder

def run_task(task_id: str):
    """
    Run a specific task by ID.

    Args:
        task_id: The unique identifier for the task to run
    """
    # For demonstration purposes, we'll use mock task data
    task_data = {
        "task_id": task_id,
        "description": f"Specific task execution for {task_id}",
        "parameters": {
            "task_specific_param": f"value_for_{task_id}",
            "direct_execution": True
        }
    }

    # Initialize engine with mock builder
    engine = TaskEngine(builder=MockBuilder())

    # Execute the task
    result = engine.execute_task(task_id, task_data)

    # Print the result
    print(f"Task {task_id} execution completed:")
    print(json.dumps(result, indent=2))

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli.run_task <task_id>")
        sys.exit(1)

    task_id = sys.argv[1]
    run_task(task_id)

