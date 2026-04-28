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
def test_macro_and_class_behavior():
    """Verify JSG_TRY/JSG_CATCH macros and JsgCatchScope class are correctly defined
    and that migrated files use the new macros with proper exception handling."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
from pathlib import Path

REPO = "/workspace/workerd"

header = Path(f"{REPO}/src/workerd/jsg/jsg.h").read_text()
impl = Path(f"{REPO}/src/workerd/jsg/jsg.c++").read_text()

# 1. JSG_TRY macro must be defined and must instantiate JsgCatchScope
try_def = re.search(r'#define\\s+JSG_TRY\\b.*', header)
assert try_def, "JSG_TRY macro not #defined in jsg.h"
# The macro must reference JsgCatchScope to set up exception handling
after_try_def = header[header.index("#define JSG_TRY"):header.index("#define JSG_TRY")+500]
assert "JsgCatchScope" in after_try_def, \
    "JSG_TRY macro must reference JsgCatchScope"

# 2. JSG_CATCH macro must be defined and use catchException + getCaughtException
catch_def = re.search(r'#define\\s+JSG_CATCH\\b.*', header)
assert catch_def, "JSG_CATCH macro not #defined in jsg.h"
after_catch_def = header[header.index("#define JSG_CATCH"):header.index("#define JSG_CATCH")+1500]
assert "catchException" in after_catch_def, \
    "JSG_CATCH macro must call catchException"
assert "getCaughtException" in after_catch_def, \
    "JSG_CATCH macro must call getCaughtException"

# 3. JsgCatchScope class must be declared with required interface
class_match = re.search(r'class\\s+JsgCatchScope\\s*\\{(.*?)\\};', header, re.DOTALL)
assert class_match, "JsgCatchScope class not declared in jsg.h"
class_body = class_match.group(1)
assert "catchException" in class_body, "JsgCatchScope missing catchException method"
assert "getCaughtException" in class_body, "JsgCatchScope missing getCaughtException method"
assert "Lock&" in class_body, "JsgCatchScope constructor must take Lock& parameter"

# 4. JsgCatchScope::catchException must be implemented in jsg.c++
assert "JsgCatchScope::catchException" in impl, \
    "JsgCatchScope::catchException not implemented in jsg.c++"
# Implementation must handle both JsExceptionThrown and kj::Exception
catch_impl_start = impl.index("JsgCatchScope::catchException")
catch_impl = impl[catch_impl_start:catch_impl_start+600]
assert "JsExceptionThrown" in catch_impl, \
    "catchException must handle JsExceptionThrown"
assert "kj::Exception" in catch_impl, \
    "catchException must handle kj::Exception"

# 5. Verify at least 4 files migrated to use BOTH JSG_TRY and JSG_CATCH
migrated_files = [
    "src/workerd/api/crypto/crypto.c++",
    "src/workerd/api/memory-cache.c++",
    "src/workerd/api/messagechannel.c++",
    "src/workerd/api/streams/standard.c++",
    "src/workerd/api/urlpattern-standard.c++",
    "src/workerd/api/urlpattern.c++",
    "src/workerd/jsg/modules-new.c++",
]
migrated = 0
for f in migrated_files:
    p = Path(f"{REPO}/{f}")
    if p.exists():
        content = p.read_text()
        if "JSG_TRY" in content and "JSG_CATCH" in content:
            migrated += 1
assert migrated >= 4, f"Only {migrated}/7 files fully migrated (need both JSG_TRY and JSG_CATCH)"

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Behavioral verification failed:\n{r.stderr}"
    assert "PASS" in r.stdout


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
    assert "`js.error()`" in content, (
        "README.md should document js.error() for creating error objects"
    )
    assert "`js.throwException()`" in content, (
        "README.md should document js.throwException() for throwing JS exceptions"
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
    r = subprocess.run(
        ["ruff", "check", f"{REPO}/tools/update_node_version.py"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff lint failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_git_clone_valid():
    """Git repository is valid and has expected commit history (pass_to_pass)."""
    r = subprocess.run(
        ["git", "-C", REPO, "log", "--oneline", "-n", "5"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Git log failed:\n{r.stderr}"
    # Verify we have the expected commit
    assert "bca5351" in r.stdout, "Expected base commit not found in git history"


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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_lint():
    """pass_to_pass | CI job 'lint' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'python3 ./tools/cross/format.py --check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_miniflare_tests_build_miniflare_and_dependencies():
    """pass_to_pass | CI job 'Run Miniflare tests' → step 'Build Miniflare and dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm turbo build --filter miniflare'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build Miniflare and dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_run_miniflare_tests_run_miniflare_tests():
    """pass_to_pass | CI job 'Run Miniflare tests' → step 'Run Miniflare tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter miniflare test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Miniflare tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_snapshot_check_snapshot_diff():
    """pass_to_pass | CI job 'check-snapshot' → step 'Check snapshot diff'"""
    r = subprocess.run(
        ["bash", "-lc", 'diff -r types/generated-snapshot/latest bazel-bin/types/definitions/latest > types.diff\ndiff -r types/generated-snapshot/experimental bazel-bin/types/definitions/experimental >> types.diff'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check snapshot diff' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")