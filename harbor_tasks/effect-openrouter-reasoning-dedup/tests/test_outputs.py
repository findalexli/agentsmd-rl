"""Behavioural tests for effect-ts/effect#6060.

The PR fixes a duplicate-emission bug in `makeStreamResponse` of
`@effect/ai-openrouter`: when a stream delta carries both `reasoning` and
`reasoning_details`, the old code emitted a reasoning part for each, doubling
every token. The fix turns the second `if` into an `else if`.

We compile and execute the function in-tree via vitest. The test file
`StreamReasoningDedup.test.ts` is co-located with this file and is copied into
`packages/ai/openrouter/test/` before vitest is invoked.
"""

import json
import os
import shutil
import subprocess
import pytest

REPO = "/workspace/effect"
OPENROUTER_PKG = os.path.join(REPO, "packages/ai/openrouter")
TEST_FILE_NAME = "StreamReasoningDedup.test.ts"
TEST_SRC = os.path.join(os.path.dirname(__file__), TEST_FILE_NAME)
TEST_DIR = os.path.join(OPENROUTER_PKG, "test")
TEST_DST = os.path.join(TEST_DIR, TEST_FILE_NAME)
RESULTS_PATH = "/tmp/vitest-results.json"


@pytest.fixture(scope="session")
def vitest_results():
    """Run the dedup test file once and parse the per-test pass/fail result."""
    os.makedirs(TEST_DIR, exist_ok=True)
    shutil.copyfile(TEST_SRC, TEST_DST)

    if os.path.exists(RESULTS_PATH):
        os.remove(RESULTS_PATH)

    cmd = [
        "pnpm", "vitest", "run",
        f"test/{TEST_FILE_NAME}",
        "--reporter=json",
        f"--outputFile={RESULTS_PATH}",
    ]
    proc = subprocess.run(
        cmd, cwd=OPENROUTER_PKG, capture_output=True, text=True, timeout=300
    )
    if not os.path.exists(RESULTS_PATH):
        raise AssertionError(
            f"vitest did not produce {RESULTS_PATH}.\n"
            f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
        )
    with open(RESULTS_PATH) as f:
        report = json.load(f)

    by_name: dict[str, dict] = {}
    for suite in report.get("testResults", []):
        for assertion in suite.get("assertionResults", []):
            full = " > ".join(assertion.get("ancestorTitles", []) + [assertion["title"]])
            by_name[full] = assertion
    if not by_name:
        raise AssertionError(
            f"No assertions parsed from vitest report.\n"
            f"Report: {json.dumps(report)[:2000]}"
        )
    return by_name


def _assert_test_passed(results: dict, suffix: str) -> None:
    matches = [name for name in results if name.endswith(suffix)]
    assert matches, (
        f"vitest report does not contain a test ending with: {suffix!r}.\n"
        f"Available tests:\n  - " + "\n  - ".join(sorted(results.keys()))
    )
    assert len(matches) == 1, f"Multiple matches for {suffix!r}: {matches}"
    result = results[matches[0]]
    status = result.get("status")
    if status != "passed":
        msgs = result.get("failureMessages") or []
        raise AssertionError(
            f"Vitest test {matches[0]!r} did not pass (status={status!r}).\n"
            f"Failure messages:\n" + "\n".join(msgs)[-2000:]
        )


def test_no_duplicate_reasoning_when_both_present(vitest_results):
    """fail-to-pass: bug reproduction. With both fields present, only ONE
    reasoning-delta should be emitted (not two)."""
    _assert_test_passed(
        vitest_results,
        "does NOT emit reasoning twice when both `reasoning` and `reasoning_details` are present",
    )


def test_uses_reasoning_details_when_both_present(vitest_results):
    """fail-to-pass: when both are present with DIFFERENT content, the
    `reasoning_details` value must be the one emitted (not `reasoning`)."""
    _assert_test_passed(
        vitest_results,
        "uses `reasoning_details` only when both are present (different content)",
    )


def test_dedup_across_multiple_chunks(vitest_results):
    """fail-to-pass: the dedup must hold across a multi-chunk stream."""
    _assert_test_passed(
        vitest_results,
        "dedups across multiple consecutive deltas that all carry both fields",
    )


def test_fallback_to_reasoning_when_details_absent(vitest_results):
    """pass-to-pass: the `reasoning` field still works when
    `reasoning_details` is undefined."""
    _assert_test_passed(
        vitest_results,
        "falls back to `reasoning` when `reasoning_details` is absent",
    )


def test_fallback_to_reasoning_when_details_empty(vitest_results):
    """pass-to-pass: an EMPTY `reasoning_details` array must still allow the
    `reasoning` fallback to fire."""
    _assert_test_passed(
        vitest_results,
        "falls back to `reasoning` when `reasoning_details` is an empty array",
    )


def test_no_reasoning_emitted_when_neither_present(vitest_results):
    """pass-to-pass: with neither field present, no reasoning parts are emitted."""
    _assert_test_passed(
        vitest_results,
        "does not emit reasoning at all when both fields are absent",
    )


def test_repo_typecheck_openrouter():
    """pass-to-pass (repo CI): the openrouter package still type-checks."""
    proc = subprocess.run(
        ["pnpm", "check"],
        cwd=OPENROUTER_PKG, capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, (
        f"`pnpm check` failed (rc={proc.returncode}).\n"
        f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
    )


def test_repo_lint_openrouter():
    """pass-to-pass (repo CI): the openrouter sources lint cleanly."""
    proc = subprocess.run(
        ["pnpm", "lint", "packages/ai/openrouter/src"],
        cwd=REPO, capture_output=True, text=True, timeout=600,
    )
    assert proc.returncode == 0, (
        f"`pnpm lint` failed (rc={proc.returncode}).\n"
        f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
    )


def test_changeset_added():
    """pass-to-pass (repo convention): AGENTS.md mandates a changeset for
    every PR. Verify a new changeset file exists that mentions
    `@effect/ai-openrouter`.
    """
    changeset_dir = os.path.join(REPO, ".changeset")
    candidates = []
    for name in os.listdir(changeset_dir):
        if not name.endswith(".md") or name == "README.md":
            continue
        path = os.path.join(changeset_dir, name)
        with open(path) as f:
            text = f.read()
        if "@effect/ai-openrouter" in text:
            candidates.append(name)
    assert candidates, (
        f"No new changeset file under {changeset_dir} mentions "
        f"`@effect/ai-openrouter`. Per AGENTS.md, every PR must include a "
        f"changeset in `.changeset/`."
    )
