"""
Task: posthog-hogql-logs-system-tables
Repo: PostHog/posthog @ 51c06f3b577793a61dd32d10b5922d8b61393118
PR:   53525

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import ast
from pathlib import Path

REPO = "/workspace/posthog"
SYSTEM_PY = Path(REPO) / "posthog" / "hogql" / "database" / "schema" / "system.py"
SKILL_MD = Path(REPO) / "products" / "posthog_ai" / "skills" / "query-examples" / "SKILL.md"
GUIDELINES_MD = Path(REPO) / "products" / "posthog_ai" / "skills" / "query-examples" / "references" / "guidelines.md"
MODELS_LOGS_MD = Path(REPO) / "products" / "posthog_ai" / "skills" / "query-examples" / "references" / "models-logs.md"


def _run_in_venv(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run Python code in the repo context."""
    return subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) - syntax check
# ---------------------------------------------------------------------------

def test_system_py_syntax():
    """system.py must parse without syntax errors."""
    r = _run_in_venv(f"""
import ast, sys
try:
    ast.parse(open({str(SYSTEM_PY)!r}).read())
    print("OK")
except SyntaxError as e:
    print(f"SyntaxError: {{e}}", file=sys.stderr)
    sys.exit(1)
""")
    assert r.returncode == 0, f"system.py has syntax errors: {r.stderr}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - repo CI command tests
# ---------------------------------------------------------------------------

def test_system_py_structure_valid():
    """system.py has valid Python structure with expected classes."""
    r = _run_in_venv(f"""
import ast, sys

source = open({str(SYSTEM_PY)!r}).read()
tree = ast.parse(source)

# Check for SystemTables class
classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
if "SystemTables" not in classes:
    print("SystemTables class not found", file=sys.stderr)
    sys.exit(1)

# Check for PostgresTable calls (indicating table definitions)
has_postgres_table = False
for node in ast.walk(tree):
    if isinstance(node, ast.Call):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr
        if func_name == "PostgresTable":
            has_postgres_table = True
            break

if not has_postgres_table:
    print("No PostgresTable definitions found", file=sys.stderr)
    sys.exit(1)

print("OK")
""")
    assert r.returncode == 0, f"system.py structure invalid: {r.stderr}"


def test_system_py_imports_valid():
    """system.py has valid import statements."""
    r = _run_in_venv(f"""
import ast, sys

source = open({str(SYSTEM_PY)!r}).read()
tree = ast.parse(source)

# Check that imports are valid Python syntax
for node in ast.walk(tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            if not alias.name.replace(".", "").replace("_", "").isalnum():
                print(f"Invalid import: {{alias.name}}", file=sys.stderr)
                sys.exit(1)
    elif isinstance(node, ast.ImportFrom):
        if node.module and not node.module.replace(".", "").replace("_", "").isalnum():
            print(f"Invalid from import: {{node.module}}", file=sys.stderr)
            sys.exit(1)

print("OK")
""")
    assert r.returncode == 0, f"system.py has invalid imports: {r.stderr}"


def test_markdown_files_parseable():
    """Markdown files are parseable and have expected structure."""
    # Check SKILL.md
    r1 = _run_in_venv(f"""
import sys
content = open({str(SKILL_MD)!r}).read()
if len(content) < 100:
    print("SKILL.md too short", file=sys.stderr)
    sys.exit(1)
if "# " not in content:
    print("SKILL.md missing heading", file=sys.stderr)
    sys.exit(1)
print("SKILL.md OK")
""")
    assert r1.returncode == 0, f"SKILL.md invalid: {r1.stderr}"

    # Check guidelines.md
    r2 = _run_in_venv(f"""
import sys
content = open({str(GUIDELINES_MD)!r}).read()
if len(content) < 100:
    print("guidelines.md too short", file=sys.stderr)
    sys.exit(1)
if "# " not in content:
    print("guidelines.md missing heading", file=sys.stderr)
    sys.exit(1)
print("guidelines.md OK")
""")
    assert r2.returncode == 0, f"guidelines.md invalid: {r2.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - code behavioral tests
# ---------------------------------------------------------------------------

def test_logs_views_table_defined():
    """logs_views must be defined as a PostgresTable with correct properties."""
    r = _run_in_venv(f"""
import sys, ast, json

source = open({str(SYSTEM_PY)!r}).read()
tree = ast.parse(source)

# Find the logs_views assignment (could be AnnAssign for annotated assignments)
found = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "logs_views":
                found = node.value
                break
        if found:
            break
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == "logs_views":
            found = node.value
            break

if not found:
    print("logs_views assignment not found", file=sys.stderr)
    sys.exit(1)

# Verify it is a PostgresTable call
if not isinstance(found, ast.Call):
    print("logs_views is not a Call expression", file=sys.stderr)
    sys.exit(1)

func_name = ""
if isinstance(found.func, ast.Name):
    func_name = found.func.id
elif isinstance(found.func, ast.Attribute):
    func_name = found.func.attr

if func_name != "PostgresTable":
    print(f"logs_views is not a PostgresTable: {{func_name}}", file=sys.stderr)
    sys.exit(1)

# Extract keyword arguments
kwargs = {{}}
for kw in found.keywords:
    if isinstance(kw.value, ast.Constant):
        kwargs[kw.arg] = kw.value.value
    elif isinstance(kw.value, ast.Dict):
        # For fields dict, get the keys
        if kw.arg == "fields":
            field_keys = []
            for k in kw.value.keys:
                if isinstance(k, ast.Constant):
                    field_keys.append(k.value)
            kwargs[kw.arg] = field_keys

result = {{
    "name": kwargs.get("name"),
    "postgres_table_name": kwargs.get("postgres_table_name"),
    "access_scope": kwargs.get("access_scope"),
    "fields": kwargs.get("fields", [])
}}
print(json.dumps(result))
""")
    assert r.returncode == 0, f"logs_views check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["name"] == "logs_views", f"Wrong name: {data['name']}"
    assert data["postgres_table_name"] == "logs_logsview", f"Wrong postgres_table_name: {data['postgres_table_name']}"
    assert data["access_scope"] == "logs", f"Wrong access_scope: {data['access_scope']}"
    required = ["id", "team_id", "short_id", "name", "filters", "created_at", "updated_at"]
    for field in required:
        assert field in data["fields"], f"logs_views missing field: {field}"


