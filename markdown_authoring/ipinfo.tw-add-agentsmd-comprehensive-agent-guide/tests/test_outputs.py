"""Behavioral checks for ipinfo.tw-add-agentsmd-comprehensive-agent-guide (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/ipinfo.tw")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Set `MAXMIND_LICENSE_KEY` before building so the Dockerfile can fetch the GeoLite2 databases. Our Docker Hub automation (and local builds when needed) exports that variable alongside `DOCKERFILE_PATH=' in text, "expected to find: " + 'Set `MAXMIND_LICENSE_KEY` before building so the Dockerfile can fetch the GeoLite2 databases. Our Docker Hub automation (and local builds when needed) exports that variable alongside `DOCKERFILE_PATH='[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Source assets live under the repository root. `Dockerfile` and `docker-compose.yml` produce the nginx-based image that serves all endpoints. Runtime configuration sits in `nginx/`: the top-level `ngin' in text, "expected to find: " + 'Source assets live under the repository root. `Dockerfile` and `docker-compose.yml` produce the nginx-based image that serves all endpoints. Runtime configuration sits in `nginx/`: the top-level `ngin'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Every endpoint is an nginx location block that formats data supplied by the GeoIP2 variables and returns static text or JSON via the `return` directive. The Dockerfile downloads and validates the GeoL' in text, "expected to find: " + 'Every endpoint is an nginx location block that formats data supplied by the GeoIP2 variables and returns static text or JSON via the `return` directive. The Dockerfile downloads and validates the GeoL'[:80]

