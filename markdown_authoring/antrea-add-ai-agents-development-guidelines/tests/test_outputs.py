"""Behavioral checks for antrea-add-ai-agents-development-guidelines (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antrea")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Follow Kubernetes logging guidelines from the [community documentation](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-instrumentation/logging.md)' in text, "expected to find: " + '- Follow Kubernetes logging guidelines from the [community documentation](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-instrumentation/logging.md)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- [Kubernetes Logging Guidelines](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-instrumentation/logging.md)' in text, "expected to find: " + '- [Kubernetes Logging Guidelines](https://github.com/kubernetes/community/blob/master/contributors/devel/sig-instrumentation/logging.md)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Shebang**: For all Bash scripts, prefer `#!/usr/bin/env bash` over alternatives like `#!/bin/bash` for better portability' in text, "expected to find: " + '- **Shebang**: For all Bash scripts, prefer `#!/usr/bin/env bash` over alternatives like `#!/bin/bash` for better portability'[:80]

