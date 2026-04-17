# run_next.py - CLI entry point for running the next queued task

from datetime import datetime
from src.state.store import TaskStore
from src.utils.report import write_report


def run_next_task():
    """Run the next queued task from the task store."""
    store = TaskStore()
    next_task = store.get_next_task()
    
    if next_task:
        print(f"Running next task: {next_task['title']} (ID: {next_task['id']})")
        print(f"Objective: {next_task['objective']}")
        print(f"Status: {next_task['status']}")
        print(f"Branch: {next_task['branch']}")
        
        # Update task status to executing
        success = store.update_task(next_task['id'], {'status': 'executing'})
        if not success:
            print("Failed to update task status to 'executing'")
            return False
        
        print("Task status updated to 'executing'")
        
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
            store.update_task(next_task['id'], {'status': 'failed'})
            return False

        # Update task status to openhands_report_ready only after report write succeeds
        success = store.update_task(next_task['id'], {'status': 'openhands_report_ready'})
        if not success:
            print("Failed to update task status to 'openhands_report_ready'")
            return False
        
        print("Task status updated to 'openhands_report_ready'")
        
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


if __name__ == "__main__":
    run_next_task()
