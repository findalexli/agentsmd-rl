"""
Task: deno-shell-metachar-escape
Repo: deno @ 6710d587bc05e4275c2336fb1cc5104d5eee9fdc
PR:   33071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/deno"
SOURCE_FILE = "ext/node/polyfills/internal/child_process.ts"


def _run_deno(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Deno eval script in the repo directory."""
    return subprocess.run(
        ["deno", "eval", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _build_win_escape_test_script(test_args: list[str]) -> str:
    """Build a Deno script that extracts escapeShellArg from the source,
    forces the Windows code path via new Function, and returns JSON results."""
    args_json = json.dumps(test_args)
    # Use plain string concatenation to avoid f-string brace conflicts with JS
    return (
        'const src = Deno.readTextFileSync("' + SOURCE_FILE + '");\n'
        + """
const marker = "function escapeShellArg(arg: string): string {";
const startIdx = src.indexOf(marker);
if (startIdx === -1) { console.error("FUNC_NOT_FOUND"); Deno.exit(1); }

// Find the matching closing brace
let depth = 0;
let endIdx = -1;
for (let i = startIdx; i < src.length; i++) {
    if (src[i] === '{') depth++;
    else if (src[i] === '}') { depth--; if (depth === 0) { endIdx = i + 1; break; } }
}
if (endIdx === -1) { console.error("FUNC_END_NOT_FOUND"); Deno.exit(1); }

let funcBody = src.slice(startIdx, endIdx);
// Force the Windows code path regardless of actual platform
funcBody = funcBody.replace('process.platform === "win32"', "true");
// Strip TypeScript type annotation
funcBody = funcBody.replace("(arg: string): string", "(arg)");

// Use new Function to create a callable (works in strict/module mode)
const openBrace = funcBody.indexOf("{");
const closeBrace = funcBody.lastIndexOf("}");
const inner = funcBody.slice(openBrace + 1, closeBrace);
const escapeShellArg = new Function("arg", inner);

const testArgs = """
        + args_json
        + """;
const results: Record<string, any> = {};
for (const arg of testArgs) {
    const result = escapeShellArg(arg);
    results[arg] = { output: result, changed: result !== arg };
}
console.log(JSON.stringify(results));
"""
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_win_escape_ampersand_pipe():
    """escapeShellArg (Windows path) must quote args containing & or |."""
    script = _build_win_escape_test_script(["a&b", "x|y", "foo&bar|baz"])
    r = _run_deno(script)
    assert r.returncode == 0, f"Deno script failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for arg in ["a&b", "x|y", "foo&bar|baz"]:
        assert results[arg]["changed"], (
            f"'{arg}' was returned unquoted: {results[arg]['output']}"
        )


def test_win_escape_angle_brackets_caret():
    """escapeShellArg (Windows path) must quote args containing <, >, or ^."""
    script = _build_win_escape_test_script(["a<b", "c>d", "e^f", "x<y>z^w"])
    r = _run_deno(script)
    assert r.returncode == 0, f"Deno script failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for arg in ["a<b", "c>d", "e^f", "x<y>z^w"]:
        assert results[arg]["changed"], (
            f"'{arg}' was returned unquoted: {results[arg]['output']}"
        )


def test_win_escape_exclamation_parens():
    """escapeShellArg (Windows path) must quote args containing !, (, or )."""
    script = _build_win_escape_test_script(["hello!", "(test)", "a(b)c", "!done"])
    r = _run_deno(script)
    assert r.returncode == 0, f"Deno script failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for arg in ["hello!", "(test)", "a(b)c", "!done"]:
        assert results[arg]["changed"], (
            f"'{arg}' was returned unquoted: {results[arg]['output']}"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression tests
# ---------------------------------------------------------------------------

def test_win_escape_existing_specials_still_quoted():
    """Args with spaces, quotes, or backslashes must still be quoted (existing behavior)."""
    test_args = ["hello world", 'say "hi"', "path\\\\to\\\\file"]
    script = _build_win_escape_test_script(test_args)
    r = _run_deno(script)
    assert r.returncode == 0, f"Deno script failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for arg in test_args:
        assert results[arg]["changed"], (
            f"'{arg}' should still be quoted: {results[arg]['output']}"
        )


def test_win_escape_plain_args_passthrough():
    """Plain alphanumeric args must pass through unchanged."""
    plain_args = ["hello", "foo123", "simple.txt", "path/to/file", "my-flag"]
    script = _build_win_escape_test_script(plain_args)
    r = _run_deno(script)
    assert r.returncode == 0, f"Deno script failed:\n{r.stderr}"
    results = json.loads(r.stdout.strip())
    for arg in plain_args:
        assert not results[arg]["changed"], (
            f"'{arg}' should not be quoted but got: {results[arg]['output']}"
        )
