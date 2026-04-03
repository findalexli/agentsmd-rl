"""
Task: pytorch-stream-context-reentrance
Repo: pytorch/pytorch @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
PR:   176603

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: This is C++ code (torch/csrc/Stream.cpp) that requires a full PyTorch
build with CUDA/accelerator headers to compile.  The Dockerfile uses
python:3.12-slim, so we cannot compile or link.  All checks analyse the
source text directly.
"""

from pathlib import Path

TARGET = Path("/workspace/pytorch/torch/csrc/Stream.cpp")


def _read_source():
    return TARGET.read_text()


def _extract_function_body(source: str, func_name: str, end_marker: str | None = None) -> str:
    """Extract the body of a C++ function from source."""
    start = source.find(func_name)
    assert start >= 0, f"{func_name} not found in source"
    if end_marker:
        end = source.find(end_marker, start + len(func_name))
        return source[start : end if end > 0 else start + 3000]
    return source[start : start + 3000]


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_file_exists_and_has_functions():
    """Target file exists with required function definitions."""
    assert TARGET.exists(), f"Target file missing: {TARGET}"
    source = _read_source()

    for func in [
        "THPStream_enter(PyObject",
        "THPStream_exit(PyObject",
        "THPStream_dealloc(THPStream",
    ]:
        assert func in source, f"Missing function definition: {func}"

    # Anti-stub: file must have substantial content (original is ~430 lines)
    meaningful = [l for l in source.splitlines() if l.strip() and not l.strip().startswith("//")]
    assert len(meaningful) >= 150, f"Only {len(meaningful)} meaningful lines -- likely a stub"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_reentrance_assertion_removed():
    """The TORCH_CHECK assertion that blocks reentrant stream usage must be removed."""
    source = _read_source()
    blocking = [
        "Stream's context should not be initialized",
        "context should not be initialized",
    ]
    for pattern in blocking:
        assert pattern not in source, (
            f"Reentrance-blocking assertion still present: '{pattern}'"
        )


# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_context_uses_stack():
    """Context management must use a stack/list, not a single dict assignment."""
    source = _read_source()
    enter_body = _extract_function_body(source, "THPStream_enter(", "THPStream_exit(")

    # The buggy pattern: self->context = dict.release()  (single dict, not a stack)
    # The fix uses a list: self->context = list.release() after PyList_New()
    for line in enter_body.splitlines():
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/*"):
            continue
        if "self->context" in stripped and "dict.release()" in stripped:
            assert False, f"Single-dict context assignment (old bug pattern): {stripped}"

    # Some stack-like data structure must exist
    stack_indicators = [
        "PyList_New", "PyList_Append",
        "std::vector", "std::stack", "std::deque",
        "push_back", "emplace_back",
    ]
    assert any(ind in source for ind in stack_indicators), (
        "No stack/list data structure found for context management"
    )


# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_enter_pushes_to_stack():
    """__enter__ must save the current stream state by pushing to a stack."""
    source = _read_source()
    enter_body = _extract_function_body(source, "THPStream_enter(", "THPStream_exit(")

    # Must get the current stream (to save it)
    assert "getCurrentStream" in enter_body, "enter() doesn't get current stream"

    # Must push/append state onto a stack
    push_ops = ["PyList_Append", "push_back", "emplace_back", "append("]
    assert any(op in enter_body for op in push_ops), "enter() doesn't push state to stack"

    # Must set the new current stream
    assert "setCurrentStream" in enter_body, "enter() doesn't set current stream"

    # Ordering: must get current stream BEFORE setting new one
    get_pos = enter_body.find("getCurrentStream")
    set_pos = enter_body.find("setCurrentStream")
    assert get_pos < set_pos, "enter() sets stream before getting current (would lose state)"


# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_exit_pops_from_stack():
    """__exit__ must pop state from the stack and restore the previous stream."""
    source = _read_source()
    exit_start = source.find("THPStream_exit(")
    assert exit_start >= 0, "THPStream_exit not found"
    rest = source[exit_start:]
    end = rest.find("END_HANDLE_TH_ERRORS")
    exit_body = rest[: end + 30] if end > 0 else rest[:3000]

    # Must pop/remove from stack
    pop_ops = ["PyList_SetSlice", "pop_back", "pop()", "erase(", "resize("]
    assert any(op in exit_body for op in pop_ops), "exit() doesn't pop from stack"

    # Must restore the previous stream
    assert "setCurrentStream" in exit_body, "exit() doesn't restore previous stream"

    # Must NOT unconditionally Py_CLEAR(self->context) (wipes entire stack)
    lines = exit_body.splitlines()
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        if "Py_CLEAR(self->context)" in stripped:
            context = "\n".join(lines[max(0, i - 3) : i])
            assert any(k in context for k in ["if", "size", "empty"]), (
                "exit() unconditionally clears context (wipes entire stack)"
            )


# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_dealloc_clears_context():
    """Destructor must clear context to prevent memory leak."""
    source = _read_source()
    dealloc_body = _extract_function_body(source, "THPStream_dealloc(")[:500]

    clear_patterns = [
        "Py_CLEAR(self->context)",
        "Py_XDECREF(self->context)",
        "Py_DECREF(self->context)",
    ]
    assert any(p in dealloc_body for p in clear_patterns), (
        "dealloc doesn't clear self->context (memory leak)"
    )
    assert "tp_free" in dealloc_body, "dealloc doesn't free the object"


# [pr_diff] fail_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_noop_when_stream_already_current():
    """enter() must handle the case where the stream is already current
    (push a sentinel / no-op instead of redundantly switching)."""
    source = _read_source()
    enter_body = _extract_function_body(source, "THPStream_enter(", "THPStream_exit(")

    # The fix compares current stream id with self->stream_id before switching.
    # Without this, reentrant use (with s: with s:) would pointlessly save/restore.
    assert "stream_id" in enter_body, "enter() doesn't compare stream ids"

    # Must have a fast-path that avoids setCurrentStream when already current.
    # The sentinel is typically Py_None appended to the list.
    sentinel_patterns = ["Py_None", "nullptr", "sentinel", "noop", "no_op", "no-op"]
    assert any(p in enter_body for p in sentinel_patterns), (
        "enter() has no sentinel/no-op path for when stream is already current"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) -- anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_enter_exit_not_stub():
    """enter() and exit() have substantial implementations, not stubs."""
    source = _read_source()

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

    enter_body = _extract_function_body(source, "THPStream_enter(", "THPStream_exit(")
    exit_start = source.find("THPStream_exit(")
    rest = source[exit_start:]
    end = rest.find("END_HANDLE_TH_ERRORS")
    exit_body = rest[: end] if end > 0 else rest[:3000]

    enter_lines = count_meaningful(enter_body)
    exit_lines = count_meaningful(exit_body)

    assert enter_lines >= 15, f"enter() has only {enter_lines} meaningful lines -- likely stub"
    assert exit_lines >= 10, f"exit() has only {exit_lines} meaningful lines -- likely stub"

    assert "self->context" in enter_body, "enter() doesn't reference self->context"
    assert "self->context" in exit_body, "exit() doesn't reference self->context"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) -- rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass -- .github/copilot-instructions.md:91 @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_error_handling_macros():
    """Entry points must use HANDLE_TH_ERRORS / END_HANDLE_TH_ERRORS for exception conversion."""
    source = _read_source()

    enter_body = _extract_function_body(source, "THPStream_enter(", "THPStream_exit(")
    assert "HANDLE_TH_ERRORS" in enter_body, "enter() missing HANDLE_TH_ERRORS"
    assert "END_HANDLE_TH_ERRORS" in enter_body, "enter() missing END_HANDLE_TH_ERRORS"

    exit_start = source.find("THPStream_exit(")
    rest = source[exit_start:]
    end = rest.find("END_HANDLE_TH_ERRORS")
    exit_body = rest[: end + 30] if end > 0 else rest[:3000]
    assert "HANDLE_TH_ERRORS" in exit_body, "exit() missing HANDLE_TH_ERRORS"
    assert "END_HANDLE_TH_ERRORS" in exit_body, "exit() missing END_HANDLE_TH_ERRORS"

    # Must have python_error() throws for Python C API error propagation
    assert "python_error" in enter_body, "enter() missing python_error throws"


# [agent_config] pass_to_pass — .github/copilot-instructions.md:89 @ 3c40486f8a515b3f6f851a0cc4b3a2dc07744f6c
# Source-analysis because: C++ requiring full PyTorch build cannot compile here
def test_python_h_included_first():
    """Python.h must be the first #include in torch/csrc/ files to avoid _XOPEN_SOURCE redefinition errors."""
    source = _read_source()
    first_include = None
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#include"):
            first_include = stripped
            break
    assert first_include is not None, "No #include found in source"
    python_h_patterns = ["<Python.h>", '"Python.h"', "python_headers.h"]
    assert any(p in first_include for p in python_h_patterns), (
        f"First #include must be Python.h or a wrapper, got: {first_include}"
    )
