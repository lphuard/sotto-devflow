# engine.py - Task orchestration engine

from datetime import datetime
from src.state.store import TaskStore
from src.utils.report import write_report


class OrchestratorEngine:
    """Task orchestration engine that uses the persistent task store."""
    
    def __init__(self):
        """Initialize the orchestrator engine."""
        self.store = TaskStore()
    
    def process_next_task(self) -> bool:
        """Process the next available task.
        
        Returns:
            True if a task was processed, False otherwise
        """
        next_task = self.store.get_next_task()
        
        if next_task:
            print(f"Orchestrator processing task: {next_task['title']}")
            
            # Update task status to executing
            success = self.store.update_task(next_task['id'], {'status': 'executing'})
            if not success:
                print("Failed to update task status to 'executing'")
                return False
            
            print(f"Task details:")
            print(f"  ID: {next_task['id']}")
            print(f"  Objective: {next_task['objective']}")
            print(f"  Branch: {next_task['branch']}")
            print(f"  PR URL: {next_task.get('pr_url', 'N/A')}")
            
            # Perform placeholder execution step
            print("Performing placeholder execution step...")
            execution_result = {
                "success": True,
                "message": "Placeholder execution completed successfully",
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Optionally write minimal JSON report
                report_file = write_report(next_task, execution_result)
                print(f"Report written to: {report_file}")
            except OSError as exc:
                print(f"Failed to write report: {exc}")
                self.store.update_task(next_task['id'], {'status': 'failed'})
                return False

            # Update task status to openhands_report_ready only after report write succeeds
            success = self.store.update_task(next_task['id'], {'status': 'openhands_report_ready'})
            if not success:
                print("Failed to update task status to 'openhands_report_ready'")
                return False

            print("Task marked as openhands_report_ready")
            
            # Print deterministic result to stdout
            print("\n=== EXECUTION RESULT ===")
            print(f"Task ID: {next_task['id']}")
            print(f"Task Title: {next_task['title']}")
            print(f"Final Status: openhands_report_ready")
            print(f"Execution Time: {execution_result['timestamp']}")
            print(f"Result: {execution_result['message']}")
            
            return True
        else:
            print("No queued tasks")
            return False
    
    def get_task_status(self, task_id: str) -> str:
        """Get the current status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            Task status or 'not_found' if task doesn't exist
        """
        task = self.store.get_task(task_id)
        if task:
            return task['status']
        else:
            return 'not_found'


if __name__ == "__main__":
    engine = OrchestratorEngine()
    engine.process_next_task()
