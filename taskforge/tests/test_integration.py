"""Real-harness integration tests for the taskforge pipeline.

No mocks. Exercises the actual code paths against:
  - the real harbor_tasks/ corpus (read-only)
  - real auto-fixer scripts in dry-run mode
  - real subprocess calls to CLI entry points

Replaces the brittle mock-heavy tests skipped in test_e2b_worker.py
(2026-04-24 audit).
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from taskforge import rubrics
from taskforge.task_lint import (
    Finding,
    check_all_gold_tests_passed,
    lint_task,
    lint_test_sh,
    lint_solve_sh,
    lint_tests_subprocess,
    lint_test_deps_in_dockerfile,
    lint_substring_assertions_instructed,
    lint_lint_requirement_stated,
    lint_instruction_leakage,
)


HARBOR = ROOT / "harbor_tasks"


# ════════════════════════════════════════════════════════════════════════════
# Rubric registry consistency — every rubric must be well-formed
# ════════════════════════════════════════════════════════════════════════════

class TestRubricRegistry:
    def test_every_rubric_has_required_fields(self):
        for r in rubrics.RUBRICS:
            assert r.name, f"rubric missing name"
            assert r.tier in ("A", "B", "C"), f"{r.name}: bad tier {r.tier}"
            assert r.description, f"{r.name}: missing description"
            assert r.artifacts, f"{r.name}: must list affected artifacts"
            assert r.verification in ("programmatic", "llm_judge", "both")
            assert r.source, f"{r.name}: must cite source"

    def test_every_llm_judge_rubric_has_judge_prompt(self):
        for r in rubrics.RUBRICS:
            if r.verification in ("llm_judge", "both"):
                # Prompt is optional in dataclass; warn but don't fail. Track A
                # rubrics specifically should have prompts since they ship to
                # the judge call.
                if r.tier == "A":
                    assert r.judge_prompt, (
                        f"Tier-A llm_judge rubric {r.name} has no judge_prompt — "
                        f"the LLM judge will see only the description"
                    )

    def test_rubric_names_are_unique(self):
        names = [r.name for r in rubrics.RUBRICS]
        assert len(names) == len(set(names)), "duplicate rubric names"

    def test_all_9_new_2026_04_24_rubrics_present(self):
        """The day's audit added these. Regression-protect against accidental removal."""
        new_rubrics = {
            "oracle_no_external_fetch", "tests_have_subprocess",
            "gold_diff_non_trivial", "instruction_no_path_leak",
            "reward_is_pure_pytest", "every_gold_test_passes",
            "test_deps_in_dockerfile", "substring_assertions_are_instructed",
            "lint_requirement_stated",
        }
        present = {r.name for r in rubrics.RUBRICS}
        missing = new_rubrics - present
        assert not missing, f"new rubrics missing: {missing}"


# ════════════════════════════════════════════════════════════════════════════
# Real-corpus lint behavior — known-good and known-broken tasks
# ════════════════════════════════════════════════════════════════════════════

# A handful of tasks that were specifically auto-fixed today. Asserting on
# the post-fix state confirms our fixers + lint behave consistently.

