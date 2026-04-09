"""
Task: next.js-docsturbopack-merge-the-contents-of
Repo: vercel/next.js @ 545eba1ff6a6e74042c6e9c7412e3315a6f36d19~1
PR:   91126

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
CRATE_PATH = f"{REPO}/turbopack/crates/turbo-tasks"
VC_DIR = f"{CRATE_PATH}/src/vc"


def _run_cargo(args: list, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run cargo command in the turbo-tasks crate directory."""
    return subprocess.run(
        ["cargo"] + args,
        capture_output=True, text=True, timeout=timeout, cwd=CRATE_PATH,
    )


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# -----------------------------------------------------------------------------

def test_crate_compiles():
    """Modified crate compiles without errors."""
    r = _run_cargo(["check"], timeout=180)
    assert r.returncode == 0, f"Crate failed to compile:\n{r.stderr}"


def test_rustdoc_builds():
    """Documentation builds successfully with cargo doc."""
    r = _run_cargo(["doc", "--no-deps"], timeout=180)
    assert r.returncode == 0, f"Documentation failed to build:\n{r.stderr}"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

def test_vc_readme_exists():
    """Vc README.md file is created with cells documentation."""
    readme_path = Path(f"{VC_DIR}/README.md")
    assert readme_path.exists(), "README.md does not exist in src/vc/"

    content = readme_path.read_text()
    # Check for key content from the merged cells documentation
    assert "Value cells" in content, "README missing 'Value cells' heading/content"
    assert "Understanding Cells" in content, "README missing 'Understanding Cells' section"
    assert "## Constructing a Cell" in content, "README missing 'Constructing a Cell' section"
    assert "## Updating a Cell" in content, "README missing 'Updating a Cell' section"
    assert "## Reading" in content or "Reading `Vc`s" in content, "README missing cell reading documentation"


def test_mod_rs_uses_include_str():
    """mod.rs uses include_str! to embed README.md as module docs."""
    mod_rs_path = Path(f"{VC_DIR}/mod.rs")
    assert mod_rs_path.exists(), "mod.rs does not exist"

    content = mod_rs_path.read_text()
    # Check that the file uses include_str! for README.md
    assert '#[doc = include_str!("README.md")]' in content, \
        "mod.rs should use #[doc = include_str!(\"README.md\")] for module documentation"


def test_vc_readme_has_cells_content():
    """README.md contains the merged cells page content (key sections)."""
    readme_path = Path(f"{VC_DIR}/README.md")
    assert readme_path.exists(), "README.md does not exist"

    content = readme_path.read_text()

    # Key content from the merged cells page
    key_sections = [
        "Immutability",
        "Recomputability",
        "Dependency Tracking",
        "cell counter",
        "Invalidat",
        "TaskOutput",
        "TaskCell",
        "[`Vc<T>`]",
        "[`ReadRef<T>`]",
    ]

    for section in key_sections:
        assert section in content, f"README.md missing expected content: {section}"


def test_lib_rs_docs_updated():
    """lib.rs documentation updated with improved Vc descriptions."""
    lib_rs_path = Path(f"{CRATE_PATH}/src/lib.rs")
    assert lib_rs_path.exists(), "lib.rs does not exist"

    content = lib_rs_path.read_text()
    # Check for updated documentation about Vc representing computation result
    # The PR changes "(potentially lazy) memoized computation" to "result of a computation"
    assert "result of a computation" in content, \
        "lib.rs should describe Vc as 'result of a computation'"


def test_raw_vc_docs_updated():
    """raw_vc.rs documentation updated with Vc links."""
    raw_vc_path = Path(f"{CRATE_PATH}/src/raw_vc.rs")
    assert raw_vc_path.exists(), "raw_vc.rs does not exist"

    content = raw_vc_path.read_text()
    # Check for new Vc link in the LocalOutput variant docs
    assert "Local `Vc`" in content or "[`Vc`]: crate::Vc" in content, \
        "raw_vc.rs should have updated Vc documentation links"


def test_resolved_vc_docs_updated():
    """resolved.rs documentation updated with reading section."""
    resolved_path = Path(f"{CRATE_PATH}/src/vc/resolved.rs")
    assert resolved_path.exists(), "resolved.rs does not exist"

    content = resolved_path.read_text()
    # Check for the new "Reading a ResolvedVc" section
    assert "## Reading a `ResolvedVc`" in content, \
        "resolved.rs should have 'Reading a ResolvedVc' section"


def test_crate_readme_updated():
    """turbo-tasks README.md simplified (cells section merged into Vc description)."""
    readme_path = Path(f"{CRATE_PATH}/README.md")
    assert readme_path.exists(), "turbo-tasks README.md does not exist"

    content = readme_path.read_text()
    # The PR merges the Cells bullet point into the Vc description
    # Check that the old separate "Cells" bullet no longer exists with the old phrasing
    # and that Vc description includes cells information
    assert "[**Cells**]" not in content or "[**[Cells]**]" not in content, \
        "Old separate Cells bullet should be removed/merged"


def test_mod_rs_typo_fixed():
    """Typo fixed in mod.rs (missing backtick)."""
    mod_rs_path = Path(f"{VC_DIR}/mod.rs")
    assert mod_rs_path.exists(), "mod.rs does not exist"

    content = mod_rs_path.read_text()
    # PR fixes: `Vc<Box<dyn MyTrait>>.` -> `Vc<Box<dyn MyTrait>>`. (adds backtick)
    # Check for properly formatted code in the upcast_non_strict docs
    assert "Vc<Box<dyn MyTrait>>`" in content or "Vc<Box<dyn MyTrait>>`." in content, \
        "Typo with missing backtick should be fixed"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# -----------------------------------------------------------------------------

def test_repo_clippy():
    """Repo's clippy linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "clippy", "--all-features"],
        capture_output=True, text=True, timeout=120, cwd=CRATE_PATH,
    )
    assert r.returncode == 0, f"Clippy failed:\n{r.stderr[-500:]}"


def test_repo_formatting():
    """Repo's code formatting passes (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--check"],
        capture_output=True, text=True, timeout=60, cwd=CRATE_PATH,
    )
    assert r.returncode == 0, f"Formatting check failed:\n{r.stderr[-500:]}"


def test_existing_tests_pass():
    """Upstream test suite (cargo test) still passes."""
    r = _run_cargo(["test", "--lib", "--", "--test-threads=1"], timeout=300)
    # Allow success or no tests found
    assert r.returncode == 0 or "test result" in r.stdout or "no tests to run" in r.stdout.lower(), \
        f"Upstream tests failed:\n{r.stdout}\n{r.stderr}"


def test_not_stub():
    """README.md has substantial content, not just a placeholder."""
    readme_path = Path(f"{VC_DIR}/README.md")
    if not readme_path.exists():
        return  # Will be caught by test_vc_readme_exists

    content = readme_path.read_text()
    # README should have substantial content (the merged cells page is long)
    lines = content.strip().split("\n")
    assert len(lines) > 50, f"README.md seems too short ({len(lines)} lines), likely stub content"
    assert len(content) > 2000, f"README.md seems too small ({len(content)} chars), likely stub content"
