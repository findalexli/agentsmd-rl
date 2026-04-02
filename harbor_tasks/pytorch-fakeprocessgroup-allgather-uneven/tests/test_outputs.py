"""
Task: pytorch-fakeprocessgroup-allgather-uneven
Repo: pytorch/pytorch @ 8401fdeb9abd665b36465c52b7aefd591cc3dbcb
PR:   177291

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: PyTorch C++ extensions cannot be built in this container (no full
torch build), so tests analyse the C++ source of FakeProcessGroup::allgather
directly.  # AST-only because: C++ code requires full torch build to compile
"""

import re
from pathlib import Path

TARGET = Path("/workspace/pytorch/torch/csrc/distributed/c10d/FakeProcessGroup.hpp")


def _allgather_body() -> str:
    """Extract the body of the allgather override method."""
    source = TARGET.read_text()
    # Use [^{]* instead of [^)]* to handle nested parens in AllgatherOptions()
    m = re.search(
        r"allgather\b[^{]*override\s*\{(.*?)\n\s*return\s+c10::make_intrusive",
        source,
        re.DOTALL,
    )
    assert m, "Could not locate allgather method in FakeProcessGroup.hpp"
    return m.group(1)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_header_balanced_braces():
    """FakeProcessGroup.hpp must have balanced braces (basic syntax gate)."""
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


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_allgather_guards_mismatched_sizes():
    """allgather must have a conditional size check before copy_.

    On the base commit the loop body is just `tensor.copy_(inputTensors[0])`,
    with no guard — this crashes when output tensors have different first-dim
    sizes.  The fix adds a size comparison so mismatched tensors are skipped.
    """
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()

    # Must contain a conditional (if statement)
    assert re.search(r"\bif\s*\(", body), (
        "No conditional found in allgather body — "
        "mismatched-size tensors will crash on copy_"
    )

    # The conditional must involve a size/shape comparison
    has_size_check = bool(
        re.search(r"\.size\s*\(", body)
        or re.search(r"\.sizes\s*\(", body)
        or re.search(r"\.numel\s*\(", body)
    )
    assert has_size_check, (
        "Conditional does not compare tensor sizes — "
        "mismatched dimensions will still crash"
    )


# [pr_diff] fail_to_pass
def test_mismatched_tensors_skipped():
    """Mismatched output tensors must be skipped, not copied.

    The fix should either `continue` past mismatched tensors or wrap copy_
    inside a matching-size conditional so that uneven outputs are left
    unchanged.
    """
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()

    # Acceptable skip patterns:
    #   1. `continue` inside a size-check conditional
    #   2. copy_ wrapped inside `if (sizes match)` block
    #   3. try/catch that swallows the copy_ error
    has_continue = "continue" in body
    has_conditional_copy = bool(
        re.search(r"\bif\s*\([^)]*\)\s*\{[^}]*copy_", body, re.DOTALL)
    )
    has_try_catch = bool(re.search(r"\btry\s*\{", body))

    assert has_continue or has_conditional_copy or has_try_catch, (
        "No skip mechanism for mismatched tensors — "
        "allgather will crash on uneven output sizes"
    )


# [pr_diff] fail_to_pass
def test_size_check_references_both_tensors():
    """The size guard must compare output tensor against input tensor.

    A correct fix compares the loop variable (output tensor) against
    inputTensors[0] — not a hardcoded constant or self-comparison.
    """
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()

    # The conditional should reference both inputTensors and a size call
    has_input_ref = bool(re.search(r"inputTensors\[0\]", body))
    has_size_call = bool(re.search(r"\.size\s*\(", body) or re.search(r"\.sizes\s*\(", body))

    assert has_input_ref and has_size_call, (
        "Size guard must compare output tensor size against inputTensors[0] size"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_copy_still_in_allgather_loop():
    """copy_ must still be present inside the allgather for-loop.

    Removing copy_ entirely would break even-sized allgather operations.
    """
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()

    assert "for" in body, "allgather loop removed"
    assert "copy_" in body, (
        "copy_ removed from allgather — even-sized tensors will not be filled"
    )

    # copy_ must appear after the for keyword (inside the loop, not before it)
    for_pos = body.index("for")
    copy_pos = body.index("copy_")
    assert copy_pos > for_pos, "copy_ appears before the for-loop (unreachable)"


# [static] pass_to_pass
def test_allgather_not_stub():
    """allgather method must have a meaningful implementation."""
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()
    lines = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith("//")]
    # Base commit has ~3 effective lines; fix adds 3 more → ≥4 expected
    assert len(lines) >= 3, f"allgather body is a stub ({len(lines)} effective lines)"
    assert "outputTensors" in body, "allgather doesn't reference outputTensors"
    assert "inputTensors" in body, "allgather doesn't reference inputTensors"


# [static] pass_to_pass
def test_allgather_iterates_output_tensors():
    """The allgather loop must iterate over outputTensors[0]."""
    # AST-only because: C++ code requires full torch build to compile
    body = _allgather_body()
    assert bool(re.search(r"for\s*\(.*outputTensors\[0\]", body, re.DOTALL)), (
        "allgather must iterate over outputTensors[0]"
    )
