"""
Task: pytorch-fakeprocessgroup-allgather-uneven
Repo: pytorch/pytorch @ 8401fdeb9abd665b36465c52b7aefd591cc3dbcb
PR:   177291

Behavioral tests that extract the allgather loop from FakeProcessGroup.hpp,
compile it in a minimal C++ harness with mock tensor types, and verify
runtime behavior with different tensor size configurations.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = Path(REPO) / "torch/csrc/distributed/c10d/FakeProcessGroup.hpp"


def _extract_allgather_loop_body() -> str:
    """Extract the for-loop body from the allgather method.

    Returns the code between checkCollectiveError() and the return statement,
    which contains the for-loop and any guards added by a fix.
    """
    source = TARGET.read_text()
    lines = source.split('\n')

    # Find allgather method signature (not _allgather_base)
    method_start = -1
    for i, line in enumerate(lines):
        if ('allgather(' in line and 'intrusive_ptr' in line
                and '_allgather' not in line):
            method_start = i
            break

    assert method_start >= 0, "Could not find allgather method"

    # Find the opening brace of the method body
    body_start = -1
    brace_depth = 0
    for i in range(method_start, min(method_start + 10, len(lines))):
        if '{' in lines[i]:
            body_start = i + 1
            brace_depth = lines[i].count('{') - lines[i].count('}')
            break

    assert body_start >= 0, "Could not find allgather method body start"

    # Collect lines between opening brace and closing brace,
    # skipping checkCollectiveError and the return statement
    body_lines = []
    for i in range(body_start, len(lines)):
        line = lines[i]
        brace_depth += line.count('{') - line.count('}')
        if brace_depth <= 0:
            break
        stripped = line.strip()
        if stripped.startswith('return '):
            continue
        if 'checkCollectiveError' in stripped:
            continue
        body_lines.append(line)

    result = '\n'.join(body_lines)
    assert result.strip(), "Extracted allgather loop body is empty"
    return result


# C++ test harness template.
# LOOP_BODY_PLACEHOLDER and SCENARIO_PLACEHOLDER are replaced at runtime.
_CPP_HARNESS = r"""
#include <vector>
#include <iostream>
#include <stdexcept>
#include <string>
#include <cstdint>

struct Tensor {
    int64_t _dim0;
    bool was_copied;

    Tensor() : _dim0(0), was_copied(false) {}
    Tensor(int64_t d0) : _dim0(d0), was_copied(false) {}

    int64_t size(int dim) const {
        return dim == 0 ? _dim0 : 1;
    }

    std::vector<int64_t> sizes() const {
        return {_dim0, 1};
    }

    int64_t numel() const { return _dim0; }

    void copy_(const Tensor& other) {
        if (_dim0 != other._dim0) {
            throw std::runtime_error("copy_ shape mismatch");
        }
        was_copied = true;
    }
};

void checkCollectiveError() {}

