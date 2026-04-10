"""
Task: areal-types-enum-logging-fix
Repo: inclusionAI/AReaL @ 4f5a2944f0acfebba378e5b88bf2ab940f84b943
PR:   #1008

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/AReaL"

TYPES_PY = f"{REPO}/areal/experimental/openai/types.py"
CLEVR_PY = f"{REPO}/areal/reward/clevr_count_70k.py"


def _mock_and_exec_clevr():
    """Exec clevr_count_70k.py with mocked areal.utils.logging (avoids torch)."""
    src = Path(CLEVR_PY).read_text()
    mock = (
        "import logging as _stdlib_logging\n"
        "class _MockLogging:\n"
        "    @staticmethod\n"
        "    def getLogger(name):\n"
        "        return _stdlib_logging.getLogger(name)\n"
        "logging = _MockLogging()\n"
    )
    modified = src.replace("from areal.utils import logging", mock)
    if "from areal.utils import logging" not in src:
        modified = mock + "\n" + src
    ns = {"re": re, "__builtins__": __builtins__}
    exec(compile(modified, "<clevr>", "exec"), ns)
    return ns


def _extract_enum_classes():
    """Extract ApiType and InputName enum classes from types.py (avoids torch/openai imports).

    AST-only because: types.py imports torch and openai at module level.
    """
    src = Path(TYPES_PY).read_text()
    tree = ast.parse(src)
    lines = src.splitlines(keepends=True)

    code_parts = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            chunk = "".join(lines[node.lineno - 1 : node.end_lineno])
            if any(kw in chunk for kw in ["torch", "openai", "areal", "__future__"]):
                continue
            code_parts.append(chunk)
        elif isinstance(node, ast.ClassDef) and node.name in ("ApiType", "InputName"):
            chunk = "".join(lines[node.lineno - 1 : node.end_lineno])
            code_parts.append(chunk)

    extracted = "\n".join(code_parts)
    if "from enum import" not in extracted and "import enum" not in extracted:
        extracted = "from enum import Enum\n" + extracted

    ns = {"__builtins__": __builtins__}
    exec(extracted, ns)
    return ns


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without syntax errors."""
    for path in [TYPES_PY, CLEVR_PY]:
        src = Path(path).read_text()
        compile(src, path, "exec")


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_reward_fn_returns_float():
    """Reward function must return float (not int) for correct, wrong, and no-match inputs."""
    ns = _mock_and_exec_clevr()
    fn = ns["clevr_count_70k_reward_fn"]

    cases = [
        ("the answer is [42]", "42", 1.0, "correct"),
        ("the answer is [99]", "42", 0.0, "wrong"),
        ("no brackets here", "42", 0.0, "no-match"),
        ("[7]", "7", 1.0, "single digit"),
        ("[3.14]", "3.14", 1.0, "decimal match"),
        ("[10]", "5", 0.0, "mismatch"),
    ]
    for completion, answer, expected, label in cases:
        r = fn("prompt", completion, [], [], answer)
        assert isinstance(r, float), f"{label}: returned {type(r).__name__}, expected float"
        assert r == expected, f"{label}: returned {r}, expected {expected}"


# [pr_diff] fail_to_pass
def test_enum_classes_str_compatible():
    """ApiType and InputName must be str-compatible Enum subclasses with correct values."""
    # AST-only because: types.py imports torch and openai at module level
    from enum import Enum

    ns = _extract_enum_classes()

    ApiType = ns.get("ApiType")
    InputName = ns.get("InputName")
    assert ApiType is not None, "ApiType class not found"
    assert InputName is not None, "InputName class not found"

    assert issubclass(ApiType, Enum), "ApiType does not inherit from Enum"
    assert issubclass(ApiType, str), "ApiType is not str-compatible (need str,Enum or StrEnum)"
    assert issubclass(InputName, Enum), "InputName does not inherit from Enum"
    assert issubclass(InputName, str), "InputName is not str-compatible"

    api_values = {m.value for m in ApiType}
    assert "completion" in api_values, 'ApiType missing "completion" value'
    assert "response" in api_values, 'ApiType missing "response" value'

    input_values = {m.value for m in InputName}
    assert "messages" in input_values, 'InputName missing "messages" value'
    assert "input_data" in input_values, 'InputName missing "input_data" value'

    # str-compatible means == comparison with raw strings works
    for member in ApiType:
        assert member == member.value, f'ApiType.{member.name} != "{member.value}"'
    for member in InputName:
        assert member == member.value, f'InputName.{member.name} != "{member.value}"'


