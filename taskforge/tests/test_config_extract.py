"""Unit tests for config_extract.py."""
import json
import tempfile
from pathlib import Path

import pytest

from taskforge.config_extract import (
    extract_gold_config,
    compare_config_changes,
    stamp_manifest,
    _parse_patches_from_solve,
    _parse_sed_commands,
    _parse_heredoc_writes,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
def task_dir(tmp_path):
    """Create a minimal task directory."""
    (tmp_path / "solution").mkdir()
    (tmp_path / "environment").mkdir()
    return tmp_path


def write_solve(task_dir, content):
    (task_dir / "solution" / "solve.sh").write_text(content)


def write_manifest(task_dir, content):
    (task_dir / "eval_manifest.yaml").write_text(content)


# ── _parse_patches_from_solve ─────────────────────────────────────────────

class TestParsePatchesFromSolve:
    def test_extracts_config_file_from_git_apply(self):
        solve = """
git apply --whitespace=fix - <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
index abc..def 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1,3 +1,5 @@
 # Agents
+
+## New Section
+New content here
PATCH
"""
        result = _parse_patches_from_solve(solve)
        assert "AGENTS.md" in result
        assert "New Section" in result["AGENTS.md"]["added"]

    def test_ignores_code_files_in_patch(self):
        solve = """
git apply - <<'PATCH'
diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1 +1 @@
-old
+new
PATCH
"""
        result = _parse_patches_from_solve(solve)
        assert len(result) == 0  # main.py is not a config file

    def test_extracts_both_added_and_removed(self):
        solve = """
git apply - <<'EOF'
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -1,3 +1,3 @@
 # Contributing
-Old text
+New text
EOF
"""
        result = _parse_patches_from_solve(solve)
        assert "CONTRIBUTING.md" in result
        assert "New text" in result["CONTRIBUTING.md"]["added"]
        assert "Old text" in result["CONTRIBUTING.md"]["removed"]


# ── _parse_sed_commands ──────────────────────────────────────────────────

class TestParseSedCommands:
    def test_extracts_append_to_md_file(self):
        solve = "sed -i '/^OLD_VAR$/a\\NEW_VAR' .opencode/agent/translator.md"
        result = _parse_sed_commands(solve)
        assert ".opencode/agent/translator.md" in result
        assert "NEW_VAR" in result[".opencode/agent/translator.md"]["added"]

    def test_extracts_substitution(self):
        solve = "sed -i 's/old text/new text/' CLAUDE.md"
        result = _parse_sed_commands(solve)
        assert "CLAUDE.md" in result

    def test_cleans_workspace_prefix(self):
        solve = "sed -i '/pattern/a\\new line' /workspace/myrepo/AGENTS.md"
        result = _parse_sed_commands(solve)
        assert "AGENTS.md" in result

    def test_ignores_non_md_files(self):
        solve = "sed -i 's/old/new/' src/main.py"
        result = _parse_sed_commands(solve)
        assert len(result) == 0


# ── _parse_heredoc_writes ────────────────────────────────────────────────

class TestParseHeredocWrites:
    def test_extracts_cat_heredoc(self):
        solve = """cat >> CLAUDE.md << 'EOF'
## New Section
Content here
EOF
"""
        result = _parse_heredoc_writes(solve)
        assert "CLAUDE.md" in result
        assert "New Section" in result["CLAUDE.md"]["added"]

    def test_extracts_echo_append(self):
        solve = 'echo "## Build" >> README.md'
        result = _parse_heredoc_writes(solve)
        assert "README.md" in result


# ── extract_gold_config ──────────────────────────────────────────────────

class TestExtractGoldConfig:
    def test_no_solve_sh(self, task_dir):
        result = extract_gold_config(task_dir)
        assert result.get("error") == "no solve.sh"

    def test_no_config_changes(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i 's/old/new/' src/main.py")
        result = extract_gold_config(task_dir)
        assert result["files"] == {}

    def test_extracts_from_sed(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i '/pattern/a\\new rule' AGENTS.md")
        result = extract_gold_config(task_dir)
        assert "AGENTS.md" in result["files"]
        assert result["tier1_count"] == 1

    def test_extracts_from_patch(self, task_dir):
        write_solve(task_dir, """#!/bin/bash
git apply - <<'PATCH'
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -1 +1,2 @@
 # Title
+New doc section
PATCH
""")
        result = extract_gold_config(task_dir)
        assert "README.md" in result["files"]
        assert result["tier2_count"] == 1


# ── stamp_manifest ───────────────────────────────────────────────────────

class TestStampManifest:
    def test_stamps_config_edits(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i '/x/a\\new' AGENTS.md")
        write_manifest(task_dir, "version: '2.0'\nchecks: []\nrubric: []")
        n = stamp_manifest(task_dir)
        assert n == 1

        import yaml
        m = yaml.safe_load((task_dir / "eval_manifest.yaml").read_text())
        assert len(m["config_edits"]) == 1
        assert m["config_edits"][0]["path"] == "AGENTS.md"
        assert m["config_edits"][0]["tier"] == 1

    def test_preserves_existing_manifest_data(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i '/x/a\\new' AGENTS.md")
        write_manifest(task_dir, "version: '2.0'\nchecks:\n  - id: test1\n    type: fail_to_pass\n    origin: pr_diff\n    description: test\nrubric: []")
        stamp_manifest(task_dir)

        import yaml
        m = yaml.safe_load((task_dir / "eval_manifest.yaml").read_text())
        assert len(m["checks"]) == 1  # preserved
        assert "config_edits" in m  # added

    def test_handles_empty_manifest(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i '/x/a\\new' AGENTS.md")
        write_manifest(task_dir, "")
        n = stamp_manifest(task_dir)
        assert n == 1

    def test_returns_zero_when_no_config_edits(self, task_dir):
        write_solve(task_dir, "#!/bin/bash\nsed -i 's/old/new/' src/main.py")
        write_manifest(task_dir, "version: '2.0'\nchecks: []")
        n = stamp_manifest(task_dir)
        assert n == 0


# ── compare_config_changes ───────────────────────────────────────────────

class TestCompareConfigChanges:
    def test_matches_modified_file(self):
        gold = {"files": {"AGENTS.md": {"added": "new rule"}}}
        agent_diff = """diff --git a/AGENTS.md b/AGENTS.md
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -1 +1,2 @@
 # Agents
+new rule from agent"""
        result = compare_config_changes(gold, agent_diff)
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["file_modified"] is True

    def test_detects_unmodified_file(self):
        gold = {"files": {"AGENTS.md": {"added": "new rule"}}}
        agent_diff = """diff --git a/src/main.py b/src/main.py
--- a/src/main.py
+++ b/src/main.py
@@ -1 +1 @@
-old
+new"""
        result = compare_config_changes(gold, agent_diff)
        assert len(result["comparisons"]) == 1
        assert result["comparisons"][0]["file_modified"] is False
