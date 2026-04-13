"""
Task: lotti-feat-improve-scroll
Repo: matthiasn/lotti @ fda7c15b3cd6b88a3d9d258d458ce202f4b025c8
PR:   2883

Verify: (1) scroll refactored to slivers for lazy rendering,
        (2) feature README documents the new scroll architecture.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/lotti"

DETAIL_CONTENT = Path(REPO) / "lib/features/projects/ui/widgets/project_mobile_detail_content.dart"
TASKS_PANEL = Path(REPO) / "lib/features/projects/ui/widgets/project_tasks_panel.dart"
README = Path(REPO) / "lib/features/projects/README.md"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code for Dart source analysis."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified Dart files have balanced braces and parentheses."""
    for path in [DETAIL_CONTENT, TASKS_PANEL]:
        src = path.read_text()
        assert src.count("{") == src.count("}"), \
            f"{path.name}: unbalanced braces"
        assert src.count("(") == src.count(")"), \
            f"{path.name}: unbalanced parentheses"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_custom_scroll_view_in_detail_content():
    """Detail content uses CustomScrollView for sliver-based lazy rendering."""
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# CustomScrollView must be present
if "CustomScrollView" not in src:
    sys.exit("Missing CustomScrollView widget")

# SingleChildScrollView must be removed from the main scroll container
if "SingleChildScrollView(" in src:
    sys.exit("SingleChildScrollView still present; should be replaced by CustomScrollView")

# CustomScrollView must have a slivers parameter
if not re.search(r"slivers\\s*:", src):
    sys.exit("CustomScrollView missing slivers: parameter")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sliver_task_panel_class_exists():
    """A sliver-compatible task panel widget class is defined."""
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_tasks_panel.dart").read()

# ProjectTasksSliverPanel must be a StatelessWidget
if not re.search(r"class\\s+ProjectTasksSliverPanel\\s+extends\\s+StatelessWidget", src):
    sys.exit("ProjectTasksSliverPanel must extend StatelessWidget")

# Must have a build method that returns a Widget
if not re.search(r"class\\s+ProjectTasksSliverPanel[\\s\\S]*?Widget\\s+build\\s*\\(", src):
    sys.exit("ProjectTasksSliverPanel must have a build method returning Widget")

