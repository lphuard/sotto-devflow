# list_tasks.py - CLI command to list all tasks from the task store

from src.state.store import TaskStore


def list_tasks():
    """List all tasks from the task store.
    
    Prints a deterministic summary of all tasks with id, title, and status.
    If no tasks are found, prints "No tasks found" and exits cleanly.
    """
    store = TaskStore()
    tasks = store.load_tasks()
    
    if not tasks:
        print("No tasks found")
        return True
    
    # Sort tasks by ID for deterministic output
    tasks.sort(key=lambda x: x["id"])
    
    # Print header
    print("ID\t\t\tTITLE\t\t\t\t\t\t\t\tSTATUS")
    print("-" * 80)
    
    # Print each task
    for task in tasks:
        print(f"{task['id']}\t\t{task['title']}\t\t{task['status']}")
    
    return True


if __name__ == "__main__":
    list_tasks()