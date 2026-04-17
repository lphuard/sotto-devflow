# run_next.py - CLI entry point for running the next queued task

from src.state.store import TaskStore


def run_next_task():
    """Run the next queued task from the task store."""
    store = TaskStore()
    next_task = store.get_next_task()
    
    if next_task:
        print(f"Running next task: {next_task['title']} (ID: {next_task['id']})")
        print(f"Objective: {next_task['objective']}")
        print(f"Status: {next_task['status']}")
        print(f"Branch: {next_task['branch']}")
        
        # Update task status to in_progress
        store.update_task(next_task['id'], {'status': 'in_progress'})
        print("Task status updated to 'in_progress'")
        
        return True
    else:
        print("No tasks available to run.")
        return False


if __name__ == "__main__":
    run_next_task()
