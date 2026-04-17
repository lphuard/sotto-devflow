import sys
import pytest
from unittest.mock import patch

from src.cli.show_status import show_status


FULL_TASK = {
    "id": "task-001",
    "title": "Test task",
    "objective": "Test objective",
    "status": "in_progress",
    "branch": "feature/test",
    "pr_url": "https://github.com/lphuard/sotto-devflow/pull/1",
}

TASK_NO_PR = {
    "id": "task-002",
    "title": "No PR task",
    "objective": "Objective",
    "status": "queued",
    "branch": "main",
}


def _mock_store(task):
    def _init(self, **kw):
        pass
    return (
        patch("src.state.store.TaskStore.__init__", _init),
        patch("src.state.store.TaskStore.get_task", return_value=task),
    )


def test_found_task_prints_all_fields(capsys):
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.get_task", return_value=FULL_TASK):
            result = show_status("task-001")

    out = capsys.readouterr().out
    assert result is True
    assert "task-001" in out
    assert "Test task" in out
    assert "Test objective" in out
    assert "in_progress" in out
    assert "feature/test" in out
    assert "https://github.com" in out


def test_pr_url_omitted_when_absent(capsys):
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.get_task", return_value=TASK_NO_PR):
            result = show_status("task-002")

    out = capsys.readouterr().out
    assert result is True
    assert "PR URL" not in out


def test_missing_task_returns_false(capsys):
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.get_task", return_value=None):
            result = show_status("task-999")

    out = capsys.readouterr().out
    assert result is False
    assert "not found" in out.lower()


def test_main_exits_one_on_missing_task():
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.get_task", return_value=None):
            with patch("sys.argv", ["show_status.py", "task-999"]):
                with pytest.raises(SystemExit) as exc:
                    import runpy
                    runpy.run_module("src.cli.show_status", run_name="__main__")
    assert exc.value.code == 1


def test_main_exits_zero_on_found_task():
    with patch("src.state.store.TaskStore.__init__", lambda self, **kw: None):
        with patch("src.state.store.TaskStore.get_task", return_value=FULL_TASK):
            with patch("sys.argv", ["show_status.py", "task-001"]):
                with pytest.raises(SystemExit) as exc:
                    import runpy
                    runpy.run_module("src.cli.show_status", run_name="__main__")
    assert exc.value.code == 0
