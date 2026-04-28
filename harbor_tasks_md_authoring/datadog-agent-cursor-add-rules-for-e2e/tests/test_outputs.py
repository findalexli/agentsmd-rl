"""Behavioral checks for datadog-agent-cursor-add-rules-for-e2e (markdown_authoring task).

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
    text = _read('.cursor/rules/e2e_tests.mdc')
    assert 'This rule provides troubleshooting tips and code patterns not covered in the main documentation. For prerequisites, setup, and basic usage, see `docs/public/how-to/test/e2e.md`.' in text, "expected to find: " + 'This rule provides troubleshooting tips and code patterns not covered in the main documentation. For prerequisites, setup, and basic usage, see `docs/public/how-to/test/e2e.md`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/e2e_tests.mdc')
    assert 'func downloadDockerImages(e *aws.Environment, vm *componentsremote.Host, images []string, dependsOn ...pulumi.Resource) ([]pulumi.Resource, error) {' in text, "expected to find: " + 'func downloadDockerImages(e *aws.Environment, vm *componentsremote.Host, images []string, dependsOn ...pulumi.Resource) ([]pulumi.Resource, error) {'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/e2e_tests.mdc')
    assert 'Note: The `-c ddagent:imagePull*` flags are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role.' in text, "expected to find: " + 'Note: The `-c ddagent:imagePull*` flags are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('test/new-e2e/tests/gpu/AGENTS.md')
    assert '**Note**: The `-c ddagent:imagePullPassword` flags in the test command are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role, which requires the cor' in text, "expected to find: " + '**Note**: The `-c ddagent:imagePullPassword` flags in the test command are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role, which requires the cor'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('test/new-e2e/tests/gpu/AGENTS.md')
    assert "3. The default environment is `agent-sandbox` (see `test/new-e2e/pkg/runner/local_profile.go`). If you're in a different account, EC2 instances won't have the correct IAM permissions." in text, "expected to find: " + "3. The default environment is `agent-sandbox` (see `test/new-e2e/pkg/runner/local_profile.go`). If you're in a different account, EC2 instances won't have the correct IAM permissions."[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('test/new-e2e/tests/gpu/AGENTS.md')
    assert 'GPU e2e tests are located in `test/new-e2e/tests/gpu/` and verify GPU monitoring functionality in both host and Kubernetes environments.' in text, "expected to find: " + 'GPU e2e tests are located in `test/new-e2e/tests/gpu/` and verify GPU monitoring functionality in both host and Kubernetes environments.'[:80]

