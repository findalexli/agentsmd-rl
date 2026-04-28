"""Behavioral checks for packmind-fix-replace-bare-nx-with (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/packmind")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)' in text, "expected to find: " + 'The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Testing**: Jest with @swc/jest as test runner. Tests are run with `./node_modules/.bin/nx run <project-name>` as detailed below.' in text, "expected to find: " + '- **Testing**: Jest with @swc/jest as test runner. Tests are run with `./node_modules/.bin/nx run <project-name>` as detailed below.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited" in text, "expected to find: " + "- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited"[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)' in text, "expected to find: " + 'The following commands apply for both NX apps and packages (use `./node_modules/.bin/nx show projects` to list actual apps and packages.)'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- **Testing**: Jest with @swc/jest as test runner. Tip: use `./node_modules/.bin/nx show projects` to list actual apps and packages.' in text, "expected to find: " + '- **Testing**: Jest with @swc/jest as test runner. Tip: use `./node_modules/.bin/nx show projects` to list actual apps and packages.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert "- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited" in text, "expected to find: " + "- Use the `./node_modules/.bin/nx lint` and `./node_modules/.bin/nx test` commands on the apps and packages you've edited"[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/AGENTS.md')
    assert '- Build an application: `./node_modules/.bin/nx build <app-name>`' in text, "expected to find: " + '- Build an application: `./node_modules/.bin/nx build <app-name>`'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/AGENTS.md')
    assert '- Test an application: `./node_modules/.bin/nx test <app-name>`' in text, "expected to find: " + '- Test an application: `./node_modules/.bin/nx test <app-name>`'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/AGENTS.md')
    assert '- Lint an application: `./node_modules/.bin/nx lint <app-name>`' in text, "expected to find: " + '- Lint an application: `./node_modules/.bin/nx lint <app-name>`'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/CLAUDE.md')
    assert '- Build an application: `./node_modules/.bin/nx build <app-name>`' in text, "expected to find: " + '- Build an application: `./node_modules/.bin/nx build <app-name>`'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/CLAUDE.md')
    assert '- Test an application: `./node_modules/.bin/nx test <app-name>`' in text, "expected to find: " + '- Test an application: `./node_modules/.bin/nx test <app-name>`'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/CLAUDE.md')
    assert '- Lint an application: `./node_modules/.bin/nx lint <app-name>`' in text, "expected to find: " + '- Lint an application: `./node_modules/.bin/nx lint <app-name>`'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/AGENTS.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck api`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck api`'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/AGENTS.md')
    assert '- Build: `./node_modules/.bin/nx build api`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build api`'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/AGENTS.md')
    assert '- Test: `./node_modules/.bin/nx test api`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test api`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/CLAUDE.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck api`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck api`'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/CLAUDE.md')
    assert '- Build: `./node_modules/.bin/nx build api`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build api`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/api/CLAUDE.md')
    assert '- Test: `./node_modules/.bin/nx test api`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test api`'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/AGENTS.md')
    assert '- Build: `./node_modules/.bin/nx build packmind-cli`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build packmind-cli`'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/AGENTS.md')
    assert '- Test: `./node_modules/.bin/nx test packmind-cli`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test packmind-cli`'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/AGENTS.md')
    assert '- Lint: `./node_modules/.bin/nx lint packmind-cli`' in text, "expected to find: " + '- Lint: `./node_modules/.bin/nx lint packmind-cli`'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/CLAUDE.md')
    assert '- Build: `./node_modules/.bin/nx build packmind-cli`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build packmind-cli`'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/CLAUDE.md')
    assert '- Test: `./node_modules/.bin/nx test packmind-cli`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test packmind-cli`'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/cli/CLAUDE.md')
    assert '- Lint: `./node_modules/.bin/nx lint packmind-cli`' in text, "expected to find: " + '- Lint: `./node_modules/.bin/nx lint packmind-cli`'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/AGENTS.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck frontend`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck frontend`'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/AGENTS.md')
    assert '- Build: `./node_modules/.bin/nx build frontend`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build frontend`'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/AGENTS.md')
    assert '- Test: `./node_modules/.bin/nx test frontend`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test frontend`'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/CLAUDE.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck frontend`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck frontend`'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/CLAUDE.md')
    assert '- Build: `./node_modules/.bin/nx build frontend`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build frontend`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/frontend/CLAUDE.md')
    assert '- Test: `./node_modules/.bin/nx test frontend`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test frontend`'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/AGENTS.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck mcp-server`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck mcp-server`'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/AGENTS.md')
    assert '- Build: `./node_modules/.bin/nx build mcp-server`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build mcp-server`'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/AGENTS.md')
    assert '- Test: `./node_modules/.bin/nx test mcp-server`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test mcp-server`'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/CLAUDE.md')
    assert '- Type check: `./node_modules/.bin/nx typecheck mcp-server`' in text, "expected to find: " + '- Type check: `./node_modules/.bin/nx typecheck mcp-server`'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/CLAUDE.md')
    assert '- Build: `./node_modules/.bin/nx build mcp-server`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build mcp-server`'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/mcp-server/CLAUDE.md')
    assert '- Test: `./node_modules/.bin/nx test mcp-server`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test mcp-server`'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/AGENTS.md')
    assert '- Build a package: `./node_modules/.bin/nx build <package-name>`' in text, "expected to find: " + '- Build a package: `./node_modules/.bin/nx build <package-name>`'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/AGENTS.md')
    assert '- Test a package: `./node_modules/.bin/nx test <package-name>`' in text, "expected to find: " + '- Test a package: `./node_modules/.bin/nx test <package-name>`'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/AGENTS.md')
    assert '- Lint a package: `./node_modules/.bin/nx lint <package-name>`' in text, "expected to find: " + '- Lint a package: `./node_modules/.bin/nx lint <package-name>`'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/CLAUDE.md')
    assert '- Build a package: `./node_modules/.bin/nx build <package-name>`' in text, "expected to find: " + '- Build a package: `./node_modules/.bin/nx build <package-name>`'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/CLAUDE.md')
    assert '- Test a package: `./node_modules/.bin/nx test <package-name>`' in text, "expected to find: " + '- Test a package: `./node_modules/.bin/nx test <package-name>`'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/CLAUDE.md')
    assert '- Lint a package: `./node_modules/.bin/nx lint <package-name>`' in text, "expected to find: " + '- Lint a package: `./node_modules/.bin/nx lint <package-name>`'[:80]


def test_signal_42():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/AGENTS.md')
    assert '- Build: `./node_modules/.bin/nx build ui`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build ui`'[:80]


def test_signal_43():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/AGENTS.md')
    assert '- Test: `./node_modules/.bin/nx test ui`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test ui`'[:80]


def test_signal_44():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/AGENTS.md')
    assert '- Lint: `./node_modules/.bin/nx lint ui`' in text, "expected to find: " + '- Lint: `./node_modules/.bin/nx lint ui`'[:80]


def test_signal_45():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/CLAUDE.md')
    assert '- Build: `./node_modules/.bin/nx build ui`' in text, "expected to find: " + '- Build: `./node_modules/.bin/nx build ui`'[:80]


def test_signal_46():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/CLAUDE.md')
    assert '- Test: `./node_modules/.bin/nx test ui`' in text, "expected to find: " + '- Test: `./node_modules/.bin/nx test ui`'[:80]


def test_signal_47():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/ui/CLAUDE.md')
    assert '- Lint: `./node_modules/.bin/nx lint ui`' in text, "expected to find: " + '- Lint: `./node_modules/.bin/nx lint ui`'[:80]

