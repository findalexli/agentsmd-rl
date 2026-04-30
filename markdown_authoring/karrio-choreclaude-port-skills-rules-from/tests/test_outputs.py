"""Behavioral checks for karrio-choreclaude-port-skills-rules-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/karrio")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- **Always use `import karrio.lib as lib`** — NEVER the legacy `DP`, `SF`, `NF`, `DF`, `XP` utilities, and NEVER create new utility functions that duplicate `lib.*`.' in text, "expected to find: " + '- **Always use `import karrio.lib as lib`** — NEVER the legacy `DP`, `SF`, `NF`, `DF`, `XP` utilities, and NEVER create new utility functions that duplicate `lib.*`.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- Tenant-scoped models inherit from `OwnedEntity` and are filtered via `Model.access_by(request)` (or `Model.objects.filter(org=request.user.org)` at the ORM level).' in text, "expected to find: " + '- Tenant-scoped models inherit from `OwnedEntity` and are filtered via `Model.access_by(request)` (or `Model.objects.filter(org=request.user.org)` at the ORM level).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/code-style.md')
    assert '- Raw SQL in migrations — use Django migration operations (`AddField`, `RemoveField`, `RenameField`, `AlterField`, `RunPython`) only.' in text, "expected to find: " + '- Raw SQL in migrations — use Django migration operations (`AddField`, `RemoveField`, `RenameField`, `AlterField`, `RunPython`) only.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/commit-conventions.md')
    assert '**Scopes**: carrier name (e.g. `ups`, `fedex`, `dhl_express`, `smartkargo`, `canadapost`), or module (`admin`, `graph`, `manager`, `core`, `cli`, `sdk`, `dashboard`, `mcp`, `tracing`, `documents`, `da' in text, "expected to find: " + '**Scopes**: carrier name (e.g. `ups`, `fedex`, `dhl_express`, `smartkargo`, `canadapost`), or module (`admin`, `graph`, `manager`, `core`, `cli`, `sdk`, `dashboard`, `mcp`, `tracing`, `documents`, `da'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/commit-conventions.md')
    assert '- Version bump process: `./bin/update-version` → `./bin/update-package-versions` → `./bin/update-version-freeze` → `./bin/update-source-version-freeze`, or use `./bin/release [version]` for the full w' in text, "expected to find: " + '- Version bump process: `./bin/update-version` → `./bin/update-package-versions` → `./bin/update-version-freeze` → `./bin/update-source-version-freeze`, or use `./bin/release [version]` for the full w'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/commit-conventions.md')
    assert 'When pulling changes from or pushing to `jtlshipping/shipping-platform` per `PRDs/SUBTREE_SYNC_WORKFLOW.md`:' in text, "expected to find: " + 'When pulling changes from or pushing to `jtlshipping/shipping-platform` per `PRDs/SUBTREE_SYNC_WORKFLOW.md`:'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extension-patterns.md')
    assert 'Karrio is modular by design: `modules/core`, `modules/graph`, `modules/admin` form the server core; `modules/connectors/*` are plugins; everything else (`modules/orders`, `modules/data`, `modules/docu' in text, "expected to find: " + 'Karrio is modular by design: `modules/core`, `modules/graph`, `modules/admin` form the server core; `modules/connectors/*` are plugins; everything else (`modules/orders`, `modules/data`, `modules/docu'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extension-patterns.md')
    assert 'Karrio uses **implicit namespace packages** (`pkgutil.extend_path`) so that multiple installed packages can contribute to the same Python namespace (e.g., `karrio.server.graph.schemas`). The core pack' in text, "expected to find: " + 'Karrio uses **implicit namespace packages** (`pkgutil.extend_path`) so that multiple installed packages can contribute to the same Python namespace (e.g., `karrio.server.graph.schemas`). The core pack'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/extension-patterns.md')
    assert '**Rule of thumb:** if a directory path already exists in another installed module (e.g., `modules/graph/karrio/server/graph/`), do NOT create an `__init__.py` at that same path in your extension modul' in text, "expected to find: " + '**Rule of thumb:** if a directory path already exists in another installed module (e.g., `modules/graph/karrio/server/graph/`), do NOT create an `__init__.py` at that same path in your extension modul'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert 'Tests should use **real DB objects, real signal dispatch, and real handler execution**. Only mock calls to **external services** — carrier API requests, third-party HTTP calls, Redis/queue tasks.' in text, "expected to find: " + 'Tests should use **real DB objects, real signal dispatch, and real handler execution**. Only mock calls to **external services** — carrier API requests, third-party HTTP calls, Redis/queue tasks.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '- Keep carrier-functional fields (country codes, zip codes, cities, addresses, weights) as fixed valid values — carrier APIs validate these combinations.' in text, "expected to find: " + '- Keep carrier-functional fields (country codes, zip codes, cities, addresses, weights) as fixed valid values — carrier APIs validate these combinations.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing.md')
    assert '- Use `@ngneat/falso` for generating fake test data (names, companies, emails, phones) in frontend E2E tests — never hardcode personal data.' in text, "expected to find: " + '- Use `@ngneat/falso` for generating fake test data (names, companies, emails, phones) in frontend E2E tests — never hardcode personal data.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-extension-module/SKILL.md')
    assert '**Namespace-package rule (critical):** the only `__init__.py` files you create are inside the **leaf** directories unique to your module — i.e. `karrio/server/<name>/__init__.py`, `karrio/server/<name' in text, "expected to find: " + '**Namespace-package rule (critical):** the only `__init__.py` files you create are inside the **leaf** directories unique to your module — i.e. `karrio/server/<name>/__init__.py`, `karrio/server/<name'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-extension-module/SKILL.md')
    assert 'Scaffold a new karrio extension module that hooks into core without modifying core code. Karrio is modular by design — `modules/core`, `modules/graph`, `modules/admin` form the server core, `modules/c' in text, "expected to find: " + 'Scaffold a new karrio extension module that hooks into core without modifying core code. Karrio is modular by design — `modules/core`, `modules/graph`, `modules/admin` form the server core, `modules/c'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/create-extension-module/SKILL.md')
    assert 'If your extension is a completely new module not already listed in `apps/api/karrio/server/settings/__init__.py`, add a matching `find_spec` guard there as a separate PR (this edits core and needs rev' in text, "expected to find: " + 'If your extension is a completely new module not already listed in `apps/api/karrio/server/settings/__init__.py`, add a matching `find_spec` guard there as a separate PR (this edits core and needs rev'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-graphql/SKILL.md')
    assert 'Auto-discovery: `modules/graph/karrio/server/graph/schema.py` iterates `schemas/` via `pkgutil.iter_modules()` and collects `Query`, `Mutation`, and `extra_types` from every sub-package. No manual reg' in text, "expected to find: " + 'Auto-discovery: `modules/graph/karrio/server/graph/schema.py` iterates `schemas/` via `pkgutil.iter_modules()` and collects `Query`, `Mutation`, and `extra_types` from every sub-package. No manual reg'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-graphql/SKILL.md')
    assert '2. **Do not** create `__init__.py` anywhere above the leaf `<name>/` directory — shared paths (`karrio/server/graph/`, `karrio/server/graph/schemas/`) must remain implicit namespace packages, otherwis' in text, "expected to find: " + '2. **Do not** create `__init__.py` anywhere above the leaf `<name>/` directory — shared paths (`karrio/server/graph/`, `karrio/server/graph/schemas/`) must remain implicit namespace packages, otherwis'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-graphql/SKILL.md')
    assert 'Every schema module (base, admin, or extension) follows the same thin-interface layout. See `.claude/rules/extension-patterns.md` for the dependency rules between these files — circular imports cause ' in text, "expected to find: " + 'Every schema module (base, admin, or extension) follows the same thin-interface layout. See `.claude/rules/extension-patterns.md` for the dependency rules between these files — circular imports cause '[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-rest-api/SKILL.md')
    assert '- **Tenant scoping**: `GenericAPIView.get_queryset()` calls `self.model.access_by(request)` when `model` is set (see `modules/core/karrio/server/core/views/api.py:99`). For `APIView` detail endpoints,' in text, "expected to find: " + '- **Tenant scoping**: `GenericAPIView.get_queryset()` calls `self.model.access_by(request)` when `model` is set (see `modules/core/karrio/server/core/views/api.py:99`). For `APIView` detail endpoints,'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-rest-api/SKILL.md')
    assert '- **`ENDPOINT_ID`**: set a 5-character prefix (e.g. `"$$$$$"`, `"&&&&&"`, `"@@@@@"`) at the top of each view module. It is concatenated with `list` / `create` / `retrieve` / `update` / `discard` etc. ' in text, "expected to find: " + '- **`ENDPOINT_ID`**: set a 5-character prefix (e.g. `"$$$$$"`, `"&&&&&"`, `"@@@@@"`) at the top of each view module. It is concatenated with `list` / `create` / `retrieve` / `update` / `discard` etc. '[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/django-rest-api/SKILL.md')
    assert "- **Base classes**: always `karrio.server.core.views.api.GenericAPIView` / `APIView`, never raw DRF `generics.GenericAPIView` / `views.APIView`. Karrio's base classes inject `LoggingMixin`, token / JW" in text, "expected to find: " + "- **Base classes**: always `karrio.server.core.views.api.GenericAPIView` / `APIView`, never raw DRF `generics.GenericAPIView` / `views.APIView`. Karrio's base classes inject `LoggingMixin`, token / JW"[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-implementation/SKILL.md')
    assert '**CRITICAL**: N+1 queries are the #1 performance killer. Check every changed model, serializer, and view. Full patterns in `.claude/rules/django-patterns.md`.' in text, "expected to find: " + '**CRITICAL**: N+1 queries are the #1 performance killer. Check every changed model, serializer, and view. Full patterns in `.claude/rules/django-patterns.md`.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-implementation/SKILL.md')
    assert '- [ ] No manually edited auto-generated files (`mapper.py`, `karrio/schemas/<carrier>/*`, `packages/karriojs/api/generated/*`)' in text, "expected to find: " + '- [ ] No manually edited auto-generated files (`mapper.py`, `karrio/schemas/<carrier>/*`, `packages/karriojs/api/generated/*`)'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/review-implementation/SKILL.md')
    assert '- [ ] New domain logic lives in `modules/<name>/`, not sprinkled across `modules/core` / `modules/graph` / `modules/manager`' in text, "expected to find: " + '- [ ] New domain logic lives in `modules/<name>/`, not sprinkled across `modules/core` / `modules/graph` / `modules/manager`'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/run-tests/SKILL.md')
    assert '| `modules/<new-extension>/` | `karrio test --failfast karrio.server.<name>.tests` (after registering in `bin/run-server-tests`) |' in text, "expected to find: " + '| `modules/<new-extension>/` | `karrio test --failfast karrio.server.<name>.tests` (after registering in `bin/run-server-tests`) |'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/run-tests/SKILL.md')
    assert '- `HUEY["immediate"] = True` in test settings — Huey tasks run synchronously. Don\'t mock them unless you\'re testing failure paths.' in text, "expected to find: " + '- `HUEY["immediate"] = True` in test settings — Huey tasks run synchronously. Don\'t mock them unless you\'re testing failure paths.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/run-tests/SKILL.md')
    assert '| `modules/connectors/<carrier>/` | `python -m unittest discover -v -f modules/connectors/<carrier>/tests` |' in text, "expected to find: " + '| `modules/connectors/<carrier>/` | `python -m unittest discover -v -f modules/connectors/<carrier>/tests` |'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '4. **PRDs in `PRDs/`** — feature architecture decisions and active workstreams (e.g. `RELEASE_2026_5_PLATFORM_UPGRADE.md`, `SUBTREE_SYNC_WORKFLOW.md`).' in text, "expected to find: " + '4. **PRDs in `PRDs/`** — feature architecture decisions and active workstreams (e.g. `RELEASE_2026_5_PLATFORM_UPGRADE.md`, `SUBTREE_SYNC_WORKFLOW.md`).'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '1. **`CLAUDE.md`** (lean, project-specific) and this `AGENTS.md` (comprehensive reference) — the two sources of truth for project conventions.' in text, "expected to find: " + '1. **`CLAUDE.md`** (lean, project-specific) and this `AGENTS.md` (comprehensive reference) — the two sources of truth for project conventions.'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '5. **Carrier integrations** — consult `CARRIER_INTEGRATION_GUIDE.md` and the existing carriers under `modules/connectors/*/`.' in text, "expected to find: " + '5. **Carrier integrations** — consult `CARRIER_INTEGRATION_GUIDE.md` and the existing carriers under `modules/connectors/*/`.'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `create-extension-module/` — Scaffold a new `modules/<name>/` extension with AppConfig + auto-discovery' in text, "expected to find: " + '- `create-extension-module/` — Scaffold a new `modules/<name>/` extension with AppConfig + auto-discovery'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `extension-patterns.md` — "extend, don\'t modify core" + namespace-package rules' in text, "expected to find: " + '- `extension-patterns.md` — "extend, don\'t modify core" + namespace-package rules'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '- `create-prd/` — Write PRDs with ASCII diagrams before non-trivial features' in text, "expected to find: " + '- `create-prd/` — Write PRDs with ASCII diagrams before non-trivial features'[:80]

