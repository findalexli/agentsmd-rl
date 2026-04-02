"""
Task: gradio-walkthrough-selected-binding
Repo: gradio-app/gradio @ dcfc429a8125204c3aafeabcab251dd7580f9a60
PR:   12925

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/repo")
TARGET = REPO / "js" / "tabs" / "Index.svelte"


def _read_clean():
    """Read Index.svelte with HTML comments stripped."""
    src = TARGET.read_text()
    return re.sub(r"<!--[\s\S]*?-->", "", src)


def _walkthrough_block(clean: str) -> str:
    """Extract the {#if ...walkthrough} ... {:else} block."""
    m = re.search(r"\{#if\b[^}]*walkthrough[^}]*\}([\s\S]*?)\{:else\}", clean)
    assert m, "No {#if ...walkthrough} ... {:else} block found"
    return m.group(1)


def _else_block(clean: str) -> str:
    """Extract the {:else} ... {/if} block."""
    m = re.search(r"\{:else\}([\s\S]*?)\{/if\}", clean)
    assert m, "No {:else} ... {/if} block found"
    return m.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_integrity():
    """Index.svelte must exist and retain at least 8 of 10 original patterns."""
    assert TARGET.is_file() and TARGET.stat().st_size > 0, f"{TARGET} missing or empty"
    clean = _read_clean()
    patterns = [
        r"import\s.*Gradio.*from\s+['\"]@gradio/utils['\"]",
        r"import\s.*Tabs.*from\s+['\"]\.\/shared\/Tabs\.svelte['\"]",
        r"import\s.*Walkthrough.*from\s+['\"]\.\/shared\/Walkthrough\.svelte['\"]",
        r"\$effect\s*\(",
        r"gradio\.dispatch\(['\"]gradio_tab_select['\"]",
        r"initial_tabs",
        r"<slot\s*/?>",
        r"\{#if\b[^}]*walkthrough",
        r"\{:else\}",
        r"\{/if\}",
    ]
    passed = sum(1 for p in patterns if re.search(p, clean))
    assert passed >= 8, f"Integrity: only {passed}/10 original patterns found"


# [static] pass_to_pass
def test_not_stub():
    """File must not be truncated — original is ~65 lines."""
    lines = TARGET.read_text().splitlines()
    assert len(lines) >= 50, f"File only has {len(lines)} lines (expected >= 50)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_walkthrough_bind_selected():
    """Walkthrough component must use bind:selected (two-way binding) in the
    {#if walkthrough} block — the core fix for back-and-forward navigation."""
    clean = _read_clean()
    wblock = _walkthrough_block(clean)
    tags = re.findall(r"<Walkthrough\b([^>]*?)>", wblock, re.S)
    assert tags, "No <Walkthrough> tag found in walkthrough block"
    assert any(re.search(r"\bbind:selected\b", t) for t in tags), (
        "Walkthrough tag(s) found but none use bind:selected"
    )


# [pr_diff] fail_to_pass
def test_no_oneway_selected_on_walkthrough():
    """Within the walkthrough block, <Walkthrough> must NOT retain a bare
    selected= (without bind:) — that one-way binding is the root cause."""
    clean = _read_clean()
    wblock = _walkthrough_block(clean)
    tags = re.findall(r"<Walkthrough\b([^>]*?)>", wblock, re.S)
    assert tags, "No <Walkthrough> tag found in walkthrough block"
    for attrs in tags:
        neutralized = attrs.replace("bind:selected", "__BOUND__")
        assert not re.search(r"\bselected\s*[={]", neutralized), (
            "One-way selected= still present on Walkthrough"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_tabs_retains_bind_selected():
    """Tabs component in {:else} branch must keep its bind:selected."""
    clean = _read_clean()
    eblock = _else_block(clean)
    tags = re.findall(r"<Tabs\b([^>]*?)>", eblock, re.S)
    assert any(re.search(r"\bbind:selected\b", t) for t in tags), (
        "Tabs missing bind:selected in else block"
    )


# [pr_diff] pass_to_pass
def test_event_dispatches_both_branches():
    """Both Walkthrough and Tabs branches must fire on:change and on:select."""
    clean = _read_clean()
    wblock = _walkthrough_block(clean)
    eblock = _else_block(clean)
    assert "on:change" in wblock and "on:select" in wblock, (
        f"Walkthrough branch missing event handlers"
    )
    assert "on:change" in eblock and "on:select" in eblock, (
        f"Tabs branch missing event handlers"
    )


# [pr_diff] pass_to_pass
def test_effect_gradio_tab_select():
    """The reactive $effect dispatching gradio_tab_select must remain intact."""
    clean = _read_clean()
    assert re.search(r"\$effect\s*\(\s*\(\)\s*=>\s*\{", clean), (
        "$effect block not found"
    )
    assert "gradio_tab_select" in clean, "gradio_tab_select dispatch missing"
    assert "gradio.props.selected" in clean, "gradio.props.selected reference missing"
