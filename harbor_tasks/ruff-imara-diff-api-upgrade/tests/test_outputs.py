"""
Task: ruff-imara-diff-api-upgrade
Repo: astral-sh/ruff @ 459f20220ac0f8467e47779f21420fecab154c9d

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/ruff"
FMT_DEV = f"{REPO}/crates/ruff_dev/src/format_dev.rs"
BASE_COMMIT = "459f20220ac0f8467e47779f21420fecab154c9d"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cargo_check_ruff_dev():
    """Code compiles with imara-diff 0.2.x — cargo check on ruff_dev crate."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff_dev"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check -p ruff_dev failed:\n{r.stderr.decode()[-2000:]}"
    )


# [pr_diff] fail_to_pass
def test_imara_diff_version_upgraded():
    """Workspace Cargo.toml pins imara-diff to 0.2.x."""
    cargo_toml = Path(f"{REPO}/Cargo.toml").read_text()
    # Must match version = "0.2" or "0.2.0" etc.
    import re
    assert re.search(r'imara-diff\s*=\s*\{\s*version\s*=\s*"0\.2', cargo_toml), (
        "Cargo.toml does not specify imara-diff 0.2.x"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_cargo_check_ruff_cli():
    """Parent crate still compiles — no regressions in public interface."""
    r = subprocess.run(
        ["cargo", "check", "-p", "ruff"],
        cwd=REPO, capture_output=True, timeout=300,
    )
    assert r.returncode == 0, (
        f"cargo check -p ruff failed:\n{r.stderr.decode()[-2000:]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_format_dev_not_truncated():
    """format_dev.rs retains substantial content (not stubbed/truncated)."""
    content = Path(FMT_DEV).read_text()
    line_count = content.count("\n")
    assert line_count > 200, (
        f"format_dev.rs has only {line_count} lines — likely truncated or stubbed"
    )


# [static] pass_to_pass
def test_statistics_struct_intact():
    """Statistics struct and its diff-related methods are still present."""
    content = Path(FMT_DEV).read_text()
    assert "pub(crate) struct Statistics" in content, "Statistics struct missing"
    assert "fn from_versions" in content, "from_versions method missing"
    assert "fn similarity_index" in content, "similarity_index method missing"
    assert "fn jaccard_index" in content, "jaccard_index method missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:76 @ 459f2022
def test_imports_at_file_top():
    """Rust imports go at file top, not inside function bodies (AGENTS.md:76)."""
    content = Path(FMT_DEV).read_text()
    in_fn = False
    for line in content.splitlines():
        stripped = line.strip()
        # Rough heuristic: detect function body start
        if stripped.startswith("fn ") or stripped.startswith("pub fn ") or \
           stripped.startswith("pub(crate) fn "):
            in_fn = True
        if in_fn and stripped.startswith("use imara_diff"):
            assert False, "imara_diff imported inside a function body"
        # Reset on next top-level item
        if in_fn and (stripped.startswith("impl ") or stripped.startswith("pub struct ") or
                      stripped.startswith("pub(crate) struct ") or
                      stripped.startswith("mod ") or stripped.startswith("#[")):
            in_fn = False


# [agent_config] pass_to_pass — AGENTS.md:79 @ 459f2022
def test_no_new_unwrap():
    """No new .unwrap() calls added in format_dev.rs (AGENTS.md:79)."""
    # Count .unwrap() in current file
    content = Path(FMT_DEV).read_text()
    curr_count = content.count(".unwrap()")
    # Count in base commit
    r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:crates/ruff_dev/src/format_dev.rs"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    base_content = r.stdout.decode() if r.returncode == 0 else ""
    base_count = base_content.count(".unwrap()")
    assert curr_count <= base_count, (
        f"New .unwrap() calls added: {base_count} -> {curr_count}"
    )


# [agent_config] pass_to_pass — AGENTS.md:79 @ 459f2022
def test_no_new_panic_or_unreachable():
    """No new panic!() or unreachable!() macros in format_dev.rs (AGENTS.md:79)."""
    content = Path(FMT_DEV).read_text()
    r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:crates/ruff_dev/src/format_dev.rs"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    base_content = r.stdout.decode() if r.returncode == 0 else ""
    for macro in ["panic!", "unreachable!"]:
        curr = content.count(macro)
        base = base_content.count(macro)
        assert curr <= base, (
            f"New {macro} added in format_dev.rs: {base} -> {curr}"
        )


# [agent_config] pass_to_pass — AGENTS.md:81 @ 459f2022
def test_no_allow_attribute_over_expect():
    """New lint suppressions should use #[expect()] not #[allow()] (AGENTS.md:81)."""
    content = Path(FMT_DEV).read_text()
    r = subprocess.run(
        ["git", "show", f"{BASE_COMMIT}:crates/ruff_dev/src/format_dev.rs"],
        cwd=REPO, capture_output=True, timeout=10,
    )
    base_content = r.stdout.decode() if r.returncode == 0 else ""
    curr_allows = content.count("#[allow(")
    base_allows = base_content.count("#[allow(")
    assert curr_allows <= base_allows, (
        f"New #[allow()] attributes added — use #[expect()] instead (AGENTS.md:81): "
        f"{base_allows} -> {curr_allows}"
    )