int main() {
    std::vector<std::vector<Tensor>> outputTensors;
    std::vector<Tensor> inputTensors;

    std::string scenario = "SCENARIO_PLACEHOLDER";
    if (scenario == "matching") {
        outputTensors = {{Tensor(5), Tensor(5)}};
        inputTensors = {Tensor(5)};
    } else {
        outputTensors = {{Tensor(5), Tensor(4)}};
        inputTensors = {Tensor(5)};
    }

    try {
LOOP_BODY_PLACEHOLDER
    } catch (const std::exception& e) {
        std::cout << "CRASH:" << e.what() << std::endl;
        return 2;
    }

    for (size_t i = 0; i < outputTensors[0].size(); i++) {
        std::cout << "tensor_" << i
                  << "_copied=" << outputTensors[0][i].was_copied
                  << std::endl;
    }

    return 0;
}
"""


def _build_and_run(loop_body: str, scenario: str) -> subprocess.CompletedProcess:
    """Compile and run the C++ test harness with the extracted loop body."""
    source = _CPP_HARNESS.replace(
        "LOOP_BODY_PLACEHOLDER", loop_body
    ).replace(
        "SCENARIO_PLACEHOLDER", scenario
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        src = Path(tmpdir) / "test.cpp"
        exe = Path(tmpdir) / "test"
        src.write_text(source)

        comp = subprocess.run(
            ["clang++", "-std=c++17", "-o", str(exe), str(src)],
            capture_output=True, text=True, timeout=30,
        )
        assert comp.returncode == 0, f"Compilation failed:\n{comp.stderr}"

        return subprocess.run(
            [str(exe)], capture_output=True, text=True, timeout=10,
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


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
    """The extracted allgather loop must compile as valid C++."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "matching")
    assert result.returncode == 0, (
        f"Allgather loop did not compile or run:\n"
        f"{result.stdout}\n{result.stderr}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- behavioral tests via C++ compilation & execution
# ---------------------------------------------------------------------------


def test_allgather_size_guard_present():
    """allgather with uneven tensors must not crash and must still copy matching ones."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "uneven")

    assert result.returncode != 2, (
        "allgather loop crashed on uneven tensors (no size guard):\n"
        f"{result.stdout}"
    )
    assert result.returncode == 0, (
        f"allgather loop failed unexpectedly:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    # Matching tensor (same size as input) must still be copied
    assert "tensor_0_copied=1" in result.stdout, (
        f"Matching tensor was not copied:\n{result.stdout}"
    )


def test_allgather_continue_present():
    """Mismatched-size tensors must be skipped; matching ones must be copied."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "uneven")

    assert result.returncode == 0, (
        f"allgather loop crashed or failed:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    # Matching tensor must still be copied
    assert "tensor_0_copied=1" in result.stdout, (
        f"Matching tensor was not copied:\n{result.stdout}"
    )
    # Mismatched tensor must NOT be copied
    assert "tensor_1_copied=0" in result.stdout, (
        "Mismatched tensor was modified when it should have been skipped:\n"
        f"{result.stdout}"
    )


def test_allgather_uneven_behavior_simulation():
    """allgather: matching tensors copied, mismatched tensors skipped."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "uneven")

    assert result.returncode == 0, (
        f"allgather loop crashed or failed:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert "tensor_0_copied=1" in result.stdout, (
        f"Matching tensor was not copied:\n{result.stdout}"
    )
    assert "tensor_1_copied=0" in result.stdout, (
        f"Mismatched tensor was modified:\n{result.stdout}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) -- regression & structure checks
# ---------------------------------------------------------------------------


def test_original_broken_behavior():
    """allgather with all-matching tensors must copy all of them.

    Verifies the core copy logic works regardless of whether a size guard
    is present -- when all tensors match, they should all be filled.
    """
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "matching")

    assert result.returncode == 0, (
        f"allgather loop failed on matching tensors:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert "tensor_0_copied=1" in result.stdout, (
        f"First matching tensor was not copied:\n{result.stdout}"
    )
    assert "tensor_1_copied=1" in result.stdout, (
        f"Second matching tensor was not copied:\n{result.stdout}"
    )


def test_allgather_copy_present():
    """copy_ must still work for matching tensors (regression check)."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "matching")

    assert result.returncode == 0, (
        f"allgather loop failed:\n{result.stdout}\n{result.stderr}"
    )
    assert "copied=1" in result.stdout, (
        f"No tensors were copied -- copy_ may be missing:\n{result.stdout}"
    )


def test_allgather_loop_structure():
    """allgather loop must iterate over and process all output tensors."""
    loop_body = _extract_allgather_loop_body()
    result = _build_and_run(loop_body, "matching")

    assert result.returncode == 0, (
        f"allgather loop structure is broken:\n"
        f"{result.stdout}\n{result.stderr}"
    )
    assert "tensor_0_copied=" in result.stdout, (
        "Loop did not process first tensor"
    )
    assert "tensor_1_copied=" in result.stdout, (
        "Loop did not process second tensor"
    )


def test_no_over_engineering():
    """Change should be minimal -- only add size guard and continue."""
    loop_code = _extract_allgather_loop_body()
    lines = [l.strip() for l in loop_code.split('\n') if l.strip()]
    assert len(lines) < 20, (
        f"Loop body too complex ({len(lines)} lines). "
        "Change should be minimal per CLAUDE.md guidelines."
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates (origin: repo_tests)
# ---------------------------------------------------------------------------


def test_repo_fake_pg_python_syntax():
    """FakeProcessGroup test file must have valid Python syntax."""
    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(test_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Python syntax error in test_fake_pg.py: {r.stderr}"
    )


def test_repo_clang_format():
    """FakeProcessGroup.hpp must pass clang-format check."""
    import pytest

    r = subprocess.run(
        ["bash", "-c",
         "command -v clang-format || "
         "(apt-get update -qq && apt-get install -y -qq clang-format)"],
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
    """test_fake_pg.py must pass ruff check per PyTorch CI."""
    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"
    subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    r = subprocess.run(
        ["ruff", "check", str(test_file)],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"ruff check failed for test_fake_pg.py:\n"
        f"{r.stdout[-500:]}{r.stderr[-500:]}"
    )


def test_repo_internal_fake_pg_syntax():
    """Internal fake_pg.py module must have valid Python syntax."""
    internal_file = (
        Path(REPO) / "torch/testing/_internal/distributed/fake_pg.py"
    )
    assert internal_file.exists(), f"Internal module not found: {internal_file}"
    r = subprocess.run(
        ["python3", "-m", "py_compile", str(internal_file)],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Python syntax error in internal fake_pg.py: {r.stderr}"
    )


# ---------------------------------------------------------------------------
# Static pass_to_pass gates (origin: static)
# ---------------------------------------------------------------------------


def test_repo_header_file_exists():
    """FakeProcessGroup.hpp must exist and be readable."""
    assert TARGET.exists(), f"Target file not found: {TARGET}"
    assert TARGET.is_file(), f"Target is not a file: {TARGET}"
    content = TARGET.read_text()
    assert len(content) > 0, "Target file is empty"
    assert "FakeProcessGroup" in content, (
        "File does not contain FakeProcessGroup class"
    )


def test_repo_test_fake_pg_ast_valid():
    """test_fake_pg.py must have valid Python AST."""
    import ast

    test_file = Path(REPO) / "test/distributed/test_fake_pg.py"
    assert test_file.exists(), f"Test file not found: {test_file}"
    content = test_file.read_text()
    try:
        ast.parse(content)
    except SyntaxError as e:
        raise AssertionError(
            f"Python AST parsing failed for test_fake_pg.py: {e}"
        )


def test_repo_header_utf8_valid():
    """FakeProcessGroup.hpp must be valid UTF-8."""
    r = subprocess.run(
        ["python3", "-c",
         "import pathlib; pathlib.Path('"
         + str(TARGET)
         + "').read_text(encoding='utf-8')"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"FakeProcessGroup.hpp is not valid UTF-8: {r.stderr}"
    )


def test_repo_header_no_tabs():
    """FakeProcessGroup.hpp must use spaces, not tabs."""
    content = TARGET.read_text()
    tab_lines = []
    for i, line in enumerate(content.split('\n'), 1):
        if '\t' in line:
            tab_lines.append(i)
    assert len(tab_lines) == 0, (
        f"Found tabs on lines: {tab_lines[:10]} -- PyTorch uses spaces"
    )
