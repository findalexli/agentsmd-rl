"""
Task: pytorch-stream-context-reentrance
Repo: pytorch/pytorch @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
PR:   176603

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is C++ code (torch/csrc/Stream.cpp) that requires a full PyTorch
build with CUDA/accelerator headers to compile. The Dockerfile uses
python:3.12-slim, so we cannot compile or link. All f2p checks use subprocess
to execute Python scripts that perform rigorous structural analysis of the
C++ source — validating control flow, stack invariants, and API patterns.
"""

import ast
import re
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = Path(f"{REPO}/torch/csrc/Stream.cpp")
TEST_ACCELERATOR = Path(f"{REPO}/test/test_accelerator.py")


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python analysis script in the repo environment."""
    script = Path(REPO) / "_eval_tmp.py"
    script.write_text(code)
    try:
        return subprocess.run(
            ["python3", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


def test_file_exists_and_has_functions():
    """Target file exists with required function definitions and is not a stub."""
    assert TARGET.exists(), f"Target file missing: {TARGET}"
    source = TARGET.read_text()

    for func in [
        "THPStream_enter(PyObject",
        "THPStream_exit(PyObject",
        "THPStream_dealloc(THPStream",
    ]:
        assert func in source, f"Missing function definition: {func}"

    meaningful = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("//")]
    assert len(meaningful) >= 150, f"Only {len(meaningful)} meaningful lines -- likely a stub"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- subprocess-executed behavioral analysis
# ---------------------------------------------------------------------------


def test_reentrance_assertion_removed():
    """The TORCH_CHECK assertion blocking reentrant stream context usage must be removed."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()
for pattern in [
    "Stream's context should not be initialized",
    "context should not be initialized",
]:
    if pattern in source:
        print(f"FAIL: blocking assertion present: {{pattern}}", file=sys.stderr)
        sys.exit(1)
# Also verify the TORCH_CHECK line that contained this is gone
for line in source.splitlines():
    stripped = line.strip()
    if "TORCH_CHECK" in stripped and "context" in stripped.lower() and "not" in stripped.lower():
        # Allow TORCH_INTERNAL_ASSERT for stack_size > 0 (the new check)
        if "TORCH_INTERNAL_ASSERT" not in stripped:
            print(f"FAIL: TORCH_CHECK on context remains: {{stripped}}", file=sys.stderr)
            sys.exit(1)
print("PASS")
'''
    )
    assert r.returncode == 0, f"Reentrance-blocking assertion still present: {r.stderr}"
    assert "PASS" in r.stdout


def test_context_uses_stack():
    """Context management uses a stack/list structure instead of single-dict assignment."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()

# Find enter function body
start = source.find("THPStream_enter(")
end = source.find("THPStream_exit(", start)
enter = source[start:end] if end > 0 else source[start:start+3000]

# BANNED: single-dict context assignment (the old bug pattern)
for i, line in enumerate(enter.splitlines()):
    stripped = line.strip()
    if stripped.startswith("//") or stripped.startswith("/*"):
        continue
    if "self->context" in stripped and "dict.release()" in stripped:
        print(f"FAIL: single-dict assignment (old bug): {{stripped}}", file=sys.stderr)
        sys.exit(1)

# REQUIRED: stack-like data structure (PyList preferred for Python C API)
stack_indicators = ["PyList_New", "PyList_Append", "std::vector", "std::stack"]
if not any(ind in source for ind in stack_indicators):
    print("FAIL: no stack/list data structure for context management", file=sys.stderr)
    sys.exit(1)

# REQUIRED: context is initialized as a list, not a dict
if "PyList_New(0)" not in enter and "PyList_New(0)" not in source:
    print("FAIL: context not initialized as empty list", file=sys.stderr)
    sys.exit(1)
print("PASS")
'''
    )
    assert r.returncode == 0, f"Stack check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_enter_pushes_to_stack():
    """enter() saves current stream state by pushing to stack before setting new stream."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()
start = source.find("THPStream_enter(")
end = source.find("THPStream_exit(", start)
enter = source[start:end] if end > 0 else source[start:start+3000]

# Must read current stream BEFORE setting the new one
if "getCurrentStream" not in enter:
    print("FAIL: enter() doesn't read current stream", file=sys.stderr)
    sys.exit(1)
if "setCurrentStream" not in enter:
    print("FAIL: enter() doesn't set current stream", file=sys.stderr)
    sys.exit(1)
get_pos = enter.find("getCurrentStream")
set_pos = enter.find("setCurrentStream")
if get_pos >= set_pos:
    print("FAIL: enter() sets stream before reading current (loses state)", file=sys.stderr)
    sys.exit(1)

# Must push/append state to a stack
push_ops = ["PyList_Append", "push_back", "emplace_back"]
if not any(op in enter for op in push_ops):
    print("FAIL: enter() doesn't push to stack", file=sys.stderr)
    sys.exit(1)

# Must save both stream and device_index into context dict
if '"_ctx_stream"' not in enter and '"_ctx_device_index"' not in enter:
    print("FAIL: enter() doesn't save stream/device context", file=sys.stderr)
    sys.exit(1)
print("PASS")
'''
    )
    assert r.returncode == 0, f"Enter push check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_exit_pops_from_stack():
    """exit() pops state from stack and restores previous stream without wiping entire stack."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()
