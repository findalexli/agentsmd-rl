"""
Task: areal-trackio-tracking-backend
Repo: inclusionAI/AReaL @ 92c467e56bf17d730bd26855de33d5e4e13ba435
PR:   #1113

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import textwrap
from dataclasses import dataclass, field, fields
from pathlib import Path
from types import SimpleNamespace

REPO = "/workspace/AReaL"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_trackio_config():
    """Extract TrackioConfig class from source and return it."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    match = re.search(
        r"(@dataclass[^\n]*\nclass TrackioConfig:.*?)(?=\n@dataclass|\nclass \w)",
        src, re.DOTALL,
    )
    assert match, "Could not find TrackioConfig class in cli_args.py"
    ns = {"__builtins__": __builtins__}
    exec("from dataclasses import dataclass, field\n" + match.group(1), ns)
    return ns["TrackioConfig"]


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

# [static] pass_to_pass
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
# Fail-to-pass (pr_diff) — TrackioConfig behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_trackio_config_exists_with_fields():
    """TrackioConfig class exists with mode, project, name, space_id fields."""
    TrackioConfig = _load_trackio_config()
    field_names = {f.name for f in fields(TrackioConfig)}
    assert "mode" in field_names, "TrackioConfig missing 'mode' field"
    assert "project" in field_names, "TrackioConfig missing 'project' field"
    assert "name" in field_names, "TrackioConfig missing 'name' field"
    assert "space_id" in field_names, "TrackioConfig missing 'space_id' field"


# [pr_diff] fail_to_pass
def test_trackio_config_rejects_invalid_modes():
    """TrackioConfig rejects invalid mode values with ValueError."""
    TrackioConfig = _load_trackio_config()
    for bad_mode in ["invalid", "remote", "cloud", "off", "enabled", ""]:
        try:
            TrackioConfig(mode=bad_mode)
            raise AssertionError(
                f"TrackioConfig accepted invalid mode={bad_mode!r}"
            )
        except (ValueError, TypeError):
            pass


# [pr_diff] fail_to_pass
def test_trackio_config_accepts_valid_modes():
    """TrackioConfig accepts all three valid mode values."""
    TrackioConfig = _load_trackio_config()
    for mode in ("disabled", "online", "local"):
        cfg = TrackioConfig(mode=mode)
        assert cfg.mode == mode, f"Expected mode={mode!r}, got {cfg.mode!r}"


# [pr_diff] fail_to_pass
def test_trackio_config_defaults():
    """TrackioConfig defaults: mode='disabled', others None."""
    TrackioConfig = _load_trackio_config()
    cfg = TrackioConfig()
    assert cfg.mode == "disabled", f"Default mode should be 'disabled', got {cfg.mode!r}"
    assert cfg.project is None, f"Default project should be None, got {cfg.project!r}"
    assert cfg.name is None, f"Default name should be None, got {cfg.name!r}"
    assert cfg.space_id is None, f"Default space_id should be None, got {cfg.space_id!r}"


# [pr_diff] fail_to_pass
def test_stats_logger_config_trackio_field():
    """StatsLoggerConfig has a 'trackio' field."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLoggerConfig")
    assert cls is not None, "StatsLoggerConfig class not found"

    # Check for a field assignment named 'trackio'
    trackio_found = False
    for node in ast.walk(cls):
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "trackio":
                trackio_found = True
                break
    assert trackio_found, "StatsLoggerConfig has no 'trackio' field"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — StatsLogger integration tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stats_logger_trackio_init():
    """StatsLogger.init() initializes trackio when mode != 'disabled'."""
    src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLogger")
    assert cls is not None, "StatsLogger class not found in stats_logger.py"

    init_method = _find_method_in_class(cls, "init")
    assert init_method is not None, "StatsLogger.init() method not found"

    init_src = ast.get_source_segment(src, init_method)
    assert "trackio" in init_src.lower(), (
        "StatsLogger.init() does not reference trackio"
    )

    # Must call trackio.init() with project and name
    has_trackio_init = False
    for node in ast.walk(init_method):
        if isinstance(node, ast.Call):
            func = node.func
            if (isinstance(func, ast.Attribute)
                and func.attr == "init"
                and isinstance(func.value, ast.Name)
                and func.value.id == "trackio"):
                has_trackio_init = True
                # Verify it passes project and name kwargs
                kw_names = {kw.arg for kw in node.keywords}
                assert "project" in kw_names, (
                    "trackio.init() missing 'project' keyword argument"
                )
                assert "name" in kw_names, (
                    "trackio.init() missing 'name' keyword argument"
                )
                break
    assert has_trackio_init, "StatsLogger.init() does not call trackio.init()"


# [pr_diff] fail_to_pass
def test_stats_logger_trackio_commit():
    """StatsLogger.commit() calls trackio.log when enabled."""
    src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLogger")
    assert cls is not None, "StatsLogger class not found"

    commit_method = _find_method_in_class(cls, "commit")
    assert commit_method is not None, "StatsLogger.commit() method not found"

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
    assert has_trackio_log, "StatsLogger.commit() does not call trackio.log()"


# [pr_diff] fail_to_pass
def test_stats_logger_trackio_close():
    """StatsLogger.close() calls trackio.finish when enabled."""
    src = Path(f"{REPO}/areal/utils/stats_logger.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLogger")
    assert cls is not None, "StatsLogger class not found"

    close_method = _find_method_in_class(cls, "close")
    assert close_method is not None, "StatsLogger.close() method not found"

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
    assert has_trackio_finish, "StatsLogger.close() does not call trackio.finish()"


# [pr_diff] fail_to_pass
def test_logging_helper_trackio():
    """logging.py log helper includes trackio.log call with graceful fallback."""
    src = Path(f"{REPO}/areal/utils/logging.py").read_text()
    tree = ast.parse(src)

    # Find the log_swanlab_wandb_tensorboard function (or renamed variant)
    log_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and "log" in node.name.lower():
            func_src = ast.get_source_segment(src, node)
            if func_src and "wandb" in func_src and "swanlab" in func_src:
                log_func = node
                break
    assert log_func is not None, "Could not find the combined logging helper function"

    func_src = ast.get_source_segment(src, log_func)
    assert "trackio" in func_src, (
        "Logging helper does not reference trackio"
    )

    # Must have a try/except for graceful fallback when trackio is not installed
    has_try_trackio = False
    for node in ast.walk(log_func):
        if isinstance(node, ast.Try):
            try_src = ast.get_source_segment(src, node)
            if try_src and "trackio" in try_src:
                has_try_trackio = True
                break
    assert has_try_trackio, (
        "Logging helper has no try/except fallback for trackio import"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
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

# [agent_config] fail_to_pass — .claude/rules/api-config.md:37-38 @ 92c467e
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

    # Must raise ValueError (not other exception types)
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


# [agent_config] fail_to_pass — .claude/rules/api-config.md:60 @ 92c467e
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


# [agent_config] fail_to_pass — .claude/rules/api-config.md:54 @ 92c467e
def test_trackio_config_field_help_metadata():
    """StatsLoggerConfig.trackio field has 'help' in metadata."""
    src = Path(f"{REPO}/areal/api/cli_args.py").read_text()
    tree = ast.parse(src)
    cls = _find_class_in_ast(tree, "StatsLoggerConfig")
    assert cls is not None, "StatsLoggerConfig not found"

    # Find the trackio annotation and its field() call
    for node in cls.body:
        if (isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "trackio"
                and node.value is not None):
            # Look for metadata={"help": ...} in field() call
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


# [agent_config] pass_to_pass — CLAUDE.md:93 @ 92c467e
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
