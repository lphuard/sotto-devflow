

# openhands_builder.py - OpenHands builder adapter for task execution

import subprocess
import tempfile
import os
from typing import Dict, Any
from pathlib import Path

from .builder import BuilderAdapter
from .openhands_parser import OpenHandsParser

class OpenHandsBuilder(BuilderAdapter):
    """OpenHands builder adapter that captures raw execution output and normalizes it."""

    def __init__(self):
        """Initialize the OpenHands builder."""
        self.parser = OpenHandsParser()

    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using OpenHands and return a normalized report.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the normalized execution report
        """
        # Capture raw execution output
        raw_result = self._capture_raw_execution(task_id, task_data)

        # Parse and normalize the raw result
        normalized_report = self.parser.parse_raw_result(task_id, raw_result)

        return normalized_report

    def _capture_raw_execution(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Capture raw OpenHands execution output.

        Args:
            task_id: The task ID
            task_data: Task data dictionary

        Returns:
            Dictionary containing raw execution output with keys:
            - stdout: Raw stdout text
            - stderr: Raw stderr text
            - exit_code: Exit code (int)
            - combined_log: Combined log text
            - log_path: Path to raw log file
        """
        # Guard: simulation mode must be explicitly opted-in via env var.
        # Without OPENHANDS_SIMULATE=true, we do not silently produce fake outcomes.
        if os.environ.get('OPENHANDS_SIMULATE', '').lower() != 'true':
            raise RuntimeError(
                "OpenHandsBuilder requires a real OpenHands installation or explicit "
                "simulation mode. Set OPENHANDS_SIMULATE=true to enable simulation."
            )

        # Create a temporary log file
        log_dir = Path("runtime/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{task_id}.log"

        # Simulate OpenHands execution with different outcomes based on task_id
        if ("fail" in task_id.lower() or "error" in task_id.lower() or
            "fail" in task_data.get('title', '').lower()):
            # Simulate a failure case
            stdout_content = f"OpenHands execution started for task {task_id}\n"
            stdout_content += "Processing task...\n"
            stdout_content += "Error: Something went wrong during execution\n"
            stdout_content += "Task failed to complete successfully\n"

            stderr_content = "Traceback (most recent call last):\n"
            stderr_content += "  File \"openhands/executor.py\", line 42, in execute\n"
            stderr_content += "    result = process_task(task)\n"
            stderr_content += "  File \"openhands/processor.py\", line 18, in process_task\n"
            stderr_content += "    raise TaskExecutionError(\"Simulated failure\")\n"
            stderr_content += "openhands.errors.TaskExecutionError: Simulated failure\n"

            exit_code = 1
        else:
            # Simulate a success case
            stdout_content = f"OpenHands execution started for task {task_id}\n"
            stdout_content += "Processing task...\n"
            stdout_content += "Running tests...\n"
            stdout_content += "All tests passed successfully\n"
            stdout_content += "Task completed successfully\n"
            stdout_content += f"Files touched: src/{task_id}.py, tests/test_{task_id}.py\n"

            stderr_content = ""

            exit_code = 0

        # Write to log file
        combined_log = f"=== STDOUT ===\n{stdout_content}\n=== STDERR ===\n{stderr_content}"

        with open(log_file, 'w') as f:
            f.write(combined_log)

        return {
            'stdout': stdout_content,
            'stderr': stderr_content,
            'exit_code': exit_code,
            'combined_log': combined_log,
            'log_path': str(log_file)
        }

    def _execute_real_openhands(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute real OpenHands command (placeholder for future implementation).

        This method is not currently used but shows how real OpenHands integration would work.

        Args:
            task_id: The task ID
            task_data: Task data dictionary

        Returns:
            Dictionary containing raw execution output
        """
        # This would be the real implementation when OpenHands is available
        try:
            # Create temporary log file
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.log', delete=False) as log_file:
                log_path = log_file.name

            # Build OpenHands command
            # This is a placeholder - actual command would depend on OpenHands CLI interface
            cmd = [
                "openhands",
                "execute",
                task_id,
                "--output", "json"
            ]

            # Add task-specific parameters if needed
            if 'parameters' in task_data:
                for key, value in task_data['parameters'].items():
                    cmd.extend([f"--{key}", str(value)])

            # Execute command and capture output
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=os.getcwd()
            )

            # Write combined log
            combined_log = f"=== COMMAND ===\n{' '.join(cmd)}\n"
            combined_log += f"=== STDOUT ===\n{result.stdout}\n"
            combined_log += f"=== STDERR ===\n{result.stderr}\n"
            combined_log += f"=== EXIT CODE ===\n{result.returncode}\n"

            with open(log_path, 'w') as f:
                f.write(combined_log)

            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'exit_code': result.returncode,
                'combined_log': combined_log,
                'log_path': log_path
            }

        except Exception as e:
            # Handle execution errors
            return {
                'stdout': '',
                'stderr': f"OpenHands execution failed: {str(e)}",
                'exit_code': 1,
                'combined_log': f"OpenHands execution failed: {str(e)}",
                'log_path': None
            }
