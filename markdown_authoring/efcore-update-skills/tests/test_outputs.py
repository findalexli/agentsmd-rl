"""Behavioral checks for efcore-update-skills (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/efcore")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/analyzers/SKILL.md')
    assert '.agents/skills/analyzers/SKILL.md' in text, "expected to find: " + '.agents/skills/analyzers/SKILL.md'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/bulk-operations/SKILL.md')
    assert '.agents/skills/bulk-operations/SKILL.md' in text, "expected to find: " + '.agents/skills/bulk-operations/SKILL.md'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/cosmos-provider/SKILL.md')
    assert '.agents/skills/cosmos-provider/SKILL.md' in text, "expected to find: " + '.agents/skills/cosmos-provider/SKILL.md'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/dbcontext-and-services/SKILL.md')
    assert '.agents/skills/dbcontext-and-services/SKILL.md' in text, "expected to find: " + '.agents/skills/dbcontext-and-services/SKILL.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/make-custom-agent/SKILL.md')
    assert '| `user-invocable` | No | Show in agents dropdown (default: true) |' in text, "expected to find: " + '| `user-invocable` | No | Show in agents dropdown (default: true) |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/make-skill/SKILL.md')
    assert '- [ ] Can determine if the skill should be user-invocable or background knowledge only' in text, "expected to find: " + '- [ ] Can determine if the skill should be user-invocable or background knowledge only'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrations/SKILL.md')
    assert "- Model snapshots use `typeof(Dictionary<string, object>)` (property bag format), not the actual CLR type. When examining the `ClrType` in a snapshot, don't assume it matches the real entity type." in text, "expected to find: " + "- Model snapshots use `typeof(Dictionary<string, object>)` (property bag format), not the actual CLR type. When examining the `ClrType` in a snapshot, don't assume it matches the real entity type."[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrations/SKILL.md')
    assert '- `SnapshotModelProcessor.Process()` is used at design-time to fixup older model snapshots for backward compatibility.' in text, "expected to find: " + '- `SnapshotModelProcessor.Process()` is used at design-time to fixup older model snapshots for backward compatibility.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/migrations/SKILL.md')
    assert '## Model Snapshot' in text, "expected to find: " + '## Model Snapshot'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/query-pipeline/SKILL.md')
    assert "description: 'Implementation details for EF Core LINQ query translation, SQL generation, and bulk operations (ExecuteUpdate/ExecuteDelete). Use when changing expression visitors, SqlExpressions, Query" in text, "expected to find: " + "description: 'Implementation details for EF Core LINQ query translation, SQL generation, and bulk operations (ExecuteUpdate/ExecuteDelete). Use when changing expression visitors, SqlExpressions, Query"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/query-pipeline/SKILL.md')
    assert '3. **Postprocessing**' in text, "expected to find: " + '3. **Postprocessing**'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/query-pipeline/SKILL.md')
    assert '5. **SQL Generation**' in text, "expected to find: " + '5. **SQL Generation**'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/servicing-pr/SKILL.md')
    assert 'PRs targeting `release/*` branches require a specific description format and should include a quirk (AppContext switch) when applicable. When updating progress on a servicing PR, ensure that the descr' in text, "expected to find: " + 'PRs targeting `release/*` branches require a specific description format and should include a quirk (AppContext switch) when applicable. When updating progress on a servicing PR, ensure that the descr'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert '2. **Provider overrides**: Override in **every** provider functional test class (`EFCore.{Provider}.FunctionalTests`) that inherits the base with provider-appropriate assertions.' in text, "expected to find: " + '2. **Provider overrides**: Override in **every** provider functional test class (`EFCore.{Provider}.FunctionalTests`) that inherits the base with provider-appropriate assertions.'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert '6. When testing cross-platform code (e.g., file paths, path separators), verify the fix works on both Windows and Linux/macOS' in text, "expected to find: " + '6. When testing cross-platform code (e.g., file paths, path separators), verify the fix works on both Windows and Linux/macOS'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert "5. Run tests with project rebuilding enabled (don't use `--no-build`) to ensure code changes are picked up" in text, "expected to find: " + "5. Run tests with project rebuilding enabled (don't use `--no-build`) to ensure code changes are picked up"[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tooling/SKILL.md')
    assert 'NuGet package `Microsoft.EntityFrameworkCore.Tasks` provides build/publish-time compiled model and precompiled query generation. Targets in `buildTransitive/Microsoft.EntityFrameworkCore.Tasks.targets' in text, "expected to find: " + 'NuGet package `Microsoft.EntityFrameworkCore.Tasks` provides build/publish-time compiled model and precompiled query generation. Targets in `buildTransitive/Microsoft.EntityFrameworkCore.Tasks.targets'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tooling/SKILL.md')
    assert '`RootCommand` parses global options. Subcommands implemented in `src/ef/Commands/`. Each invokes MSBuild to build, then shells out via `dotnet exec ef.dll`, which hosts `OperationExecutor`.' in text, "expected to find: " + '`RootCommand` parses global options. Subcommands implemented in `src/ef/Commands/`. Each invokes MSBuild to build, then shells out via `dotnet exec ef.dll`, which hosts `OperationExecutor`.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/tooling/SKILL.md')
    assert 'PowerShell module: `Add-Migration`, `Update-Database`, `Scaffold-DbContext`, `Optimize-DbContext`, etc.' in text, "expected to find: " + 'PowerShell module: `Add-Migration`, `Update-Database`, `Scaffold-DbContext`, `Optimize-DbContext`, etc.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/update-pipeline/SKILL.md')
    assert '→ `ModificationCommand` per table row, composed of `ColumnModification` per column' in text, "expected to find: " + '→ `ModificationCommand` per table row, composed of `ColumnModification` per column'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/update-pipeline/SKILL.md')
    assert '→ `SharedTableEntryMap` is used to track entries mapped to the same row' in text, "expected to find: " + '→ `SharedTableEntryMap` is used to track entries mapped to the same row'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert "Skill files in `.agents/skills/` provide domain-specific knowledge so that agents don't need repetitive instructions from the user. Keep skills updated: when you discover non-obvious patterns, key fil" in text, "expected to find: " + "Skill files in `.agents/skills/` provide domain-specific knowledge so that agents don't need repetitive instructions from the user. Keep skills updated: when you discover non-obvious patterns, key fil"[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- **Prefer minimal comments** - The code should be self-explanatory. Add comments sparingly and only to explain *why* a non-intuitive solution was necessary, not *what* the code does. Comments are app' in text, "expected to find: " + '- **Prefer minimal comments** - The code should be self-explanatory. Add comments sparingly and only to explain *why* a non-intuitive solution was necessary, not *what* the code does. Comments are app'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Avoid breaking public APIs. If you need to break a public API, add a new API instead and mark the old one as obsolete. Use `ObsoleteAttribute` with the message pointing to the new API' in text, "expected to find: " + '- Avoid breaking public APIs. If you need to break a public API, add a new API instead and mark the old one as obsolete. Use `ObsoleteAttribute` with the message pointing to the new API'[:80]

