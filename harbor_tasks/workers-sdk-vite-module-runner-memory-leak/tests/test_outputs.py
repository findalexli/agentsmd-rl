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
    """runInRunnerObject must clean up pendingCallbacks within its own body, not rely on executeCallback."""
    source = TARGET.read_text()
    _, body = _extract_function(source, "runInRunnerObject")

    js_func = f"async function runInRunnerObject(env, callback) {body}"

    # Mock executeCallback runs the callback and stores results but does NOT
    # delete from pendingCallbacks. If runInRunnerObject doesn't handle its
    # own cleanup, the map will leak entries.
    test_js = (
        "const pendingCallbacks = new Map();\n"
        "const callbackResults = new Map();\n"
        "let nextCallbackId = 0;\n\n"
        + js_func
        + "\n\n"
        + r"""
async function main() {
    const env = {
        __VITE_RUNNER_OBJECT__: {
            get() {
                return {
                    async executeCallback(id) {
                        const cb = pendingCallbacks.get(id);
                        if (!cb) throw new Error("No pending callback with id " + id);
                        const result = await cb();
                        callbackResults.set(id, result);
                        // Deliberately NOT calling pendingCallbacks.delete(id).
                        // The caller (runInRunnerObject) must handle its own cleanup.
                    }
                };
            }
        }
    };

    // Single call: verify cleanup after one successful call
    const result = await runInRunnerObject(env, async () => 99);
    if (result !== 99) {
        console.error("FAIL: expected 99, got " + result);
        process.exit(1);
    }
    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks has " + pendingCallbacks.size + " entry after single call (caller must clean up)");
        process.exit(1);
    }

    // Multiple calls: verify no accumulation over time
    for (let i = 0; i < 10; i++) {
        const r = await runInRunnerObject(env, async () => i * 2);
        if (r !== i * 2) {
            console.error("FAIL: call " + i + " expected " + (i*2) + ", got " + r);
            process.exit(1);
        }
    }
    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks has " + pendingCallbacks.size + " entries after 10 calls");
        process.exit(1);
    }

    console.log("PASS: caller cleans up pendingCallbacks");
}

main().catch(e => { console.error("FAIL: " + e.message + "\n" + e.stack); process.exit(1); });
"""
    )

    test_path = Path("/tmp/test_caller_cleanup.mjs")
    test_path.write_text(test_js)

    r = subprocess.run(
        ["node", str(test_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Caller cleanup test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_error_handling_around_rpc_call():
    """runInRunnerObject must handle RPC errors: propagate them and still clean up maps."""
    source = TARGET.read_text()
    _, body = _extract_function(source, "runInRunnerObject")

    js_func = f"async function runInRunnerObject(env, callback) {body}"

    test_js = (
        "const pendingCallbacks = new Map();\n"
        "const callbackResults = new Map();\n"
        "let nextCallbackId = 0;\n\n"
        + js_func
        + "\n\n"
        + r"""
async function main() {
    const env = {
        __VITE_RUNNER_OBJECT__: {
            get() {
                return {
                    async executeCallback(id) {
                        throw new Error("RPC transport error");
                    }
                };
            }
        }
    };

    // Test that the RPC error propagates to the caller
    let errorCaught = false;
    try {
        await runInRunnerObject(env, async () => "value");
    } catch (e) {
        errorCaught = true;
        if (!e.message.includes("RPC transport error")) {
            console.error("FAIL: error message was altered: " + e.message);
            process.exit(1);
        }
    }

    if (!errorCaught) {
        console.error("FAIL: RPC error was swallowed instead of propagating");
        process.exit(1);
    }

    // After the error, both maps must be clean (no leaked entries)
    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks leaked " + pendingCallbacks.size + " entries after RPC error");
        process.exit(1);
    }
    if (callbackResults.size !== 0) {
        console.error("FAIL: callbackResults leaked " + callbackResults.size + " entries after RPC error");
        process.exit(1);
    }

    // A second error call must also clean up (no stale state from first call)
    errorCaught = false;
    try {
        await runInRunnerObject(env, async () => "another");
    } catch (e) {
        errorCaught = true;
    }
    if (!errorCaught) {
        console.error("FAIL: second RPC error was swallowed");
        process.exit(1);
    }
    if (pendingCallbacks.size !== 0) {
        console.error("FAIL: pendingCallbacks leaked after second error");
        process.exit(1);
    }

    console.log("PASS: errors propagated and maps cleaned up");
}

main().catch(e => { console.error("FAIL: " + e.message + "\n" + e.stack); process.exit(1); });
"""
    )

    test_path = Path("/tmp/test_error_handling.mjs")
    test_path.write_text(test_js)

    r = subprocess.run(
        ["node", str(test_path)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Error handling test failed:\n{r.stdout}\n{r.stderr}"


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
