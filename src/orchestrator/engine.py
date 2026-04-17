# engine.py - Task orchestration engine

from src.state.store import TaskStore


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
            
            # Simulate task processing
            print(f"Task details:")
            print(f"  ID: {next_task['id']}")
            print(f"  Objective: {next_task['objective']}")
            print(f"  Branch: {next_task['branch']}")
            print(f"  PR URL: {next_task.get('pr_url', 'N/A')}")
            
            # Update task status to done
            success = self.store.update_task(next_task['id'], {'status': 'done'})
            if success:
                print("Task marked as completed")
                return True
            else:
                print("Failed to update task status")
                return False
        else:
            print("No tasks available for processing")
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
