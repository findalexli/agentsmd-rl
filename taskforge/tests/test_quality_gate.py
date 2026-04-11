"""Tests for quality_gate: fast classification + Gemini structured output."""

import json
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

import yaml

from taskforge.quality_gate import (
    classify_task_fast,
    classify_task,
    QualityResult,
    QUALITY_SCHEMA,
)


class TestQualitySchema(unittest.TestCase):
    """Verify schema structure."""

    def test_has_meta_referential_field(self):
        props = QUALITY_SCHEMA["properties"]
        assert "meta_referential" in props
        assert props["meta_referential"]["type"] == "boolean"

    def test_has_competing_principles_field(self):
        props = QUALITY_SCHEMA["properties"]
        assert "competing_principles" in props
        assert props["competing_principles"]["type"] == "boolean"

    def test_reasoning_before_verdict_in_ordering(self):
        order = QUALITY_SCHEMA["propertyOrdering"]
        assert order.index("reasoning") < order.index("verdict")

    def test_meta_before_verdict(self):
        order = QUALITY_SCHEMA["propertyOrdering"]
        assert order.index("meta_referential") < order.index("verdict")


class TestClassifyFast(unittest.TestCase):

    def setUp(self):
        self.task_dir = Path("/tmp/test_quality_gate")
        self.task_dir.mkdir(parents=True, exist_ok=True)

    def _write_manifest(self, data):
        (self.task_dir / "eval_manifest.yaml").write_text(yaml.dump(data))

    def test_no_manifest_is_delete(self):
        empty = Path("/tmp/test_qg_empty")
        empty.mkdir(parents=True, exist_ok=True)
        r = classify_task_fast(empty)
        assert r.verdict == "DELETE"
        assert "no_manifest" in r.flags

    def test_no_config_signal_is_delete(self):
        self._write_manifest({
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "checks": [{"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"}],
        })
        r = classify_task_fast(self.task_dir)
        assert r.verdict == "DELETE"

    def test_tier2_only_flagged(self):
        self._write_manifest({
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "checks": [{"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"}],
            "config_edits": [{"path": "README.md", "tier": 2, "gold_added": "stuff"}],
            "rubric": [{"rule": "test rule"}],
        })
        r = classify_task_fast(self.task_dir)
        assert "tier2_only" in r.flags
        assert r.has_tier1 is False
        assert r.verdict == ""  # needs Gemini

    def test_tier1_not_flagged(self):
        self._write_manifest({
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "checks": [{"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"}],
            "config_edits": [{"path": "AGENTS.md", "tier": 1, "gold_added": "stuff"}],
            "rubric": [{"rule": "test rule"}],
        })
        r = classify_task_fast(self.task_dir)
        assert "tier2_only" not in r.flags
        assert r.has_tier1 is True

    def test_rich_task_needs_gemini(self):
        self._write_manifest({
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "checks": [
                {"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
                {"id": "y", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
            ],
            "config_edits": [{"path": "AGENTS.md", "tier": 1, "gold_added": "stuff"}],
            "rubric": [{"rule": "test rule"}],
            "distractors": [{"rule": "dist", "collision_type": "scope_ambiguity"}],
        })
        r = classify_task_fast(self.task_dir)
        assert r.verdict == ""  # needs Gemini
        assert r.rubric_count == 1
        assert r.distractor_count == 1
        assert r.f2p_count == 2

    def test_agent_config_check_prevents_delete(self):
        """Tasks with agent_config origin checks should not auto-DELETE."""
        self._write_manifest({
            "version": "2.0",
            "source": {"repo": "test/repo", "pr": 1, "base_commit": "abc"},
            "checks": [
                {"id": "x", "type": "fail_to_pass", "origin": "agent_config",
                 "description": "d", "source": {"path": "AGENTS.md", "lines": "1"}},
            ],
        })
        r = classify_task_fast(self.task_dir)
        assert r.verdict != "DELETE"


class TestClassifyWithGemini(unittest.TestCase):

    @patch("taskforge.quality_gate.call_gemini")
    def test_high_verdict_passes_through(self, mock_gemini):
        task_dir = Path("/tmp/test_qg_gemini")
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "instruction.md").write_text("Fix the bug")
        (task_dir / "solution").mkdir(exist_ok=True)
        (task_dir / "solution" / "solve.sh").write_text("git apply p")
        yaml.dump({
            "version": "2.0",
            "source": {"repo": "t/r", "pr": 1, "base_commit": "a"},
            "checks": [{"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"}],
            "config_edits": [{"path": "AGENTS.md", "tier": 1}],
            "rubric": [{"rule": "R"}],
        }, open(task_dir / "eval_manifest.yaml", "w"))

        mock_gemini.return_value = {
            "config_navigation": "deep_hierarchy",
            "config_edit_organic": True,
            "meta_referential": True,
            "competing_principles": True,
            "task_type": "bugfix_plus_config",
            "reasoning": "Agent must navigate hierarchy",
            "verdict": "HIGH",
        }

        r = classify_task(task_dir, "fake-key")
        assert r.verdict == "HIGH"
        assert r.config_navigation == "deep_hierarchy"
        assert r.config_edit_organic is True

    @patch("taskforge.quality_gate.call_gemini")
    def test_meta_referential_boost_from_medium(self, mock_gemini):
        """MEDIUM tasks with meta+competing+organic get boosted to HIGH."""
        task_dir = Path("/tmp/test_qg_boost")
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "instruction.md").write_text("Rewrite AGENTS.md")
        (task_dir / "solution").mkdir(exist_ok=True)
        (task_dir / "solution" / "solve.sh").write_text("git apply p")
        yaml.dump({
            "version": "2.0",
            "source": {"repo": "t/r", "pr": 1, "base_commit": "a"},
            "checks": [
                {"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
                {"id": "y", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
                {"id": "z", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
            ],
            "config_edits": [{"path": "AGENTS.md", "tier": 1}],
            "rubric": [{"rule": "R"}],
        }, open(task_dir / "eval_manifest.yaml", "w"))

        mock_gemini.return_value = {
            "config_navigation": "flat_single_file",
            "config_edit_organic": True,
            "meta_referential": True,
            "competing_principles": True,
            "task_type": "feature_plus_config",
            "reasoning": "Agent must rewrite its own instructions",
            "verdict": "MEDIUM",
        }

        r = classify_task(task_dir, "fake-key")
        assert r.verdict == "HIGH"  # boosted from MEDIUM
        assert "boosted:MEDIUM→HIGH" in r.flags

    @patch("taskforge.quality_gate.call_gemini")
    def test_no_boost_without_tests(self, mock_gemini):
        """Meta-referential but trivial code (<=2 f2p) doesn't get boosted."""
        task_dir = Path("/tmp/test_qg_noboost")
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "instruction.md").write_text("Update docs")
        (task_dir / "solution").mkdir(exist_ok=True)
        (task_dir / "solution" / "solve.sh").write_text("echo")
        yaml.dump({
            "version": "2.0",
            "source": {"repo": "t/r", "pr": 1, "base_commit": "a"},
            "checks": [
                {"id": "x", "type": "fail_to_pass", "origin": "pr_diff", "description": "d"},
            ],
            "config_edits": [{"path": "AGENTS.md", "tier": 1}],
            "rubric": [{"rule": "R"}],
        }, open(task_dir / "eval_manifest.yaml", "w"))

        mock_gemini.return_value = {
            "config_navigation": "flat_single_file",
            "config_edit_organic": True,
            "meta_referential": True,
            "competing_principles": False,
            "task_type": "docs_only",
            "reasoning": "Mostly docs",
            "verdict": "LOW",
        }

        r = classify_task(task_dir, "fake-key")
        assert r.verdict == "LOW"  # NOT boosted (only 1 f2p)


if __name__ == "__main__":
    unittest.main()
