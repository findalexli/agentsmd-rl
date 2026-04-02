"""
Task: opencode-subagent-footer-restore
Repo: anomalyco/opencode @ 41b0d03f6afabc30696e9ccbbdbb7c3df34fd404
PR:   #19491

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
FOOTER = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/subagent-footer.tsx"
SESSION = f"{REPO}/packages/opencode/src/cli/cmd/tui/routes/session/index.tsx"
DIALOG_MODEL = f"{REPO}/packages/opencode/src/cli/cmd/tui/component/dialog-model.tsx"
DIALOG_VARIANT = f"{REPO}/packages/opencode/src/cli/cmd/tui/component/dialog-variant.tsx"


def _strip_comments(code: str) -> str:
    """Remove single-line and multi-line JS/TS comments."""
    code = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    code = re.sub(r"/\*[\s\S]*?\*/", "", code)
    return code


def _read_stripped(path: str) -> str:
    return _strip_comments(Path(path).read_text())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified TSX files must have balanced braces."""
    for path in [FOOTER, SESSION, DIALOG_MODEL, DIALOG_VARIANT]:
        p = Path(path)
        if not p.exists():
            continue
        src = p.read_text()
        depth = 0
        for ch in src:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            assert depth >= 0, f"{path} has unbalanced braces (depth went negative)"
        assert depth == 0, f"{path} has unbalanced braces (final depth={depth})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_subagent_footer_exists_with_navigation():
    """SubagentFooter exports a component with navigation commands and event handlers."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())

    # Must export SubagentFooter
    assert re.search(
        r"export\s+(default\s+)?function\s+SubagentFooter"
        r"|export\s+\{[^}]*SubagentFooter"
        r"|export\s+const\s+SubagentFooter",
        code,
    ), "SubagentFooter not exported"

    # Must return JSX
    assert re.search(r"return\s*\([\s\S]*?<", code), "No JSX return found"

    # Must reference all 3 session navigation commands
    nav_patterns = [
        r"session[._]parent|session\.parent",
        r"session[._]child[._](cycle[._]reverse|previous)|session\.child\.previous",
        r"session[._]child[._](cycle(?![._]reverse)|next)|session\.child\.next",
    ]
    for pat in nav_patterns:
        assert re.search(pat, code), f"Missing navigation command matching: {pat}"

    # Must have JSX event handlers
    assert re.search(
        r"on(MouseUp|MouseDown|Click|Press|KeyPress|KeyDown)\s*=\s*\{", code
    ), "No event handlers found"


# [pr_diff] fail_to_pass
def test_subagent_footer_token_cost():
    """SubagentFooter computes token usage and cost for display."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())

    # Token properties accessed
    assert re.search(r"tokens\s*[.\[]\s*[\"']?input", code), "Missing tokens.input access"
    assert re.search(r"tokens\s*[.\[]\s*[\"']?output", code), "Missing tokens.output access"

    # Array iteration for accumulation
    assert re.search(
        r"\.(reduce|forEach|map|filter|find|findLast)\s*\(", code
    ) or re.search(
        r"for\s*\(\s*(const|let|var)\s+\w+\s+(of|in)", code
    ), "No array iteration found"

    # Cost accumulation
    assert re.search(r"\.cost\b|cost\s*[+]=|cost\s*:", code), "No cost logic found"

    # Number formatting
    assert re.search(
        r"Intl\.NumberFormat|toFixed|toLocaleString|Locale\.|\.format\s*\(", code
    ), "No number formatting found"


# [pr_diff] fail_to_pass
def test_session_imports_and_renders_subagent_footer():
    """Session index.tsx imports and conditionally renders SubagentFooter on parentID."""
    p = Path(SESSION)
    assert p.exists(), "Session index.tsx not found"
    code = _strip_comments(p.read_text())

    # Import
    assert re.search(
        r"import\s+.*SubagentFooter.*from\s*['\"]"
        r"|import\s*\{[^}]*SubagentFooter[^}]*\}\s*from"
        r"|require\s*\(\s*['\"].*subagent-footer",
        code,
    ), "SubagentFooter not imported in session/index.tsx"

    # Render
    assert re.search(r"<SubagentFooter", code), "SubagentFooter not rendered in JSX"

    # Conditional on parentID
    assert "parentID" in code, "No parentID condition for SubagentFooter rendering"


