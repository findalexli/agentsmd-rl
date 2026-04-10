"""
Task: mlflow-analyze-ci-support-run-urls
Repo: mlflow/mlflow @ 6469b26207d525615816a9498e849bcf4a8da75e
PR:   21331

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/mlflow"
ANALYZE_CI = Path(REPO) / ".claude/skills/src/skills/commands/analyze_ci.py"
SKILL_MD = Path(REPO) / ".claude/skills/analyze-ci/SKILL.md"


def _extract_regex_patterns(source: str) -> dict[str, str]:
    """Extract top-level NAME = re.compile(r"...") patterns from source."""
    tree = ast.parse(source)
    patterns = {}
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
            and len(node.value.args) >= 1
        ):
            name = node.targets[0].id
            if name.endswith("_PATTERN"):
                arg = node.value.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    patterns[name] = arg.value
    return patterns


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """analyze_ci.py must parse without syntax errors."""
    r = subprocess.run(
        ["python3", "-c", f"import py_compile; py_compile.compile(\"{ANALYZE_CI}\", doraise=True)"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_run_url_pattern_matches_run_urls():
    """RUN_URL_PATTERN must match bare workflow run URLs."""
    source = ANALYZE_CI.read_text()
    patterns = _extract_regex_patterns(source)
    assert "RUN_URL_PATTERN" in patterns, "RUN_URL_PATTERN not defined"
    pat = re.compile(patterns["RUN_URL_PATTERN"])

    run_urls = [
        "https://github.com/mlflow/mlflow/actions/runs/22626454465",
        "https://github.com/owner/repo/actions/runs/99999",
        "https://github.com/a/b/actions/runs/1",
    ]
    for url in run_urls:
        m = pat.search(url)
        assert m is not None, f"RUN_URL_PATTERN failed to match: {url}"
        assert m.group(2).isdigit(), f"Group 2 should be run ID, got: {m.group(2)}"


# [pr_diff] fail_to_pass
def test_run_url_pattern_excludes_job_urls():
    """RUN_URL_PATTERN must NOT match job URLs (which have /job/N suffix)."""
    source = ANALYZE_CI.read_text()
    patterns = _extract_regex_patterns(source)
    assert "RUN_URL_PATTERN" in patterns, "RUN_URL_PATTERN not defined"
    pat = re.compile(patterns["RUN_URL_PATTERN"])

    job_urls = [
        "https://github.com/mlflow/mlflow/actions/runs/12345/job/67890",
        "https://github.com/owner/repo/actions/runs/1/job/2",
    ]
    for url in job_urls:
        assert pat.search(url) is None, f"RUN_URL_PATTERN should not match job URL: {url}"


# [pr_diff] fail_to_pass
def test_resolve_urls_dispatches_run_pattern():
    """resolve_urls must handle RUN_URL_PATTERN in its dispatch logic."""
    source = ANALYZE_CI.read_text()
    tree = ast.parse(source)
    resolve_fn = None
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "resolve_urls":
            resolve_fn = node
            break
    assert resolve_fn is not None, "resolve_urls function not found"
    fn_source = ast.get_source_segment(source, resolve_fn)
    assert "RUN_URL_PATTERN" in fn_source, (
        "resolve_urls does not reference RUN_URL_PATTERN — "
        "run URLs are not dispatched"
    )
    assert "get_jobs" in fn_source, (
        "resolve_urls should call get_jobs to fetch failed jobs for the run"
    )


# [pr_diff] fail_to_pass
def test_help_text_mentions_run_url():
    """Help text or error messages must mention run URL or workflow run as a valid format."""
    source = ANALYZE_CI.read_text()
    # Check that the argparse help or error messages explicitly mention run URLs
    # as a distinct format (not just "job URL" which also contains "runs")
    has_run_url_mention = False
    for line in source.split("\n"):
        lower = line.lower()
        # Look for lines that mention "run url" or "workflow run url" distinctly
        if ("run url" in lower or "workflow run" in lower) and "job" not in lower:
            has_run_url_mention = True
            break
    assert has_run_url_mention, (
        "Code should mention run URL or workflow run URL in help text or error messages"
    )


# ---------------------------------------------------------------------------
# Config/doc update tests (REQUIRED for agentmd-edit)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_skill_md_documents_run_urls():
    """SKILL.md must document workflow run URL as a supported input format."""
    content = SKILL_MD.read_text()
    assert "run" in content.lower(), "SKILL.md should mention workflow runs"
    assert "actions/runs/" in content, "SKILL.md should show a run URL example"
    # Must have a run URL example that is NOT a job URL (no /job/ suffix)
    lines = content.split("\n")
    has_bare_run_url = False
    for line in lines:
        if "actions/runs/" in line and "/job/" not in line:
            has_bare_run_url = True
            break
    assert has_bare_run_url, (
        "SKILL.md must have a bare run URL example (actions/runs/N without /job/)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_ruff_check_analyze_ci():
    """Ruff linting passes on analyze_ci.py (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.2", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    r = subprocess.run(
        ["python3", "-m", "ruff", "check", str(ANALYZE_CI)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_clint_tests():
    """Clint linter tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "packaging", "pytest", "tomli", "typing_extensions", "-e", ".", "-q"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/dev/clint",
    )
    assert r.returncode == 0, f"Failed to install clint: {r.stderr}"

    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=300, cwd=f"{REPO}/dev/clint",
    )
    assert r.returncode == 0, f"Clint tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_patterns_intact():
    """PR_URL_PATTERN and JOB_URL_PATTERN must still exist and match their URL formats."""
    source = ANALYZE_CI.read_text()
    patterns = _extract_regex_patterns(source)

    assert "PR_URL_PATTERN" in patterns, "PR_URL_PATTERN was removed"
    pr_pat = re.compile(patterns["PR_URL_PATTERN"])
    assert pr_pat.search("https://github.com/mlflow/mlflow/pull/19601") is not None

    assert "JOB_URL_PATTERN" in patterns, "JOB_URL_PATTERN was removed"
    job_pat = re.compile(patterns["JOB_URL_PATTERN"])
    assert job_pat.search("https://github.com/mlflow/mlflow/actions/runs/12345/job/67890") is not None


# [repo_tests] pass_to_pass
def test_analyze_ci_module_structure():
    """Repo: analyze_ci.py has expected structure (register func, run func, resolve_urls)."""
    source = ANALYZE_CI.read_text()
    tree = ast.parse(source)

    # Check for required async functions
    async_funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)}
    required_async = {"resolve_urls", "cmd_analyze_async"}
    for func in required_async:
        assert func in async_funcs, f"Required async function {func} missing"

    # Check for required regular functions
    funcs = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
    required_funcs = {"register", "run"}
    for func in required_funcs:
        assert func in funcs, f"Required function {func} missing"


# [repo_tests] pass_to_pass
def test_skill_md_valid_structure():
    """Repo: SKILL.md has valid markdown structure with Usage and Examples sections."""
    content = SKILL_MD.read_text()

    # Check for required sections
    assert "## Usage" in content, "SKILL.md missing ## Usage section"
    assert "## Examples" in content, "SKILL.md missing ## Examples section"

    # Check that examples are code blocks
    assert "```" in content, "SKILL.md should have code blocks in examples"

    # Verify at least one GitHub URL pattern is documented
    assert "github.com/" in content, "SKILL.md should document GitHub URL patterns"
