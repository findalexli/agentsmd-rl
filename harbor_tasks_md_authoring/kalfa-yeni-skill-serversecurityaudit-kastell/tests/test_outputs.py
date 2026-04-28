"""Behavioral checks for kalfa-yeni-skill-serversecurityaudit-kastell (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/kalfa")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/development/server-security-audit/SKILL.md')
    assert '> 19 adımın tamamı: SSH, fail2ban, UFW, SSH ciphers, sysctl, unattended-upgrades, login banners, account locking, cloud metadata block, DNS security, APT validation, resource limits, service disabling' in text, "expected to find: " + '> 19 adımın tamamı: SSH, fail2ban, UFW, SSH ciphers, sysctl, unattended-upgrades, login banners, account locking, cloud metadata block, DNS security, APT validation, resource limits, service disabling'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/development/server-security-audit/SKILL.md')
    assert '[Kastell](https://kastell.dev) — 13 MCP aracı: server_audit, server_lock, server_secure, server_doctor, server_fleet, server_info, server_logs, server_guard, server_evidence, server_backup, server_pro' in text, "expected to find: " + '[Kastell](https://kastell.dev) — 13 MCP aracı: server_audit, server_lock, server_secure, server_doctor, server_fleet, server_info, server_logs, server_guard, server_evidence, server_backup, server_pro'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/development/server-security-audit/SKILL.md')
    assert 'Production sunucularını kapsamlı güvenlik denetimine alın, zafiyetleri tespit edin ve otomatik sertleştirme uygulayın. Kastell MCP araçlarıyla tam yaşam döngüsü yönetimi.' in text, "expected to find: " + 'Production sunucularını kapsamlı güvenlik denetimine alın, zafiyetleri tespit edin ve otomatik sertleştirme uygulayın. Kastell MCP araçlarıyla tam yaşam döngüsü yönetimi.'[:80]

