"""
Test suite for remix-run/remix#11113: disposed roots stop forwarding DOM error events.

Strategy: write a self-contained .tsx test file into the repo's test directory,
run vitest once, parse the JSON results, and have one pytest function per
assertion.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path("/workspace/remix")
COMPONENT_DIR = REPO / "packages" / "component"
TEST_DIR = COMPONENT_DIR / "src" / "test"
INSTALLED_FIXTURE = TEST_DIR / "vdom.dispose-task.test.tsx"
VITEST_OUT = Path("/tmp/vitest_results.json")

TASK_TEST_FIXTURE = """\
import { describe, it, expect } from 'vitest'
import { createRoot, createRangeRoot } from '../lib/vdom.ts'

describe('task: disposed roots stop forwarding DOM error events', () => {
  it('createRoot dispose stops forwarding bubbling DOM error events', () => {
    let container = document.createElement('div')
    let root = createRoot(container)
    let forwarded: unknown
    root.addEventListener('error', (event) => {
      forwarded = (event as ErrorEvent).error
    })

    root.dispose()

    container.dispatchEvent(
      new ErrorEvent('error', { bubbles: true, error: new Error('after dispose root') }),
    )

    expect(forwarded).toBeUndefined()
  })

  it('createRangeRoot dispose stops forwarding bubbling DOM error events', () => {
    let host = document.createElement('div')
    let start = document.createComment('start')
    let end = document.createComment('end')
    host.append(start, end)

    let root = createRangeRoot([start, end])
    let forwarded: unknown
    root.addEventListener('error', (event) => {
      forwarded = (event as ErrorEvent).error
    })

    root.dispose()

    host.dispatchEvent(
      new ErrorEvent('error', { bubbles: true, error: new Error('after dispose range') }),
    )

    expect(forwarded).toBeUndefined()
  })

  it('createRoot still forwards before dispose (sanity check)', () => {
    let container = document.createElement('div')
    let root = createRoot(container)
    let forwarded: unknown
    root.addEventListener('error', (event) => {
      forwarded = (event as ErrorEvent).error
    })

    let expected = new Error('before dispose')
    container.dispatchEvent(new ErrorEvent('error', { bubbles: true, error: expected }))

    expect(forwarded).toBe(expected)
  })

  it('createRangeRoot still forwards before dispose (sanity check)', () => {
    let host = document.createElement('div')
    let start = document.createComment('start')
    let end = document.createComment('end')
    host.append(start, end)

    let root = createRangeRoot([start, end])
    let forwarded: unknown
    root.addEventListener('error', (event) => {
      forwarded = (event as ErrorEvent).error
    })

    let expected = new Error('before dispose range')
    host.dispatchEvent(new ErrorEvent('error', { bubbles: true, error: expected }))

    expect(forwarded).toBe(expected)
  })

  it('multiple dispose calls do not throw', () => {
    let container = document.createElement('div')
    let root = createRoot(container)
    expect(() => {
      root.dispose()
      root.dispose()
      root.dispose()
    }).not.toThrow()
  })
})
"""


@pytest.fixture(scope="session")
def vitest_results():
    INSTALLED_FIXTURE.write_text(TASK_TEST_FIXTURE)

    targets = [
        "src/test/vdom.dispose-task.test.tsx",
        "src/test/vdom.errors.test.tsx",
        "src/test/vdom.range-root.test.tsx",
    ]
    cmd = [
        "pnpm", "exec", "vitest", "run",
        *targets,
        "--reporter=json",
        f"--outputFile={VITEST_OUT}",
    ]
    env = dict(os.environ)
    env.setdefault("CI", "1")
    proc = subprocess.run(
        cmd, cwd=str(COMPONENT_DIR), capture_output=True, text=True, timeout=600, env=env
    )

    if not VITEST_OUT.exists():
        raise RuntimeError(
            f"vitest did not produce JSON output.\n"
            f"stdout:\n{proc.stdout[-2000:]}\n"
            f"stderr:\n{proc.stderr[-2000:]}"
        )

    # Remove fixture file so that subsequent CI test runs (which run all
    # component tests) only execute the upstream test suite, not our
    # fail-to-pass fixture.
    INSTALLED_FIXTURE.unlink(missing_ok=True)

    with VITEST_OUT.open() as f:
        data = json.load(f)
    return data


def _find_test(results, name_substring: str):
    for tr in results.get("testResults", []):
        for t in tr.get("assertionResults", []):
            full = t.get("fullName") or t.get("title") or ""
            if name_substring in full:
                return t
    return None


def _assert_passed(results, name_substring: str):
    t = _find_test(results, name_substring)
    assert t is not None, (
        f"Could not find test matching {name_substring!r}. "
        f"Available tests: "
        f"{[a.get('fullName') for tr in results.get('testResults', []) for a in tr.get('assertionResults', [])]}"
    )
    status = t.get("status")
    assert status == "passed", (
        f"Test {name_substring!r} status={status!r}. "
        f"Failure: {t.get('failureMessages', [])}"
    )


# ---------------- f2p (fail-to-pass) tests ----------------

def test_createroot_dispose_stops_forwarding(vitest_results):
    """f2p: After createRoot.dispose(), bubbling DOM error events must not be forwarded."""
    _assert_passed(vitest_results, "createRoot dispose stops forwarding bubbling DOM error events")


def test_createrangeroot_dispose_stops_forwarding(vitest_results):
    """f2p: After createRangeRoot.dispose(), bubbling DOM error events must not be forwarded."""
    _assert_passed(
        vitest_results,
        "createRangeRoot dispose stops forwarding bubbling DOM error events",
    )


def test_createroot_still_forwards_before_dispose(vitest_results):
    """f2p: before dispose, error events must still be forwarded (no over-fix)."""
    _assert_passed(vitest_results, "createRoot still forwards before dispose")


def test_createrangeroot_still_forwards_before_dispose(vitest_results):
    """f2p: before dispose, range-root error events must still be forwarded."""
    _assert_passed(vitest_results, "createRangeRoot still forwards before dispose")


def test_multiple_dispose_calls_safe(vitest_results):
    """f2p: idempotent dispose — calling dispose() multiple times must not throw."""
    _assert_passed(vitest_results, "multiple dispose calls do not throw")


# ---------------- p2p (pass-to-pass) tests from upstream ----------------

def test_p2p_existing_error_forwarding(vitest_results):
    """p2p: upstream test for forwards bubbling DOM error events to root listeners."""
    _assert_passed(vitest_results, "forwards bubbling DOM error events to root listeners")


def test_p2p_dispose_no_op_before_render(vitest_results):
    """p2p: upstream test for dispose-before-render is a no-op."""
    _assert_passed(vitest_results, "dispose is a no-op before first render")


def test_p2p_setup_error_dispatches(vitest_results):
    """p2p: setup errors are dispatched as error events on the root."""
    _assert_passed(vitest_results, "dispatches error event when setup throws")


def test_p2p_render_error_dispatches(vitest_results):
    """p2p: render errors are dispatched as error events on the root."""
    _assert_passed(vitest_results, "dispatches error event when render function throws")


def test_p2p_queueTask_error_dispatches(vitest_results):
    """p2p: queueTask errors are dispatched as error events on the root."""
    _assert_passed(vitest_results, "dispatches error event when sync queueTask throws")


def test_p2p_sync_event_handlers(vitest_results):
    """p2p: sync event handlers attached via on() mixin run."""
    _assert_passed(vitest_results, "runs sync event handlers attached via on() mixin")


def test_p2p_range_root_renders_content(vitest_results):
    """p2p: createRangeRoot can render content between markers."""
    _assert_passed(vitest_results, "renders content between markers")


def test_p2p_range_root_forwards_error(vitest_results):
    """p2p: createRangeRoot forwards bubbling DOM error events."""
    _assert_passed(
        vitest_results,
        "forwards bubbling DOM error events to range root listeners",
    )


# ---------------- repo-level p2p check ----------------

def test_repo_typecheck():
    """p2p: tsc --noEmit must succeed for the component package."""
    proc = subprocess.run(
        ["pnpm", "exec", "tsc", "--noEmit"],
        cwd=str(COMPONENT_DIR),
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, (
        f"tsc --noEmit failed.\nstdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")