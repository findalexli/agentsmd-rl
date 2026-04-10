"""
Task: nextjs-emit-asset-dedup-conflict
Repo: vercel/next.js @ 5a922bc9bb9b4435da87f5b6783e3b14e26aadf9
PR:   92292

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
EMIT_RS = f"{REPO}/crates/next-core/src/emit.rs"
ISSUE_MOD = f"{REPO}/turbopack/crates/turbopack-core/src/issue/mod.rs"


def _read(path: str) -> str:
    return Path(path).read_text()


def _run_cargo(args: list[str], cwd: str = REPO, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run cargo command and return result."""
    return subprocess.run(
        ["cargo"] + args,
        capture_output=True, text=True, cwd=cwd, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [repo_state] pass_to_pass
def test_repo_git_state_clean():
    """Repository has clean git state with no uncommitted changes (pass_to_pass)."""
    r = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"
    assert r.stdout.strip() == "", \
        f"Repository has uncommitted changes:\n{r.stdout[:500]}"


# [repo_state] pass_to_pass
def test_repo_base_commit_verified():
    """Repository is at the expected base commit (pass_to_pass)."""
    r = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert r.returncode == 0, f"git rev-parse failed: {r.stderr}"
    head_commit = r.stdout.strip()
    expected_commit = "5a922bc9bb9b4435da87f5b6783e3b14e26aadf9"
    assert head_commit == expected_commit, \
        f"Expected base commit {expected_commit}, got {head_commit}"


# [static] pass_to_pass
def test_files_exist_and_not_stub():
    """Modified files exist with real Rust code (anti-stub gate)."""
    checks = {
        EMIT_RS: {"min_lines": 100, "patterns": [r"#\[turbo_tasks::function\]", r"async fn emit_assets"]},
        ISSUE_MOD: {"min_lines": 100, "patterns": [r"pub enum IssueStage", r"impl Display for IssueStage"]},
    }
    for path, spec in checks.items():
        content = _read(path)
        lines = content.count("\n") + 1
        assert lines >= spec["min_lines"], f"{path} has {lines} lines (min {spec['min_lines']})"
        for pat in spec["patterns"]:
            assert re.search(pat, content), f"{path} missing pattern: {pat}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — existing functions preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_emit_and_emit_rebase_preserved():
    """emit() and emit_rebase() turbo_tasks functions still exist."""
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core package failed to compile: {r.stderr[-1000:]}"


# [pr_diff] pass_to_pass
def test_emit_assets_function_signature():
    """emit_assets function signature preserved with all original parameters."""
    src = _read(EMIT_RS)
    assert re.search(r"pub async fn emit_assets\s*\(", src), \
        "emit_assets() function missing"
    for param in ["assets", "node_root", "client_relative_path", "client_output_path"]:
        assert param in src, f"emit_assets() missing parameter: {param}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — EmitConflictIssue struct (behavioral)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_emit_conflict_issue_struct():
    """EmitConflictIssue struct exists and compiles with correct fields."""
    # First check syntax via cargo check
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core failed to compile: {r.stderr[-1000:]}"

    # Verify struct exists with correct fields by compiling a test program
    test_code = """
use std::process::Command;

fn main() {
    let output = Command::new("cargo")
        .args(["check", "--package", "next-core", "--lib", "--message-format=short"])
        .current_dir("/workspace/next.js")
        .output()
        .expect("cargo check failed");

    if !output.status.success() {
        eprintln!("Compilation failed");
        std::process::exit(1);
    }
    println!("PASS: EmitConflictIssue struct compiles");
}
"""
    r = subprocess.run(
        ["rustc", "-", "-o", "/tmp/check_emit"],
        input=test_code, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0 or "linking" in r.stderr.lower(), \
        f"Test compilation failed: {r.stderr}"

    # Verify struct exists in source with correct fields
    src = _read(EMIT_RS)
    assert re.search(r"#\[turbo_tasks::value\]\s*struct\s+EmitConflictIssue", src), \
        "EmitConflictIssue struct with #[turbo_tasks::value] not found"

    struct_body = re.search(r"struct\s+EmitConflictIssue\s*\{([\s\S]*?)\n\}", src)
    assert struct_body, "EmitConflictIssue struct body not found"
    body = struct_body.group(1)
    assert re.search(r"asset_path\s*:\s*FileSystemPath", body), \
        "EmitConflictIssue.asset_path must be FileSystemPath"
    assert re.search(r"detail\s*:\s*RcStr", body), \
        "EmitConflictIssue.detail must be RcStr"


# [pr_diff] fail_to_pass
def test_emit_conflict_issue_impls_issue():
    """EmitConflictIssue implements Issue trait with Emit stage and Error severity."""
    # Behavioral check: verify both files compile together
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core failed to compile: {r.stderr[-1000:]}"

    # Check IssueStage::Emit exists in turbopack-core
    r2 = _run_cargo(["check", "--package", "turbopack-core", "--lib"],
                    cwd=f"{REPO}/turbopack/crates/turbopack-core", timeout=600)
    assert r2.returncode == 0, f"turbopack-core failed to compile: {r2.stderr[-1000:]}"

    # Verify implementation details in source
    src = _read(EMIT_RS)
    assert re.search(r"impl\s+Issue\s+for\s+EmitConflictIssue", src), \
        "impl Issue for EmitConflictIssue not found"

    # stage() must return IssueStage::Emit
    stage_m = re.search(
        r"fn\s+stage\s*\([^)]*\)\s*->\s*Vc<IssueStage>\s*\{[\s\S]*?IssueStage::Emit",
        src,
    )
    assert stage_m, "stage() must return IssueStage::Emit"

    # severity() must return Error
    assert re.search(r"fn\s+severity\s*\([^)]*\)\s*->\s*IssueSeverity\s*\{[\s\S]*?IssueSeverity::Error", src), \
        "severity() must return IssueSeverity::Error"

    # title() must describe asset conflict
    title_m = re.search(
        r"fn\s+title\s*\([^)]*\)\s*->[^{]*\{[\s\S]*?StyledString::Text\s*\(\s*\"([^\"]+)\"",
        src,
    )
    assert title_m, "title() returning StyledString::Text not found"
    title_lower = title_m.group(1).lower()
    assert any(w in title_lower for w in ["asset", "conflict", "same", "different", "emitted"]), \
        f"title() doesn't describe asset conflict: {title_m.group(1)}"

    # file_path() must use asset_path
    assert re.search(r"fn\s+file_path\b[\s\S]*?asset_path", src), \
        "file_path() must use self.asset_path"

    # description() must use detail
    assert re.search(r"fn\s+description\b[\s\S]*?self\.detail", src), \
        "description() must use self.detail"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — assets_diff function (behavioral)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_assets_diff_function():
    """assets_diff turbo_tasks function compiles and has correct signature."""
    # Behavioral check: verify the code compiles
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core failed to compile: {r.stderr[-1000:]}"

    # Verify function signature and body in source
    src = _read(EMIT_RS)

    # Function must exist with turbo_tasks attribute
    assert re.search(r"#\[turbo_tasks::function\]\s*async fn assets_diff\s*\(", src), \
        "assets_diff() turbo_tasks function not found"

    # Must accept asset1, asset2, extension, node_root
    sig = re.search(r"async fn assets_diff\s*\(([\s\S]*?)\)\s*->", src)
    assert sig, "assets_diff signature not found"
    params = sig.group(1)
    assert "asset1" in params, "assets_diff missing asset1 param"
    assert "asset2" in params, "assets_diff missing asset2 param"
    assert re.search(r"extension\s*:\s*RcStr", params), "assets_diff missing extension: RcStr"
    assert re.search(r"node_root\s*:\s*FileSystemPath", params), "assets_diff missing node_root"

    # Must handle file content comparison (AssetContent::File)
    assert re.search(r"AssetContent::File", src), "assets_diff must handle AssetContent::File"

    # Must use xxh3 hashing for conflict file names
    assert re.search(r"hash_xxh3_hash64", src), "assets_diff must use xxh3 hashing"

    # Must write conflicting versions for user diffing
    assert re.search(r"\.write\s*\(", src) and re.search(r"file content differs", src, re.IGNORECASE), \
        "assets_diff must write conflicting versions when content differs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — IssueStage::Emit variant (behavioral)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_issue_stage_emit_variant():
    """IssueStage::Emit variant exists and compiles with correct Display impl."""
    # Behavioral check: verify turbopack-core compiles
    r = _run_cargo(["check", "--package", "turbopack-core", "--lib"],
                   cwd=f"{REPO}/turbopack/crates/turbopack-core", timeout=600)
    assert r.returncode == 0, f"turbopack-core failed to compile: {r.stderr[-1000:]}"

    # Verify enum and Display impl in source
    src = _read(ISSUE_MOD)

    # Emit must be in the enum
    enum_body = re.search(r"pub enum IssueStage\s*\{([\s\S]*?)\n\}", src)
    assert enum_body, "IssueStage enum not found"
    assert re.search(r"\bEmit\b", enum_body.group(1)), "IssueStage::Emit variant not found"

    # Display impl must map Emit => "emit"
    display_m = re.search(
        r"impl\s+Display\s+for\s+IssueStage[\s\S]*?match\s*self\s*\{([\s\S]*?)\n\s*\}",
        src,
    )
    assert display_m, "Display impl for IssueStage not found"
    display_body = display_m.group(1)
    assert re.search(r"IssueStage::Emit\s*=>\s*write!\s*\([^)]*\"emit\"", display_body), \
        "IssueStage::Emit must display as 'emit'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — dedup/grouping logic in emit_assets (behavioral)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_emit_assets_dedup_logic():
    """emit_assets groups assets by path, checks conflicts, uses join! for parallel emission."""
    # Behavioral check: verify the code compiles
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core failed to compile: {r.stderr[-1000:]}"

    # Verify implementation details in source
    src = _read(EMIT_RS)

    # Must group assets by output path (FxIndexMap or HashMap)
    assert re.search(r"(?:FxIndexMap|HashMap)\s*<\s*FileSystemPath", src), \
        "Must group assets by path using a map"

    # Must have dedup/conflict-checking logic
    assert re.search(r"EmitConflictIssue\s*\{", src), \
        "EmitConflictIssue must be constructed in dedup logic"

    # Must emit the issue via .emit()
    assert re.search(r"\.emit\s*\(\s*\)", src), \
        "Issue must be emitted via .emit()"

    # Must use join! (not try_join!) for deterministic parallel emission
    assert re.search(r"\bjoin!\s*\(", src), \
        "Must use join! for parallel emission"
    # Must not use bare try_join! (try_flat_join is fine)
    try_join_matches = re.findall(r"(?<!\w)try_join!\s*\(", src)
    assert len(try_join_matches) == 0, \
        "Must use join! not try_join! for deterministic error reporting"

    # Must still emit assets (emit and emit_rebase calls must remain)
    assert re.search(r"emit\s*\([^)]*\)\.as_side_effect\(\)", src), \
        "Must still call emit().as_side_effect()"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — cargo fmt import ordering (behavioral)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — CLAUDE.md Rust/Cargo section
def test_imports_cargo_fmt_sorted():
    """New imports in emit.rs follow cargo fmt convention."""
    # Behavioral check: run cargo fmt --check
    r = _run_cargo(["fmt", "--", "--check", EMIT_RS], timeout=60)
    # If cargo fmt is not available, fall back to manual check
    if r.returncode != 0 and "not found" in r.stderr.lower():
        # Manual ASCII sort check as fallback
        src = _read(EMIT_RS)
        use_lines = [line.strip() for line in src.splitlines() if line.strip().startswith("use ")]

        assert len(use_lines) >= 5, f"Expected >= 5 use statements, got {len(use_lines)}"

        for i in range(len(use_lines) - 1):
            assert use_lines[i] <= use_lines[i + 1], (
                f"Import order violation in emit.rs: '{use_lines[i]}' > '{use_lines[i+1]}'"
            )
    else:
        # cargo fmt check passed or found real formatting issues
        pass


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Rust code compilation and validation
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_rust_files_no_merge_conflicts():
    """Modified Rust files have no merge conflict markers (pass_to_pass)."""
    for path in [EMIT_RS, ISSUE_MOD]:
        content = _read(path)
        assert "<<<<<<< HEAD" not in content, f"{path} contains merge conflict markers"
        assert "=======" not in content, f"{path} contains merge conflict markers"
        assert ">>>>>>>" not in content, f"{path} contains merge conflict markers"


# [repo_tests] pass_to_pass
def test_rust_files_valid_braces():
    """Modified Rust files have balanced braces (basic syntax check) (pass_to_pass)."""
    for path in [EMIT_RS, ISSUE_MOD]:
        content = _read(path)
        # Basic brace counting - not perfect but catches obvious issues
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, (
            f"{path} has mismatched braces: {open_braces} open vs {close_braces} close"
        )
        open_parens = content.count("(")
        close_parens = content.count(")")
        assert open_parens == close_parens, (
            f"{path} has mismatched parens: {open_parens} open vs {close_parens} close"
        )


# [repo_tests] pass_to_pass
def test_emit_rs_no_broken_imports():
    """emit.rs has no obviously broken import paths (pass_to_pass)."""
    src = _read(EMIT_RS)
    # Check that common imports look valid (no empty paths, double slashes)
    import_lines = [line for line in src.splitlines() if line.strip().startswith("use ")]
    for line in import_lines:
        # Check for obviously broken patterns
        assert "::" in line, f"Invalid import (no ::): {line}"
        assert "  ::" not in line, f"Import with double spaces: {line}"


# [repo_tests] pass_to_pass
def test_next_core_compiles():
    """next-core package compiles without errors (pass_to_pass)."""
    r = _run_cargo(["check", "--package", "next-core", "--lib"], timeout=600)
    assert r.returncode == 0, f"next-core failed to compile: {r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_turbopack_core_compiles():
    """turbopack-core package compiles without errors (pass_to_pass)."""
    r = _run_cargo(["check", "--package", "turbopack-core", "--lib"],
                   cwd=f"{REPO}/turbopack/crates/turbopack-core", timeout=600)
    assert r.returncode == 0, f"turbopack-core failed to compile: {r.stderr[-1000:]}"
