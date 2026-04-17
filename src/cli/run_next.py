# run_next.py - CLI entry point for running the next queued task

import json
import os
from pathlib import Path
from datetime import datetime
from src.state.store import TaskStore


def write_report(task, report_data):
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
        
        # Update task status to openhands_report_ready
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
        
        # Optionally write minimal JSON report
        report_file = write_report(next_task, execution_result)
        print(f"Report written to: {report_file}")
        
        return True
    else:
        print("No queued tasks")
        return False


if __name__ == "__main__":
    run_next_task()
