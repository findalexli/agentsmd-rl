"""Behavioral checks for gumroad-add-claude-code-skills-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/gumroad")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert '2. Run `git diff` and `git diff --cached` to understand staged and unstaged changes.' in text, "expected to find: " + '2. Run `git diff` and `git diff --cached` to understand staged and unstaged changes.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert '- Use the imperative mood ("Add", "Fix", "Remove", not "Added", "Fixes", "Removed").' in text, "expected to find: " + '- Use the imperative mood ("Add", "Fix", "Remove", not "Added", "Fixes", "Removed").'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit/SKILL.md')
    assert '- Do NOT use conventional commit prefixes (no `feat:`, `fix:`, `chore:`, etc.).' in text, "expected to find: " + '- Do NOT use conventional commit prefixes (no `feat:`, `fix:`, `chore:`, etc.).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-issue/SKILL.md')
    assert 'The root cause. Explain the technical reason the problem exists — not just symptoms. Reference code areas and behaviors (e.g., "the PayPal webhook handler" or "the dispute resolution flow"), not speci' in text, "expected to find: " + 'The root cause. Explain the technical reason the problem exists — not just symptoms. Reference code areas and behaviors (e.g., "the PayPal webhook handler" or "the dispute resolution flow"), not speci'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-issue/SKILL.md')
    assert 'If the user points to code, trace the relevant paths to understand the root cause. Include aggregated, anonymized data that quantifies the impact when available (e.g., "99 purchases across 82 sellers ' in text, "expected to find: " + 'If the user points to code, trace the relevant paths to understand the root cause. Include aggregated, anonymized data that quantifies the impact when available (e.g., "99 purchases across 82 sellers '[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-issue/SKILL.md')
    assert '- The issue is public (open source). It must be **self-contained**: an OSS contributor who has no access to prod, Slack, or internal tools should have everything they need to implement it without aski' in text, "expected to find: " + '- The issue is public (open source). It must be **self-contained**: an OSS contributor who has no access to prod, Slack, or internal tools should have everything they need to implement it without aski'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/SKILL.md')
    assert 'Generate a concise, high-quality PR description from the current branch and its linked GitHub issue. Output to an unstaged `.md` file — never publish or update a PR.' in text, "expected to find: " + 'Generate a concise, high-quality PR description from the current branch and its linked GitHub issue. Output to an unstaged `.md` file — never publish or update a PR.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/SKILL.md')
    assert 'This PR was implemented with AI assistance using Claude Code for code generation. All code was self-reviewed.' in text, "expected to find: " + 'This PR was implemented with AI assistance using Claude Code for code generation. All code was self-reviewed.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/SKILL.md')
    assert "Use the template below. Adapt sections based on what's relevant — not every section is needed for every PR." in text, "expected to find: " + "Use the template below. Adapt sections based on what's relevant — not every section is needed for every PR."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/references/example.md')
    assert 'Inertia.js caches the entire `page.props` object in browser history state. When users navigate backward/forward, the browser restores the cached props including the flash message, causing it to re-ren' in text, "expected to find: " + 'Inertia.js caches the entire `page.props` object in browser history state. When users navigate backward/forward, the browser restores the cached props including the flash message, causing it to re-ren'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/references/example.md')
    assert 'Clear the flash prop from Inertia\'s cache immediately after displaying the message using `router.replaceProp("flash", null)`. This is a client-side operation that modifies the current page state witho' in text, "expected to find: " + 'Clear the flash prop from Inertia\'s cache immediately after displaying the message using `router.replaceProp("flash", null)`. This is a client-side operation that modifies the current page state witho'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/pr-description/references/example.md')
    assert '<img width="602" height="141" alt="Screenshot 2026-01-06 at 23 10 31" src="https://github.com/user-attachments/assets/d7b2ba00-5007-4100-bb0a-85b6fb04d87f" />' in text, "expected to find: " + '<img width="602" height="141" alt="Screenshot 2026-01-06 at 23 10 31" src="https://github.com/user-attachments/assets/d7b2ba00-5007-4100-bb0a-85b6fb04d87f" />'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'Check the diff against every applicable rule in CONTRIBUTING.md (code standards, naming conventions, testing standards, Sidekiq patterns, PR structure, etc.). The file is the single source of truth — ' in text, "expected to find: " + 'Check the diff against every applicable rule in CONTRIBUTING.md (code standards, naming conventions, testing standards, Sidekiq patterns, PR structure, etc.). The file is the single source of truth — '[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'Evaluate readability and maintainability of new/modified code. See [references/review-guidance.md](references/review-guidance.md) for what to flag vs what to leave alone. The goal is clear, explicit c' in text, "expected to find: " + 'Evaluate readability and maintainability of new/modified code. See [references/review-guidance.md](references/review-guidance.md) for what to flag vs what to leave alone. The goal is clear, explicit c'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/SKILL.md')
    assert 'Wrong conditionals, missing edge cases, race conditions, nil/null handling, off-by-one errors, security vulnerabilities (injection, XSS, CSRF). Focus on code paths introduced or modified by the PR.' in text, "expected to find: " + 'Wrong conditionals, missing edge cases, race conditions, nil/null handling, off-by-one errors, security vulnerabilities (injection, XSS, CSRF). Focus on code paths introduced or modified by the PR.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/references/review-guidance.md')
    assert "Supplementary review guidance beyond what CONTRIBUTING.md already covers. Read CONTRIBUTING.md first — this file adds the reviewer's lens." in text, "expected to find: " + "Supplementary review guidance beyond what CONTRIBUTING.md already covers. Read CONTRIBUTING.md first — this file adds the reviewer's lens."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/references/review-guidance.md')
    assert 'Evaluate readability and maintainability of new/modified code. The goal is clear, explicit code — not clever or compact code.' in text, "expected to find: " + 'Evaluate readability and maintainability of new/modified code. The goal is clear, explicit code — not clever or compact code.'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-pr/references/review-guidance.md')
    assert '- Three similar lines that could theoretically be abstracted — duplication is fine if the cases are independent' in text, "expected to find: " + '- Three similar lines that could theoretically be abstracted — duplication is fine if the cases are independent'[:80]

