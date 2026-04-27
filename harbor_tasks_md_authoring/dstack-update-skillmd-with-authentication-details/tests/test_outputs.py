"""Behavioral checks for dstack-update-skillmd-with-authentication-details (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dstack")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '- OpenAI-compatible models: Use `service.url` from `dstack run get <run-name> --json` and append `/v1` as the base URL; do **not** use deprecated `service.model.base_url` for requests.' in text, "expected to find: " + '- OpenAI-compatible models: Use `service.url` from `dstack run get <run-name> --json` and append `/v1` as the base URL; do **not** use deprecated `service.model.base_url` for requests.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '- Authentication: Unless `auth` is `false`, include `Authorization: Bearer <DSTACK_TOKEN>` on all service requests.' in text, "expected to find: " + '- Authentication: Unless `auth` is `false`, include `Authorization: Bearer <DSTACK_TOKEN>` on all service requests.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dstack/SKILL.md')
    assert '-d \'{"model":"<model name>","messages":[{"role":"user","content":"Hello"}],"max_tokens":64}\'' in text, "expected to find: " + '-d \'{"model":"<model name>","messages":[{"role":"user","content":"Hello"}],"max_tokens":64}\''[:80]