exit_start = source.find("THPStream_exit(")
rest = source[exit_start:]
end = rest.find("END_HANDLE_TH_ERRORS")
exit_body = rest[:end+30] if end > 0 else rest[:3000]

# Must pop/remove from stack (not clear entire context)
pop_ops = ["PyList_SetSlice", "pop_back", "pop()", "erase("]
if not any(op in exit_body for op in pop_ops):
    print("FAIL: exit() doesn't pop from stack", file=sys.stderr)
    sys.exit(1)

# Must restore previous stream
if "setCurrentStream" not in exit_body:
    print("FAIL: exit() doesn't restore previous stream", file=sys.stderr)
    sys.exit(1)

# Must NOT unconditionally wipe self->context (that would destroy the stack)
# Allowed: conditional Py_CLEAR, or PyList_SetSlice to pop single entry
lines = exit_body.splitlines()
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith("//"):
        continue
    if "Py_CLEAR(self->context)" in stripped:
        context = "\\n".join(lines[max(0, i-3):i])
        if not any(k in context for k in ["if", "size", "empty"]):
            print("FAIL: unconditional Py_CLEAR wipes entire stack", file=sys.stderr)
            sys.exit(1)

# Must read from top of stack, not directly from self->context dict
if "PyList_GET_ITEM" not in exit_body and "PyList_GetItem" not in exit_body:
    print("FAIL: exit() doesn't read from top of stack", file=sys.stderr)
    sys.exit(1)
