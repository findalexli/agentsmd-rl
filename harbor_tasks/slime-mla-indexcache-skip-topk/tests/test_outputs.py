"""
Task: slime-mla-indexcache-skip-topk
Repo: THUDM/slime @ 6e3699c83ac65c119e755ccec1a14ac87644489f
PR:   1736

skip_topk / next_skip_topk must be initialized unconditionally in __init__,
not only inside `if is_nextn:` (which is inside `if self.use_nsa:`).
The agent edits docker/patch/latest/sglang.patch to fix this.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

# AST-only because: the patched code targets sglang's DeepseekV2AttentionMLA which
# requires torch, triton, CUDA — none available in this CPU container. We analyse
# the patch text (the artifact being modified) structurally instead.
"""

import pytest
from pathlib import Path

REPO = "/workspace/slime"
PATCH_FILE = Path(REPO) / "docker/patch/latest/sglang.patch"


# ---------------------------------------------------------------------------
# Helpers — extract the deepseek_v2.py section from sglang.patch
# ---------------------------------------------------------------------------

def _dsv2_section():
    """Return the raw text of the deepseek_v2.py diff section from sglang.patch."""
    content = PATCH_FILE.read_text()
    marker = "python/sglang/srt/models/deepseek_v2.py"
    for section in content.split("diff --git "):
        if marker in section.split("\n")[0]:
            return section
    return ""


def _dsv2_added_lines():
    """Return lines from added (+) hunks in the deepseek_v2.py section.

    Each returned line has its leading '+' stripped so indentation is preserved.
    Context lines (space-prefixed) are excluded — we want only new additions.
    """
    section = _dsv2_section()
    lines = []
    in_hunk = False
    for line in section.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])  # strip leading '+'
    return lines


def _dsv2_all_hunk_lines():
    """Return both context and added lines from hunks (strips the diff prefix).

    Removed lines (-) are excluded. Used for pass_to_pass checks that look
    for code present in both base and fixed versions.
    """
    section = _dsv2_section()
    lines = []
    in_hunk = False
    for line in section.split("\n"):
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-") and not line.startswith("---"):
            continue  # skip removed lines
        if line.startswith("+") and not line.startswith("+++"):
            lines.append(line[1:])
        elif line.startswith(" "):
            lines.append(line[1:])
    return lines


def _min_indent_of_assignment(attr_name, added_only=True):
    """Find minimum indentation of 'self.attr_name = ...' lines.

    If added_only=True, only inspect added (+) lines; otherwise include context.
    Returns None if the attribute assignment is not found.
    """
    lines = _dsv2_added_lines() if added_only else _dsv2_all_hunk_lines()
    min_indent = float("inf")
    for line in lines:
        if f"self.{attr_name} = " in line and "==" not in line:
            indent = len(line) - len(line.lstrip())
            if indent < min_indent:
                min_indent = indent
    return min_indent if min_indent != float("inf") else None


def _hunk_text():
    """All non-blank, non-comment hunk lines joined for substring search."""
    return "\n".join(
        l for l in _dsv2_all_hunk_lines()
        if l.strip() and not l.strip().startswith("#")
    )


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_patch_targets_deepseek_v2():
    """Patch file exists and modifies deepseek_v2.py."""
    assert PATCH_FILE.exists(), f"{PATCH_FILE} does not exist"
    content = PATCH_FILE.read_text()
    assert "deepseek_v2.py" in content, "sglang.patch does not modify deepseek_v2.py"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core bug: attrs must not require use_nsa=True
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skip_topk_init_unconditional():
    """self.skip_topk must be initialized unconditionally, not only inside `if is_nextn:`.

    Base commit layout in sglang.patch (buggy):
        +            if is_nextn:          # indent 12 — inside if self.use_nsa:
        +                self.skip_topk = False   # indent 16, conditional

    Fixed layout (correct):
        +        self.skip_topk = False    # indent 8, unconditional before if self.use_nsa:
    """
    min_indent = _min_indent_of_assignment("skip_topk")
    assert min_indent is not None, (
        "self.skip_topk assignment not found in sglang.patch deepseek_v2.py added lines"
    )
    # indent 8  → method body, unconditional (gold fix)
    # indent 12 → inside if self.use_nsa: else branch (also valid)
    # indent 16 → inside if is_nextn: inside if self.use_nsa: (BUG)
    assert min_indent <= 12, (
        f"self.skip_topk is only assigned at indent={min_indent} — still nested inside "
        f"'if is_nextn:' (indent 12+). Non-NSA MLA models will get AttributeError. "
        f"The fix must initialize skip_topk unconditionally before 'if self.use_nsa:'."
    )


