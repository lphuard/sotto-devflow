# run_next.py - CLI entry point for running the next queued task

import sys

from src.integrations.openhands_builder import OpenHandsBuilder
from src.orchestrator.engine import TaskEngine


def run_next_task() -> bool:
    """Run the next queued task from the task store."""
    engine = TaskEngine(builder=OpenHandsBuilder())
    return engine.process_next_task()


def run_next() -> bool:
    """Backward-compatible alias for the queued task runner."""
    return run_next_task()


if __name__ == "__main__":
    sys.exit(0 if run_next_task() else 1)