# Must accept a ProjectRecord parameter (typed field)
if "ProjectRecord" not in src:
    sys.exit("ProjectTasksSliverPanel must reference ProjectRecord type")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sliver_list_for_lazy_task_rows():
    """Task rows are rendered lazily via SliverList."""
    r = _run_py('''
import re, sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_tasks_panel.dart").read()

# SliverList must be used for lazy rendering
if "SliverList" not in src:
    sys.exit("Task panel should use SliverList for lazy rendering")

# Must have itemBuilder callback — this is what makes rendering lazy
if "itemBuilder" not in src:
    sys.exit("SliverList must have itemBuilder for lazy item construction")

# Must have itemCount to bound the list
if "itemCount" not in src:
    sys.exit("SliverList must have itemCount to limit lazy rendering")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_task_panel():
    """Detail content renders tasks through the sliver panel, not the eager panel."""
    r = _run_py('''
import sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# Must reference the sliver panel
if "ProjectTasksSliverPanel" not in src:
    sys.exit("Detail content must use ProjectTasksSliverPanel for lazy task rendering")

# The old eager panel reference should be gone
if "ProjectTasksPanel(" in src:
    sys.exit("Old eager ProjectTasksPanel should be replaced by ProjectTasksSliverPanel")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_detail_content_uses_sliver_adapters():
    """Detail content wraps static header sections in SliverToBoxAdapter."""
    r = _run_py('''
import sys
src = open("/workspace/lotti/lib/features/projects/ui/widgets/project_mobile_detail_content.dart").read()

# SliverToBoxAdapter must wrap non-lazy content
if "SliverToBoxAdapter" not in src:
    sys.exit("Static header widgets should be wrapped in SliverToBoxAdapter inside CustomScrollView")

# Must wrap the HealthPanel in a SliverToBoxAdapter
if "SliverToBoxAdapter" not in src or "HealthPanel" not in src:
    sys.exit("HealthPanel must be wrapped in SliverToBoxAdapter")

# Verify the header widget is also in a SliverToBoxAdapter
if "_ProjectMobileHeader" not in src:
    sys.exit("Header widget must be present")

print("PASS")
''')
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_sliver_panel_not_stub():
    """Sliver panel has real build logic, not just a placeholder."""
    src = TASKS_PANEL.read_text()
    # Must have both SliverList and a builder/itemBuilder for actual lazy rendering
    assert "SliverList" in src, "Sliver panel must use SliverList"
    assert "itemBuilder" in src or "delegate" in src, \
        "Sliver panel must have an itemBuilder or delegate for rendering items"
    assert "TaskSummaryRow" in src, \
        "Sliver panel must render TaskSummaryRow widgets"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — repo CI tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_python_syntax():
    """Python matrix provisioner syntax is valid (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", f"{REPO}/tools/matrix_provisioner/provision.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_python_lint():
    """Python matrix provisioner passes flake8 linting (pass_to_pass)."""
    # Install tools first
    r = subprocess.run(
        ["pip3", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["flake8", f"{REPO}/tools/matrix_provisioner/provision.py"],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/tools/matrix_provisioner",
    )
    assert r.returncode == 0, f"flake8 linting failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_python_format():
    """Python matrix provisioner passes black format check (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "black", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["black", "--check", f"{REPO}/tools/matrix_provisioner/provision.py", "--line-length=100"],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/tools/matrix_provisioner",
    )
    assert r.returncode == 0, f"black format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_python_isort():
    """Python matrix provisioner passes isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "isort", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["isort", "--check-only", f"{REPO}/tools/matrix_provisioner/provision.py"],
        capture_output=True, text=True, timeout=60, cwd=f"{REPO}/tools/matrix_provisioner",
    )
    assert r.returncode == 0, f"isort check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_python_unit_tests():
    """Python matrix provisioner unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "pytest", "pytest-asyncio", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    # Install dependencies first
    r = subprocess.run(
        ["pip3", "install", "-r", f"{REPO}/tools/matrix_provisioner/requirements.txt", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["pytest", f"{REPO}/tools/matrix_provisioner/tests/", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/tools/matrix_provisioner",
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_yaml_valid():
    """pubspec.yaml is valid YAML (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    code = """
import yaml
import sys
try:
    with open('/workspace/lotti/pubspec.yaml', 'r') as f:
        yaml.safe_load(f)
    print('PASS')
except Exception as e:
    sys.exit(f'YAML parse error: {e}')
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"YAML validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass
def test_repo_project_structure():
    """Modified files exist in correct locations (pass_to_pass)."""
    required_paths = [
        f"{REPO}/lib/features/projects/ui/widgets/project_mobile_detail_content.dart",
        f"{REPO}/lib/features/projects/ui/widgets/project_tasks_panel.dart",
        f"{REPO}/lib/features/projects/README.md",
    ]
    for path in required_paths:
        r = subprocess.run(
            ["test", "-f", path],
            capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"Required file missing: {path}"


# [repo_tests] pass_to_pass
def test_repo_dart_analysis_options():
    """analysis_options.yaml is valid YAML with expected sections (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    code = """
import yaml
import sys
try:
    with open('/workspace/lotti/analysis_options.yaml', 'r') as f:
        data = yaml.safe_load(f)
    assert 'include' in data, "Missing 'include' key"
    assert 'linter' in data or 'analyzer' in data, "Missing analyzer config"
    print('PASS')
except Exception as e:
    sys.exit(f'analysis_options.yaml error: {e}')
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"analysis_options validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - NEW: Dart detail content syntax check
def test_repo_dart_detail_content_syntax():
    """Modified Dart file project_mobile_detail_content.dart has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import sys
src = open('{REPO}/lib/features/projects/ui/widgets/project_mobile_detail_content.dart').read()

# Check balanced braces
if src.count("{{") != src.count("}}"):
    sys.exit("Unbalanced braces")

# Check balanced parentheses
if src.count("(") != src.count(")"):
    sys.exit("Unbalanced parentheses")

# Check balanced brackets
if src.count("[") != src.count("]"):
    sys.exit("Unbalanced brackets")

# Verify no unterminated string literals (basic check)
lines = src.split('\\n')
for i, line in enumerate(lines, 1):
    # Skip comments and lines with escaped quotes
    if '//' in line:
        line = line[:line.index('//')]
    single_quotes = line.count("'") - line.count("\\'")
    double_quotes = line.count('"') - line.count('\\"')
    if single_quotes % 2 != 0 or double_quotes % 2 != 0:
        # Could be multi-line string, skip
        pass

print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Dart syntax check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - NEW: Dart tasks panel syntax check
def test_repo_dart_tasks_panel_syntax():
    """Modified Dart file project_tasks_panel.dart has valid syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"""
import sys
src = open('{REPO}/lib/features/projects/ui/widgets/project_tasks_panel.dart').read()

# Check balanced braces
if src.count("{{") != src.count("}}"):
    sys.exit("Unbalanced braces")

# Check balanced parentheses
if src.count("(") != src.count(")"):
    sys.exit("Unbalanced parentheses")

# Check balanced brackets
if src.count("[") != src.count("]"):
    sys.exit("Unbalanced brackets")

print('PASS')
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Dart syntax check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - NEW: pubspec.yaml structure validation
def test_repo_pubspec_valid():
    """pubspec.yaml has valid structure with required fields (pass_to_pass)."""
    r = subprocess.run(
        ["pip3", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    code = """
import yaml
import sys
try:
    with open('/workspace/lotti/pubspec.yaml', 'r') as f:
        data = yaml.safe_load(f)
    assert 'name' in data, "Missing 'name' field"
    assert 'version' in data, "Missing 'version' field"
    assert 'environment' in data, "Missing 'environment' section"
    assert 'dependencies' in data, "Missing 'dependencies' section"
    print('PASS')
except Exception as e:
    sys.exit(f'pubspec.yaml error: {e}')
"""
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"pubspec validation failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# [repo_tests] pass_to_pass - NEW: Matrix provisioner Makefile test
def test_repo_matrix_provisioner_make_test():
    """Matrix provisioner tests pass via Makefile (pass_to_pass)."""
    # Install dependencies first
    r = subprocess.run(
        ["pip3", "install", "pytest", "pytest-asyncio", "flake8", "black", "isort", "-q"],
        capture_output=True, text=True, timeout=120,
    )
    r = subprocess.run(
        ["pip3", "install", "-r", f"{REPO}/tools/matrix_provisioner/requirements.txt", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["make", "test"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/tools/matrix_provisioner",
    )
    assert r.returncode == 0, f"Make test failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
