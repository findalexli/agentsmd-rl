"""Emit a CTRF-compatible JSON report at /logs/verifier/ctrf.json after the
pytest run. Consumed by Harbor's per-test audit (`every_gold_test_passes`).
"""

from __future__ import annotations

import json
import time
from pathlib import Path

CTRF_PATH = Path("/logs/verifier/ctrf.json")
_REPORTS: dict[str, dict] = {}
_STARTED_AT = 0


def pytest_sessionstart(session):
    global _STARTED_AT
    _STARTED_AT = int(time.time() * 1000)


def pytest_runtest_logreport(report):
    # Only record one outcome per nodeid; prefer the "call" phase.
    if report.when == "call":
        _REPORTS[report.nodeid] = {
            "outcome": report.outcome,
            "duration": getattr(report, "duration", 0.0),
            "longrepr": str(report.longrepr) if report.failed else "",
        }
    elif report.when == "setup" and report.outcome != "passed":
        _REPORTS.setdefault(
            report.nodeid,
            {
                "outcome": report.outcome,
                "duration": getattr(report, "duration", 0.0),
                "longrepr": str(report.longrepr) if report.failed else "",
            },
        )


def pytest_sessionfinish(session, exitstatus):
    stopped = int(time.time() * 1000)
    summary = {
        "tests": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "pending": 0,
        "other": 0,
        "start": _STARTED_AT,
        "stop": stopped,
    }
    tests = []
    status_map = {"passed": "passed", "failed": "failed", "skipped": "skipped"}
    for nodeid, info in _REPORTS.items():
        st = status_map.get(info.get("outcome"), "other")
        summary["tests"] += 1
        summary[st] = summary.get(st, 0) + 1
        tests.append(
            {
                "name": nodeid,
                "status": st,
                "duration": int(info.get("duration", 0.0) * 1000),
                "message": info.get("longrepr", "") or "",
            }
        )

    report = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": summary,
            "tests": tests,
        }
    }
    try:
        CTRF_PATH.parent.mkdir(parents=True, exist_ok=True)
        CTRF_PATH.write_text(json.dumps(report, indent=2))
    except OSError:
        pass
