"""
Task: workers-sdk-vite-module-runner-memory-leak
Repo: workers-sdk @ 9fcdfca775d3d412abe7547d0833414599bab221
PR:   13087

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
TARGET = Path(REPO) / "packages/vite-plugin-cloudflare/src/workers/runner-worker/module-runner.ts"


def _extract_function(source: str, name: str):
    """Extract a function/method from TypeScript source.

    Returns (full_text, body_with_braces) where body_with_braces is just { ... }.
    """
    for prefix in [f"async function {name}", f"function {name}"]:
        idx = source.find(prefix)
        if idx != -1:
            break
    else:
        idx = source.find(f"async {name}(")
        assert idx != -1, f"Could not find function/method '{name}'"

    func_start = idx

    paren_depth = 0
    opening_brace = -1
    for i in range(func_start, len(source)):
        if source[i] == "(":
            paren_depth += 1
        elif source[i] == ")":
            paren_depth -= 1
        elif source[i] == "{" and paren_depth == 0:
            opening_brace = i
            break

    assert opening_brace != -1, f"Could not find opening brace of '{name}'"

    brace_depth = 0
    closing_brace = -1
    for i in range(opening_brace, len(source)):
        if source[i] == "{":
            brace_depth += 1
        elif source[i] == "}":
            brace_depth -= 1
            if brace_depth == 0:
                closing_brace = i + 1
                break

    assert closing_brace != -1, f"Could not find closing brace of '{name}'"

    full_text = source[func_start:closing_brace]
    body_with_braces = source[opening_brace:closing_brace]
    return full_text, body_with_braces


def _setup_pnpm():
    """Install pnpm globally and install dependencies."""
    # Install pnpm
    subprocess.run(
        ["npm", "install", "-g", "pnpm@9.12.0"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install dependencies (lockfile should be up to date from base commit)
    subprocess.run(
        ["pnpm", "install"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Modified file must parse and contain expected structure."""
    source = TARGET.read_text()
    assert "async function runInRunnerObject" in source, "runInRunnerObject function missing"
    assert "class __VITE_RUNNER_OBJECT__" in source, "DurableObject class missing"
    assert "executeCallback" in source, "executeCallback method missing"
    assert source.count("{") == source.count("}"), "Unbalanced braces in source file"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cleanup_on_error():
    """pendingCallbacks and callbackResults must be cleaned up when executeCallback throws."""
    source = TARGET.read_text()
    _, body = _extract_function(source, "runInRunnerObject")

    # Build a plain-JS version of the function (body has no TS type annotations)
    js_func = f"async function runInRunnerObject(env, callback) {body}"

    test_js = (
        "const pendingCallbacks = new Map();\n"
        "const callbackResults = new Map();\n"
        "let nextCallbackId = 0;\n\n"
        + js_func
        + "\n\n"
        + r"""
async function main() {
    // === ERROR PATH (f2p) ===
    // Simulates RPC failure where executeCallback never completes
    const envError = {
        __VITE_RUNNER_OBJECT__: {
            get() {
                return {
                    async executeCallback(id) {
                        throw new Error("simulated RPC failure");
                    }
                };
            }
        }
    };

    // Multiple error calls to detect accumulation
    for (const val of ["a", "b", "c", "d", "e"]) {
        try {
            await runInRunnerObject(envError, async () => val);
        } catch (e) {
            // Expected: error should propagate
        }
    }

    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks leaked " + pendingCallbacks.size + " entries after errors");
        process.exit(1);
    }
    if (callbackResults.size !== 0) {
        console.error("FAIL: callbackResults leaked " + callbackResults.size + " entries after errors");
        process.exit(1);
    }

    // === SUCCESS PATH ===
    // Mock executeCallback that runs the callback but does NOT clean pendingCallbacks
    // (runInRunnerObject must handle all cleanup itself)
    const envSuccess = {
        __VITE_RUNNER_OBJECT__: {
            get() {
                return {
                    async executeCallback(id) {
                        const cb = pendingCallbacks.get(id);
                        if (!cb) throw new Error("No pending callback with id " + id);
                        const result = await cb();
                        callbackResults.set(id, result);
                    }
                };
            }
        }
    };

    const r1 = await runInRunnerObject(envSuccess, async () => 42);
    if (r1 !== 42) {
        console.error("FAIL: expected 42, got " + r1);
        process.exit(1);
    }

    const r2 = await runInRunnerObject(envSuccess, async () => "hello");
    if (r2 !== "hello") {
        console.error("FAIL: expected 'hello', got " + r2);
        process.exit(1);
    }

    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks leaked " + pendingCallbacks.size + " entries on success");
        process.exit(1);
    }
    if (callbackResults.size !== 0) {
        console.error("FAIL: callbackResults leaked " + callbackResults.size + " entries on success");
        process.exit(1);
    }

    console.log("PASS: all cleanup tests passed");
}

main().catch(e => { console.error("FAIL: " + e.message + "\n" + e.stack); process.exit(1); });
"""
    )

    test_path = Path("/tmp/test_module_runner_cleanup.mjs")
    test_path.write_text(test_js)

    r = subprocess.run(
        ["node", str(test_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Cleanup behavioral test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_caller_cleans_up_pending_callbacks():
    """runInRunnerObject must clean up pendingCallbacks within its own body."""
    source = TARGET.read_text()
    full_text, _ = _extract_function(source, "runInRunnerObject")

    # In the buggy version, pendingCallbacks.delete(id) is only in executeCallback,
    # not in runInRunnerObject itself. The fix adds cleanup to runInRunnerObject.
    assert "pendingCallbacks.delete" in full_text, (
        "runInRunnerObject must clean up pendingCallbacks "
        "(missing cleanup causes memory leak on error)"
    )


# [pr_diff] fail_to_pass
def test_error_handling_around_rpc_call():
    """runInRunnerObject must wrap the RPC call in error handling."""
    source = TARGET.read_text()
    full_text, _ = _extract_function(source, "runInRunnerObject")

    has_try = "try" in full_text
    has_finally = "finally" in full_text
    has_catch = "catch" in full_text

    assert has_try and (has_finally or has_catch), (
        "runInRunnerObject must use try/catch or try/finally "
        "to ensure cleanup on error"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_build():
    """Repo's build for vite-plugin passes (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "turbo", "build", "--filter", "@cloudflare/vite-plugin", "--output-logs=errors-only"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's typecheck for vite-plugin passes (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "turbo", "check:type", "--filter", "@cloudflare/vite-plugin", "--output-logs=errors-only"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_runner_worker_tests():
    """Repo's runner-worker unit tests pass (pass_to_pass)."""
    _setup_pnpm()
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/workers/runner-worker/__tests__/env.spec.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/packages/vite-plugin-cloudflare",
    )
    assert r.returncode == 0, f"Runner-worker tests failed:\n{r.stderr[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """runInRunnerObject must have real logic, not a stub."""
    source = TARGET.read_text()
    full_text, _ = _extract_function(source, "runInRunnerObject")

    assert "pendingCallbacks.set" in full_text, "Must add to pendingCallbacks"
    assert "callbackResults" in full_text, "Must reference callbackResults"
    assert "nextCallbackId" in full_text, "Must use nextCallbackId counter"
    assert "executeCallback" in full_text, "Must call executeCallback via RPC"

    lines = [
        l.strip()
        for l in full_text.split("\n")
        if l.strip() and not l.strip().startswith("//")
    ]
    assert len(lines) >= 8, (
        f"Function body too short ({len(lines)} lines) - likely a stub"
    )
