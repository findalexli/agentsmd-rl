"""Behavioural tests for opencode#23744 — Effect Schema migration of MessageV2.Format."""

import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/opencode/packages/opencode"
TESTS_DIR = Path(__file__).parent
PROBE_SRC = TESTS_DIR / "probe.test.ts"
PROBE_DST = Path(REPO) / "test" / "_probe_effect_schema.test.ts"


def _run_bun_test(test_path: str, timeout: int = 180) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bun", "test", test_path, "--timeout", "30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _install_probe() -> None:
    PROBE_DST.write_text(PROBE_SRC.read_text())


def _cleanup_probe() -> None:
    if PROBE_DST.exists():
        PROBE_DST.unlink()


def test_effect_schema_migration_probe():
    """f2p: OutputFormatText/JsonSchema/Format are migrated to Effect Schema with .zod accessors."""
    _install_probe()
    try:
        r = _run_bun_test("test/_probe_effect_schema.test.ts")
        assert r.returncode == 0, (
            f"Effect Schema probe failed (exit={r.returncode}):\n"
            f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
        )
    finally:
        _cleanup_probe()


def test_structured_output_test():
    """p2p: upstream test/session/structured-output.test.ts (22 tests)."""
    r = _run_bun_test("test/session/structured-output.test.ts")
    assert r.returncode == 0, (
        f"structured-output.test.ts failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )


def test_message_v2_test():
    """p2p: upstream test/session/message-v2.test.ts (24 tests)."""
    r = _run_bun_test("test/session/message-v2.test.ts")
    assert r.returncode == 0, (
        f"message-v2.test.ts failed:\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-1000:]}"
    )
