"""
Task: nextjs-dynamicio-deprecation-message
Repo: vercel/next.js @ 4b62ff78c0ad4117477ab78806df809f4c1f8b33
PR:   92081

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/next.js"
CONFIG_TS = f"{REPO}/packages/next/src/server/config.ts"

# Self-contained Node.js script that extracts normalizeNextConfigZodErrors
# from config.ts, strips TypeScript annotations, mocks the normalizeZodErrors
# dependency, evaluates the real function logic, and tests it with mock Zod
# errors.  Outputs JSON with the function's return value.
_EVAL_SCRIPT = textwrap.dedent(r"""
    const fs = require("fs");
    const src = fs.readFileSync(process.argv[1], "utf8");

    // --- locate and extract normalizeNextConfigZodErrors ---
    const fnTag = "function normalizeNextConfigZodErrors";
    const fnIdx = src.indexOf(fnTag);
    if (fnIdx === -1) {
        process.stdout.write(JSON.stringify({error: "function_not_found"}));
        process.exit(0);
    }
    let depth = 0, started = false, end = fnIdx;
    for (let i = fnIdx; i < src.length; i++) {
        if (src[i] === "{") { depth++; started = true; }
        if (src[i] === "}" && started) { depth--; if (depth === 0) { end = i + 1; break; } }
    }
    let fnSrc = src.slice(fnIdx, end);

    // --- strip TypeScript type annotations ---
    fnSrc = fnSrc
        .replace(/error\s*:\s*ZodError<NextConfig>/g, "error")
        .replace(/\)\s*:\s*\[warnings\s*:\s*string\[\]\s*,\s*fatalErrors\s*:\s*string\[\]\]/g, ")")
        .replace(/const\s+warnings\s*:\s*string\[\]/g, "const warnings")
        .replace(/const\s+fatalErrors\s*:\s*string\[\]/g, "const fatalErrors")
        .replace(/let\s+message\s*:\s*string/g, "let message");

    // --- mock normalizeZodErrors (mirrors real signature) ---
    const mockNormalizeZodErrors = (err) =>
        err.issues.map(issue => ({ issue, message: issue.message || "" }));

    // --- build and evaluate the function ---
    let fn;
    try {
        const wrapped = `
            const normalizeZodErrors = ${mockNormalizeZodErrors.toString()};
            ${fnSrc}
            return normalizeNextConfigZodErrors;
        `;
        fn = new Function(wrapped)();
    } catch (e) {
        process.stdout.write(JSON.stringify({error: "eval_failed", detail: e.message}));
        process.exit(0);
    }

    // --- run the test case passed via argv[2] (JSON Zod error) ---
    const mockError = JSON.parse(process.argv[2]);
    const [warnings, fatalErrors] = fn(mockError);
    process.stdout.write(JSON.stringify({ warnings, fatalErrors }));
""")


def _run_fn(zod_error_json: str) -> dict:
    """Evaluate normalizeNextConfigZodErrors with a mock Zod error."""
    r = subprocess.run(
        ["node", "-e", _EVAL_SCRIPT, CONFIG_TS, zod_error_json],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"Node script crashed:\nstdout={r.stdout.decode()[-500:]}\n"
        f"stderr={r.stderr.decode()[-500:]}"
    )
    result = json.loads(r.stdout.decode())
    assert "error" not in result, (
        f"Function extraction failed: {result}"
    )
    return result


def _make_unrecognized_key_error(key: str) -> str:
    """Build a mock Zod error JSON for an unrecognized experimental key."""
    return json.dumps({
        "issues": [{
            "code": "unrecognized_keys",
            "path": ["experimental"],
            "message": f"Unrecognized key(s) in object: '{key}'",
            "keys": [key],
        }]
    })


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """config.ts must be valid TypeScript (parseable by Node)."""
    # Use node to verify the file is syntactically valid JS/TS by reading it
    # and checking the function can be extracted and stripped of types.
    r = subprocess.run(
        ["node", "-e", _EVAL_SCRIPT, CONFIG_TS,
         _make_unrecognized_key_error("someRandomKey")],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"config.ts failed to parse:\n{r.stderr.decode()[-500:]}"
    )
    result = json.loads(r.stdout.decode())
    assert "error" not in result, f"Function extraction failed: {result}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dynamicio_fatal_error():
    """dynamicIO in experimental config must produce a fatal error mentioning cacheComponents."""
    result = _run_fn(_make_unrecognized_key_error("dynamicIO"))
    assert len(result["fatalErrors"]) >= 1, (
        f"Expected dynamicIO to be a fatal error, got warnings only: {result}"
    )
    assert len(result["warnings"]) == 0, (
        f"dynamicIO should NOT appear in warnings: {result}"
    )
    fatal_msg = result["fatalErrors"][0]
    assert "cacheComponents" in fatal_msg, (
        f"Fatal error should mention 'cacheComponents' replacement: {fatal_msg}"
    )


# [pr_diff] fail_to_pass
def test_dynamicio_includes_docs_link():
    """dynamicIO fatal error must include a link to the cacheComponents docs."""
    result = _run_fn(_make_unrecognized_key_error("dynamicIO"))
    fatal_msg = " ".join(result["fatalErrors"])
    expected_url = "https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents"
    assert expected_url in fatal_msg, (
        f"Fatal error should include docs link '{expected_url}': {fatal_msg}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / pr_diff) -- regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_turbopack_handling_preserved():
    """turbopackPersistentCaching must still produce a fatal error."""
    result = _run_fn(_make_unrecognized_key_error("turbopackPersistentCaching"))
    assert len(result["fatalErrors"]) >= 1, (
        f"turbopackPersistentCaching should still be fatal: {result}"
    )
    fatal_msg = result["fatalErrors"][0]
    assert "turbopackFileSystemCacheForDev" in fatal_msg, (
        f"Should suggest turbopackFileSystemCacheForDev: {fatal_msg}"
    )


# [pr_diff] pass_to_pass
def test_generic_unrecognized_key_is_warning():
    """An unrecognized experimental key (not dynamicIO or turbopack) should be a warning, not fatal."""
    result = _run_fn(_make_unrecognized_key_error("someUnknownFlag"))
    assert len(result["warnings"]) >= 1, (
        f"Unknown key should produce a warning: {result}"
    )
    assert len(result["fatalErrors"]) == 0, (
        f"Unknown key should NOT be fatal: {result}"
    )