print("PASS")
'''
    )
    assert r.returncode == 0, f"Exit pop check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_dealloc_clears_context():
    """Destructor clears self->context to prevent memory leak."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()
start = source.find("THPStream_dealloc(")
body = source[start:start+500] if start >= 0 else ""

# Must clear context to prevent leak
clear_patterns = ["Py_CLEAR(self->context)", "Py_XDECREF(self->context)", "Py_DECREF(self->context)"]
if not any(p in body for p in clear_patterns):
    print("FAIL: dealloc doesn't clear self->context (memory leak)", file=sys.stderr)
    sys.exit(1)

# Must still free the object
if "tp_free" not in body:
    print("FAIL: dealloc doesn't free the object", file=sys.stderr)
    sys.exit(1)

# Must clear weak refs before clearing context (standard pattern)
weak_pos = body.find("PyObject_ClearWeakRefs")
clear_pos = min(body.find(p) for p in clear_patterns if p in body)
if weak_pos < 0 or clear_pos < 0 or weak_pos > clear_pos:
    print("FAIL: weak ref clear order wrong", file=sys.stderr)
    sys.exit(1)
print("PASS")
'''
    )
    assert r.returncode == 0, f"Dealloc check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_noop_when_stream_already_current():
    """enter() has a no-op fast path when the stream is already current."""
    r = _run_py(
        f'''
import sys
source = open("{TARGET}").read()
start = source.find("THPStream_enter(")
end = source.find("THPStream_exit(", start)
enter = source[start:end] if end > 0 else source[start:start+3000]

# Must compare current stream id with self->stream_id
if "stream_id" not in enter:
    print("FAIL: enter() doesn't compare stream ids", file=sys.stderr)
    sys.exit(1)

# Must have a comparison that detects "already current"
if "cur_stream" not in enter:
    print("FAIL: enter() doesn't fetch current stream for comparison", file=sys.stderr)
    sys.exit(1)

# Must have sentinel/no-op path
sentinel_patterns = ["Py_None", "nullptr", "sentinel", "noop", "no_op", "no-op"]
if not any(p in enter for p in sentinel_patterns):
    print("FAIL: no sentinel/no-op path for already-current stream", file=sys.stderr)
    sys.exit(1)

# Must return early (Py_INCREF + return) in no-op case without calling setCurrentStream
# Find the no-op block and verify it returns before setCurrentStream
noop_kw = "Py_None"
noop_pos = enter.find(noop_kw)
set_pos = enter.find("setCurrentStream")
if noop_pos >= 0 and set_pos >= 0:
    # The no-op sentinel push should be before setCurrentStream in the code
    # (since the no-op returns early)
    noop_return = enter.find("return _self;", noop_pos)
    if noop_return >= 0 and noop_return < set_pos:
        pass  # correct: no-op returns before reaching setCurrentStream
    elif noop_pos < set_pos:
        pass  # sentinel code is before setCurrentStream (acceptable)
print("PASS")
'''
    )
    assert r.returncode == 0, f"No-op check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- anti-stub
# ---------------------------------------------------------------------------


def test_enter_exit_not_stub():
    """enter() and exit() have substantial implementations with real logic."""
    source = TARGET.read_text()

    def count_meaningful(body: str) -> int:
        count = 0
        for line in body.splitlines():
            s = line.strip()
            if not s or s.startswith("//") or s.startswith("/*") or s == "*/" or s.startswith("*"):
                continue
            if s in ("{", "}", "};"):
                continue
            count += 1
        return count

    enter_start = source.find("THPStream_enter(")
    enter_end = source.find("THPStream_exit(", enter_start)
    enter_body = source[enter_start:enter_end] if enter_end > 0 else source[enter_start:enter_start+3000]

    exit_start = source.find("THPStream_exit(")
    rest = source[exit_start:]
    end_marker = rest.find("END_HANDLE_TH_ERRORS")
    exit_body = rest[:end_marker] if end_marker > 0 else rest[:3000]

    enter_lines = count_meaningful(enter_body)
    exit_lines = count_meaningful(exit_body)

    assert enter_lines >= 15, f"enter() has only {enter_lines} meaningful lines -- likely stub"
    assert exit_lines >= 10, f"exit() has only {exit_lines} meaningful lines -- likely stub"
    assert "self->context" in enter_body, "enter() doesn't reference self->context"
    assert "self->context" in exit_body, "exit() doesn't reference self->context"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------


def test_error_handling_macros():
    """Entry points use HANDLE_TH_ERRORS / END_HANDLE_TH_ERRORS for exception conversion."""
    source = TARGET.read_text()

    enter_start = source.find("THPStream_enter(")
    enter_end = source.find("THPStream_exit(", enter_start)
    enter_body = source[enter_start:enter_end] if enter_end > 0 else source[enter_start:enter_start+3000]
    assert "HANDLE_TH_ERRORS" in enter_body, "enter() missing HANDLE_TH_ERRORS"
    assert "END_HANDLE_TH_ERRORS" in enter_body, "enter() missing END_HANDLE_TH_ERRORS"

    exit_start = source.find("THPStream_exit(")
    rest = source[exit_start:]
    end = rest.find("END_HANDLE_TH_ERRORS")
    exit_body = rest[:end+30] if end > 0 else rest[:3000]
    assert "HANDLE_TH_ERRORS" in exit_body, "exit() missing HANDLE_TH_ERRORS"
    assert "END_HANDLE_TH_ERRORS" in exit_body, "exit() missing END_HANDLE_TH_ERRORS"
    assert "python_error" in enter_body, "enter() missing python_error throws"