# [pr_diff] fail_to_pass
def test_subagent_footer_title():
    """SubagentFooter displays 'Subagent session' title text."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert re.search(r"(?i)subagent session", code), "Missing 'Subagent session' title"


# [pr_diff] fail_to_pass
def test_dialog_model_no_else():
    """dialog-model.tsx else block replaced with early return."""
    code = _read_stripped(DIALOG_MODEL)
    assert "} else {" not in code, "dialog-model.tsx still uses else block"


# [pr_diff] fail_to_pass
def test_dialog_variant_no_unused_import():
    """dialog-variant.tsx unused useSync import removed."""
    code = _read_stripped(DIALOG_VARIANT)
    assert not re.search(
        r"import\s*\{[^}]*useSync[^}]*\}\s*from", code
    ), "dialog-variant.tsx still imports unused useSync"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_dialog_model_export_preserved():
    """DialogModel component is still exported."""
    p = Path(DIALOG_MODEL)
    assert p.exists(), "dialog-model.tsx not found"
    code = p.read_text()
    assert re.search(r"export\s+(default\s+)?function\s+DialogModel", code), \
        "DialogModel export missing"


# [pr_diff] pass_to_pass
def test_dialog_variant_export_preserved():
    """DialogVariant component is still exported."""
    p = Path(DIALOG_VARIANT)
    assert p.exists(), "dialog-variant.tsx not found"
    code = p.read_text()
    assert re.search(r"export\s+(default\s+)?function\s+DialogVariant", code), \
        "DialogVariant export missing"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:84 @ 41b0d03
def test_no_else_blocks_in_modified_files():
    """No else blocks in dialog-model.tsx or subagent-footer.tsx (AGENTS.md:84)."""
    for path in [DIALOG_MODEL, FOOTER]:
        p = Path(path)
        if not p.exists():
            continue
        code = _strip_comments(p.read_text())
        count = code.count("} else {")
        assert count == 0, f"{path} has {count} else blocks (AGENTS.md:84: avoid else)"


# [agent_config] fail_to_pass — AGENTS.md:13 @ 41b0d03
def test_no_any_type_in_footer():
    """SubagentFooter must not use the 'any' type (AGENTS.md:13)."""
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert not re.search(r":\s*any\b|as\s+any\b", code), \
        "SubagentFooter uses 'any' type (AGENTS.md:13: avoid any)"


# [agent_config] fail_to_pass — AGENTS.md:12 @ 41b0d03
def test_no_try_catch_in_footer():
    """SubagentFooter must not use try/catch (AGENTS.md:12)."""
    # Regex-only because: TSX with Solid.js framework deps cannot be imported in Python
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    assert not re.search(r"\btry\s*\{", code), \
        "SubagentFooter uses try/catch (AGENTS.md:12: avoid try/catch)"


# [agent_config] fail_to_pass — AGENTS.md:70 @ 41b0d03
def test_prefer_const_in_footer():
    """SubagentFooter should use const, not let (AGENTS.md:70)."""
    # Regex-only because: TSX with Solid.js framework deps cannot be imported in Python
    p = Path(FOOTER)
    assert p.exists(), "subagent-footer.tsx does not exist"
    code = _strip_comments(p.read_text())
    # Find `let` declarations (not inside strings)
    let_matches = re.findall(r"^\s*(?:export\s+)?let\s+\w+", code, re.MULTILINE)
    assert len(let_matches) == 0, \
        f"SubagentFooter uses 'let' ({len(let_matches)}x) — prefer const (AGENTS.md:70)"
