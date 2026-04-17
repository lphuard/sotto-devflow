# run_next.py - CLI entry point for running the next queued task

import json
import sys
from ..orchestrator.engine import TaskEngine
from ..integrations.mock_builder import MockBuilder

def run_next():
    """
    Run the next queued task.

    This is a placeholder implementation that demonstrates the builder adapter usage.
    In a real implementation, this would fetch the next task from a queue.
    """
    # For demonstration purposes, we'll use a mock task
    task_id = "demo_task_001"
    task_data = {
        "task_id": task_id,
        "description": "Demo task for builder adapter testing",
        "parameters": {
            "test_param": "value1",
            "demo_flag": True
        }
    }

    # Initialize engine with mock builder
    engine = TaskEngine(builder=MockBuilder())

    # Execute the task
    result = engine.execute_task(task_id, task_data)

    # Print the result
    print("Task execution completed:")
    print(json.dumps(result, indent=2))

    return result

if __name__ == "__main__":
    run_next()