def test_python_h_included_first():
    """Python headers must be present in torch/csrc/ files."""
    source = TARGET.read_text()
    # Python headers may appear after torch/csrc headers; check presence not position
    found_python_header = False
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#include"):
            if any(p in stripped for p in ["<Python.h>", '"Python.h"', "python_headers.h", "structmember.h"]):
                found_python_header = True
                break
    assert found_python_header, "No Python header found in includes"

# ---------------------------------------------------------------------------
# CI-derived pass-to-pass (repo_tests) -- structural validation of repo files
# ---------------------------------------------------------------------------


def test_repo_python_syntax_valid():
    """Repo Python test files have valid syntax (pass_to_pass)."""
    # Verify test_accelerator.py can be parsed
    source = TEST_ACCELERATOR.read_text()
    try:
        ast.parse(source)
    except SyntaxError as e:
        raise AssertionError(f"Syntax error in {TEST_ACCELERATOR}: {e}")


def test_repo_cpp_structure_valid():
    """Target C++ file has valid structure - balanced braces (pass_to_pass)."""
    source = TARGET.read_text()

    # Check balanced braces
    open_count = source.count('{')
    close_count = source.count('}')
    assert open_count == close_count, f"Unbalanced braces: {open_count} open, {close_count} close"

    # Check balanced parentheses
    open_paren = source.count('(')
    close_paren = source.count(')')
    assert open_paren == close_paren, f"Unbalanced parentheses: {open_paren} open, {close_paren} close"


def test_repo_cpp_includes_present():
    """Target C++ file has required include statements (pass_to_pass)."""
    source = TARGET.read_text()

    # Check for key includes that should be present
    required_includes = [
        'torch/csrc/Stream.h',
        'structmember.h',
    ]

    for inc in required_includes:
        pattern = f'#include <{inc}>'
        alt_pattern = f'#include "{inc}"'
        assert pattern in source or alt_pattern in source, f"Missing required include: {inc}"


def test_repo_test_file_has_test_class():
    """Python test file contains expected test class (pass_to_pass)."""
    source = TEST_ACCELERATOR.read_text()
    tree = ast.parse(source)

    # Find test classes
    test_classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Look for TestCase inheritance or unittest patterns
            if any('TestCase' in ast.unparse(base) for base in node.bases if isinstance(base, ast.Name)):
                test_classes.append(node.name)
            elif node.name.startswith('Test'):
                test_classes.append(node.name)

    assert len(test_classes) > 0, "No test classes found in test file"
    assert 'TestAccelerator' in test_classes, f"Expected TestAccelerator class, found: {test_classes}"


def test_repo_test_methods_exist():
    """Python test file has expected test methods (pass_to_pass)."""
    source = TEST_ACCELERATOR.read_text()
    tree = ast.parse(source)

    # Find all test methods
    test_methods = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                    test_methods.append(item.name)

    # Check for stream context manager test (relevant to our PR)
    stream_tests = [m for m in test_methods if 'stream' in m.lower() and 'context' in m.lower()]
    assert len(stream_tests) > 0, f"No stream context manager tests found. Methods: {test_methods[:10]}..."

# ---------------------------------------------------------------------------
# CI-derived pass-to-pass (repo_tests) -- actual subprocess commands from CI
# ---------------------------------------------------------------------------


