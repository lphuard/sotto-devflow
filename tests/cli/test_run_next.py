from unittest.mock import patch

from src.cli.run_next import run_next, run_next_task


def test_run_next_task_returns_engine_result():
    with patch("src.cli.run_next.TaskEngine.__init__", lambda self, builder=None: None):
        with patch("src.cli.run_next.TaskEngine.process_next_task", return_value=True) as process_next_task:
            assert run_next_task() is True

    process_next_task.assert_called_once_with()


def test_run_next_alias_matches_run_next_task():
    with patch("src.cli.run_next.run_next_task", return_value=False) as runner:
        assert run_next() is False

    runner.assert_called_once_with()
