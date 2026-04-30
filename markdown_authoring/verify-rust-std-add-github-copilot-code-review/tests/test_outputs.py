"""Behavioral checks for verify-rust-std-add-github-copilot-code-review (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/verify-rust-std")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository is a fork of the Rust standard library used exclusively for formal verification. Verification targets include memory safety, undefined behavior, and functional correctness, depending o' in text, "expected to find: " + 'This repository is a fork of the Rust standard library used exclusively for formal verification. Verification targets include memory safety, undefined behavior, and functional correctness, depending o'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "- **No unjustified assumptions.** Every `#[kani::assume]`, `requires`, or equivalent precondition must be justified by the function's documented safety contract or API invariants. Flag assumptions tha" in text, "expected to find: " + "- **No unjustified assumptions.** Every `#[kani::assume]`, `requires`, or equivalent precondition must be justified by the function's documented safety contract or API invariants. Flag assumptions tha"[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- The contribution must be automated and pass as part of PR CI checks. Contributors should maintain the proofs and provide support thoughtout the lifetime of the contest (i.e. keeping it up-to-date wi' in text, "expected to find: " + '- The contribution must be automated and pass as part of PR CI checks. Contributors should maintain the proofs and provide support thoughtout the lifetime of the contest (i.e. keeping it up-to-date wi'[:80]

