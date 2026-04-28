"""Behavioral checks for content-add-claude-skills-for-profile (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/content")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **OCP4/Kubernetes rules** live under `applications/openshift/`, organized by component (e.g., `api-server/`, `kubelet/`, `etcd/`). Each component directory contains rule subdirectories. The rule ID ' in text, "expected to find: " + '- **OCP4/Kubernetes rules** live under `applications/openshift/`, organized by component (e.g., `api-server/`, `kubelet/`, `etcd/`). Each component directory contains rule subdirectories. The rule ID '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert 'Each supported operating system or platform is called a **product**. To see the full list of products, check the subdirectories under `products/` — each subdirectory name is a product ID (e.g., `rhel9' in text, "expected to find: " + 'Each supported operating system or platform is called a **product**. To see the full list of products, check the subdirectories under `products/` — each subdirectory name is a product ID (e.g., `rhel9'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/CLAUDE.md')
    assert '- **Linux rules** (RHEL, RHCOS, Fedora, Ubuntu, etc.) live under `linux_os/guide/`, organized by system area (e.g., `system/`, `services/`, `auditing/`). Browse the subdirectories to find the appropri' in text, "expected to find: " + '- **Linux rules** (RHEL, RHCOS, Fedora, Ubuntu, etc.) live under `linux_os/guide/`, organized by system area (e.g., `system/`, `services/`, `auditing/`). Browse the subdirectories to find the appropri'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/find-rule/SKILL.md')
    assert '6. **Present results** organized by match strength. For every rule, include a **Rationale** — a concise (1-2 sentence) explanation of why this rule satisfies or partially satisfies the requirement. Wr' in text, "expected to find: " + '6. **Present results** organized by match strength. For every rule, include a **Rationale** — a concise (1-2 sentence) explanation of why this rule satisfies or partially satisfies the requirement. Wr'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/find-rule/SKILL.md')
    assert '8. **Always suggest a control structure** with a `notes` field that includes a concise rationale for each rule, explaining why it was included for this control. This helps maintainers understand the r' in text, "expected to find: " + '8. **Always suggest a control structure** with a `notes` field that includes a concise rationale for each rule, explaining why it was included for this control. This helps maintainers understand the r'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/find-rule/SKILL.md')
    assert '2. **Respect scope constraints.** If the user specifies a scope (e.g., "only OpenShift control plane", "only node-level"), restrict results to that scope. Do not return rules outside the requested sco' in text, "expected to find: " + '2. **Respect scope constraints.** If the user specifies a scope (e.g., "only OpenShift control plane", "only node-level"), restrict results to that scope. Do not return rules outside the requested sco'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-profile/SKILL.md')
    assert '2. If the `product` field does not list all the products from the argument, warn the user and offer to update it. A control file needs all target products listed in its `product` field to work with ea' in text, "expected to find: " + '2. If the `product` field does not list all the products from the argument, warn the user and offer to update it. A control file needs all target products listed in its `product` field to work with ea'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-profile/SKILL.md')
    assert 'Check if a control file exists that matches the profile name. Control files live under `controls/` and `products/*/controls/`, typically named `<profile>_<product>.yml` or as a split directory with th' in text, "expected to find: " + 'Check if a control file exists that matches the profile name. Control files live under `controls/` and `products/*/controls/`, typically named `<profile>_<product>.yml` or as a split directory with th'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/manage-profile/SKILL.md')
    assert '- **Versioned profile** (e.g., `cis-v1-7-0.profile`): Contains the actual `selections`, `metadata.version`, and all profile configuration. Users pin to this for a stable baseline.' in text, "expected to find: " + '- **Versioned profile** (e.g., `cis-v1-7-0.profile`): Contains the actual `selections`, `metadata.version`, and all profile configuration. Users pin to this for a stable baseline.'[:80]

