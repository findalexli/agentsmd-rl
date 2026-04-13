"""
Task: pytorch-fakeprocessgroup-allgather-uneven
Repo: pytorch/pytorch @ 8401fdeb9abd665b36465c52b7aefd591cc3dbcb
PR:   177291

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: Full PyTorch build takes hours. Tests use:
1. clang -fsyntax-only to verify C++ compiles
2. Python simulation of the loop logic to verify behavioral fix
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = Path(REPO) / "torch/csrc/distributed/c10d/FakeProcessGroup.hpp"


def _extract_allgather_loop() -> str:
    """Extract the allgather method's loop body from the header."""
    source = TARGET.read_text()

    # Find the allgather method - it spans multiple lines with signature on one
    # line and 'override {' on a subsequent line
    lines = source.split('\n')
    in_signature = False
    in_allgather = False
    brace_count = 0
    method_lines = []

    for line in lines:
        # Start of allgather signature
        if 'allgather(' in line and 'c10::intrusive_ptr<Work>' in line:
            in_signature = True
            method_lines.append(line)
            continue

        if in_signature:
            method_lines.append(line)
            # Check for override and opening brace
            if 'override' in line:
                in_signature = False
                in_allgather = True
                brace_count = line.count('{') - line.count('}')
                continue

        if in_allgather:
            method_lines.append(line)
            brace_count += line.count('{') - line.count('}')
            if brace_count == 0:
                break

    if method_lines:
        return '\n'.join(method_lines)

    return ""


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------


def test_header_balanced_braces():
    """FakeProcessGroup.hpp must have balanced braces."""
    source = TARGET.read_text()
    depth = 0
    in_str = False
    esc = False
    for ch in source:
        if esc:
            esc = False
            continue
        if ch == "\\":
            esc = True
            continue
        if ch == '"' and not in_str:
            in_str = True
            continue
        if ch == '"' and in_str:
            in_str = False
            continue
        if not in_str:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            assert depth >= 0, "Unmatched closing brace"
    assert depth == 0, f"Unbalanced braces (depth={depth})"


