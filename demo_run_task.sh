#!/bin/bash

# Demo script for run_task functionality

echo "=== Demo: run_task <id> implementation ==="
echo ""

echo "1. Testing missing task error handling:"
python -m src.cli.run_task task-999
echo "Exit code: $?"
echo ""

echo "2. Testing non-runnable task error handling:"
python -m src.cli.run_task task-001
echo "Exit code: $?"
echo ""

echo "3. Testing queued task execution (creating a new queued task first):"
# Add a new queued task for demo
python -c "
from src.state.store import TaskStore
store = TaskStore()
new_task = {
    'id': 'demo-queued',
    'title': 'Demo Queued Task',
    'objective': 'Demonstrate targeted execution',
    'status': 'queued',
    'branch': 'main'
}
store.add_task(new_task)
print('Added demo queued task')
"

echo "Running the queued task:"
python -m src.cli.run_task demo-queued
echo "Exit code: $?"
echo ""

echo "4. Verifying task status was updated:"
python -c "
from src.state.store import TaskStore
store = TaskStore()
task = store.get_task('demo-queued')
if task:
    print(f'Task status: {task[\"status\"]}')
else:
    print('Task not found')
"

echo ""
echo "=== Demo complete ==="