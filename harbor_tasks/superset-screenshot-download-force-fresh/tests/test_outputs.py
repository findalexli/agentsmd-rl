"""Behavioral tests for the dashboard screenshot-download fix.

The bug: useDownloadScreenshot.ts posts to
``/api/v1/dashboard/<id>/cache_dashboard_screenshot/`` without any
``force`` flag, so the backend returns the cached (possibly stale)
thumbnail instead of regenerating the screenshot.

Each test exercises the hook end-to-end via a synthetic Node.js harness
(see /opt/test_harness/runner.js) that bundles the TypeScript source
with esbuild, replaces React/redux/etc. imports with stubs, and
captures the URL passed to ``SupersetClient.post``.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/superset")
HOOK = REPO / "superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts"
HARNESS_DIR = Path("/opt/test_harness")
RUNNER = HARNESS_DIR / "runner.js"


def _run_harness() -> str:
    """Run the Node harness against the current hook source and return
    the last ``ENDPOINT:`` line emitted on stdout."""
    assert HOOK.exists(), f"Hook source missing: {HOOK}"
    assert RUNNER.exists(), f"Runner missing: {RUNNER}"
    result = subprocess.run(
        ["node", str(RUNNER), str(HOOK)],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(HARNESS_DIR),
    )
    if result.returncode != 0:
        raise AssertionError(
            f"Harness exited with code {result.returncode}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    endpoint_lines = [
        line[len("ENDPOINT:") :]
        for line in result.stdout.splitlines()
        if line.startswith("ENDPOINT:")
    ]
    if not endpoint_lines:
        raise AssertionError(
            f"Harness produced no ENDPOINT: line.\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return endpoint_lines[-1]


def test_post_endpoint_requests_fresh_screenshot():
    """Downloads must request a fresh screenshot.

    A correct fix surfaces a ``force`` flag set to ``true`` in the URL
    that POSTs to cache_dashboard_screenshot. Accepted encodings:
    ``force=true``, ``force:true`` (rison), ``force:!t`` (rison short),
    or URL-encoded variants.
    """
    endpoint = _run_harness()
    assert "force" in endpoint, (
        f"Expected force flag in URL, got: {endpoint!r}"
    )
    pattern = re.compile(r"force[:=%][^&]*?(true|!t)", re.IGNORECASE)
    assert pattern.search(endpoint), (
        "URL must request a fresh screenshot (force=true / force:!t in "
        f"any encoding); got: {endpoint!r}"
    )


def test_post_endpoint_targets_cache_dashboard_screenshot():
    """Hook still posts to the cache_dashboard_screenshot endpoint."""
    endpoint = _run_harness()
    assert "cache_dashboard_screenshot" in endpoint, (
        f"Expected URL to target cache_dashboard_screenshot, got: {endpoint!r}"
    )


def test_post_endpoint_includes_dashboard_id():
    """The dashboard id must still be interpolated into the URL path."""
    endpoint = _run_harness()
    # The runner calls the hook with dashboardId=1234.
    assert "/dashboard/1234/cache_dashboard_screenshot" in endpoint, (
        f"Expected dashboard id in URL path, got: {endpoint!r}"
    )


def test_hook_has_apache_license_header():
    """Repo convention: TypeScript source files require ASF license headers."""
    text = HOOK.read_text(encoding="utf-8")
    head = text[:1500]
    assert "Apache" in head and "License, Version 2.0" in head, (
        "useDownloadScreenshot.ts is missing its Apache 2.0 license header"
    )
