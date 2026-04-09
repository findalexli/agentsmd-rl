"""
Task: opencode-format-childprocess-spawner
Repo: anomalyco/opencode @ c8909908f50afc3622d354cd8fd7a83dc3445706
PR:   #19457

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
FORMAT_TS = f"{REPO}/packages/opencode/src/format/index.ts"
BASE_COMMIT = "c8909908f50afc3622d354cd8fd7a83dc3445706"


def _read_format_ts() -> str:
    """Read format/index.ts and strip comments for analysis."""
    src = Path(FORMAT_TS).read_text()
    # Strip single-line and multi-line comments
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates from repository
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_tests():
    """Repo's format test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/format/format.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/packages/opencode",
    )
    assert r.returncode == 0, f"Format tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + compilation gates
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_format_test_suite_passes():
    """Upstream format test suite must pass after refactor (both index.ts and test layer wiring)."""
    r = subprocess.run(
        ["bun", "test", "--timeout", "30000", "test/format/format.test.ts"],
        cwd=f"{REPO}/packages/opencode",
        capture_output=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"Format test suite failed (exit {r.returncode}):\n"
        f"{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_module_imports_cleanly():
    """format/index.ts must be importable without errors (catches missing deps, syntax)."""
    r = subprocess.run(
        [
            "bun", "-e",
            "import('./packages/opencode/src/format/index.ts')"
            ".then(() => { console.log('ok'); process.exit(0) })"
            ".catch(e => { console.error(e.message); process.exit(1) })",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=15,
    )
    stdout = r.stdout.decode()
    assert r.returncode == 0 and "ok" in stdout, (
        f"Module import failed:\n{r.stderr.decode()[-1000:]}"
    )


# [static] pass_to_pass
def test_format_exports_preserved():
    """Format namespace must still export Service, layer, defaultLayer, runPromise."""
    code = _read_format_ts()
    for name in ("Service", "layer", "defaultLayer", "runPromise"):
        assert name in code, f"Expected export '{name}' not found in format/index.ts"


# [agent_config] pass_to_pass — AGENTS.md:13
def test_no_any_type_introduced():
    """No 'any' type annotations introduced in format/index.ts. AGENTS.md:13"""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", "packages/opencode/src/format/index.ts"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added:
        assert not re.search(r":\s*any\b", line), (
            f"'any' type annotation in added line: {line.strip()}"
        )
        assert not re.search(r"\bas\s+any\b", line), (
            f"'as any' cast in added line: {line.strip()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_uses_childprocess_spawner():
    """formatFile must use ChildProcessSpawner, not Process.spawn."""
    code = _read_format_ts()

    assert not re.search(r"Process\.spawn\s*\(", code), (
        "Process.spawn is still called — must be replaced with ChildProcessSpawner"
    )
    assert re.search(r"import\s[\s\S]*?ChildProcessSpawner", code) or re.search(
        r'import\s[\s\S]*?from\s+["\'].*(?:child.*process|unstable/process)', code, re.IGNORECASE
    ), "ChildProcessSpawner is not imported"

    # Must actually be used in code body, not just imported
    body_start = code.find("function")
    assert body_start != -1 and "ChildProcessSpawner" in code[body_start:], (
        "ChildProcessSpawner imported but not used in code body"
    )


# [pr_diff] fail_to_pass
def test_format_file_returns_effect():
    """formatFile must return an Effect (not be async) and caller must not wrap with Effect.promise."""
    code = _read_format_ts()

    assert not re.search(r"async\s+function\s+formatFile", code), (
        "formatFile is still declared as async — must return Effect"
    )
    assert not re.search(r"Effect\.promise\s*\(\s*\(\)\s*=>\s*(?:\w+\.)?formatFile", code), (
        "Effect.promise wrapper still used around formatFile — yield the Effect directly"
    )


# [pr_diff] fail_to_pass
def test_default_layer_includes_spawner():
    """defaultLayer must provide a spawner layer dependency."""
    code = _read_format_ts()
    match = re.search(r"defaultLayer\s*=[\s\S]{0,500}", code)
    assert match, "defaultLayer definition not found"
    assert re.search(r"[Ss]pawner", match.group(0)), (
        "defaultLayer does not reference a spawner layer"
    )


# [pr_diff] fail_to_pass
def test_no_process_util_import():
    """Process utility import must be removed (replaced by Effect ChildProcessSpawner)."""
    code = _read_format_ts()
    assert not re.search(r"""from\s+['"](\.\./)*util/process['"]""", code), (
        "Still importing from util/process — must use ChildProcessSpawner instead"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:12
def test_no_try_catch_in_format_file():
    """formatFile must not use try/catch (Effect error handling instead). AGENTS.md:12"""
    code = _read_format_ts()
    idx = code.find("formatFile")
    assert idx != -1, "formatFile not found"
    # Check a generous window after formatFile definition
    body = code[idx : idx + 3000]
    assert not re.search(r"\btry\s*\{", body), (
        "formatFile still uses try/catch — use Effect error combinators instead"
    )


# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:20
def test_format_file_uses_effect_gen():
    """formatFile must use Effect.gen(function* () { ... }) for composition. packages/opencode/AGENTS.md:20"""
    code = _read_format_ts()
    idx = code.find("formatFile")
    assert idx != -1, "formatFile not found"
    body = code[idx : idx + 3000]
    assert re.search(r"Effect\.gen\s*\(\s*function\s*\*", body), (
        "formatFile does not use Effect.gen(function* () { ... }) pattern"
    )


# [agent_config] pass_to_pass — AGENTS.md:70
def test_no_let_in_added_lines():
    """New/changed lines must use const, not let. AGENTS.md:70"""
    r = subprocess.run(
        ["git", "diff", BASE_COMMIT, "--", "packages/opencode/src/format/index.ts"],
        cwd=REPO,
        capture_output=True,
        timeout=10,
    )
    diff = r.stdout.decode()
    added = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    for line in added:
        # Allow 'let' inside string literals or comments, but flag declarations
        stripped = line.lstrip("+").strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        assert not re.search(r"\blet\s+\w+", stripped), (
            f"'let' declaration in added line — use 'const' instead: {stripped}"
        )


# [agent_config] pass_to_pass — AGENTS.md:84
def test_no_else_in_format_file():
    """formatFile should not use else statements — prefer early returns. AGENTS.md:84"""
    code = _read_format_ts()
    idx = code.find("formatFile")
    assert idx != -1, "formatFile not found"
    body = code[idx : idx + 3000]
    assert not re.search(r"\}\s*else\s*\{", body), (
        "formatFile uses else — prefer early returns or ternaries"
    )
