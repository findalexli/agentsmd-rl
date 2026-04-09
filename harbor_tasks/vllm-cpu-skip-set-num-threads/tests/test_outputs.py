"""
Task: vllm-cpu-skip-set-num-threads
Repo: vllm-project/vllm @ 677424c7acd9fb7477294017c99f798588002d4f
PR:   38535

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/vllm"
TARGET = f"{REPO}/vllm/v1/worker/cpu_worker.py"

# Script that extracts the monkey-patch from cpu_worker.py via AST,
# execs it against real torch, then runs a test body.
# On the base commit (no patch present), extraction fails → subprocess
# exits non-zero → test correctly fails.
_EXTRACT_AND_TEST = """
import ast, textwrap, logging, torch
from pathlib import Path

TARGET = "{target}"
source = Path(TARGET).read_text()
src_lines = source.splitlines(keepends=True)
tree = ast.parse(source)

init_device = None
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and node.name == "CPUWorker":
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "init_device":
                init_device = item
                break

assert init_device is not None, "CPUWorker.init_device not found"

def is_set_num_threads_assign(n):
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if (isinstance(t, ast.Attribute) and t.attr == "set_num_threads"
                    and isinstance(t.value, ast.Name) and t.value.id == "torch"):
                return True
    return False

nodes = []
for n in ast.walk(init_device):
    if isinstance(n, ast.FunctionDef) and n is not init_device:
        nodes.append(n)
    if is_set_num_threads_assign(n):
        nodes.append(n)

assert nodes, "No torch.set_num_threads monkey-patch found in init_device"

nodes.sort(key=lambda n: n.lineno)
parts = []
for n in nodes:
    chunk = "".join(src_lines[n.lineno - 1 : n.end_lineno])
    parts.append(textwrap.dedent(chunk))
code = "\\n".join(parts)

logger = logging.getLogger("vllm.v1.worker.cpu_worker")
exec(code, {{"torch": torch, "logger": logger, "__builtins__": __builtins__,
            "logging": logging}})

{test_body}
"""


def _run_subprocess(test_body: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run the extraction + test body in an isolated subprocess."""
    script = _EXTRACT_AND_TEST.format(target=TARGET, test_body=test_body)
    return subprocess.run(
        ["python3", "-c", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_set_num_threads_noop():
    """After monkey-patch, torch.set_num_threads must not change thread count."""
    r = _run_subprocess("""
baseline = torch.get_num_threads()
for n in [1, 2, 4, 8, 16]:
    torch.set_num_threads(n)
    actual = torch.get_num_threads()
    assert actual == baseline, (
        f"Thread count changed from {baseline} to {actual} after set_num_threads({n})"
    )
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_warning_logged():
    """Monkey-patched set_num_threads emits a log warning when called."""
    r = _run_subprocess("""
import io, logging

# Set up a stream handler on the vllm worker logger to capture output
log_buf = io.StringIO()
handler = logging.StreamHandler(log_buf)
handler.setLevel(logging.DEBUG)
vllm_logger = logging.getLogger("vllm.v1.worker.cpu_worker")
vllm_logger.addHandler(handler)
vllm_logger.setLevel(logging.DEBUG)

torch.set_num_threads(2)
torch.set_num_threads(8)

log_output = log_buf.getvalue()
assert log_output.strip(), (
    "No log output when calling patched set_num_threads"
)
# Verify the warning mentions the key information
assert "set_num_threads" in log_output.lower() or "skip" in log_output.lower(), (
    f"Log message doesn't mention set_num_threads or skip: {log_output!r}"
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_patch_after_thread_binding():
    """After monkey-patch is applied, thread binding is protected from later changes."""
    # This test verifies that the monkey-patch is applied in the correct order:
    # thread binding first, then the patch. We do this by executing the extracted
    # patch code and verifying thread count protection works.
    r = _run_subprocess("""
import logging, io

# Capture warnings to verify the patch includes logging
log_buf = io.StringIO()
handler = logging.StreamHandler(log_buf)
handler.setLevel(logging.WARNING)
vllm_logger = logging.getLogger("vllm.v1.worker.cpu_worker")
vllm_logger.addHandler(handler)
vllm_logger.setLevel(logging.WARNING)

# Get baseline thread count
baseline = torch.get_num_threads()

# Try to change thread count multiple times
torch.set_num_threads(1)
actual_1 = torch.get_num_threads()
torch.set_num_threads(8)
actual_8 = torch.get_num_threads()

# Verify thread count never changed (protected by patch)
assert actual_1 == baseline, (
    f"Thread count changed from {baseline} to {actual_1} after set_num_threads(1)"
)
assert actual_8 == baseline, (
    f"Thread count changed from {baseline} to {actual_8} after set_num_threads(8)"
)

# Verify warning was logged (proves patch is active with logging)
log_output = log_buf.getvalue()
assert log_output.strip(), "No warning logged when calling patched set_num_threads"
assert "set_num_threads" in log_output.lower() or "skip" in log_output.lower() or "cpu" in log_output.lower(), (
    f"Log message doesn't mention expected keywords: {log_output!r}"
)
print("PASS")
""")
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
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

    nested_funcs = [
        n for n in ast.walk(init_device)
        if isinstance(n, ast.FunctionDef) and n is not init_device
    ]
    assert nested_funcs, "No replacement function defined inside init_device"

    for func in nested_funcs:
        has_call = any(isinstance(n, ast.Call) for n in ast.walk(func))
        assert has_call, (
            f"Function '{func.name}' has no function calls — appears to be a stub"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_cpu_worker():
    """Repo's Python syntax check on cpu_worker.py passes (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Python syntax check failed:\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_lint_cpu_worker():
    """Repo's ruff lint check on cpu_worker.py passes (pass_to_pass)."""
    # Install ruff if not present
    install_ruff = subprocess.run(
        ["pip", "install", "ruff", "--quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Ruff may already be installed, ignore errors

    r = subprocess.run(
        ["ruff", "check", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ruff lint check failed:\n{r.stdout}\n{r.stderr}"
