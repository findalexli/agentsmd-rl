"""Behavioral checks for jstime-add-comprehensive-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/jstime")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'jstime is a minimal and performant JavaScript runtime built on top of the V8 JavaScript engine, written in Rust. The project provides a CLI tool and an embeddable core library for executing JavaScript' in text, "expected to find: " + 'jstime is a minimal and performant JavaScript runtime built on top of the V8 JavaScript engine, written in Rust. The project provides a CLI tool and an embeddable core library for executing JavaScript'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'fn my_function(scope: &mut v8::HandleScope, args: v8::FunctionCallbackArguments, mut retval: v8::ReturnValue) {' in text, "expected to find: " + 'fn my_function(scope: &mut v8::HandleScope, args: v8::FunctionCallbackArguments, mut retval: v8::ReturnValue) {'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Error Handling**: Use `Result<T, E>` for fallible operations; prefer descriptive error messages' in text, "expected to find: " + '- **Error Handling**: Use `Result<T, E>` for fallible operations; prefer descriptive error messages'[:80]

