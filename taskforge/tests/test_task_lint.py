"""Tests for taskforge.task_lint — the 20-rubric programmatic linter."""

from pathlib import Path

import pytest

from taskforge.task_lint import (
    Finding,
    lint_dockerfile,
    lint_manifest,
    lint_task,
    lint_test_outputs,
    lint_test_sh,
    summarize,
)


# ═════════════════════════════════════════════════════════════════════════════
# Helpers
# ═════════════════════════════════════════════════════════════════════════════

def make_task(tmp_path: Path, *, dockerfile: str = "", test_sh: str = "",
              test_outputs: str = "", manifest: str = "") -> Path:
    """Create a minimal task dir with the given file contents."""
    (tmp_path / "environment").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "solution").mkdir()
    if dockerfile:
        (tmp_path / "environment" / "Dockerfile").write_text(dockerfile)
    if test_sh:
        (tmp_path / "tests" / "test.sh").write_text(test_sh)
    if test_outputs:
        (tmp_path / "tests" / "test_outputs.py").write_text(test_outputs)
    if manifest:
        (tmp_path / "eval_manifest.yaml").write_text(manifest)
    return tmp_path


def names(findings: list[Finding]) -> list[str]:
    return [f.rubric for f in findings]


# ═════════════════════════════════════════════════════════════════════════════
# Dockerfile
# ═════════════════════════════════════════════════════════════════════════════

