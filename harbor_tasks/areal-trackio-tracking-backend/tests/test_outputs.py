"""
Task: areal-trackio-tracking-backend
Repo: inclusionAI/AReaL @ 92c467e56bf17d730bd26855de33d5e4e13ba435
PR:   #1113

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This version uses subprocess.run() for behavioral (code-executing) tests
to reliably distinguish between base commit (broken) and gold commit (fixed).
"""

import ast
import re
import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO = "/workspace/AReaL"


def _exec_code_via_subprocess(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess by writing to a temp file.

    This avoids shell escaping issues and ensures clean execution.
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
            env={**os.environ, 'PYTHONPATH': REPO}
        )
        return result
    finally:
        os.unlink(tmp_path)


def _find_class_in_ast(tree, classname):
    """Find an ast.ClassDef node by name."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            return node
    return None


def _find_method_in_class(class_node, method_name):
    """Find a method (FunctionDef) in a ClassDef node."""
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            return item
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified files must parse without errors."""
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        src = Path(f"{REPO}/{fname}").read_text()
        compile(src, fname, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — TrackioConfig behavioral tests (with subprocess)
# ---------------------------------------------------------------------------

def test_trackio_config_exists_with_fields():
    """TrackioConfig class exists with mode, project, name, space_id fields."""
    code = '''
import re
from pathlib import Path
from dataclasses import fields

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r\'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)\'
match = re.search(pattern, src, re.DOTALL)

if not match:
    print("FAIL: Could not find TrackioConfig class in cli_args.py")
    exit(1)

ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\\n" + match.group(1), ns)
TrackioConfig = ns["TrackioConfig"]

field_names = {f.name for f in fields(TrackioConfig)}
required = {"mode", "project", "name", "space_id"}
missing = required - field_names
if missing:
    print(f"FAIL: Missing fields: {missing}")
    exit(1)
print("PASS: All required fields present")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_rejects_invalid_modes():
    """TrackioConfig rejects invalid mode values with ValueError."""
    code = '''
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r\'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)\'
match = re.search(pattern, src, re.DOTALL)

if not match:
    print("FAIL: Could not find TrackioConfig class")
    exit(1)

ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\\n" + match.group(1), ns)
TrackioConfig = ns["TrackioConfig"]

invalid_modes = ["invalid", "remote", "cloud", "off", "enabled", ""]
for bad_mode in invalid_modes:
    try:
        cfg = TrackioConfig(mode=bad_mode)
        print(f"FAIL: Accepted invalid mode={bad_mode!r}")
        exit(1)
    except ValueError:
        pass
    except Exception as e:
        print(f"FAIL: Wrong exception type for mode={bad_mode!r}: {type(e).__name__}")
        exit(1)
print("PASS: All invalid modes rejected with ValueError")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_accepts_valid_modes():
    """TrackioConfig accepts all three valid mode values."""
    code = '''
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r\'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)\'
match = re.search(pattern, src, re.DOTALL)

if not match:
    print("FAIL: Could not find TrackioConfig class")
    exit(1)

ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\\n" + match.group(1), ns)
TrackioConfig = ns["TrackioConfig"]

for mode in ("disabled", "online", "local"):
    cfg = TrackioConfig(mode=mode)
    if cfg.mode != mode:
        print(f"FAIL: Expected mode={mode!r}, got {cfg.mode!r}")
        exit(1)
print("PASS: All valid modes accepted")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_defaults():
    """TrackioConfig defaults: mode=disabled, others None."""
    code = '''
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r\'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)\'
match = re.search(pattern, src, re.DOTALL)

if not match:
    print("FAIL: Could not find TrackioConfig class")
    exit(1)

ns = {"__builtins__": __builtins__}
exec("from dataclasses import dataclass, field\\n" + match.group(1), ns)
TrackioConfig = ns["TrackioConfig"]

cfg = TrackioConfig()
errors = []
if cfg.mode != "disabled":
    errors.append(f"mode should be \'disabled\', got {cfg.mode!r}")
if cfg.project is not None:
    errors.append(f"project should be None, got {cfg.project!r}")
if cfg.name is not None:
    errors.append(f"name should be None, got {cfg.name!r}")
if cfg.space_id is not None:
    errors.append(f"space_id should be None, got {cfg.space_id!r}")

if errors:
    for e in errors:
        print(f"FAIL: {e}")
    exit(1)
print("PASS: All defaults correct")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_config_trackio_field():
    """StatsLoggerConfig has a trackio field."""
    code = '''
import ast
from pathlib import Path

REPO = "/workspace/AReaL"
src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
tree = ast.parse(src)

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "StatsLoggerConfig":
        cls = node
        break

if cls is None:
    print("FAIL: StatsLoggerConfig class not found")
    exit(1)

trackio_found = False
for node in ast.walk(cls):
    if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
        if node.target.id == "trackio":
            trackio_found = True
            break

if not trackio_found:
    print("FAIL: StatsLoggerConfig has no \'trackio\' field")
    exit(1)

print("PASS: StatsLoggerConfig.trackio field exists")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_init():
    """StatsLogger.init() initializes trackio when mode != disabled."""
    code = '''
import ast
from pathlib import Path

REPO = "/workspace/AReaL"
src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
tree = ast.parse(src)

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "StatsLogger":
        cls = node
        break
assert cls is not None, "StatsLogger class not found"

init_method = None
for item in cls.body:
    if isinstance(item, ast.FunctionDef) and item.name == "init":
        init_method = item
        break
assert init_method is not None, "StatsLogger.init() not found"

has_trackio_init = False
for node in ast.walk(init_method):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute)
            and func.attr == "init"
            and isinstance(func.value, ast.Name)
            and func.value.id == "trackio"):
            has_trackio_init = True
            kw_names = {kw.arg for kw in node.keywords}
            if "project" not in kw_names or "name" not in kw_names:
                print("FAIL: trackio.init() missing project or name kwargs")
                exit(1)
            break

