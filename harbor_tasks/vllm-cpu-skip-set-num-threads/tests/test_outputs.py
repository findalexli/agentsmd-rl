"""
Task: vllm-cpu-skip-set-num-threads
Repo: vllm-project/vllm @ 677424c7acd9fb7477294017c99f798588002d4f
PR:   38535

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import io
import logging
import textwrap
import warnings
from pathlib import Path

import torch

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/v1/worker/cpu_worker.py"


def _extract_and_apply_patch():
    """Find the torch.set_num_threads monkey-patch in init_device, exec it.

    Returns the original torch.set_num_threads so callers can restore it.
    Raises AssertionError if no monkey-patch is found (i.e. base commit).

    AST-only because: cpu_worker.py imports vLLM C extensions and distributed
    modules that cannot be imported in a CPU-only test environment without the
    full vLLM build. We parse the source, extract the replacement function and
    assignment, then exec just the relevant snippet with mocked globals.
    """
    source = Path(TARGET).read_text()
    src_lines = source.splitlines(keepends=True)
    tree = ast.parse(source)

    # Locate CPUWorker.init_device
    init_device = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                    init_device = item
                    break
    assert init_device is not None, "CPUWorker.init_device not found"

    # Detect torch.set_num_threads reassignment (direct or via setattr)
    def is_set_num_threads_assign(n):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if (isinstance(t, ast.Attribute) and t.attr == "set_num_threads"
                        and isinstance(t.value, ast.Name) and t.value.id == "torch"):
                    return True
        if isinstance(n, ast.Expr) and isinstance(n.value, ast.Call):
            func = n.value.func
            if isinstance(func, ast.Name) and func.id == "setattr":
                args = n.value.args
                if (len(args) >= 3
                        and isinstance(args[0], ast.Name) and args[0].id == "torch"
                        and isinstance(args[1], ast.Constant)
                        and args[1].value == "set_num_threads"):
                    return True
        return False

    nodes = []
    found = False
    for n in ast.walk(init_device):
        if isinstance(n, ast.FunctionDef) and n is not init_device:
            nodes.append(n)
        if is_set_num_threads_assign(n):
            nodes.append(n)
            found = True

    assert found, "No torch.set_num_threads monkey-patch found in init_device"

    nodes.sort(key=lambda n: n.lineno)
    parts = []
    for n in nodes:
        chunk = "".join(src_lines[n.lineno - 1 : n.end_lineno])
        parts.append(textwrap.dedent(chunk))
    code = "\n".join(parts)

    original = torch.set_num_threads
    logger = logging.getLogger("vllm.v1.worker.cpu_worker")
    exec(code, {"torch": torch, "logger": logger, "__builtins__": __builtins__,
                "logging": logging})
    return original


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_set_num_threads_noop():
    """After monkey-patch, torch.set_num_threads must not change thread count."""
    original = _extract_and_apply_patch()
    try:
        baseline = torch.get_num_threads()
        for n in [1, 2, 4, 8, 16]:
            torch.set_num_threads(n)
            assert torch.get_num_threads() == baseline, (
                f"Thread count changed from {baseline} to {torch.get_num_threads()} "
                f"after set_num_threads({n})"
            )
    finally:
        torch.set_num_threads = original


# [pr_diff] fail_to_pass
def test_warning_logged():
    """Monkey-patched set_num_threads emits a log or warning when called."""
    original = _extract_and_apply_patch()
    try:
        # Capture logging from any logger (not just vllm-specific)
        log_buf = io.StringIO()
        handler = logging.StreamHandler(log_buf)
        handler.setLevel(logging.DEBUG)
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        old_level = root_logger.level
        root_logger.setLevel(logging.DEBUG)

        # Also capture Python warnings
        with warnings.catch_warnings(record=True) as caught_warnings:
            warnings.simplefilter("always")
            torch.set_num_threads(2)
            torch.set_num_threads(8)

        log_output = log_buf.getvalue()
        root_logger.removeHandler(handler)
        root_logger.setLevel(old_level)

        has_log = bool(log_output.strip())
        has_warnings = len(caught_warnings) > 0
        assert has_log or has_warnings, (
            "No log output or warnings when calling patched set_num_threads"
        )
    finally:
        torch.set_num_threads = original


# [pr_diff] fail_to_pass
# AST-only because: cpu_worker.py imports vLLM C extensions and distributed
# modules that cannot be imported in a CPU-only test environment
def test_patch_after_thread_binding():
    """Monkey-patch must appear after init_cpu_threads_env in source order."""
    source = Path(TARGET).read_text()
    src_lines = source.splitlines()
    tree = ast.parse(source)

    init_device = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                    init_device = item
                    break
    assert init_device is not None, "CPUWorker.init_device not found"

    # Find init_cpu_threads_env call line
    init_env_line = None
    for lineno in range(init_device.lineno, init_device.end_lineno + 1):
        if lineno <= len(src_lines) and "init_cpu_threads_env" in src_lines[lineno - 1]:
            init_env_line = lineno
            break
    assert init_env_line is not None, "init_cpu_threads_env call not found in init_device"

    # Find torch.set_num_threads reassignment line
    patch_line = None
    for node in ast.walk(init_device):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if (isinstance(t, ast.Attribute) and t.attr == "set_num_threads"
                        and isinstance(t.value, ast.Name) and t.value.id == "torch"):
                    patch_line = node.lineno
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
            func = node.value.func
            if isinstance(func, ast.Name) and func.id == "setattr":
                args = node.value.args
                if (len(args) >= 3
                        and isinstance(args[0], ast.Name) and args[0].id == "torch"
                        and isinstance(args[1], ast.Constant)
                        and args[1].value == "set_num_threads"):
                    patch_line = node.lineno
    assert patch_line is not None, "No torch.set_num_threads reassignment found"
    assert patch_line > init_env_line, (
        f"Monkey-patch (L{patch_line}) must come after "
        f"init_cpu_threads_env (L{init_env_line})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
# AST-only because: cpu_worker.py cannot be imported (vLLM C extensions, GPU deps)
def test_init_device_exists():
    """CPUWorker class and init_device method must still exist."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)
    found_class = found_method = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
            found_class = True
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                    found_method = True
    assert found_class, "CPUWorker class not found"
    assert found_method, "init_device method not found in CPUWorker"


# [pr_diff] pass_to_pass
def test_key_functionality_preserved():
    """Distributed init and random seed setting must remain in cpu_worker.py."""
    content = Path(TARGET).read_text()
    assert "init_worker_distributed_environment" in content, \
        "init_worker_distributed_environment missing from cpu_worker.py"
    assert "set_random_seed" in content, \
        "set_random_seed missing from cpu_worker.py"


# [static] pass_to_pass
# AST-only because: cpu_worker.py cannot be imported (vLLM C extensions, GPU deps)
def test_replacement_has_body():
    """Replacement function must have real logic (logging/warning call), not just pass."""
    source = Path(TARGET).read_text()
    tree = ast.parse(source)

    init_device = None
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                    init_device = item
                    break
    assert init_device is not None

    # Find nested function(s) defined inside init_device that are assigned to
    # torch.set_num_threads
    nested_funcs = [
        n for n in ast.walk(init_device)
        if isinstance(n, ast.FunctionDef) and n is not init_device
    ]
    assert nested_funcs, "No replacement function defined inside init_device"

    for func in nested_funcs:
        # Verify the function body contains at least one Call (logging, warning, etc.)
        has_call = any(isinstance(n, ast.Call) for n in ast.walk(func))
        assert has_call, (
            f"Function '{func.name}' has no function calls — appears to be a stub"
        )
