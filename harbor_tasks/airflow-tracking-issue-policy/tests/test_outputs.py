"""Tests for AGENTS.md tracking-issue policy task.

This is a markdown_authoring task. Behaviour we validate is the *presence*
in AGENTS.md of three signals that any reasonable implementation of the
required policy must contain. Track 2 (LLM judge) handles semantic
quality; this file is the structural sanity oracle.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/airflow")
AGENTS = REPO / "AGENTS.md"


def _read_agents() -> str:
    assert AGENTS.is_file(), f"{AGENTS} missing"
    return AGENTS.read_text(encoding="utf-8")


def test_agents_md_preserved():
    """pass_to_pass: AGENTS.md still exists with its original top-level heading."""
    r = subprocess.run(
        ["grep", "-c", "^# AGENTS instructions$", str(AGENTS)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"grep failed: {r.stderr}"
    count = int(r.stdout.strip())
    assert count == 1, f"expected exactly 1 '# AGENTS instructions' top heading, found {count}"


def test_tracking_issue_section_heading():
    """fail_to_pass: AGENTS.md contains a new section about tracking issues for deferred work."""
    r = subprocess.run(
        ["grep", "-Ein", r"^#{2,4}\s+.*Tracking issues", str(AGENTS)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "Expected a markdown heading mentioning 'Tracking issues' "
        f"in AGENTS.md; grep stdout={r.stdout!r} stderr={r.stderr!r}"
    )


def test_full_issue_url_example_present():
    """fail_to_pass: a full GitHub issue URL example for apache/airflow appears in AGENTS.md."""
    r = subprocess.run(
        [
            "grep",
            "-Ein",
            r"https://github\.com/apache/airflow/issues/[0-9]+",
            str(AGENTS),
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        "Expected a full https://github.com/apache/airflow/issues/<N> URL "
        f"as an example in AGENTS.md; got stdout={r.stdout!r}"
    )


def test_forward_looking_phrase_called_out():
    """fail_to_pass: the negative example phrase 'will open a tracking issue' is mentioned."""
    text = _read_agents()
    # The phrase may wrap across lines / quotation marks, so allow any whitespace
    # (including newline + leading indent in fenced or wrapped prose).
    pattern = re.compile(r"will\s+open\s+a\s+tracking\s+issue", re.IGNORECASE)
    assert pattern.search(text), (
        "Expected the negative example phrase 'will open a tracking issue' "
        "to be cited in AGENTS.md as language to avoid."
    )


def test_signals_appear_in_one_section():
    """fail_to_pass: heading, URL example, and negative phrase appear within a single
    contiguous section (guards against keyword stuffing in unrelated parts of the file)."""
    text = _read_agents()
    # Split on markdown level-2 headings ("## ").
    parts = re.split(r"(?m)^##\s", text)
    matches = []
    for part in parts:
        has_heading = re.search(r"(?im)^#{2,4}\s+.*Tracking issues", part) is not None
        has_url = (
            re.search(
                r"https://github\.com/apache/airflow/issues/[0-9]+", part
            )
            is not None
        )
        has_neg = (
            re.search(r"(?i)will\s+open\s+a\s+tracking\s+issue", part) is not None
        )
        if has_heading and has_url and has_neg:
            matches.append(part[:80])
    assert matches, (
        "Expected the tracking-issue section heading, a full issue URL example, "
        "and the negative phrase 'will open a tracking issue' to all appear "
        "within a single contiguous section of AGENTS.md."
    )
