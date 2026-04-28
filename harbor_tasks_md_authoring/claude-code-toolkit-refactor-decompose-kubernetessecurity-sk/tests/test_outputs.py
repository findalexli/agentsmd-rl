"""Behavioral checks for claude-code-toolkit-refactor-decompose-kubernetessecurity-sk (markdown_authoring task).

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
    text = _read('skills/kubernetes-security/SKILL.md')
    assert 'Use loaded reference knowledge to answer with concrete YAML manifests and specific configurations. The references contain complete, copy-paste-ready examples for each security domain.' in text, "expected to find: " + 'Use loaded reference knowledge to answer with concrete YAML manifests and specific configurations. The references contain complete, copy-paste-ready examples for each security domain.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/SKILL.md')
    assert '| PodSecurity, SecurityContext, runAsNonRoot, readOnlyRootFilesystem, restricted, baseline, image hardening, distroless, Dockerfile | `references/pod-security.md` | ~90 lines |' in text, "expected to find: " + '| PodSecurity, SecurityContext, runAsNonRoot, readOnlyRootFilesystem, restricted, baseline, image hardening, distroless, Dockerfile | `references/pod-security.md` | ~90 lines |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/SKILL.md')
    assert "Validate the security posture against the misconfiguration table in `references/supply-chain.md`. Flag any of the 8 common misconfigurations if present in the user's manifests." in text, "expected to find: " + "Validate the security posture against the misconfiguration table in `references/supply-chain.md`. Flag any of the 8 common misconfigurations if present in the user's manifests."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/network-policies.md')
    assert 'Start with a default-deny policy for both ingress and egress in every namespace. Apply this on day one, not later. Without network policies, lateral movement between compromised pods is trivial.' in text, "expected to find: " + 'Start with a default-deny policy for both ingress and egress in every namespace. Apply this on day one, not later. Without network policies, lateral movement between compromised pods is trivial.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/network-policies.md')
    assert 'Solution: Verify pod labels match the NetworkPolicy `podSelector` and `from`/`to` selectors. Use `kubectl describe networkpolicy` to inspect rules.' in text, "expected to find: " + 'Solution: Verify pod labels match the NetworkPolicy `podSelector` and `from`/`to` selectors. Use `kubectl describe networkpolicy` to inspect rules.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/network-policies.md')
    assert '> **Scope**: Default-deny NetworkPolicy YAML, allow-list patterns, DNS egress rules, and namespace isolation' in text, "expected to find: " + '> **Scope**: Default-deny NetworkPolicy YAML, allow-list patterns, DNS egress rules, and namespace isolation'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/pod-security.md')
    assert 'Kubernetes PodSecurity admission replaces the deprecated PodSecurityPolicy. Apply labels at the namespace level. All containers must run as non-root with a read-only root filesystem unless there is a ' in text, "expected to find: " + 'Kubernetes PodSecurity admission replaces the deprecated PodSecurityPolicy. Apply labels at the namespace level. All containers must run as non-root with a read-only root filesystem unless there is a '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/pod-security.md')
    assert 'Containers should never run as privileged or with elevated capabilities unless explicitly justified. Privileged mode grants full host access to an attacker if the pod is compromised. Use specific capa' in text, "expected to find: " + 'Containers should never run as privileged or with elevated capabilities unless explicitly justified. Privileged mode grants full host access to an attacker if the pod is compromised. Use specific capa'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/pod-security.md')
    assert '> **Scope**: PodSecurityStandards (Baseline, Restricted, Privileged), SecurityContext configuration, non-root enforcement, and image hardening' in text, "expected to find: " + '> **Scope**: PodSecurityStandards (Baseline, Restricted, Privileged), SecurityContext configuration, non-root enforcement, and image hardening'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/rbac-patterns.md')
    assert 'RBAC (Role-Based Access Control) is the primary authorization mechanism in Kubernetes. Grant the minimum permissions required. Prefer namespace-scoped Roles over ClusterRoles. Write exact verbs and re' in text, "expected to find: " + 'RBAC (Role-Based Access Control) is the primary authorization mechanism in Kubernetes. Grant the minimum permissions required. Prefer namespace-scoped Roles over ClusterRoles. Write exact verbs and re'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/rbac-patterns.md')
    assert 'Solution: Identify the API group, resource, and verb from the error message. Create or update a Role with the exact permissions needed. List specific verbs and resources.' in text, "expected to find: " + 'Solution: Identify the API group, resource, and verb from the error message. Create or update a Role with the exact permissions needed. List specific verbs and resources.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/rbac-patterns.md')
    assert '> **Scope**: Role, RoleBinding, ClusterRole YAML manifests and ServiceAccount best practices for least-privilege Kubernetes access control' in text, "expected to find: " + '> **Scope**: Role, RoleBinding, ClusterRole YAML manifests and ServiceAccount best practices for least-privilege Kubernetes access control'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/supply-chain.md')
    assert 'Supply chain security covers image provenance, admission-time policy enforcement, secret management, and misconfiguration detection. These controls complement RBAC, pod security, and network policies ' in text, "expected to find: " + 'Supply chain security covers image provenance, admission-time policy enforcement, secret management, and misconfiguration detection. These controls complement RBAC, pod security, and network policies '[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/supply-chain.md')
    assert 'Store secrets using Sealed Secrets or External Secrets Operator, not environment variables from manifests or checked-in YAML. Secrets exposed as env vars are visible in `kubectl describe pod` output, ' in text, "expected to find: " + 'Store secrets using Sealed Secrets or External Secrets Operator, not environment variables from manifests or checked-in YAML. Secrets exposed as env vars are visible in `kubectl describe pod` output, '[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/kubernetes-security/references/supply-chain.md')
    assert '> **Scope**: Image signing with cosign, admission controllers (Kyverno, OPA Gatekeeper), secret management (Sealed Secrets, External Secrets Operator), and common misconfiguration detection' in text, "expected to find: " + '> **Scope**: Image signing with cosign, admission controllers (Kyverno, OPA Gatekeeper), secret management (Sealed Secrets, External Secrets Operator), and common misconfiguration detection'[:80]

