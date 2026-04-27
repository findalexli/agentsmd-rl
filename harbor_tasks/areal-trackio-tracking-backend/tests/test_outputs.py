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
from unittest.mock import patch, MagicMock

REPO = "/workspace/AReaL"


def _exec_code_via_subprocess(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO,
            env={**os.environ, "PYTHONPATH": REPO}
        )
        return result
    finally:
        os.unlink(tmp_path)


def _find_class_in_ast(tree, classname):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == classname:
            return node
    return None


def _find_method_in_class(class_node, method_name):
    for item in class_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == method_name:
            return item
    return None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        src = Path(f"{REPO}/{fname}").read_text()
        compile(src, fname, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — TrackioConfig behavioral tests
# ---------------------------------------------------------------------------

def test_trackio_config_exists_with_fields():
    code = """
import re
from pathlib import Path
from dataclasses import fields

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
# Match @dataclass ... class TrackioConfig: block
pattern = r'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)'
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
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_rejects_invalid_modes():
    code = """
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)'
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
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_accepts_valid_modes():
    code = """
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)'
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
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_trackio_config_defaults():
    code = """
import re
from pathlib import Path

src = Path("/workspace/AReaL/areal/api/cli_args.py").read_text()
pattern = r'(@dataclass[^\\n]*\\nclass TrackioConfig:.*?)(?=\\n@dataclass|\\nclass \\w)'
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
    errors.append(f"mode should be 'disabled', got {cfg.mode!r}")
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
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_config_trackio_field():
    code = """
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
    print("FAIL: StatsLoggerConfig has no 'trackio' field")
    exit(1)

print("PASS: StatsLoggerConfig.trackio field exists")
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def _stats_logger_preamble():
    """Return common preamble code for StatsLogger subprocess tests.

    Mocks all heavy deps and loads stats_logger.py via importlib so the test
    is not coupled to any specific import pattern for trackio.
    """
    return """
import sys, importlib.util
import unittest.mock as mock

# Mock all heavy deps that stats_logger.py and its transitive imports need
for mod_name in [
    "swanlab", "wandb", "torch", "torch.cuda",
    "tensorboardX", "aiohttp", "aiohttp.web",
    "areal", "areal.api", "areal.infra",
    "areal.utils", "areal.utils.logging", "areal.utils.printing",
    "areal.version",
]:
    sys.modules.setdefault(mod_name, mock.MagicMock())

# Wire torch.distributed so 'import torch.distributed as dist' gets the same mock
_torch_dist = mock.MagicMock()
_torch_dist.is_initialized.return_value = False
sys.modules["torch"].distributed = _torch_dist
sys.modules["torch.distributed"] = _torch_dist

# areal.api.cli_args needs real types for isinstance() checks in StatsLogger
_cli_args_mod = mock.MagicMock()
_cli_args_mod.StatsLoggerConfig = type("StatsLoggerConfig", (), {})
_cli_args_mod.BaseExperimentConfig = type("BaseExperimentConfig", (), {})
sys.modules["areal.api.cli_args"] = _cli_args_mod
"""


def _stats_logger_load():
    """Return code to load StatsLogger via importlib."""
    return """
# Load stats_logger.py directly via importlib (bypasses areal/__init__.py)
spec = importlib.util.spec_from_file_location(
    "areal.utils.stats_logger",
    "/workspace/AReaL/areal/utils/stats_logger.py",
)
_sl_mod = importlib.util.module_from_spec(spec)
sys.modules["areal.utils.stats_logger"] = _sl_mod
spec.loader.exec_module(_sl_mod)
StatsLogger = _sl_mod.StatsLogger
"""


def _stats_logger_dummy_config(
    trackio_mode="online",
    trackio_project='"my_project"',
    trackio_name='"my_name"',
    trackio_space_id="None",
    experiment_name="test_exp",
    trial_name="test_trial",
):
    """Return code that defines dummy config classes and creates a StatsLogger."""
    return f"""
from dataclasses import dataclass, field

@dataclass
class DummyWandBConfig:
    mode: str = "disabled"
    wandb_base_url: str = ""
    wandb_api_key: str = ""
    entity: str = ""
    project: str | None = None
    name: str | None = None
    job_type: str = ""
    group: str = ""
    notes: str = ""
    tags: list = field(default_factory=list)
    id_suffix: str = ""

@dataclass
class DummySwanlabConfig:
    mode: str = "disabled"
    api_key: str = ""
    project: str | None = None
    name: str | None = None
    config: dict | None = None

@dataclass
class DummyTensorBoardConfig:
    path: str | None = None

