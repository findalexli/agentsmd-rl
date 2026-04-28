"""Behavioral checks for nanoframework.iot.device-add-githubcopilotinstructionsmd-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/nanoframework.iot.device")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'This repository contains **IoT device bindings** (drivers) for [.NET nanoFramework](https://www.nanoframework.net/) — a free, open-source platform that enables running C# on resource-constrained embed' in text, "expected to find: " + 'This repository contains **IoT device bindings** (drivers) for [.NET nanoFramework](https://www.nanoframework.net/) — a free, open-source platform that enables running C# on resource-constrained embed'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Uses [Nerdbank.GitVersioning](https://github.com/dotnet/Nerdbank.GitVersioning). Each device has a `version.json` that sets the base version (e.g., `"version": "1.2"`). The full version is computed fr' in text, "expected to find: " + 'Uses [Nerdbank.GitVersioning](https://github.com/dotnet/Nerdbank.GitVersioning). Each device has a `version.json` that sets the base version (e.g., `"version": "1.2"`). The full version is computed fr'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'The build system requires **Windows + Visual Studio + MSBuild** with the nanoFramework project system components installed. The `dotnet build` / `dotnet restore` commands do **not** work for `.nfproj`' in text, "expected to find: " + 'The build system requires **Windows + Visual Studio + MSBuild** with the nanoFramework project system components installed. The `dotnet build` / `dotnet restore` commands do **not** work for `.nfproj`'[:80]

