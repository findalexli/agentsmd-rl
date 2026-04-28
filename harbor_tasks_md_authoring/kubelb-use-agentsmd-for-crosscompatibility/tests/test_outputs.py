"""Behavioral checks for kubelb-use-agentsmd-for-crosscompatibility (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kubelb")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Official documentation for KubeLB is available at <https://docs.kubermatic.com/kubelb>. Please refer to this documentation for the latest information about the project. If and when you find gaps in th' in text, "expected to find: " + 'Official documentation for KubeLB is available at <https://docs.kubermatic.com/kubelb>. Please refer to this documentation for the latest information about the project. If and when you find gaps in th'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'When debugging test failures, use the `make e2e-select select=<key>=<value>` command to run a single test or a group of tests that were failing. The labels can be found in the `chainsaw-test.yaml` fil' in text, "expected to find: " + 'When debugging test failures, use the `make e2e-select select=<key>=<value>` command to run a single test or a group of tests that were failing. The labels can be found in the `chainsaw-test.yaml` fil'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'PRs and issues must use the templates in `.github/`. For PRs, use `.github/PULL_REQUEST_TEMPLATE.md` — fill in all sections (description, kind, release note, documentation).' in text, "expected to find: " + 'PRs and issues must use the templates in `.github/`. For PRs, use `.github/PULL_REQUEST_TEMPLATE.md` — fill in all sections (description, kind, release note, documentation).'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert '| `layer4/verify-status-propagation.yaml` | Verify LB IP matches tenant service IP | `service_name`, `tenant`, `kubelb_namespace` |' in text, "expected to find: " + '| `layer4/verify-status-propagation.yaml` | Verify LB IP matches tenant service IP | `service_name`, `tenant`, `kubelb_namespace` |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert 'Chainsaw sets `$namespace` to auto-generated test namespace. Never use `namespace` as a binding name. Hardcode `default` directly.' in text, "expected to find: " + 'Chainsaw sets `$namespace` to auto-generated test namespace. Never use `namespace` as a binding name. Hardcode `default` directly.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/AGENTS.md')
    assert '| `common/verify-route-crd.yaml` | Assert Route CRD exists with labels | `resource_name`, `expected_kind`, `kubelb_namespace` |' in text, "expected to find: " + '| `common/verify-route-crd.yaml` | Assert Route CRD exists with labels | `resource_name`, `expected_kind`, `kubelb_namespace` |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e/CLAUDE.md')
    assert 'test/e2e/CLAUDE.md' in text, "expected to find: " + 'test/e2e/CLAUDE.md'[:80]