# [pr_diff] fail_to_pass
def test_properties_use_enum_types():
    """api_type and input_name_for_logging properties must return enum instances, not bare strings."""
    # AST-only because: types.py imports torch and openai at module level
    src = Path(TYPES_PY).read_text()
    tree = ast.parse(src)

    cls_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "InteractionWithTokenLogpReward":
            cls_node = node
            break
    assert cls_node is not None, "InteractionWithTokenLogpReward class not found"

    for method in cls_node.body:
        if not isinstance(method, ast.FunctionDef):
            continue
        if method.name not in ("api_type", "input_name_for_logging"):
            continue

        returns = [n for n in ast.walk(method) if isinstance(n, ast.Return)]
        for ret in returns:
            if (
                ret.value
                and isinstance(ret.value, ast.Constant)
                and isinstance(ret.value.value, str)
            ):
                raise AssertionError(
                    f'{method.name} returns bare string "{ret.value.value}" instead of enum'
                )


# [pr_diff] fail_to_pass
def test_no_bare_print_uses_logger():
    """clevr_count_70k.py must not use bare print(); must use logger instead."""
    # AST-only because: checking for absence of print() requires full-file AST scan
    src = Path(CLEVR_PY).read_text()
    tree = ast.parse(src)

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "print":
                raise AssertionError("bare print() found in clevr_count_70k.py")

    has_logger = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr in ("info", "debug", "warning", "error", "critical")
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in ("logger", "log", "logging")
        ):
            has_logger = True
            break
    assert has_logger, "no logger/logging call found in clevr_count_70k.py"


