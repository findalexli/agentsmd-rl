"""Tests for AReaL PR #951: improved Archon pipeline parallelism memory handling.

The PR adds:
  1. ``is_moe_model_config`` utility in
     ``areal/experimental/models/archon/utils.py``.
  2. ``_NullOutputChunks`` shim in
     ``areal/experimental/engine/archon_runner.py`` (a list whose ``append``
     is a no-op so PyTorch's per-microbatch logits don't accumulate).
  3. ``ArchonEngineConfig.reshard_after_forward_policy`` field with
     validation in ``__post_init__``.

The repo cannot be imported directly without installing torch + many
heavy deps, so these tests load the relevant classes / functions
straight from the source files via ``importlib`` (for files with only
stdlib imports) or AST extraction (for files with heavy imports).
"""

from __future__ import annotations

import ast
import importlib.util
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pytest

REPO = Path("/workspace/areal")
UTILS_PY = REPO / "areal/experimental/models/archon/utils.py"
RUNNER_PY = REPO / "areal/experimental/engine/archon_runner.py"
CLI_ARGS_PY = REPO / "areal/api/cli_args.py"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _import_file_as_module(path: Path, name: str):
    """Import a file directly. Only works for files whose imports are
    available in the current interpreter."""
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _extract_classes(path: Path, names: list[str], extra_namespace: dict | None = None):
    """AST-extract specific class definitions from a Python source file
    and exec them in a clean namespace, without importing anything else
    the file might otherwise pull in.

    Returns a dict ``{class_name: class_obj}``.

    Missing classes are *not* in the returned dict (callers should KeyError).
    """
    src = path.read_text()
    tree = ast.parse(src)
    ns: dict[str, Any] = {
        "dataclass": dataclass,
        "field": field,
        "Any": Any,
        "list": list,
    }
    if extra_namespace:
        ns.update(extra_namespace)
    nodes = [
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name in names
    ]
    if not nodes:
        return {}
    module = ast.Module(body=nodes, type_ignores=[])
    exec(compile(module, str(path), "exec"), ns)
    return {n: ns[n] for n in names if n in ns}


# --------------------------------------------------------------------------- #
# fail-to-pass: is_moe_model_config utility
# --------------------------------------------------------------------------- #


def test_is_moe_model_config_exists_and_importable():
    """The utility must be importable from the archon utils module."""
    mod = _import_file_as_module(UTILS_PY, "_archon_utils_under_test")
    assert hasattr(mod, "is_moe_model_config"), (
        "is_moe_model_config must be defined in "
        "areal/experimental/models/archon/utils.py"
    )
    # Also exported in __all__
    assert "is_moe_model_config" in getattr(mod, "__all__", []), (
        "is_moe_model_config must be listed in the module's __all__"
    )


def test_is_moe_model_config_true_for_moe_configs():
    """Returns True for configs with num_experts > 1 or num_local_experts > 1."""
    mod = _import_file_as_module(UTILS_PY, "_archon_utils_under_test_2")
    is_moe = mod.is_moe_model_config

    class FakeCfg:
        pass

    # num_experts > 1
    cfg = FakeCfg()
    cfg.num_experts = 8
    assert is_moe(cfg) is True

    cfg = FakeCfg()
    cfg.num_experts = 2
    assert is_moe(cfg) is True

    # num_local_experts > 1 (used when num_experts is missing)
    cfg = FakeCfg()
    cfg.num_local_experts = 4
    assert is_moe(cfg) is True


def test_is_moe_model_config_false_for_dense_or_missing():
    """Returns False for configs without expert attrs or with <=1 expert."""
    mod = _import_file_as_module(UTILS_PY, "_archon_utils_under_test_3")
    is_moe = mod.is_moe_model_config

    class FakeCfg:
        pass

    # No expert-related attribute
    cfg = FakeCfg()
    assert is_moe(cfg) is False

    # num_experts is None (HF puts None for non-MoE in some configs)
    cfg = FakeCfg()
    cfg.num_experts = None
    assert is_moe(cfg) is False

    # num_experts == 1 (degenerate "MoE" with single expert)
    cfg = FakeCfg()
    cfg.num_experts = 1
    assert is_moe(cfg) is False

    # num_local_experts == 1
    cfg = FakeCfg()
    cfg.num_local_experts = 1
    assert is_moe(cfg) is False


# --------------------------------------------------------------------------- #
# fail-to-pass: _NullOutputChunks
# --------------------------------------------------------------------------- #


def test_null_output_chunks_class_exists():
    """The runner module must define a _NullOutputChunks class."""
    classes = _extract_classes(RUNNER_PY, ["_NullOutputChunks"])
    assert "_NullOutputChunks" in classes, (
        "_NullOutputChunks must be defined in "
        "areal/experimental/engine/archon_runner.py"
    )


def test_null_output_chunks_subclass_of_list():
    """_NullOutputChunks must be a list subclass so PyTorch's pipelining
    code that does `output_chunks.append(output)` and later expects a
    list-like object still works."""
    classes = _extract_classes(RUNNER_PY, ["_NullOutputChunks"])
    cls = classes["_NullOutputChunks"]
    assert issubclass(cls, list)


