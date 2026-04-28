"""Test harness for workers-sdk AI auth error PR."""

import os
import shutil
import subprocess

REPO = "/workspace/workers-sdk"


def test_existing_ai_tests_pass():
    """P2P: Existing AI fetcher vitest tests pass on the base commit."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "src/__tests__/ai.local.test.ts"],
        cwd=os.path.join(REPO, "packages", "wrangler"),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Existing AI tests failed.\n"
        f"stdout: {r.stdout[-1500:]}\n"
        f"stderr: {r.stderr[-1000:]}"
    )


def test_403_auth_error_logging():
    """F2P: 403 with auth error code 1031 triggers user-friendly error message."""
    test_src = "/tests/ai_403_behavior.test.ts"
    test_dst = os.path.join(
        REPO, "packages", "wrangler", "src", "__tests__", "ai_403_behavior.test.ts"
    )
    shutil.copy(test_src, test_dst)
    try:
        r = subprocess.run(
            ["pnpm", "exec", "vitest", "run", "src/__tests__/ai_403_behavior.test.ts"],
            cwd=os.path.join(REPO, "packages", "wrangler"),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, (
            f"403 auth handling test failed.\n"
            f"stdout: {r.stdout[-1500:]}\n"
            f"stderr: {r.stderr[-1000:]}"
        )
    finally:
        if os.path.exists(test_dst):
            os.unlink(test_dst)
