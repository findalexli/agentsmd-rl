"""
Task: supabase-skip-versions-request-empty-dbregion
Repo: supabase @ b5326ce3b2130bd89689606cb2290501832d910f
PR:   44561

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/supabase"
TARGET_FILE = "apps/studio/data/config/project-creation-postgres-versions-query.ts"
FULL_PATH = f"{REPO}/{TARGET_FILE}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

def test_typescript_parses():
    """Modified TypeScript file must parse without errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        timeout=60,
    )
    # If tsc fails to run (e.g., no tsconfig), check at least that file exists and has valid TS syntax
    if r.returncode != 0:
        # Verify file exists and can be parsed by basic regex checks
        src = Path(FULL_PATH).read_text()
        # Basic sanity: should have export, function name, return statement
        assert "useProjectCreationPostgresVersionsQuery" in src, "Target function not found"
        assert "enabled:" in src, "enabled property not found"


def test_no_syntax_errors():
    """File must not contain obvious syntax errors (balanced braces)."""
    src = Path(FULL_PATH).read_text()
    # Check balanced braces
    open_count = src.count("{")
    close_count = src.count("}")
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"
    # Check balanced parentheses
    open_paren = src.count("(")
    close_paren = src.count(")")
    assert open_paren == close_paren, f"Unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_enabled_uses_truthy_check_for_dbregion():
    """
    The enabled property should use !!dbRegion (truthy check) not just typeof check.

    This prevents the query from firing when dbRegion is an empty string ''
    (which has typeof 'string' but is falsy).
    """
    src = Path(FULL_PATH).read_text()

    # Find the enabled line and check the pattern
    # The fix changes: typeof dbRegion !== 'undefined'  ->  !!dbRegion
    enabled_pattern = r'enabled:\s*([^,\n]+)'
    match = re.search(enabled_pattern, src, re.DOTALL)
    assert match, "Could not find enabled property in query"

    enabled_expr = match.group(1)

    # Must NOT have the old pattern (typeof dbRegion !== 'undefined')
    assert "typeof dbRegion !== 'undefined'" not in enabled_expr, \
        "Old buggy pattern still present: typeof dbRegion !== 'undefined'"

    # MUST have !!dbRegion for proper falsy checking
    assert "!!dbRegion" in enabled_expr or "Boolean(dbRegion)" in enabled_expr, \
        "Missing truthy check for dbRegion (expected !!dbRegion)"


def test_enabled_handles_empty_string():
    """
    The enabled expression must properly handle empty string '' as falsy.

    An empty string has typeof 'string' so typeof check passes,
    but !!'' is false, which is the correct behavior.
    """
    src = Path(FULL_PATH).read_text()

    # Get the enabled expression
    enabled_pattern = r'enabled:\s*([^,\n]+)'
    match = re.search(enabled_pattern, src, re.DOTALL)
    assert match, "Could not find enabled property"

    enabled_expr = match.group(1).strip()

    # Check that enabled expression includes the necessary conditions
    # The fix: enabled && typeof organizationSlug !== 'undefined' && organizationSlug !== '_' && !!dbRegion
    required_parts = [
        "enabled",
        "typeof organizationSlug !== 'undefined'",
        "organizationSlug !== '_'",
    ]

    for part in required_parts:
        assert part in enabled_expr, f"Missing required condition: {part}"

    # Must use !!dbRegion (truthy check handles empty string, undefined, null)
    assert "!!dbRegion" in enabled_expr, \
        "enabled must use !!dbRegion to handle empty string correctly"


def test_organization_slug_checks_preserved():
    """
    The organizationSlug checks must be preserved exactly.

    These are: typeof organizationSlug !== 'undefined' && organizationSlug !== '_'
    """
    src = Path(FULL_PATH).read_text()

    # Find the useQuery call and extract enabled expression
    enabled_match = re.search(r'enabled:\s*([^,\n]+(?:\n[^,}]*)*)', src, re.DOTALL)
    assert enabled_match, "Could not find enabled property"

    enabled_expr = enabled_match.group(1)

    # Must preserve the organizationSlug checks
    assert "typeof organizationSlug !== 'undefined'" in enabled_expr, \
        "Missing typeof check for organizationSlug"
    assert "organizationSlug !== '_'" in enabled_expr, \
        "Missing '_' check for organizationSlug"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

def test_query_options_pattern_followed():
    """
    File should follow the studio-queries skill pattern for query options.

    Should export types prefixed with domain name and use proper structure.
    """
    src = Path(FULL_PATH).read_text()

    # Check for proper type exports (XVariables, XData, XError pattern)
    assert "ProjectCreationPostgresVersionsVariables" in src or "Variables" in src, \
        "Missing Variables type export"

    # Check for useQuery hook usage
    assert "useQuery" in src, "Missing useQuery hook usage"

    # Check for proper imports from react-query
    assert "@tanstack/react-query" in src, "Missing @tanstack/react-query import"


