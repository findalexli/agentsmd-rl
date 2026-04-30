"""Behavioral checks for grafana-agentsmd-add-developer-details-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/grafana")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'These built-in plugins require separate build steps: `azuremonitor`, `cloud-monitoring`, `grafana-postgresql-datasource`, `loki`, `tempo`, `jaeger`, `mysql`, `parca`, `zipkin`, `grafana-pyroscope-data' in text, "expected to find: " + 'These built-in plugins require separate build steps: `azuremonitor`, `cloud-monitoring`, `grafana-postgresql-datasource`, `loki`, `tempo`, `jaeger`, `mysql`, `parca`, `zipkin`, `grafana-pyroscope-data'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Patterns**: Wire DI (regenerate with `make gen-go`), services implement interfaces in same package, business logic in `pkg/services/<domain>/` not in API handlers, database via `sqlstore`, plugin co' in text, "expected to find: " + '**Patterns**: Wire DI (regenerate with `make gen-go`), services implement interfaces in same package, business logic in `pkg/services/<domain>/` not in API handlers, database via `sqlstore`, plugin co'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Patterns**: Redux Toolkit with slices (not old Redux), function components with hooks, Emotion CSS-in-JS via `useStyles2`, RTK Query for data fetching, React Testing Library for tests.' in text, "expected to find: " + '**Patterns**: Redux Toolkit with slices (not old Redux), function components with hooks, Emotion CSS-in-JS via `useStyles2`, RTK Query for data fetching, React Testing Library for tests.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'Use triple backticks with language specifier for code blocks. Introduce each block with a short description. Use `UPPER_SNAKE_CASE` for placeholder names in code samples (e.g., `<SERVICE_NAME>`). Prov' in text, "expected to find: " + 'Use triple backticks with language specifier for code blocks. Introduce each block with a short description. Use `UPPER_SNAKE_CASE` for placeholder names in code samples (e.g., `<SERVICE_NAME>`). Prov'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'When documenting API endpoints, specify the HTTP method (`GET`, `POST`, `PUT`, `DELETE`). Provide the full request path in backticks. Use `{paramName}` for path parameters.' in text, "expected to find: " + 'When documenting API endpoints, specify the HTTP method (`GET`, `POST`, `PUT`, `DELETE`). Provide the full request path in backticks. Use `{paramName}` for path parameters.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('docs/AGENTS.md')
    assert 'Use single backticks for: user input, placeholders (_`<PLACEHOLDER_NAME>`_), files/directories, source code identifiers, config options/values, status codes.' in text, "expected to find: " + 'Use single backticks for: user input, placeholders (_`<PLACEHOLDER_NAME>`_), files/directories, source code identifiers, config options/values, status codes.'[:80]

