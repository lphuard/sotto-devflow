
# openhands_builder.py - OpenHands builder adapter implementation

import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .builder import BuilderAdapter

class OpenHandsBuilder(BuilderAdapter):
    """OpenHands builder adapter that executes tasks using the OpenHands subprocess."""

    def __init__(self, openhands_path: str = None, timeout: int = 300):
        """
        Initialize the OpenHands builder adapter.

        Args:
            openhands_path: Path to the OpenHands executable
            timeout: Timeout in seconds for OpenHands execution
        """
        self.openhands_path = openhands_path or "mock_openhands.py"
        self.timeout = timeout

    def construct_prompt(self, task_id: str, task_data: Dict[str, Any]) -> str:
        """
        Construct a deterministic prompt from task fields.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            String containing the constructed prompt for OpenHands
        """
        # Extract relevant task fields
        title = task_data.get("title", "Untitled Task")
        objective = task_data.get("objective", "")
        branch = task_data.get("branch", "main")
        pr_url = task_data.get("pr_url", "")

        # Construct deterministic prompt
        prompt_parts = [
            f"Task ID: {task_id}",
            f"Title: {title}",
            f"Branch: {branch}",
            f"Objective: {objective}",
        ]

        if pr_url:
            prompt_parts.append(f"PR URL: {pr_url}")

        prompt_parts.append("\nPlease complete this task using the following instructions:")
        prompt_parts.append("1. Analyze the task requirements")
        prompt_parts.append("2. Implement the necessary changes")
        prompt_parts.append("3. Test your implementation")
        prompt_parts.append("4. Provide a summary of the changes made")

        return "\n".join(prompt_parts)

    def execute_openhands(self, prompt: str) -> Dict[str, Any]:
        """
        Execute OpenHands subprocess and capture stdout, stderr, and exit code.

        Args:
            prompt: The prompt to pass to OpenHands

        Returns:
            Dictionary containing execution results
        """
        try:
            # Create a temporary file for the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(prompt)
                temp_file_path = temp_file.name

            # Execute OpenHands subprocess
            cmd = ["python3", self.openhands_path, "--prompt-file", temp_file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )

            # Clean up temporary file
            Path(temp_file_path).unlink()

            return {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        except subprocess.TimeoutExpired as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"OpenHands execution timed out after {self.timeout} seconds",
                "success": False
            }
        except Exception as e:
            return {
                "exit_code": -1,
                "stdout": "",
                "stderr": f"OpenHands execution failed: {str(e)}",
                "success": False
            }

    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the OpenHands builder adapter.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the execution report
        """
        # Construct prompt from task data
        prompt = self.construct_prompt(task_id, task_data)

        # Execute OpenHands
        execution_result = self.execute_openhands(prompt)

        # Generate normalized report
        report = self.generate_report(task_id, task_data, execution_result)

        return report

    def generate_report(self, task_id: str, task_data: Dict[str, Any], execution_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a normalized builder report.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters
            execution_result: Dictionary containing execution results

        Returns:
            Dictionary containing the normalized report
        """
        # Determine status based on execution result
        status = "success" if execution_result["success"] else "failed"

        # Extract summary from OpenHands output or provide default
        summary = "OpenHands execution completed successfully"
        if not execution_result["success"]:
            summary = f"OpenHands execution failed with exit code {execution_result['exit_code']}"

        # Parse OpenHands output for additional details if available
        output_details = {}
        if execution_result["stdout"]:
            try:
                # Try to parse JSON output if available
                output_details = json.loads(execution_result["stdout"])
            except (json.JSONDecodeError, ValueError):
                # If not JSON, use raw output
                output_details = {"raw_output": execution_result["stdout"]}

        # Construct normalized report
        report = {
            "task_id": task_id,
            "builder": "openhands",
            "status": status,
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "execution_details": {
                "exit_code": execution_result["exit_code"],
                "success": execution_result["success"],
                "stdout": execution_result["stdout"],
                "stderr": execution_result["stderr"],
            },
            "task_data": {
                "title": task_data.get("title", ""),
                "objective": task_data.get("objective", ""),
                "branch": task_data.get("branch", ""),
                "pr_url": task_data.get("pr_url", ""),
            },
            "results": output_details,
            "metadata": {
                "builder_version": "1.0.0",
                "execution_time": datetime.now().isoformat(),
            }
        }

        return report
