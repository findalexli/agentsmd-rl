"""
Task: sglang-grammar-backend-think-end-id-tests
Repo: sgl-project/sglang @ 5dd2c243eb52dfd04f27b998e2595fe0c66437b1
PR:   #22158

Tests verify that create_grammar_backend test calls correctly pass think_end_id
as an explicit keyword argument instead of setting tokenizer.think_end_id.

Behavioral tests execute the actual repo test methods via subprocess, with
lightweight mocks for heavy dependencies (torch, etc.) that are not needed
for the tested logic.

Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/sglang"
TEST_FILE = f"{REPO}/test/registered/unit/constrained/test_base_grammar_backend.py"
PROD_FILE = f"{REPO}/python/sglang/srt/constrained/base_grammar_backend.py"

# ---------------------------------------------------------------------------
# Mock setup code: creates lightweight stubs for heavy deps (torch, etc.)
# and loads the actual production + test modules so they can be executed.
# ---------------------------------------------------------------------------
MOCK_SETUP = textwrap.dedent('''\
import sys, types

# Create namespace packages (avoid sglang.__init__ which needs numpy/torch)
sglang = types.ModuleType("sglang")
sglang.__path__ = ["/workspace/sglang/python/sglang"]
sglang.__package__ = "sglang"
sys.modules["sglang"] = sglang

sglang_srt = types.ModuleType("sglang.srt")
sglang_srt.__path__ = ["/workspace/sglang/python/sglang/srt"]
sglang_srt.__package__ = "sglang.srt"
sys.modules["sglang.srt"] = sglang_srt
sglang.srt = sglang_srt

sglang_srt_constrained = types.ModuleType("sglang.srt.constrained")
sglang_srt_constrained.__path__ = ["/workspace/sglang/python/sglang/srt/constrained"]
sglang_srt_constrained.__package__ = "sglang.srt.constrained"
sys.modules["sglang.srt.constrained"] = sglang_srt_constrained
sglang_srt.constrained = sglang_srt_constrained

# Mock torch (only used for type annotations in constrained modules)
class _FakeTensor: pass
_torch = types.ModuleType("torch")
_torch.Tensor = _FakeTensor
sys.modules["torch"] = _torch

# Minimal ServerArgs (needed by base_grammar_backend import)
from dataclasses import dataclass
from typing import Optional

@dataclass
class ServerArgs:
    grammar_backend: str = "outlines"
    reasoning_parser: Optional[str] = None
    constrained_json_whitespace_pattern: str = ""
    constrained_json_disable_any_whitespace: bool = False

_sa_mod = types.ModuleType("sglang.srt.server_args")
_sa_mod.ServerArgs = ServerArgs
sys.modules["sglang.srt.server_args"] = _sa_mod

# Mock CI registration (no-op)
for _n, _p in [
    ("sglang.test", ["/workspace/sglang/python/sglang/test"]),
    ("sglang.test.ci", ["/workspace/sglang/python/sglang/test/ci"]),
    ("sglang.test.ci.ci_register", None),
]:
    _m = types.ModuleType(_n)
    if _p: _m.__path__ = _p
    _m.__package__ = _n
    sys.modules[_n] = _m
sys.modules["sglang.test.ci.ci_register"].register_cpu_ci = lambda *a, **kw: None
sglang.test = sys.modules["sglang.test"]
sys.modules["sglang.test"].ci = sys.modules["sglang.test.ci"]
sys.modules["sglang.test.ci"].ci_register = sys.modules["sglang.test.ci.ci_register"]

# Load production constrained modules
import importlib.util
for _mod_name, _mod_path in [
    ("sglang.srt.constrained.base_grammar_backend",
     "/workspace/sglang/python/sglang/srt/constrained/base_grammar_backend.py"),
    ("sglang.srt.constrained.reasoner_grammar_backend",
     "/workspace/sglang/python/sglang/srt/constrained/reasoner_grammar_backend.py"),
]:
    _spec = importlib.util.spec_from_file_location(_mod_name, _mod_path)
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[_mod_name] = _mod
    setattr(sglang_srt_constrained, _mod_name.rsplit(".", 1)[1], _mod)
    _spec.loader.exec_module(_mod)

# Mock backend modules referenced by @patch decorators in test file
from unittest.mock import MagicMock as _MM
for _backend, _cls in [
    ("outlines_backend", "OutlinesGrammarBackend"),
    ("xgrammar_backend", "XGrammarGrammarBackend"),
    ("llguidance_backend", "GuidanceBackend"),
]:
    _fn = "sglang.srt.constrained." + _backend
    if _fn not in sys.modules:
        _bm = types.ModuleType(_fn)
        setattr(_bm, _cls, _MM())
        sys.modules[_fn] = _bm
        setattr(sglang_srt_constrained, _backend, _bm)

# Load the repo test module
_spec = importlib.util.spec_from_file_location(
    "test_base_grammar_backend",
    "/workspace/sglang/test/registered/unit/constrained/test_base_grammar_backend.py",
)
_test_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_test_mod)
''')


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified test file must parse without errors."""
    source = Path(TEST_FILE).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_think_end_id_passed_in_reasoner_test():
    """Execute test_reasoner_wrapping_on_builtin_backend and verify it passes.

    This test calls create_grammar_backend and asserts the result is a
    ReasonerGrammarBackend with think_end_id=42. It only passes when
    think_end_id is provided as an explicit keyword argument to the function.
    """
    script = MOCK_SETUP + textwrap.dedent('''\
import sys, unittest

suite = unittest.TestSuite()
suite.addTest(
    _test_mod.TestCreateGrammarBackend("test_reasoner_wrapping_on_builtin_backend")
)
result = unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)
if not result.wasSuccessful():
    for _, tb in result.failures + result.errors:
        print(tb, file=sys.stderr)
    sys.exit(1)
''')
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"test_reasoner_wrapping_on_builtin_backend failed when executed:\n"
        f"{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_think_end_id_none_in_no_wrapping_test():
    """Execute test_no_reasoner_wrapping_without_think_end_id with a spy on
    create_grammar_backend to verify think_end_id=None is passed as a kwarg."""
    script = MOCK_SETUP + textwrap.dedent('''\
import sys
from sglang.srt.constrained.base_grammar_backend import (
    create_grammar_backend as _real,
)

_captured_kwargs = []

def _spy(*args, **kwargs):
    _captured_kwargs.append(dict(kwargs))
    return _real(*args, **kwargs)

# Replace function reference in test module so test methods call our spy
_test_mod.create_grammar_backend = _spy

import unittest
suite = unittest.TestSuite()
suite.addTest(
    _test_mod.TestCreateGrammarBackend(
        "test_no_reasoner_wrapping_without_think_end_id"
    )
)
unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)

found = any(
    "think_end_id" in kw and kw["think_end_id"] is None for kw in _captured_kwargs
)
if not found:
    print(
        f"think_end_id=None not passed as kwarg: {_captured_kwargs}",
        file=sys.stderr,
    )
    sys.exit(1)
''')
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"think_end_id=None not passed as kwarg:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_think_end_id_passed_in_no_parser_test():
    """Execute test_no_reasoner_wrapping_without_reasoning_parser with a spy
    on create_grammar_backend to verify think_end_id=42 is passed as a kwarg.
    """
    script = MOCK_SETUP + textwrap.dedent('''\
import sys
from sglang.srt.constrained.base_grammar_backend import (
    create_grammar_backend as _real,
)

_captured_kwargs = []

def _spy(*args, **kwargs):
    _captured_kwargs.append(dict(kwargs))
    return _real(*args, **kwargs)

_test_mod.create_grammar_backend = _spy

import unittest
suite = unittest.TestSuite()
suite.addTest(
    _test_mod.TestCreateGrammarBackend(
        "test_no_reasoner_wrapping_without_reasoning_parser"
    )
)
unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)

found = any(
    "think_end_id" in kw and kw["think_end_id"] == 42 for kw in _captured_kwargs
)
if not found:
    print(
        f"think_end_id=42 not passed as kwarg: {_captured_kwargs}",
        file=sys.stderr,
    )
    sys.exit(1)
''')
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"think_end_id=42 not passed as kwarg:\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_no_tokenizer_think_end_id_assignment():
    """Run the affected test methods and verify none of them set
    tokenizer.think_end_id as an attribute (dead code from the old API).

    Uses a MagicMock subclass that detects think_end_id assignments, then
    checks that no such assignment occurred during test execution.
    """
    script = MOCK_SETUP + textwrap.dedent('''\
import sys
import unittest
import unittest.mock

_assignments = []

class _TrackingMock(unittest.mock.MagicMock):
    def __setattr__(self, name, value):
        if name == "think_end_id":
            _assignments.append(value)
        super().__setattr__(name, value)

# Replace MagicMock in test module so tokenizer mocks are tracked
_test_mod.MagicMock = _TrackingMock

suite = unittest.TestSuite()
for name in [
    "test_custom_backend_skips_reasoner_wrapping",
    "test_reasoner_wrapping_on_builtin_backend",
    "test_no_reasoner_wrapping_without_think_end_id",
    "test_no_reasoner_wrapping_without_reasoning_parser",
]:
    suite.addTest(_test_mod.TestCreateGrammarBackend(name))

unittest.TextTestRunner(verbosity=0, stream=open("/dev/null", "w")).run(suite)

if _assignments:
    print(
        f"tokenizer.think_end_id set {len(_assignments)} time(s): {_assignments}",
        file=sys.stderr,
    )
    sys.exit(1)
''')
    r = subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"tokenizer.think_end_id still assigned in test methods:\n{r.stderr}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_production_function_has_think_end_id_param():
    """Production create_grammar_backend must accept think_end_id parameter.

    This is a sanity check that the base commit has the updated API.
    """
    source = Path(PROD_FILE).read_text()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "create_grammar_backend":
            param_names = [arg.arg for arg in node.args.args]
            kwonly_names = [arg.arg for arg in node.args.kwonlyargs]
            assert "think_end_id" in param_names or "think_end_id" in kwonly_names, \
                f"create_grammar_backend does not accept think_end_id. Params: {param_names}, kwonly: {kwonly_names}"
            return
    raise AssertionError("create_grammar_backend function not found in production code")


