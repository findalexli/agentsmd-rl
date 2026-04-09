"""
Task: uv-keyring-doctest-removal
Repo: uv @ 84a854c169ef8acdcc90692e40f6f540be74b956
PR:   18919

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/uv"
README = Path(f"{REPO}/crates/uv-keyring/README.md")
LIB_RS = Path(f"{REPO}/crates/uv-keyring/src/lib.rs")
MOCK_RS = Path(f"{REPO}/crates/uv-keyring/src/mock.rs")
CARGO_TOML = Path(f"{REPO}/crates/uv-keyring/Cargo.toml")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_uv_keyring_cargo_check():
    """uv-keyring crate compiles with cargo check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-keyring"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_uv_keyring_cargo_clippy():
    """uv-keyring crate passes clippy linting (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "-p", "uv-keyring", "--all-targets", "--all-features", "--", "-D", "warnings"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo clippy failed:\n{r.stderr[-500:]}"


# [repo_ci] pass_to_pass
def test_cargo_fmt_check():
    """Workspace code is formatted correctly (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--all", "--check"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt check failed:\n{r.stderr[-500:]}"


# [static] pass_to_pass
def test_cargo_toml_valid():
    """Cargo.toml must remain valid TOML."""
    r = subprocess.run(
        [
            "python3", "-c",
            "import tomllib, sys; "
            "tomllib.load(open(sys.argv[1], 'rb'))",
            str(CARGO_TOML),
        ],
        capture_output=True,
        timeout=10,
    )
    assert r.returncode == 0, (
        f"Cargo.toml is not valid TOML:\n{r.stderr.decode()}"
    )


# [static] pass_to_pass
def test_readme_exists_with_docs():
    """README.md must still exist and contain usage documentation."""
    assert README.exists(), "crates/uv-keyring/README.md is missing"
    content = README.read_text()
    assert len(content) > 200, "README.md appears gutted (too short)"
    assert "Entry" in content, "README.md should still document the Entry API"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_no_wrong_crate_imports():
    """README code blocks must not import from non-existent 'keyring' crate."""
    content = README.read_text()

    # Extract all Rust code blocks
    code_blocks = re.findall(r"```rust\n(.*?)```", content, re.DOTALL)

    for block in code_blocks:
        # Strip hidden lines (lines starting with #)
        visible = "\n".join(
            line for line in block.splitlines()
            if not re.match(r"^#\s", line)
        )
        # Check for bare 'keyring::' that is NOT 'uv_keyring::'
        wrong_refs = re.findall(r"(?<![_a-zA-Z])keyring::", visible)
        assert not wrong_refs, (
            f"README code block references non-existent crate 'keyring::' — "
            f"should use 'uv_keyring::' or be removed.\n"
            f"Block:\n{visible[:300]}"
        )


# [pr_diff] fail_to_pass
def test_readme_no_await_in_sync_fn():
    """README code blocks must not use .await in a non-async fn main."""
    content = README.read_text()
    code_blocks = re.findall(r"```rust\n(.*?)```", content, re.DOTALL)

    for block in code_blocks:
        # Strip hidden lines
        visible = "\n".join(
            line for line in block.splitlines()
            if not re.match(r"^#\s", line)
        )
        if ".await" not in visible:
            continue
        # If the block uses .await, it must have an async context
        # Check for: async fn main, async fn, async block, or #[tokio::main]
        has_async = bool(
            re.search(r"async\s+fn", visible)
            or re.search(r"#\[tokio::main\]", visible)
            or re.search(r"async\s*\{", visible)
        )
        assert has_async, (
            f"README code block uses .await but has no async context "
            f"(async fn / #[tokio::main] / async block).\n"
            f"Block:\n{visible[:300]}"
        )


# [pr_diff] fail_to_pass
def test_mock_no_wrong_crate_refs():
    """mock.rs doc code examples must not reference non-existent 'keyring' crate."""
    content = MOCK_RS.read_text()

    # Extract Rust code blocks from the doc comment at the top of the file
    code_blocks = re.findall(r"```rust\n(.*?)```", content, re.DOTALL)

    for block in code_blocks:
        # Strip hidden doc-test lines (starting with '# ')
        visible = "\n".join(
            line for line in block.splitlines()
            if not re.match(r"^#\s", line)
        )
        wrong_refs = re.findall(r"(?<![_a-zA-Z])keyring::", visible)
        assert not wrong_refs, (
            f"mock.rs code block references non-existent crate 'keyring::' — "
            f"should use 'uv_keyring::' or be removed.\n"
            f"Block:\n{visible[:300]}"
        )

    # Also check for hidden lines (# keyring::...) that would compile as doctests
    for block in code_blocks:
        hidden_lines = [
            line for line in block.splitlines()
            if re.match(r"^#\s", line)
        ]
        for line in hidden_lines:
            wrong_refs = re.findall(r"(?<![_a-zA-Z])keyring::", line)
            assert not wrong_refs, (
                f"mock.rs hidden doctest line references 'keyring::': {line.strip()}"
            )
