"""Behavioral tests for the AReaL #1008 enum/logging cleanup task.

The repo's `areal/__init__.py` pulls in heavy dependencies (aiohttp, ray,
fastapi, transformers, ...) that we deliberately do NOT install in this
CPU-only environment. We bypass the package machinery by:

  1. Pre-populating `sys.modules` with light stubs for `areal`, `areal.api`,
     `areal.utils`, and `areal.utils.logging`.
  2. Loading the two target files directly via `importlib.util` so their
     internal `from areal.* import …` statements resolve against the stubs
     rather than executing the real package-level __init__.py.
"""

from __future__ import annotations

import importlib.util
import io
import logging
import os
import subprocess
import sys
import types as _t
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import pytest

REPO = Path("/workspace/AReaL")
TYPES_PATH = REPO / "areal/experimental/openai/types.py"
CLEVR_PATH = REPO / "areal/reward/clevr_count_70k.py"


@dataclass
class _StubModelResponse:
    input_tokens: list = field(default_factory=list)
    output_tokens: list = field(default_factory=list)
    output_logprobs: list = field(default_factory=list)
    output_versions: list = field(default_factory=list)

    @property
    def input_len(self) -> int:
        return len(self.input_tokens)

    @property
    def output_len(self) -> int:
        return len(self.output_tokens)


def _install_stubs() -> None:
    """Stub out areal subtree before importing the targets."""
    # Wipe any cached areal.* modules so we re-import against the stubs.
    for k in list(sys.modules):
        if k == "areal" or k.startswith("areal."):
            sys.modules.pop(k)

    areal = _t.ModuleType("areal")
    areal.__path__ = []  # mark as a package

    api = _t.ModuleType("areal.api")
    api.ModelResponse = _StubModelResponse

    utils = _t.ModuleType("areal.utils")
    utils.__path__ = []
    # Alias the stdlib logging module under areal.utils.logging --
    # `getLogger`, `info`, `warning` etc. are all standard-library API.
    utils_logging = logging

    # Belt-and-braces: also expose `logging` as an attribute on areal.utils,
    # so `from areal.utils import logging` is satisfied at attr-lookup time.
    utils.logging = utils_logging
    sys.modules["areal"] = areal
    sys.modules["areal.api"] = api
    sys.modules["areal.utils"] = utils
    sys.modules["areal.utils.logging"] = utils_logging


def _load_module(name: str, path: Path):
    """Load a Python source file as a fresh module using its file path.

    This bypasses areal/__init__.py entirely.
    """
    if name in sys.modules:
        del sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _load_types_module():
    _install_stubs()
    return _load_module("areal_pr1008_types", TYPES_PATH)


def _load_clevr_module():
    _install_stubs()
    return _load_module("areal_pr1008_clevr", CLEVR_PATH)