@dataclass
class DummyTrackioConfig:
    mode: str = "{trackio_mode}"
    project: str | None = {trackio_project}
    name: str | None = {trackio_name}
    space_id: str | None = {trackio_space_id}

@dataclass
class DummyStatsLoggerConfig:
    experiment_name: str = "{experiment_name}"
    trial_name: str = "{trial_name}"
    fileroot: str = "/tmp/test_logs"
    wandb: DummyWandBConfig = field(default_factory=DummyWandBConfig)
    swanlab: DummySwanlabConfig = field(default_factory=DummySwanlabConfig)
    tensorboard: DummyTensorBoardConfig = field(default_factory=DummyTensorBoardConfig)
    trackio: DummyTrackioConfig = field(default_factory=DummyTrackioConfig)

# Wrap in a top-level config with .stats_logger attribute
@dataclass
class DummyBaseConfig:
    experiment_name: str = "{experiment_name}"
    trial_name: str = "{trial_name}"
    stats_logger: DummyStatsLoggerConfig = field(default_factory=DummyStatsLoggerConfig)

top_config = DummyBaseConfig()
logger = StatsLogger(top_config, ft_spec=mock.MagicMock())
"""


def test_stats_logger_trackio_init():
    """Behavioral test: StatsLogger.init() calls trackio.init with correct kwargs.

    Uses importlib to load stats_logger.py directly with all heavy deps mocked,
    so the test works regardless of the import pattern used (import trackio,
    import trackio as tio, from trackio import init, etc.).
    """
    code = _stats_logger_preamble() + """
# Set up custom trackio mock to capture init calls
init_calls = []
def capture_init(**kwargs):
    init_calls.append(kwargs)

mock_trackio = mock.MagicMock()
mock_trackio.init = capture_init
mock_trackio.log = mock.MagicMock()
mock_trackio.finish = mock.MagicMock()
sys.modules["trackio"] = mock_trackio
""" + _stats_logger_load() + _stats_logger_dummy_config(
        trackio_project='"my_project"',
        trackio_name='"my_name"',
        trackio_space_id='"user/my-space"',
    ) + """
if not init_calls:
    print("FAIL: trackio.init was never called")
    sys.exit(1)

call_kwargs = init_calls[0]

if "project" not in call_kwargs:
    print("FAIL: trackio.init missing 'project' kwarg")
    sys.exit(1)
if "name" not in call_kwargs:
    print("FAIL: trackio.init missing 'name' kwarg")
    sys.exit(1)
if "space_id" not in call_kwargs:
    print("FAIL: trackio.init missing 'space_id' kwarg")
    sys.exit(1)

print("PASS: trackio.init called with project, name, space_id kwargs")
"""
    r = _exec_code_via_subprocess(code, timeout=60)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_init_fallback():
    """Behavioral test: project defaults to experiment_name, name to trial_name when None."""
    code = _stats_logger_preamble() + """
init_calls = []
def capture_init(**kwargs):
    init_calls.append(kwargs)

mock_trackio = mock.MagicMock()
mock_trackio.init = capture_init
mock_trackio.log = mock.MagicMock()
mock_trackio.finish = mock.MagicMock()
sys.modules["trackio"] = mock_trackio
""" + _stats_logger_load() + _stats_logger_dummy_config(
        trackio_project="None",
        trackio_name="None",
        trackio_space_id='"user/my-space"',
        experiment_name="my_experiment",
        trial_name="my_trial",
    ) + """
if not init_calls:
    print("FAIL: trackio.init was never called")
    sys.exit(1)

call_kwargs = init_calls[0]

if call_kwargs.get("project") != "my_experiment":
    print(f"FAIL: Expected project='my_experiment', got {call_kwargs.get('project')!r}")
    sys.exit(1)
if call_kwargs.get("name") != "my_trial":
    print(f"FAIL: Expected name='my_trial', got {call_kwargs.get('name')!r}")
    sys.exit(1)

print("PASS: trackio.init uses experiment_name/trial_name fallback correctly")
"""
    r = _exec_code_via_subprocess(code, timeout=60)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_commit():
    """Behavioral test: StatsLogger.commit() calls trackio.log when enabled.

    Uses sys.modules mocking + importlib so any import pattern works.
    """
    code = _stats_logger_preamble() + """
mock_trackio = mock.MagicMock()
mock_trackio.init = mock.MagicMock()
mock_trackio.finish = mock.MagicMock()
mock_log_calls = []

def mock_log(*args, **kwargs):
    mock_log_calls.append({"args": args, "kwargs": kwargs})