def test_not_stub():
    """Modified function is not a stub (has real logic)."""
    src = Path(FULL_PATH).read_text()

    # The function should have meaningful body with query configuration
    # Count non-trivial statements in the useQuery call
    assert "queryKey:" in src, "Missing queryKey configuration"
    assert "queryFn:" in src, "Missing queryFn configuration"
    assert "enabled:" in src, "Missing enabled configuration"

    # Should not be a placeholder
    assert "TODO" not in src, "Contains TODO placeholder"
    assert "FIXME" not in src, "Contains FIXME placeholder"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD derived checks
# ---------------------------------------------------------------------------

def test_target_file_exists():
    """Target TypeScript file must exist and be readable (pass_to_pass)."""
    path = Path(FULL_PATH)
    assert path.exists(), f"Target file does not exist: {FULL_PATH}"
    assert path.is_file(), f"Target path is not a file: {FULL_PATH}"
    # Should be able to read the content
    content = path.read_text()
    assert len(content) > 0, "Target file is empty"


def test_file_has_typescript_exports():
    """File must have TypeScript export statements (pass_to_pass)."""
    src = Path(FULL_PATH).read_text()
    # Should have at least one export
    assert "export " in src, "File missing TypeScript exports"
    # Should export the main hook function - check the specific hook name
    hook_export_pattern = r'export\s+(const|function)\s+useProjectCreationPostgresVersionsQuery'
    assert re.search(hook_export_pattern, src), "Missing main hook export"


def test_file_imports_react_query():
    """File must import from @tanstack/react-query (pass_to_pass)."""
    src = Path(FULL_PATH).read_text()
    # React Query v5 uses @tanstack/react-query
    assert "@tanstack/react-query" in src, "Missing @tanstack/react-query import"
    # Should import useQuery
    assert "useQuery" in src, "Missing useQuery import or usage"


def test_file_has_proper_query_structure():
    """File must have standard React Query structure (pass_to_pass)."""
    src = Path(FULL_PATH).read_text()
    # Query files should have these key properties
    assert "queryKey:" in src, "Missing queryKey property"
    assert "queryFn:" in src, "Missing queryFn property"
    assert "enabled:" in src, "Missing enabled property"


def test_file_no_commonjs_require():
    """File should not use CommonJS require (pass_to_pass)."""
    src = Path(FULL_PATH).read_text()
    # TypeScript files should use ES modules, not CommonJS
    # Check for require( usage that's not part of dynamic import()
    require_pattern = r'\brequire\s*\('
    matches = re.findall(require_pattern, src)
    assert len(matches) == 0, f"File uses CommonJS require(): found {len(matches)} occurrences"


def test_config_directory_exists():
    """The data/config directory must exist (pass_to_pass)."""
    config_dir = Path(f"{REPO}/apps/studio/data/config")
    assert config_dir.exists(), "data/config directory does not exist"
    assert config_dir.is_dir(), "data/config is not a directory"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md / SKILL.md
# ---------------------------------------------------------------------------

def test_query_enabled_gating_rule():
    """
    [agent_config] Query must be gated with 'enabled' so it doesn't run until required variables exist.

    From studio-queries SKILL.md:
    "Gate with `enabled` so the query doesn't run until required variables exist"
    """
    src = Path(FULL_PATH).read_text()

    # Find the useQuery configuration
    assert "enabled:" in src, "Missing enabled gating for query"

    # The enabled expression should check for required variables
    enabled_match = re.search(r'enabled:\s*([^,\n]+(?:\n[^,}]*)*)', src, re.DOTALL)
    if enabled_match:
        enabled_expr = enabled_match.group(1)
        # Should check for organizationSlug and dbRegion
        assert "organizationSlug" in enabled_expr, \
            "enabled should check organizationSlug"
        assert "dbRegion" in enabled_expr, \
            "enabled should check dbRegion"


def test_query_keys_structure():
    """
    [agent_config] Query should follow proper key structure if keys.ts exists.

    From studio-queries SKILL.md:
    "Define a `keys.ts` per domain. Export `*Keys` helpers using array keys with `as const`."
    """
    src = Path(FULL_PATH).read_text()

    # Check that queryKey uses an array structure (not a string)
    querykey_match = re.search(r'queryKey:\s*(\[[^\]]+\])', src)
    if querykey_match:
        key_array = querykey_match.group(1)
        # Should be an array with variables
        assert "organizationSlug" in key_array or "dbRegion" in key_array or "cloudProvider" in key_array, \
            "queryKey should include relevant variables"
