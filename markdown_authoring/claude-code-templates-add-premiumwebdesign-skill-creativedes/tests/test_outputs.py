"""Behavioral checks for claude-code-templates-add-premiumwebdesign-skill-creativedes (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-templates")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/creative-design/premium-web-design/SKILL.md')
    assert "3. **Source topic-relevant 3D from Spline — and confirm it's unique to this site.** Build a keyword map of 8–12 terms for the product you're selling. Run three search passes: `site:my.spline.design [k" in text, "expected to find: " + "3. **Source topic-relevant 3D from Spline — and confirm it's unique to this site.** Build a keyword map of 8–12 terms for the product you're selling. Run three search passes: `site:my.spline.design [k"[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/creative-design/premium-web-design/SKILL.md')
    assert '- **AI tooling / developer tools / IDEs** → **Vercel**, **Cursor**, **Windsurf**, **Linear**, **Stripe**, **Figma**, **Arc Browser**, **Zed**, **Raycast**, **Supabase**, **Replit**, **v0.dev**, **Anth' in text, "expected to find: " + '- **AI tooling / developer tools / IDEs** → **Vercel**, **Cursor**, **Windsurf**, **Linear**, **Stripe**, **Figma**, **Arc Browser**, **Zed**, **Raycast**, **Supabase**, **Replit**, **v0.dev**, **Anth'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/creative-design/premium-web-design/SKILL.md')
    assert '**If the field is technology**, the aesthetic should skew toward: pure-white or near-black grounds (not cream); neo-grotesque sans-serifs (Söhne-feel, Inter Tight, IBM Plex Sans, Instrument Sans) as d' in text, "expected to find: " + '**If the field is technology**, the aesthetic should skew toward: pure-white or near-black grounds (not cream); neo-grotesque sans-serifs (Söhne-feel, Inter Tight, IBM Plex Sans, Instrument Sans) as d'[:80]