# Writable cache dirs for ruff and pytest in the read-only tests mount.
_RUFF_CACHE = "/tmp/ruff_cache"
os.makedirs(_RUFF_CACHE, exist_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass: ApiType / InputName enums must exist as str-Enum subclasses.
# ---------------------------------------------------------------------------

def test_api_type_enum_defined():
    """ApiType enum must exist with COMPLETION/RESPONSE/NONE members."""
    mod = _load_types_module()
    assert hasattr(mod, "ApiType"), "ApiType is not defined in types.py"
    cls = mod.ApiType
    assert isinstance(cls, type) and issubclass(cls, Enum), "ApiType must be an Enum"
    assert issubclass(cls, str), "ApiType must be a str-Enum (subclass of str)"
    members = {m.name: m.value for m in cls}
    assert members == {
        "COMPLETION": "completion",
        "RESPONSE": "response",
        "NONE": "none",
    }, f"ApiType members mismatch: {members}"


def test_input_name_enum_defined():
    """InputName enum must exist with MESSAGES/INPUT_DATA/NONE members."""
    mod = _load_types_module()
    assert hasattr(mod, "InputName"), "InputName is not defined in types.py"
    cls = mod.InputName
    assert isinstance(cls, type) and issubclass(cls, Enum), "InputName must be an Enum"
    assert issubclass(cls, str), "InputName must be a str-Enum"
    members = {m.name: m.value for m in cls}
    assert members == {
        "MESSAGES": "messages",
        "INPUT_DATA": "input_data",
        "NONE": "none",
    }, f"InputName members mismatch: {members}"


def test_api_type_property_returns_enum_for_completion():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter(completion=object())
    val = inst.api_type
    assert isinstance(val, mod.ApiType), (
        f"api_type returned {type(val).__name__}, expected ApiType enum"
    )
    assert val is mod.ApiType.COMPLETION
    assert val == "completion"  # str-Enum backward compat


def test_api_type_property_returns_enum_for_response():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter(response=object())
    val = inst.api_type
    assert isinstance(val, mod.ApiType)
    assert val is mod.ApiType.RESPONSE
    assert val == "response"


def test_api_type_property_returns_enum_for_none():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter()
    val = inst.api_type
    assert isinstance(val, mod.ApiType)
    assert val is mod.ApiType.NONE


def test_input_name_for_logging_returns_enum_completion():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter(completion=object())
    val = inst.input_name_for_logging
    assert isinstance(val, mod.InputName)
    assert val is mod.InputName.MESSAGES
    assert val == "messages"


def test_input_name_for_logging_returns_enum_response():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter(response=object())
    val = inst.input_name_for_logging
    assert isinstance(val, mod.InputName)
    assert val is mod.InputName.INPUT_DATA
    assert val == "input_data"


def test_input_name_for_logging_returns_enum_none():
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward
    inst = Inter()
    val = inst.input_name_for_logging
    assert isinstance(val, mod.InputName)
    assert val is mod.InputName.NONE


# ---------------------------------------------------------------------------
# Fail-to-pass: warning message space fix in to_tensor_dict.
# ---------------------------------------------------------------------------

def test_to_tensor_dict_warning_has_space_after_properly():
    """The warning emitted when child input_len <= parent_len must read
    'constructed properly. Ignoring' (with a space), not 'properly.Ignoring'.
    """
    mod = _load_types_module()
    Inter = mod.InteractionWithTokenLogpReward

    parent_resp = _StubModelResponse(
        input_tokens=[1, 2, 3, 4, 5],
        output_tokens=[6, 7],
        output_logprobs=[0.1, 0.2],
        output_versions=[1, 1],
    )
    parent = Inter(model_response=parent_resp, chat_template_type="concat")
    parent.output_message_list = [{"role": "assistant", "content": "x"}]
    parent.messages = [{"role": "user", "content": "y"}]

    # Child has input_len (3) <= parent_len (7) -> triggers warning branch.
    child_resp = _StubModelResponse(
        input_tokens=[1, 2, 3],
        output_tokens=[8, 9],
        output_logprobs=[0.3, 0.4],
        output_versions=[1, 1],
    )
    child = Inter(model_response=child_resp, parent=parent, chat_template_type="concat")

    captured = io.StringIO()
    handler = logging.StreamHandler(captured)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter("%(message)s"))
    target_logger = logging.getLogger("TokenLogpReward")
    prev_level = target_logger.level
    prev_propagate = target_logger.propagate
    target_logger.setLevel(logging.WARNING)
    target_logger.addHandler(handler)
    target_logger.propagate = False
    try:
        child.to_tensor_dict()
    finally:
        target_logger.removeHandler(handler)
        target_logger.setLevel(prev_level)
        target_logger.propagate = prev_propagate

    msg = captured.getvalue()
    assert "properly." in msg, f"Warning was not emitted as expected. Got: {msg!r}"
    assert "properly.Ignoring" not in msg, (
        "Warning still has 'properly.Ignoring' (no space). "
        f"Full message: {msg!r}"
    )
    assert "properly. Ignoring" in msg, (
        "Warning is missing the space between 'properly.' and 'Ignoring'. "
        f"Full message: {msg!r}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass: clevr_count_70k_reward_fn must use logger.info, not print,
# and must return a float.
# ---------------------------------------------------------------------------

def test_clevr_no_print_call(monkeypatch, capsys):
    """The reward fn must NOT call print() on a correct answer."""
    mod = _load_clevr_module()
    calls = []
    monkeypatch.setattr(
        mod, "print", lambda *a, **kw: calls.append((a, kw)), raising=False
    )
    result = mod.clevr_count_70k_reward_fn(
        prompt="how many?",
        completions="The count is [3]",
        prompt_ids=None,
        completion_ids=None,
        answer="3",
    )
    captured = capsys.readouterr()
    assert calls == [], f"reward fn called print(): {calls}"
    assert "completions:" not in captured.out, (
        f"reward fn leaked debug output to stdout: {captured.out!r}"
    )
    assert result == 1.0


def test_clevr_correct_answer_logs_via_logger(caplog):
    """On a correct answer, the reward fn must emit an INFO log via the
    'CLEVR70KReward' logger."""
    mod = _load_clevr_module()
    with caplog.at_level(logging.INFO, logger="CLEVR70KReward"):
        result = mod.clevr_count_70k_reward_fn(
            prompt="p",
            completions="answer is [7]",
            prompt_ids=None,
            completion_ids=None,
            answer="7",
        )
    assert result == 1.0
    clevr_records = [r for r in caplog.records if r.name == "CLEVR70KReward"]
    assert clevr_records, (
        "Expected at least one log record from logger 'CLEVR70KReward' "
        "but none were captured. The reward fn likely still uses print() "
        "or did not register a logger named 'CLEVR70KReward'."
    )
    joined = " ".join(r.getMessage() for r in clevr_records)
    assert "completions" in joined and "answer" in joined, (
        f"Log records do not mention completions/answer: {joined!r}"
    )


def test_clevr_returns_float_type():
    """The reward fn must return a Python float (not int)."""
    mod = _load_clevr_module()
    cases = [
        ("count is [4]", "4", 1.0),
        ("count is [4]", "5", 0.0),
        ("no answer here", "3", 0.0),  # extract_answer returns "" -> "" != "3"
    ]
    for completions, answer, expected in cases:
        r = mod.clevr_count_70k_reward_fn(
            prompt="p",
            completions=completions,
            prompt_ids=None,
            completion_ids=None,
            answer=answer,
        )
        assert isinstance(r, float), (
            f"Expected float, got {type(r).__name__} for ({completions!r}, {answer!r})"
        )
        assert r == expected, (
            f"Expected {expected}, got {r} for ({completions!r}, {answer!r})"
        )


def test_clevr_none_answer_returns_zero_float():
    mod = _load_clevr_module()
    r = mod.clevr_count_70k_reward_fn(
        prompt="p",
        completions="count is [3]",
        prompt_ids=None,
        completion_ids=None,
        answer=None,
    )
    assert isinstance(r, float)
    assert r == 0.0


# ---------------------------------------------------------------------------
# Pass-to-pass regression guard.
# ---------------------------------------------------------------------------

def test_clevr_extract_answer_preserved():
    """extract_answer must still return the last bracketed number."""
    mod = _load_clevr_module()
    assert mod.extract_answer("foo [1] bar [2.5] baz", data_name="") == "2.5"
    assert mod.extract_answer("no brackets here", data_name="") == ""


# ---------------------------------------------------------------------------
# Pass-to-pass: ruff lint + format on the changed files (repo CI/CD).
# ---------------------------------------------------------------------------

def test_ruff_lint_changed_files():
    """Repo's pinned ruff (0.14.9) must pass on the changed files."""
    env = os.environ.copy()
    env["RUFF_CACHE_DIR"] = _RUFF_CACHE
    r = subprocess.run(
        [
            "ruff", "check", "--no-cache",
            "--config", str(REPO / "pyproject.toml"),
            str(TYPES_PATH), str(CLEVR_PATH),
        ],
        capture_output=True, text=True, timeout=60, env=env, cwd="/tmp",
    )
    assert r.returncode == 0, (
        f"ruff lint failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


def test_ruff_format_changed_files():
    """ruff format --check must pass."""
    env = os.environ.copy()
    env["RUFF_CACHE_DIR"] = _RUFF_CACHE
    r = subprocess.run(
        [
            "ruff", "format", "--check", "--no-cache",
            "--config", str(REPO / "pyproject.toml"),
            str(TYPES_PATH), str(CLEVR_PATH),
        ],
        capture_output=True, text=True, timeout=60, env=env, cwd="/tmp",
    )
    assert r.returncode == 0, (
        f"ruff format check failed:\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass: byte-compile sanity check.
# ---------------------------------------------------------------------------

def test_changed_files_compile():
    r = subprocess.run(
        ["python", "-m", "py_compile", str(TYPES_PATH), str(CLEVR_PATH)],
        capture_output=True, text=True, timeout=30, cwd="/tmp",
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr}"
