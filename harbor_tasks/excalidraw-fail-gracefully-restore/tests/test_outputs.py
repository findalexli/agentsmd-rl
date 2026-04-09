"""Test excalidraw restore.ts error handling fix."""

import subprocess
import os

REPO = "/workspace/excalidraw"
RESTORE_TS = "packages/excalidraw/data/restore.ts"


def test_repairBinding_has_error_handling():
    """Verify repairBinding function has try-catch error handling."""
    with open(f"{REPO}/{RESTORE_TS}", "r") as f:
        content = f.read()

    # Find the repairBinding function
    func_start = content.find("const repairBinding = <T extends ExcalidrawArrowElement>")
    if func_start == -1:
        raise AssertionError("repairBinding function not found")

    # Find the end of the function (next top-level function or export)
    func_content = content[func_start:]

    # Check for try block in repairBinding
    assert "try {" in func_content[:2000], \
        "repairBinding must have try-catch block"

    # Check for error logging with contextual message
    assert 'console.error("Error repairing binding:", error)' in func_content or \
           'console.error("Error repairing binding:"' in func_content, \
        "repairBinding must log errors with 'Error repairing binding:' message"


def test_restoreElements_has_error_handling():
    """Verify restoreElements handles element restoration errors gracefully."""
    with open(f"{REPO}/{RESTORE_TS}", "r") as f:
        content = f.read()

    # Find the restoreElements function and check its error handling
    # Look for the try block around restoreElement call
    assert "try {" in content, "restoreElements must have try-catch block"

    # Check for error logging with contextual message
    assert 'console.error("Error restoring element:", error)' in content or \
           'console.error("Error restoring element:"' in content, \
        "restoreElements must log errors with 'Error restoring element:' message"

    # Check that migratedElement is set to null in catch block
    assert "migratedElement = null" in content, \
        "restoreElements must set migratedElement to null when error occurs"


def test_element_with_throwing_property_is_filtered():
    """Test that an element with a throwing property is filtered out during restore."""
    # Create a test TypeScript file that exercises the fix
    test_code = '''
import { describe, it, expect, vi } from "vitest";
import * as restore from "../../data/restore";
import { API } from "../helpers/api";

describe("restoreElements error handling", () => {
  it("should filter out element if restore throws", () => {
    const rect1 = API.createElement({
      type: "rectangle",
      boundElements: [],
    });
    const rect2 = API.createElement({
      type: "rectangle",
      boundElements: [],
    });

    // Define getter that throws
    Object.defineProperty(rect2, "seed", {
      get: () => {
        throw new Error("FORBIDDEN!");
      },
    });

    // Mock console.error to verify it's called
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    const restoredElements = restore.restoreElements([rect1, rect2], null);

    // Should only have 1 element (rect1), rect2 should be filtered out
    expect(restoredElements.length).toBe(1);
    expect(restoredElements[0].id).toBe(rect1.id);

    // Verify error was logged
    expect(consoleSpy).toHaveBeenCalledWith(
      "Error restoring element:",
      expect.any(Error)
    );

    consoleSpy.mockRestore();
  });
});
'''

    # Write the test file
    test_path = f"{REPO}/packages/excalidraw/tests/data/restore_error.test.ts"
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        # Run the specific test
        result = subprocess.run(
            ["yarn", "vitest", "run", "restore_error", "--reporter=json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Check that test passed
        assert result.returncode == 0, f"Test failed: {result.stderr}"

    finally:
        # Cleanup
        if os.path.exists(test_path):
            os.remove(test_path)


def test_arrow_binding_with_invalid_data_is_filtered():
    """Test that arrow element with throwing binding property is filtered out during restore."""
    test_code = '''
import { describe, it, expect, vi } from "vitest";
import * as restore from "../../data/restore";
import { API } from "../helpers/api";

describe("repairBinding error handling", () => {
  it("should filter out arrow element if binding access throws", () => {
    const rect1 = API.createElement({
      type: "rectangle",
      boundElements: [],
    });
    const arrowElement = API.createElement({
      type: "arrow",
      id: "id-arrow01",
      endBinding: {
        elementId: rect1.id,
        fixedPoint: [0.5, 0.5],
        mode: "inside",
      },
    });

    Object.assign(rect1, {
      boundElements: [{ type: "arrow", id: arrowElement.id }],
    });

    // Make endBinding throw when accessed (simulating corrupted data)
    Object.defineProperty(arrowElement, "endBinding", {
      get: () => {
        throw new Error("Invalid binding data!");
      },
    });

    // Mock console.error
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    const restoredElements = restore.restoreElements([arrowElement, rect1], null);

    // Only rect1 should be restored; arrow should be filtered out due to error
    expect(restoredElements.length).toBe(1);
    expect(restoredElements[0].id).toBe(rect1.id);

    // Verify error was logged (could be "Error restoring element:" or "Error repairing binding:")
    const wasCalledWithError = consoleSpy.mock.calls.some(
      (call) => (call[0] === "Error restoring element:" || call[0] === "Error repairing binding:") && call[1] instanceof Error
    );
    expect(wasCalledWithError).toBe(true);

    consoleSpy.mockRestore();
  });
});
'''

    test_path = f"{REPO}/packages/excalidraw/tests/data/binding_error.test.ts"
    with open(test_path, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["yarn", "vitest", "run", "binding_error", "--reporter=json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"Test failed: {result.stderr}"

    finally:
        if os.path.exists(test_path):
            os.remove(test_path)


def test_console_error_includes_context():
    """Verify that console.error includes contextual information about the error."""
    with open(f"{REPO}/{RESTORE_TS}", "r") as f:
        content = f.read()

    # Check that error messages include contextual information
    assert "Error repairing binding:" in content, \
        "Must include 'Error repairing binding:' message"
    assert "Error restoring element:" in content, \
        "Must include 'Error restoring element:' message"

    # Verify the error object is passed to console.error
    assert "console.error" in content, "Must use console.error for logging"


def test_existing_restore_tests_pass():
    """Run the existing restore tests to verify the fix doesn't break anything."""
    result = subprocess.run(
        ["yarn", "vitest", "run", "restore", "--reporter=json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    # Check that tests passed
    if result.returncode != 0:
        # Try to parse output for more details
        output = result.stdout + result.stderr
        assert False, f"Existing restore tests failed: {output[:2000]}"


def test_typescript_compiles():
    """Verify TypeScript compiles without errors."""
    result = subprocess.run(
        ["yarn", "test:typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"TypeScript type check failed: {result.stderr}"


def test_repo_lint_passes():
    """Repo's ESLint check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:code"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint check failed:\n{r.stderr[-500:]}"


def test_repo_prettier_passes():
    """Repo's Prettier formatting check passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:other"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_repo_full_test_suite_passes():
    """Repo's full test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["yarn", "test:app", "--watch=false"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Test suite failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
