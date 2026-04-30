"""Emit a CTRF-format result file at /logs/verifier/ctrf.json."""
from __future__ import annotations

import json
import os
import time
from pathlib import Path


_RESULTS: list[dict] = []
_START_MS = 0


def pytest_sessionstart(session):
    global _START_MS
    _START_MS = int(time.time() * 1000)


def pytest_runtest_logreport(report):
    if report.when != "call" and not (report.when == "setup" and report.outcome == "failed"):
        return
    status = report.outcome  # "passed" | "failed" | "skipped"
    _RESULTS.append({
        "name": report.nodeid,
        "status": status,
        "duration": int(getattr(report, "duration", 0) * 1000),
        "message": str(report.longrepr) if report.failed else "",
    })


def pytest_sessionfinish(session, exitstatus):
    stop_ms = int(time.time() * 1000)
    passed = sum(1 for r in _RESULTS if r["status"] == "passed")
    failed = sum(1 for r in _RESULTS if r["status"] == "failed")
    skipped = sum(1 for r in _RESULTS if r["status"] == "skipped")
    out = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": {
                "tests": len(_RESULTS),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "pending": 0,
                "other": 0,
                "start": _START_MS,
                "stop": stop_ms,
            },
            "tests": _RESULTS,
        },
    }
    out_path = Path("/logs/verifier/ctrf.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
