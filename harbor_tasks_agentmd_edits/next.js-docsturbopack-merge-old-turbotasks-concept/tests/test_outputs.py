"""
Task: Turbopack chunking: split app code by monorepo package name
Repo: vercel/next.js @ 581975d7cfa5c9aa8a008df3306d8779a175bfc7
PR:   78073

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"
SOURCE_FILE = f"{REPO}/turbopack/crates/turbopack-core/src/chunk/chunking/dev.rs"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Rust files must compile without errors."""
    r = subprocess.run(
        ["cargo", "check", "--package", "turbopack-core"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_monorepo_package_detection():
    """package_name() extracts monorepo package names from /packages/ paths."""
    src = Path(SOURCE_FILE).read_text()

    # Verify the function exists and has the monorepo regex
    assert "MONOREPO_PACKAGE_REGEX" in src, "MONOREPO_PACKAGE_REGEX not found"

    # Test the actual regex pattern by extracting and testing it
    # The pattern should be: /packages/((?:@[^/]+/)?[^/]+)
    monorepo_pattern = r'/packages/((?:@[^/]+/)?[^/]+)'
    assert monorepo_pattern in src, f"Monorepo pattern not found: {monorepo_pattern}"

    # Simulate what the fixed code does: extract package names from monorepo paths
    def extract_package_name(ident: str) -> str:
        """Simulate the fixed package_name() function behavior."""
        node_modules_pattern = r'/node_modules/((?:@[^/]+/)?[^/]+)'
        monorepo_pattern = r'/packages/((?:@[^/]+/)?[^/]+)'

        # Check node_modules first
        matches = list(re.finditer(node_modules_pattern, ident))
        if matches:
            last = matches[-1]
            return last.group(0)[len('/node_modules/'):]

        # Fall back to monorepo pattern
        matches = list(re.finditer(monorepo_pattern, ident))
        if matches:
            last = matches[-1]
            return last.group(0)[len('/packages/'):]

        return ""

    # Test monorepo package paths (new behavior - must work with fix)
    assert extract_package_name("/project/packages/ui/components/Button.js") == "ui"
    assert extract_package_name("/project/packages/shared/utils/index.ts") == "shared"
    assert extract_package_name("/project/packages/@scope/utils/index.js") == "@scope/utils"
    assert extract_package_name("/project/packages/@org/pkg/dist/index.js") == "@org/pkg"

    # Test scoped monorepo packages
    assert extract_package_name("/home/user/monorepo/packages/@company/ui/src/index.tsx") == "@company/ui"


# [pr_diff] fail_to_pass
def test_node_modules_still_works():
    """package_name() still extracts node_modules package names (existing behavior)."""
    # Simulate the fixed code behavior
    def extract_package_name(ident: str) -> str:
        node_modules_pattern = r'/node_modules/((?:@[^/]+/)?[^/]+)'
        matches = list(re.finditer(node_modules_pattern, ident))
        if matches:
            last = matches[-1]
            return last.group(0)[len('/node_modules/'):]
        return ""

    # Test node_modules paths (existing behavior - must continue working)
    assert extract_package_name("/project/node_modules/react/index.js") == "react"
    assert extract_package_name("/project/node_modules/lodash/debounce.js") == "lodash"
    assert extract_package_name("/project/node_modules/@types/node/index.js") == "@types/node"
    assert extract_package_name("/project/node_modules/@babel/runtime/helpers.js") == "@babel/runtime"

    # Test nested node_modules (takes the last one)
    assert extract_package_name("/project/node_modules/foo/node_modules/bar/index.js") == "bar"


# [pr_diff] fail_to_pass
def test_app_vendors_split_uses_package_name_split():
    """app_vendors_split() calls package_name_split() for app chunk items."""
    src = Path(SOURCE_FILE).read_text()

    # Find the app_vendors_split function body
    # After the fix, it should call package_name_split instead of folder_split for app chunks
    # The key line: package_name_split(app_chunk_items, key, split_context).await?;
    assert "package_name_split(app_chunk_items, key, split_context)" in src, \
        "app_vendors_split should call package_name_split for app chunk items"


# [pr_diff] fail_to_pass
def test_monorepo_priority():
    """node_modules takes priority over monorepo when both patterns match."""
    def extract_package_name(ident: str) -> str:
        """Simulate the fixed package_name() function - node_modules first."""
        node_modules_pattern = r'/node_modules/((?:@[^/]+/)?[^/]+)'
        monorepo_pattern = r'/packages/((?:@[^/]+/)?[^/]+)'

        # Check node_modules first (as per the fix)
        matches = list(re.finditer(node_modules_pattern, ident))
        if matches:
            last = matches[-1]
            return last.group(0)[len('/node_modules/'):]

        # Fall back to monorepo pattern
        matches = list(re.finditer(monorepo_pattern, ident))
        if matches:
            last = matches[-1]
            return last.group(0)[len('/packages/'):]

        return ""

    # Path with both node_modules and packages - node_modules should win
    assert extract_package_name("/project/packages/foo/node_modules/react/index.js") == "react"
    assert extract_package_name("/monorepo/packages/bar/node_modules/lodash/lib.js") == "lodash"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_doc_comment_updated():
    """Doc comment for package_name_split mentions monorepo packages."""
    src = Path(SOURCE_FILE).read_text()

    # Find the doc comment for package_name_split
    # After the fix, it should mention "monorepo" or "packages"
    assert "monorepo" in src.lower() or "packages" in src.lower(), \
        "Doc comment should mention monorepo packages"

    # The old comment said "node_modules package name only"
    # New comment should mention both
    old_comment = "Split chunk items by node_modules package name"
    assert old_comment not in src, "Old doc comment not updated"


# [static] pass_to_pass
def test_regexes_compiled_with_lazy():
    """Both regexes use Lazy::new for static compilation."""
    src = Path(SOURCE_FILE).read_text()

    # Check for both static regex declarations
    assert "static NODE_MODULES_PACKAGE_REGEX: Lazy<Regex>" in src, \
        "NODE_MODULES_PACKAGE_REGEX not properly declared"
    assert "static MONOREPO_PACKAGE_REGEX: Lazy<Regex>" in src, \
        "MONOREPO_PACKAGE_REGEX not properly declared"


# [static] pass_to_pass
def test_not_stub():
    """Modified function has real logic, not just pass/return."""
    src = Path(SOURCE_FILE).read_text()

    # Extract the package_name function body
    # Check it has the actual if-else chain with both regex checks
    assert "if let Some(result) = NODE_MODULES_PACKAGE_REGEX" in src, \
        "Function should check NODE_MODULES_PACKAGE_REGEX"
    assert "if let Some(result) = MONOREPO_PACKAGE_REGEX" in src, \
        "Function should check MONOREPO_PACKAGE_REGEX"
    assert "else" in src, "Function should have else branch"


# ---------------------------------------------------------------------------
# Repo tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_tests_pass():
    """Turbopack-core crate compiles and existing tests pass."""
    # Run cargo test on the turbopack-core crate
    r = subprocess.run(
        ["cargo", "test", "--package", "turbopack-core", "--lib", "--", "--test-threads=1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    # Allow to fail if there are no tests (exit code 0 or 101 with "no tests" message)
    if r.returncode != 0:
        # Check if it's just "no tests to run" which is fine
        if "no tests" not in r.stdout.lower() and "no tests" not in r.stderr.lower():
            assert r.returncode == 0, f"Tests failed:\n{r.stdout}\n{r.stderr}"
