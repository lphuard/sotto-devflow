# mock_builder.py - Mock builder implementation for testing

from typing import Any, Dict

from .builder import BuilderAdapter


class MockBuilder(BuilderAdapter):
    """Mock builder that returns deterministic placeholder success reports."""

    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the mock builder."""
        return {
            "task_id": task_id,
            "status": "success",
            "report_type": "mock_execution",
            "execution_id": f"mock-{task_id}",
            "timestamp": "1970-01-01T00:00:00",
            "steps": [
                {
                    "step": 1,
                    "action": "initialize_task",
                    "status": "completed",
                    "details": "Task initialization completed successfully",
                },
                {
                    "step": 2,
                    "action": "execute_task",
                    "status": "completed",
                    "details": "Mock task execution completed successfully",
                },
                {
                    "step": 3,
                    "action": "finalize_task",
                    "status": "completed",
                    "details": "Task finalization completed successfully",
                },
            ],
            "results": {
                "output": "Mock execution completed successfully",
                "data": {
                    "mock_data": "This is placeholder data from mock builder",
                    "task_processed": True,
                    "success": True,
                },
            },
            "metadata": {
                "builder": "mock",
                "version": "1.0.0",
                "environment": "test",
            },
        }