if not has_trackio_init:
    print("FAIL: StatsLogger.init() does not call trackio.init()")
    exit(1)

print("PASS: StatsLogger.init() calls trackio.init() with project and name")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_commit():
    """StatsLogger.commit() calls trackio.log when enabled."""
    code = '''
import ast
from pathlib import Path

REPO = "/workspace/AReaL"
src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
tree = ast.parse(src)

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "StatsLogger":
        cls = node
        break
assert cls is not None, "StatsLogger class not found"

commit_method = None
for item in cls.body:
    if isinstance(item, ast.FunctionDef) and item.name == "commit":
        commit_method = item
        break
assert commit_method is not None, "StatsLogger.commit() not found"

has_trackio_log = False
for node in ast.walk(commit_method):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute)
            and func.attr == "log"
            and isinstance(func.value, ast.Name)
            and func.value.id == "trackio"):
            has_trackio_log = True
            break

if not has_trackio_log:
    print("FAIL: StatsLogger.commit() does not call trackio.log()")
    exit(1)

print("PASS: StatsLogger.commit() calls trackio.log()")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_close():
    """StatsLogger.close() calls trackio.finish when enabled."""
    code = '''
import ast
from pathlib import Path

REPO = "/workspace/AReaL"
src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
tree = ast.parse(src)

cls = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "StatsLogger":
        cls = node
        break
assert cls is not None, "StatsLogger class not found"

close_method = None
for item in cls.body:
    if isinstance(item, ast.FunctionDef) and item.name == "close":
        close_method = item
        break
assert close_method is not None, "StatsLogger.close() not found"

has_trackio_finish = False
for node in ast.walk(close_method):
    if isinstance(node, ast.Call):
        func = node.func
        if (isinstance(func, ast.Attribute)
            and func.attr == "finish"
            and isinstance(func.value, ast.Name)
            and func.value.id == "trackio"):
            has_trackio_finish = True
            break

if not has_trackio_finish:
    print("FAIL: StatsLogger.close() does not call trackio.finish()")
    exit(1)

