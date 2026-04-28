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
# Helper: run a behavioral test by importing the module with mocked deps
# ---------------------------------------------------------------------------

_MOCK_SETUP = r"""
import sys, types, re, asyncio, io, contextlib

# Mock tiktoken
_tk = types.ModuleType('tiktoken')
class _MockEnc:
    def encode(self, s): return list(range(len(s)))
    def decode(self, tokens): return ''
_tk.get_encoding = lambda _: _MockEnc()
sys.modules['tiktoken'] = _tk

# Mock claude_agent_sdk
_sdk = types.ModuleType('claude_agent_sdk')
for _n in ('AssistantMessage', 'ClaudeAgentOptions', 'ResultMessage', 'TextBlock', 'query'):
    setattr(_sdk, _n, type(_n, (), {}))
sys.modules['claude_agent_sdk'] = _sdk

# Mock skills.github
_skills_pkg = types.ModuleType('skills')
sys.modules['skills'] = _skills_pkg
_gh = types.ModuleType('skills.github')

class _Job:
    def __init__(self, conclusion='failure'):
        self.conclusion = conclusion
        self.id = 1
        self.name = 'test'
        self.workflow_name = 'ci'
        self.html_url = 'https://example.com'
        self.steps = []

class _JobStep: pass
class _GitHubClient: pass
def _get_token(): return 'fake'

_gh.Job = _Job
_gh.JobStep = _JobStep
_gh.GitHubClient = _GitHubClient
_gh.get_github_token = _get_token
sys.modules['skills.github'] = _gh

# Import the module under test
sys.path.insert(0, '/workspace/mlflow/.claude/skills/src')
import importlib.util as _ilu
_spec = _ilu.spec_from_file_location(
    'analyze_ci',
    '/workspace/mlflow/.claude/skills/src/skills/commands/analyze_ci.py',
)
mod = _ilu.module_from_spec(_spec)
sys.modules['analyze_ci'] = mod
_spec.loader.exec_module(mod)
"""


