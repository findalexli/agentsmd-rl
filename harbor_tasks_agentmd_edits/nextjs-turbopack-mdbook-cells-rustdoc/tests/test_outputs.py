"""
Task: nextjs-turbopack-mdbook-cells-rustdoc
Repo: vercel/next.js @ 196ed2b83919892d45eaf7aed80852d0c9cc38c7
PR:   91126

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
TURBO_TASKS = f"{REPO}/turbopack/crates/turbo-tasks"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust files must parse and compile without errors."""
    # Check cargo check passes on turbo-tasks crate
    r = subprocess.run(
        ["cargo", "check"],
        cwd=TURBO_TASKS,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr.decode()}"


# [static] pass_to_pass
def test_doc_tests_pass():
    """Rust documentation tests must pass."""
    r = subprocess.run(
        ["cargo", "test", "--doc"],
        cwd=TURBO_TASKS,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Doc tests failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core documentation refactor tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_vc_readme_created():
    """New Vc README.md file must be created with the mdbook content."""
    readme_path = Path(f"{TURBO_TASKS}/src/vc/README.md")
    assert readme_path.exists(), "Vc README.md must be created"

    content = readme_path.read_text()
    # Check for key content migrated from mdbook
    assert "Value cells" in content, "README must contain 'Value cells' heading"
    assert "Understanding Cells" in content, "README must contain 'Understanding Cells' section"
    assert "Constructing a Cell" in content, "README must contain 'Constructing a Cell' section"
    assert "Reading" in content and "Vc" in content, "README must document reading Vcs"


# [pr_diff] fail_to_pass
def test_vc_mod_uses_include_str():
    """Vc mod.rs must use include_str! to embed README.md documentation."""
    mod_path = Path(f"{TURBO_TASKS}/src/vc/mod.rs")
    content = mod_path.read_text()

    # Check for the include_str! directive (the key change)
    assert '#[doc = include_str!("README.md")]' in content, \
        "mod.rs must use include_str! to embed README.md documentation"

    # Ensure old inline docs were removed (should NOT have the old doc comment header)
    assert "A \"Value Cell\" (`Vc` for short) is a reference to" not in content, \
        "Old inline doc comments should be removed from mod.rs"


# [pr_diff] fail_to_pass
def test_readme_updated_cells_description():
    """Main turbo-tasks README.md must be updated to consolidate Cells into Vc description."""
    readme_path = Path(f"{TURBO_TASKS}/README.md")
    content = readme_path.read_text()

    # The PR consolidates the separate "Cells" bullet into Vc description
    # Before: separate "[Cells][book-cells]" and "[`Vc`s]" bullets
    # After: combined into a single `[Vc`s]` bullet
    vc_section = content.split("It defines some derived elements from that:")[1].split("[")[0]
    assert "[Cells]" not in vc_section or "Cells" not in content.split("It defines some derived elements from that:")[1].split("\n")[0], \
        "Separate 'Cells' bullet should be consolidated into Vc description"


# [pr_diff] fail_to_pass
def test_lib_rs_docs_updated():
    """lib.rs documentation for value macro must be updated (serde -> bincode)."""
    lib_path = Path(f"{TURBO_TASKS}/src/lib.rs")
    content = lib_path.read_text()

    # Check that serialization docs now mention bincode instead of serde
    assert "bincode::Encode" in content, "lib.rs docs should mention bincode::Encode"
    assert "bincode::Decode" in content, "lib.rs docs should mention bincode::Decode"

    # Check the updated Vc description
    assert "represents the result of a computation" in content, \
        "lib.rs should have updated Vc description"


# [pr_diff] fail_to_pass
def test_raw_vc_docs_updated():
    """raw_vc.rs must have updated intra-doc links for Vc references."""
    raw_vc_path = Path(f"{TURBO_TASKS}/src/raw_vc.rs")
    content = raw_vc_path.read_text()

    # Check for the improved link format (using separate link reference line)
    assert "[`Vc`]: crate::Vc" in content, \
        "raw_vc.rs should use separate link reference lines for Vc"


# [pr_diff] fail_to_pass
def test_typo_fixed_resolved_vc():
    """Typo in mod.rs upcast_non_strict docs must be fixed."""
    mod_path = Path(f"{TURBO_TASKS}/src/vc/mod.rs")
    content = mod_path.read_text()

    # Check the typo was fixed (double space after period -> single space)
    assert "ResolvedVc<Box<dyn MyTrait>>`>. So this function" in content, \
        "Typo in upcast_non_strict docs must be fixed (space after period)"

    # Make sure old typo isn't present
    assert "ResolvedVc<Box<dyn MyTrait>>.  So this function" not in content, \
        "Old typo with double space should not exist"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub and quality checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_vc_readme_not_empty():
    """Vc README.md must have substantial content, not be a stub."""
    readme_path = Path(f"{TURBO_TASKS}/src/vc/README.md")
    content = readme_path.read_text()

    # Should have substantial content (not just a stub)
    assert len(content) > 5000, f"README.md too short ({len(content)} chars), likely a stub"

    # Should have multiple sections
    sections = ["Understanding Cells", "Constructing a Cell", "Updating a Cell",
                "Reading", "Subtypes", "Equality", "Execution Model", "Eventual Consistency"]
    for section in sections:
        assert section in content, f"README.md missing section: {section}"


# [static] pass_to_pass
def test_resolved_vc_docs_updated():
    """resolved.rs must have new 'Reading a ResolvedVc' section."""
    resolved_path = Path(f"{TURBO_TASKS}/src/vc/resolved.rs")
    content = resolved_path.read_text()

    assert "## Reading a `ResolvedVc`" in content, \
        "resolved.rs should have new 'Reading a ResolvedVc' section"
    assert "Even though a `Vc` may be resolved" in content, \
        "resolved.rs should document that resolved Vcs still need .await"


# [static] pass_to_pass
def test_alexrc_updated():
    """.alexrc file should have 'dirty' added to the denylist."""
    alexrc_path = Path(f"{REPO}/.alexrc")
    content = alexrc_path.read_text()

    assert '"dirty"' in content, ".alexrc should include 'dirty' in denylist"
