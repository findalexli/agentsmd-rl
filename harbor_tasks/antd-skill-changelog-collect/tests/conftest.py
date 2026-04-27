import json
from pathlib import Path

_RESULTS = []


def pytest_runtest_logreport(report):
    if report.when != "call":
        if report.when == "setup" and report.outcome == "failed":
            _RESULTS.append({"name": report.nodeid, "status": "failed", "duration": int(report.duration * 1000)})
        return
    status = {"passed": "passed", "failed": "failed", "skipped": "skipped"}.get(report.outcome, "other")
    _RESULTS.append({"name": report.nodeid, "status": status, "duration": int(report.duration * 1000)})


def pytest_sessionfinish(session, exitstatus):
    out = Path("/logs/verifier/ctrf.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    summary = {
        "tests": len(_RESULTS),
        "passed": sum(1 for r in _RESULTS if r["status"] == "passed"),
        "failed": sum(1 for r in _RESULTS if r["status"] == "failed"),
        "skipped": sum(1 for r in _RESULTS if r["status"] == "skipped"),
        "other": sum(1 for r in _RESULTS if r["status"] == "other"),
    }
    out.write_text(json.dumps({"results": {"tool": {"name": "pytest"}, "summary": summary, "tests": _RESULTS}}, indent=2))