def test_null_output_chunks_append_is_noop_and_stays_empty():
    """The whole point of the class: append() must do nothing so each
    microbatch's logits get freed instead of accumulated."""
    classes = _extract_classes(RUNNER_PY, ["_NullOutputChunks"])
    cls = classes["_NullOutputChunks"]

    chunks = cls()
    assert isinstance(chunks, list)
    assert len(chunks) == 0

    # Appending values of varying types must all be ignored.
    for item in (1, "two", object(), [3, 4], {"k": "v"}, None):
        chunks.append(item)

    assert len(chunks) == 0
    assert list(chunks) == []


def test_null_output_chunks_other_list_ops_still_work():
    """append is the only override; other list operations (extend via
    +, iter, len) should behave normally so the rest of the pipeline
    code doesn't break."""
    classes = _extract_classes(RUNNER_PY, ["_NullOutputChunks"])
    cls = classes["_NullOutputChunks"]

    chunks = cls()
    # Indexing into an empty container, iteration, len all work.
    assert len(chunks) == 0
    assert list(chunks) == []
    # The class behaves as a list at the type level.
    assert isinstance(chunks, list)


# --------------------------------------------------------------------------- #
# fail-to-pass: reshard_after_forward_policy validation
# --------------------------------------------------------------------------- #


def _load_archon_engine_config():
    classes = _extract_classes(CLI_ARGS_PY, ["ArchonEngineConfig"])
    assert "ArchonEngineConfig" in classes, (
        "ArchonEngineConfig must be defined in areal/api/cli_args.py"
    )
    return classes["ArchonEngineConfig"]


def test_reshard_policy_field_default_value():
    """The new field must default to the string 'default'."""
    cfg = _load_archon_engine_config()()
    assert hasattr(cfg, "reshard_after_forward_policy"), (
        "ArchonEngineConfig must expose a reshard_after_forward_policy field"
    )
    assert cfg.reshard_after_forward_policy == "default"


def test_reshard_policy_accepts_all_documented_values():
    """The three documented values 'default', 'always', 'never' must be accepted."""
    Cfg = _load_archon_engine_config()
    for value in ("default", "always", "never"):
        cfg = Cfg(reshard_after_forward_policy=value)
        assert cfg.reshard_after_forward_policy == value


def test_reshard_policy_rejects_invalid_value():
    """An invalid value must raise ValueError with a clear message that
    includes the field name and the allowed values, per the project's
    api-config rule (`__post_init__` raises ``ValueError`` with a clear
    message)."""
    Cfg = _load_archon_engine_config()

    for bad in ("invalid", "all", "ALWAYS", "", "Default", "none"):
        with pytest.raises(ValueError) as excinfo:
            Cfg(reshard_after_forward_policy=bad)
        msg = str(excinfo.value)
        assert "reshard_after_forward_policy" in msg, (
            f"ValueError for bad value {bad!r} must mention the field name; "
            f"got: {msg}"
        )
        # Mention valid choices so the user knows what is allowed.
        for choice in ("default", "always", "never"):
            assert choice in msg, (
                f"ValueError for bad value {bad!r} must mention valid choice "
                f"{choice!r}; got: {msg}"
            )


def test_reshard_policy_field_is_keyword_only_dataclass_field():
    """The new field must be added with a default and a help string in
    metadata (project's api-config rule: 'Add fields with defaults' for
    backward compat; CLI rule: 'must have clear help in metadata')."""
    Cfg = _load_archon_engine_config()
    from dataclasses import fields as dc_fields

    found = None
    for f in dc_fields(Cfg):
        if f.name == "reshard_after_forward_policy":
            found = f
            break
    assert found is not None, "reshard_after_forward_policy must be a dataclass field"
    assert found.default == "default", "default must be the string 'default'"
    md = dict(found.metadata)
    assert md.get("help"), "help text must be non-empty (CLI integration rule)"
    assert md.get("choices") == ["default", "always", "never"], (
        "metadata['choices'] must list the three allowed values"
    )


# --------------------------------------------------------------------------- #
# pass-to-pass: repo CI/CD checks
# --------------------------------------------------------------------------- #

# Files modified by the PR -- exercised by the linter on the gold tree.
_PR_PYTHON_FILES = [
    "areal/api/cli_args.py",
    "areal/experimental/engine/archon_engine.py",
    "areal/experimental/engine/archon_runner.py",
    "areal/experimental/models/archon/utils.py",
]


def test_ruff_lint_passes_on_pr_files():
    """The repo's own linter (ruff 0.14.9, configured in pyproject.toml)
    must pass cleanly on the files this PR modifies."""
    r = subprocess.run(
        ["ruff", "check", *_PR_PYTHON_FILES],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ruff check failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )


def test_ruff_format_check_passes_on_pr_files():
    """The repo's own formatter check must pass on PR-modified files
    (project enforces ruff-format via pre-commit)."""
    r = subprocess.run(
        ["ruff", "format", "--check", *_PR_PYTHON_FILES],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"ruff format --check failed:\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
