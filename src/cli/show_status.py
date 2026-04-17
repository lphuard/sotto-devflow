# show_status.py - CLI command to show status of a specific task

import sys
from src.state.store import TaskStore


def show_status(task_id: str) -> bool:
    """Show status of a specific task by ID.
    
    Args:
        task_id: ID of the task to show
        
    Returns:
        True if task was found and displayed, False if task was not found
        
    Prints detailed task information including id, title, objective, status, branch, and pr_url.
    If task is not found, prints clear error message and exits with non-zero status.
    """
    store = TaskStore()
    task = store.get_task(task_id)
    
    if task is None:
        print(f"Error: Task with ID '{task_id}' not found")
        return False
    
    # Print task details
    print(f"ID: {task['id']}")
    print(f"Title: {task['title']}")
    print(f"Objective: {task['objective']}")
    print(f"Status: {task['status']}")
    print(f"Branch: {task['branch']}")
    
    # Only print PR URL if it exists and is not empty
    if task.get('pr_url', ''):
        print(f"PR URL: {task['pr_url']}")
    
    return True


def main():
    """Main entry point for show_status command."""
    if len(sys.argv) != 2:
        print("Usage: python show_status.py <task_id>")
        return False
    
    task_id = sys.argv[1]
    success = show_status(task_id)
    
    # Exit with appropriate status code
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)