# [static] pass_to_pass
def test_test_methods_preserved():
    """All original test methods must still exist (agent didn't delete tests)."""
    source = Path(TEST_FILE).read_text()
    tree = ast.parse(source)
    methods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TestCreateGrammarBackend":
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    methods.add(item.name)
    required = [
        "test_reasoner_wrapping_on_builtin_backend",
        "test_no_reasoner_wrapping_without_think_end_id",
        "test_no_reasoner_wrapping_without_reasoning_parser",
        "test_custom_backend_skips_reasoner_wrapping",
    ]
    for name in required:
        assert name in methods, f"Required test method {name} was deleted"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_test_file():
    """Test file must have valid Python syntax (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", f"import ast; ast.parse(open('{TEST_FILE}').read())"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Syntax error in test file:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_test_file():
    """Test file must pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_test_file():
    """Test file must pass black formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Black check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_ruff_prod_file():
    """Production file must pass ruff linting (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", "--select=E9,F63,F7,F82", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Ruff check failed on production file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_black_prod_file():
    """Production file must pass black formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "black", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["black", "--check", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Black check failed on production file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort_test_file():
    """Test file must pass isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"isort check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_isort_prod_file():
    """Production file must pass isort import sorting check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "isort", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["isort", "--check-only", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"isort check failed on production file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_codespell_test_file():
    """Test file must pass codespell spell check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["codespell", "--config", f"{REPO}/.codespellrc", TEST_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"codespell check failed on test file:\n{r.stdout}{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_codespell_prod_file():
    """Production file must pass codespell spell check (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "codespell", "-q"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    r = subprocess.run(
        ["codespell", "--config", f"{REPO}/.codespellrc", PROD_FILE],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"codespell check failed on production file:\n{r.stdout}{r.stderr}"
