# run_task.py - CLI entry point for running a specific task by ID

from datetime import datetime
from src.state.store import TaskStore
from src.utils.report import write_report


def run_task(task_id: str) -> bool:
    """Run a specific task by ID.
    
    Args:
        task_id: ID of the task to run
        
    Returns:
        True if task was run successfully, False otherwise
    """
    store = TaskStore()
    task = store.get_task(task_id)
    
    # Check if task exists
    if task is None:
        print(f"Error: Task with ID '{task_id}' not found")
        return False
    
    # Check if task is runnable (only queued tasks are runnable in v1)
    if task["status"] != "queued":
        print(f"Error: Task '{task_id}' has status '{task['status']}' and cannot be run")
        print("Only tasks with status 'queued' are runnable in v1")
        return False
    
    print(f"Running task: {task['title']} (ID: {task['id']})")
    print(f"Objective: {task['objective']}")
    print(f"Status: {task['status']}")
    print(f"Branch: {task['branch']}")
    
    # Update task status to executing
    success = store.update_task(task['id'], {'status': 'executing'})
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
        report_file = write_report(task, execution_result)
        print(f"Report written to: {report_file}")
    except OSError as exc:
        print(f"Failed to write report: {exc}")
        store.update_task(task['id'], {'status': 'failed'})
        return False
    
    # Update task status to openhands_report_ready only after report write succeeds
    success = store.update_task(task['id'], {'status': 'openhands_report_ready'})
    if not success:
        print("Failed to update task status to 'openhands_report_ready'")
        return False
    
    print("Task status updated to 'openhands_report_ready'")
    
    # Print deterministic result to stdout
    print("\n=== EXECUTION RESULT ===")
    print(f"Task ID: {task['id']}")
    print(f"Task Title: {task['title']}")
    print(f"Final Status: openhands_report_ready")
    print(f"Execution Time: {execution_result['timestamp']}")
    print(f"Result: {execution_result['message']}")
    
    return True


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python -m src.cli.run_task <task_id>")
        sys.exit(1)
    
    task_id = sys.argv[1]
    success = run_task(task_id)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)