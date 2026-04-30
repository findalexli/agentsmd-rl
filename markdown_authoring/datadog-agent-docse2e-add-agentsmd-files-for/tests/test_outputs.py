"""Behavioral checks for datadog-agent-docse2e-add-agentsmd-files-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/datadog-agent")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-e2e/SKILL.md')
    assert 'description: Write E2E tests for the Datadog Agent using the new-e2e framework with fakeintake assertions' in text, "expected to find: " + 'description: Write E2E tests for the Datadog Agent using the new-e2e framework with fakeintake assertions'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-e2e/SKILL.md')
    assert '| Real tests to use as patterns | `test/new-e2e/tests/` (see lookup table in e2e-framework AGENTS.md) |' in text, "expected to find: " + '| Real tests to use as patterns | `test/new-e2e/tests/` (see lookup table in e2e-framework AGENTS.md) |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/write-e2e/SKILL.md')
    assert 'argument-hint: "<feature-or-check-name> [--platform linux|windows|both] [--env host|docker|k8s]"' in text, "expected to find: " + 'argument-hint: "<feature-or-check-name> [--platform linux|windows|both] [--env host|docker|k8s]"'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'arrive in **fakeintake** (a mock Datadog intake). By default the fakeintake forwards payloads to `dddev` org account.' in text, "expected to find: " + 'arrive in **fakeintake** (a mock Datadog intake). By default the fakeintake forwards payloads to `dddev` org account.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '| Sub-project `AGENTS.md` | APIs, conventions, or extension patterns in that sub-project change |' in text, "expected to find: " + '| Sub-project `AGENTS.md` | APIs, conventions, or extension patterns in that sub-project change |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "| `.claude/skills/*/SKILL.md` | A skill's steps, examples, or recommendations become outdated |" in text, "expected to find: " + "| `.claude/skills/*/SKILL.md` | A skill's steps, examples, or recommendations become outdated |"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e-framework/AGENTS.md')
    assert '| custom environment | user-defined struct | `e2e.WithPulumiProvisioner()` | Agent on host + workloads on docker, multi-VM, extra services |' in text, "expected to find: " + '| custom environment | user-defined struct | `e2e.WithPulumiProvisioner()` | Agent on host + workloads on docker, multi-VM, extra services |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e-framework/AGENTS.md')
    assert '| `environments.Kubernetes` | K8s cluster + Agent + FakeIntake | `awskubernetes.Provisioner()` | K8s checks, DaemonSet, Cluster Agent |' in text, "expected to find: " + '| `environments.Kubernetes` | K8s cluster + Agent + FakeIntake | `awskubernetes.Provisioner()` | K8s checks, DaemonSet, Cluster Agent |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e-framework/AGENTS.md')
    assert '| `environments.Host` | VM + Agent + FakeIntake | `awshost.Provisioner()` | System checks, agent commands, file-based config |' in text, "expected to find: " + '| `environments.Host` | VM + Agent + FakeIntake | `awshost.Provisioner()` | System checks, agent commands, file-based config |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('test/e2e-framework/CLAUDE.md')
    assert '@../../CLAUDE.md' in text, "expected to find: " + '@../../CLAUDE.md'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('test/fakeintake/AGENTS.md')
    assert '| `/api/v2/contlcycle` | ContainerLifecycleAggregator | `GetContainerLifecycleEvents()` |' in text, "expected to find: " + '| `/api/v2/contlcycle` | ContainerLifecycleAggregator | `GetContainerLifecycleEvents()` |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('test/fakeintake/AGENTS.md')
    assert 'payloads the agent sends (metrics, logs, traces, check runs, etc.) and exposes' in text, "expected to find: " + 'payloads the agent sends (metrics, logs, traces, check runs, etc.) and exposes'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('test/fakeintake/AGENTS.md')
    assert '- `aggregator/common.go` — generic `Aggregator[T]` base (compression, storage)' in text, "expected to find: " + '- `aggregator/common.go` — generic `Aggregator[T]` base (compression, storage)'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('test/fakeintake/CLAUDE.md')
    assert '@../../CLAUDE.md' in text, "expected to find: " + '@../../CLAUDE.md'[:80]