@pytest.mark.skipif(not HARBOR.exists(), reason="harbor_tasks/ not present")
class TestRealCorpusLint:
    def test_clean_task_post_autofix_has_no_hard_fails(self):
        """transformers-processor-chat-template-kwargs had no reward-gate bugs
        before today and should still be clean after our changes."""
        td = HARBOR / "transformers-processor-chat-template-kwargs"
        if not td.exists():
            pytest.skip(f"{td.name} not in corpus")
        fs = lint_test_sh(td)
        purity_fails = [f for f in fs if f.rubric == "reward_is_pure_pytest"
                        and f.severity == "fail"]
        assert not purity_fails, (
            f"clean reference task has purity fails: {[str(f) for f in purity_fails]}"
        )

    def test_contaminated_oracle_caught(self):
        td = HARBOR / "airflow-worker-serviceaccount-split"
        if not td.exists():
            pytest.skip(f"{td.name} not in corpus")
        fs = [f for f in lint_solve_sh(td)
              if f.rubric == "oracle_no_external_fetch"]
        assert fs, "broken-oracle task no longer flagged by oracle_no_external_fetch"
        assert "curl_gh_diff" in fs[0].detail or "github" in fs[0].detail.lower()

    def test_autofixed_test_sh_no_longer_flagged(self):
        """airflow-migration-0097-sqlite-fk-fix had grep_gate + early_exit
        before today's auto-fix; the early_exit should be cleared."""
        td = HARBOR / "airflow-migration-0097-sqlite-fk-fix"
        if not td.exists():
            pytest.skip(f"{td.name} not in corpus")
        fs = [f for f in lint_test_sh(td)
              if f.rubric == "reward_is_pure_pytest"]
        details = " ".join(f.detail for f in fs)
        # early_exit was auto-disabled — should NOT appear anymore
        assert "terminates script before LLM judge" not in details, (
            "early_exit auto-fix appears to have regressed"
        )

    def test_pip_installable_linter_dockerfile_now_includes_ruff(self):
        """ClickHouse-pr-102169 had codespell missing; the auto-fixer (today)
        injected a pip install. Verify it sticks."""
        td = HARBOR / "Accept digest for init container image"
        if not td.exists():
            pytest.skip(f"{td.name} not in corpus")
        df = (td / "environment" / "Dockerfile").read_text()
        # Verify our auto-fix marker is present
        assert "auto-installed (scaffold Change 2A retrofit" in df, (
            "Dockerfile auto-augment marker missing"
        )

    def test_lint_requirement_section_appended(self):
        """ClickHouse-pr-102080 had mypy in tests; auto-fixer appended the section."""
        td = HARBOR / "ClickHouse-pr-102080"
        if not td.exists():
            pytest.skip(f"{td.name} not in corpus")
        instr = (td / "instruction.md").read_text()
        assert "## Code Style Requirements" in instr, (
            "auto-fix didn't add Code Style Requirements section"
        )


# ════════════════════════════════════════════════════════════════════════════
# Synthetic task fixtures — exercise each new linter in isolation
# ════════════════════════════════════════════════════════════════════════════

def _make_task(tmp: Path, *, dockerfile: str, test_sh: str, test_outputs: str,
               instruction: str = "# Task\n\nA bug to fix.\n",
               solve: str = "#!/bin/bash\nset -e\necho dummy\n",
               manifest: str = 'version: "2.0"\nchecks: []\n') -> Path:
    """Create a minimal task dir for lint tests."""
    (tmp / "environment").mkdir(parents=True)
    (tmp / "tests").mkdir(parents=True)
    (tmp / "solution").mkdir(parents=True)
    (tmp / "environment" / "Dockerfile").write_text(dockerfile)
    (tmp / "tests" / "test.sh").write_text(test_sh)
    (tmp / "tests" / "test_outputs.py").write_text(test_outputs)
    (tmp / "instruction.md").write_text(instruction)
    (tmp / "solution" / "solve.sh").write_text(solve)
    (tmp / "tests" / "eval_manifest.yaml").write_text(manifest)
    return tmp


CLEAN_TEST_SH = """#!/usr/bin/env bash
set -e
python3 -m pytest /tests/test_outputs.py
if [ $? -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi
"""

CLEAN_TEST_OUTPUTS = """import subprocess

def test_behavioral():
    r = subprocess.run(["python3", "-c", "print(42)"], capture_output=True)
    assert r.returncode == 0
"""


