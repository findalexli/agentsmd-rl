"""Behavioral checks for pup-fixskills-align-datadog-skills-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pup")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-code-generation/SKILL.md')
    assert 'pup monitors list --tags="env:production" --output=table' in text, "expected to find: " + 'pup monitors list --tags="env:production" --output=table'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-code-generation/SKILL.md')
    assert 'pup monitors list --tags="team:backend"' in text, "expected to find: " + 'pup monitors list --tags="team:backend"'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-code-generation/SKILL.md')
    assert 'pup monitors list --tags="env:prod"' in text, "expected to find: " + 'pup monitors list --tags="env:prod"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-logs/SKILL.md')
    assert 'pup logs search --query="*" --from="1h" | jq \'group_by(.service) | map({service: .[0].service, count: length}) | sort_by(-.count)[:10]\'' in text, "expected to find: " + 'pup logs search --query="*" --from="1h" | jq \'group_by(.service) | map({service: .[0].service, count: length}) | sort_by(-.count)[:10]\''[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-logs/SKILL.md')
    assert 'pup logs search --query="@http.status_code:>=500" --from="1h"' in text, "expected to find: " + 'pup logs search --query="@http.status_code:>=500" --from="1h"'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-logs/SKILL.md')
    assert 'pup obs-pipelines create --file pipeline.json' in text, "expected to find: " + 'pup obs-pipelines create --file pipeline.json'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-monitors/SKILL.md')
    assert "pup monitors list | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, name, status: .overall_state}'" in text, "expected to find: " + "pup monitors list | jq 'sort_by(.overall_state_modified) | .[:10] | .[] | {id, name, status: .overall_state}'"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-monitors/SKILL.md')
    assert 'pup monitors list | jq \'.[] | select(.tags | contains(["team:"]) | not) | {id, name}\'' in text, "expected to find: " + 'pup monitors list | jq \'.[] | select(.tags | contains(["team:"]) | not) | {id, name}\''[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-monitors/SKILL.md')
    assert 'pup monitors update 12345 --file monitor-muted-until.json' in text, "expected to find: " + 'pup monitors update 12345 --file monitor-muted-until.json'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-pup/SKILL.md')
    assert '| Security signals | `pup security signals list --query "*" --from 24h` |' in text, "expected to find: " + '| Security signals | `pup security signals list --query "*" --from 24h` |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-pup/SKILL.md')
    assert 'pup security signals list --query "*" --from 24h' in text, "expected to find: " + 'pup security signals list --query "*" --from 24h'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dd-pup/SKILL.md')
    assert 'pup infrastructure hosts list --count 100' in text, "expected to find: " + 'pup infrastructure hosts list --count 100'[:80]

