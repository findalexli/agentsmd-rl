"""Behavioral checks for wcf-add-github-copilot-instructions (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wcf")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Localized strings use `.resx` files under `Resources/Strings.resx` in each project. The generated resource class uses a custom `ClassName` (e.g., `System.SRP` for Primitives, `System.SR` for others) —' in text, "expected to find: " + 'Localized strings use `.resx` files under `Resources/Strings.resx` in each project. The generated resource class uses a custom `ClassName` (e.g., `System.SRP` for Primitives, `System.SR` for others) —'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains the .NET (Core) WCF **client** libraries. These are the client-side subset of Windows Communication Foundation, ported to .NET Core/.NET. WCF *service* hosting is in the separ' in text, "expected to find: " + 'This repository contains the .NET (Core) WCF **client** libraries. These are the client-side subset of Windows Communication Foundation, ported to .NET Core/.NET. WCF *service* hosting is in the separ'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '**Deprecated packages**: `System.ServiceModel.Duplex` and `System.ServiceModel.Security` are retired (type-forward to Primitives). Their assemblies are bundled inside the Primitives NuGet package for ' in text, "expected to find: " + '**Deprecated packages**: `System.ServiceModel.Duplex` and `System.ServiceModel.Security` are retired (type-forward to Primitives). Their assemblies are bundled inside the Primitives NuGet package for '[:80]

