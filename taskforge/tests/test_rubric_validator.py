"""Unit tests for rubric_validator.py."""
import json
from pathlib import Path

import pytest
import yaml

from taskforge.rubric_validator import (
    find_config_files,
    extract_context,
    load_rubric,
    phase1_check,
    validate,
    _get_precision,
)


@pytest.fixture
def repo_dir(tmp_path):
    """Create a mock repo with config files."""
    (tmp_path / "AGENTS.md").write_text(
        "# Agents\n\n## Style\n\n"
        "- Prefer single-word names\n"
        "- Avoid try/catch\n"
        "- Use const over let\n"
        "\n## Build\n\npnpm build\n"
    )
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "CLAUDE.md").write_text("# Claude\nLocal rules here\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')\n")
    return tmp_path


@pytest.fixture
def task_dir(tmp_path):
    """Create a mock task directory."""
    task = tmp_path / "task"
    task.mkdir()
    (task / "solution").mkdir()
    (task / "solution" / "solve.sh").write_text("#!/bin/bash\necho 'fix'\n")
    (task / "instruction.md").write_text("Fix the bug.\n")
    return task


# ── find_config_files ────────────────────────────────────────────────────

class TestFindConfigFiles:
    def test_finds_agents_md(self, repo_dir):
        configs = find_config_files(repo_dir)
        paths = [c["path"] for c in configs]
        assert "AGENTS.md" in paths

    def test_finds_claude_md_in_subdirectory(self, repo_dir):
        configs = find_config_files(repo_dir)
        paths = [c["path"] for c in configs]
        assert ".claude/CLAUDE.md" in paths

    def test_skips_node_modules(self, repo_dir):
        nm = repo_dir / "node_modules" / "pkg"
        nm.mkdir(parents=True)
        (nm / "AGENTS.md").write_text("should be skipped")
        configs = find_config_files(repo_dir)
        paths = [c["path"] for c in configs]
        assert not any("node_modules" in p for p in paths)

    def test_includes_preview(self, repo_dir):
        configs = find_config_files(repo_dir)
        agents = next(c for c in configs if c["path"] == "AGENTS.md")
        assert "# Agents" in agents["preview"]

    def test_empty_repo(self, tmp_path):
        configs = find_config_files(tmp_path)
        assert configs == []


# ── extract_context ──────────────────────────────────────────────────────

class TestExtractContext:
    def test_file_exists_with_lines(self, repo_dir):
        result = extract_context(repo_dir, "AGENTS.md", "5")
        assert result["exists"] is True
        assert "Prefer single-word names" in result["cited_text"]

    def test_file_exists_no_lines(self, repo_dir):
        result = extract_context(repo_dir, "AGENTS.md", "")
        assert result["exists"] is True
        assert result["snippet"]  # returns first 100 lines

    def test_file_missing(self, repo_dir):
        result = extract_context(repo_dir, "NONEXISTENT.md", "1")
        assert result["exists"] is False

    def test_line_out_of_range(self, repo_dir):
        result = extract_context(repo_dir, "AGENTS.md", "999")
        assert result["exists"] is True
        assert "out of range" in result["snippet"]

    def test_line_range(self, repo_dir):
        result = extract_context(repo_dir, "AGENTS.md", "5-7")
        assert result["exists"] is True
        assert result["cited_text"]  # should have content

    def test_padding(self, repo_dir):
        result = extract_context(repo_dir, "AGENTS.md", "5", padding=2)
        lines = result["snippet"].split("\n")
        # Should have ~5 lines (line 3-7 with padding 2 around line 5)
        assert len(lines) >= 3


# ── load_rubric ──────────────────────────────────────────────────────────

class TestLoadRubric:
    def test_loads_rules(self, task_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "version": "2.0",
            "rubric": [
                {"rule": "Use single words", "source": {"path": "AGENTS.md", "lines": "5"}},
                {"rule": "Avoid try/catch"},
            ]
        }))
        rules = load_rubric(task_dir)
        assert len(rules) == 2
        assert rules[0]["path"] == "AGENTS.md"
        assert rules[0]["lines"] == "5"

    def test_empty_rubric(self, task_dir):
        (task_dir / "eval_manifest.yaml").write_text("version: '2.0'\nrubric: []\n")
        rules = load_rubric(task_dir)
        assert rules == []

    def test_no_manifest(self, task_dir):
        rules = load_rubric(task_dir)
        assert rules == []

    def test_string_rules(self, task_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": ["rule one", "rule two"]
        }))
        rules = load_rubric(task_dir)
        assert len(rules) == 2
        assert rules[0]["rule"] == "rule one"
        assert rules[0]["path"] == ""


# ── phase1_check ─────────────────────────────────────────────────────────

class TestPhase1Check:
    def test_detects_existing_file(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": [{"rule": "test", "source": {"path": "AGENTS.md", "lines": "5"}}]
        }))
        context = phase1_check(task_dir, repo_dir)
        assert len(context["config_inventory"]) >= 1
        assert context["rule_checks"][0]["file_exists"] is True
        assert context["rule_checks"][0]["p1_verdict"] == "needs_semantic_check"

    def test_detects_missing_file(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": [{"rule": "test", "source": {"path": "NONEXISTENT.md", "lines": "1"}}]
        }))
        context = phase1_check(task_dir, repo_dir)
        assert context["rule_checks"][0]["file_exists"] is False
        assert context["rule_checks"][0]["p1_verdict"] == "file_missing"

    def test_detects_no_source(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": [{"rule": "generic rule"}]
        }))
        context = phase1_check(task_dir, repo_dir)
        assert context["rule_checks"][0]["p1_verdict"] == "no_source_cited"


# ── _get_precision ───────────────────────────────────────────────────────

class TestGetPrecision:
    def test_returns_score(self):
        assert _get_precision({"precision_score": 0.75}) == 0.75

    def test_handles_zero(self):
        assert _get_precision({"precision_score": 0.0}) == 0.0

    def test_falls_back_to_overall(self):
        assert _get_precision({"overall_precision": 0.5}) == 0.5

    def test_prefers_precision_score(self):
        assert _get_precision({"precision_score": 0.8, "overall_precision": 0.5}) == 0.8

    def test_zero_precision_not_falsy(self):
        assert _get_precision({"precision_score": 0.0, "overall_precision": 0.8}) == 0.0

    def test_defaults_to_zero(self):
        assert _get_precision({}) == 0.0


# ── validate ─────────────────────────────────────────────────────────────

class TestValidate:
    def test_no_rules_returns_clean(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text("version: '2.0'\nrubric: []\n")
        result = validate(task_dir, repo_dir)
        assert result["status"] == "no_rules"
        assert result["precision_score"] == 1.0

    def test_context_only_mode(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": [{"rule": "test", "source": {"path": "AGENTS.md", "lines": "5"}}]
        }))
        result = validate(task_dir, repo_dir, context_only=True)
        assert result["status"] == "context_only"
        assert "config_files" in result
        assert len(result["phase1"]) == 1

    def test_no_gemini_key(self, task_dir, repo_dir):
        (task_dir / "eval_manifest.yaml").write_text(yaml.dump({
            "rubric": [{"rule": "test", "source": {"path": "AGENTS.md", "lines": "5"}}]
        }))
        result = validate(task_dir, repo_dir, gemini_key="")
        assert result["status"] == "no_gemini_key"
        assert result["precision_score"] == 0.0
