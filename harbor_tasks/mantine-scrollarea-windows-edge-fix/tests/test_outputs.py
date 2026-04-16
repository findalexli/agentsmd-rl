"""
Behavioral tests for mantine ScrollAreaViewport Windows Edge fix.

Tests verify actual runtime behavior by rendering the component with
@testing-library/react inside Jest and checking wheel event handling:
- Propagation stops at vertical scroll boundaries when shift-scrolling
  with horizontal scroll enabled
- User's onWheel handler is still forwarded
- Propagation is NOT stopped when conditions aren't met
"""

import subprocess
import json
import os
import shutil
import pytest

REPO = "/workspace/mantine"
TARGET_FILE = "packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport/ScrollAreaViewport.tsx"
JEST_TEST_SRC = "/tests/scroll_viewport_behavior.test.tsx"
JEST_TEST_DST = os.path.join(
    REPO,
    "packages/@mantine/core/src/components/ScrollArea/ScrollAreaViewport",
    "viewport_wheel_behavioral.test.tsx",
)

# Map pytest f2p test names → Jest test titles
JEST_TEST_MAP = {
    "test_onwheel_prop_extracted": "onwheel_prop_forwarding",
    "test_handlewheel_function_exists": "wheel_handler_active",
    "test_handlewheel_calls_onwheel": "onwheel_forwarded_with_boundary_behavior",
    "test_stoppropagation_at_boundaries": "stops_at_both_boundaries",
    "test_shiftkey_check": "shiftkey_required",
    "test_scrollbarXEnabled_in_handlewheel_condition": "scrollbar_x_required",
    "test_handlewheel_attached_to_box": "handler_on_rendered_element",
    "test_horizontal_scroll_check": "horizontal_scroll_required",
    "test_viewport_boundaries_logic": "boundary_detection_logic",
}


@pytest.fixture(scope="session")
def behavioral_results():
    """Run behavioral Jest tests once and return per-test pass/fail results."""
    shutil.copy2(JEST_TEST_SRC, JEST_TEST_DST)
    result_file = "/tmp/jest_behavioral_results.json"
    try:
        r = subprocess.run(
            [
                "npx", "jest",
                "--testPathPatterns=viewport_wheel_behavioral",
                "--json",
                f"--outputFile={result_file}",
                "--forceExit",
                "--testTimeout=30000",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )

        with open(result_file) as f:
            data = json.load(f)

        results = {}
        for suite in data.get("testResults", []):
            for test in suite.get("assertionResults", []):
                results[test["title"]] = {
                    "status": test["status"],
                    "message": "\n".join(test.get("failureMessages", [])),
                }

        return results
    except Exception as e:
        return {"_error": str(e)}
    finally:
        if os.path.exists(JEST_TEST_DST):
            os.remove(JEST_TEST_DST)


def _assert_behavioral_test(behavioral_results, pytest_name):
    """Helper: assert a specific behavioral Jest test passed."""
    if "_error" in behavioral_results:
        pytest.fail(f"Jest behavioral tests failed to run: {behavioral_results['_error']}")

    jest_title = JEST_TEST_MAP[pytest_name]
    result = behavioral_results.get(jest_title)
    if result is None:
        pytest.fail(f"Behavioral test '{jest_title}' not found in Jest results")
    assert result["status"] == "passed", (
        f"Behavioral test '{jest_title}' failed:\n{result['message'][:500]}"
    )


# ===== Fail-to-pass behavioral tests =====


def test_onwheel_prop_extracted(behavioral_results):
    """onWheel prop is forwarded AND propagation stops at boundary (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_onwheel_prop_extracted")


def test_handlewheel_function_exists(behavioral_results):
    """Wheel handler stops propagation at boundary, allows at non-boundary (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_handlewheel_function_exists")


def test_handlewheel_calls_onwheel(behavioral_results):
    """onWheel prop called even when propagation is stopped at boundary (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_handlewheel_calls_onwheel")


def test_stoppropagation_at_boundaries(behavioral_results):
    """Propagation stops at top and bottom boundaries, continues in middle (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_stoppropagation_at_boundaries")


def test_shiftkey_check(behavioral_results):
    """Shift key required: stops with shift at boundary, propagates without (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_shiftkey_check")


def test_scrollbarXEnabled_in_handlewheel_condition(behavioral_results):
    """scrollbarXEnabled required: stops when enabled at boundary, propagates when disabled (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_scrollbarXEnabled_in_handlewheel_condition")


def test_handlewheel_attached_to_box(behavioral_results):
    """Wheel handler on rendered element stops propagation at boundary (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_handlewheel_attached_to_box")


def test_horizontal_scroll_check(behavioral_results):
    """Horizontal scrollability required: stops when scrollable, propagates when not (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_horizontal_scroll_check")


def test_viewport_boundaries_logic(behavioral_results):
    """Boundary detection correct: scrollTop<1 is top, scrollTop>=sH-cH-1 is bottom (fail_to_pass)."""
    _assert_behavioral_test(behavioral_results, "test_viewport_boundaries_logic")


# ===== Pass-to-pass tests =====


def test_typescript_compilation():
    """TypeScript compilation passes for the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180,
    )
    if r.returncode != 0 and ("Command failed" in r.stderr or "not found" in r.stderr):
        pytest.skip("Monorepo typecheck unavailable")
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_eslint():
    """Repo's ESLint passes on the modified file (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", TARGET_FILE, "--max-warnings=0"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier check passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "prettier:test"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_syncpack():
    """Repo's syncpack version consistency passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "syncpack"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Syncpack check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_jest_scrollarea():
    """Repo's Jest tests for ScrollArea pass (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "jest", "--testPathPatterns=ScrollArea\\.test", "--testTimeout=30000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Jest tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
