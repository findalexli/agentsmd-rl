"""Behavioral checks for cognithor-docsskills-port-skillmd-improvements-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/cognithor")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/backup/SKILL.md')
    assert 'description: "Automated hourly backup skill that creates timestamped archives of Cognithor config files, skill definitions, and data directories on a cron schedule. Use when setting up automated backu' in text, "expected to find: " + 'description: "Automated hourly backup skill that creates timestamped archives of Cognithor config files, skill definitions, and data directories on a cron schedule. Use when setting up automated backu'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/backup/SKILL.md')
    assert 'Automated backup skill that creates timestamped archives of Cognithor configuration, skills, and data on a cron schedule (`0 * * * *` — hourly by default).' in text, "expected to find: " + 'Automated backup skill that creates timestamped archives of Cognithor configuration, skills, and data on a cron schedule (`0 * * * *` — hourly by default).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/backup/SKILL.md')
    assert '- **Permission denied**: Verify `$BACKUP_DIR` ownership and retry with correct permissions' in text, "expected to find: " + '- **Permission denied**: Verify `$BACKUP_DIR` ownership and retry with correct permissions'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmail_sync/SKILL.md')
    assert 'description: "API integration skill that fetches Gmail messages, syncs inbox labels, and processes attachments via the Gmail REST API. Use when fetching new emails, syncing inbox state, triaging unrea' in text, "expected to find: " + 'description: "API integration skill that fetches Gmail messages, syncs inbox labels, and processes attachments via the Gmail REST API. Use when fetching new emails, syncing inbox state, triaging unrea'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmail_sync/SKILL.md')
    assert 'Fetches Gmail messages, syncs labels, and processes attachments via the Gmail REST API using `httpx`. Requires network access.' in text, "expected to find: " + 'Fetches Gmail messages, syncs labels, and processes attachments via the Gmail REST API using `httpx`. Requires network access.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/gmail_sync/SKILL.md')
    assert '- **Empty response**: Confirm query parameters are correct; check `last_sync_epoch` is valid' in text, "expected to find: " + '- **Empty response**: Confirm query parameters are correct; check `last_sync_epoch` is valid'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test/SKILL.md')
    assert 'description: "Diagnostic smoke-test skill that validates Cognithor\'s skill loading, SkillRegistry registration, and Planner-Gatekeeper-Executor pipeline. Use when running a framework health check, ver' in text, "expected to find: " + 'description: "Diagnostic smoke-test skill that validates Cognithor\'s skill loading, SkillRegistry registration, and Planner-Gatekeeper-Executor pipeline. Use when running a framework health check, ver'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test/SKILL.md')
    assert 'Diagnostic smoke-test that sends a probe through the full Planner → Gatekeeper → Executor pipeline and returns a status response.' in text, "expected to find: " + 'Diagnostic smoke-test that sends a probe through the full Planner → Gatekeeper → Executor pipeline and returns a status response.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test/SKILL.md')
    assert 'This is a diagnostic-only skill — the `"result": "TODO"` placeholder confirms the pipeline works without performing real work.' in text, "expected to find: " + 'This is a diagnostic-only skill — the `"result": "TODO"` placeholder confirms the pipeline works without performing real work.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test_skill/SKILL.md')
    assert 'description: "Extended diagnostic skill that validates the full Cognithor skill lifecycle — SkillRegistry scanning, keyword matching (exact + fuzzy at 70% threshold), and async execution. Use when tes' in text, "expected to find: " + 'description: "Extended diagnostic skill that validates the full Cognithor skill lifecycle — SkillRegistry scanning, keyword matching (exact + fuzzy at 70% threshold), and async execution. Use when tes'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test_skill/SKILL.md')
    assert '3. **Check keyword matching** — the SkillRegistry uses exact match (case-insensitive) then fuzzy match (70% threshold). Verify the input routes to this skill, not the sibling `test` skill' in text, "expected to find: " + '3. **Check keyword matching** — the SkillRegistry uses exact match (case-insensitive) then fuzzy match (70% threshold). Verify the input routes to this skill, not the sibling `test` skill'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/test_skill/SKILL.md')
    assert 'Diagnostic-only skill — `"result": "TODO"` is intentional. Differs from `test` by validating keyword disambiguation and the full scan-to-execute lifecycle.' in text, "expected to find: " + 'Diagnostic-only skill — `"result": "TODO"` is intentional. Differs from `test` by validating keyword disambiguation and the full scan-to-execute lifecycle.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wetter_abfrage/SKILL.md')
    assert 'description: "Weather query skill that retrieves current temperature, humidity, wind speed, and multi-day forecasts for a given city or coordinate. Use when checking the weather, getting a forecast, l' in text, "expected to find: " + 'description: "Weather query skill that retrieves current temperature, humidity, wind speed, and multi-day forecasts for a given city or coordinate. Use when checking the weather, getting a forecast, l'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wetter_abfrage/SKILL.md')
    assert 'Retrieves current weather conditions (temperature, humidity, wind speed, conditions) and multi-day forecasts for a user-specified location.' in text, "expected to find: " + 'Retrieves current weather conditions (temperature, humidity, wind speed, conditions) and multi-day forecasts for a user-specified location.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/wetter_abfrage/SKILL.md')
    assert '| API timeout | Network issue or rate limit | Retry once after 2s; report failure if persistent |' in text, "expected to find: " + '| API timeout | Network issue or rate limit | Retry once after 2s; report failure if persistent |'[:80]

