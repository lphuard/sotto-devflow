# report.py - Shared task report writing utility

import json
from pathlib import Path
from datetime import datetime


def write_report(task: dict, report_data: dict) -> Path:
    """Write a JSON report for a task to runtime/reports/<task_id>.json."""
    reports_dir = Path("runtime/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    report_file = reports_dir / f"{task['id']}.json"

    report = {
        "task_id": task["id"],
        "title": task["title"],
        "status": "openhands_report_ready",
        "timestamp": datetime.now().isoformat(),
        "data": report_data,
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    return report_file
