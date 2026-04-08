"""
Task: sglang-mistral-ci-ratelimit-patch
Repo: sgl-project/sglang @ 33cca495ae75e745be62b5b009f4c87fb40dd044
PR:   21729

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import contextlib
import logging
import subprocess
import sys
import textwrap
import types
from pathlib import Path

REPO = "/repo"
TARGET = f"{REPO}/python/sglang/srt/utils/hf_transformers_utils.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code in a subprocess within the repo directory."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _extract_source_range(source, tree, names):
    """Extract module-level declarations (assignments + functions) by name."""
    lines = source.splitlines(keepends=True)
    chunks = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
        elif isinstance(node, ast.FunctionDef) and node.name in names:
            chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    return "\n\n".join(chunks)


@contextlib.contextmanager
def _patch_env(ci_mode, transformers_version="5.3.0"):
    """Context manager: exec extracted patch code with mocked sglang/transformers deps.

    Yields (namespace, mock_tut) where namespace has the extracted functions and
    mock_tut is the mock transformers.tokenization_utils_tokenizers module.
    """
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    code = _extract_source_range(source, tree, {
        "_is_base_mistral_patched",
        "_TRANSFORMERS_PATCHED_VERSION",
        "_patch_is_base_mistral_in_ci",
    })
    if not code.strip():
        # Patch function doesn't exist (e.g. base commit) — yield None
        yield None, None
        return

    # Mock sglang.srt.environ.envs.SGLANG_IS_IN_CI
    mock_envs = types.SimpleNamespace(
        SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: ci_mode)
    )

    # Mock transformers and its submodule — use a single object so that
    # `import transformers.tokenization_utils_tokenizers as tut` (which
    # resolves via sys.modules["transformers"].tokenization_utils_tokenizers)
    # and sys.modules["transformers.tokenization_utils_tokenizers"] are the same.
    mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
    mock_tut.is_base_mistral = lambda model_id: True  # original behavior

    mock_transformers = types.ModuleType("transformers")
    mock_transformers.__version__ = transformers_version
    mock_transformers.tokenization_utils_tokenizers = mock_tut

    # Temporarily install mocks in sys.modules
    mock_modules = {
        "sglang": types.ModuleType("sglang"),
        "sglang.srt": types.ModuleType("sglang.srt"),
        "sglang.srt.environ": types.SimpleNamespace(envs=mock_envs),
        "transformers": mock_transformers,
        "transformers.tokenization_utils_tokenizers": mock_tut,
    }

    saved = {}
    for name, mod in mock_modules.items():
        saved[name] = sys.modules.get(name)
        sys.modules[name] = mod

    try:
        ns = {"logger": logging.getLogger("test_patch"), "__builtins__": __builtins__}
        exec(compile(code, "<patch>", "exec"), ns)
        yield ns, mock_tut
    finally:
        for name, orig in saved.items():
            if orig is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = orig


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """hf_transformers_utils.py must parse without syntax errors."""
    source = Path(TARGET).read_text()
    ast.parse(source)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_ci_patches_is_base_mistral():
    """In CI mode, _patch_is_base_mistral_in_ci replaces is_base_mistral with False."""
    r = _run_py("""\
import ast, types, sys, logging

TARGET = "/repo/python/sglang/srt/utils/hf_transformers_utils.py"
source = open(TARGET).read()
tree = ast.parse(source)

names = {
    "_is_base_mistral_patched",
    "_TRANSFORMERS_PATCHED_VERSION",
    "_patch_is_base_mistral_in_ci",
}
lines = source.splitlines(keepends=True)
chunks = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    elif isinstance(node, ast.FunctionDef) and node.name in names:
        chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))

code = "\\n\\n".join(chunks)
assert code.strip(), "Patch function _patch_is_base_mistral_in_ci not found"

mock_envs = types.SimpleNamespace(
    SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: True)
)
mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
mock_tut.is_base_mistral = lambda model_id: True
mock_tf = types.ModuleType("transformers")
mock_tf.__version__ = "5.3.0"
mock_tf.tokenization_utils_tokenizers = mock_tut

sys.modules["sglang"] = types.ModuleType("sglang")
sys.modules["sglang.srt"] = types.ModuleType("sglang.srt")
sys.modules["sglang.srt.environ"] = types.SimpleNamespace(envs=mock_envs)
sys.modules["transformers"] = mock_tf
sys.modules["transformers.tokenization_utils_tokenizers"] = mock_tut

ns = {"logger": logging.getLogger("test"), "__builtins__": __builtins__}
exec(compile(code, "<patch>", "exec"), ns)
ns["_patch_is_base_mistral_in_ci"]()

for model_id in ["mistralai/Mistral-7B", "some-other-model", "", "x" * 100]:
    result = mock_tut.is_base_mistral(model_id)
    assert result is False, f"Expected False for {model_id!r}, got {result!r}"