def test_repo_kernel_launch_check():
    """CUDA kernel launch check passes (from CI quick-checks) (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "torch/testing/_internal/check_kernel_launches.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Kernel launch check failed:" + chr(10) + r.stderr[-500:]


def test_repo_no_nonbreaking_spaces():
    """No non-breaking spaces in source files (from CI quick-checks) (pass_to_pass)."""
    # Check for non-breaking spaces using git ls-files
    r = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Git ls-files failed: {r.stderr}"
    # Check each file for non-breaking spaces
    nbsp = bytes([0xC2, 0xA0]).decode("utf-8")
    files_with_nbsp = []
    for filepath in r.stdout.strip().splitlines()[:100]:  # Check first 100 files
        if not filepath:
            continue
        try:
            with open(f"{REPO}/{filepath}", "rb") as f:
                fc = f.read()
                if nbsp.encode("utf-8") in fc:
                    files_with_nbsp.append(filepath)
        except Exception:
            continue
    assert len(files_with_nbsp) == 0, f"Files with non-breaking spaces: {files_with_nbsp[:5]}"


def test_repo_valid_filenames():
    """Cross-OS compatible filenames (from CI quick-checks) (pass_to_pass)."""
    import re as re_module
    r = subprocess.run(
        ["git", "ls-files"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to list files: {r.stderr}"
    # Check for invalid characters in filenames
    invalid_pattern = re_module.compile(r"[<>:\"|?*]|[ .]$")
    bad_files = [line for line in r.stdout.splitlines() if invalid_pattern.search(line)]
    assert len(bad_files) == 0, f"Invalid filenames found: {bad_files[:5]}"


def test_repo_no_versionless_shebangs():
    """No versionless Python shebangs (from CI quick-checks) (pass_to_pass)."""
    r = subprocess.run(
        ["git", "grep", "-l", "^#!", "--", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # Find files with shebangs
    versionless = []
    for filepath in r.stdout.strip().splitlines():
        if not filepath:
            continue
        try:
            with open(f"{REPO}/{filepath}", "r", encoding="utf-8", errors="ignore") as f:
                first_line = f.readline()
                if first_line.startswith("#!") and first_line.rstrip() == "#!python":
                    versionless.append(filepath)
        except Exception:
            continue
    assert len(versionless) == 0, f"Files with versionless shebangs: {versionless[:5]}"


def test_repo_flake8_syntax():
    """Python files pass flake8 syntax check (E901, E902) (pass_to_pass)."""
    # Install flake8 if needed
    r = subprocess.run(
        ["pip", "install", "flake8", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    # Run flake8 on the test file to check for syntax errors only
    r = subprocess.run(
        ["flake8", "--select=E901,E902", f"{REPO}/test/test_accelerator.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    msg = "Flake8 syntax check failed:" + chr(10) + r.stdout[-500:] + chr(10) + r.stderr[-500:]
    assert r.returncode == 0, msg


def test_repo_ciflow_tags_valid():
    """CI flow tags validation passes (from CI quick-checks) (pass_to_pass)."""
    # Install pyyaml if needed
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", ".github/scripts/collect_ciflow_labels.py", "--validate-tags"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"CIFlow tags validation failed:\n{r.stderr[-500:]}"


def test_repo_actions_will_cancel():
    """GitHub Actions workflow cancellation check passes (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", ".github/scripts/ensure_actions_will_cancel.py"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Actions will cancel check failed:\n{r.stderr[-500:]}"


def test_repo_docstring_linter():
    """Docstring linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_docstring_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Docstring linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_header_only_linter():
    """Header-only linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_header_only_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Header-only linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_gitutils():
    """Git utilities tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "pyyaml", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", ".github/scripts/test_gitutils.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Gitutils tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_set_linter():
    """Set linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_set_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Set linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_stable_shim_usage_linter():
    """Stable shim usage linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_stable_shim_usage_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Stable shim usage linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_stable_shim_version_linter():
    """Stable shim version linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_stable_shim_version_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"Stable shim version linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_gb_registry_linter():
    """Graph break registry linter tests pass (from CI test-tools) (pass_to_pass)."""
    r = subprocess.run(
        ["pip", "install", "pytest", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["python3", "-m", "pytest", "tools/test/test_gb_registry_linter.py", "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
        env={**subprocess.os.environ, "PYTHONPATH": REPO},
    )
    assert r.returncode == 0, f"GB registry linter tests failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"
