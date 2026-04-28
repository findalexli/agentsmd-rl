"""Behavioral checks for uyuni-expand-githubcopilotinstructionsmd-into-full-cloud (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/uyuni")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| `spacecmd/`, `spacewalk/`, `client/`, `utils/`, `reporting/`, `projects/`, `susemanager-utils/`, `susemanager-sync-data/`, `susemanager-branding-oss/`, `branding/` | Mixed | Supporting packages, cli' in text, "expected to find: " + '| `spacecmd/`, `spacewalk/`, `client/`, `utils/`, `reporting/`, `projects/`, `susemanager-utils/`, `susemanager-sync-data/`, `susemanager-branding-oss/`, `branding/` | Mixed | Supporting packages, cli'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| `java/` | Java 17, Ant + Ivy, Maven (for some modules), Hibernate 7.x, Struts 1.2.9 (legacy), SparkJava (modern) | Main server: `core/`, `webapp/`, `doclets/`. XML-RPC APIs, legacy JSP/Struts UI, mo' in text, "expected to find: " + '| `java/` | Java 17, Ant + Ivy, Maven (for some modules), Hibernate 7.x, Struts 1.2.9 (legacy), SparkJava (modern) | Main server: `core/`, `webapp/`, `doclets/`. XML-RPC APIs, legacy JSP/Struts UI, mo'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '| `web/` | Node 22.x, npm ≥10, React + TypeScript, webpack, Jest, Formik, `node-gettext` | Modern web UI under `web/html/src/`. Incrementally replacing legacy JSP/JS. |' in text, "expected to find: " + '| `web/` | Node 22.x, npm ≥10, React + TypeScript, webpack, Jest, Formik, `node-gettext` | Modern web UI under `web/html/src/`. Incrementally replacing legacy JSP/JS. |'[:80]

