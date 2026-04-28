"""
Task: lotti-due-date-display-readme
Repo: matthiasn/lotti @ 88b2b0e5c762e01aeeefbf27dcc339c05a63a0a4
PR:   2565

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = "/workspace/lotti"


def _analyze_dart(script: str, filepath: str) -> dict:
    """Run a Python analysis script against a Dart file, return JSON result."""
    r = subprocess.run(
        ["python3", "-c", script, filepath],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        return {"ok": False, "err": r.stderr.strip() or f"exit {r.returncode}"}
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        return {"ok": False, "err": f"bad output: {r.stdout[:200]}"}


# ---------------------------------------------------------------------------
# pass_to_pass — syntax / structural checks
# ---------------------------------------------------------------------------


def test_syntax_check():
    """Modified Dart files have balanced braces and parens."""
    for rel in [
        "lib/features/journal/ui/widgets/list_cards/modern_task_card.dart",
        "lib/features/tasks/ui/header/task_due_date_wrapper.dart",
    ]:
        src = Path(f"{REPO}/{rel}").read_text()
        assert src.count("{") == src.count("}"), (
            f"{rel}: unbalanced braces ({src.count('{')} open vs {src.count('}')} close)"
        )
        assert src.count("(") == src.count(")"), (
            f"{rel}: unbalanced parens ({src.count('(')} open vs {src.count(')')} close)"
        )


def test_modified_dart_files_exist():
    """Modified Dart source files exist and are non-empty (pass_to_pass)."""
    for rel in [
        "lib/features/journal/ui/widgets/list_cards/modern_task_card.dart",
        "lib/features/tasks/ui/header/task_due_date_wrapper.dart",
    ]:
        path = Path(f"{REPO}/{rel}")
        assert path.exists(), f"{rel}: file not found"
        content = path.read_text()
        assert len(content) > 0, f"{rel}: file is empty"
        assert "class " in content, f"{rel}: no class definitions found"


def test_test_files_exist_for_modified():
    """Test files exist for the modified Dart components (pass_to_pass)."""
    for rel in [
        "test/features/journal/ui/widgets/list_cards/modern_task_card_test.dart",
        "test/features/tasks/ui/header/task_due_date_wrapper_test.dart",
    ]:
        path = Path(f"{REPO}/{rel}")
        assert path.exists(), f"{rel}: test file not found"
        content = path.read_text()
        assert len(content) > 0, f"{rel}: test file is empty"
        assert "testWidgets" in content or "test(" in content or "group(" in content, (
            f"{rel}: no test definitions found"
        )


def _ensure_yaml():
    """Ensure pyyaml is installed."""
    try:
        import yaml  # noqa: F401
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml", "-q"], check=True)


def test_pubspec_yaml_valid():
    """Repo's pubspec.yaml is valid YAML (pass_to_pass)."""
    _ensure_yaml()
    import yaml
    pubspec_path = Path(f"{REPO}/pubspec.yaml")
    assert pubspec_path.exists(), "pubspec.yaml not found"
    content = pubspec_path.read_text()
    # Should parse without error
    data = yaml.safe_load(content)
    assert data is not None, "pubspec.yaml is empty or invalid"
    assert "name" in data, "pubspec.yaml missing 'name' field"
    assert data["name"] == "lotti", f"Expected name 'lotti', got '{data.get('name')}'"


def test_analysis_options_yaml_valid():
    """Repo's analysis_options.yaml is valid YAML (pass_to_pass)."""
    _ensure_yaml()
    import yaml
    opts_path = Path(f"{REPO}/analysis_options.yaml")
    assert opts_path.exists(), "analysis_options.yaml not found"
    content = opts_path.read_text()
    # Should parse without error
    data = yaml.safe_load(content)
    assert data is not None, "analysis_options.yaml is empty or invalid"


# ---------------------------------------------------------------------------
# pass_to_pass — repo CI tests (enriched)
# These run actual CI commands from the repo's workflows
# ---------------------------------------------------------------------------