# [pr_diff] fail_to_pass
def test_log_message_space_fix():
    """Warning message in to_tensor_dict must not have 'properly.Ignoring' (missing space)."""
    # AST-only because: to_tensor_dict requires torch tensors to execute
    src = Path(TYPES_PY).read_text()
    tree = ast.parse(src)

    func_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "to_tensor_dict":
            func_node = node
            break
    assert func_node is not None, "to_tensor_dict method not found in types.py"

    # Collect all string literal fragments within the method
    warning_strings = []
    for node in ast.walk(func_node):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            warning_strings.append(node.value)

    joined = "".join(warning_strings)
    # The bug: adjacent f-strings produce "properly.Ignoring" with no space
    assert "properly.I" not in joined, (
        "missing space after 'properly.' in to_tensor_dict warning message"
    )
    # Positive check: "properly." must be followed by a space
    if "properly." in joined:
        idx = joined.index("properly.") + len("properly.")
        assert idx < len(joined) and joined[idx] == " ", (
            "no space after 'properly.' in warning message"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_extract_answer_works():
    """extract_answer must still parse bracketed numbers correctly."""
    ns = _mock_and_exec_clevr()
    fn = ns["extract_answer"]

    assert fn("[42]", "") == "42", "single number extraction failed"
    assert fn("text [1.5] more [2.0]", "") == "2.0", "last-match extraction failed"
    assert fn("no brackets here", "") == "", "no-match should return empty string"
    assert fn("[7]", "") == "7", "single digit extraction failed"
    assert fn("[100]", "") == "100", "three digit extraction failed"


# [pr_diff] pass_to_pass
def test_reward_fn_edge_cases():
    """Reward function handles None answer and various inputs correctly."""
    ns = _mock_and_exec_clevr()
    fn = ns["clevr_count_70k_reward_fn"]

    r = fn("p", "[42]", [], [], None)
    assert r == 0 or r == 0.0, f"None answer should return 0, got {r!r}"

    for comp, ans in [("[100]", "100"), ("[0]", "0"), ("[55.5]", "55.5")]:
        r = fn("p", f"result is {comp}", [], [], ans)
        assert r == 1 or r == 1.0, f"correct match {comp}={ans} should return 1, got {r!r}"

    r = fn("p", "just text", [], [], "5")
    assert r == 0 or r == 0.0, f"no solution should return 0, got {r!r}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- AGENTS.md:30 @ 4f5a294
def test_no_wildcard_imports():
    """Modified files must not use wildcard imports (from x import *)."""
    # AST-only because: structural check for import style
    for path in [TYPES_PY, CLEVR_PY]:
        src = Path(path).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.names:
                for alias in node.names:
                    if alias.name == "*":
                        raise AssertionError(
                            f'wildcard import "from {node.module} import *" in {Path(path).name}'
                        )


# [agent_config] fail_to_pass -- AGENTS.md:99 @ 4f5a294
def test_reward_fn_has_return_annotation():
    """clevr_count_70k_reward_fn must have an explicit -> float return type annotation."""
    # AST-only because: checking annotation presence, not runtime behavior
    tree = ast.parse(Path(CLEVR_PY).read_text())

    fn_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "clevr_count_70k_reward_fn":
            fn_node = node
            break
    assert fn_node is not None, "clevr_count_70k_reward_fn not found"

    assert fn_node.returns is not None, (
        "clevr_count_70k_reward_fn has no return type annotation (expected '-> float')"
    )
    ann = fn_node.returns
    assert isinstance(ann, ast.Name) and ann.id == "float", (
        f"clevr_count_70k_reward_fn return annotation is '{ast.unparse(ann)}', expected 'float'"
    )


# [agent_config] fail_to_pass -- AGENTS.md:99 @ 4f5a294
def test_properties_annotated_with_enum_types():
    """api_type and input_name_for_logging properties must be annotated with enum types, not str."""
    # AST-only because: types.py imports torch and openai at module level
    src = Path(TYPES_PY).read_text()
    tree = ast.parse(src)

    cls_node = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "InteractionWithTokenLogpReward":
            cls_node = node
            break
    assert cls_node is not None, "InteractionWithTokenLogpReward class not found"

    expected = {"api_type": "ApiType", "input_name_for_logging": "InputName"}
    for method in cls_node.body:
        if not isinstance(method, ast.FunctionDef):
            continue
        if method.name not in expected:
            continue

        expected_type = expected[method.name]
        assert method.returns is not None, (
            f"{method.name} has no return type annotation (expected '-> {expected_type}')"
        )
        ann = method.returns
        ann_str = ast.unparse(ann)
        assert ann_str == expected_type, (
            f"{method.name} return annotation is '{ann_str}', expected '{expected_type}' not bare 'str'"
        )


# [agent_config] fail_to_pass -- AGENTS.md:89-91 @ 4f5a294
def test_reward_uses_areal_logging():
    """clevr_count_70k.py must import logging from areal.utils, not stdlib."""
    # AST-only because: checking import source module paths
    src = Path(CLEVR_PY).read_text()
    tree = ast.parse(src)

    uses_areal_logging = False
    uses_stdlib_logging = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and "areal" in node.module and any(
                a.name == "logging" for a in node.names
            ):
                uses_areal_logging = True
            elif node.module == "logging":
                uses_stdlib_logging = True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "logging":
                    uses_stdlib_logging = True

    assert uses_areal_logging, "clevr_count_70k.py must use 'from areal.utils import logging'"
    assert not uses_stdlib_logging, (
        "clevr_count_70k.py must not import stdlib logging directly -- use areal.utils.logging"
    )


# [agent_config] fail_to_pass -- AGENTS.md:89 @ 4f5a294
def test_logger_pascalcase_name():
    """getLogger in clevr_count_70k.py must use a PascalCase descriptive name."""
    # AST-only because: checking string argument convention
    tree = ast.parse(Path(CLEVR_PY).read_text())

    found = False
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "getLogger"
            and node.args
        ):
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                name = arg.value
                assert name and name[0].isupper(), (
                    f'getLogger("{name}") is not PascalCase'
                )
                assert len(name) >= 3, f'getLogger("{name}") is too short to be descriptive'
                found = True
                break

    assert found, "no getLogger call with string argument found in clevr_count_70k.py"


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass tests (added during p2p_enrichment)
# These verify the repo's own CI checks pass on base commit and after fix.
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_py_compile():
    """Modified Python files compile without syntax errors (pass_to_pass).

    Mirrors the repo's pre-commit check for Python file validity.
    """
    for path in [TYPES_PY, CLEVR_PY]:
        r = subprocess.run(
            ["python", "-m", "py_compile", path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"py_compile failed for {path}:\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_check():
    """Modified Python files pass ruff linting (pass_to_pass).

    Mirrors the repo's ruff pre-commit hook check.
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install might fail if already installed or network issues; ignore

    r = subprocess.run(
        ["ruff", "check", TYPES_PY, CLEVR_PY],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff check failed:\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_format():
    """Modified Python files are properly formatted (pass_to_pass).

    Mirrors the repo's ruff format pre-commit hook check.
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install might fail if already installed; ignore

    r = subprocess.run(
        ["ruff", "format", "--check", TYPES_PY, CLEVR_PY],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff format check failed (files need formatting):\n{r.stdout}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_ruff_check_fix():
    """Modified Python files have no auto-fixable lint issues (pass_to_pass).

    Mirrors the repo's ruff pre-commit hook check with --fix flag.
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install might fail if already installed or network issues; ignore

    r = subprocess.run(
        ["ruff", "check", "--fix", TYPES_PY, CLEVR_PY],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff check --fix failed:\\n{r.stdout}\\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_import_sorting():
    """Modified Python files follow isort conventions via ruff (pass_to_pass).

    Mirrors the repo's ruff isort check (part of pre-commit I rules).
    """
    r = subprocess.run(
        ["pip", "install", "ruff==0.14.9", "--quiet"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Install might fail if already installed or network issues; ignore

    r = subprocess.run(
        ["ruff", "check", "--select", "I", TYPES_PY, CLEVR_PY],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"ruff import sorting check failed:\\n{r.stdout}\\n{r.stderr}"
