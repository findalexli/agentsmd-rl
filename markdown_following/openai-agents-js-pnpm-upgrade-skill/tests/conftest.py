"""Convert the pytest-json-report payload to CTRF after the session ends."""

import json
from pathlib import Path

import pytest


CTRF_PATH = Path("/logs/verifier/ctrf.json")
JSON_REPORT_PATH = Path("/logs/verifier/pytest_json.json")


def _to_ctrf_status(outcome: str) -> str:
    if outcome == "passed":
        return "passed"
    if outcome == "skipped":
        return "skipped"
    return "failed"


@pytest.hookimpl(trylast=True)
def pytest_unconfigure(config):  # noqa: D401
    """After pytest writes the JSON report, transcode it to CTRF."""
    if not JSON_REPORT_PATH.exists():
        return
    try:
        report = json.loads(JSON_REPORT_PATH.read_text())
    except json.JSONDecodeError:
        return

    tests = []
    for entry in report.get("tests", []):
        tests.append({
            "name": entry.get("nodeid", "<unknown>"),
            "status": _to_ctrf_status(entry.get("outcome", "")),
            "duration": int(round(entry.get("duration", 0.0) * 1000)),
        })
    summary = report.get("summary", {})
    ctrf = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": {
                "tests": summary.get("total", len(tests)),
                "passed": summary.get("passed", 0),
                "failed": summary.get("failed", 0),
                "skipped": summary.get("skipped", 0),
                "pending": 0,
                "other": 0,
                "start": int(report.get("created", 0) * 1000),
                "stop": int((report.get("created", 0) + report.get("duration", 0)) * 1000),
            },
            "tests": tests,
        }
    }
    CTRF_PATH.parent.mkdir(parents=True, exist_ok=True)
    CTRF_PATH.write_text(json.dumps(ctrf, indent=2))
