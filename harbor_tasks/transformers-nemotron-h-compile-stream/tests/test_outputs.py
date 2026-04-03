"""
Task: transformers-nemotron-h-compile-stream
Repo: huggingface/transformers @ 20a233bdc5c0fae8fa116184f105adf498d44ba2
PR:   #44854

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/transformers"
MODELING = f"{REPO}/src/transformers/models/nemotron_h/modeling_nemotron_h.py"
MODULAR = f"{REPO}/src/transformers/models/nemotron_h/modular_nemotron_h.py"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_class_method(tree, class_name, method_name):
    """Return the AST node for a method in a class, or None."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == method_name:
                    return item
    return None


def _method_has_pattern(method_node, pattern_check):
    """Walk a method's AST and return True if pattern_check(child) is True for any node."""
    for child in ast.walk(method_node):
        if pattern_check(child):
            return True
    return False


def _is_cuda_stream_call(node):
    if isinstance(node, ast.Call):
        dump = ast.dump(node)
        return "cuda" in dump and "stream" in dump and "default_stream" in dump
    return False


def _is_nullcontext_call(node):
    if isinstance(node, ast.Call):
        return "nullcontext" in ast.dump(node)
    return False


def _is_compile_guard_call(node):
    if isinstance(node, ast.Call):
        dump = ast.dump(node)
        return "torchdynamo_compiling" in dump or "is_compiling" in dump
    return False


