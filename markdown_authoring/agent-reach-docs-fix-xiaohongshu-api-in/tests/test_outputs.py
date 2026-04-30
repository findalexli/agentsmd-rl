"""Behavioral checks for agent-reach-docs-fix-xiaohongshu-api-in (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/agent-reach")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'mcporter call \'xiaohongshu.publish_with_video(title: "标题", content: "正文", video: "/path/to/video.mp4", tags: ["vlog"])\'' in text, "expected to find: " + 'mcporter call \'xiaohongshu.publish_with_video(title: "标题", content: "正文", video: "/path/to/video.mp4", tags: ["vlog"])\''[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'mcporter call \'xiaohongshu.publish_content(title: "标题", content: "正文", images: ["/path/to/img.jpg"], tags: ["美食"])\'' in text, "expected to find: " + 'mcporter call \'xiaohongshu.publish_content(title: "标题", content: "正文", images: ["/path/to/img.jpg"], tags: ["美食"])\''[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('agent_reach/skill/SKILL.md')
    assert 'mcporter call \'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy", load_all_comments: true)\'' in text, "expected to find: " + 'mcporter call \'xiaohongshu.get_feed_detail(feed_id: "xxx", xsec_token: "yyy", load_all_comments: true)\''[:80]

