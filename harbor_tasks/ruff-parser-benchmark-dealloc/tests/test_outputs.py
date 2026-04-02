"""
Task: ruff-parser-benchmark-dealloc
Repo: astral-sh/ruff @ bd477d9535b5b83795e7eb42675faa8aa4fb954f
PR:   #24301

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
TARGET = "crates/ruff_benchmark/benches/parser.rs"


def _repo_dir():
    """Return whichever workspace path exists."""
    for p in ["/workspace/ruff", "/repo"]:
        if Path(p).is_dir():
            return p
    raise FileNotFoundError("Neither /workspace/ruff nor /repo found")


def _target_path():
    return Path(_repo_dir()) / TARGET


def _read_source_no_comments():
    """Read parser.rs and strip Rust comments for structural checks."""
    src = _target_path().read_text()
    # Remove block comments
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    # Remove line comments
    src = re.sub(r"//.*", "", src)
    return src


# ---------------------------------------------------------------------------
# Gates (pass_to_pass) — compilation
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_compiles():
    """Benchmark crate must compile (proves valid Rust)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_benchmark", "--benches"],
        cwd=_repo_dir(),
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr.decode()[-2000:]}"
    )


# [pr_diff] pass_to_pass
def test_benchmarks_run():
    """Benchmarks execute successfully in test mode."""
    r = subprocess.run(
        ["cargo", "test", "-p", "ruff_benchmark", "--benches"],
        cwd=_repo_dir(),
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo test --benches failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dealloc_excluded():
    """Deallocation must be excluded from benchmark measurement.

    Valid approaches: iter_with_large_drop, iter_batched, iter_batched_ref,
    ManuallyDrop, or mem::forget — anything that prevents AST drop from
    being timed inside the measurement loop.
    """
    src = _read_source_no_comments()
    has_iter_variant = bool(
        re.search(r"iter_with_large_drop|iter_batched|iter_batched_ref", src)
    )
    has_manual_drop = bool(re.search(r"ManuallyDrop|mem::forget", src))
    assert has_iter_variant or has_manual_drop, (
        "No deallocation-excluding mechanism found (expected iter_with_large_drop, "
        "iter_batched, iter_batched_ref, ManuallyDrop, or mem::forget)"
    )


# [pr_diff] fail_to_pass
def test_count_visitor_removed():
    """CountVisitor dead code must be removed.

    CountVisitor was only used to prevent compiler optimization of the parse
    result — it adds overhead unrelated to parsing and is dead code after
    switching to a dealloc-excluding iter method.
    """
    src = _read_source_no_comments()
    assert "CountVisitor" not in src, (
        "CountVisitor still present — this is dead code that should be removed"
    )


# [pr_diff] fail_to_pass
def test_unused_visitor_imports_removed():
    """Unused StatementVisitor/walk_stmt imports must be cleaned up."""
    src = _read_source_no_comments()
    assert "StatementVisitor" not in src, "Unused import StatementVisitor still present"
    assert "walk_stmt" not in src, "Unused import walk_stmt still present"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_benchmark_parser_preserved():
    """The benchmark_parser function must still exist."""
    src = _read_source_no_comments()
    assert "fn benchmark_parser" in src, "benchmark_parser function is missing"


# [pr_diff] pass_to_pass
def test_parse_module_called():
    """parse_module must still be invoked in the benchmark."""
    src = _read_source_no_comments()
    assert "parse_module" in src, "parse_module is no longer called in benchmark"


# [pr_diff] pass_to_pass
def test_criterion_macros_preserved():
    """criterion_group! and criterion_main! macros must be preserved."""
    src = _read_source_no_comments()
    assert "criterion_group!" in src, "criterion_group! macro missing"
    assert "criterion_main!" in src, "criterion_main! macro missing"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """File must have meaningful content (not gutted/stubbed)."""
    path = _target_path()
    assert path.exists(), f"{TARGET} does not exist"
    lines = path.read_text().splitlines()
    assert len(lines) >= 25, (
        f"File has only {len(lines)} lines — appears stubbed"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ bd477d9535b5b83795e7eb42675faa8aa4fb954f
def test_imports_at_top():
    """Rust imports should be at the top of the file, not locally in functions.

    Rule from AGENTS.md line 76: 'Rust imports should always go at the top
    of the file, never locally in functions.'
    """
    src = _target_path().read_text()
    # Find all function bodies and check for 'use ' statements inside them
    # Pattern: fn ... { ... use some::path ... }
    fn_bodies = re.findall(
        r"fn\s+\w+[^{]*\{(.*?)^\}", src, re.DOTALL | re.MULTILINE
    )
    for body in fn_bodies:
        # Strip comments first
        clean = re.sub(r"//.*", "", body)
        clean = re.sub(r"/\*.*?\*/", "", clean, flags=re.DOTALL)
        local_uses = re.findall(r"^\s*use\s+\w+", clean, re.MULTILINE)
        assert not local_uses, (
            f"Found local import(s) inside function body: {local_uses}"
        )


# [agent_config] pass_to_pass — AGENTS.md:79 @ bd477d9535b5b83795e7eb42675faa8aa4fb954f
def test_no_unwrap():
    """No .unwrap() calls — use .expect() or proper error handling instead.

    Rule from AGENTS.md line 79: 'Try hard to avoid patterns that require
    panic!, unreachable!, or .unwrap().'
    """
    src = _read_source_no_comments()
    # Match .unwrap() but not .unwrap_or, .unwrap_or_else, .unwrap_or_default
    unwrap_calls = re.findall(r"\.unwrap\(\)", src)
    assert not unwrap_calls, (
        f"Found {len(unwrap_calls)} .unwrap() call(s) — use .expect() or "
        "proper error handling instead (AGENTS.md line 79)"
    )


# [agent_config] pass_to_pass — AGENTS.md:33-37 @ bd477d9535b5b83795e7eb42675faa8aa4fb954f
def test_clippy_passes():
    """Clippy must pass on the benchmark crate without warnings.

    Rule from AGENTS.md lines 33-37: clippy --workspace --all-targets -- -D warnings.
    Scoped to ruff_benchmark crate for performance.
    """
    r = subprocess.run(
        ["cargo", "clippy", "-p", "ruff_benchmark", "--benches", "--", "-D", "warnings"],
        cwd=_repo_dir(),
        capture_output=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo clippy failed:\n{r.stderr.decode()[-2000:]}"
    )