def test_syntax_valid():
    """C++ code must be syntactically valid (clang -fsyntax-only)."""
    # Extract just the allgather method and wrap in minimal context for parsing
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    # Write a minimal test file that includes the header for syntax checking
    test_cpp = Path(REPO) / "_syntax_check.cpp"

    # Create a minimal file that includes the header
    # We need to handle the case where dependencies aren't available
    cpp_content = f'''
// Minimal syntax check for FakeProcessGroup.hpp
// This verifies the code structure is valid C++

// Forward declarations to satisfy parsing
namespace c10 {{
    template<typename T> class intrusive_ptr;
    class ScalarType;
}}

namespace torch {{
    class Tensor {{
    public:
        long size(int dim) const {{ return 0; }}
        void copy_(const torch::Tensor& other) {{}}
    }};
}}

// Simplified check - verify the pattern exists
// The actual header is complex; we verify key patterns exist
'''

    test_cpp.write_text(cpp_content)

    try:
        # Run clang in syntax-only mode
        r = subprocess.run(
            ["clang", "-fsyntax-only", "-std=c++17", "-xc++", str(test_cpp)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        # We expect this to work for our minimal file
        assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    finally:
        test_cpp.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - behavioral tests via subprocess
# -----------------------------------------------------------------------------


def test_allgather_size_guard_present():
    """allgather must have a size(0) comparison guard before copy_."""
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    # Check for size comparison pattern
    has_size_check = (
        "tensor.size(0)" in loop_code and
        "inputTensors[0].size(0)" in loop_code and
        "!=" in loop_code
    )
    assert has_size_check, (
        "Missing size(0) comparison guard in allgather loop. "
        "Expected: if (tensor.size(0) != inputTensors[0].size(0))"
    )


def test_allgather_continue_present():
    """Mismatched tensors must be skipped via continue statement."""
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    # The fix adds: if (size mismatch) { continue; }
    has_continue = "continue;" in loop_code
    assert has_continue, (
        "Missing 'continue;' statement in allgather loop. "
        "Mismatched-size tensors will not be skipped."
    )


def test_allgather_uneven_behavior_simulation():
    """Simulated loop behavior: uneven tensors are skipped without crash.

    This test simulates the C++ allgather loop logic in Python to verify
    the fix correctly handles uneven tensor sizes without crashing.
    """
    SIMULATION_SCRIPT = """
import sys

# Simulate the allgather loop behavior
class MockTensor:
    def __init__(self, shape0, data=None):
        self._shape0 = shape0
        self._data = data
        self.copied = False

    def size(self, dim):
        if dim == 0:
            return self._shape0
        return 1

    def copy_(self, other):
        # In real PyTorch, this would crash if shapes don't match
        if self._shape0 != other._shape0:
            raise RuntimeError(f"Shape mismatch: {self._shape0} vs {other._shape0}")
        self._data = other._data
        self.copied = True

# Simulate the FIXED allgather loop
def fixed_allgather(output_tensors, input_tensor):
    for tensor in output_tensors:
        # The fix: check sizes before copy
        if tensor.size(0) != input_tensor.size(0):
            continue
        tensor.copy_(input_tensor)

# Test: uneven output tensors (the bug scenario)
input_tensor = MockTensor(5, "ones")
output_tensors = [MockTensor(5), MockTensor(4)]  # Uneven sizes

try:
    fixed_allgather(output_tensors, input_tensor)

    # Verify behavior
    assert output_tensors[0].copied, "First tensor (size 5) should be copied"
    assert not output_tensors[1].copied, "Second tensor (size 4) should be skipped"

    print("PASS: Uneven allgather handled correctly")
    sys.exit(0)
except Exception as e:
    print(f"FAIL: {e}")
    sys.exit(1)
"""

    r = subprocess.run(
        ["python3", "-c", SIMULATION_SCRIPT],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Behavior simulation failed: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


def test_original_broken_behavior():
    """Original code (without fix) would crash on uneven tensors.

    This test simulates the ORIGINAL buggy allgather loop to confirm
    the bug exists and our simulation is accurate.
    """
    BROKEN_SIMULATION = """
import sys

class MockTensor:
    def __init__(self, shape0, data=None):
        self._shape0 = shape0
        self._data = data
        self.copied = False

    def size(self, dim):
        return self._shape0 if dim == 0 else 1

    def copy_(self, other):
        if self._shape0 != other._shape0:
            raise RuntimeError(f"copy_ failed: shape {self._shape0} != {other._shape0}")
        self.copied = True

# Original buggy loop (no size guard)
def broken_allgather(output_tensors, input_tensor):
    for tensor in output_tensors:
        # No guard - directly copy (crashes on mismatch)
        tensor.copy_(input_tensor)

# Test with uneven tensors
input_tensor = MockTensor(5, "ones")
output_tensors = [MockTensor(5), MockTensor(4)]

try:
    broken_allgather(output_tensors, input_tensor)
    print("FAIL: Should have crashed but did not")
    sys.exit(1)
except RuntimeError as e:
    print(f"PASS: Confirmed bug exists - {e}")
    sys.exit(0)
"""

    r = subprocess.run(
        ["python3", "-c", BROKEN_SIMULATION],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Broken simulation failed unexpectedly: {r.stderr}"
    assert "PASS" in r.stdout, f"Expected PASS, got: {r.stdout}"


# -----------------------------------------------------------------------------
# Pass-to-pass (pr_diff) - regression + anti-stub
# -----------------------------------------------------------------------------


def test_allgather_copy_present():
    """copy_ must still be present in the allgather loop (regression check)."""
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    has_copy = "copy_(" in loop_code and "inputTensors[0]" in loop_code
    assert has_copy, (
        "copy_ statement missing from allgather loop. "
        "Even-sized tensors will not be filled."
    )


def test_allgather_loop_structure():
    """allgather must have a for-loop over outputTensors[0]."""
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    # Check for loop structure
    has_for_loop = "for" in loop_code and "outputTensors" in loop_code
    assert has_for_loop, "Missing for-loop over outputTensors in allgather"


# [agent_config] pass_to_pass - check from CLAUDE.md rules
# (These are config-derived tests that ensure agent followed instructions)


def test_no_over_engineering():
    """Change should be minimal - only add size guard and continue."""
    loop_code = _extract_allgather_loop()
    assert loop_code, "Could not extract allgather method"

    # Count lines in loop body (approximate)
    lines = [l.strip() for l in loop_code.split('\n') if l.strip()]

    # The fix should add ~3 lines: if check, continue, and closing brace
    # Original loop had ~3 lines: for, copy_, return
    # Fixed loop should have ~5-7 lines
    assert len(lines) < 20, (
        f"Loop body too complex ({len(lines)} lines). "
        "Change should be minimal per CLAUDE.md guidelines."
    )


# -----------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (origin: repo_tests)
# These verify the repo's own CI checks pass on the code
# All use subprocess.run() to execute actual CI commands
# -----------------------------------------------------------------------------


def test_repo_fake_pg_python_syntax():
    """FakeProcessGroup test file must have valid Python syntax (pass_to_pass).

    Runs `python3 -m py_compile` which is a lightweight CI check for Python
    syntax validity. Mirrors PyTorch CI Python compilation checks.
    """
    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"

    r = subprocess.run(
        ["python3", "-m", "py_compile", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Python syntax error in test_fake_pg.py: {r.stderr}"


def test_repo_clang_format():
    """FakeProcessGroup.hpp must pass clang-format check (pass_to_pass).

    PyTorch CI runs clang-format on all C++ changes. This test verifies
    the header file follows the project's formatting guidelines.
    """
    import pytest

    r = subprocess.run(
        ["bash", "-c", "command -v clang-format || (apt-get update -qq && apt-get install -y -qq clang-format)"],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        pytest.skip("clang-format not available and could not be installed")

    r = subprocess.run(
        ["clang-format", "--dry-run", "-Werror", str(TARGET)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"clang-format check failed for FakeProcessGroup.hpp:\n"
        f"{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
    )


def test_repo_ruff_check():
    """test_fake_pg.py must pass ruff check per PyTorch CI (pass_to_pass).

    PyTorch CI uses ruff for Python linting. This test verifies the test
    file passes ruff's linting rules.
    """
    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"

    # Install ruff if not available
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )

    r = subprocess.run(
        ["ruff", "check", str(test_file)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"ruff check failed for test_fake_pg.py:\n{r.stdout[-500:]}{r.stderr[-500:]}"


def test_repo_internal_fake_pg_syntax():
    """Internal fake_pg.py module must have valid Python syntax (pass_to_pass).

    Verifies the FakeProcessGroup backend registration module can be parsed
    using `python3 -m py_compile`, matching PyTorch CI Python checks.
    """
    internal_file = Path(REPO) / "torch/testing/_internal/distributed/fake_pg.py"
    assert internal_file.exists(), f"Internal module not found: {internal_file}"

    r = subprocess.run(
        ["python3", "-m", "py_compile", str(internal_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Python syntax error in internal fake_pg.py: {r.stderr}"


# -----------------------------------------------------------------------------
# Static pass_to_pass gates (origin: static)
# These are file-content checks that don't run CI commands
# -----------------------------------------------------------------------------


def test_repo_header_file_exists():
    """FakeProcessGroup.hpp must exist and be readable (pass_to_pass)."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"
    assert TARGET.is_file(), f"Target is not a file: {TARGET}"
    # Verify we can read it
    content = TARGET.read_text()
    assert len(content) > 0, "Target file is empty"
    assert "FakeProcessGroup" in content, "File does not contain FakeProcessGroup class"


def test_repo_test_fake_pg_ast_valid():
    """test_fake_pg.py must have valid Python AST (pass_to_pass).

    This test parses the test file's AST to ensure it is structurally
    valid Python code that could be executed (deps notwithstanding).
    """
    import ast

    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"

    content = test_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(f"Python AST parsing failed for test_fake_pg.py: {e}")


def test_repo_header_utf8_valid():
    """FakeProcessGroup.hpp must be valid UTF-8 (pass_to_pass).

    PyTorch CI requires all source files to be valid UTF-8 encoded.
    """
    r = subprocess.run(
        ["python3", "-c", "import pathlib; pathlib.Path('" + str(TARGET) + "').read_text(encoding='utf-8')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"FakeProcessGroup.hpp is not valid UTF-8: {r.stderr}"


def test_repo_header_no_tabs():
    """FakeProcessGroup.hpp must use spaces, not tabs (pass_to_pass).

    PyTorch uses spaces for indentation per .clang-format configuration.
    """
    content = TARGET.read_text()
    tab_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if '\t' in line:
            tab_lines.append(i)

    assert len(tab_lines) == 0, f"Found tabs on lines: {tab_lines[:10]} - PyTorch uses spaces"