class TestDockerfile:
    def test_latest_tag_flagged(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:latest\n")
        findings = lint_dockerfile(task)
        assert "dockerfile_determinism" in names(findings)

    def test_untagged_base_flagged(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python\n")
        findings = lint_dockerfile(task)
        assert "dockerfile_determinism" in names(findings)

    def test_pinned_base_ok(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12-slim\n")
        findings = lint_dockerfile(task)
        assert not findings

    def test_unpinned_pip_flagged(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nRUN pip install pytest\n")
        findings = lint_dockerfile(task)
        assert "pinned_dependencies" in names(findings)

    def test_pinned_pip_ok(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nRUN pip install pytest==8.3.4\n")
        findings = lint_dockerfile(task)
        assert "pinned_dependencies" not in names(findings)

    def test_pip_requirements_file_ok(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nRUN pip install -r requirements.txt\n")
        findings = lint_dockerfile(task)
        assert "pinned_dependencies" not in names(findings)

    def test_copy_solution_flagged(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nCOPY solution/ /opt/sol/\n")
        findings = lint_dockerfile(task)
        assert "no_hidden_solution_artifacts" in names(findings)
        assert [f.tier for f in findings if f.rubric == "no_hidden_solution_artifacts"] == ["A"]

    def test_copy_tests_flagged(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nCOPY tests/ /opt/tests/\n")
        findings = lint_dockerfile(task)
        assert "tests_or_solution_in_image" in names(findings)

    def test_curl_pipe_bash_warned(self, tmp_path):
        task = make_task(tmp_path, dockerfile="FROM python:3.12\nRUN curl https://example.com/install.sh | bash\n")
        findings = lint_dockerfile(task)
        assert any(f.rubric == "dockerfile_determinism" and f.severity == "warn" for f in findings)


# ═════════════════════════════════════════════════════════════════════════════
# test.sh
# ═════════════════════════════════════════════════════════════════════════════

class TestTestSh:
    BOOTSTRAP = """\
#!/usr/bin/env bash
set +e
if ! python3 -c "import pytest" 2>/dev/null; then
    apt-get update && apt-get install -y python3-pip
    pip install pytest==8.0.0
fi
python3 -m pytest /tests/test_outputs.py
"""

    BARE_INSTALL = """\
#!/usr/bin/env bash
set +e
pip install pytest
python3 -m pytest /tests/test_outputs.py
"""

    def test_pytest_bootstrap_guard_silenced(self, tmp_path):
        task = make_task(tmp_path, test_sh=self.BOOTSTRAP)
        findings = lint_test_sh(task)
        assert not [f for f in findings if f.rubric == "no_network_during_tests"]

    def test_bare_install_flagged(self, tmp_path):
        task = make_task(tmp_path, test_sh=self.BARE_INSTALL)
        findings = lint_test_sh(task)
        assert any(f.rubric == "no_network_during_tests" for f in findings)


# ═════════════════════════════════════════════════════════════════════════════
# test_outputs.py
# ═════════════════════════════════════════════════════════════════════════════

TAUTOLOGICAL_ONLY = """
def test_foo():
    x = get_foo()
    assert x is not None
    assert isinstance(x, list)
"""

BEHAVIORAL = """
import subprocess

def test_bar():
    # Real subprocess call to satisfy tests_have_subprocess rubric
    r = subprocess.run(["python3", "-c", "print(42)"], capture_output=True)
    assert r.returncode == 0
    assert r.stdout.strip() == b"42"
"""

MIXED_WITH_HEREDOC = '''
import subprocess

def test_cc():
    """Test with heredoc — multi-line string at col 0 inside the body."""
    assert NODE_OK, "guard"

    r = subprocess.run(["node", "-e", r"""
const text = readBunTs();
const x = doWork(text);
process.stdout.write(JSON.stringify({ok: x === "foo"}));
"""], capture_output=True)
    assert r.returncode == 0
    assert r.stdout.decode().endswith('"ok":true}')
'''

PURE_GREP_TEST = """
def test_grep():
    content = open("/workspace/repo/src/foo.py").read()
    assert "def bar" in content
"""


class TestTestOutputs:
    def test_tautological_all_flagged(self, tmp_path):
        task = make_task(tmp_path, test_outputs=TAUTOLOGICAL_ONLY)
        findings = lint_test_outputs(task)
        assert "test_not_tautological" in names(findings)

    def test_behavioral_not_flagged(self, tmp_path):
        task = make_task(tmp_path, test_outputs=BEHAVIORAL)
        findings = lint_test_outputs(task)
        assert "test_not_tautological" not in names(findings)

    def test_heredoc_body_parsed_correctly(self, tmp_path):
        """Regression: indent-based extraction breaks on col-0 heredocs;
        AST extraction handles them."""
        task = make_task(tmp_path, test_outputs=MIXED_WITH_HEREDOC)
        findings = lint_test_outputs(task)
        # test_cc has 3 asserts (guard + 2 real); should NOT be flagged
        assert not [f for f in findings if f.rubric == "test_not_tautological"]

    def test_pure_grep_flagged(self, tmp_path):
        task = make_task(tmp_path, test_outputs=PURE_GREP_TEST)
        findings = lint_test_outputs(task)
        assert "tests_verify_behavior_not_text" in names(findings)

    def test_syntax_error_does_not_crash(self, tmp_path):
        task = make_task(tmp_path, test_outputs="def test_foo(:\n    assert")
        findings = lint_test_outputs(task)
        assert findings == []  # graceful fallback


# ═════════════════════════════════════════════════════════════════════════════
# manifest
# ═════════════════════════════════════════════════════════════════════════════

class TestManifest:
    def test_no_p2p_flagged(self, tmp_path):
        task = make_task(tmp_path, manifest="""
version: "2.0"
checks:
  - id: a
    type: fail_to_pass
  - id: b
    type: fail_to_pass
""")
        findings = lint_manifest(task)
        assert "pass_to_pass_coverage" in names(findings)

    def test_with_p2p_ok(self, tmp_path):
        task = make_task(tmp_path, manifest="""
version: "2.0"
checks:
  - id: a
    type: fail_to_pass
  - id: b
    type: fail_to_pass
  - id: c
    type: pass_to_pass
""")
        findings = lint_manifest(task)
        assert "pass_to_pass_coverage" not in names(findings)

    def test_few_f2p_warns(self, tmp_path):
        task = make_task(tmp_path, manifest="""
version: "2.0"
checks:
  - id: a
    type: fail_to_pass
  - id: c
    type: pass_to_pass
""")
        findings = lint_manifest(task)
        assert "f2p_p2p_classification_correct" in names(findings)


# ═════════════════════════════════════════════════════════════════════════════
# summarize + orchestrator
# ═════════════════════════════════════════════════════════════════════════════

def test_summarize_counts_tiers(tmp_path):
    task = make_task(
        tmp_path,
        dockerfile="FROM python:latest\nCOPY solution/ /opt/\n",
        test_outputs=TAUTOLOGICAL_ONLY,
    )
    findings = lint_task(task)
    s = summarize(findings)
    assert s["tier_a_fails"] >= 2  # no_hidden_solution_artifacts + test_not_tautological
    assert s["by_tier"]["A"] >= 2
    assert s["by_tier"]["B"] >= 1  # dockerfile_determinism


def test_clean_task_empty_findings(tmp_path):
    task = make_task(
        tmp_path,
        dockerfile="FROM python:3.12-slim\nRUN pip install pytest==8.3.4\n",
        test_sh=TestTestSh.BOOTSTRAP,
        test_outputs=BEHAVIORAL,
        manifest="""
version: "2.0"
checks:
  - id: a
    type: fail_to_pass
  - id: b
    type: fail_to_pass
  - id: c
    type: pass_to_pass
""",
    )
    findings = lint_task(task)
    assert findings == [], f"expected clean, got: {[str(f) for f in findings]}"