def _run_behavioral_test(script: str) -> subprocess.CompletedProcess:
    """Run a Python script that imports analyze_ci with mocked deps."""
    return subprocess.run(
        ["python3", "-c", _MOCK_SETUP + script],
        capture_output=True, text=True, timeout=30,
    )


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
    """A compiled _PATTERN regex in the module must match bare workflow run URLs."""
    r = _run_behavioral_test(r"""
import re

# Find all compiled _PATTERN regex objects exported by the module
patterns = {name: val for name, val in vars(mod).items()
            if isinstance(val, re.Pattern) and name.endswith('_PATTERN')}

run_urls = [
    "https://github.com/mlflow/mlflow/actions/runs/22626454465",
    "https://github.com/owner/repo/actions/runs/99999",
    "https://github.com/a/b/actions/runs/1",
]
for url in run_urls:
    matching = [name for name, pat in patterns.items() if pat.search(url)]
    assert matching, f"No _PATTERN regex matches run URL: {url}"
    # Verify the pattern captures the run ID as a digit string in group 2
    for name in matching:
        m = patterns[name].search(url)
        assert m.group(2).isdigit(), f"group(2) should be run ID digits, got: {m.group(2)}"
""")
    assert r.returncode == 0, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_run_url_pattern_excludes_job_urls():
    """The pattern(s) matching run URLs must NOT match job URLs."""
    r = _run_behavioral_test(r"""
import re

patterns = {name: val for name, val in vars(mod).items()
            if isinstance(val, re.Pattern) and name.endswith('_PATTERN')}

# Identify which patterns match bare run URLs
run_url = "https://github.com/mlflow/mlflow/actions/runs/12345"
run_matching = [name for name, pat in patterns.items() if pat.search(run_url)]
assert run_matching, "No _PATTERN regex matches bare run URLs"

# Those same patterns must NOT match job URLs (which have /job/N suffix)
job_urls = [
    "https://github.com/mlflow/mlflow/actions/runs/12345/job/67890",
    "https://github.com/owner/repo/actions/runs/1/job/2",
]
for name in run_matching:
    pat = patterns[name]
    for job_url in job_urls:
        assert pat.search(job_url) is None, (
            f"Pattern {name} incorrectly matches job URL: {job_url}"
        )
""")
    assert r.returncode == 0, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_resolve_urls_dispatches_run_pattern():
    """resolve_urls must accept a bare run URL and fetch jobs for the run."""
    r = _run_behavioral_test(r"""
import asyncio, io, contextlib

class _AsyncIter:
    def __init__(self, items):
        self._items = iter(items)
    def __aiter__(self): return self
    async def __anext__(self):
        try: return next(self._items)
        except StopIteration: raise StopAsyncIteration

class MockClient:
    def __init__(self): self.calls = []
    async def get_job(self, owner, repo, job_id):
        self.calls.append(('get_job', owner, repo, job_id))
        return _Job()
    def get_jobs(self, owner, repo, run_id):
        self.calls.append(('get_jobs', owner, repo, run_id))
        return _AsyncIter([_Job()])

client = MockClient()
stderr_buf = io.StringIO()
with contextlib.redirect_stderr(stderr_buf):
    try:
        result = asyncio.run(mod.resolve_urls(
            client,
            ['https://github.com/mlflow/mlflow/actions/runs/12345'],
        ))
    except SystemExit:
        err = stderr_buf.getvalue()
        assert False, f"resolve_urls rejected run URL as invalid: {err}"

# Must have called the jobs-fetching API (not single-job get_job)
assert any(c[0] == 'get_jobs' for c in client.calls), (
    f"Expected get_jobs to be called for run URL, got: {client.calls}"
)
assert len(result) > 0, "resolve_urls should return jobs for a valid run URL"
""")
    assert r.returncode == 0, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_help_text_mentions_run_url():
    """Help text or error messages must mention run URL as a valid format."""
    r = _run_behavioral_test(r"""
import argparse, asyncio, io, contextlib

# Check argparse help text from register()
parser = argparse.ArgumentParser()
subs = parser.add_subparsers()
mod.register(subs)
help_text = subs.choices['analyze-ci'].format_help().lower()

# Check error messages from resolve_urls on an invalid URL
class _NoopClient: pass
stderr_buf = io.StringIO()
with contextlib.redirect_stderr(stderr_buf):
    try:
        asyncio.run(mod.resolve_urls(_NoopClient(), ['https://example.com/invalid']))
    except SystemExit:
        pass
error_text = stderr_buf.getvalue().lower()

combined = help_text + ' ' + error_text
# At least one of help text or error message must mention run URL
mentions_run = 'run url' in combined or 'workflow run' in combined
assert mentions_run, (
    f"Neither help text nor error messages mention run URL format.\n"
    f"Help: {help_text}\nError: {error_text}"
)
""")
    assert r.returncode == 0, f"Test failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_skill_md_documents_run_urls():
    """SKILL.md must document workflow run URL as a supported input format."""
    r = subprocess.run(
        ["python3", "-c", r"""
content = open('/workspace/mlflow/.claude/skills/analyze-ci/SKILL.md').read()
assert 'run' in content.lower(), 'SKILL.md should mention workflow runs'
assert 'actions/runs/' in content, 'SKILL.md should show a run URL example'
lines = content.split('\n')
has_bare_run_url = any('actions/runs/' in line and '/job/' not in line for line in lines)
assert has_bare_run_url, (
    'SKILL.md must have a bare run URL example (actions/runs/N without /job/)'
)
"""],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"SKILL.md check failed:\n{r.stdout}\n{r.stderr}"


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
def test_repo_ruff_check_all_commands():
    """Ruff linting passes on all command files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.2", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    cmds_dir = Path(REPO) / ".claude/skills/src/skills/commands"
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", str(cmds_dir)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed on commands:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_check_github_module():
    """Ruff linting passes on github module (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.2", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    github_dir = Path(REPO) / ".claude/skills/src/skills/github"
    r = subprocess.run(
        ["python3", "-m", "ruff", "check", str(github_dir)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff check failed on github module:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_format_check():
    """Ruff format check passes on all skills files (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff==0.15.2", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    skills_dir = Path(REPO) / ".claude/skills/src/skills"
    r = subprocess.run(
        ["python3", "-m", "ruff", "format", "--check", str(skills_dir)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stdout}\n{r.stderr}"


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


# [repo_tests] pass_to_pass
def test_repo_mlflow_typo_check():
    """MLflow typo checker passes on modified files (pass_to_pass)."""
    r = subprocess.run(
        ["bash", f"{REPO}/dev/mlflow-typo.sh", str(ANALYZE_CI)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Typo check failed for analyze_ci.py:\n{r.stdout}\n{r.stderr}"

    r = subprocess.run(
        ["bash", f"{REPO}/dev/mlflow-typo.sh", str(SKILL_MD)],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Typo check failed for SKILL.md:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_syntax_check_all_commands():
    """All command files parse without syntax errors (pass_to_pass)."""
    cmds_dir = Path(REPO) / ".claude/skills/src/skills/commands"
    for py_file in cmds_dir.glob("*.py"):
        if py_file.name == "__init__.py":
            continue
        r = subprocess.run(
            ["python3", "-c", f"import py_compile; py_compile.compile('{py_file}', doraise=True)"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {py_file.name}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_syntax_check_github_module():
    """All github module files parse without syntax errors (pass_to_pass)."""
    github_dir = Path(REPO) / ".claude/skills/src/skills/github"
    for py_file in github_dir.glob("*.py"):
        r = subprocess.run(
            ["python3", "-c", f"import py_compile; py_compile.compile('{py_file}', doraise=True)"],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax error in {py_file.name}:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_analyze_ci_patterns_valid():
    """Regex patterns in analyze_ci.py are valid and compile (pass_to_pass)."""
    source = ANALYZE_CI.read_text()
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

    # Verify key patterns exist and compile
    required_patterns = ["PR_URL_PATTERN", "JOB_URL_PATTERN"]
    for pat_name in required_patterns:
        assert pat_name in patterns, f"Required pattern {pat_name} not found"
        # Verify it compiles as valid regex
        try:
            re.compile(patterns[pat_name])
        except re.error as e:
            raise AssertionError(f"Invalid regex in {pat_name}: {e}")


# [repo_tests] pass_to_pass
def test_repo_skill_md_frontmatter_valid():
    """SKILL.md has valid YAML frontmatter with required fields (pass_to_pass)."""
    content = SKILL_MD.read_text()

    # Check frontmatter delimiters
    assert content.startswith("---"), "SKILL.md must start with --- frontmarker"

    # Extract frontmatter
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must have complete frontmatter (--- ... ---)"

    # Parse key-value pairs
    required_fields = ["name", "description"]
    frontmatter = parts[1].strip()
    assert frontmatter, "Frontmatter should not be empty"
    found_fields = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            found_fields[key.strip()] = val.strip()

    for field in required_fields:
        assert field in found_fields, f"Frontmatter missing required field: {field}"



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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_macos_run_pre_commit():
    """pass_to_pass | CI job 'lint-macos' → step 'Run pre-commit'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pre-commit run --all-files'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run pre-commit' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_macos_test_clint():
    """pass_to_pass | CI job 'lint-macos' → step 'Test clint'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-sync pytest dev/clint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test clint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_macos_check_function_signatures():
    """pass_to_pass | CI job 'lint-macos' → step 'Check function signatures'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run --no-project dev/check_function_signatures.py'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check function signatures' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_tests_run_fs2db_pytest_tests():
    """pass_to_pass | CI job 'unit-tests' → step 'Run fs2db pytest tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run pytest tests/store/fs2db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run fs2db pytest tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_ui():
    """pass_to_pass | CI job 'build' → step 'Build UI'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn && yarn build'], cwd=os.path.join(REPO, 'mlflow/server/js'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build UI' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")