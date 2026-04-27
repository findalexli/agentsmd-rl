"""Behavioral checks for claude-code-templates-featcfcrawl-add-modifiedsince-support- (markdown_authoring task).

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
    text = _read('cli-tool/components/skills/utilities/cf-crawl/SKILL.md')
    assert 'Only crawls pages modified since the given date. Skipped pages appear with `status=skipped` in results. This is ideal for daily doc-syncing: do one full crawl, then incremental updates to see only wha' in text, "expected to find: " + 'Only crawls pages modified since the given date. Skipped pages appear with `status=skipped` in results. This is ideal for daily doc-syncing: do one full crawl, then incremental updates to see only wha'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/utilities/cf-crawl/SKILL.md')
    assert '- `--since DATE`: only crawl pages modified since DATE (ISO date like `2026-03-10` or Unix timestamp). Converts to Unix timestamp for the `modifiedSince` API parameter' in text, "expected to find: " + '- `--since DATE`: only crawl pages modified since DATE (ISO date like `2026-03-10` or Unix timestamp). Converts to Unix timestamp for the `modifiedSince` API parameter'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('cli-tool/components/skills/utilities/cf-crawl/SKILL.md')
    assert 'curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl/<JOB_ID>?status=skipped&limit=50" \\' in text, "expected to find: " + 'curl -s -X GET "https://api.cloudflare.com/client/v4/accounts/${CLOUDFLARE_ACCOUNT_ID}/browser-rendering/crawl/<JOB_ID>?status=skipped&limit=50" \\'[:80]

