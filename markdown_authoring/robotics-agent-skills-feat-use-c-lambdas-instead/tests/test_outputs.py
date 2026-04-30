"""Behavioral checks for robotics-agent-skills-feat-use-c-lambdas-instead (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/robotics-agent-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ros2/SKILL.md')
    assert '"camera/image_raw", sensor_qos, [this](const std::shared_ptr<const sensor_msgs::msg::Image>& msg){' in text, "expected to find: " + '"camera/image_raw", sensor_qos, [this](const std::shared_ptr<const sensor_msgs::msg::Image>& msg){'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ros2/SKILL.md')
    assert 'det_pub_ = this->create_publisher<vision_msgs::msg::Detection2D>("detections", reliable_qos);' in text, "expected to find: " + 'det_pub_ = this->create_publisher<vision_msgs::msg::Detection2D>("detections", reliable_qos);'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/ros2/SKILL.md')
    assert 'void image_callback(const std::shared_ptr<const sensor_msgs::msg::Image>& msg) {' in text, "expected to find: " + 'void image_callback(const std::shared_ptr<const sensor_msgs::msg::Image>& msg) {'[:80]

