"""
Structural checks for the bonk agent instruction file.

This is a markdown_authoring task. The primary evaluation signal is Track 2
(Gemini semantic-diff of config_edits). These tests provide a sanity gate
(Track 1) ensuring distinctive signal markers from the gold markdown diff
are present in the authored file.
"""
import os
import subprocess

REPO = "/workspace/workers-sdk"
BONK_MD = os.path.join(REPO, ".opencode", "agents", "bonk.md")


def test_file_exists():
    """The agent instruction file exists at the expected path."""
    assert os.path.isfile(BONK_MD), f"{BONK_MD} not found"


def test_triggering_comment_rule():
    """The new 'Triggering comment is the task' rule is present."""
    r = subprocess.run(
        ["grep", "-qF", "**Triggering comment is the task:**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'Triggering comment is the task' rule"


def test_no_re_reviewing_rule():
    """The new 'No re-reviewing on fixup requests' rule is present."""
    r = subprocess.run(
        ["grep", "-qF", "**No re-reviewing on fixup requests:**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'No re-reviewing on fixup requests' rule"


def test_start_from_triggering_comment_step():
    """The implementation workflow starts from the triggering comment."""
    r = subprocess.run(
        ["grep", "-qF", "**Start from the triggering comment.**", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing 'Start from the triggering comment' step"


def test_negative_examples_plural():
    """The examples section uses plural 'Negative examples' heading."""
    r = subprocess.run(
        ["grep", "-qF", "Negative examples:", BONK_MD],
        capture_output=True,
    )
    assert r.returncode == 0, "Missing plural 'Negative examples:' heading"

