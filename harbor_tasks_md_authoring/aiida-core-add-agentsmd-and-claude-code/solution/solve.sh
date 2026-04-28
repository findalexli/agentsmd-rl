#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aiida-core

# Idempotency guard
if grep -qF "CI enforces this via `verdi devel check-load-time`, which fails if any module ou" ".claude/skills/adding-a-cli-command/SKILL.md" && grep -qF "After modifying `pyproject.toml`, the `uv-lock` and `generate-conda-environment`" ".claude/skills/adding-dependencies/SKILL.md" && grep -qF "Other notable files: `ProcessBuilder` (`engine/processes/builder.py`), `Computer" ".claude/skills/architecture-overview/SKILL.md" && grep -qF "The emoji *is* the type indicator, so the message after it should be just the de" ".claude/skills/commit-conventions/SKILL.md" && grep -qF "- **Process state inconsistent with node attributes** : check whether `seal()` h" ".claude/skills/debugging-processes/SKILL.md" && grep -qF "Data created with older AiiDA versions is guaranteed to work with newer versions" ".claude/skills/deprecating-api/SKILL.md" && grep -qF "Hooks worth knowing about: `uv-lock` (lockfile consistency), `imports` (auto-gen" ".claude/skills/linting-and-ci/SKILL.md" && grep -qF "`pytest-instafail` (show failures instantly, enabled by default), `pytest-xdist`" ".claude/skills/running-tests/SKILL.md" && grep -qF "- Documentation follows the [Divio documentation system](https://www.divio.com/b" ".claude/skills/writing-and-building-docs/SKILL.md" && grep -qF "Mocks should only be used for genuinely external dependencies (network, SSH), ca" ".claude/skills/writing-tests/SKILL.md" && grep -qF "- **Provenance:** all data and computations are tracked as nodes in a directed a" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/adding-a-cli-command/SKILL.md b/.claude/skills/adding-a-cli-command/SKILL.md
@@ -0,0 +1,65 @@
+---
+name: adding-a-cli-command
+description: Use when adding a new `verdi` subcommand in `src/aiida/cmdline/`.
+---
+
+# Adding a new verdi CLI command
+
+## Steps
+
+1. Create the command under `src/aiida/cmdline/commands/`, typically as part of an existing `cmd_*.py` file (`cmd_process.py`, `cmd_calcjob.py`, `cmd_devel.py`, etc.).
+2. Use Click decorators plus AiiDA's custom decorators from `aiida.cmdline.utils.decorators` (e.g. `@decorators.with_dbenv()` for commands that need the storage backend loaded).
+3. Register the command in the appropriate command group (usually via `@<group>.command()`).
+4. Add tests in `tests/cmdline/commands/`.
+
+## Import-time constraint (CRITICAL)
+
+`verdi` must load quickly even for `verdi --help`, so `aiida.*` imports inside `src/aiida/cmdline/` **must be deferred to inside the function body**, not placed at module top level:
+
+```python
+# WRONG - will break CI via verdi devel check-load-time
+from aiida.orm import QueryBuilder
+
+@cmd_something.command()
+def my_command():
+    qb = QueryBuilder()
+    ...
+
+# RIGHT
+@cmd_something.command()
+def my_command():
+    from aiida.orm import QueryBuilder
+    qb = QueryBuilder()
+    ...
+```
+
+CI enforces this via `verdi devel check-load-time`, which fails if any module outside `aiida.brokers`, `aiida.cmdline`, `aiida.common`, `aiida.manage`, `aiida.plugins`, or `aiida.restapi` is imported at startup.
+
+At the top level of a `cmd_*.py` file, only `click`, standard library, and the whitelisted `aiida.*` submodules listed above may be imported.
+
+## Reusable arguments and options
+
+AiiDA provides a library of reusable, ALL_CAPS Click parameters in `src/aiida/cmdline/params/`: `arguments` (positional) and `options` (flags).
+Always check for an existing one before defining ad-hoc `click.argument()` / `click.option()` calls.
+
+```python
+from aiida.cmdline.params import arguments, options
+
+@verdi_process.command('show')
+@arguments.PROCESSES()
+@options.RAW()
+def process_show(processes, raw):
+    ...
+```
+
+Both are wrapped in `OverridableArgument` / `OverridableOption` classes that store defaults but allow per-command customization via `.clone()`.
+
+## Relevant source
+
+- Decorators: `src/aiida/cmdline/utils/decorators.py`
+- Existing commands: `src/aiida/cmdline/commands/cmd_*.py`
+- Reusable arguments: `src/aiida/cmdline/params/arguments/main.py`
+- Reusable options: `src/aiida/cmdline/params/options/main.py`
+- Custom option types: `src/aiida/cmdline/params/options/{callable,conditional,interactive,multivalue,config}.py`
+- Parameter types (ParamType subclasses): `src/aiida/cmdline/params/types/`
+- Load-time check implementation: `src/aiida/cmdline/commands/cmd_devel.py` (`check-load-time`)
diff --git a/.claude/skills/adding-dependencies/SKILL.md b/.claude/skills/adding-dependencies/SKILL.md
@@ -0,0 +1,17 @@
+---
+name: adding-dependencies
+description: Use when adding a new third-party dependency to aiida-core's `pyproject.toml`.
+---
+
+# Adding dependencies to aiida-core
+
+Before adding a new dependency to `pyproject.toml`, ensure it:
+
+- Fills a non-trivial feature gap not easily resolved otherwise
+- Is actively maintained
+- Supports all Python versions supported by aiida-core
+- Is available on both [PyPI](https://pypi.org/) and [conda-forge](https://conda-forge.org/)
+- Uses an MIT-compatible license (MIT, BSD, Apache, LGPL — **not** GPL)
+
+After modifying `pyproject.toml`, the `uv-lock` and `generate-conda-environment` pre-commit hooks will automatically update `uv.lock` and `environment.yml` to stay in sync.
+Run `uv run pre-commit` to trigger them.
diff --git a/.claude/skills/architecture-overview/SKILL.md b/.claude/skills/architecture-overview/SKILL.md
@@ -0,0 +1,82 @@
+---
+name: architecture-overview
+description: Use when exploring the aiida-core codebase structure, looking for key files, or understanding how packages relate to each other.
+---
+
+# AiiDA Core Architecture
+
+## Source layout
+
+The source code lives under `src/aiida/` with these main packages:
+
+| Package | Purpose |
+|---------|---------|
+| `brokers/` | Message broker interface (RabbitMQ via [`kiwipy`](https://github.com/aiidateam/kiwipy)) |
+| `calculations/` | Built-in calculations |
+| `cmdline/` | CLI (`verdi` command) built with `click` |
+| `common/` | Shared utilities, exceptions, warnings, constants |
+| `engine/` | Workflow engine: process runner, daemon, persistence, transport tasks (with [`plumpy`](https://github.com/aiidateam/plumpy) dependency) |
+| `manage/` | Configuration management, manager singleton |
+| `orm/` | Object-relational mapping: nodes, groups, users, computers, querybuilder |
+| `parsers/` | Built-in parser plugins |
+| `plugins/` | Plugin entry point system and factories |
+| `repository/` | File repository abstraction layer |
+| `restapi/` | Flask-based REST API (soon to be replaced by `aiida-restapi`) |
+| `schedulers/` | Built-in HPC scheduler plugins (SLURM, PBS, SGE, LSF, etc.) |
+| `storage/` | Storage backends (primarily `psql_dos` (`sqlite_dos`) for PostgreSQL (SQLite) + disk-objectstore) |
+| `tools/` | Utility tools (graph visualization, archive operations, data dumping, etc.) |
+| `transports/` | Built-in Transport plugins (SSH, local) |
+| `workflows/` | Built-in workflows |
+
+## Key entry points
+
+| Area | Key file(s) | Purpose |
+|------|------------|---------|
+| Engine core | `src/aiida/engine/processes/process.py` | Base `Process` class |
+| CalcJob | `src/aiida/engine/processes/calcjobs/calcjob.py` | `CalcJob` implementation |
+| CalcJob file ops | `src/aiida/engine/daemon/execmanager.py` | File copying, job submission, retrieval |
+| WorkChain | `src/aiida/engine/processes/workchains/workchain.py` | `WorkChain` implementation |
+| ORM node | `src/aiida/orm/nodes/node.py` | Base `Node` class |
+| QueryBuilder | `src/aiida/orm/querybuilder.py` | Query interface for the provenance graph |
+| Process runner | `src/aiida/engine/runners.py` | `Runner` executes and submits processes |
+| Plugin factories | `src/aiida/plugins/factories.py` | `DataFactory`, `CalculationFactory`, etc. |
+| Storage ABC | `src/aiida/orm/implementation/storage_backend.py` | `StorageBackend` abstract base class |
+| Transport ABC | `src/aiida/transports/transport.py` | `Transport`, `BlockingTransport`, `AsyncTransport` |
+| Scheduler ABC | `src/aiida/schedulers/scheduler.py` | `Scheduler` base class |
+
+Other notable files: `ProcessBuilder` (`engine/processes/builder.py`), `Computer` (`orm/computers.py`), `Config` (`manage/configuration/config.py`), `Manager` (`manage/manager.py`), `DaemonClient` (`engine/daemon/client.py`), `Profile` (`manage/configuration/profile.py`), `psql_dos` backend (`storage/psql_dos/backend.py`), `RabbitmqBroker` (`brokers/rabbitmq/broker.py`), `Repository` (`repository/repository.py`).
+
+## Database and file storage
+
+- ORM: SQLAlchemy. File storage: disk-objectstore. Migrations: Alembic (under `src/aiida/storage/psql_dos/migrations/`).
+- Main backend: `psql_dos` (PostgreSQL + disk-objectstore). Lightweight: `sqlite_dos` (SQLite + disk-objectstore).
+
+## Abstract base classes (ABCs)
+
+AiiDA defines ABCs for extensible components.
+To create a plugin, implement the corresponding ABC and register it as an entry point.
+
+| ABC | Location | Purpose | Entry point |
+|-----|----------|---------|-------------|
+| `Transport` | `aiida.transports.transport` | File transfer and remote command execution | `aiida.transports` |
+| `Scheduler` | `aiida.schedulers.scheduler` | HPC job scheduler interface | `aiida.schedulers` |
+| `Parser` | `aiida.parsers.parser` | Parse calculation outputs | `aiida.parsers` |
+| `StorageBackend` | `aiida.orm.implementation.storage_backend` | Database and file storage | `aiida.storage` |
+| `AbstractCode` | `aiida.orm.nodes.data.code.abstract` | Code/executable representation | `aiida.data` |
+| `CalcJobImporter` | `aiida.engine.processes.calcjobs.importer` | Import existing calculation results | `aiida.calculations.importers` |
+
+## Quick API overview via stubs
+
+To get a compact view of a module's public API without reading the full source (which can pollute context), generate type stubs:
+
+```bash
+uv run stubgen -p aiida.orm -o /tmp/stubs             # public API only
+uv run stubgen -p aiida.orm -o /tmp/stubs --include-private  # include _private members
+```
+
+The generated `.pyi` files show only signatures, classes, and type annotations, useful for understanding an API surface quickly.
+`stubgen` ships with `mypy`, which is part of the `pre-commit` optional dependencies (`uv sync --extra pre-commit` or just `uv sync` if already installed).
+
+## Project configuration
+
+`pyproject.toml` (dependencies, entry points, ruff/mypy config), `uv.lock`, `.pre-commit-config.yaml`, `.readthedocs.yml`, `.github/workflows/`, `.docker/`.
diff --git a/.claude/skills/commit-conventions/SKILL.md b/.claude/skills/commit-conventions/SKILL.md
@@ -0,0 +1,75 @@
+---
+name: commit-conventions
+description: Use when making commits, creating branches, or preparing pull requests for aiida-core.
+---
+
+# Commit and PR conventions for aiida-core
+
+## Branching and versioning
+
+- All development happens on `main` through pull requests.
+- Recommended branch naming convention: `<prefix>/<issue>/<short_description>`
+  - Prefixes: `feature/`, `fix/`, `docs/`, `ci/`, `refactor/`
+  - Example: `fix/1234/querybuilder-improvements`
+- The `main` branch uses a `.post0` version suffix to indicate development after the last release (e.g., `2.6.0.post0` = development after `2.6.0`).
+- Versioning follows [SemVer](https://semver.org/) (major.minor.patch).
+
+## Commit style (not enforced)
+
+Follow the **50/72 rule**:
+
+- Subject line: max 50 characters, imperative mood ("Add feature", not "Added feature"), capitalized, no period
+- Body: wrap at 72 characters, explain *what* and *why* (the code shows *how*)
+- Merged PRs (via squash) append the PR number: `Fix bug in QueryBuilder (#1234)` (GH web UI automatically appends on squash-merge)
+- Some contributors use emoji prefixes as a semantic type indicator (see below)
+
+```
+Short summary in imperative mood (50 chars)
+
+More detailed explanation wrapped at 72 characters. Focus on
+why the change was made, not how.
+```
+
+Guidelines:
+
+- One issue per commit, self-contained changes: makes bisecting and reverting safe
+- Link GitHub issues either via the PR description or the GH web UI.
+
+## Emoji prefixes (up for discussion)
+
+The following practices are used by some contributors but not consistently adopted.
+They may be formalized or dropped in the future.
+
+Some contributors use emojis as a one-character semantic type prefix.
+The emoji *is* the type indicator, so the message after it should be just the description: write `🐛 QueryBuilder crashes on empty filter`, not `🐛 Fix: QueryBuilder crashes on empty filter`.
+Emoji selection is adapted from [MyST-Parser](https://github.com/executablebooks/MyST-Parser/blob/master/AGENTS.md#commit-message-format):
+
+| Emoji | Meaning | Branch Prefix |
+|-------|---------|---------------|
+| `✨` | New feature | `feature/` |
+| `🐛` | Bug fix | `fix/` |
+| `🚑` | Hotfix (urgent production fix) | `hotfix/` |
+| `👌` | Improvement (no breaking changes) | `improve/` |
+| `‼️` | Breaking change | `breaking/` |
+| `📚` | Documentation | `docs/` |
+| `🔧` | Maintenance (typos, etc.) | `chore/` |
+| `🧪` | Tests or CI changes only | `test/` |
+| `♻️` | Refactoring | `refactor/` |
+| `⬆️` | Dependency upgrade | `deps/` |
+| `🔖` | Release | `release/` |
+
+## Pull request requirements
+
+When submitting changes:
+
+1. **Description**: Include a meaningful description explaining the change and link to related issues
+2. **Tests**: Include test cases for new functionality or bug fixes
+3. **Documentation**: Update docs if behavior changes or new features are added
+4. **Code quality**: Ensure `uv run pre-commit` passes
+
+Merging (maintainers): **Squash and merge** for single-issue PRs, **rebase and merge** for multi-commit PRs with individually significant commits.
+
+## Git tooling
+
+The `.git-blame-ignore-revs` file lists commits that should be ignored by `git blame` (e.g., bulk reformatting).
+When landing a large-scale formatting-only commit, add its SHA to this file.
diff --git a/.claude/skills/debugging-processes/SKILL.md b/.claude/skills/debugging-processes/SKILL.md
@@ -0,0 +1,75 @@
+---
+name: debugging-processes
+description: Use when diagnosing failed, stuck, or misbehaving AiiDA processes or the daemon.
+---
+
+# Debugging processes and the daemon
+
+## Inspecting a single process
+
+```bash
+verdi process status <PK>       # call stack and where execution stopped
+verdi process report <PK>       # log messages emitted during execution
+verdi process show <PK>         # inputs, outputs, exit code
+verdi node show <PK>            # node attributes and extras
+```
+
+For a full provenance dump including input/output files:
+
+```bash
+verdi process dump <PK>         # dump a process and its provenance
+```
+
+For CalcJobs specifically, jump to the remote working directory on the HPC (requires SSH access, which may not be available for sandboxed agents):
+
+```bash
+verdi calcjob gotocomputer <PK>
+```
+
+## Inspecting the daemon
+
+```bash
+# storage (PostgreSQL or SQLite) + daemon & broker (RabbitMQ, if configured):
+verdi status
+# tail daemon logs in real-time
+# best with a single daemon worker, multiple workers garble output:
+verdi daemon logshow
+# requeue processes stuck after a daemon crash (stop the daemon first):
+verdi process repair
+```
+
+## Common failure modes
+
+- **Process stuck in `waiting`** : usually means the daemon lost track of it after a crash or restart. Run `verdi process repair` to requeue.
+- **Process state inconsistent with node attributes** : check whether `seal()` has been called; only `_updatable_attributes` can change on a stored `ProcessNode` before sealing.
+- **`presto`-marked test failures** : these use an in-memory `SqliteTempBackend`, so the bug is in the code, not in service configuration.
+- **Daemon subprocess killed on shutdown** : daemon-launched subprocesses must pass `start_new_session=True` or they inherit the daemon's signal handling and die with it.
+
+## Interactive inspection
+
+```bash
+verdi shell                       # interactive IPython shell with AiiDA loaded
+verdi devel run-sql "SELECT ..."  # run raw SQL against the profile database (USE WITH CAUTION)
+```
+
+Useful patterns inside `verdi shell`:
+
+```python
+from aiida.orm import QueryBuilder, Node, load_node
+
+# Find nodes by type
+qb = QueryBuilder().append(Node, filters={'node_type': {'like': 'data.core.dict.%'}})
+
+# Inspect a specific node
+node = load_node(<PK>)
+node.base.attributes.all   # all stored attributes
+node.base.extras.all        # all extras (mutable even after storing)
+node.base.repository.list_object_names()  # files in the node's repository
+```
+
+## Related source
+
+- Process runner: `src/aiida/engine/runners.py`
+- Daemon client: `src/aiida/engine/daemon/client.py`
+- CalcJob exec manager (file copying, job submission, retrieval): `src/aiida/engine/daemon/execmanager.py`
+- Transport tasks (submit, update, retrieve): `src/aiida/engine/processes/calcjobs/tasks.py`
diff --git a/.claude/skills/deprecating-api/SKILL.md b/.claude/skills/deprecating-api/SKILL.md
@@ -0,0 +1,57 @@
+---
+name: deprecating-api
+description: Use when deprecating a public Python API or `verdi` CLI command in aiida-core.
+---
+
+# Deprecating API in aiida-core
+
+Public API is anything importable from a second-level package (`from aiida.orm import ...`, `from aiida.engine import ...`).
+Public API must go through a deprecation cycle before removal.
+Data created with older AiiDA versions is guaranteed to work with newer versions (database migrations are applied automatically), so backwards compatibility matters.
+
+## Python API
+
+Use the `warn_deprecation` helper, which handles `stacklevel=2` and respects the user's deprecation-visibility config:
+
+```python
+from aiida.common.warnings import warn_deprecation
+
+def old_function(x):
+    warn_deprecation('`old_function` is deprecated, use `new_function` instead.', version=3)
+    return new_function(x)
+```
+
+Add a `.. deprecated::` note to the docstring with replacement guidance:
+
+```python
+def old_function(x):
+    """Do the thing.
+
+    .. deprecated:: 2.7
+       Use :func:`new_function` instead. Will be removed in 3.0.
+    """
+```
+
+## CLI commands
+
+Use `@decorators.deprecated_command()` from `aiida.cmdline.utils.decorators`:
+
+```python
+from aiida.cmdline.utils import decorators
+
+@verdi_group.command('old-command')
+@decorators.deprecated_command('Use `verdi new-command` instead.')
+def old_command():
+    ...
+```
+
+## Removal timeline
+
+- Minor release: add the deprecation warning, update docstrings and user-facing docs.
+- Next major release: remove the deprecated API.
+- Users can surface all pending deprecation warnings by setting `AIIDA_WARN_v3=1`.
+
+## Relevant source
+
+- Warning classes: `src/aiida/common/warnings.py`
+- CLI deprecation decorator: `src/aiida/cmdline/utils/decorators.py`
diff --git a/.claude/skills/linting-and-ci/SKILL.md b/.claude/skills/linting-and-ci/SKILL.md
@@ -0,0 +1,35 @@
+---
+name: linting-and-ci
+description: Use when running pre-commit, linting, type checking, or fixing CI failures in aiida-core.
+---
+
+# Linting, pre-commit, and CI in aiida-core
+
+Always invoke via `uv run` so tools pick up the locked project environment.
+Never use bare `python` or `pip`.
+
+## Pre-commit
+
+```bash
+uv run pre-commit                                    # check staged files
+uv run pre-commit run --all-files                    # check everything
+uv run pre-commit run mypy                           # run a specific hook
+uv run pre-commit run ruff --all-files               # run ruff on all files
+uv run pre-commit run --from-ref main --to-ref HEAD  # check only changes since branching off main
+uv run pre-commit run --from-ref $(git merge-base main HEAD) --to-ref HEAD  # same, but robust when main has advanced
+```
+
+Hooks worth knowing about: `uv-lock` (lockfile consistency), `imports` (auto-generates `__all__`), `nbstripout`, `generate-conda-environment`, `verdi-autodocs`.
+
+CI enforces import-time constraints on `src/aiida/cmdline/`; see the `adding-a-cli-command` skill for details.
+
+## Other verdi development helpers
+
+```bash
+verdi shell                       # IPython shell with AiiDA loaded
+verdi status                      # service status (daemon, storage, broker if configured)
+verdi daemon start/stop/restart   # manage the daemon
+verdi devel check-load-time       # check for import-time violations
+```
+
+Set `AIIDA_WARN_v3=1` to surface deprecation warnings.
diff --git a/.claude/skills/running-tests/SKILL.md b/.claude/skills/running-tests/SKILL.md
@@ -0,0 +1,51 @@
+---
+name: running-tests
+description: Use when running pytest, checking test results, or understanding test infrastructure in aiida-core.
+---
+
+# Running tests in aiida-core
+
+Always invoke via `uv run` so tests pick up the locked project environment.
+Never use bare `python` or `pytest`.
+
+## Installing the dev environment
+
+```bash
+uv sync                                           # install from uv.lock
+```
+
+## Running tests
+
+```bash
+uv run pytest                                     # full suite (requires PostgreSQL + RabbitMQ)
+uv run pytest -m presto                           # quick subset (SqliteTempBackend, no services)
+uv run pytest tests/orm/test_nodes.py             # specific module
+uv run pytest tests/orm/test_nodes.py::TestNode   # specific class
+uv run pytest tests/orm/test_nodes.py::TestNode::test_store  # specific method
+uv run pytest -n auto                             # parallel
+uv run pytest -x --ff                             # stop on first failure, failed first on rerun
+uv run pytest --no-instafail                       # disable instant failure output (enabled by default via addopts)
+uv run pytest --cov aiida                         # run with coverage
+```
+
+## Pytest plugins and default options
+
+The project uses several pytest plugins (configured in `pyproject.toml` under `[tool.pytest.ini_options]`):
+`pytest-instafail` (show failures instantly, enabled by default), `pytest-xdist` (parallel via `-n`), `pytest-cov`, `pytest-timeout`, `pytest-rerunfailures`, `pytest-benchmark` (skipped by default), `pytest-regressions`.
+
+Default `addopts`: `--instafail --tb=short --strict-config --strict-markers -ra --benchmark-skip --durations=5`.
+
+## Notes
+
+- `presto`-marked tests use an in-memory `SqliteTempBackend`. If they fail, the bug is in the code, not in service configuration.
+- Tests have a default timeout of 240 seconds (`pytest-timeout`). Override per-test with `@pytest.mark.timeout(seconds)` if needed.
+- Transport tests require passwordless SSH to localhost.
+- Reusable fixtures live in `tests/conftest.py` and per-subtree `conftest.py` files, check there before writing ad-hoc setup.
+- See the `writing-tests` skill for test philosophy, marker conventions, and parametrization patterns.
+
+## verdi test helpers
+
+```bash
+verdi devel launch-add            # launch test ArithmeticAddCalculation
+verdi devel launch-multiply-add   # launch test MultiplyAddWorkChain
+```
diff --git a/.claude/skills/writing-and-building-docs/SKILL.md b/.claude/skills/writing-and-building-docs/SKILL.md
@@ -0,0 +1,26 @@
+---
+name: writing-and-building-docs
+description: Use when writing, editing, or building documentation files (`.md`, `.rst`) under `docs/`.
+---
+
+# Writing and building documentation for aiida-core
+
+When writing or editing `.md` or `.rst` files under `docs/`:
+
+- Write **one sentence per line** (no manual line wrapping): makes diffs easy to review.
+- File/directory names: alphanumeric, lowercase, underscores as separators.
+- Headers in **sentence case** (e.g., "Entry points", not "Entry Points").
+- Documentation follows the [Divio documentation system](https://www.divio.com/blog/documentation/): tutorials (learning-oriented), how-to guides (goal-oriented), topics (understanding-oriented), reference (information-oriented).
+
+## Building the docs
+
+```bash
+uv run sphinx-build -b html docs/source docs/build/html
+```
+
+For live-reloading during development, use `sphinx-autobuild` (not a project dependency, install manually):
+
+```bash
+uv pip install sphinx-autobuild
+uv run sphinx-autobuild docs/source docs/build/html
+```
diff --git a/.claude/skills/writing-tests/SKILL.md b/.claude/skills/writing-tests/SKILL.md
@@ -0,0 +1,55 @@
+---
+name: writing-tests
+description: Use when writing new pytest tests, fixtures, or regression tests for aiida-core.
+---
+
+# Writing tests for aiida-core
+
+Tests live under `tests/` and mirror the source layout in `src/aiida/`.
+Reusable fixtures live in `tests/conftest.py` and per-subtree `conftest.py` files.
+
+## Philosophy
+
+- **Prefer real objects over mocks.** Use fixtures to create real nodes, processes, computers, etc.
+  Mocks should only be used for genuinely external dependencies (network, SSH), cases where setup would be prohibitively complex, or when you need to force an exception that would not otherwise appear naturally.
+- **Don't chase coverage with shallow tests.** A test that mocks everything tests nothing.
+- **Test the contract, not the implementation.** Assert observable outcomes, not internal method calls.
+- **Make assertions as strong as possible.** `assert result == expected_value`, not `assert result is not None`.
+  Check exact values, types, and lengths.
+- **Regression tests for bugs.** First write a test that reproduces the bug, then fix the code.
+- **Test edge cases and failure paths.** Don't just test the happy path. Test boundary values, empty inputs, invalid arguments, and expected exceptions.
+- **One behavior per test.** Each test must be independent, deterministic, and must not test framework behavior (Python, SQLAlchemy, Click).
+
+## Marker conventions
+
+- `@pytest.mark.presto`: runs against `SqliteTempBackend` (in-memory, no PostgreSQL / RabbitMQ).
+  Prefer `presto`-compatible tests where possible: they are much faster and runnable in any environment.
+- `@pytest.mark.requires_rmq`: requires a running RabbitMQ instance.
+- `@pytest.mark.requires_psql`: requires a running PostgreSQL instance.
+- `@pytest.mark.nightly`: long-running tests, only executed in nightly CI.
+- Transport tests require passwordless SSH to localhost.
+
+## Parametrization
+
+Use `pytest.mark.parametrize` instead of duplicating test bodies:
+
+```python
+import pytest
+
+@pytest.mark.parametrize('value,expected', [
+    (1, 2),
+    (2, 4),
+    (3, 6),
+])
+def test_double(value, expected):
+    assert double(value) == expected
+```
+
+## Fixtures
+
+Check `tests/conftest.py` before writing ad-hoc setup.
+If you find yourself reinventing a fixture, it probably already exists.
+
+## Running the tests
+
+See the `running-tests` skill for the full `uv run pytest` cheatsheet.
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,85 @@
+# AGENTS.md - AI Coding Assistant Guide for AiiDA Core
+
+This file provides context for AI coding assistants (Claude Code, GitHub Copilot, etc.) working on the `aiida-core` codebase.
+
+**IMPORTANT**: Always use the project's tooling. Use `uv run` to run Python, tests, and tools (e.g., `uv run pytest`, `uv run pre-commit`). Never use bare `python` or `pip`. Check `pyproject.toml` and `.pre-commit-config.yaml` for the full configuration.
+
+## Project overview
+
+AiiDA is a workflow manager for computational science with a strong focus on provenance, performance, and extensibility.
+It is written in Python (see `pyproject.toml` for supported versions) and uses PostgreSQL/SQLite for metadata storage, [`disk-objectstore`](https://github.com/aiidateam/disk-objectstore) for file storage, and RabbitMQ as a message broker.
+
+## Key design concepts
+
+- **Provenance:** all data and computations are tracked as nodes in a directed acyclic graph (DAG). Nodes are immutable once stored, except extras (always mutable) and `ProcessNode._updatable_attributes` (process state, exit status, checkpoint, etc., mutable until `seal()`).
+- **Process/Node duality:** processes (`CalcJob`, `WorkChain`, `calcfunction`, `workfunction`) define *how* to run; process nodes record *that* something ran.
+- **CREATE vs RETURN links:** calculations *create* new data nodes; workflows *return* existing data nodes. Workflows orchestrate but don't create data themselves.
+- **Don't break provenance:** never circumvent the link system or modify stored nodes in ways that would break the DAG.
+- **Public API:** anything importable from a second-level package (e.g., `from aiida.orm import ...`) is public API with deprecation guarantees. Deeper internal modules may change without notice.
+- **Plugin system:** entry points (`pyproject.toml` `[project.entry-points]`) allow extending AiiDA with new calculation types, data types, schedulers, transports, and storage backends.
+- **Daemon signal handling:** the daemon captures `SIGINT`/`SIGTERM` for graceful shutdown. Subprocesses in daemon code must pass `start_new_session=True`.
+
+### Process / Node duality
+
+Each process class has a corresponding node class that records its execution:
+
+| Process class | Node class | Link types |
+|--------------|------------|------------|
+| `@calcfunction` | `CalcFunctionNode` | INPUT_CALC → CREATE |
+| `CalcJob` | `CalcJobNode` | INPUT_CALC → CREATE |
+| `@workfunction` | `WorkFunctionNode` | INPUT_WORK → RETURN/CALL |
+| `WorkChain` | `WorkChainNode` | INPUT_WORK → RETURN/CALL |
+
+## Code style
+
+Code style is enforced via **pre-commit hooks** (`.pre-commit-config.yaml`). Always run `uv run pre-commit` before pushing.
+Formatting: `ruff`. Type checking: `mypy`. Write new code following ruff conventions with proper type hints.
+Docstrings: Sphinx-style (`:param:`, `:return:`, `:raises:`), types in annotations not docstrings. Prefer `pathlib` over `os.path`.
+New source files should include the standard copyright header (copy from any existing `.py` file).
+In `cmdline/`: delay `aiida` imports to function level (keeps `verdi` CLI responsive, see the `adding-a-cli-command` skill).
+See the `linting-and-ci` skill for details.
+
+### Error handling
+
+Use `aiida.common.exceptions` for AiiDA-specific exceptions, `aiida.common.warnings` for non-fatal issues.
+Assign exception messages to a variable before raising: `msg = f'...'; raise TypeError(msg)`
+
+### Best practices (not enforced)
+
+- Prefer pure functions without side effects where possible
+- Prefer explicit keyword arguments over positional, especially for same-type parameters. Minimize `*args`/`**kwargs`.
+- Prefer `dataclass` or `TypedDict` over plain dicts for structured data
+- Use `Enum` or `Literal` over bare strings to constrain inputs
+- Avoid mutable default arguments — use `None` and assign inside the body
+- Use context managers for resource cleanup (files, connections, transactions)
+- Favor composition over inheritance. Use `Protocol` for structural subtyping where possible.
+- Follow SOLID principles, Postel's law (accept broad inputs, return narrow types), the principle of least surprise, and separation of concerns
+
+## Claude Code skills
+
+The following Claude Code skills (under `.claude/skills/`) provide task-specific guidance. Listed here as a reference for all agents:
+
+- `adding-a-cli-command`: `verdi` subcommands and import-time constraints
+- `adding-dependencies`: third-party dependency checklist
+- `architecture-overview`: codebase structure, key files, ABCs
+- `commit-conventions`: branching, commit style, PR requirements
+- `debugging-processes`: diagnosing failed or stuck processes and the daemon
+- `deprecating-api`: deprecation warnings and removal timeline
+- `linting-and-ci`: pre-commit, CI checks
+- `running-tests`: pytest cheatsheet, plugins, fixtures
+- `writing-and-building-docs`: documentation style and building
+- `writing-tests`: test philosophy, markers, parametrization
+
+## AI assistant guidelines
+
+When working on this codebase:
+
+- **Read before writing**: Always read existing code and understand patterns before proposing changes.
+  Don't guess how AiiDA works.
+- **Match existing style**: Follow patterns you see in surrounding code.
+- **Don't modify code you weren't asked to change**: If fixing a bug in function A, don't also "improve" functions B and C nearby.
+- **Don't add docstrings/type hints to unchanged code**: Only add to code you're actively modifying.
+
+## Key dependencies
+
+Key dependencies (all under [github.com/aiidateam](https://github.com/aiidateam)): `plumpy` (process state machine), `kiwipy` (message broker interface), `disk-objectstore` (file storage).
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
