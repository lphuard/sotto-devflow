from types import SimpleNamespace
from unittest.mock import patch

from src.cli.run_task import run_task


QUEUED_TASK = {
    "id": "task-001",
    "title": "Test task",
    "objective": "Test objective",
    "status": "queued",
    "branch": "feature/test",
}


def _patch_engine(task):
    def _init(self, builder=None):
        self.store = SimpleNamespace(get_task=lambda task_id: task)

    return patch("src.cli.run_task.TaskEngine.__init__", _init)


def test_missing_task_returns_false(capsys):
    with _patch_engine(None):
        assert run_task("task-999") is False

    assert "not found" in capsys.readouterr().out.lower()


def test_non_queued_task_returns_false(capsys):
    task = {**QUEUED_TASK, "status": "done"}
    with _patch_engine(task):
        assert run_task(task["id"]) is False

    out = capsys.readouterr().out
    assert "cannot be run" in out
    assert "queued" in out


def test_queued_task_executes_and_prints_result(capsys):
    result = {
        "report": {
            "timestamp": "2026-04-17T00:00:00",
            "summary": "Mock execution completed successfully",
            "status": "success",
            "exit_code": 0,
        },
        "final_state": {"status": "openhands_report_ready"},
        "report_file": "runtime/reports/task-001.json",
        "executing_state": {"status": "executing"},
    }

    with _patch_engine(QUEUED_TASK):
        with patch("src.cli.run_task.TaskEngine.execute_task", return_value=result) as execute_task:
            assert run_task(QUEUED_TASK["id"]) is True

    execute_task.assert_called_once_with(QUEUED_TASK["id"], QUEUED_TASK)
    out = capsys.readouterr().out
    assert "Running task: Test task" in out
    assert "openhands_report_ready" in out
    assert "Mock execution completed successfully" in out
