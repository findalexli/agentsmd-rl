"""
Task: prisma-client-noargs-error-readme-urls
Repo: prisma/prisma @ 58fec5e43a794832bb4c5ec3f5f3f9513bbaa657
PR:   28737

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
CLIENT_FILE = Path(REPO) / "packages" / "client" / "src" / "runtime" / "getPrismaClient.ts"
README_FILE = Path(REPO) / "README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files parse without syntax errors."""
    # Use node to check basic JS/TS syntax (won't catch type errors, but catches parse errors)
    r = subprocess.run(
        ["node", "--check", "--input-type=module"],
        input=b"",  # dummy — just verify node works
        capture_output=True,
        timeout=10,
    )
    # Verify the modified file is valid TypeScript by checking it parses as a module
    # (node can't directly parse .ts, so we check the file is non-empty and has valid structure)
    content = CLIENT_FILE.read_text()
    assert len(content) > 1000, "getPrismaClient.ts should be a substantial file"
    # Check balanced braces as a basic structure check
    assert content.count("{") - content.count("}") < 3, \
        "getPrismaClient.ts has unbalanced braces — likely a syntax error"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_noargs_error_thrown():
    """Constructor must throw PrismaClientInitializationError when called without args."""
    content = CLIENT_FILE.read_text()

    # The fix adds a guard that throws PrismaClientInitializationError when optionsArg is missing.
    # On base commit, there's no such guard — the code does: if (optionsArg) { validate... }
    # Accept various guard styles: !optionsArg, optionsArg === undefined, optionsArg == null, etc.
    has_guard = bool(re.search(
        r'if\s*\(\s*!optionsArg\b|'
        r'if\s*\(\s*optionsArg\s*===?\s*(undefined|null)\b|'
        r'if\s*\(\s*(undefined|null)\s*===?\s*optionsArg\b|'
        r'if\s*\(\s*typeof\s+optionsArg\s*===?\s*["\']undefined["\']\b',
        content,
    ))
    assert has_guard, \
        "getPrismaClient.ts must check for missing optionsArg and throw"
    assert "PrismaClientInitializationError" in content, \
        "Must use PrismaClientInitializationError for the error"

    # Verify the throw is in the right context (inside constructor, before config assignment)
    constructor_match = re.search(
        r'constructor\(optionsArg.*?\{(.*?)// prevents unhandled error',
        content,
        re.DOTALL,
    )
    assert constructor_match, "Could not find constructor body"
    constructor_body = constructor_match.group(1)

    # The guard must come BEFORE config assignment
    guard_pos = re.search(
        r'if\s*\(\s*(!optionsArg|optionsArg\s*===?\s*(undefined|null)|typeof\s+optionsArg)',
        constructor_body,
    )
    config_pos = constructor_body.find("configOverride")
    assert guard_pos is not None, "Guard check must exist in constructor"
    assert config_pos >= 0, "Config override must exist in constructor"
    assert guard_pos.start() < config_pos, \
        "Guard check for missing optionsArg must come BEFORE config override access"


# [pr_diff] fail_to_pass
def test_error_message_content():
    """Error message must guide users on correct PrismaClient construction."""
    content = CLIENT_FILE.read_text()

    # The error message should help users understand what they need to pass.
    # Find the throw block near the optionsArg guard.
    # Look for throw + PrismaClientInitializationError in the constructor's early section
    constructor_match = re.search(
        r'constructor\(optionsArg.*?\{(.*?)// prevents unhandled error',
        content,
        re.DOTALL,
    )
    assert constructor_match, "Could not find constructor body"
    early_body = constructor_match.group(1)

    # There must be a throw with PrismaClientInitializationError in the early guard
    assert "throw new PrismaClientInitializationError" in early_body, \
        "Must throw PrismaClientInitializationError in the optionsArg guard"

    # Extract the section between the throw and the next closing brace of the if-block
    throw_pos = early_body.find("throw new PrismaClientInitializationError")
    assert throw_pos >= 0
    error_section = early_body[throw_pos:throw_pos + 500]

    # The error should mention PrismaClient or options to guide the user
    assert "PrismaClient" in error_section or "options" in error_section.lower(), \
        "Error message should mention PrismaClient or options to guide the user"


# [pr_diff] fail_to_pass

    # On the base commit, validatePrismaClientOptions is inside: if (optionsArg) { validate... }
    # After fix, it's called unconditionally (the guard throws before reaching it)
    # Check there's no pattern: if (optionsArg) { ... validatePrismaClientOptions ... }
    conditional_validate = re.search(
        r'if\s*\(optionsArg\)\s*\{[^}]*validatePrismaClientOptions',
        content,
        re.DOTALL,
    )
    assert conditional_validate is None, \
        "validatePrismaClientOptions should NOT be inside an if(optionsArg) block"

    # Verify it IS still called somewhere
    assert "validatePrismaClientOptions(optionsArg" in content, \
        "validatePrismaClientOptions must still be called with optionsArg"


# [pr_diff] fail_to_pass

    # After the null guard, optionsArg is guaranteed to be truthy,
    # so optional chaining on it is unnecessary
    # Find the adapter access pattern
    adapter_lines = [
        line.strip() for line in content.split("\n")
        if "optionsArg" in line and "adapter" in line and "optionsArg.__internal" not in line
    ]

    has_unnecessary_optional = any("optionsArg?.adapter" in line for line in adapter_lines)
    has_direct_access = any("optionsArg.adapter" in line for line in adapter_lines)

    assert not has_unnecessary_optional, \
        "optionsArg?.adapter should be optionsArg.adapter (optionsArg is guaranteed non-null after guard)"
    assert has_direct_access, \
        "Should access optionsArg.adapter directly (without optional chaining)"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README.md URL and content updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # The old URLs used /docs/concepts/components/ which are broken
    old_url_count = content.count("/docs/concepts/components/")
    assert old_url_count == 0, \
        f"README.md still has {old_url_count} broken URLs using /docs/concepts/components/ — " \
        "these should be updated to /docs/orm/ paths"

    # Verify new URLs are present
    new_url_count = content.count("/docs/orm/prisma-client")
    assert new_url_count >= 3, \
        f"README.md should have at least 3 Prisma Client doc links using /docs/orm/prisma-client " \
        f"(found {new_url_count})"

    prisma_migrate_count = content.count("/docs/orm/prisma-migrate")
    assert prisma_migrate_count >= 1, \
        "README.md should link to Prisma Migrate docs at /docs/orm/prisma-migrate"


# [config_edit] fail_to_pass

    # The PR updates the note from "Depending on your database, you may need..."
    # to "As of Prisma 7, you will need to use a driver adapter"
    assert "Prisma 7" in content, \
        "README.md should mention Prisma 7 in the driver adapter context"

    # Check that the old wording is gone
    assert "Depending on your database, you may need to use a" not in content, \
        "README.md should replace the old 'may need' wording with Prisma 7 requirement"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """getPrismaClient.ts constructor must have real logic, not just pass/return."""
    content = CLIENT_FILE.read_text()

    # The constructor should have substantial logic
    constructor_match = re.search(
        r'constructor\(optionsArg.*?\{(.*?)_createPrismaPromise',
        content,
        re.DOTALL,
    )
    assert constructor_match, "Could not find constructor body"
    body = constructor_match.group(1)

    # Should have real statements — at least the guard, config assignment, validate call
    assert len(body.strip().split("\n")) >= 5, \
        "Constructor body is too short — looks like a stub"
    assert "throw" in body, "Constructor should throw on invalid input"
    assert "validatePrismaClientOptions" in body, \
        "Constructor should validate options"
