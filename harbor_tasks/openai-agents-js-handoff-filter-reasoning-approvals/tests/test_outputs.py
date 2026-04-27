"""Behavioral tests for the openai-agents-js handoff-filter regression.

The agent must update `removeAllTools()` so that handoff input filtering also
strips orphaned `reasoning` items and `hosted_tool_call` approval placeholders
in addition to the existing tool-call types.

The fail-to-pass tests below execute real TypeScript via vitest. Pass-to-pass
tests run the upstream test suite for the affected package and the linter, to
guard against regressions in unrelated code.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
TEST_DIR = Path(__file__).parent
PKG_TEST_EXTENSIONS_DIR = (
    REPO / "packages" / "agents-core" / "test" / "extensions"
)
REGRESSION_SRC = TEST_DIR / "handoffFilters.regression.test.ts"
REGRESSION_DEST = PKG_TEST_EXTENSIONS_DIR / "handoffFilters.regression.test.ts"


def _ensure_regression_test_installed() -> None:
    PKG_TEST_EXTENSIONS_DIR.mkdir(parents=True, exist_ok=True)
    shutil.copy(REGRESSION_SRC, REGRESSION_DEST)


def _run(cmd, timeout=600, env_overrides=None):
    env = os.environ.copy()
    env.setdefault("CI", "1")
    env.setdefault("NODE_ENV", "test")
    if env_overrides:
        env.update(env_overrides)
    return subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: behavioral regression coverage for the PR
# ---------------------------------------------------------------------------


def test_removeAllTools_filters_reasoning_and_approval_items():
    """removeAllTools must drop reasoning items and tool-approval placeholders.

    Runs a vitest regression suite that constructs RunReasoningItem and
    RunToolApprovalItem instances plus a `type: 'reasoning'` input entry and
    asserts they are removed by the filter helper. Fails on the base commit
    because the source code only filters tool-call/handoff/tool-search items.
    """
    _ensure_regression_test_installed()
    rel = REGRESSION_DEST.relative_to(REPO).as_posix()
    r = _run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--project",
            "@openai/agents-core",
            rel,
        ],
        timeout=600,
    )
    combined = (r.stdout or "") + "\n" + (r.stderr or "")
    assert r.returncode == 0, (
        "vitest regression run failed (code "
        f"{r.returncode}).\n----- stdout (tail) -----\n"
        f"{(r.stdout or '')[-3000:]}\n----- stderr (tail) -----\n"
        f"{(r.stderr or '')[-1500:]}"
    )
    # Sanity check: vitest actually executed our regression file.
    assert "handoffFilters.regression.test.ts" in combined, (
        "vitest output did not reference the regression test file:\n"
        + combined[-1500:]
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: existing repository checks must still hold
# ---------------------------------------------------------------------------


def test_repo_handoff_filters_unit_tests_pass():
    """The original handoffFilters.test.ts suite must keep passing.

    This guards against a fix that breaks the previously-asserted behavior
    (e.g. accidentally removing handoff items twice or dropping plain
    messages).
    """
    rel = "packages/agents-core/test/extensions/handoffFilters.test.ts"
    r = _run(
        ["pnpm", "exec", "vitest", "run", "--project", "@openai/agents-core", rel],
        timeout=600,
    )
    assert r.returncode == 0, (
        "Original handoffFilters tests failed (code "
        f"{r.returncode}).\nstdout tail:\n{(r.stdout or '')[-2000:]}\n"
        f"stderr tail:\n{(r.stderr or '')[-1000:]}"
    )


def test_repo_agents_core_typecheck():
    """`pnpm -F @openai/agents-core build-check` must pass.

    Validates that the changes still type-check across packages, tests and
    examples consumed by agents-core.
    """
    r = _run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        timeout=600,
    )
    assert r.returncode == 0, (
        "build-check (tsc --noEmit) failed (code "
        f"{r.returncode}).\nstdout tail:\n{(r.stdout or '')[-2000:]}\n"
        f"stderr tail:\n{(r.stderr or '')[-1000:]}"
    )