print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_idempotent_multiple_calls():
    """Calling _patch_is_base_mistral_in_ci multiple times doesn't break the patch."""
    r = _run_py("""\
import ast, types, sys, logging

TARGET = "/repo/python/sglang/srt/utils/hf_transformers_utils.py"
source = open(TARGET).read()
tree = ast.parse(source)

names = {
    "_is_base_mistral_patched",
    "_TRANSFORMERS_PATCHED_VERSION",
    "_patch_is_base_mistral_in_ci",
}
lines = source.splitlines(keepends=True)
chunks = []
for node in ast.iter_child_nodes(tree):
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))
    elif isinstance(node, ast.FunctionDef) and node.name in names:
        chunks.append("".join(lines[node.lineno - 1 : node.end_lineno]))

code = "\\n\\n".join(chunks)
assert code.strip(), "Patch function not found"

mock_envs = types.SimpleNamespace(
    SGLANG_IS_IN_CI=types.SimpleNamespace(get=lambda: True)
)
mock_tut = types.ModuleType("transformers.tokenization_utils_tokenizers")
mock_tut.is_base_mistral = lambda model_id: True
mock_tf = types.ModuleType("transformers")
mock_tf.__version__ = "5.3.0"
mock_tf.tokenization_utils_tokenizers = mock_tut

sys.modules["sglang"] = types.ModuleType("sglang")
sys.modules["sglang.srt"] = types.ModuleType("sglang.srt")
sys.modules["sglang.srt.environ"] = types.SimpleNamespace(envs=mock_envs)
sys.modules["transformers"] = mock_tf
sys.modules["transformers.tokenization_utils_tokenizers"] = mock_tut

ns = {"logger": logging.getLogger("test"), "__builtins__": __builtins__}
exec(compile(code, "<patch>", "exec"), ns)
patch_fn = ns["_patch_is_base_mistral_in_ci"]
for _ in range(5):
    patch_fn()
for model_id in ["model-a", "model-b", "model-c"]:
    result = mock_tut.is_base_mistral(model_id)
    assert result is False, f"Expected False for {model_id!r} after 5 calls"

print("PASS")
""")
    assert r.returncode == 0, f"Subprocess failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_patch_before_from_pretrained():
    """_patch_is_base_mistral_in_ci() is called before AutoTokenizer.from_pretrained in get_tokenizer."""
    # AST-only because: get_tokenizer has heavy deps (vllm, torch) that can't be imported
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_tokenizer":
            patch_line = None
            pretrained_line = None

            for child in ast.walk(node):
                if isinstance(child, ast.Call):
                    # _patch_is_base_mistral_in_ci()
                    if isinstance(child.func, ast.Name) and child.func.id == "_patch_is_base_mistral_in_ci":
                        patch_line = child.lineno
                    # AutoTokenizer.from_pretrained(...)
                    if (isinstance(child.func, ast.Attribute)
                            and child.func.attr == "from_pretrained"
                            and isinstance(child.func.value, ast.Name)
                            and child.func.value.id == "AutoTokenizer"):
                        if pretrained_line is None:
                            pretrained_line = child.lineno

            assert patch_line is not None, (
                "_patch_is_base_mistral_in_ci() not called in get_tokenizer"
            )
            assert pretrained_line is not None, (
                "AutoTokenizer.from_pretrained not found in get_tokenizer"
            )
            assert patch_line < pretrained_line, (
                f"Patch (line {patch_line}) must come before "
                f"from_pretrained (line {pretrained_line})"
            )
            return

    raise AssertionError("get_tokenizer function not found")


# [static] fail_to_pass
def test_not_stub():
    """File has non-trivial CI patching logic (not a stub)."""
    # AST-only because: module has heavy deps (torch, triton)
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    assert "is_base_mistral" in source, "File does not reference is_base_mistral"

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            body_types = {type(n).__name__ for n in ast.walk(node)}
            has_conditional = "If" in body_types
            has_import = "Import" in body_types or "ImportFrom" in body_types
            has_assign_or_global = "Global" in body_types or "Assign" in body_types
            stmt_count = sum(1 for n in ast.walk(node) if isinstance(n, ast.stmt))

            if has_conditional and has_import and has_assign_or_global and stmt_count >= 6:
                return

    raise AssertionError(
        "No function with CI patching logic found "
        "(need conditionals + imports + assignments, 6+ statements)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_patch_without_ci_env():
    """Without SGLANG_IS_IN_CI, is_base_mistral is NOT replaced."""
    with _patch_env(ci_mode=False) as (ns, mock_tut):
        if ns is None:
            return  # Patch function doesn't exist on base → trivially correct
        ns["_patch_is_base_mistral_in_ci"]()
        for model_id in ["test-1", "test-2", "test-3"]:
            assert mock_tut.is_base_mistral(model_id) is True, (
                "is_base_mistral should NOT be patched without CI env"
            )


# [pr_diff] pass_to_pass
def test_version_guard_skips_on_mismatch():
    """Mismatched transformers version causes patch to be skipped."""
    with _patch_env(ci_mode=True, transformers_version="99.0.0") as (ns, mock_tut):
        if ns is None:
            return  # Patch function doesn't exist on base → trivially correct
        ns["_patch_is_base_mistral_in_ci"]()
        for model_id in ["test-1", "test-2"]:
            assert mock_tut.is_base_mistral(model_id) is True, (
                "is_base_mistral should NOT be patched when version mismatches"
            )


# [pr_diff] pass_to_pass
def test_get_tokenizer_signature():
    """get_tokenizer function exists with expected parameters."""
    # AST-only because: get_tokenizer has heavy deps
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "get_tokenizer":
            pos_params = [arg.arg for arg in node.args.args]
            kw_params = [arg.arg for arg in node.args.kwonlyargs]
            all_params = pos_params + kw_params
            assert "tokenizer_name" in all_params, f"tokenizer_name not in params: {all_params}"
            assert "tokenizer_mode" in all_params, f"tokenizer_mode not in params: {all_params}"
            return

    raise AssertionError("get_tokenizer function not found")


# [pr_diff] pass_to_pass
def test_tokenizer_warnings_filter_exists():
    """TokenizerWarningsFilter class exists with a filter() method."""
    # AST-only because: module has heavy deps (torch, triton)
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "TokenizerWarningsFilter":
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            assert "filter" in methods, "TokenizerWarningsFilter missing filter() method"
            return

    raise AssertionError("TokenizerWarningsFilter class not found")
