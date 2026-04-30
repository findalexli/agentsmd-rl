"""Behavioral checks for flow-docs-add-agentsmd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flow")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'flips/20220203-capability-controllers.md   Sole historical FLIP in this repo; new FLIPs go to onflow/flips' in text, "expected to find: " + 'flips/20220203-capability-controllers.md   Sole historical FLIP in this repo; new FLIPs go to onflow/flips'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `cd protobuf && ./gradlew check build` — JVM build used by CI (`ci-pull-request-jvm-protobuf.yml`).' in text, "expected to find: " + '- `cd protobuf && ./gradlew check build` — JVM build used by CI (`ci-pull-request-jvm-protobuf.yml`).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `cd openapi && make generate-docker` — same, using `swaggerapi/swagger-codegen-cli-v3` container.' in text, "expected to find: " + '- `cd openapi && make generate-docker` — same, using `swaggerapi/swagger-codegen-cli-v3` container.'[:80]

