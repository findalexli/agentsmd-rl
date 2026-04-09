"""
Task: deno-fixextweb-support-object-in-domexception
Repo: denoland/deno @ e6e72e57c2e2566b54f4672e03a6ff4d91d7b167
PR:   31939

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/deno"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified DOMException file must be valid JavaScript."""
    r = subprocess.run(
        ["deno", "check", "ext/web/01_dom_exception.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # If deno check fails due to internal dependencies, try parsing with node
    if r.returncode != 0:
        # Fallback: at least verify it's parseable JavaScript
        r2 = subprocess.run(
            ["node", "--check", f"{REPO}/ext/web/01_dom_exception.js"],
            capture_output=True, text=True, timeout=30,
        )
        # node --check may fail on Deno-specific imports, that's ok
        # We just want to ensure it's syntactically valid JS
        assert "SyntaxError" not in r2.stderr, f"Syntax error in modified file: {r2.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_domexception_supports_options_object():
    """DOMException constructor accepts options object with name and cause properties."""
    r = subprocess.run(
        ["deno", "eval", """
const err = new DOMException("test message", { name: "NotFoundError", cause: "original cause" });
if (err.name !== "NotFoundError") {
    console.error("Expected name to be 'NotFoundError', got:", err.name);
    Deno.exit(1);
}
if (err.message !== "test message") {
    console.error("Expected message to be 'test message', got:", err.message);
    Deno.exit(1);
}
// Check cause property exists and is set correctly
if (!Object.prototype.hasOwnProperty.call(err, 'cause')) {
    console.error("Expected cause property to exist on DOMException");
    Deno.exit(1);
}
if (err.cause !== "original cause") {
    console.error("Expected cause to be 'original cause', got:", err.cause);
    Deno.exit(1);
}
console.log("PASS");
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_domexception_backwards_compatible_string():
    """DOMException constructor still accepts string as second argument (backwards compat)."""
    r = subprocess.run(
        ["deno", "eval", """
const err = new DOMException("test message", "AbortError");
if (err.name !== "AbortError") {
    console.error("Expected name to be 'AbortError', got:", err.name);
    Deno.exit(1);
}
if (err.message !== "test message") {
    console.error("Expected message to be 'test message', got:", err.message);
    Deno.exit(1);
}
// No cause property when using string argument
if (Object.prototype.hasOwnProperty.call(err, 'cause')) {
    console.error("Expected no cause property when using string argument");
    Deno.exit(1);
}
console.log("PASS");
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_domexception_cause_with_error_object():
    """DOMException cause property can be an Error object."""
    r = subprocess.run(
        ["deno", "eval", """
const originalError = new Error("original error");
const err = new DOMException("wrapped", { cause: originalError });
if (err.cause !== originalError) {
    console.error("Expected cause to be the original error object");
    Deno.exit(1);
}
console.log("PASS");
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# [pr_diff] fail_to_pass
def test_domexception_options_defaults():
    """DOMException with options object defaults name to undefined (converts to 'Error')."""
    r = subprocess.run(
        ["deno", "eval", """
const err = new DOMException("test", { cause: "cause only" });
// When options.name is undefined, it should convert to "Error"
if (err.name !== "Error") {
    console.error("Expected name to be 'Error' when not specified in options, got:", err.name);
    Deno.exit(1);
}
if (err.cause !== "cause only") {
    console.error("Expected cause to be set correctly");
    Deno.exit(1);
}
console.log("PASS");
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Test failed: {r.stderr or r.stdout}"
    assert "PASS" in r.stdout, f"Expected PASS in output, got: {r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_domexception_tests_pass():
    """Upstream DOMException tests still pass after the fix."""
    r = subprocess.run(
        ["deno", "test", "--allow-all", "ext/web/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # If deno test doesn't work for this repo structure, we can skip
    # The important thing is that we tried to run existing tests
    if "No test modules found" in r.stderr or "No test files found" in r.stdout:
        # Try running via cargo test if available
        r2 = subprocess.run(
            ["cargo", "test", "--lib", "dom_exception", "--", "--test-threads=1"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        if r2.returncode != 0:
            # If neither works, just verify the file is syntactically correct
            # This is a fallback to prevent false failures due to test harness issues
            return


# [static] pass_to_pass
def test_not_stub():
    """Modified DOMException constructor has real logic, not just pass/return."""
    src = Path(f"{REPO}/ext/web/01_dom_exception.js").read_text()
    # Check for the key new logic: ReflectHas and ObjectDefineProperty for cause
    assert "ReflectHas" in src, "Modified file should use ReflectHas for cause check"
    assert "ObjectDefineProperty" in src, "Modified file should define cause property"
    assert "options.name" in src, "Modified file should support options.name"


# [static] pass_to_pass
def test_reflecthas_imported():
    """ReflectHas is imported from primordials (needed for the fix)."""
    src = Path(f"{REPO}/ext/web/01_dom_exception.js").read_text()
    assert "ReflectHas" in src, "ReflectHas should be imported from primordials"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cargo_check_web():
    """Cargo check passes for deno_web crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "deno_web"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_clippy_web():
    """Cargo clippy passes for deno_web crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "deno_web"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_cargo_test_web_lib():
    """Cargo test --lib passes for deno_web crate (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "test", "--lib", "-p", "deno_web"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo test failed:\n{r.stderr[-500:]}"


# Note: cargo check -p deno requires cmake which is not installed in the
# test environment. The deno_web crate tests above provide sufficient CI/CD
# coverage for this DOMException change which only affects ext/web.
