"""Behavioral checks for antigravity-awesome-skills-featindexing-issue-auditor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/indexing-issue-auditor/SKILL.md')
    assert "Act as a **Senior Technical SEO Architect, Web Infrastructure Engineer, and Site Reliability Auditor**. Your objective is to perform a deep-dive scan of a website's architecture to identify, diagnose," in text, "expected to find: " + "Act as a **Senior Technical SEO Architect, Web Infrastructure Engineer, and Site Reliability Auditor**. Your objective is to perform a deep-dive scan of a website's architecture to identify, diagnose,"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/indexing-issue-auditor/SKILL.md')
    assert '- **SSR & Hydration**: Verify if Googlebot is seeing the same content as users in JavaScript-heavy environments (Next.js/Nuxt). Detect if "hidden" content requires client-side hydration that Google ca' in text, "expected to find: " + '- **SSR & Hydration**: Verify if Googlebot is seeing the same content as users in JavaScript-heavy environments (Next.js/Nuxt). Detect if "hidden" content requires client-side hydration that Google ca'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/indexing-issue-auditor/SKILL.md')
    assert 'Detect 404s, "Crawled but not indexed", "Soft 404s", and noindex tags. Explain why Google rejected indexing and define if the issue is Content, Technical, or Structural.' in text, "expected to find: " + 'Detect 404s, "Crawled but not indexed", "Soft 404s", and noindex tags. Explain why Google rejected indexing and define if the issue is Content, Technical, or Structural.'[:80]

