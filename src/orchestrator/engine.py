# engine.py - Task orchestration engine

import json
from pathlib import Path
from datetime import datetime
from src.state.store import TaskStore


class OrchestratorEngine:
    """Task orchestration engine that uses the persistent task store."""
    
    def __init__(self):
        """Initialize the orchestrator engine."""
        self.store = TaskStore()
    
    def _write_report(self, task, report_data):
        """Write an optional JSON report for the task."""
        reports_dir = Path("runtime/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / f"{task['id']}.json"
        
        # Create minimal report structure
        report = {
            "task_id": task['id'],
            "title": task['title'],
            "status": "openhands_report_ready",
            "timestamp": datetime.now().isoformat(),
            "data": report_data
        }
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report_file
    
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
            
            # Update task status to openhands_report_ready
            success = self.store.update_task(next_task['id'], {'status': 'openhands_report_ready'})
            if success:
                print("Task marked as openhands_report_ready")
                
                # Print deterministic result to stdout
                print("\n=== EXECUTION RESULT ===")
                print(f"Task ID: {next_task['id']}")
                print(f"Task Title: {next_task['title']}")
                print(f"Final Status: openhands_report_ready")
                print(f"Execution Time: {execution_result['timestamp']}")
                print(f"Result: {execution_result['message']}")
                
                # Optionally write minimal JSON report
                report_file = self._write_report(next_task, execution_result)
                print(f"Report written to: {report_file}")
                
                return True
            else:
                print("Failed to update task status to 'openhands_report_ready'")
                return False
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
