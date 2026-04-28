"""Behavioral checks for documentation-merge-agentsmd-and-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/documentation")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Style**: Follow [12 Rules of Technical Writing](../12-rules-of-technical-writing.md) and [Style Guide](../STYLE_GUIDE.pdf)' in text, "expected to find: " + '- **Style**: Follow [12 Rules of Technical Writing](../12-rules-of-technical-writing.md) and [Style Guide](../STYLE_GUIDE.pdf)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Branch prefixes**: `cms/` for CMS docs, `cloud/` for Cloud docs, `repo/` for everything else' in text, "expected to find: " + '- **Branch prefixes**: `cms/` for CMS docs, `cloud/` for Cloud docs, `repo/` for everything else'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Code examples**: Must be validated against [strapi/strapi](https://github.com/strapi/strapi)' in text, "expected to find: " + '- **Code examples**: Must be validated against [strapi/strapi](https://github.com/strapi/strapi)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is at [docs.strapi.io](https://docs.strapi.io). This repository contains only documentatio' in text, "expected to find: " + 'This is the official Strapi documentation repository, built with Docusaurus 3. The main documentation website is at [docs.strapi.io](https://docs.strapi.io). This repository contains only documentatio'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `yarn llms:generate-and-validate` — Generate and validate LLM code examples (`docusaurus/scripts/generate-llms-code.js --anchors --check-files` → generates `llms-code.txt`)' in text, "expected to find: " + '- `yarn llms:generate-and-validate` — Generate and validate LLM code examples (`docusaurus/scripts/generate-llms-code.js --anchors --check-files` → generates `llms-code.txt`)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- 12 Rules of Technical Writing: `12-rules-of-technical-writing.md` ([external](https://strapi.notion.site/12-Rules-of-Technical-Writing-c75e080e6b19432287b3dd61c2c9fa04))' in text, "expected to find: " + '- 12 Rules of Technical Writing: `12-rules-of-technical-writing.md` ([external](https://strapi.notion.site/12-Rules-of-Technical-Writing-c75e080e6b19432287b3dd61c2c9fa04))'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