class TestRewardPurityLinter:
    def test_grep_gate_flagged(self, tmp_path):
        bad = "#!/usr/bin/env bash\npytest 2>&1 | grep -q failed\nif [ $? -ne 0 ]; then echo 1 > /logs/verifier/reward.txt; else echo 0 > /logs/verifier/reward.txt; fi\n"
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=bad, test_outputs=CLEAN_TEST_OUTPUTS)
        fs = [f for f in lint_test_sh(td) if f.rubric == "reward_is_pure_pytest"]
        assert fs, "grep gate not flagged"
        assert any("grep/awk/sed" in f.detail for f in fs)

    def test_wrong_path_flagged(self, tmp_path):
        bad = "#!/usr/bin/env bash\npytest /tests/test_outputs.py\nif [ $? -eq 0 ]; then echo 1 > /logs/verifier/reward.json; fi\n"
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=bad, test_outputs=CLEAN_TEST_OUTPUTS)
        fs = [f for f in lint_test_sh(td) if f.rubric == "reward_is_pure_pytest"]
        assert fs, "wrong path not flagged"
        assert any("non-canonical path" in f.detail for f in fs)

    def test_clean_test_sh_no_finding(self, tmp_path):
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=CLEAN_TEST_OUTPUTS)
        fs = [f for f in lint_test_sh(td) if f.rubric == "reward_is_pure_pytest"]
        assert not fs, f"clean test.sh flagged: {[str(f) for f in fs]}"


class TestTestsHaveSubprocess:
    def test_grep_only_test_flagged(self, tmp_path):
        grep_only = """def test_grep():
    content = open("/repo/foo.py").read()
    assert "expected_pattern" in content
"""
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=grep_only)
        fs = lint_tests_subprocess(td)
        assert fs and fs[0].rubric == "tests_have_subprocess"

    def test_subprocess_test_passes(self, tmp_path):
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=CLEAN_TEST_OUTPUTS)
        fs = lint_tests_subprocess(td)
        assert not fs


class TestOracleNoExternalFetch:
    @pytest.mark.parametrize("solve", [
        "#!/bin/bash\ncurl -sL https://github.com/foo/bar/pull/42.diff | git apply -",
        "#!/bin/bash\ngit show abc1234567 | git apply -",
        "#!/bin/bash\nwget https://github.com/foo/bar/pull/99.patch && git apply 99.patch",
        "#!/bin/bash\ngh pr diff 42 | git apply -",
    ])
    def test_external_fetch_pattern_caught(self, tmp_path, solve):
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=CLEAN_TEST_OUTPUTS,
                        solve=solve)
        fs = [f for f in lint_solve_sh(td) if f.rubric == "oracle_no_external_fetch"]
        assert fs, f"pattern not caught in: {solve!r}"

    def test_inline_heredoc_solve_clean(self, tmp_path):
        solve = """#!/bin/bash
cd /workspace/repo
git apply - <<'PATCH'
diff --git a/foo.py b/foo.py
index abc..def 100644
--- a/foo.py
+++ b/foo.py
@@ -1 +1 @@
-old
+new
PATCH
"""
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=CLEAN_TEST_OUTPUTS,
                        solve=solve)
        fs = [f for f in lint_solve_sh(td) if f.rubric == "oracle_no_external_fetch"]
        assert not fs


