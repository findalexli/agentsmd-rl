"""Behavioral checks for airflow-fix-spdx-license-for-skillmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/airflow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/airflow-translations/SKILL.md')
    assert 'https://www.apache.org/licenses/LICENSE-2.0 -->' in text, "expected to find: " + 'https://www.apache.org/licenses/LICENSE-2.0 -->'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/airflow-translations/SKILL.md')
    assert '<!-- SPDX-License-Identifier: Apache-2.0' in text, "expected to find: " + '<!-- SPDX-License-Identifier: Apache-2.0'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/airflow-translations/locales/zh-CN.md')
    assert 'https://www.apache.org/licenses/LICENSE-2.0 -->' in text, "expected to find: " + 'https://www.apache.org/licenses/LICENSE-2.0 -->'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/skills/airflow-translations/locales/zh-CN.md')
    assert '<!-- SPDX-License-Identifier: Apache-2.0' in text, "expected to find: " + '<!-- SPDX-License-Identifier: Apache-2.0'[:80]