def test_logs_alerts_table_defined():
    """logs_alerts must be defined as a PostgresTable with alert-specific properties."""
    r = _run_in_venv(f"""
import sys, ast, json

source = open({str(SYSTEM_PY)!r}).read()
tree = ast.parse(source)

# Find the logs_alerts assignment (could be AnnAssign for annotated assignments)
found = None
for node in ast.walk(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "logs_alerts":
                found = node.value
                break
        if found:
            break
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id == "logs_alerts":
            found = node.value
            break

if not found:
    print("logs_alerts assignment not found", file=sys.stderr)
    sys.exit(1)

if not isinstance(found, ast.Call):
    print("logs_alerts is not a Call expression", file=sys.stderr)
    sys.exit(1)

func_name = ""
if isinstance(found.func, ast.Name):
    func_name = found.func.id
elif isinstance(found.func, ast.Attribute):
    func_name = found.func.attr

if func_name != "PostgresTable":
    print(f"logs_alerts is not a PostgresTable: {{func_name}}", file=sys.stderr)
    sys.exit(1)

# Extract keyword arguments
kwargs = {{}}
for kw in found.keywords:
    if isinstance(kw.value, ast.Constant):
        kwargs[kw.arg] = kw.value.value
    elif isinstance(kw.value, ast.Dict):
        if kw.arg == "fields":
            field_keys = []
            for k in kw.value.keys:
                if isinstance(k, ast.Constant):
                    field_keys.append(k.value)
            kwargs[kw.arg] = field_keys

result = {{
    "name": kwargs.get("name"),
    "postgres_table_name": kwargs.get("postgres_table_name"),
    "access_scope": kwargs.get("access_scope"),
    "fields": kwargs.get("fields", [])
}}
print(json.dumps(result))
""")
    assert r.returncode == 0, f"logs_alerts check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["name"] == "logs_alerts", f"Wrong name: {data['name']}"
    assert data["postgres_table_name"] == "logs_logsalertconfiguration", f"Wrong postgres_table_name: {data['postgres_table_name']}"
    assert data["access_scope"] == "logs", f"Wrong access_scope: {data['access_scope']}"
    # Check alert-specific fields
    alert_fields = ["threshold_count", "threshold_operator", "window_minutes",
                    "check_interval_minutes", "state", "evaluation_periods"]
    for field in alert_fields:
        assert field in data["fields"], f"logs_alerts missing field: {field}"


def test_logs_tables_registered_in_system_tables():
    """SystemTables.children dict must include logs_alerts and logs_views entries."""
    r = _run_in_venv(f"""
import sys, ast, json

source = open({str(SYSTEM_PY)!r}).read()
tree = ast.parse(source)

# Find the SystemTables class and extract children dict keys
children_keys = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "SystemTables":
        for item in node.body:
            if isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                if item.target.id == "children":
                    if isinstance(item.value, ast.Dict):
                        for k in item.value.keys:
                            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                                children_keys.append(k.value)

print(json.dumps({{"children": children_keys}}))
""")
    assert r.returncode == 0, f"SystemTables analysis failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    children = set(data["children"])
    assert "logs_alerts" in children, f"SystemTables.children missing 'logs_alerts', has: {children}"
    assert "logs_views" in children, f"SystemTables.children missing 'logs_views', has: {children}"


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) - config/documentation update tests
# ---------------------------------------------------------------------------

def test_skill_md_references_logs():
    """SKILL.md must list a Logs reference in its data schema section."""
    content = SKILL_MD.read_text()
    assert "models-logs" in content, \
        "SKILL.md should reference models-logs.md in its data schema list"
    assert "[Logs]" in content or "[logs]" in content.lower(), \
        "SKILL.md should have a [Logs] link entry"


def test_guidelines_lists_logs_tables():
    """guidelines.md must list system.logs_alerts and system.logs_views in the system data table."""
    content = GUIDELINES_MD.read_text()
    assert "system.logs_alerts" in content, \
        "guidelines.md should list system.logs_alerts in the system data table"
    assert "system.logs_views" in content, \
        "guidelines.md should list system.logs_views in the system data table"


def test_guidelines_references_logs_model():
    """guidelines.md System Models Reference must link to the logs reference doc."""
    content = GUIDELINES_MD.read_text()
    assert "models-logs" in content, \
        "guidelines.md should link to models-logs reference doc"


def test_models_logs_reference_created():
    """models-logs.md must exist and document both system.logs_views and system.logs_alerts."""
    assert MODELS_LOGS_MD.exists(), \
        f"models-logs.md not found at {MODELS_LOGS_MD}"
    content = MODELS_LOGS_MD.read_text()
    assert "logs_views" in content, \
        "models-logs.md should document system.logs_views"
    assert "logs_alerts" in content or "LogsAlertConfiguration" in content, \
        "models-logs.md should document system.logs_alerts"
    assert "LogsView" in content or "logs_views" in content, \
        "models-logs.md should document the LogsView table"
    # Must have meaningful content, not just a placeholder
    assert len(content) > 200, \
        f"models-logs.md is too short ({len(content)} chars) - needs real documentation"
