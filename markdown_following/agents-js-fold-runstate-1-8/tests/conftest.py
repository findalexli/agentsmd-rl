"""Emit a tiny CTRF-style JSON report at the end of the pytest run.

The harness audits whether every individual test passed by reading
``/logs/verifier/ctrf.json``. We write that file ourselves rather than
depending on a third-party reporter plugin.
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path

_OUT = Path("/logs/verifier/ctrf.json")
_RECORDS: list[dict] = []
_START: float = 0.0


def pytest_sessionstart(session) -> None:  # noqa: D401
    global _START
    _START = time.time()


def pytest_runtest_logreport(report) -> None:
    if report.when != "call":
        return
    _RECORDS.append(
        {
            "name": report.nodeid,
            "status": "passed" if report.passed else ("failed" if report.failed else "skipped"),
            "duration": int(report.duration * 1000),
        }
    )


def pytest_sessionfinish(session, exitstatus) -> None:
    summary = {
        "tests": len(_RECORDS),
        "passed": sum(1 for r in _RECORDS if r["status"] == "passed"),
        "failed": sum(1 for r in _RECORDS if r["status"] == "failed"),
        "skipped": sum(1 for r in _RECORDS if r["status"] == "skipped"),
        "start": int(_START * 1000),
        "stop": int(time.time() * 1000),
    }
    payload = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": summary,
            "tests": _RECORDS,
        }
    }
    try:
        _OUT.parent.mkdir(parents=True, exist_ok=True)
        _OUT.write_text(json.dumps(payload, indent=2))
    except OSError:
        # Best-effort; harness reward signal is the reward.txt file.
        pass
