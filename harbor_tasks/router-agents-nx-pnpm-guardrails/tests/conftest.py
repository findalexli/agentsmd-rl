"""Emit a minimal CTRF-format report at /logs/verifier/ctrf.json.

Rather than depend on an external ctrf plugin, we generate a minimal CTRF
report inline from pytest's session results.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

CTRF_PATH = Path("/logs/verifier/ctrf.json")

_RESULTS: list[dict] = []
_START_MS: int = 0


def pytest_configure(config):
    global _START_MS
    _START_MS = int(time.time() * 1000)


def pytest_runtest_logreport(report):
    if report.when != "call":
        return
    status_map = {"passed": "passed", "failed": "failed", "skipped": "skipped"}
    status = status_map.get(report.outcome, "other")
    duration_ms = int(getattr(report, "duration", 0.0) * 1000)
    entry = {
        "name": report.nodeid,
        "status": status,
        "duration": duration_ms,
    }
    if report.longreprtext:
        entry["message"] = report.longreprtext[:2000]
    _RESULTS.append(entry)


def pytest_sessionfinish(session, exitstatus):
    summary = {
        "tests": len(_RESULTS),
        "passed": sum(1 for r in _RESULTS if r["status"] == "passed"),
        "failed": sum(1 for r in _RESULTS if r["status"] == "failed"),
        "skipped": sum(1 for r in _RESULTS if r["status"] == "skipped"),
        "pending": 0,
        "other": sum(1 for r in _RESULTS if r["status"] == "other"),
        "start": _START_MS,
        "stop": int(time.time() * 1000),
    }
    ctrf = {
        "results": {
            "tool": {"name": "pytest"},
            "summary": summary,
            "tests": _RESULTS,
        }
    }
    CTRF_PATH.parent.mkdir(parents=True, exist_ok=True)
    CTRF_PATH.write_text(json.dumps(ctrf, indent=2))
