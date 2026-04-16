#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
Tests for apache/airflow#64893: SearchBar debounce callback not cancelled on clear.

The bug: When a user types in the SearchBar and immediately clears it, the pending
debounced onChange callback is not cancelled. After the debounce delay, the old
value is applied, causing the cleared input to revert to the previous search term.

The fix: Cancel the pending debounce before calling onChange("") when clearing.
"""
import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/airflow")
UI_DIR = REPO / "airflow-core" / "src" / "airflow" / "ui"
TEST_FILE = UI_DIR / "src" / "components" / "SearchBar.test.tsx"

# The test file patch from the PR - adds regression tests for the debounce bug
TEST_PATCH = r'''
--- a/airflow-core/src/airflow/ui/src/components/SearchBar.test.tsx
+++ b/airflow-core/src/airflow/ui/src/components/SearchBar.test.tsx
@@ -16,16 +16,22 @@
  * specific language governing permissions and limitations
  * under the License.
  */
-import { fireEvent, render, screen, waitFor } from "@testing-library/react";
-import { describe, it, expect, vi } from "vitest";
+import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
+import { afterEach, describe, expect, it, vi } from "vitest";

 import { Wrapper } from "src/utils/Wrapper";

 import { SearchBar } from "./SearchBar";

+afterEach(() => {
+  vi.useRealTimers();
+});
+
 describe("Test SearchBar", () => {
   it("Renders and clear button works", async () => {
-    render(<SearchBar defaultValue="" onChange={vi.fn()} placeholder="Search Dags" />, {
+    const onChange = vi.fn();
+
+    render(<SearchBar defaultValue="" onChange={onChange} placeholder="Search Dags" />, {
       wrapper: Wrapper,
     });

@@ -44,5 +50,35 @@ describe("Test SearchBar", () => {
     fireEvent.click(clearButton);

     expect((input as HTMLInputElement).value).toBe("");
+    expect(onChange).toHaveBeenCalledWith("");
+  });
+
+  it("cancels pending debounced changes when clearing", () => {
+    vi.useFakeTimers();
+
+    const onChange = vi.fn();
+
+    render(<SearchBar defaultValue="" onChange={onChange} placeholder="Search Dags" />, {
+      wrapper: Wrapper,
+    });
+
+    const input = screen.getByTestId("search-dags");
+
+    fireEvent.change(input, { target: { value: "air" } });
+
+    expect((input as HTMLInputElement).value).toBe("air");
+    expect(onChange).not.toHaveBeenCalled();
+
+    fireEvent.click(screen.getByTestId("clear-search"));
+
+    expect((input as HTMLInputElement).value).toBe("");
+    expect(onChange).toHaveBeenCalledTimes(1);
+    expect(onChange).toHaveBeenNthCalledWith(1, "");
+
+    act(() => {
+      vi.advanceTimersByTime(200);
+    });
+
+    expect(onChange).toHaveBeenCalledTimes(1);
   });
 });
'''


def _ensure_test_file_patched():
    """
    Ensure the test file has the regression tests from the PR.
    """
    content = TEST_FILE.read_text()
    if "cancels pending debounced changes when clearing" in content:
        return  # Already patched

    result = subprocess.run(
        ["patch", "-p1", "--forward"],
        input=TEST_PATCH,
        cwd=REPO,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"Patch output: {result.stdout}\n{result.stderr}")


def _run_vitest_searchbar():
    """Run all SearchBar tests and return (returncode, stdout, stderr)."""
    _ensure_test_file_patched()

    result = subprocess.run(
        [
            "pnpm", "run", "test", "--",
            "--reporter=verbose",
            "src/components/SearchBar.test.tsx"
        ],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.returncode, result.stdout, result.stderr


def _searchbar_file_all_passed(output: str) -> bool:
    """
    Check if all SearchBar tests passed based on file summary.

    When all tests pass, vitest shows:
      ✓ src/components/SearchBar.test.tsx (2 tests) 142ms

    When some fail, it shows:
      ❯ src/components/SearchBar.test.tsx (2 tests | 1 failed) 142ms
    """
    # Look for SearchBar.test.tsx with checkmark and no "failed"
    pattern = r"[✓✔]\s+src/components/SearchBar\.test\.tsx.*tests\)"
    if re.search(pattern, output):
        # Make sure it doesn't say "failed"
        fail_pattern = r"SearchBar\.test\.tsx.*failed"
        return not re.search(fail_pattern, output)
    return False


def _test_failed_in_output(output: str, test_name: str) -> bool:
    """Check if a specific test failed in vitest output."""
    # Look for the X/× pattern for failing tests with the test name
    pattern = rf"[×✕✗]\s+.*{re.escape(test_name)}"
    return bool(re.search(pattern, output))


def test_searchbar_debounce_cancel_on_clear():
    """
    Fail-to-pass: Verify that clearing SearchBar cancels pending debounced callbacks.

    BUG BEHAVIOR (base commit):
    - Clear button calls onChange("")
    - After 200ms, debounced handler fires, calling onChange("air")
    - Result: onChange called TWICE

    FIXED BEHAVIOR:
    - Clear button calls handleSearchChange.cancel() then onChange("")
    - After 200ms, nothing happens (debounce was cancelled)
    - Result: onChange called ONCE with ""

    This test FAILS on base commit and PASSES after the fix.
    """
    returncode, stdout, stderr = _run_vitest_searchbar()

    print("STDOUT:", stdout[-3000:] if len(stdout) > 3000 else stdout)
    print("STDERR:", stderr[-1000:] if len(stderr) > 1000 else stderr)

    test_name = "cancels pending debounced changes when clearing"

    # This test passes if:
    # 1. All SearchBar tests passed (file summary shows ✓), OR
    # 2. The specific test doesn't show as failed
    all_passed = _searchbar_file_all_passed(stdout)
    specific_failed = _test_failed_in_output(stdout, test_name)

    passed = all_passed or (returncode == 0 and not specific_failed)

    assert passed, (
        f"SearchBar debounce cancel test failed. "
        f"Expected onChange to be called exactly once after clear + timer advance."
    )


def test_searchbar_clear_button_works():
    """
    Pass-to-pass: Verify clear button resets input value and calls onChange.

    This tests basic clear button functionality. It passes on both base and fixed
    versions because onChange("") is called when clicking clear in both cases.
    """
    returncode, stdout, stderr = _run_vitest_searchbar()

    print("STDOUT:", stdout[-3000:] if len(stdout) > 3000 else stdout)
    print("STDERR:", stderr[-1000:] if len(stderr) > 1000 else stderr)

    test_name = "Renders and clear button works"

    # This test passes if:
    # 1. All SearchBar tests passed, OR
    # 2. The specific test doesn't show as failed
    all_passed = _searchbar_file_all_passed(stdout)
    specific_failed = _test_failed_in_output(stdout, test_name)

    passed = all_passed or not specific_failed

    assert passed, f"SearchBar clear button test failed"


def test_searchbar_all_tests_pass():
    """
    Pass-to-pass: All SearchBar component tests pass together.

    This checks the overall test run succeeds (exit code 0).
    """
    returncode, stdout, stderr = _run_vitest_searchbar()

    print("STDOUT:", stdout[-3000:] if len(stdout) > 3000 else stdout)
    print("STDERR:", stderr[-1000:] if len(stderr) > 1000 else stderr)

    assert returncode == 0, f"SearchBar tests had failures:\n{stdout[-1000:]}"


def test_lint_passes():
    """
    Pass-to-pass: ESLint and TypeScript type checking pass.

    The `pnpm run lint` command runs both ESLint and tsc.
    """
    result = subprocess.run(
        ["pnpm", "run", "lint"],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=180
    )

    print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print("STDERR:", result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)

    assert result.returncode == 0, f"Lint/typecheck failed:\n{result.stdout[-1000:]}"


def test_prettier_format_check():
    """
    Pass-to-pass: Prettier code formatting is consistent.

    This checks that all source files match the project's Prettier configuration.
    """
    result = subprocess.run(
        ["npx", "prettier", "--check", "."],
        cwd=UI_DIR,
        capture_output=True,
        text=True,
        timeout=120
    )

    print("STDOUT:", result.stdout[-2000:] if len(result.stdout) > 2000 else result.stdout)
    print("STDERR:", result.stderr[-1000:] if len(result.stderr) > 1000 else result.stderr)

    assert result.returncode == 0, f"Prettier check failed:\n{result.stdout[-1000:]}"


if __name__ == "__main__":
    sys.exit(subprocess.call(["pytest", __file__, "-v", "--tb=short"]))
