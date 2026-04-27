"""Per-session CTRF JSON reporter so the harness can inspect individual
test status (rubric: every_gold_test_passes).

CTRF schema (common subset): {"results": {"tool": {"name": "pytest"},
"summary": {...}, "tests": [{"name", "status", "duration"}]}}.
"""
import json
import time
from pathlib import Path

CTRF_PATH = Path("/logs/verifier/ctrf.json")
_results: list[dict] = []
_start = time.time()


def pytest_runtest_logreport(report):
    if report.when != "call" and report.outcome != "skipped":
        return
    if report.when == "call":
        status = "passed" if report.outcome == "passed" else "failed"
    elif report.when == "setup" and report.outcome == "failed":
        status = "failed"
    elif report.outcome == "skipped":
        status = "skipped"
    else:
        return
    _results.append(
        {
            "name": report.nodeid,
            "status": status,
            "duration": int((report.duration or 0) * 1000),
            "message": str(report.longrepr) if report.failed else "",
        }
    )


def pytest_sessionfinish(session, exitstatus):
    summary = {
        "tests": len(_results),
        "passed": sum(1 for r in _results if r["status"] == "passed"),
        "failed": sum(1 for r in _results if r["status"] == "failed"),
        "skipped": sum(1 for r in _results if r["status"] == "skipped"),
        "pending": 0,
        "other": 0,
        "start": int(_start),
        "stop": int(time.time()),
    }
    payload = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": summary,
            "tests": _results,
        }
    }
    CTRF_PATH.parent.mkdir(parents=True, exist_ok=True)
    CTRF_PATH.write_text(json.dumps(payload, indent=2))
