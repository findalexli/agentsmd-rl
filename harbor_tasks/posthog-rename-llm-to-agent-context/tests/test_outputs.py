"""Behavioral tests for the LLM context → Agent context rename in PostHog.

Each test calls `grep` via subprocess against the live working-tree files,
so the assertions reflect the on-disk state the agent left behind.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/posthog")
PR_TEMPLATE = REPO / ".github" / "pull_request_template.md"
AGENTS_MD = REPO / "AGENTS.md"
AI_POLICY = REPO / "AI_POLICY.md"


def _grep(pattern: str, path: Path, fixed: bool = True, extended: bool = False) -> tuple[int, str]:
    """Run grep; return (returncode, stdout). 0 = match, 1 = no match."""
    flags = ["-c"]
    if fixed:
        flags.append("-F")
    if extended:
        # extended regex; drop -F (incompatible)
        flags = ["-cE"]
    r = subprocess.run(
        ["grep", *flags, "--", pattern, str(path)],
        capture_output=True,
        text=True,
        timeout=15,
    )
    return r.returncode, r.stdout.strip()


# ─────────────────────────── fail-to-pass (f2p) ──────────────────────────────

def test_pr_template_agent_context_heading_uncommented():
    """PR template must contain a real (uncommented) `## 🤖 Agent context` heading."""
    assert PR_TEMPLATE.exists(), f"missing file: {PR_TEMPLATE}"
    # Match the heading at the start of a line — i.e. NOT inside an HTML comment.
    rc, _ = _grep(r"^## 🤖 Agent context\s*$", PR_TEMPLATE, fixed=False, extended=True)
    assert rc == 0, (
        "PR template is missing an uncommented `## 🤖 Agent context` heading. "
        "The section must be a live heading, not wrapped in <!-- ... -->."
    )
    # And ensure it's NOT inside an HTML comment on that same line
    rc_bad, _ = _grep(r"<!--\s*## 🤖 Agent context", PR_TEMPLATE, fixed=False, extended=True)
    assert rc_bad != 0, "the `## 🤖 Agent context` heading must not be HTML-commented out"


def test_pr_template_drops_llm_context_phrase():
    """All `LLM context` mentions must be gone from the PR template."""
    assert PR_TEMPLATE.exists(), f"missing file: {PR_TEMPLATE}"
    rc, _ = _grep("LLM context", PR_TEMPLATE)
    assert rc != 0, (
        "PR template still mentions 'LLM context' — every reference should be "
        "renamed to 'Agent context'."
    )


def test_pr_template_no_uncomment_instruction():
    """The old guidance to 'uncomment this section' should be gone — the section is live now."""
    assert PR_TEMPLATE.exists()
    # Old wording told agents to uncomment the LLM context section. The whole
    # point of the rename is that the section is uncommented by default, so any
    # language asking the reader to uncomment it is stale.
    rc, _ = _grep("uncomment this section", PR_TEMPLATE)
    assert rc != 0, (
        "PR template still tells the reader to 'uncomment this section'. "
        "The Agent context section is live by default — that instruction is stale."
    )


def test_agents_md_references_agent_context_section():
    """AGENTS.md must point agents at the new section name (with the emoji)."""
    assert AGENTS_MD.exists(), f"missing file: {AGENTS_MD}"
    rc, _ = _grep("🤖 Agent context", AGENTS_MD)
    assert rc == 0, (
        "AGENTS.md PR-description rule should reference the new "
        "`## 🤖 Agent context` section by name."
    )


def test_agents_md_drops_llm_context_section_reference():
    """AGENTS.md must no longer reference the old `## LLM context` section by name.

    NOTE: AGENTS.md may still mention 'LLM context' incidentally elsewhere
    (e.g. the Temporal payload-size rule talks about LLM context as data
    flowing through workflows). What must go is the PR-descriptions rule
    that pointed agents at the literal `## LLM context` heading.
    """
    assert AGENTS_MD.exists()
    rc, _ = _grep("`## LLM context`", AGENTS_MD)
    assert rc != 0, (
        "AGENTS.md still references the old `## LLM context` section by name. "
        "The PR-description rule should now point at the renamed section."
    )
    # Also: the stale instruction to "uncomment" that section is gone.
    rc2, _ = _grep("uncomment and fill the", AGENTS_MD)
    assert rc2 != 0, (
        "AGENTS.md still tells agents to 'uncomment and fill the' section — "
        "that's stale guidance now that the section is live by default."
    )


def test_ai_policy_uses_agent_context_section():
    """AI_POLICY.md must call it the 'Agent context section' now."""
    assert AI_POLICY.exists(), f"missing file: {AI_POLICY}"
    rc, _ = _grep("Agent context section", AI_POLICY)
    assert rc == 0, (
        "AI_POLICY.md should describe the PR template as including an "
        "'Agent context section', not an 'LLM context section'."
    )


def test_ai_policy_drops_llm_disclosure_phrasing():
    """AI_POLICY.md disclosure paragraph must be reworded around 'agent', not 'LLM'."""
    assert AI_POLICY.exists()
    rc, _ = _grep("LLM context section", AI_POLICY)
    assert rc != 0, "AI_POLICY.md still says 'LLM context section'"
    rc2, _ = _grep("If an LLM co-authored or authored your PR", AI_POLICY)
    assert rc2 != 0, (
        "AI_POLICY.md still uses the old 'If an LLM co-authored or authored "
        "your PR' phrasing — should be reworded around 'agent'."
    )


# ──────────────────────────── pass-to-pass (p2p) ─────────────────────────────

def test_pr_template_preserves_problem_section():
    """`## Problem` heading must still anchor the PR template."""
    assert PR_TEMPLATE.exists()
    rc, _ = _grep("## Problem", PR_TEMPLATE)
    assert rc == 0, "PR template lost its `## Problem` section"


def test_pr_template_preserves_changes_section():
    """`## Changes` heading must still anchor the PR template."""
    assert PR_TEMPLATE.exists()
    rc, _ = _grep("## Changes", PR_TEMPLATE)
    assert rc == 0, "PR template lost its `## Changes` section"


def test_agents_md_preserves_pr_descriptions_subsection():
    """The 'PR descriptions' subsection in AGENTS.md must remain — that's where the rule lives."""
    assert AGENTS_MD.exists()
    rc, _ = _grep("### PR descriptions", AGENTS_MD)
    assert rc == 0, "AGENTS.md lost the `### PR descriptions` subsection"


def test_ai_policy_preserves_disclose_ai_usage_section():
    """The `**Disclose AI usage.**` block must still exist in AI_POLICY.md."""
    assert AI_POLICY.exists()
    rc, _ = _grep("**Disclose AI usage.**", AI_POLICY)
    assert rc == 0, "AI_POLICY.md lost the `**Disclose AI usage.**` paragraph"


def test_files_track_in_git_repo():
    """Sanity p2p — the three target files are tracked in the cloned repo at base."""
    r = subprocess.run(
        ["git", "ls-files",
         ".github/pull_request_template.md", "AGENTS.md", "AI_POLICY.md"],
        cwd=str(REPO), capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"git ls-files failed: {r.stderr}"
    tracked = set(r.stdout.split())
    expected = {".github/pull_request_template.md", "AGENTS.md", "AI_POLICY.md"}
    assert expected.issubset(tracked), (
        f"expected all three files tracked in git; got: {tracked}"
    )
