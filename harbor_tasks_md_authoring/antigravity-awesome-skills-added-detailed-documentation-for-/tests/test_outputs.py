"""Behavioral checks for antigravity-awesome-skills-added-detailed-documentation-for- (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/antigravity-awesome-skills")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-backend/SKILL.md')
    assert 'description: Build ASP.NET Core 8+ backend services with EF Core, auth, background jobs, and production API patterns.' in text, "expected to find: " + 'description: Build ASP.NET Core 8+ backend services with EF Core, auth, background jobs, and production API patterns.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-backend/SKILL.md')
    assert 'You are an expert .NET/C# backend developer with 8+ years of experience building enterprise-grade APIs and services.' in text, "expected to find: " + 'You are an expert .NET/C# backend developer with 8+ years of experience building enterprise-grade APIs and services.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/dotnet-backend/SKILL.md')
    assert '- Cloud-provider-specific deployment details (Azure/AWS/GCP) are out of scope unless explicitly requested.' in text, "expected to find: " + '- Cloud-provider-specific deployment details (Azure/AWS/GCP) are out of scope unless explicitly requested.'[:80]

