import subprocess
import json
import os

REPO = "/workspace/workers-sdk"
MINIFLARE_DIST = os.path.join(REPO, "packages/miniflare/dist/src/index.js")


def run_js(code: str) -> str:
    """Run JavaScript code via Node.js and return stdout."""
    full_code = f"""
const m = require('{MINIFLARE_DIST}');
{code}
"""
    r = subprocess.run(
        ["node", "-e", full_code],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    if r.returncode != 0:
        raise RuntimeError(f"JS error: {r.stderr}")
    return r.stdout.strip()


def test_globsToRegExps_endAnchor_prevents_double_extension():
    """
    Regression test for https://github.com/cloudflare/workers-sdk/issues/8280
    With endAnchor=true, **/*.wasm must NOT match foo.wasm.js or main.wasm.test.ts
    """
    # Call globsToRegExps with endAnchor: true and testRegExps
    result = run_js(f"""
const wasmMatcher = m.globsToRegExps(["**/*.wasm"], {{ endAnchor: true }});
const tests = [
    {{ path: "foo.wasm", expected: true }},
    {{ path: "path/to/foo.wasm", expected: true }},
    {{ path: "/absolute/path/to/foo.wasm", expected: true }},
    {{ path: "foo.wasm.js", expected: false }},
    {{ path: "src/main.wasm.test.js", expected: false }},
    {{ path: "foo.wasm.map", expected: false }},
];
const failures = tests.filter(t => {{
    const got = m.testRegExps(wasmMatcher, t.path);
    if (got !== t.expected) return true;
}});
if (failures.length > 0) {{
    console.log("FAIL: " + JSON.stringify(failures));
}} else {{
    console.log("PASS");
}}
""")
    assert result == "PASS", f"endAnchor test failed: {result}"


def test_globsToRegExps_without_endAnchor_matches_substring():
    """
    Without endAnchor, patterns should match substrings (KV Sites relies on this).
    """
    result = run_js(f"""
const matcher = m.globsToRegExps(["b"]);
const tests = [
    {{ path: "b/b.txt", expected: true }},
    {{ path: "a.txt", expected: false }},
];
const failures = tests.filter(t => {{
    const got = m.testRegExps(matcher, t.path);
    if (got !== t.expected) return true;
}});
if (failures.length > 0) {{
    console.log("FAIL: " + JSON.stringify(failures));
}} else {{
    console.log("PASS");
}}
""")
    assert result == "PASS", f"without endAnchor test failed: {result}"


def test_miniflare_build():
    """Repo's miniflare package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "build", "--filter", "miniflare"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_miniflare_typecheck():
    """Repo's miniflare package passes TypeScript type checking (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "run", "check:type", "-F", "miniflare"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_miniflare_matcher_tests():
    """Run the miniflare matcher's own test suite."""
    r = subprocess.run(
        ["pnpm", "test", "-F", "miniflare", "matcher"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Matcher tests failed:\n{r.stderr[-1000:]}"


def test_compileModuleRules_uses_endAnchor():
    """
    compileModuleRules should pass endAnchor: true so that module rules
    like **/*.wasm don't match double-extension files.
    """
    result = run_js(f"""
const rules = [{{ include: ["**/*.wasm"], type: "CompiledWasm" }}];
const compiled = m.compileModuleRules(rules);
// compiled[i].include is a MatcherRegExps object: {{ include: [...], exclude: [...] }}
const wasmMatcher = compiled[0].include;

const tests = [
    {{ path: "foo.wasm", expected: true }},
    {{ path: "foo.wasm.js", expected: false }},
    {{ path: "path/to/bar.wasm", expected: true }},
    {{ path: "path/to/bar.wasm.ts", expected: false }},
];
const failures = tests.filter(t => {{
    const got = m.testRegExps(wasmMatcher, t.path);
    if (got !== t.expected) return true;
}});
if (failures.length > 0) {{
    console.log("FAIL: " + JSON.stringify(failures));
}} else {{
    console.log("PASS");
}}
""")
    assert result == "PASS", f"compileModuleRules test failed: {result}"