mock_trackio.log = mock_log
sys.modules["trackio"] = mock_trackio
""" + _stats_logger_load() + _stats_logger_dummy_config() + """
mock_log_calls.clear()

logger.commit(epoch=1, step=100, global_step=100, data={"loss": 0.5})

if not mock_log_calls:
    print("FAIL: trackio.log was never called during commit")
    sys.exit(1)

# Check that log data contains 'loss' -- could be positional or keyword arg
call = mock_log_calls[0]
all_items = list(call["args"]) + [call["kwargs"]]
found_loss = any(isinstance(a, dict) and "loss" in a for a in all_items)
if not found_loss:
    print(f"FAIL: trackio.log call missing 'loss' data: {mock_log_calls}")
    sys.exit(1)

print("PASS: trackio.log called with data during commit")
"""
    r = _exec_code_via_subprocess(code, timeout=60)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_stats_logger_trackio_close():
    """Behavioral test: StatsLogger.close() calls trackio.finish when enabled.

    Uses sys.modules mocking + importlib so any import pattern works.
    """
    code = _stats_logger_preamble() + """
mock_trackio = mock.MagicMock()
mock_trackio.init = mock.MagicMock()
mock_trackio.log = mock.MagicMock()
mock_finish_called = []

def mock_finish():
    mock_finish_called.append(True)

mock_trackio.finish = mock_finish
sys.modules["trackio"] = mock_trackio
""" + _stats_logger_load() + _stats_logger_dummy_config() + """
mock_finish_called.clear()

logger.close()

if not mock_finish_called:
    print("FAIL: trackio.finish was never called during close")
    sys.exit(1)

print("PASS: trackio.finish called during close")
"""
    r = _exec_code_via_subprocess(code, timeout=60)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


def test_logging_helper_trackio():
    code = """
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
"""
    r = _exec_code_via_subprocess(code)
    assert r.returncode == 0, f"Test failed: stdout={r.stdout}, stderr={r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

def test_trackio_config_not_stub():
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


def test_trackio_config_post_init_validation():
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

def test_repo_ruff_format():
    r = subprocess.run(
        ["ruff", "format", "--check", "areal/api/cli_args.py",
         "areal/utils/logging.py", "areal/utils/stats_logger.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff format check failed:\n{r.stderr}\n{r.stdout}"


def test_repo_ruff_lint():
    r = subprocess.run(
        ["ruff", "check", "--ignore", "UP042", "areal/api/cli_args.py",
         "areal/utils/logging.py", "areal/utils/stats_logger.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stderr}\n{r.stdout}"


def test_repo_python_syntax():
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        src = Path(f"{REPO}/{fname}").read_text()
        try:
            ast.parse(src)
        except SyntaxError as e:
            raise AssertionError(f"Syntax error in {fname}: {e}")


def test_repo_yaml_valid():
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
    for fname in [
        "areal/api/cli_args.py",
        "areal/utils/logging.py",
        "areal/utils/stats_logger.py",
    ]:
        content = Path(f"{REPO}/{fname}").read_text()
        if content and not content.endswith("\n"):
            raise AssertionError(f"Missing newline at end of {fname}")


def test_repo_py_compile():
    r = subprocess.run(
        ["python", "-m", "py_compile", "areal/api/cli_args.py",
         "areal/utils/logging.py", "areal/utils/stats_logger.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python compilation failed:\n{r.stderr}"


def test_repo_toml_valid():
    r = subprocess.run(
        ["python", "-c",
         "import tomllib; tomllib.load(open(\"pyproject.toml\", \"rb\"))"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"TOML validation failed:\n{r.stderr}"


def test_repo_docs_cli_syntax():
    r = subprocess.run(
        ["python", "-m", "py_compile", "docs/generate_cli_docs.py"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"CLI docs script syntax failed:\n{r.stderr}"


def test_repo_ast_parse_cli_args():
    r = subprocess.run(
        ["python", "-c",
         "import ast; ast.parse(open(\"areal/api/cli_args.py\").read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed for cli_args.py:\n{r.stderr}"


def test_repo_ast_parse_stats_logger():
    r = subprocess.run(
        ["python", "-c",
         "import ast; ast.parse(open(\"areal/utils/stats_logger.py\").read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed for stats_logger.py:\n{r.stderr}"


def test_repo_ast_parse_logging():
    r = subprocess.run(
        ["python", "-c",
         "import ast; ast.parse(open(\"areal/utils/logging.py\").read())"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"AST parse failed for logging.py:\n{r.stderr}"
