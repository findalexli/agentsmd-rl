"""
Task: prisma-featcli-update-bundled-prismastudiocore-to
Repo: prisma/prisma @ 32fb24b53c2a46971f3093eee9934c18e0f47642
PR:   29376

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/prisma"
STUDIO_TS = Path(REPO) / "packages" / "cli" / "src" / "Studio.ts"
AGENTS_MD = Path(REPO) / "AGENTS.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Studio.ts must be valid TypeScript (no unterminated strings or brackets)."""
    content = STUDIO_TS.read_text()
    # Basic bracket balance check for TypeScript
    opens = content.count("{") + content.count("(") + content.count("[")
    closes = content.count("}") + content.count(")") + content.count("]")
    # Allow some tolerance for template literals/strings but should be close
    assert abs(opens - closes) < 10, (
        f"Bracket imbalance detected: opens={opens}, closes={closes}"
    )
    # File should still have core structure
    assert "class Studio" in content or "Studio" in content, "Studio class missing"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_transaction_procedure_handler():
    """Studio BFF must handle the 'transaction' procedure via executeTransaction."""
    content = STUDIO_TS.read_text()
    # Must check for 'transaction' procedure
    assert re.search(r"procedure\s*===?\s*['\"]transaction['\"]", content), (
        "Studio.ts must handle the 'transaction' BFF procedure"
    )
    # Must call executeTransaction on the executor
    assert "executeTransaction" in content, (
        "Studio.ts must call executeTransaction for transaction procedure"
    )
    # Must handle the error case (return serialized error if executor doesn't support it)
    # Find the transaction block and verify it has error handling
    tx_match = re.search(
        r"procedure\s*===?\s*['\"]transaction['\"].*?(?=procedure\s*===?\s*['\"]|\Z)",
        content,
        re.DOTALL,
    )
    assert tx_match, "Transaction handler block not found"
    tx_block = tx_match.group(0)
    assert "error" in tx_block.lower() or "Error" in tx_block, (
        "Transaction handler must include error handling"
    )


# [pr_diff] fail_to_pass
def test_favicon_endpoint():
    """Studio must serve a favicon at /favicon.ico."""
    content = STUDIO_TS.read_text()
    # Must have a route for /favicon.ico
    assert re.search(r"""['"]/favicon\.ico['"]""", content), (
        "Studio.ts must define a /favicon.ico route"
    )
    # The favicon should be SVG (Prisma logo)
    assert "image/svg+xml" in content, (
        "Favicon should be served as image/svg+xml"
    )
    # The HTML shell should include a favicon link tag
    assert re.search(r'rel="icon"', content) or re.search(r"rel='icon'", content), (
        "HTML template should include a <link rel='icon'> tag"
    )


# [pr_diff] fail_to_pass
def test_import_map_includes_radix_toggle():
    """HTML import map must include @radix-ui/react-toggle with React pinning."""
    content = STUDIO_TS.read_text()
    # Must have radix-ui/react-toggle in the import map
    assert "@radix-ui/react-toggle" in content, (
        "Import map must include @radix-ui/react-toggle"
    )
    # The URL should pin React deps to avoid canary React version mismatch
    # Look for the deps=react@ pattern in the URL
    assert re.search(r"deps=react@", content), (
        "Radix toggle import must pin React deps via ?deps=react@... "
        "to avoid invalid-hook-call crashes with canary React"
    )


# [pr_diff] fail_to_pass
def test_import_map_includes_chartjs():
    """HTML import map must include chart.js/auto."""
    content = STUDIO_TS.read_text()
    assert "chart.js/auto" in content, (
        "Import map must include chart.js/auto for Studio charting support"
    )
    # Should reference esm.sh for the chart.js import
    assert re.search(r"esm\.sh/chart\.js", content), (
        "chart.js should be loaded via esm.sh CDN"
    )


# [pr_diff] fail_to_pass

    # Find the import map block
    importmap_match = re.search(r"importmap.*?</script>", content, re.DOTALL)
    assert importmap_match, "Import map block not found in Studio.ts"
    importmap_block = importmap_match.group(0)

    # The import map should NOT have 4+ hardcoded React version strings
    hardcoded_react_count = len(re.findall(r"esm\.sh/react@19\.2\.0", importmap_block))
    assert hardcoded_react_count < 2, (
        f"Found {hardcoded_react_count} hardcoded React version URLs in import map. "
        "Extract the React version into a constant to avoid drift."
    )


# ---------------------------------------------------------------------------
# Config-edit tests (config_edit) — AGENTS.md update verification
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_bff_procedures_preserved():
    """Existing BFF procedures (query, sequence, sql-lint) must still be present."""
    content = STUDIO_TS.read_text()
    for proc in ["query", "sequence", "sql-lint"]:
        assert re.search(
            rf"procedure\s*===?\s*['\"]{ re.escape(proc) }['\"]", content
        ), f"BFF procedure '{proc}' must still be handled in Studio.ts"


# [static] pass_to_pass
def test_not_stub():
    """Transaction handler must have real logic, not just a pass-through."""
    content = STUDIO_TS.read_text()
    # Find the transaction handler block
    tx_match = re.search(
        r"procedure\s*===?\s*['\"]transaction['\"].*?(?=procedure\s*===?\s*['\"]|\Z)",
        content,
        re.DOTALL,
    )
    assert tx_match, "Transaction handler not found"
    tx_block = tx_match.group(0)
    # Must have substantive logic: check executor capability, call it, handle errors
    assert "executeTransaction" in tx_block, "Must call executeTransaction"
    assert re.search(r"error|Error", tx_block), "Must handle errors"
    assert re.search(r"return|ctx\.json|ctx\.body", tx_block), "Must return a response"
    # Block should have meaningful length (not just a one-liner)
    non_empty_lines = [l.strip() for l in tx_block.split("\n") if l.strip()]
    assert len(non_empty_lines) >= 5, (
        f"Transaction handler has only {len(non_empty_lines)} lines — too short for real logic"
    )
