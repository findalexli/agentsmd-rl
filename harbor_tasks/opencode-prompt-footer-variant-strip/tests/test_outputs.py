"""
Task: opencode-prompt-footer-variant-strip
Repo: anomalyco/opencode @ 8446719b13a1c9566bccd206cb522f7e524b1867
PR:   #19489

Remove the unused variant_cycle keybind hint from the TUI prompt footer.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/repo")
FILE = REPO / "packages/opencode/src/cli/cmd/tui/component/prompt/index.tsx"


def _read_file() -> str:
    return FILE.read_text()


def _extract_fallback_match_block() -> str:
    """Extract the content of the last <Match when={true}> block (the default fallback).

    Returns the text between <Match when={true}> and its closing </Match>.
    """
    lines = _read_file().splitlines()
    # Find the last <Match when={true}> — this is the fallback in the footer Switch
    match_idx = -1
    for i in range(len(lines) - 1, -1, -1):
        if re.search(r"<Match\s+when=\{?\s*true\s*\}?\s*>", lines[i]):
            match_idx = i
            break
    assert match_idx != -1, "No <Match when={true}> found in file"

    # Find the closing </Match> for this block by tracking nesting
    depth = 1
    end_idx = match_idx + 1
    while end_idx < len(lines) and depth > 0:
        line = lines[end_idx]
        # Count Match opens (excluding self-closing)
        depth += len(re.findall(r"<Match[\s>]", line))
        depth -= len(re.findall(r"</Match>", line))
        end_idx += 1

    return "\n".join(lines[match_idx:end_idx])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_not_stubbed():
    """File exists and has not been replaced with a stub."""
    assert FILE.exists(), f"{FILE} does not exist"
    lines = _read_file().splitlines()
    assert len(lines) > 500, f"File has only {len(lines)} lines — looks stubbed"


# [static] pass_to_pass
def test_syntax_balanced_braces():
    """Braces and parentheses are balanced (basic syntax sanity)."""
    src = _read_file()
    braces = 0
    parens = 0
    for ch in src:
        if ch == "{":
            braces += 1
        elif ch == "}":
            braces -= 1
        elif ch == "(":
            parens += 1
        elif ch == ")":
            parens -= 1
    assert braces == 0, f"Unbalanced braces: {braces}"
    assert parens == 0, f"Unbalanced parens: {parens}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_variant_cycle_removed_from_fallback():
    """The variant_cycle keybind reference is removed from the fallback Match block."""
    block = _extract_fallback_match_block()
    assert "variant_cycle" not in block, (
        "variant_cycle reference still present in <Match when={true}> fallback block"
    )


# [pr_diff] fail_to_pass
def test_variant_list_conditional_removed_from_fallback():
    """The variant.list() conditional Show block is removed from the fallback."""
    block = _extract_fallback_match_block()
    assert "variant.list()" not in block, (
        "variant.list() conditional still present in <Match when={true}> fallback block"
    )


# [pr_diff] fail_to_pass
def test_fallback_block_agent_cycle_first():
    """In the <Match when={true}> fallback block, variant content is gone
    and agent_cycle follows directly (no variant text between Match open and agent_cycle)."""
    block = _extract_fallback_match_block()
    lines = block.splitlines()
    # The first non-whitespace content after <Match when={true}> should be agent_cycle
    content_lines = [l.strip() for l in lines[1:] if l.strip() and not l.strip().startswith("//")]
    assert len(content_lines) > 0, "Fallback Match block is empty"
    # Find first <text> element — it should reference agent_cycle, not variant
    first_text_line = None
    for l in content_lines:
        if "<text" in l or "agent_cycle" in l or "variant" in l:
            first_text_line = l
            break
    assert first_text_line is not None, "No <text> element found in fallback Match block"
    assert "variant" not in first_text_line, (
        f"variant reference found before agent_cycle: {first_text_line}"
    )
    assert "agent_cycle" in block, "agent_cycle not found in fallback Match block"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_agent_cycle_keybind_present():
    """The agent_cycle keybind hint must remain in the footer."""
    src = _read_file()
    assert "agent_cycle" in src, "agent_cycle keybind was removed (regression)"


# [pr_diff] pass_to_pass
def test_command_list_keybind_present():
    """The command_list keybind hint must remain in the footer."""
    src = _read_file()
    assert "command_list" in src, "command_list keybind was removed (regression)"


# [pr_diff] pass_to_pass
def test_prompt_export_intact():
    """The Prompt component export must still exist."""
    src = _read_file()
    assert "export function Prompt" in src, "Prompt component export missing"


# [pr_diff] pass_to_pass
def test_jsx_control_flow_intact():
    """Switch/Match JSX control flow primitives must still be used."""
    src = _read_file()
    assert "<Switch>" in src, "Switch JSX primitive missing"
    assert "<Match" in src, "Match JSX primitive missing"


# [static] pass_to_pass
def test_jsx_tags_balanced():
    """Common JSX tags must be balanced (catches orphaned tags from partial deletion)."""
    src = _read_file()
    for tag in ["text", "span", "Switch", "Match", "Show", "For"]:
        opens = len(re.findall(rf"<{tag}[\s>]", src))
        closes = len(re.findall(rf"</{tag}>", src))
        self_closing = len(re.findall(rf"<{tag}\s[^>]*/>", src))
        assert (opens - self_closing) == closes, (
            f"Tag <{tag}> unbalanced: {opens - self_closing} opens vs {closes} closes"
        )