print("PASS: StatsLogger.close() calls trackio.finish()")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_logging_helper_trackio():
    """logging.py log helper includes trackio.log call with graceful fallback."""
    code = '''
import ast
from pathlib import Path

REPO = "/workspace/AReaL"
src = Path(f"{REPO}/areal/utils/logging.py").read_text()
tree = ast.parse(src)

log_func = None
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and "log" in node.name.lower():
        func_src = ast.get_source_segment(src, node)
        if func_src and "wandb" in func_src and "swanlab" in func_src:
            log_func = node
            break

if log_func is None:
    print("FAIL: Could not find the combined logging helper function")
    exit(1)

func_src = ast.get_source_segment(src, log_func)
if "trackio" not in func_src:
    print("FAIL: Logging helper does not reference trackio")
    exit(1)

has_try_trackio = False
for node in ast.walk(log_func):
    if isinstance(node, ast.Try):
        try_src = ast.get_source_segment(src, node)
        if try_src and "trackio" in try_src:
            has_try_trackio = True
            break

if not has_try_trackio:
    print("FAIL: Logging helper has no try/except fallback for trackio import")
    exit(1)

print("PASS: Logging helper includes trackio with graceful fallback")
'''
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_trackio_config_not_stub():
    """TrackioConfig.__post_init__ has real validation logic, not just pass/return."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "TrackioConfig")
    assert cls is not None, "TrackioConfig not found"
    post_init = _find_method_in_class(cls, "__post_init__")
    assert post_init is not None, "TrackioConfig missing __post_init__"

    meaningful = sum(
        1 for stmt in ast.walk(post_init)
        if isinstance(stmt, (ast.If, ast.Raise, ast.Assert, ast.Assign))
    )
    assert meaningful >= 2, (
        f"TrackioConfig.__post_init__ has only {meaningful} meaningful statements"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .claude/rules/api-config.md
# ---------------------------------------------------------------------------

def test_trackio_config_post_init_validation():
    """TrackioConfig uses __post_init__ with ValueError for validation."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "TrackioConfig")
    assert cls is not None, "TrackioConfig class not found"

    post_init = _find_method_in_class(cls, "__post_init__")
    assert post_init is not None, (
        "TrackioConfig missing __post_init__ (required by .claude/rules/api-config.md)"
    )

    raises_value_error = False
    for node in ast.walk(post_init):
        if isinstance(node, ast.Raise) and node.exc is not None:
            exc = node.exc
            if isinstance(exc, ast.Call):
                exc = exc.func
            if isinstance(exc, ast.Name) and exc.id == "ValueError":
                raises_value_error = True
                break
    assert raises_value_error, (
        "TrackioConfig.__post_init__ does not raise ValueError"
    )


def test_trackio_config_has_docstring():
    """TrackioConfig class has a docstring (all public configs must have docstring)."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "TrackioConfig")
    assert cls is not None, "TrackioConfig class not found"

    has_docstring = (
        cls.body
        and isinstance(cls.body[0], ast.Expr)
        and isinstance(cls.body[0].value, ast.Constant)
        and isinstance(cls.body[0].value.value, str)
        and len(cls.body[0].value.value.strip()) > 10
    )
    assert has_docstring, (
        "TrackioConfig is missing a class docstring "
        "(required by .claude/rules/api-config.md)"
    )


def test_trackio_config_field_help_metadata():
    """StatsLoggerConfig.trackio field has 'help' in metadata."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLoggerConfig")
    assert cls is not None, "StatsLoggerConfig not found"

    for node in cls.body:
        if (isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "trackio"
                and node.value is not None):
            field_src = ast.get_source_segment(src, node.value)
            if field_src:
                assert "metadata" in field_src, (
                    "trackio field is missing metadata dict"
                )
                assert "help" in field_src, (
                    "trackio field metadata is missing 'help' key "
                    "(required by .claude/rules/api-config.md)"
                )
                return
    raise AssertionError(
        "StatsLoggerConfig.trackio field not found or has no field() call"
    )


def test_no_wildcard_imports():
    """No wildcard imports in modified files."""
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        tree = ast.parse(Path(f"{REPO}/{fname}").read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and any(
                alias.name == "*" for alias in node.names
            ):
                raise AssertionError(
                    f"Wildcard import in {fname}: from {node.module} import *"
                )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD validation
# ---------------------------------------------------------------------------

def test_repo_yaml_valid():
    """Repo's YAML configuration files are syntactically valid (pass_to_pass)."""
    import yaml

    yaml_files = [
        ".github/workflows/pre-commit.yml",
        ".github/workflows/test-areal.yml",
        ".pre-commit-config.yaml",
    ]
    for f in yaml_files:
        p = Path(f"{REPO}/{f}")
        if p.exists():
            try:
                yaml.safe_load(p.read_text())
            except yaml.YAMLError as e:
                raise AssertionError(f"Invalid YAML in {f}: {e}")


def test_repo_json_valid():
    """Repo's JSON files are syntactically valid (pass_to_pass)."""
    import json

    json_files = list(Path(REPO).rglob("*.json"))
    if not json_files:
        return

    for f in json_files[:10]:
        try:
            json.loads(f.read_text())
        except json.JSONDecodeError as e:
            raise AssertionError(f"Invalid JSON in {f}: {e}")


def test_repo_no_trailing_whitespace():
    """Modified files have no trailing whitespace (pass_to_pass)."""
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        content = Path(f"{REPO}/{fname}").read_text()
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if line != line.rstrip():
                raise AssertionError(f"Trailing whitespace in {fname}:{i}")


def test_repo_newline_at_eof():
    """Modified files end with a newline (pass_to_pass)."""
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        content = Path(f"{REPO}/{fname}").read_text()
        if content and not content.endswith("\n"):
            raise AssertionError(f"Missing newline at end of {fname}")
