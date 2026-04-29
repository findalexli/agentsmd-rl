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

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm test
# 0 fail→pass + 45 pass→pass test name(s) discovered.

def test_exec_p2p_chromium_src_lib_mixins_animate_layout_mixin_test_tsx_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/animate-layout-mixin.test.tsx (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_animate_mixins_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/animate-mixins.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_css_mixin_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/css-mixin.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_keys_mixin_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/keys-mixin.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_on_mixin_test_tsx_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/on-mixin.test.tsx (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_press_mixin_test_tsx_12_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/press-mixin.test.tsx (12 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_lib_mixins_ref_mixin_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/lib/mixins/ref-mixin.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_client_entry_test_tsx_20_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/client-entry.test.tsx (20 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_create_element_test_ts_1_test(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/create-element.test.ts (1 test)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_diff_dom_test_tsx_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/diff-dom.test.tsx (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_document_state_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/document-state.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_event_listeners_test_tsx_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/event-listeners.test.tsx (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_frame_test_tsx_40_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/frame.test.tsx (40 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_attributes_test_tsx_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.attributes.test.tsx (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_boolean_attrs_test_tsx_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.boolean-attrs.test.tsx (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_components_test_tsx_13_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.components.test.tsx (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_css_test_tsx_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.css.test.tsx (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_extra_nodes_test_tsx_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.extra-nodes.test.tsx (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_forms_test_tsx_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.forms.test.tsx (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_mismatch_test_tsx_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.mismatch.test.tsx (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_text_test_tsx_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.text.test.tsx (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_hydration_void_elements_test_tsx_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/hydration.void-elements.test.tsx (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_jsx_test_tsx_12_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/jsx.test.tsx (12 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_spring_test_ts_25_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/spring.test.ts (25 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_stream_test_tsx_86_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/stream.test.tsx (86 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_style_test_ts_4_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/style.test.ts (4 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_stylesheet_test_ts_11_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/stylesheet.test.ts (11 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_components_test_tsx_6_tests_1_skipped(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.components.test.tsx (6 tests | 1 skipped)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_connect_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.connect.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_context_test_tsx_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.context.test.tsx (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_controlled_props_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.controlled-props.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_dom_order_test_tsx_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.dom-order.test.tsx (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_elements_fragments_test_tsx_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.elements-fragments.test.tsx (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_errors_test_tsx_16_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.errors.test.tsx (16 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_events_test_tsx_3_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.events.test.tsx (3 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_insert_remove_test_tsx_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.insert-remove.test.tsx (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_keys_test_tsx_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.keys.test.tsx (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_mixins_test_tsx_16_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.mixins.test.tsx (16 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_props_test_tsx_33_tests_21_skipped(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.props.test.tsx (33 tests | 21 skipped)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_range_root_test_tsx_22_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.range-root.test.tsx (22 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_replacements_test_tsx_21_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.replacements.test.tsx (21 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_scheduler_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.scheduler.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_signals_test_tsx_5_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.signals.test.tsx (5 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_svg_test_tsx_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.svg.test.tsx (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_chromium_src_test_vdom_tasks_test_tsx_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): ' chromium  src/test/vdom.tasks.test.tsx (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