def _is_stream_attr(node):
    if isinstance(node, ast.Attribute):
        dump = ast.dump(node)
        return "stream" in dump and ("cuda" in dump or "default_stream" in dump)
    return False


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modeling and modular files must parse without errors."""
    # AST-only because: torch/CUDA deps make these files unimportable on CPU
    for path in [MODELING, MODULAR]:
        src = Path(path).read_text()
        ast.parse(src)  # Raises SyntaxError on failure


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core fix verification
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_block_forward_no_stream_context():
    """NemotronHBlock.forward must not create a stream context (cuda.stream or nullcontext).

    The bug: Block.forward created a temporary torch.cuda.Stream on every call.
    During torch.compile, Dynamo stores a weakref to it; the local stream gets GC'd,
    leaving a dangling pointer -> segfault. The fix removes stream management from Block.forward.
    """
    # AST-only because: NemotronHBlock requires torch.nn.Module + CUDA runtime
    tree = ast.parse(Path(MODELING).read_text())
    fwd = _find_class_method(tree, "NemotronHBlock", "forward")
    assert fwd is not None, "NemotronHBlock.forward not found"

    assert not _method_has_pattern(fwd, _is_cuda_stream_call), \
        "NemotronHBlock.forward still creates torch.cuda.stream context"
    assert not _method_has_pattern(fwd, _is_nullcontext_call), \
        "NemotronHBlock.forward still uses nullcontext"


# [pr_diff] fail_to_pass
def test_mixer_stream_with_compile_guard():
    """NemotronHMamba2Mixer must have CUDA stream management guarded by is_torchdynamo_compiling.

    The fix moves stream management into the mixer's forward (or cuda_kernels_forward),
    where it belongs, and guards the CUDA fast path with a compile check so torch.compile
    never traces through the stream creation.
    """
    # AST-only because: NemotronHMamba2Mixer requires torch + mamba_ssm CUDA kernels
    tree = ast.parse(Path(MODELING).read_text())

    has_stream = False
    has_guard = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHMamba2Mixer":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and item.name in ("forward", "cuda_kernels_forward"):
                    has_stream = has_stream or _method_has_pattern(item, _is_stream_attr)
                    has_guard = has_guard or _method_has_pattern(item, _is_compile_guard_call)
            break

    assert has_stream, "NemotronHMamba2Mixer missing CUDA stream management in forward/cuda_kernels_forward"
    assert has_guard, "NemotronHMamba2Mixer missing compile guard (is_torchdynamo_compiling)"


# [pr_diff] fail_to_pass
def test_modular_block_no_stream_context():
    """Modular NemotronHBlock.forward must also not have the stream context pattern.

    Both the modular source and the generated modeling file need consistent fixes.
    """
    # AST-only because: modular file imports torch + model-specific CUDA modules
    tree = ast.parse(Path(MODULAR).read_text())
    fwd = _find_class_method(tree, "NemotronHBlock", "forward")

    if fwd is None:
        # If NemotronHBlock doesn't override forward in modular, that's fine —
        # it means the stream context was removed by not overriding
        return

    assert not _method_has_pattern(fwd, _is_cuda_stream_call), \
        "Modular NemotronHBlock.forward still creates torch.cuda.stream context"
    assert not _method_has_pattern(fwd, _is_nullcontext_call), \
        "Modular NemotronHBlock.forward still uses nullcontext"


# [pr_diff] fail_to_pass
def test_no_contextlib_import():
    """Neither modeling nor modular file should import contextlib after the fix.

    The contextlib import was only used for nullcontext() in the old stream_context
    pattern. With stream management removed from Block.forward, it's unused.
    """
    for path, label in [(MODELING, "modeling"), (MODULAR, "modular")]:
        src = Path(path).read_text()
        tree = ast.parse(src)
        # AST-only because: torch deps make these unimportable; check import list
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name != "contextlib", \
                        f"{label} file still has 'import contextlib'"
            if isinstance(node, ast.ImportFrom) and node.module == "contextlib":
                assert False, f"{label} file still has 'from contextlib import ...'"


# [pr_diff] fail_to_pass
def test_modular_mixer_has_forward_override():
    """Modular NemotronHMamba2Mixer must override forward with compile guard and stream.

    The fix adds a forward() override to the modular Mixer class that guards the
    CUDA fast path with is_torchdynamo_compiling() and wraps it in a cuda stream.
    """
    # AST-only because: modular file imports torch + mamba CUDA kernels
    tree = ast.parse(Path(MODULAR).read_text())

    has_stream = False
    has_guard = False

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHMamba2Mixer":
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) \
                        and item.name in ("forward", "cuda_kernels_forward"):
                    has_stream = has_stream or _method_has_pattern(item, _is_stream_attr)
                    has_guard = has_guard or _method_has_pattern(item, _is_compile_guard_call)
            break

    assert has_stream, "Modular NemotronHMamba2Mixer missing CUDA stream in forward/cuda_kernels_forward"
    assert has_guard, "Modular NemotronHMamba2Mixer missing compile guard (is_torchdynamo_compiling)"


# [pr_diff] fail_to_pass
def test_is_fast_path_available_sentinel():
    """Both files must define is_fast_path_available = False at module level.

    The fix adds a module-level sentinel `is_fast_path_available = False` to ensure
    the CUDA kernel fast path is never taken (the mamba_ssm kernels aren't available).
    Without this, the variable would be undefined and the mixer's forward guard would fail.
    """
    # AST-only because: torch deps prevent importing these modules
    for path, label in [(MODELING, "modeling"), (MODULAR, "modular")]:
        tree = ast.parse(Path(path).read_text())
        found = False
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "is_fast_path_available":
                        # Must be assigned False (not True, not a variable)
                        if isinstance(node.value, ast.Constant) and node.value.value is False:
                            found = True
        assert found, f"{label} file missing module-level 'is_fast_path_available = False'"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_required_classes_preserved():
    """Core class structure must be intact in modeling file."""
    # AST-only because: can't import modeling file without torch/CUDA
    tree = ast.parse(Path(MODELING).read_text())

    required = {"NemotronHBlock", "NemotronHMamba2Mixer", "NemotronHPreTrainedModel", "NemotronHForCausalLM"}
    found = {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and node.name in required}
    missing = required - found
    assert not missing, f"Missing classes: {missing}"

    # NemotronHBlock must have forward and __init__
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHBlock":
            methods = {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            assert "forward" in methods, "NemotronHBlock missing forward"
            assert "__init__" in methods, "NemotronHBlock missing __init__"

    # NemotronHMamba2Mixer must have forward, torch_forward, cuda_kernels_forward
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "NemotronHMamba2Mixer":
            methods = {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            for m in ("forward", "torch_forward", "cuda_kernels_forward"):
                assert m in methods, f"NemotronHMamba2Mixer missing {m}"


# [pr_diff] fail_to_pass
def test_block_forward_not_stub():
    """NemotronHBlock.forward must have real implementation: residual add, mixer/norm calls, return."""
    # AST-only because: torch.nn.Module subclass, can't instantiate without CUDA
    tree = ast.parse(Path(MODELING).read_text())
    fwd = _find_class_method(tree, "NemotronHBlock", "forward")
    assert fwd is not None, "NemotronHBlock.forward not found"

    assert len(fwd.body) >= 4, f"forward too short ({len(fwd.body)} statements)"

    has_addition = _method_has_pattern(fwd, lambda n: isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add))
    has_call = _method_has_pattern(fwd, lambda n: isinstance(n, ast.Call))
    has_return = _method_has_pattern(fwd, lambda n: isinstance(n, ast.Return))

    assert has_addition, "forward missing residual connection (addition)"
    assert has_call, "forward missing function calls (norm/mixer)"
    assert has_return, "forward missing return statement"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:2 @ 20a233bdc5c0fae8fa116184f105adf498d44ba2
def test_ruff_lint():
    """Ruff lint on modified files (CLAUDE.md: 'make style: runs formatters and linters (ruff)')."""
    r = subprocess.run(
        ["ruff", "check", MODELING, MODULAR, "--quiet"],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Ruff errors:\n{r.stdout}\n{r.stderr}"
