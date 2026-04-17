import json
import sys
import pytest
from pathlib import Path
from unittest.mock import patch

from src.cli.list_tasks import list_tasks


VALID_TASK = {
    "id": "task-001",
    "title": "Test task",
    "objective": "Test objective",
    "status": "queued",
    "branch": "main",
}

VALID_TASK_2 = {
    "id": "task-002",
    "title": "Another task",
    "objective": "Another objective",
    "status": "done",
    "branch": "feature/x",
}


@pytest.fixture
def store_path(tmp_path):
    p = tmp_path / "tasks.json"
    return p


def write_tasks(path, tasks):
    path.write_text(json.dumps(tasks))


def test_empty_store(store_path, capsys):
    write_tasks(store_path, [])
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.load_tasks", return_value=[]):
            result = list_tasks()

    out = capsys.readouterr().out
    assert result is True
    assert "No tasks found" in out


def test_single_task_output(capsys):
    with patch("src.state.store.TaskStore.load_tasks", return_value=[VALID_TASK]):
        with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
            result = list_tasks()

    out = capsys.readouterr().out
    assert result is True
    assert "task-001" in out
    assert "Test task" in out
    assert "queued" in out


def test_tasks_sorted_by_id(capsys):
    tasks = [VALID_TASK_2, VALID_TASK]  # deliberately reversed
    with patch("src.state.store.TaskStore.load_tasks", return_value=tasks):
        with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
            list_tasks()

    lines = [l for l in capsys.readouterr().out.splitlines() if "task-" in l]
    assert lines[0].startswith("task-001")
    assert lines[1].startswith("task-002")


def test_column_alignment(capsys):
    with patch("src.state.store.TaskStore.load_tasks", return_value=[VALID_TASK]):
        with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
            list_tasks()

    lines = capsys.readouterr().out.splitlines()
    header = lines[0]
    data = lines[2]  # skip separator

    # ID column starts at same offset in header and data row
    assert header.index("TITLE") == data.index("Test task")


def test_main_exits_zero(store_path):
    with patch("src.state.store.TaskStore.load_tasks", return_value=[VALID_TASK]):
        with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
            with pytest.raises(SystemExit) as exc:
                import runpy
                with patch("sys.argv", ["list_tasks.py"]):
                    runpy.run_module("src.cli.list_tasks", run_name="__main__")
    assert exc.value.code == 0