def test_repo_flake8_manifest_tool():
    """Python linting passes for manifest_tool (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install may "fail" if already installed, that's ok
    r = subprocess.run(
        [
            "flake8",
            ".",
            "--count",
            "--max-line-length=120",
            "--extend-ignore=E203,W503",
        ],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/flatpak/manifest_tool",
    )
    assert r.returncode == 0, f"Flake8 linting failed:\n{r.stdout}\n{r.stderr}"


def test_repo_pytest_manifest_tool():
    """Repo's manifest_tool Python tests pass (pass_to_pass)."""
    # Install required dependencies
    r = subprocess.run(
        ["pip", "install", "pytest", "pyyaml", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Run the manifest_tool tests
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=f"{REPO}/flatpak/manifest_tool",
    )
    assert r.returncode == 0, f"Pytest failed:\n{r.stdout[-2000:]}\n{r.stderr[-1000:]}"


def test_repo_dart_syntax_core_files():
    """Core modified Dart files have valid syntax (pass_to_pass)."""
    # Use py_compile equivalent approach - check for balanced braces/parens
    for rel in [
        "lib/features/journal/ui/widgets/list_cards/modern_task_card.dart",
        "lib/features/tasks/ui/header/task_due_date_wrapper.dart",
    ]:
        src = Path(f"{REPO}/{rel}").read_text()
        # Check for basic syntax markers
        assert src.count("{") == src.count("}"), f"{rel}: unbalanced braces"
        assert src.count("(") == src.count(")"), f"{rel}: unbalanced parens"
        # Check for valid Dart structure indicators
        assert "class " in src, f"{rel}: no class definitions found"
        assert "import " in src, f"{rel}: no import statements found"




def test_repo_metainfo_xml_valid():
    """Flatpak metainfo.xml is valid XML (pass_to_pass)."""
    import xml.etree.ElementTree as ET

    metainfo_path = Path(f"{REPO}/flatpak/com.matthiasn.lotti.metainfo.xml")
    assert metainfo_path.exists(), "metainfo.xml not found"
    try:
        tree = ET.parse(metainfo_path)
        root = tree.getroot()
        assert root.tag == "component", f"Expected root tag 'component', got '{root.tag}'"
        # Check required fields exist
        id_elem = root.find("id")
        assert id_elem is not None, "metainfo.xml missing <id> element"
        assert id_elem.text == "com.matthiasn.lotti", f"Expected id 'com.matthiasn.lotti', got '{id_elem.text}'"
    except ET.ParseError as e:
        raise AssertionError(f"metainfo.xml is invalid XML: {e}")


def test_repo_flathub_source_yaml_valid():
    """Flatpak source YAML is valid (pass_to_pass)."""
    _ensure_yaml()
    import yaml

    source_path = Path(f"{REPO}/flatpak/com.matthiasn.lotti.source.yml")
    assert source_path.exists(), "source.yml not found"
    try:
        content = source_path.read_text()
        data = yaml.safe_load(content)
        assert data is not None, "source.yml is empty or invalid"
        assert "app-id" in data, "source.yml missing 'app-id' field"
        assert data["app-id"] == "com.matthiasn.lotti", f"Expected id 'com.matthiasn.lotti', got '{data.get('id')}'"
    except yaml.YAMLError as e:
        raise AssertionError(f"source.yml is invalid YAML: {e}")


def test_repo_manifest_tool_validation_tests():
    """Manifest tool validation tests pass (pass_to_pass)."""
    # Install dependencies
    r = subprocess.run(
        ["pip", "install", "pytest", "pyyaml", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Run only the validation tests
    r = subprocess.run(
        ["python3", "-m", "pytest", "tests/test_validation.py", "-v", "--tb=short"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=f"{REPO}/flatpak/manifest_tool",
        env={**subprocess.os.environ, "PYTHONPATH": f"{REPO}/flatpak"},
    )
    assert r.returncode == 0, f"Validation tests failed:\n{r.stdout[-1500:]}\n{r.stderr[-500:]}"

# ---------------------------------------------------------------------------
# fail_to_pass — behavioral tests
# ---------------------------------------------------------------------------

# Analysis script for task card: verifies due date is hidden for completed/rejected
# by checking that completion status (!isCompleted) gates the hasDueDate computation
# OR that there's an early return when completed before the date is shown.
_ANALYZE_CARD = r"""
import json, re, sys

src = open(sys.argv[1]).read()

# Find the _buildDateRow method body
m = re.search(r'Widget _buildDateRow\(.*?\{', src)
if not m:
    print(json.dumps({"ok": False, "err": "_buildDateRow not found"}))
    sys.exit(0)

# Extract method body by counting braces
depth = 1
body_start = m.end()
body_end = len(src)
for i in range(body_start, len(src)):
    if src[i] == '{':
        depth += 1
    elif src[i] == '}':
        depth -= 1
        if depth == 0:
            body_end = i
            break

body = src[body_start:body_end]

# Check 1: hasDueDate computation must be gated by !isCompleted
# This accepts: hasDueDate = ... && !isCompleted, or hasDueDate = ... && (isCompleted ? false : ...)
# We check for the negation pattern (!isCompleted or isCompleted ? false) in a hasDueDate expression
has_due_gated = False
for line in body.split('\n'):
    s = line.strip()
    # Look for hasDueDate assignment with a due-related expression
    if ('hasDueDate' in s or re.search(r'due\s*!=\s*null', s)) and '=' in s:
        # Check for negation of isCompleted: either !isCompleted or isCompleted ? false
        if re.search(r'!.*(?:isCompleted|isComplete|isDone|isFinished)', s) or \
           re.search(r'isCompleted\s*\?\s*false', s):
            has_due_gated = True
            break

if not has_due_gated:
    # Check 2: If no gating in hasDueDate expression, there must be an early return
    # when isCompleted is true, BEFORE any date-displaying widget is built
    early_return = False
    for line in body.split('\n'):
        s = line.strip()
        # Look for early return/conditional return when isCompleted is true
        if re.search(r'if\s*\(\s*!?(?:isCompleted|isComplete|isDone|isFinished)', s):
            # Check this leads to returning an empty/shrink widget
            early_return = True
            break

    if not early_return:
        print(json.dumps({
            "ok": False,
            "err": "Completion status must gate the due date display (either in hasDueDate computation or via early return)"
        }))
        sys.exit(0)

# Check 3: Must reference TaskDone or TaskRejected in the method (for status check)
if not re.search(r'(TaskDone|TaskRejected)', body):
    print(json.dumps({"ok": False, "err": "Must reference TaskDone or TaskRejected for completion check"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
"""


def test_task_card_hides_due_date_for_completed():
    """ModernTaskCard._buildDateRow skips due date display for completed/rejected tasks."""
    card = f"{REPO}/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart"
    result = _analyze_dart(_ANALYZE_CARD, card)
    assert result.get("ok"), result.get("err", "Unknown error")


# Analysis script for wrapper: verifies urgency styling is disabled for completed/rejected
# by checking that isUrgent is gated by !isCompleted and urgentColor returns null when completed
_ANALYZE_WRAPPER = r"""
import json, re, sys

src = open(sys.argv[1]).read()

# Check 1: Must import task.dart for TaskDone/TaskRejected types
if not re.search(r"import.*package:lotti/classes/task\.dart", src):
    print(json.dumps({"ok": False, "err": "Missing import for lotti/classes/task.dart"}))
    sys.exit(0)

# Check 2: Must reference TaskDone or TaskRejected for completion status
if not re.search(r'(TaskDone|TaskRejected)', src):
    print(json.dumps({"ok": False, "err": "Must reference TaskDone or TaskRejected for status check"}))
    sys.exit(0)

# Check 3: isUrgent must be gated by !isCompleted (negation pattern)
# This accepts: isUrgent: !isCompleted && status.isUrgent, or isUrgent: isCompleted ? false : status.isUrgent
is_urgent_gated = False
for line in src.split('\n'):
    s = line.strip()
    if 'isUrgent' in s and ':' in s and '!' not in s.split(':')[0]:
        # Look for negation pattern: !isCompleted && ...isUrgent OR isCompleted ? false
        if re.search(r'!.*(?:isCompleted|isComplete|isDone|isFinished).*isUrgent', s) or \
           re.search(r'isCompleted\s*\?\s*false', s):
            is_urgent_gated = True
            break

if not is_urgent_gated:
    print(json.dumps({"ok": False, "err": "isUrgent must be gated by completion status (!isCompleted)"}))
    sys.exit(0)

# Check 4: urgentColor must return null when task is completed (ternary: isCompleted ? null : ...)
urgent_color_gated = False
for line in src.split('\n'):
    s = line.strip()
    if 'urgentColor' in s and ':' in s:
        # Look for ternary with null when completed: isCompleted ? null : ...
        if re.search(r'isCompleted\s*\?\s*null\s*:', s):
            urgent_color_gated = True
            break

if not urgent_color_gated:
    print(json.dumps({"ok": False, "err": "urgentColor must return null for completed tasks (isCompleted ? null : ...)"}))
    sys.exit(0)

print(json.dumps({"ok": True}))
"""


def test_due_date_wrapper_disables_urgency():
    """TaskDueDateWrapper disables urgency styling for completed/rejected tasks."""
    wrapper = f"{REPO}/lib/features/tasks/ui/header/task_due_date_wrapper.dart"
    result = _analyze_dart(_ANALYZE_WRAPPER, wrapper)
    assert result.get("ok"), result.get("err", "Unknown error")


def test_readme_updated():
    """README references live 'Meet Lotti' blog series with link."""
    readme = Path(f"{REPO}/README.md").read_text()
    assert "Coming Soon: Deep Dive" not in readme, (
        "README still says 'Coming Soon: Deep Dive Series' — "
        "should be updated to reflect the launched blog series"
    )
    assert "meet-lotti" in readme.lower(), (
        "README should reference the 'Meet Lotti' blog series"
    )
    assert "matthiasnehlsen.substack.com/p/meet-lotti" in readme, (
        "README should link to the Meet Lotti blog post on Substack"
    )


def test_changelog_documents_changes():
    """CHANGELOG documents due date visibility changes for completed/rejected tasks."""
    changelog = Path(f"{REPO}/CHANGELOG.md").read_text()
    lower = changelog.lower()
    assert "due date visibility refinements" in lower, (
        "CHANGELOG should document the 'Due Date Visibility Refinements' changes "
        "for completed and rejected tasks"
    )
    assert "hidden on task cards for completed" in lower or "grayed-out" in lower, (
        "CHANGELOG should mention that due dates are hidden on cards "
        "or shown grayed-out for completed/rejected tasks"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_type_check_run_mypy_type_checking():
    """pass_to_pass | CI job 'type-check' → step 'Run MyPy Type Checking'"""
    # CI workflow uses "mypy . --ignore-missing-imports || true" with
    # continue-on-error: true — type warnings are informational, not blocking.
    r = subprocess.run(
        ["bash", "-lc", 'mypy . --ignore-missing-imports || true'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run MyPy Type Checking' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")