# [pr_diff] fail_to_pass
def test_next_skip_topk_init_unconditional():
    """self.next_skip_topk must be initialized unconditionally, not only inside `if is_nextn:`.

    Same bug as skip_topk: only set inside `if is_nextn:` (inside `if self.use_nsa:`),
    so non-NSA MLA models raise AttributeError in forward_absorb_prepare.
    """
    min_indent = _min_indent_of_assignment("next_skip_topk")
    assert min_indent is not None, (
        "self.next_skip_topk assignment not found in sglang.patch deepseek_v2.py added lines"
    )
    assert min_indent <= 12, (
        f"self.next_skip_topk is only assigned at indent={min_indent} — still nested inside "
        f"'if is_nextn:'. Non-NSA MLA models will AttributeError. "
        f"Initialize next_skip_topk unconditionally before 'if self.use_nsa:'."
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: topk caching infrastructure must survive
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_config_attrs_preserved():
    """index_topk_freq, index_topk_pattern, index_skip_topk_offset still configured in NSA branch."""
    text = _hunk_text()
    required = ["index_topk_freq", "index_topk_pattern", "index_skip_topk_offset"]
    missing = [r for r in required if r not in text]
    assert not missing, (
        f"Config attributes missing from sglang.patch: {', '.join(missing)}. "
        "The NSA branch must still configure topk caching parameters."
    )


# [pr_diff] pass_to_pass
def test_forward_skip_logic_preserved():
    """forward_absorb_prepare conditionally skips indexer via skip_topk with prev_topk_indices fallback."""
    text = _hunk_text()
    assert "prev_topk_indices" in text, (
        "prev_topk_indices not found in patch — cross-layer topk caching broken"
    )
    has_conditional = (
        "if not self.skip_topk" in text
        or "if self.skip_topk" in text
    )
    assert has_conditional, (
        "No conditional skip logic using skip_topk in sglang.patch forward path"
    )


# [pr_diff] pass_to_pass
def test_return_includes_topk_indices():
    """forward_absorb_prepare returns topk_indices for cross-layer caching."""
    lines = _dsv2_all_hunk_lines()
    has_tuple_return = any(
        l.strip().startswith("return output,") and "topk" in l
        or l.strip().startswith("return output, None")
        for l in lines
    )
    assert has_tuple_return, (
        "forward_absorb_prepare must return a (output, topk_indices) tuple "
        "for cross-layer topk index caching"
    )
    text = _hunk_text()
    assert "next_skip_topk" in text, (
        "next_skip_topk logic missing from patch return path"
    )


# [pr_diff] pass_to_pass
def test_decoder_layer_threads_topk():
    """DecoderLayer returns 3-tuple and DeepseekV2Model unpacks topk_indices across layers."""
    lines = _dsv2_all_hunk_lines()
    has_layer_return = any(
        l.strip().startswith("return ")
        and "hidden_states" in l
        and "residual" in l
        and "topk" in l
        for l in lines
    )
    assert has_layer_return, (
        "DeepseekV2DecoderLayer does not return 3-tuple (hidden_states, residual, topk_indices)"
    )
    has_unpack = any(
        "topk" in l and "residual" in l and "hidden_states" in l and "=" in l
        and l.strip().startswith(("hidden_states", "topk"))
        for l in lines
    )
    assert has_unpack, (
        "DeepseekV2Model does not unpack topk_indices from layer call"
    )
