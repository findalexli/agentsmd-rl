"""Behavioral tests for remix-run/remix#11034: fix dynamic css selectors.

The bug: `processStyle` in packages/component/src/lib/style/lib/style.ts
threw when a nested selector or at-rule had an `undefined` value, e.g.
`css={{ '&:hover': pending ? undefined : { background: 'white' } }}`.

The intended fix: skip keys whose values are not plain record objects
(undefined, null, primitives, arrays).
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/workspace/remix")
STYLE_TS = REPO / "packages/component/src/lib/style/lib/style.ts"
STYLE_IMPORT = f"file://{STYLE_TS}"


def _run_node_ts(ts_code: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Execute a TypeScript module via Node 24 type-stripping; capture stdout/stderr."""
    fd, path = tempfile.mkstemp(suffix=".mts")
    os.close(fd)
    try:
        Path(path).write_text(ts_code)
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", path],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# fail_to_pass: behavioral regressions covered by the PR
# ---------------------------------------------------------------------------


def test_nested_selector_with_undefined_value_does_not_throw():
    """`'& span.special': undefined` must not raise; output must contain neither
    that selector nor the literal 'undefined'."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "blue",
    "& span": {{ color: "rgb(0, 0, 255)" }},
    "& span.special": undefined,
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
console.log("SELECTOR=" + result.selector);
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, (
        f"Node exited non-zero — likely thrown error.\n"
        f"STDERR:\n{r.stderr}\nSTDOUT:\n{r.stdout}"
    )
    out = r.stdout
    assert "CSS_START" in out and "CSS_END" in out
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "& span.special" not in css, (
        f"Undefined nested selector must be skipped from emitted CSS, got:\n{css}"
    )
    assert "undefined" not in css, (
        f"Emitted CSS must not contain the literal text 'undefined':\n{css}"
    )
    assert "& span" in css, f"Sibling nested selector should still be emitted:\n{css}"
    assert "rgb(0, 0, 255)" in css, f"Sibling color value should still be emitted:\n{css}"


def test_at_rule_with_undefined_value_does_not_throw():
    """`'@media (min-width: 600px)': undefined` must not raise; output must omit it."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "red",
    "@media (min-width: 600px)": undefined,
    "@media (min-width: 900px)": {{ color: "green" }},
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, (
        f"Node exited non-zero — at-rule with undefined value threw.\n"
        f"STDERR:\n{r.stderr}\nSTDOUT:\n{r.stdout}"
    )
    out = r.stdout
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "min-width: 600px" not in css, (
        f"Disabled @media rule must not appear in CSS:\n{css}"
    )
    assert "min-width: 900px" in css, (
        f"Active @media rule must still appear:\n{css}"
    )
    assert "color: green" in css


def test_at_rule_undefined_inside_function_at_rule_does_not_throw():
    """`@function` body containing a nested `@media` with undefined value
    must not raise. Tests the at-rule body path."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "purple",
    "@function --my-fn()": {{
        "result": "10px",
        "@media (prefers-reduced-motion)": undefined,
    }},
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, (
        f"Node exited non-zero — undefined nested @-rule inside @function threw.\n"
        f"STDERR:\n{r.stderr}\nSTDOUT:\n{r.stdout}"
    )
    out = r.stdout
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "@function --my-fn()" in css, f"Outer @function should be preserved:\n{css}"
    assert "prefers-reduced-motion" not in css, (
        f"Disabled inner @media must not appear:\n{css}"
    )
    assert "result: 10px" in css


def test_array_value_is_not_treated_as_record():
    """`isRecord` must reject arrays. Pass an array as a keyframe step value;
    the broken predicate would iterate it as a record and emit numeric-key
    declarations, the corrected one skips it (yielding an empty frame block)."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "black",
    "@keyframes spin": {{
        "from": ["color: red"],
        "to": {{ color: "blue" }},
    }},
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, (
        f"Node exited non-zero unexpectedly.\nSTDERR:\n{r.stderr}\nSTDOUT:\n{r.stdout}"
    )
    out = r.stdout
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "0: color: red" not in css, (
        f"Array must not be iterated as a record (would yield numeric-key declarations):\n{css}"
    )
    assert "color: blue" in css, f"Valid keyframe step must be emitted:\n{css}"


def test_undefined_at_rule_does_not_emit_empty_block():
    """When an at-rule's value is undefined, it must be entirely skipped — not
    emitted as `@media (...) {}`. Otherwise the broken behavior of producing
    a stray empty block remains."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "teal",
    "@media (max-width: 480px)": undefined,
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Failed to run.\n{r.stderr}\n{r.stdout}"
    out = r.stdout
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "max-width: 480px" not in css, (
        f"Skipped at-rule must not appear at all (no empty stub block):\n{css}"
    )


# ---------------------------------------------------------------------------
# pass_to_pass: behavior that already worked at the base commit
# ---------------------------------------------------------------------------


def test_basic_styles_still_compile():
    """Sanity check: a normal css object still produces the expected base block."""
    code = f'''
import {{ processStyle }} from "{STYLE_IMPORT}";

let cache = new Map();
let result = processStyle({{
    color: "white",
    backgroundColor: "blue",
    "&:hover": {{ backgroundColor: "darkblue" }},
}}, cache);

console.log("CSS_START");
console.log(result.css);
console.log("CSS_END");
console.log("SELECTOR=" + result.selector);
'''
    r = _run_node_ts(code)
    assert r.returncode == 0, f"Basic styles failed.\n{r.stderr}\n{r.stdout}"
    out = r.stdout
    css = out.split("CSS_START\n", 1)[1].split("\nCSS_END", 1)[0]
    assert "color: white" in css
    assert "background-color: blue" in css
    assert "&:hover" in css
    assert "background-color: darkblue" in css
    # Selector format
    assert "SELECTOR=rmx-" in out


def test_node_can_strip_types_on_style_module():
    """pass_to_pass: the style.ts file parses under Node 24 type-stripping
    (smoke test that the file is syntactically valid)."""
    r = subprocess.run(
        [
            "node",
            "--experimental-strip-types",
            "--no-warnings",
            "--check",
            str(STYLE_TS),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"style.ts has a syntax error:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")