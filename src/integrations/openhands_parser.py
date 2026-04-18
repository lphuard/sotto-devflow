# openhands_parser.py - Parser for OpenHands output and reports

import re
from typing import Dict, Any, Optional
from datetime import datetime

class OpenHandsParser:
    """Parser for normalizing OpenHands execution output into structured build reports."""

    def __init__(self):
        """Initialize the parser."""
        pass

    def parse_raw_result(self, task_id: str, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse raw OpenHands execution result into a normalized structured report.

        Args:
            task_id: The task ID
            raw_result: Dictionary containing raw execution output with keys:
                - stdout: Raw stdout text
                - stderr: Raw stderr text
                - exit_code: Exit code (int)
                - combined_log: Optional combined log text
                - log_path: Optional path to raw log file

        Returns:
            Dictionary containing normalized report with required fields:
            - task_id
            - builder
            - status
            - summary
            And optional fields:
            - exit_code
            - raw_status
            - stdout_excerpt
            - stderr_excerpt
            - tests_passed
            - files_touched
            - recommendation
            - raw_log_path
            - timestamp
        """
        # Extract raw data
        stdout = raw_result.get('stdout', '')
        stderr = raw_result.get('stderr', '')
        exit_code = raw_result.get('exit_code', 0)
        combined_log = raw_result.get('combined_log', '')
        log_path = raw_result.get('log_path', None)

        # Normalize status
        normalized_status = self._normalize_status(exit_code, stdout, stderr)

        # Generate summary
        summary = self._generate_summary(normalized_status, exit_code)

        # Extract optional fields conservatively
        stdout_excerpt = self._extract_excerpt(stdout, max_lines=5)
        stderr_excerpt = self._extract_excerpt(stderr, max_lines=5)
        tests_passed = self._extract_tests_passed(stdout, stderr)
        files_touched = self._extract_files_touched(stdout, stderr)

        # Build normalized report
        report = {
            'task_id': task_id,
            'builder': 'openhands',
            'status': normalized_status,
            'summary': summary,
            'exit_code': exit_code,
            'raw_status': self._get_raw_status(exit_code),
            'stdout_excerpt': stdout_excerpt,
            'stderr_excerpt': stderr_excerpt,
            'tests_passed': tests_passed,
            'files_touched': files_touched,
            'recommendation': self._generate_recommendation(normalized_status),
            'raw_log_path': log_path,
            'timestamp': datetime.now().isoformat()
        }

        return report

    def _normalize_status(self, exit_code: int, stdout: str, stderr: str) -> str:
        """
        Normalize raw execution result into stable status.

        Args:
            exit_code: Exit code from execution
            stdout: Stdout text
            stderr: Stderr text

        Returns:
            Normalized status: 'success', 'failure', or 'partial_success'
        """
        if exit_code == 0:
            # Check for fatal indicators in output even with exit code 0
            fatal_indicators = ['fatal', 'error', 'failed', 'exception', 'traceback']
            if any(indicator in stderr.lower() for indicator in fatal_indicators):
                return 'failure'
            return 'success'
        else:
            return 'failure'

    def _get_raw_status(self, exit_code: int) -> str:
        """Get raw status string based on exit code."""
        if exit_code == 0:
            return 'exit_0'
        else:
            return f'exit_{exit_code}'

    def _generate_summary(self, status: str, exit_code: int) -> str:
        """Generate deterministic summary based on status and exit code."""
        if status == 'success':
            return 'OpenHands execution completed successfully.'
        elif status == 'failure':
            return f'OpenHands execution failed with exit code {exit_code}.'
        else:
            return 'OpenHands execution completed, but output parsing was partial.'

    def _extract_excerpt(self, text: str, max_lines: int = 5) -> Optional[str]:
        """Extract a short excerpt from text, limited to max_lines."""
        if not text:
            return None

        lines = text.split('\n')
        excerpt_lines = lines[:max_lines]
        excerpt = '\n'.join(excerpt_lines)

        if len(lines) > max_lines:
            excerpt += f'\n... ({len(lines) - max_lines} more lines)'

        return excerpt if excerpt.strip() else None

    def _extract_tests_passed(self, stdout: str, stderr: str) -> Optional[bool]:
        """Extract whether tests passed from output (conservative approach)."""
        # Look for clear test success indicators
        success_indicators = ['all tests passed', 'tests: passed', 'test success']
        failure_indicators = ['tests failed', 'test failure', 'failed tests']

        # Check stdout first
        stdout_lower = stdout.lower()
        if any(indicator in stdout_lower for indicator in success_indicators):
            return True
        elif any(indicator in stdout_lower for indicator in failure_indicators):
            return False

        # Check stderr as secondary source
        stderr_lower = stderr.lower()
        if any(indicator in stderr_lower for indicator in success_indicators):
            return True
        elif any(indicator in stderr_lower for indicator in failure_indicators):
            return False

        # If we can't determine, return None
        return None

    def _extract_files_touched(self, stdout: str, stderr: str) -> list:
        """Extract list of files touched from output (conservative approach)."""
        files_touched = []

        # Only patterns that require an explicit path context (modified/created/etc.)
        # The broad bare-extension pattern is omitted to avoid matching traceback filenames.
        patterns = [
            r'(?:modified|created|updated|touched|changed)\s+([^\s]+)',
            r'file\s+([^\s]+)\s+(?:modified|created|updated|touched|changed)',
            r'([^\s]+\.(py|js|ts|json|md|txt|html|css))\s+(?:modified|created|updated|touched|changed)',
        ]

        combined_text = f"{stdout}\n{stderr}"

        for pattern in patterns:
            matches = re.findall(pattern, combined_text)
            for match in matches:
                if isinstance(match, tuple):
                    for group in match:
                        if group and group not in files_touched:
                            files_touched.append(group)
                elif match and match not in files_touched:
                    files_touched.append(match)

        # Post-filter: only keep tokens that look like real file paths.
        # Must start with / or ./ or ../ (absolute/explicit-relative), or contain
        # a directory separator, AND must have a file extension.
        # Tokens with spaces, quotes, or traceback punctuation are rejected.
        validated = []
        for token in set(files_touched):
            if not token:
                continue
            # Reject tokens containing whitespace or quote characters
            if any(c in token for c in (' ', '"', "'")):
                continue
            # Reject tokens that are clearly traceback noise (e.g. end with "," or ":")
            if token.endswith((',', ':', ')')):
                continue
            # Require an explicit path prefix or a directory separator
            has_prefix = token.startswith('/') or token.startswith('./') or token.startswith('../')
            has_sep = '/' in token
            # Require a file extension (basename must contain a dot that isn't the first char)
            basename = token.rsplit('/', 1)[-1] if '/' in token else token
            parts = basename.split('.')
            has_ext = len(parts) > 1 and parts[0] != '' and len(parts[-1]) <= 10
            if (has_prefix or has_sep) and has_ext:
                validated.append(token)

        return validated

    def _generate_recommendation(self, status: str) -> str:
        """Generate recommendation based on execution status."""
        if status == 'success':
            return 'Task completed successfully. Ready for review or next steps.'
        elif status == 'failure':
            return 'Task failed. Review logs and output for troubleshooting.'
        else:
            return 'Task completed with partial results. Manual review recommended.'
