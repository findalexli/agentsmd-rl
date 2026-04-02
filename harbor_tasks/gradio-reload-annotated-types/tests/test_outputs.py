"""
Task: gradio-reload-annotated-types
Repo: gradio-app/gradio @ c4986883b267570d76b442899c6fc09d14e3e222
PR:   12940

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import types
import __future__

REPO = "/workspace/gradio"
UTILS = f"{REPO}/gradio/utils.py"
SKILLS = f"{REPO}/gradio/cli/commands/skills.py"

CO_FUTURE_ANNOTATIONS = __future__.annotations.compiler_flag


def _find_code_object(module_code: types.CodeType, name: str) -> types.CodeType:
    """Find a named function's code object in compiled module code."""
    for const in module_code.co_consts:
        if isinstance(const, types.CodeType) and const.co_name == name:
            return const
    raise LookupError(f"No code object named {name!r} found in module")


def _compile_utils() -> types.CodeType:
    """Compile gradio/utils.py and return its module-level code object."""
    src = open(UTILS).read()
    return compile(src, UTILS, "exec")


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_utils_syntax():
    """gradio/utils.py must parse without syntax errors."""
    src = open(UTILS).read()
    ast.parse(src)


# [static] pass_to_pass
def test_skills_syntax():
    """gradio/cli/commands/skills.py must parse without syntax errors."""
    src = open(SKILLS).read()
    ast.parse(src)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_watchfn_no_future_annotations_flag():
    """watchfn code object must not carry CO_FUTURE_ANNOTATIONS flag.

    When utils.py has 'from __future__ import annotations', every function in
    the module inherits CO_FUTURE_ANNOTATIONS. This causes exec() inside
    watchfn to propagate the flag into user code, breaking Annotated types.
    """
    module_code = _compile_utils()
    watchfn_code = _find_code_object(module_code, "watchfn")
    has_flag = bool(watchfn_code.co_flags & CO_FUTURE_ANNOTATIONS)
    assert not has_flag, (
        "watchfn still has CO_FUTURE_ANNOTATIONS — "
        "from __future__ import annotations likely still present in utils.py"
    )


# [pr_diff] fail_to_pass
def test_annotated_class_hints_resolve():
    """Annotated class type hints resolve after exec with watchfn's compile flags.

    Simulates the reload path: compile user code using the same flags as
    watchfn, exec it, then call get_type_hints. On the buggy base, the
    inherited CO_FUTURE_ANNOTATIONS flag stringifies annotations, and
    get_type_hints raises on ForwardRef strings like 'Annotated[str, "desc"]'.
    """
    from typing import Annotated, get_type_hints

    module_code = _compile_utils()
    watchfn_code = _find_code_object(module_code, "watchfn")
    # Extract only the __future__-related flags (safe for compile())
    future_flags = watchfn_code.co_flags & CO_FUTURE_ANNOTATIONS

    user_code = (
        "from typing import Annotated\n"
        "class UserConfig:\n"
        "    name: Annotated[str, 'user name']\n"
        "    count: Annotated[int, 'item count']\n"
        "    flag: Annotated[bool, 'enabled']\n"
    )

    code = compile(user_code, "<reload>", "exec", flags=future_flags)
    ns: dict = {}
    exec(code, ns)

    hints = get_type_hints(ns["UserConfig"], include_extras=True)
    assert "name" in hints, "Missing 'name' in type hints"
    assert "count" in hints, "Missing 'count' in type hints"
    assert "flag" in hints, "Missing 'flag' in type hints"
    assert hints["name"] == Annotated[str, "user name"]
    assert hints["count"] == Annotated[int, "item count"]


# [pr_diff] fail_to_pass
def test_annotations_not_stringified_after_exec():
    """Function annotations are real type objects, not strings, after exec with watchfn's flags.

    When CO_FUTURE_ANNOTATIONS propagates into exec'd code, raw __annotations__
    contain strings instead of actual type objects. This test checks the raw
    annotations directly.
    """
    module_code = _compile_utils()
    watchfn_code = _find_code_object(module_code, "watchfn")
    future_flags = watchfn_code.co_flags & CO_FUTURE_ANNOTATIONS

    user_code = (
        "from typing import Annotated\n"
        "def process(x: Annotated[str, 'input'], n: Annotated[int, 'repeat']) "
        "-> Annotated[list, 'results']:\n"
        "    return [x] * n\n"
    )

    code = compile(user_code, "<reload>", "exec", flags=future_flags)
    ns: dict = {}
    exec(code, ns)

    func = ns["process"]
    for param_name, ann in func.__annotations__.items():
        assert not isinstance(ann, str), (
            f"Annotation for {param_name!r} is a string {ann!r} — "
            "CO_FUTURE_ANNOTATIONS is leaking into exec'd code"
        )


# [pr_diff] fail_to_pass
def test_forward_refs_are_quoted():
    """Forward-reference annotations (App, Blocks, etc.) must be string literals.

    When 'from __future__ import annotations' is removed, bare references to
    types like App and Blocks (forward refs due to circular imports) would cause
    NameError at import time. The fix must quote them as strings.

    # AST-only because: gradio cannot be imported (heavy deps + circular imports)
    """
    src = open(UTILS).read()
    tree = ast.parse(src)

    # These types are forward refs in utils.py — must be quoted after removing
    # from __future__ import annotations. Taken from the PR diff.
    forward_ref_names = {"App", "Blocks", "Component", "BlockContext",
                         "Request", "SessionState", "Button"}

    errors = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # Check return annotation
            if isinstance(node.returns, ast.Name) and node.returns.id in forward_ref_names:
                errors.append(f"{node.name}() return annotation: bare {node.returns.id}")
            # Check parameter annotations
            for arg in node.args.args + node.args.posonlyargs + node.args.kwonlyargs:
                if isinstance(arg.annotation, ast.Name) and arg.annotation.id in forward_ref_names:
                    errors.append(f"{node.name}({arg.arg}) annotation: bare {arg.annotation.id}")

    assert not errors, (
        "Found bare forward-reference annotations that would cause NameError:\n"
        + "\n".join(f"  - {e}" for e in errors)
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_utils_compiles_cleanly():
    """gradio/utils.py compiles without syntax errors after annotation changes."""
    module_code = _compile_utils()
    assert module_code is not None


# [static] pass_to_pass
def test_not_stub():
    """utils.py retains its full implementation (not stubbed out)."""
    src = open(UTILS).read()
    assert "def watchfn" in src, "watchfn function missing"
    assert "class BaseReloader" in src, "BaseReloader class missing"
    assert "def safe_join" in src, "safe_join function missing"
    assert len(src.splitlines()) > 400, "File suspiciously short — likely stubbed"
