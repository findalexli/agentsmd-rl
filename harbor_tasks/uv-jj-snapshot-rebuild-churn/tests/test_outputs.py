"""
Task: uv-jj-snapshot-rebuild-churn
Repo: astral-sh/uv @ cde48c8ac8eb13e8eff5cfb5c9fc39dad69c4f19
PR:   18685

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/repo"
FILE = Path(REPO) / "crates" / "uv-cli" / "build.rs"


def _read_source():
    return FILE.read_text()


def _extract_commit_info_body(source: str) -> str:
    """Extract the body of the commit_info function by brace-matching."""
    match = re.search(r'fn\s+commit_info\s*\([^)]*\)\s*(?:->\s*[^{]+)?\s*\{', source)
    assert match, "commit_info function not found in build.rs"

    start = source.rindex('{', match.start(), match.end())
    depth = 0
    for i in range(start, len(source)):
        if source[i] == '{':
            depth += 1
        elif source[i] == '}':
            depth -= 1
            if depth == 0:
                return source[start:i + 1]
    raise AssertionError("Could not find closing brace of commit_info")


def _strip_comments(text: str) -> str:
    text = re.sub(r'//[^\n]*', '', text)
    return re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)


def _get_added_lines() -> list[str]:
    """Return the added lines (without '+' prefix) from git diff of build.rs."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/uv-cli/build.rs"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    return [l[1:] for l in result.stdout.splitlines()
            if l.startswith('+') and not l.startswith('+++')]


def _install_rust():
    """Install Rust toolchain if not already installed."""
    cargo_bin = Path.home() / ".cargo" / "bin"
    cargo_path = cargo_bin / "cargo"
    if not cargo_path.exists():
        subprocess.run(
            ["bash", "-c",
             "curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain nightly"],
            capture_output=True, timeout=120,
        )
        subprocess.run(
            [str(cargo_bin / "rustup"), "component", "add", "rustfmt", "clippy"],
            capture_output=True, timeout=60,
        )
    return str(cargo_bin)


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) -- CI checks from the repo's actual CI pipeline
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_cargo_fmt():
    """Repo's Rust code passes formatting checks (pass_to_pass)."""
    cargo_bin = _install_rust()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=120, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_clippy_uv_cli():
    """Repo's clippy lints pass for uv-cli crate (pass_to_pass)."""
    cargo_bin = _install_rust()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-cli", "--all-targets", "--all-features"],
        capture_output=True, text=True, timeout=180, cwd=REPO, env=env,
    )
    # Allow warnings - we just want to verify it compiles with clippy
    # A non-zero exit with "error:" indicates actual errors, not just warnings
    if r.returncode != 0:
        errors = [l for l in (r.stderr or "").splitlines() if "error:" in l and "warning:" not in l]
        assert not errors, f"cargo clippy found errors:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_cargo_check_uv_cli():
    """Repo's uv-cli crate compiles successfully (pass_to_pass)."""
    cargo_bin = _install_rust()
    env = {**os.environ, "PATH": f"{cargo_bin}:{os.environ.get('PATH', '')}"}
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli", "--no-default-features"],
        capture_output=True, text=True, timeout=180, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- file exists and function present
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_build_rs_exists():
    """build.rs must exist and contain the commit_info function."""
    source = _read_source()
    assert re.search(r'fn\s+commit_info\s*\(', source), \
        "commit_info function not found in build.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jj_early_return():
    """commit_info must check for .jj directory and return/guard before git ops."""
    source = _read_source()
    body = _extract_commit_info_body(source)
    clean = _strip_comments(body)

    # Must reference ".jj" somewhere in the function
    jj_refs = list(re.finditer(r'["\']\.jj["\']', clean))
    assert jj_refs, "No reference to '.jj' found in commit_info"

    jj_pos = jj_refs[0].start()

    # Must have an existence check (.exists(), .is_dir(), .try_exists()) near the .jj ref
    after_jj = clean[jj_pos:jj_pos + 400]
    assert re.search(r'\.(exists|is_dir|try_exists)\s*\(\)', after_jj), \
        "No existence check (.exists()/.is_dir()) found after .jj reference"

    # Git operations must come AFTER the .jj check
    git_ops = []
    for pattern in [r'git_head\s*\(', r'Command::new\s*\(\s*"git"', r'cargo:rerun-if-changed']:
        for m in re.finditer(pattern, clean):
            git_ops.append(m.start())

    if git_ops:
        earliest_git = min(git_ops)
        assert jj_pos < earliest_git, \
            ".jj reference must appear before git operations in commit_info"

        # Must have either an early return between .jj and git ops, or a negation guard
        returns_between = [r.start() for r in re.finditer(r'\breturn\b', clean)
                          if jj_pos < r.start() < earliest_git]
        negation_guard = bool(re.search(r'if\s+!.*\.jj', clean, re.DOTALL)) or \
                         bool(re.search(r'if\s+!\w+\.(exists|is_dir)\s*\(\)', after_jj))

        assert returns_between or negation_guard, \
            "No early return or negation guard found between .jj check and git operations"