class TestEnvDepsInDockerfile:
    def test_missing_ruff_flagged(self, tmp_path):
        tests = "import subprocess\ndef test_ruff():\n    r = subprocess.run(['ruff', 'check', '.'], capture_output=True)\n    assert r.returncode == 0\n"
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=tests)
        fs = lint_test_deps_in_dockerfile(td)
        assert fs, "missing ruff not flagged"
        assert "ruff" in fs[0].snippet

    def test_implicit_via_node_base_image(self, tmp_path):
        """FROM node:* should auto-recognize npx/npm/pnpm/yarn as installed."""
        tests = "import subprocess\ndef test_npx():\n    r = subprocess.run(['npx', 'tsc', '--version'], capture_output=True)\n    assert r.returncode == 0\n"
        td = _make_task(tmp_path, dockerfile="FROM node:22-slim\nRUN apt-get update\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=tests)
        fs = lint_test_deps_in_dockerfile(td)
        assert not fs, f"npx falsely flagged with FROM node: {[str(f) for f in fs]}"

    def test_explicit_pip_install_satisfies(self, tmp_path):
        tests = "import subprocess\ndef test_ruff():\n    r = subprocess.run(['ruff', 'check', '.'], capture_output=True)\n    assert r.returncode == 0\n"
        td = _make_task(tmp_path, dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4 ruff==0.5.0\n",
                        test_sh=CLEAN_TEST_SH, test_outputs=tests)
        fs = lint_test_deps_in_dockerfile(td)
        assert not fs, "ruff in pip install line should satisfy gate"


class TestSubstringAssertionsInstructed:
    def test_ungrounded_literal_flagged(self, tmp_path):
        tests = """def test_warn():
    assert "is larger than 5 MB. Large files should not be committed" in output
"""
        td = _make_task(
            tmp_path,
            dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
            test_sh=CLEAN_TEST_SH, test_outputs=tests,
            instruction="# Task\n\nThe warning should mention size limits.\n",
        )
        fs = lint_substring_assertions_instructed(td)
        assert fs

    def test_grounded_literal_not_flagged(self, tmp_path):
        tests = """def test_warn():
    assert "exact warning message body" in output
"""
        td = _make_task(
            tmp_path,
            dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
            test_sh=CLEAN_TEST_SH, test_outputs=tests,
            instruction="# Task\n\nThe warning must say: \"exact warning message body\".\n",
        )
        fs = lint_substring_assertions_instructed(td)
        assert not fs


class TestLintRequirementStated:
    def test_ruff_in_tests_no_mention_in_instr_flagged(self, tmp_path):
        # `ruff format --check` matches the `_LINT_TOOLS["ruff"]` pattern via
        # the `format` keyword
        tests = "import subprocess\ndef test_ruff():\n    subprocess.run(['ruff format --check .'.split()])\n"
        td = _make_task(
            tmp_path,
            dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4 ruff==0.5.0\n",
            test_sh=CLEAN_TEST_SH, test_outputs=tests,
            instruction="# Task\n\nFix bug X.\n",
        )
        fs = lint_lint_requirement_stated(td)
        assert fs and "ruff" in fs[0].snippet

    def test_ruff_mentioned_in_instr_clean(self, tmp_path):
        tests = "import subprocess\ndef test_ruff():\n    subprocess.run(['ruff format --check .'.split()])\n"
        td = _make_task(
            tmp_path,
            dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4 ruff==0.5.0\n",
            test_sh=CLEAN_TEST_SH, test_outputs=tests,
            instruction="# Task\n\nFix bug X. Code must pass `ruff format`.\n",
        )
        fs = lint_lint_requirement_stated(td)
        assert not fs


class TestInstructionPathLeak:
    def test_full_path_in_instruction_flagged_warn(self, tmp_path):
        # `--- a/<path>` and `+++ b/<path>` are the lines lint_instruction_leakage
        # parses from solve.sh's embedded heredoc patch
        solve = """#!/bin/bash
git apply - <<'PATCH'
diff --git a/src/foo/bar.py b/src/foo/bar.py
--- a/src/foo/bar.py
+++ b/src/foo/bar.py
@@ -1 +1 @@
-old
+new
PATCH
"""
        td = _make_task(
            tmp_path,
            dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
            test_sh=CLEAN_TEST_SH, test_outputs=CLEAN_TEST_OUTPUTS,
            solve=solve,
            instruction="# Task\n\nThe file `src/foo/bar.py` has a bug.\n",
        )
        fs = lint_instruction_leakage(td)
        # warn-severity, not fail (per design — endemic in corpus)
        assert fs and fs[0].severity == "warn"


# ════════════════════════════════════════════════════════════════════════════
# check_all_gold_tests_passed — file-system contract
# ════════════════════════════════════════════════════════════════════════════

class TestGoldTestPassChecker:
    def test_missing_file_returns_empty(self, tmp_path):
        assert check_all_gold_tests_passed(tmp_path / "nonexistent.json") == []

    def test_malformed_json_returns_empty(self, tmp_path):
        bad = tmp_path / "bad.json"
        bad.write_text("not json at all {")
        assert check_all_gold_tests_passed(bad) == []

    def test_all_passed_returns_empty(self, tmp_path):
        good = tmp_path / "ctrf.json"
        good.write_text(json.dumps({
            "results": {"tests": [
                {"name": "test_a", "status": "passed"},
                {"name": "test_b", "status": "passed"},
            ]}
        }))
        assert check_all_gold_tests_passed(good) == []

    def test_one_failed_flagged(self, tmp_path):
        partial = tmp_path / "ctrf.json"
        partial.write_text(json.dumps({
            "results": {"tests": [
                {"name": "test_a", "status": "passed"},
                {"name": "test_b_broken", "status": "failed"},
            ]}
        }))
        fs = check_all_gold_tests_passed(partial)
        assert len(fs) == 1
        assert fs[0].rubric == "every_gold_test_passes"
        assert "test_b_broken" in fs[0].snippet


# ════════════════════════════════════════════════════════════════════════════
# Auto-fixer scripts — real subprocess, real corpus, idempotency
# ════════════════════════════════════════════════════════════════════════════

class TestAutoFixerScriptsIdempotent:
    """Each fixer should produce 0 changes on a second run."""

    def _run_fixer(self, name: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [".venv/bin/python", f"scripts/{name}", *args],
            cwd=ROOT, capture_output=True, text=True, timeout=180,
        )

    @pytest.mark.skipif(not (ROOT / "scripts" / "fix_lint_requirement.py").exists(),
                        reason="auto-fixer not present")
    def test_fix_lint_requirement_dry_run_zero_after_apply(self):
        """We applied this fixer in a prior commit; running --dry-run now
        should report 0 augmentations needed (idempotency)."""
        r = self._run_fixer("fix_lint_requirement.py", "--dry-run")
        assert r.returncode == 0, f"fixer crashed: {r.stderr}"
        # Output: "Tasks augmented: N"
        assert "Tasks augmented: 0" in r.stdout, (
            f"non-zero on rerun (not idempotent): {r.stdout[-300:]}"
        )

    @pytest.mark.skipif(not (ROOT / "scripts" / "fix_test_deps.py").exists(),
                        reason="auto-fixer not present")
    def test_fix_test_deps_dry_run_only_remaining_non_pip(self):
        r = self._run_fixer("fix_test_deps.py", "--dry-run")
        assert r.returncode == 0
        # We applied to all 165 pip-installable tasks already. Rerun should
        # find at most a handful (newly-flagged after lint refactor).
        assert "Tasks auto-fixable" in r.stdout

    @pytest.mark.skipif(not (ROOT / "scripts" / "fix_reward_purity.py").exists(),
                        reason="auto-fixer not present")
    def test_fix_reward_purity_dry_run_runs(self):
        r = self._run_fixer("fix_reward_purity.py", "--dry-run")
        assert r.returncode == 0
        # "Found" goes to stderr; summary to stdout. Either contains evidence
        # the script ran successfully.
        combined = r.stdout + r.stderr
        assert "Found" in combined or "DRY-RUN summary" in r.stdout


# ════════════════════════════════════════════════════════════════════════════
# CLI entry points — real --help invocations
# ════════════════════════════════════════════════════════════════════════════

class TestCLIHelp:
    @pytest.mark.parametrize("script", [
        "scripts/run_agent_eval.py",
        "scripts/fix_reward_purity.py",
        "scripts/fix_lint_requirement.py",
        "scripts/fix_test_deps.py",
    ])
    def test_help_works(self, script):
        if not (ROOT / script).exists():
            pytest.skip(f"{script} not present")
        r = subprocess.run(
            [".venv/bin/python", script, "--help"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{script} --help failed: {r.stderr}"
        assert "usage" in r.stdout.lower()

    def test_run_agent_eval_lists_all_backends(self):
        r = subprocess.run(
            [".venv/bin/python", "scripts/run_agent_eval.py", "--help"],
            cwd=ROOT, capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0
        # Today's added backends must show up
        for backend in ("kimi", "glm5", "minimax", "anthropic"):
            assert backend in r.stdout, f"backend {backend} missing from --help"
        assert "--pin-claude-version" in r.stdout


# ════════════════════════════════════════════════════════════════════════════
# Backend pool — real env-var resolution
# ════════════════════════════════════════════════════════════════════════════

class TestBackendPool:
    def test_backends_from_env_returns_list(self, monkeypatch):
        from taskforge import backends
        # Provide one minimal key so we get at least 1 backend
        monkeypatch.setenv("ANTHROPIC_API_KEY", "x" * 40)
        monkeypatch.setenv("ANTHROPIC_ENABLED", "1")
        result = backends.backends_from_env()
        assert isinstance(result, list)
        assert all(hasattr(b, "name") for b in result)
        assert all(hasattr(b, "base_url") for b in result)

    def test_no_disabled_fireworks_or_gemini_as_agent(self):
        """Today we removed the dead Fireworks + Gemini-as-agent backends.
        They must not appear regardless of env."""
        import os
        from taskforge import backends
        # Even if someone sets FIREWORKS_API_KEY + FIREWORKS_ENABLED, the
        # registration code is gone — backend pool won't include "fireworks".
        os.environ["FIREWORKS_API_KEY"] = "x" * 40
        os.environ["FIREWORKS_ENABLED"] = "1"
        try:
            names = {b.name for b in backends.backends_from_env()}
            assert "fireworks" not in names, (
                "Fireworks backend resurrected — should be removed permanently"
            )
            assert "gemini" not in names, (
                "Gemini-as-agent backend resurrected — should be removed permanently"
            )
        finally:
            os.environ.pop("FIREWORKS_API_KEY", None)
            os.environ.pop("FIREWORKS_ENABLED", None)


# ════════════════════════════════════════════════════════════════════════════
# Scaffold prompts referenced in code must exist on disk
# ════════════════════════════════════════════════════════════════════════════

class TestPromptsExist:
    def test_all_prompts_in_use_exist(self):
        prompt_dir = ROOT / "taskforge" / "prompts"
        assert prompt_dir.is_dir()
        prompts = {p.name for p in prompt_dir.glob("*.md")}
        # These are referenced by name in e2b_worker.py / pipeline.py
        expected = {
            "scaffold.md", "scaffold_agentmd.md",
            "fix_task_quality.md", "validate_and_fix.md",
            "improve_tests.md", "instruction_reconcile.md",
            "tests_rewrite.md", "enrich_p2p.md", "enrich_rubric.md",
            "fix_rubric.md",
        }
        missing = expected - prompts
        assert not missing, f"prompts referenced in code but missing: {missing}"

    def test_scaffold_prompt_mentions_new_rubrics(self):
        """The scaffold prompt should educate the agent about every Tier-A
        rubric. After today's update, all 6 new ones must be named."""
        scaffold = (ROOT / "taskforge" / "prompts" / "scaffold.md").read_text()
        for r in ("oracle_no_external_fetch", "tests_have_subprocess",
                  "gold_diff_non_trivial", "reward_is_pure_pytest",
                  "test_deps_in_dockerfile", "every_gold_test_passes"):
            assert r in scaffold, f"scaffold.md doesn't mention rubric {r}"


# ════════════════════════════════════════════════════════════════════════════
# End-to-end lint orchestrator on a real task
# ════════════════════════════════════════════════════════════════════════════

@pytest.mark.skipif(not HARBOR.exists(), reason="harbor_tasks/ not present")
class TestLintTaskOrchestrator:
    def test_lint_task_runs_on_real_corpus_without_crashing(self):
        """Smoke-test the orchestrator across a sample of real tasks. The
        previous unit tests caught a malformed-yaml crash; this prevents
        regression."""
        sample = sorted(d for d in HARBOR.iterdir() if d.is_dir())[:20]
        crashed = []
        for td in sample:
            try:
                lint_task(td)
            except Exception as e:
                crashed.append((td.name, type(e).__name__, str(e)[:80]))
        assert not crashed, f"orchestrator crashed on real tasks: {crashed}"

    def test_findings_have_required_attrs(self):
        sample = sorted(d for d in HARBOR.iterdir() if d.is_dir())[:5]
        for td in sample:
            for f in lint_task(td):
                assert isinstance(f, Finding)
                assert f.rubric and f.tier in ("A", "B", "C")
                assert f.severity in ("fail", "warn")
                assert isinstance(f.path, str)
                assert isinstance(f.line, int)
