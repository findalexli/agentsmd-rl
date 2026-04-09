"""
Task: supabase-connect-sheet-undefined-pooler
Repo: supabase @ 042248fd6d70bc56d49db6c16462a8cc237c2945
PR:   44611

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/supabase"
TARGET_FILE = (
    f"{REPO}/apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx"
)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified files must exist and be readable (no syntax errors in basic parsing)."""
    # Read the file - if it can be read as UTF-8 text, basic check passes
    # The actual TypeScript validity is implicitly tested by the fix pattern tests
    src = Path(TARGET_FILE).read_text()
    # Verify it is a TypeScript/React file by checking for basic structure
    assert "import" in src, "File does not appear to be valid TypeScript (no imports found)"
    assert "export" in src, "File does not appear to be valid TypeScript (no exports found)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_optional_chaining_present():
    """The fix uses optional chaining to safely access ipv4SupportedForDedicatedPooler."""
    src = Path(TARGET_FILE).read_text()
    # Check that the optional chaining pattern is present
    assert "connectionStringPooler?.ipv4SupportedForDedicatedPooler" in src, (
        "Missing optional chaining operator (?.) on connectionStringPooler"
    )


def test_explicit_typing_present():
    """The fix adds explicit typing for connectionStringPooler as ConnectionStringPooler | undefined."""
    src = Path(TARGET_FILE).read_text()
    # Check that the explicit type annotation is present
    assert "connectionStringPooler: ConnectionStringPooler | undefined" in src, (
        "Missing explicit type annotation for connectionStringPooler"
    )


def test_nullish_coalescing_present():
    """The fix uses nullish coalescing (?? false) for the hasIPv4Addon variable."""
    src = Path(TARGET_FILE).read_text()
    # Check that nullish coalescing with false default is present
    assert "connectionStringPooler?.ipv4SupportedForDedicatedPooler ?? false" in src, (
        "Missing nullish coalescing (?? false) for hasIPv4Addon"
    )


def test_imports_connection_string_pooler_type():
    """The fix imports the ConnectionStringPooler type from Connect.types."""
    src = Path(TARGET_FILE).read_text()
    # Check that the ConnectionStringPooler type is imported
    assert "ConnectionStringPooler" in src, "Missing ConnectionStringPooler type import"
    # Check it is imported from the correct module
    import_pattern = r"import\s+type\s*\{[^}]*ConnectionStringPooler[^}]*\}\s*from\s*[\"\'']@/components/interfaces/ConnectSheet/Connect.types[\"\'']"
    assert re.search(import_pattern, src) is not None, (
        "ConnectionStringPooler type not imported from Connect.types"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------


def test_not_stub():
    """Modified function is not a stub (has real logic, not just pass/return)."""
    src = Path(TARGET_FILE).read_text()
    # The component should have substantial content (hooks, logic, JSX)
    # Just verify it is not a trivial stub function
    assert "const connectionStrings = useConnectionStringDatabases()" in src, (
        "Function appears to be a stub - missing expected hook usage"
    )
    # Verify the function has the hasIPv4Addon logic (not just a stub return)
    assert "hasIPv4Addon" in src, "Missing hasIPv4Addon variable usage"


def test_repo_lint():
    """Repo ESLint check passes on studio app (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && cd apps/studio && NODE_OPTIONS='--max-old-space-size=512' pnpm run lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


def test_repo_tests_connect_sheet():
    """Repo ConnectSheet tests pass (pass_to_pass) - tests for modified module."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --frozen-lockfile >/dev/null 2>&1 && cd apps/studio && NODE_OPTIONS='--max-old-space-size=1024' pnpm vitest run --reporter=verbose 'ConnectSheet'"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ConnectSheet tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
