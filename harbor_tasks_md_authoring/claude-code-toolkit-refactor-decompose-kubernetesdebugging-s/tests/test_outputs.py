"""Behavioral checks for claude-code-toolkit-refactor-decompose-kubernetesdebugging-s (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/claude-code-toolkit")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/SKILL.md')
    assert '| CrashLoopBackOff, OOMKilled, config error, health check, liveness probe, ImagePullBackOff, image pull, registry auth, Pending, FailedScheduling, node affinity, taint, PVC | `references/crash-diagnos' in text, "expected to find: " + '| CrashLoopBackOff, OOMKilled, config error, health check, liveness probe, ImagePullBackOff, image pull, registry auth, Pending, FailedScheduling, node affinity, taint, PVC | `references/crash-diagnos'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/SKILL.md')
    assert '| CPU throttling, memory limit, OOMKill, ephemeral storage, DiskPressure, debug container, distroless, kubectl reference, rollout, exec | `references/resource-debugging.md` | ~100 lines |' in text, "expected to find: " + '| CPU throttling, memory limit, OOMKill, ephemeral storage, DiskPressure, debug container, distroless, kubectl reference, rollout, exec | `references/resource-debugging.md` | ~100 lines |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/SKILL.md')
    assert "**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references." in text, "expected to find: " + "**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/crash-diagnosis.md')
    assert 'Fix: Increase `resources.limits.memory` or fix the memory leak in the application. Do not blindly increase limits without checking actual usage first -- over-provisioning wastes cluster resources, and' in text, "expected to find: " + 'Fix: Increase `resources.limits.memory` or fix the memory leak in the application. Do not blindly increase limits without checking actual usage first -- over-provisioning wastes cluster resources, and'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/crash-diagnosis.md')
    assert 'CrashLoopBackOff means the container starts, exits, and Kubernetes restarts it with exponential backoff. Do not `kubectl delete pod` to "fix" this -- the replacement pod will crash the same way, and y' in text, "expected to find: " + 'CrashLoopBackOff means the container starts, exits, and Kubernetes restarts it with exponential backoff. Do not `kubectl delete pod` to "fix" this -- the replacement pod will crash the same way, and y'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/crash-diagnosis.md')
    assert '> **Scope**: CrashLoopBackOff (OOMKilled, config errors, health check failures), ImagePullBackOff (auth, tags, network), and Pending pod diagnosis (scheduling, affinity, taints, PVC). Does NOT cover n' in text, "expected to find: " + '> **Scope**: CrashLoopBackOff (OOMKilled, config errors, health check failures), ImagePullBackOff (auth, tags, network), and Pending pod diagnosis (scheduling, affinity, taints, PVC). Does NOT cover n'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/network-debugging.md')
    assert '> **Scope**: Service resolution, DNS debugging, port-forwarding for local testing, and NetworkPolicy verification. Does NOT cover pod crash diagnosis or resource limits.' in text, "expected to find: " + '> **Scope**: Service resolution, DNS debugging, port-forwarding for local testing, and NetworkPolicy verification. Does NOT cover pod crash diagnosis or resource limits.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/network-debugging.md')
    assert 'kubectl run dns-debug --rm -it --restart=Never --image=busybox:1.36 -n <namespace> -- \\' in text, "expected to find: " + 'kubectl run dns-debug --rm -it --restart=Never --image=busybox:1.36 -n <namespace> -- \\'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/network-debugging.md')
    assert '> **Version range**: Kubernetes 1.25+ (ephemeral containers assumed available)' in text, "expected to find: " + '> **Version range**: Kubernetes 1.25+ (ephemeral containers assumed available)'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/resource-debugging.md')
    assert '> **Scope**: CPU throttling detection, memory limits and OOMKill analysis, ephemeral storage pressure, ephemeral debug containers, and kubectl command reference table. Does NOT cover crash diagnosis r' in text, "expected to find: " + '> **Scope**: CPU throttling detection, memory limits and OOMKill analysis, ephemeral storage pressure, ephemeral debug containers, and kubectl command reference table. Does NOT cover crash diagnosis r'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/resource-debugging.md')
    assert 'Solution: Use `kubectl logs --previous` to get crash logs. If the container exits immediately, check the entrypoint command and environment variables.' in text, "expected to find: " + 'Solution: Use `kubectl logs --previous` to get crash logs. If the container exits immediately, check the entrypoint command and environment variables.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-debugging/references/resource-debugging.md')
    assert 'Solution: Check cluster version with `kubectl version`. For older clusters, create a standalone debug pod in the same namespace with `kubectl run`.' in text, "expected to find: " + 'Solution: Check cluster version with `kubectl version`. For older clusters, create a standalone debug pod in the same namespace with `kubectl run`.'[:80]

