"""Behavioral checks for buildwithclaude-add-cfproxy-skill-free-vless (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/buildwithclaude")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/cf-proxy/SKILL.md')
    assert 'description: Deploy a free VLESS proxy/VPN node on Cloudflare Pages using edgetunnel. Automates code download, UUID generation, Pages deployment, free domain registration (DNSExit), DNS configuration,' in text, "expected to find: " + 'description: Deploy a free VLESS proxy/VPN node on Cloudflare Pages using edgetunnel. Automates code download, UUID generation, Pages deployment, free domain registration (DNSExit), DNS configuration,'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/cf-proxy/SKILL.md')
    assert '**Output**: Skill walks through the full 7-phase setup interactively — collecting Cloudflare credentials, generating config, deploying to Pages, registering a free domain if needed, configuring DNS, b' in text, "expected to find: " + '**Output**: Skill walks through the full 7-phase setup interactively — collecting Cloudflare credentials, generating config, deploying to Pages, registering a free domain if needed, configuring DNS, b'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('plugins/all-skills/skills/cf-proxy/SKILL.md')
    assert "- Always use a **subdomain** for CNAME records (e.g., `vless.example.com`), never the root domain — a root CNAME destroys the zone's SOA/NS records" in text, "expected to find: " + "- Always use a **subdomain** for CNAME records (e.g., `vless.example.com`), never the root domain — a root CNAME destroys the zone's SOA/NS records"[:80]

