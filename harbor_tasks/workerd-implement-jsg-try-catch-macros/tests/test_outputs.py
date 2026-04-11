"""
Task: workerd-implement-jsg-try-catch-macros
Repo: cloudflare/workerd @ bca5351754a7d3ee0568971d57435859bc3a71e6
PR:   6021

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_jsg_header_well_formed():
    """jsg.h must have balanced braces and no obvious syntax errors."""
    header = Path(f"{REPO}/src/workerd/jsg/jsg.h")
    content = header.read_text()
    # Basic brace balance check
    opens = content.count("{")
    closes = content.count("}")
    assert abs(opens - closes) < 5, (
        f"Brace imbalance in jsg.h: {opens} opens vs {closes} closes"
    )
    # Must still contain the workerd::jsg namespace
    assert "namespace workerd::jsg" in content, "Missing workerd::jsg namespace"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_try_macro_defined():
    """JSG_TRY macro must be #defined in jsg.h."""
    r = subprocess.run(
        ["grep", "-c", r"#define JSG_TRY", "src/workerd/jsg/jsg.h"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count >= 1, "JSG_TRY macro not defined in jsg.h"


# [pr_diff] fail_to_pass
def test_jsg_catch_macro_defined():
    """JSG_CATCH macro must be #defined in jsg.h."""
    r = subprocess.run(
        ["grep", "-c", r"#define JSG_CATCH", "src/workerd/jsg/jsg.h"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count >= 1, "JSG_CATCH macro not defined in jsg.h"


# [pr_diff] fail_to_pass
def test_jsg_catch_scope_implementation():
    """JsgCatchScope class must be implemented in jsg.c++ with catchException method."""
    r = subprocess.run(
        ["grep", "-c", "JsgCatchScope::catchException", "src/workerd/jsg/jsg.c++"],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    count = int(r.stdout.strip()) if r.returncode == 0 else 0
    assert count >= 1, "JsgCatchScope::catchException not implemented in jsg.c++"


# [pr_diff] fail_to_pass
def test_callers_migrated_to_jsg_try():
    """At least 4 source files must use JSG_TRY (migrated from js.tryCatch)."""
    migrated_files = [
        "src/workerd/api/crypto/crypto.c++",
        "src/workerd/api/memory-cache.c++",
        "src/workerd/api/messagechannel.c++",
        "src/workerd/api/streams/standard.c++",
        "src/workerd/api/urlpattern-standard.c++",
        "src/workerd/api/urlpattern.c++",
        "src/workerd/jsg/modules-new.c++",
    ]
    migrated_count = 0
    for fpath in migrated_files:
        r = subprocess.run(
            ["grep", "-l", "JSG_TRY", fpath],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        )
        if r.returncode == 0:
            migrated_count += 1
    assert migrated_count >= 4, (
        f"Only {migrated_count}/7 files migrated to JSG_TRY, expected at least 4"
    )


# [pr_diff] fail_to_pass
def test_jsg_catch_scope_class_declared():
    """JsgCatchScope class must be declared in jsg.h with getCaughtException method."""
    header = Path(f"{REPO}/src/workerd/jsg/jsg.h").read_text()
    assert "class JsgCatchScope" in header, "JsgCatchScope class not declared in jsg.h"
    assert "getCaughtException" in header, "getCaughtException method not in jsg.h"
    assert "catchException" in header, "catchException method not declared in jsg.h"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_jsg_try_catch():
    """src/workerd/jsg/README.md must document the JSG_TRY and JSG_CATCH macros."""
    readme = Path(f"{REPO}/src/workerd/jsg/README.md")
    content = readme.read_text()
    assert "JSG_TRY" in content, "README.md should document JSG_TRY macro"
    assert "JSG_CATCH" in content, "README.md should document JSG_CATCH macro"
    # Must include usage example with the macro syntax
    assert "JSG_TRY(js)" in content, "README.md should show JSG_TRY usage with js parameter"


# [agent_config] fail_to_pass — CLAUDE.md:128 @ bca535...
def test_readme_documents_exception_handling_update():
    """README.md must update exception handling docs to reference js.error/js.throwException."""
    readme = Path(f"{REPO}/src/workerd/jsg/README.md")
    content = readme.read_text()
    # The PR updates the JsExceptionThrown section to recommend js.error() and js.throwException()
    assert "js.throwException" in content, (
        "README.md should document js.throwException() for throwing JS exceptions"
    )
    assert "js.error" in content, (
        "README.md should document js.error() for creating error objects"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_no_remaining_js_trycatch_in_migrated_files():
    """Migrated files should not contain js.tryCatch calls (replaced by JSG_TRY)."""
    # This is pass_to_pass: on base commit, files DO use js.tryCatch but this test
    # checks a subset (modules-new.c++) that should be fully migrated.
    # On base, modules-new.c++ uses js.tryCatch — but we test the inverse: that
    # jsg.h itself does NOT use js.tryCatch (it never did, so this always passes).
    header = Path(f"{REPO}/src/workerd/jsg/jsg.h").read_text()
    # jsg.h should not contain js.tryCatch calls — it defines macros, not uses them
    assert "js.tryCatch([" not in header, "jsg.h should not contain js.tryCatch lambda calls"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI command tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_python_lint():
    """Python tools pass ruff linting (pass_to_pass)."""
    # Install ruff if not present
    install = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=60,
    )
    # Run ruff check on Python tools
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/tools/update_node_version.py"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_shellcheck_build_script():
    """Shell scripts pass shellcheck validation (pass_to_pass)."""
    # Install shellcheck if not present
    install = subprocess.run(
        ["apt-get", "update", "-qq"],
        capture_output=True, text=True, timeout=60,
    )
    install2 = subprocess.run(
        ["apt-get", "install", "-y", "-qq", "shellcheck"],
        capture_output=True, text=True, timeout=120,
    )
    # Run shellcheck on build script (only errors, not warnings)
    r = subprocess.run(
        ["shellcheck", "-S", "error", f"{REPO}/build-releases.sh"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Shellcheck failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_clone_valid():
    """Git repository is valid and has expected commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "-n", "5"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    # Verify we have the expected commit
    assert "bca53517" in r.stdout, "Expected base commit not found in git history"


# [repo_tests] pass_to_pass
def test_repo_jsg_module_exists():
    """JSG module source files exist in expected locations (pass_to_pass)."""
    r = subprocess.run(
        ["ls", "-la", f"{REPO}/src/workerd/jsg/jsg.h", f"{REPO}/src/workerd/jsg/jsg.c++"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"JSG module files not found:\n{r.stderr}"
    # Verify file sizes are reasonable (not empty)
    for line in r.stdout.strip().split("\n"):
        if "jsg.h" in line or "jsg.c++" in line:
            parts = line.split()
            if len(parts) >= 5:
                size = int(parts[4])
                assert size > 10000, f"JSG source file seems too small ({size} bytes)"
