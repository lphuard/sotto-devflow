# list_tasks.py - CLI command to list all tasks from the task store

import sys
from src.state.store import TaskStore


def list_tasks():
    """List all tasks from the task store."""
    store = TaskStore()
    tasks = store.load_tasks()

    if not tasks:
        print("No tasks found")
        return True

    tasks.sort(key=lambda x: x["id"])

    print(f"{'ID':<20}{'TITLE':<50}STATUS")
    print("-" * 80)

    for task in tasks:
        print(f"{task['id']:<20}{task['title']:<50}{task['status']}")

    return True


if __name__ == "__main__":
    success = list_tasks()
    sys.exit(0 if success else 1)
