"""Behavioral checks for aiida-core-add-agentsmd-and-claude-code (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aiida-core")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-a-cli-command/SKILL.md')
    assert 'CI enforces this via `verdi devel check-load-time`, which fails if any module outside `aiida.brokers`, `aiida.cmdline`, `aiida.common`, `aiida.manage`, `aiida.plugins`, or `aiida.restapi` is imported ' in text, "expected to find: " + 'CI enforces this via `verdi devel check-load-time`, which fails if any module outside `aiida.brokers`, `aiida.cmdline`, `aiida.common`, `aiida.manage`, `aiida.plugins`, or `aiida.restapi` is imported '[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-a-cli-command/SKILL.md')
    assert '`verdi` must load quickly even for `verdi --help`, so `aiida.*` imports inside `src/aiida/cmdline/` **must be deferred to inside the function body**, not placed at module top level:' in text, "expected to find: " + '`verdi` must load quickly even for `verdi --help`, so `aiida.*` imports inside `src/aiida/cmdline/` **must be deferred to inside the function body**, not placed at module top level:'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-a-cli-command/SKILL.md')
    assert "2. Use Click decorators plus AiiDA's custom decorators from `aiida.cmdline.utils.decorators` (e.g. `@decorators.with_dbenv()` for commands that need the storage backend loaded)." in text, "expected to find: " + "2. Use Click decorators plus AiiDA's custom decorators from `aiida.cmdline.utils.decorators` (e.g. `@decorators.with_dbenv()` for commands that need the storage backend loaded)."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-dependencies/SKILL.md')
    assert 'After modifying `pyproject.toml`, the `uv-lock` and `generate-conda-environment` pre-commit hooks will automatically update `uv.lock` and `environment.yml` to stay in sync.' in text, "expected to find: " + 'After modifying `pyproject.toml`, the `uv-lock` and `generate-conda-environment` pre-commit hooks will automatically update `uv.lock` and `environment.yml` to stay in sync.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-dependencies/SKILL.md')
    assert '- Is available on both [PyPI](https://pypi.org/) and [conda-forge](https://conda-forge.org/)' in text, "expected to find: " + '- Is available on both [PyPI](https://pypi.org/) and [conda-forge](https://conda-forge.org/)'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/adding-dependencies/SKILL.md')
    assert "description: Use when adding a new third-party dependency to aiida-core's `pyproject.toml`." in text, "expected to find: " + "description: Use when adding a new third-party dependency to aiida-core's `pyproject.toml`."[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/architecture-overview/SKILL.md')
    assert 'Other notable files: `ProcessBuilder` (`engine/processes/builder.py`), `Computer` (`orm/computers.py`), `Config` (`manage/configuration/config.py`), `Manager` (`manage/manager.py`), `DaemonClient` (`e' in text, "expected to find: " + 'Other notable files: `ProcessBuilder` (`engine/processes/builder.py`), `Computer` (`orm/computers.py`), `Config` (`manage/configuration/config.py`), `Manager` (`manage/manager.py`), `DaemonClient` (`e'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/architecture-overview/SKILL.md')
    assert '`pyproject.toml` (dependencies, entry points, ruff/mypy config), `uv.lock`, `.pre-commit-config.yaml`, `.readthedocs.yml`, `.github/workflows/`, `.docker/`.' in text, "expected to find: " + '`pyproject.toml` (dependencies, entry points, ruff/mypy config), `uv.lock`, `.pre-commit-config.yaml`, `.readthedocs.yml`, `.github/workflows/`, `.docker/`.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/architecture-overview/SKILL.md')
    assert '`stubgen` ships with `mypy`, which is part of the `pre-commit` optional dependencies (`uv sync --extra pre-commit` or just `uv sync` if already installed).' in text, "expected to find: " + '`stubgen` ships with `mypy`, which is part of the `pre-commit` optional dependencies (`uv sync --extra pre-commit` or just `uv sync` if already installed).'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit-conventions/SKILL.md')
    assert 'The emoji *is* the type indicator, so the message after it should be just the description: write `🐛 QueryBuilder crashes on empty filter`, not `🐛 Fix: QueryBuilder crashes on empty filter`.' in text, "expected to find: " + 'The emoji *is* the type indicator, so the message after it should be just the description: write `🐛 QueryBuilder crashes on empty filter`, not `🐛 Fix: QueryBuilder crashes on empty filter`.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit-conventions/SKILL.md')
    assert '- The `main` branch uses a `.post0` version suffix to indicate development after the last release (e.g., `2.6.0.post0` = development after `2.6.0`).' in text, "expected to find: " + '- The `main` branch uses a `.post0` version suffix to indicate development after the last release (e.g., `2.6.0.post0` = development after `2.6.0`).'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/commit-conventions/SKILL.md')
    assert 'Merging (maintainers): **Squash and merge** for single-issue PRs, **rebase and merge** for multi-commit PRs with individually significant commits.' in text, "expected to find: " + 'Merging (maintainers): **Squash and merge** for single-issue PRs, **rebase and merge** for multi-commit PRs with individually significant commits.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debugging-processes/SKILL.md')
    assert '- **Process state inconsistent with node attributes** : check whether `seal()` has been called; only `_updatable_attributes` can change on a stored `ProcessNode` before sealing.' in text, "expected to find: " + '- **Process state inconsistent with node attributes** : check whether `seal()` has been called; only `_updatable_attributes` can change on a stored `ProcessNode` before sealing.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debugging-processes/SKILL.md')
    assert "- **Daemon subprocess killed on shutdown** : daemon-launched subprocesses must pass `start_new_session=True` or they inherit the daemon's signal handling and die with it." in text, "expected to find: " + "- **Daemon subprocess killed on shutdown** : daemon-launched subprocesses must pass `start_new_session=True` or they inherit the daemon's signal handling and die with it."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/debugging-processes/SKILL.md')
    assert 'For CalcJobs specifically, jump to the remote working directory on the HPC (requires SSH access, which may not be available for sandboxed agents):' in text, "expected to find: " + 'For CalcJobs specifically, jump to the remote working directory on the HPC (requires SSH access, which may not be available for sandboxed agents):'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deprecating-api/SKILL.md')
    assert 'Data created with older AiiDA versions is guaranteed to work with newer versions (database migrations are applied automatically), so backwards compatibility matters.' in text, "expected to find: " + 'Data created with older AiiDA versions is guaranteed to work with newer versions (database migrations are applied automatically), so backwards compatibility matters.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deprecating-api/SKILL.md')
    assert 'Public API is anything importable from a second-level package (`from aiida.orm import ...`, `from aiida.engine import ...`).' in text, "expected to find: " + 'Public API is anything importable from a second-level package (`from aiida.orm import ...`, `from aiida.engine import ...`).'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/deprecating-api/SKILL.md')
    assert "Use the `warn_deprecation` helper, which handles `stacklevel=2` and respects the user's deprecation-visibility config:" in text, "expected to find: " + "Use the `warn_deprecation` helper, which handles `stacklevel=2` and respects the user's deprecation-visibility config:"[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/linting-and-ci/SKILL.md')
    assert 'Hooks worth knowing about: `uv-lock` (lockfile consistency), `imports` (auto-generates `__all__`), `nbstripout`, `generate-conda-environment`, `verdi-autodocs`.' in text, "expected to find: " + 'Hooks worth knowing about: `uv-lock` (lockfile consistency), `imports` (auto-generates `__all__`), `nbstripout`, `generate-conda-environment`, `verdi-autodocs`.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/linting-and-ci/SKILL.md')
    assert 'uv run pre-commit run --from-ref $(git merge-base main HEAD) --to-ref HEAD  # same, but robust when main has advanced' in text, "expected to find: " + 'uv run pre-commit run --from-ref $(git merge-base main HEAD) --to-ref HEAD  # same, but robust when main has advanced'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/linting-and-ci/SKILL.md')
    assert 'CI enforces import-time constraints on `src/aiida/cmdline/`; see the `adding-a-cli-command` skill for details.' in text, "expected to find: " + 'CI enforces import-time constraints on `src/aiida/cmdline/`; see the `adding-a-cli-command` skill for details.'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tests/SKILL.md')
    assert '`pytest-instafail` (show failures instantly, enabled by default), `pytest-xdist` (parallel via `-n`), `pytest-cov`, `pytest-timeout`, `pytest-rerunfailures`, `pytest-benchmark` (skipped by default), `' in text, "expected to find: " + '`pytest-instafail` (show failures instantly, enabled by default), `pytest-xdist` (parallel via `-n`), `pytest-cov`, `pytest-timeout`, `pytest-rerunfailures`, `pytest-benchmark` (skipped by default), `'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tests/SKILL.md')
    assert '- Tests have a default timeout of 240 seconds (`pytest-timeout`). Override per-test with `@pytest.mark.timeout(seconds)` if needed.' in text, "expected to find: " + '- Tests have a default timeout of 240 seconds (`pytest-timeout`). Override per-test with `@pytest.mark.timeout(seconds)` if needed.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/running-tests/SKILL.md')
    assert '- `presto`-marked tests use an in-memory `SqliteTempBackend`. If they fail, the bug is in the code, not in service configuration.' in text, "expected to find: " + '- `presto`-marked tests use an in-memory `SqliteTempBackend`. If they fail, the bug is in the code, not in service configuration.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-and-building-docs/SKILL.md')
    assert '- Documentation follows the [Divio documentation system](https://www.divio.com/blog/documentation/): tutorials (learning-oriented), how-to guides (goal-oriented), topics (understanding-oriented), refe' in text, "expected to find: " + '- Documentation follows the [Divio documentation system](https://www.divio.com/blog/documentation/): tutorials (learning-oriented), how-to guides (goal-oriented), topics (understanding-oriented), refe'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-and-building-docs/SKILL.md')
    assert 'For live-reloading during development, use `sphinx-autobuild` (not a project dependency, install manually):' in text, "expected to find: " + 'For live-reloading during development, use `sphinx-autobuild` (not a project dependency, install manually):'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-and-building-docs/SKILL.md')
    assert 'description: Use when writing, editing, or building documentation files (`.md`, `.rst`) under `docs/`.' in text, "expected to find: " + 'description: Use when writing, editing, or building documentation files (`.md`, `.rst`) under `docs/`.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-tests/SKILL.md')
    assert 'Mocks should only be used for genuinely external dependencies (network, SSH), cases where setup would be prohibitively complex, or when you need to force an exception that would not otherwise appear n' in text, "expected to find: " + 'Mocks should only be used for genuinely external dependencies (network, SSH), cases where setup would be prohibitively complex, or when you need to force an exception that would not otherwise appear n'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-tests/SKILL.md')
    assert "- **Test edge cases and failure paths.** Don't just test the happy path. Test boundary values, empty inputs, invalid arguments, and expected exceptions." in text, "expected to find: " + "- **Test edge cases and failure paths.** Don't just test the happy path. Test boundary values, empty inputs, invalid arguments, and expected exceptions."[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/writing-tests/SKILL.md')
    assert '- **One behavior per test.** Each test must be independent, deterministic, and must not test framework behavior (Python, SQLAlchemy, Click).' in text, "expected to find: " + '- **One behavior per test.** Each test must be independent, deterministic, and must not test framework behavior (Python, SQLAlchemy, Click).'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- **Provenance:** all data and computations are tracked as nodes in a directed acyclic graph (DAG). Nodes are immutable once stored, except extras (always mutable) and `ProcessNode._updatable_attribut' in text, "expected to find: " + '- **Provenance:** all data and computations are tracked as nodes in a directed acyclic graph (DAG). Nodes are immutable once stored, except extras (always mutable) and `ProcessNode._updatable_attribut'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert "**IMPORTANT**: Always use the project's tooling. Use `uv run` to run Python, tests, and tools (e.g., `uv run pytest`, `uv run pre-commit`). Never use bare `python` or `pip`. Check `pyproject.toml` and" in text, "expected to find: " + "**IMPORTANT**: Always use the project's tooling. Use `uv run` to run Python, tests, and tools (e.g., `uv run pytest`, `uv run pre-commit`). Never use bare `python` or `pip`. Check `pyproject.toml` and"[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'It is written in Python (see `pyproject.toml` for supported versions) and uses PostgreSQL/SQLite for metadata storage, [`disk-objectstore`](https://github.com/aiidateam/disk-objectstore) for file stor' in text, "expected to find: " + 'It is written in Python (see `pyproject.toml` for supported versions) and uses PostgreSQL/SQLite for metadata storage, [`disk-objectstore`](https://github.com/aiidateam/disk-objectstore) for file stor'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]

