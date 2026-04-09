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

_EVAL_SCRIPT = textwrap.dedent(r"""
    const fs = require("fs");
    const src = fs.readFileSync(process.argv[1], "utf8");
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
    fnSrc = fnSrc
        .replace(/error\s*:\s*ZodError<NextConfig>/g, "error")
        .replace(/\)\s*:\s*\[warnings\s*:\s*string\[\]\s*,\s*fatalErrors\s*:\s*string\[\]\]/g, ")")
        .replace(/const\s+warnings\s*:\s*string\[\]/g, "const warnings")
        .replace(/const\s+fatalErrors\s*:\s*string\[\]/g, "const fatalErrors")
        .replace(/let\s+message\s*:\s*string/g, "let message");
    const mockNormalizeZodErrors = (err) =>
        err.issues.map(issue => ({ issue, message: issue.message || "" }));
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
    const mockError = JSON.parse(process.argv[2]);
    const [warnings, fatalErrors] = fn(mockError);
    process.stdout.write(JSON.stringify({ warnings, fatalErrors }));
""")


def _run_fn(zod_error_json: str) -> dict:
    r = subprocess.run(
        ["node", "-e", _EVAL_SCRIPT, CONFIG_TS, zod_error_json],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"Node script crashed:\nstdout={r.stdout.decode()[-500:]}\n"
        f"stderr={r.stderr.decode()[-500:]}"
    )
    result = json.loads(r.stdout.decode())
    assert "error" not in result, f"Function extraction failed: {result}"
    return result


def _make_unrecognized_key_error(key: str) -> str:
    return json.dumps({
        "issues": [{
            "code": "unrecognized_keys",
            "path": ["experimental"],
            "message": f"Unrecognized key(s) in object: '{key}'",
            "keys": [key],
        }]
    })


def test_syntax_check():
    r = subprocess.run(
        ["node", "-e", _EVAL_SCRIPT, CONFIG_TS, _make_unrecognized_key_error("someRandomKey")],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"config.ts failed to parse:\n{r.stderr.decode()[-500:]}"
    result = json.loads(r.stdout.decode())
    assert "error" not in result, f"Function extraction failed: {result}"


def test_dynamicio_fatal_error():
    result = _run_fn(_make_unrecognized_key_error("dynamicIO"))
    assert len(result["fatalErrors"]) >= 1, f"Expected dynamicIO to be a fatal error: {result}"
    assert len(result["warnings"]) == 0, f"dynamicIO should NOT appear in warnings: {result}"
    assert "cacheComponents" in result["fatalErrors"][0], f"Fatal error should mention 'cacheComponents'"


def test_dynamicio_includes_docs_link():
    result = _run_fn(_make_unrecognized_key_error("dynamicIO"))
    fatal_msg = " ".join(result["fatalErrors"])
    expected_url = "https://nextjs.org/docs/app/api-reference/config/next-config-js/cacheComponents"
    assert expected_url in fatal_msg, f"Fatal error should include docs link: {fatal_msg}"


def test_turbopack_handling_preserved():
    result = _run_fn(_make_unrecognized_key_error("turbopackPersistentCaching"))
    assert len(result["fatalErrors"]) >= 1, f"turbopackPersistentCaching should still be fatal: {result}"
    assert "turbopackFileSystemCacheForDev" in result["fatalErrors"][0], f"Should suggest turbopackFileSystemCacheForDev"


def test_generic_unrecognized_key_is_warning():
    result = _run_fn(_make_unrecognized_key_error("someUnknownFlag"))
    assert len(result["warnings"]) >= 1, f"Unknown key should produce a warning: {result}"
    assert len(result["fatalErrors"]) == 0, f"Unknown key should NOT be fatal: {result}"


def test_repo_eslint():
    """Repo's ESLint passes on config.ts (pass_to_pass)."""
    # Install dependencies first (needed for ESLint to resolve imports)
    install_r = subprocess.run(
        ["bash", "-c", "cd /workspace/next.js && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    # Dependencies might already be installed, so we don't assert on this
    
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/next.js && npx eslint packages/next/src/server/config.ts --max-warnings 0"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_prettier():
    """Repo's Prettier formatting passes on config.ts (pass_to_pass)."""
    # Install dependencies first
    subprocess.run(
        ["bash", "-c", "cd /workspace/next.js && corepack enable && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    
    r = subprocess.run(
        ["bash", "-c", "cd /workspace/next.js && npx prettier --check packages/next/src/server/config.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"
