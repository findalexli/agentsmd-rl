"""Behavioral checks for msbuild.sdk.sqlproj-add-copilot-cloud-agent-onboarding (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/msbuild.sdk.sqlproj")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- `dotnet build ./test/TestProjectWithGenerateScriptAndTargetDatabaseName/TestProjectWithGenerateScriptAndTargetDatabaseName.csproj -c Release`' in text, "expected to find: " + '- `dotnet build ./test/TestProjectWithGenerateScriptAndTargetDatabaseName/TestProjectWithGenerateScriptAndTargetDatabaseName.csproj -c Release`'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- For package/version resolution issues, inspect `ResolveDatabaseReferences` and `ValidateEnvironment` logic in `Sdk.targets` first.' in text, "expected to find: " + '- For package/version resolution issues, inspect `ResolveDatabaseReferences` and `ValidateEnvironment` logic in `Sdk.targets` first.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- When modifying SDK target behavior, validate at least one relevant `test/TestProject*` scenario build in addition to unit tests.' in text, "expected to find: " + '- When modifying SDK target behavior, validate at least one relevant `test/TestProject*` scenario build in addition to unit tests.'[:80]

