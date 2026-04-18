
# builder.py - Builder adapter interface for task execution

from abc import ABC, abstractmethod
from typing import Dict, Any

class BuilderAdapter(ABC):
    """Abstract base class for builder adapters."""

    @abstractmethod
    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using the builder adapter.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the execution report
        """
        pass


class OpenCloudBuilder(BuilderAdapter):
    """Builder adapter that delegates task execution to Codex Cloud (OpenAI).

    This adapter uses the Codex CLI (`codex`) to execute tasks via OpenClaw's
    built-in exec tooling. It requires the `codex` CLI to be installed and
    authenticated in the environment.
    """

    def execute(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task using Codex Cloud.

        Args:
            task_id: The unique identifier for the task
            task_data: Dictionary containing task data and parameters

        Returns:
            Dictionary containing the normalized execution report
        """
        # Import here to avoid hard dependency
        try:
            import subprocess
            from pathlib import Path
            from datetime import datetime
        except Exception as e:
            return {
                "task_id": task_id,
                "builder": "opencloud",
                "status": "failed",
                "summary": f"OpenCloudBuilder failed to import dependencies: {e}",
                "timestamp": datetime.now().isoformat(),
            }

        # Prepare a prompt for Codex Cloud
        prompt_parts = []
        prompt_parts.append(f"Task ID: {task_id}")
        prompt_parts.append(f"Title: {task_data.get('title', 'Untitled Task')}")
        prompt_parts.append(f"Branch: {task_data.get('branch', 'main')}")
        prompt_parts.append(f"Objective: {task_data.get('objective', '')}")

        prompt = "\n".join(prompt_parts)

        # Use OpenClaw's exec tool to run `codex exec` with PTY
        # This delegates to the host's shell where `codex` is installed
        try:
            import subprocess
            result = subprocess.run(
                ["codex", "exec", "--full-auto", prompt],
                capture_output=True,
                text=True,
                timeout=300,
            )

            # Simple normalization
            status = "success" if result.returncode == 0 else "failed"
            summary = "Codex Cloud execution completed successfully"
            if result.returncode != 0:
                summary = f"Codex Cloud execution failed with exit code {result.returncode}"

            return {
                "task_id": task_id,
                "builder": "opencloud",
                "status": status,
                "summary": summary,
                "timestamp": datetime.now().isoformat(),
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }

        except Exception as e:
            return {
                "task_id": task_id,
                "builder": "opencloud",
                "status": "failed",
                "summary": f"OpenCloudBuilder execution error: {e}",
                "timestamp": datetime.now().isoformat(),
            }


