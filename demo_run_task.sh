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
# Ensure a runnable queued task for demo
python -c "
from src.state.store import TaskStore
store = TaskStore()
task_id = 'demo-queued'
task = store.get_task(task_id)

if task is None:
    new_task = {
        'id': task_id,
        'title': 'Demo Queued Task',
        'objective': 'Demonstrate targeted execution',
        'status': 'queued',
        'branch': 'main'
    }
    added = store.add_task(new_task)
    print('Added demo queued task' if added else 'Failed to add demo queued task')
else:
    if task['status'] != 'queued':
        updated = store.update_task(task_id, {'status': 'queued'})
        print(f'Reset existing demo task to queued: {updated}')
    else:
        print('Demo queued task already exists in queued status')
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