# [pr_diff] fail_to_pass
def test_jj_code_added_to_diff():
    """Agent must have actually modified build.rs to add .jj handling (not baseline)."""
    result = subprocess.run(
        ["git", "diff", "HEAD", "--", "crates/uv-cli/build.rs"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    added_lines = [l for l in result.stdout.splitlines()
                   if l.startswith('+') and not l.startswith('+++')]
    jj_additions = [l for l in added_lines if '.jj' in l]
    assert jj_additions, \
        "build.rs diff does not contain .jj additions -- bug not fixed"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression: existing git functionality preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_git_functionality_preserved():
    """Existing git detection, commands, env vars, and rerun directives must remain."""
    source = _read_source()
    clean = _strip_comments(source)

    checks = {
        "GIT_PATH": bool(re.search(r'["\']\.git["\']', clean)),
        "GIT_HEAD_FN": bool(re.search(r'fn\s+git_head\s*\(', clean)),
        "GIT_CMD": bool(re.search(r'Command::new\s*\(\s*"git"\s*\)', clean)),
        "ENV_VARS": bool(re.search(r'UV_COMMIT', clean)),
        "RERUN_DIRECTIVES": bool(re.search(r'cargo:rerun-if-changed', clean)),
    }
    failed = [k for k, v in checks.items() if not v]
    assert not failed, \
        f"Existing git functionality broken -- missing: {', '.join(failed)}"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """commit_info function must have a substantial body (not a trivial stub)."""
    source = _read_source()
    body = _extract_commit_info_body(source)
    meaningful = [l.strip() for l in body.split('\n')
                  if l.strip() and not l.strip().startswith('//')]
    assert len(meaningful) > 10, \
        f"commit_info body only has {len(meaningful)} meaningful lines -- likely a stub"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- CLAUDE.md:7 @ cde48c8
def test_no_panic_unwrap_unsafe_in_new_code():
    """New code must not use .unwrap(), panic!, unreachable!, or unsafe (CLAUDE.md:7)."""
    # AST-only because: Rust source, no compiler available in test image
    added = _get_added_lines()
    violations = []
    for line in added:
        stripped = line.strip()
        if stripped.startswith('//'):
            continue
        if '.unwrap()' in stripped:
            violations.append(f".unwrap(): {stripped}")
        if re.search(r'\bpanic!\s*\(', stripped):
            violations.append(f"panic!: {stripped}")
        if re.search(r'\bunreachable!\s*\(', stripped):
            violations.append(f"unreachable!: {stripped}")
        if re.search(r'\bunsafe\s*\{', stripped):
            violations.append(f"unsafe block: {stripped}")
    assert not violations, \
        f"New code violates CLAUDE.md:7 (avoid unwrap/panic/unreachable/unsafe): {violations}"


# [agent_config] pass_to_pass -- CLAUDE.md:17 @ cde48c8
def test_descriptive_variable_names():
    """New code must use descriptive variable names (CLAUDE.md:17)."""
    # AST-only because: Rust source, no compiler available in test image
    added = _get_added_lines()
    bad = [l for l in added if re.search(r'\blet\s+[a-z]\s*=', l)]
    assert not bad, \
        f"Single-character variable names in new code (violates CLAUDE.md:17): {bad}"


# [agent_config] pass_to_pass -- CLAUDE.md:10 @ cde48c8
def test_prefer_expect_over_allow():
    """New code must use #[expect()] not #[allow()] for clippy suppression (CLAUDE.md:10)."""
    # AST-only because: Rust source, no compiler available in test image
    added = _get_added_lines()
    allow_attrs = [l for l in added
                   if re.search(r'#\[allow\s*\(', l.strip())
                   and not l.strip().startswith('//')]
    assert not allow_attrs, \
        f"New code uses #[allow()] instead of #[expect()] (violates CLAUDE.md:10): {allow_attrs}"
