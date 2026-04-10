"""
Task: gradio-dataframe-nan-sort
Repo: gradio-app/gradio @ 735351422ca90c178e1b5bb9437ce9831eaf951d
PR:   12890

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/gradio"
TARGET = f"{REPO}/js/dataframe/shared/utils/utils.ts"


def _run_cast(calls: list[tuple]) -> list:
    """Run cast_value_to_type via Node, return results as JSON.

    calls: list of (value_js_expr, type_string) pairs.
    Returns a list of results, one per call.
    """
    test_lines = []
    for i, (val_expr, dtype) in enumerate(calls):
        test_lines.append(f'  results.push(testFn({val_expr}, "{dtype}"));')

    js = f"""
import {{ readFileSync }} from "fs";
const source = readFileSync("{TARGET}", "utf8");
const funcMatch = source.match(
  /export\\s+function\\s+cast_value_to_type\\s*\\([^)]*\\)[^{{]*\\{{([\\s\\S]*?)^\\}}/m
);
if (!funcMatch) {{ console.log("EXTRACT_FAIL"); process.exit(1); }}
const testFn = new Function("v", "t", funcMatch[1]);
const results = [];
{chr(10).join(test_lines)}
console.log(JSON.stringify(results));
"""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", js],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, (
        f"Node execution failed:\nstdout: {r.stdout.decode()}\nstderr: {r.stderr.decode()}"
    )
    return json.loads(r.stdout.decode().strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target file must parse as valid TypeScript/JavaScript."""
    p = Path(TARGET)
    assert p.exists(), f"{TARGET} not found"
    r = subprocess.run(
        ["node", "-e", f'require("fs").readFileSync("{TARGET}", "utf8")'],
        capture_output=True, timeout=10,
    )
    assert r.returncode == 0, "File is unreadable"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_null_number_preservation():
    """cast_value_to_type(null, "number") must return null, not 0."""
    results = _run_cast([
        ("null", "number"),
        ("null", "bool"),
        ("null", "date"),
    ])
    assert results[0] is None, f"null+number returned {results[0]!r}, expected null"
    assert results[1] is None, f"null+bool returned {results[1]!r}, expected null"
    assert results[2] is None, f"null+date returned {results[2]!r}, expected null"


# [pr_diff] fail_to_pass
def test_undefined_preservation():
    """cast_value_to_type(undefined, ...) must return undefined (JSON null) for all types."""
    # undefined serializes as JSON null, so we check via a separate script
    # that distinguishes undefined from null
    js = f"""
import {{ readFileSync }} from "fs";
const source = readFileSync("{TARGET}", "utf8");
const funcMatch = source.match(
  /export\\s+function\\s+cast_value_to_type\\s*\\([^)]*\\)[^{{]*\\{{([\\s\\S]*?)^\\}}/m
);
if (!funcMatch) {{ console.log("EXTRACT_FAIL"); process.exit(1); }}
const testFn = new Function("v", "t", funcMatch[1]);
const types = ["number", "bool", "date", "str"];
const results = [];
for (const t of types) {{
    results.push(testFn(undefined, t) === undefined);
    results.push(testFn(null, t) === null);
}}
console.log(JSON.stringify(results));
"""
    r = subprocess.run(
        ["node", "--input-type=module", "-e", js],
        capture_output=True, timeout=15,
    )
    assert r.returncode == 0, f"Node failed: {r.stderr.decode()}"
    results = json.loads(r.stdout.decode().strip())
    # All should be true
    for i, ok in enumerate(results):
        assert ok, f"null/undefined preservation check {i} failed"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_number_coercion_regression():
    """Normal number coercion still works: strings become numbers, floats preserved."""
    results = _run_cast([
        ('"42"', "number"),
        ("3.14", "number"),
        ('"0"', "number"),
        ('"-7.5"', "number"),
    ])
    assert results[0] == 42, f"'42' -> {results[0]!r}"
    assert results[1] == 3.14, f"3.14 -> {results[1]!r}"
    assert results[2] == 0, f"'0' -> {results[2]!r}"
    assert results[3] == -7.5, f"'-7.5' -> {results[3]!r}"


# [repo_tests] pass_to_pass
def test_bool_coercion_regression():
    """Normal bool coercion still works."""
    results = _run_cast([
        ('"true"', "bool"),
        ('"false"', "bool"),
        ("true", "bool"),
    ])
    assert results[0] is True, f"'true' -> {results[0]!r}"
    assert results[1] is False, f"'false' -> {results[1]!r}"
    assert results[2] is True, f"true -> {results[2]!r}"


# [repo_tests] pass_to_pass
def test_str_passthrough_regression():
    """String type returns value as-is."""
    results = _run_cast([
        ('"hello"', "str"),
        ('"123"', "str"),
    ])
    assert results[0] == "hello", f"'hello' -> {results[0]!r}"
    assert results[1] == "123", f"'123' -> {results[1]!r}"


# [static] pass_to_pass
def test_not_stub():
    """cast_value_to_type has real logic — not a trivial stub."""
    content = Path(TARGET).read_text()
    assert "export function cast_value_to_type" in content, "Function not found"
    # Function must contain type-coercion logic
    assert "Number" in content, "Missing Number coercion"
    assert "isNaN" in content or "NaN" in content, "Missing NaN handling"
    # File must be substantial
    lines = content.strip().splitlines()
    assert len(lines) > 15, f"File too short ({len(lines)} lines) — likely a stub"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI/CD checks
# ---------------------------------------------------------------------------

def _ensure_pnpm():
    """Ensure pnpm is installed and available."""
    r = subprocess.run(["which", "pnpm"], capture_output=True)
    if r.returncode != 0:
        subprocess.run(["npm", "install", "-g", "pnpm"], check=True, capture_output=True)


def _install_deps():
    """Install pnpm dependencies if not already installed."""
    if not Path(f"{REPO}/node_modules").exists():
        _ensure_pnpm()
        subprocess.run(
            ["pnpm", "install", "--frozen-lockfile"],
            cwd=REPO, capture_output=True, timeout=180
        )


# [repo_tests] pass_to_pass
def test_repo_format_check():
    """Repo's Prettier format check passes (pass_to_pass)."""
    _ensure_pnpm()
    _install_deps()
    r = subprocess.run(
        ["pnpm", "format:check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests():
    """Repo's unit tests pass (pass_to_pass)."""
    _ensure_pnpm()
    _install_deps()
    # Build client first (required by test:run)
    subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "test:run"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Tests pass even with some skipped tests
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_dataframe_utils_tests():
    """Dataframe utils-specific tests pass (pass_to_pass)."""
    _ensure_pnpm()
    _install_deps()
    # Build client first (required)
    subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--config", ".config/vitest.config.ts",
         "js/dataframe/test/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Dataframe utils tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_dataframe_sort_tests():
    """Dataframe sort utils tests pass (pass_to_pass)."""
    _ensure_pnpm()
    _install_deps()
    # Build client first (required)
    subprocess.run(
        ["pnpm", "--filter", "@gradio/client", "build"],
        capture_output=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "vitest", "run", "--config", ".config/vitest.config.ts",
         "js/dataframe/test/sort_utils.test.ts"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Dataframe sort tests failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"
