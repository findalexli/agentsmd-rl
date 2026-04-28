#!/usr/bin/env bash
set -euo pipefail

cd /workspace/karrio

# Idempotency guard
if grep -qF "- **Always use `import karrio.lib as lib`** \u2014 NEVER the legacy `DP`, `SF`, `NF`," ".claude/rules/code-style.md" && grep -qF "**Scopes**: carrier name (e.g. `ups`, `fedex`, `dhl_express`, `smartkargo`, `can" ".claude/rules/commit-conventions.md" && grep -qF "Karrio is modular by design: `modules/core`, `modules/graph`, `modules/admin` fo" ".claude/rules/extension-patterns.md" && grep -qF "Tests should use **real DB objects, real signal dispatch, and real handler execu" ".claude/rules/testing.md" && grep -qF "**Namespace-package rule (critical):** the only `__init__.py` files you create a" ".claude/skills/create-extension-module/SKILL.md" && grep -qF "Auto-discovery: `modules/graph/karrio/server/graph/schema.py` iterates `schemas/" ".claude/skills/django-graphql/SKILL.md" && grep -qF "- **Tenant scoping**: `GenericAPIView.get_queryset()` calls `self.model.access_b" ".claude/skills/django-rest-api/SKILL.md" && grep -qF "**CRITICAL**: N+1 queries are the #1 performance killer. Check every changed mod" ".claude/skills/review-implementation/SKILL.md" && grep -qF "| `modules/<new-extension>/` | `karrio test --failfast karrio.server.<name>.test" ".claude/skills/run-tests/SKILL.md" && grep -qF "4. **PRDs in `PRDs/`** \u2014 feature architecture decisions and active workstreams (" "AGENTS.md" && grep -qF "- `create-extension-module/` \u2014 Scaffold a new `modules/<name>/` extension with A" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/code-style.md b/.claude/rules/code-style.md
@@ -1,31 +1,63 @@
 # Code Style & Naming Conventions
 
-## General
-- Write code as if the same person authored the entire codebase
-- Favor functional, declarative style: use `map`, `reduce`, `filter`, list comprehensions
-- Concise but readable: no unnecessary verbosity, no cryptic one-liners
-- Never reinvent the wheel — always search for existing utilities first
+## General Principles
+
+- Write code as if the same person authored the entire codebase — consistency is paramount.
+- Favor functional, declarative style: list comprehensions, `map` / `filter` / `reduce`.
+- `list(dict.fromkeys(items))` for order-preserving deduplication.
+- Concise but readable — no unnecessary verbosity, no cryptic one-liners.
+- Never reinvent the wheel — always search for existing utilities before writing new code.
 
 ## Python
-- PEP 8 with 4-space indentation
-- Format: `black`, type check: `mypy`
-- snake_case for modules/functions, PascalCase for classes
-- Always use `import karrio.lib as lib` — never the legacy `DP`, `SF`, `NF`, `DF`, `XP` utilities
-- Import order: stdlib → third-party → karrio core → local/relative
-
-## TypeScript/React
-- 2-space indentation, format with Prettier
-- PascalCase for components, camelCase for functions/variables
-- Functional components only (no class components)
-- Import order: React/Next → third-party → @karrio packages → local
-- Always import types from `@karrio/types` (never define inline)
-- Use existing hooks from `@karrio/hooks/*` (never raw fetch/axios)
-- Use existing UI components from `@karrio/ui` (never duplicate patterns)
-
-## Anti-Patterns
-- Never use `pytest` — we use `unittest` and Django tests
-- Never use raw SQL in Django migrations — use Django operations only
-- Never catch bare `Exception` — be specific
-- Never use mutable default arguments
-- Never add features not explicitly requested
-- Never use `any` type in TypeScript
+
+- PEP 8, 4-space indentation, format with `ruff format` (previously `black`), type-check with `mypy`.
+- `snake_case` for modules/functions, `PascalCase` for classes.
+- Import order: stdlib → third-party → karrio core → local/relative.
+- **Always use `import karrio.lib as lib`** — NEVER the legacy `DP`, `SF`, `NF`, `DF`, `XP` utilities, and NEVER create new utility functions that duplicate `lib.*`.
+- Use specific exceptions; never bare `except:` or `except Exception:`.
+- No mutable default arguments — use `functools.partial` or sentinel pattern.
+
+### Localization (i18n)
+
+- **All user-facing strings** must use `django.utils.translation.gettext` (or `gettext_lazy`) — never hardcode messages.
+- This includes: error messages, validation messages, notification text, and any string returned in API responses that users see.
+- Import as `from django.utils.translation import gettext as _` and wrap strings: `_("Shipment created successfully")`.
+- Internal log messages and developer-facing strings (e.g., exception names, debug logs) do NOT need `gettext`.
+
+## TypeScript / React
+
+- 2-space indentation, format with Prettier.
+- `PascalCase` for components, `camelCase` for functions/variables.
+- Functional components only — no class components; use hooks.
+- Import order: React/Next → third-party → `@karrio/*` packages → local.
+- Always import types from `@karrio/types` — never define inline.
+- Use existing hooks from `@karrio/hooks/*` — never raw fetch/axios.
+- Use existing UI components from `@karrio/ui` — never duplicate patterns.
+- Never use `any` — use proper types, or `unknown` with type guards.
+- Use regenerate scripts (`./bin/run-generate-on`, Next codegen) for type generation — never manually edit generated files.
+
+## Django Models
+
+- Tenant-scoped models inherit from `OwnedEntity` and are filtered via `Model.access_by(request)` (or `Model.objects.filter(org=request.user.org)` at the ORM level).
+- System models: plain `models.Model` (no tenant scoping).
+- Register with `@core.register_model` decorator when applicable.
+- Use `functools.partial(core.uuid, prefix="xxx_")` for ID generation.
+- JSONField defaults: `functools.partial(karrio.server.core.models._identity, value=[])` (never bare `[]`).
+
+## Serializers
+
+- Use mixin classes for shared logic between Account and System serializers.
+- `@owned_model_serializer` for tenant-scoped serializers (handles `created_by` + `link_org()`).
+- Plain serializers for system-scoped models (manual `created_by` in `create()`).
+- Always use `Serializer.map()` pattern for validation + save.
+
+## Anti-Patterns (NEVER DO)
+
+- `pytest` — always `unittest` for SDK, `karrio test` for Django server.
+- Raw SQL in migrations — use Django migration operations (`AddField`, `RemoveField`, `RenameField`, `AlterField`, `RunPython`) only.
+- `RunSQL` — must work across SQLite, PostgreSQL, MySQL.
+- New utility functions duplicating `karrio.lib` — check `lib.*` reference first.
+- Bare exceptions, mutable defaults, `any` types.
+- Class components in React — use function components + hooks.
+- Manual CSS files — use Tailwind classes.
+- Features not explicitly requested.
diff --git a/.claude/rules/commit-conventions.md b/.claude/rules/commit-conventions.md
@@ -0,0 +1,65 @@
+# Commit & PR Conventions
+
+## Commit Messages
+
+Format: `type(scope): summary` or `type: summary`
+
+**Types**: `feat`, `fix`, `chore`, `refactor`, `test`, `docs`, `release`
+
+**Scopes**: carrier name (e.g. `ups`, `fedex`, `dhl_express`, `smartkargo`, `canadapost`), or module (`admin`, `graph`, `manager`, `core`, `cli`, `sdk`, `dashboard`, `mcp`, `tracing`, `documents`, `data`, `events`, `orders`, `proxy`, `pricing`, `connectors`).
+
+Examples:
+
+```
+feat(smartkargo): add rate + shipment support
+fix(dhl_parcel_de): make package dimensions optional in shipment request
+chore: update requirements
+refactor(graph): auto-discover schemas via pkgutil.iter_modules
+test(admin): add system rate sheet CRUD tests
+docs(subtree): document SUBTREE_SYNC_WORKFLOW
+release: 2026.5.0
+```
+
+## Rules
+
+- **CRITICAL**: NEVER add `Co-Authored-By: <AI model>` or any AI attribution lines.
+- **CRITICAL**: NEVER add "Generated with Claude Code" or similar AI footers to commits or PR bodies.
+- **CRITICAL**: NEVER commit without explicit user permission.
+- Max 72-character subject line, imperative mood ("add", not "added").
+- Reference issues: `refs #123` or `fixes #123`.
+- Keep commits focused — one logical change per commit.
+- Run tests before pushing: `./bin/run-sdk-tests` and/or `./bin/run-server-tests`.
+
+## Pull Requests
+
+- Title under 70 characters, same format as commits.
+- Body follows [`git-workflow.md`](./git-workflow.md) — Feature / Fix / Release templates.
+- No AI-generated boilerplate footers.
+- Group related changes by `### Feat`, `### Fix`, `### Docs`, `### Chore` sections in release PRs.
+- Use tables for file-level change summaries and audit matrices.
+- Include test/build evidence in the Verification section.
+
+## Branch Naming
+
+Format: `type/description` — examples:
+
+- `feat/2026.5-huey-http`
+- `fix/dhl-parcel-de-dimensions-optional`
+- `hotfix/2026.1.29-idempotent-archiving-migrations`
+- `chore/2026.5-ruff-precommit`
+- `sync/shipping-platform-2026-04-19` (upstream subtree sync; see `PRDs/SUBTREE_SYNC_WORKFLOW.md`)
+
+## Release Commits
+
+- Format: `release: YYYY.M.PATCH` (calendar versioning).
+- Central version file: `apps/api/karrio/server/VERSION`.
+- Version bump process: `./bin/update-version` → `./bin/update-package-versions` → `./bin/update-version-freeze` → `./bin/update-source-version-freeze`, or use `./bin/release [version]` for the full workflow.
+
+## Subtree Sync Commits
+
+When pulling changes from or pushing to `jtlshipping/shipping-platform` per `PRDs/SUBTREE_SYNC_WORKFLOW.md`:
+
+- Prefix with `fix: sync shipping-platform patches (<brief description>)`.
+- Branch name: `sync/shipping-platform-YYYY-MM-DD`.
+- Isolate sync to a single commit; no mixing with semantic changes.
+- Document conflict-resolution decisions in the PR body (the SUBTREE_SYNC_WORKFLOW matrix is the authority).
diff --git a/.claude/rules/extension-patterns.md b/.claude/rules/extension-patterns.md
@@ -0,0 +1,236 @@
+# Extension Patterns — "Extend, Don't Modify Core"
+
+## The Golden Rule
+
+Karrio is modular by design: `modules/core`, `modules/graph`, `modules/admin` form the server core; `modules/connectors/*` are plugins; everything else (`modules/orders`, `modules/data`, `modules/documents`, `modules/events`, `modules/pricing`, `modules/manager`, ...) is an auto-discovered extension module.
+
+**Prefer adding a new extension module over modifying an existing one.** Modify a core module only when the feature is genuinely generic and benefits all karrio deployments.
+
+## Decision Tree
+
+```
+Is this feature specific to one domain (orders, documents, pricing, …)?
+  YES -> Extend or create the relevant modules/<name>/ package
+  NO  -> Is it a bug fix in an existing module?
+    YES -> Fix in that module, isolate to a clean commit
+    NO  -> Is it a new generic capability the server always needs?
+      YES -> Add to modules/core or modules/graph
+      NO  -> Create a new extension module in modules/<name>/
+```
+
+## The Extension Module Pattern
+
+### Architecture
+
+```
+                    ┌────────────────────────────────────────┐
+                    │               karrio/                  │
+                    │                                        │
+                    │  modules/                              │
+                    │  ├── core/      (OSS core)             │
+                    │  ├── graph/     (OSS graph)            │
+                    │  ├── admin/     (OSS admin)            │
+                    │  ├── manager/                          │
+                    │  ├── orders/                           │
+                    │  ├── data/                             │
+                    │  ├── documents/                        │
+                    │  ├── events/                           │
+                    │  ├── pricing/                          │
+                    │  ├── connectors/*/  (carrier plugins)  │
+                    │  └── <your-module>/                    │
+                    │         │                              │
+                    │         │ hooks via                     │
+                    │         │ AppConfig.ready()             │
+                    │         ▼                              │
+                    │  ┌────────────────────┐                │
+                    │  │  core hook points  │                │
+                    │  │  @pre_processing    │                │
+                    │  │  pkgutil discover  │                │
+                    │  │  INSTALLED_APPS    │                │
+                    │  └────────────────────┘                │
+                    └────────────────────────────────────────┘
+```
+
+### Canonical Examples
+
+Study these before creating new extensions:
+
+- `modules/orders/karrio/server/orders/` — domain module with REST + GraphQL + signals
+- `modules/events/karrio/server/events/` — webhook/event delivery module with Huey task registration
+- `modules/documents/karrio/server/documents/` — module that registers its own auto-discovered URLs
+- `modules/graph/karrio/server/graph/schemas/base/` — reference GraphQL module layout (base schemas for the whole server)
+
+### Module File Organization
+
+Keep `__init__.py` as a **thin interface definition** — just `Query` field declarations and `Mutation` one-liner delegations. All resolver logic belongs in `types.py` and `mutations.py`.
+
+**Canonical reference:** `modules/graph/karrio/server/graph/schemas/base/__init__.py`
+
+- **`__init__.py`** — Interface only. `Query` uses `strawberry.field(resolver=types.XType.resolve)`. `Mutation` methods are one-liners that delegate to `mutations.XMutation.mutate()`. No business logic, no imports of domain modules.
+- **`types.py`** — Strawberry types with `resolve` / `resolve_list` static methods containing query logic.
+- **`inputs.py`** — Strawberry input types and filters.
+- **`mutations.py`** — Mutation classes with `mutate()` static methods containing mutation logic.
+- **`datatypes.py`** — `@attr.s(auto_attribs=True)` dataclasses for structured data flowing through the module. Prefer typed attributes over raw dicts.
+- **`utils.py`** — Reusable helper functions (payload builders, transformers, formatters, availability decorators). **Must not import from `types.py` or `mutations.py`** — see dependency rule below.
+
+```
+modules/<name>/karrio/server/graph/schemas/<name>/
+├── __init__.py      # Thin interface: Query fields + Mutation delegators
+├── types.py         # Strawberry types + resolve/resolve_list methods
+├── inputs.py        # Strawberry input types and filters
+├── mutations.py     # Mutation classes + mutate() methods
+├── datatypes.py     # @attr.s dataclasses for typed data
+└── utils.py         # Business logic, payload builders, decorators
+```
+
+### Dependency Direction (one-way only)
+
+Imports between schema files must flow in one direction. Circular imports between these files cause silent schema registration failures (`schema.py` catches the error and skips the module).
+
+```
+__init__.py ──→ types.py ──→ utils.py
+            ──→ mutations.py ──→ utils.py
+            ──→ inputs.py
+```
+
+- **`utils.py`** must never import `types.py` or `mutations.py`.
+- **`types.py`** must never import `mutations.py` (or vice versa).
+- Factory methods that construct a GraphQL type belong as **static methods on the type itself** (e.g., `ShipmentType.parse(...)`), not in `utils.py`.
+
+```python
+# ✅ Good — type knows how to construct itself
+@strawberry.type
+class ItemType:
+    id: int
+    name: str
+
+    @staticmethod
+    def parse(raw: dict) -> "ItemType":
+        return ItemType(id=raw["id"], name=raw.get("name", ""))
+
+# ❌ Bad — utils.py imports types.py, creating circular dependency
+# utils.py
+import karrio.server.graph.schemas.items.types as types
+def enrich_item(raw: dict) -> types.ItemType:  # circular!
+    return types.ItemType(...)
+```
+
+```python
+# ✅ Good __init__.py — thin interface
+@strawberry.type
+class Query:
+    items: typing.List[types.ItemType] = strawberry.field(
+        resolver=types.ItemType.resolve_list
+    )
+    item: typing.Optional[types.ItemType] = strawberry.field(
+        resolver=types.ItemType.resolve
+    )
+
+@strawberry.type
+class Mutation:
+    @strawberry.mutation
+    def create_item(self, info: Info, input: inputs.CreateItemInput) -> mutations.CreateItemMutation:
+        return mutations.CreateItemMutation.mutate(info, **input.__dict__)
+
+# ❌ Bad __init__.py — inline resolver logic
+@strawberry.type
+class Query:
+    @strawberry.field
+    @staticmethod
+    def items(info: Info) -> typing.List[types.ItemType]:
+        # 50 lines of business logic...
+```
+
+### Hook Registration Pattern
+
+```python
+# apps.py
+from django.apps import AppConfig
+
+class OrdersConfig(AppConfig):
+    name = "karrio.server.orders"
+
+    def ready(self):
+        from karrio.server.orders import signals  # noqa: registers signal handlers
+        # Append validation hooks to a core serializer's pre_process_functions:
+        # from karrio.server.manager.serializers import ShipmentSerializer
+        # ShipmentSerializer.pre_process_functions.append(validators.validate_order_link)
+```
+
+### Settings Auto-Discovery
+
+```python
+# modules/<name>/karrio/server/settings/<name>.py
+from karrio.server.settings.base import *  # noqa
+
+INSTALLED_APPS += ["karrio.server.<name>"]
+KARRIO_URLS += ["karrio.server.<name>.urls"]  # if module has REST endpoints
+```
+
+Karrio discovers settings modules via `importlib.util.find_spec()` at startup. Your settings file runs only if the module is installed via `-e ./modules/<name>` in `requirements.build.txt`.
+
+### GraphQL Extension (Auto-Discovery)
+
+```python
+# modules/<name>/karrio/server/graph/schemas/<name>/__init__.py
+import strawberry
+import typing
+from strawberry.types import Info
+
+@strawberry.type
+class Query:
+    # Fields auto-merged into root Query via pkgutil.iter_modules()
+    ...
+
+@strawberry.type
+class Mutation:
+    # Fields auto-merged into root Mutation
+    ...
+
+extra_types: typing.List = []  # required even if empty
+```
+
+### Namespace Packages — NEVER Add `__init__.py` to Shared Paths
+
+Karrio uses **implicit namespace packages** (`pkgutil.extend_path`) so that multiple installed packages can contribute to the same Python namespace (e.g., `karrio.server.graph.schemas`). The core packages (`modules/graph/`, `modules/admin/`, etc.) already define the namespace roots.
+
+**NEVER add `__init__.py` files to namespace paths that are owned by another package.** Doing so converts the implicit namespace package into a regular package, which shadows the core package and breaks `pkgutil.iter_modules()` discovery.
+
+```
+# ❌ WRONG — adding __init__.py to a namespace owned by core graph
+modules/<yourmod>/karrio/server/graph/__init__.py            # breaks karrio.server.graph
+modules/<yourmod>/karrio/server/graph/schemas/__init__.py    # breaks schema discovery
+
+# ✅ CORRECT — only add __init__.py inside your module's own leaf directory
+modules/<yourmod>/karrio/server/graph/schemas/<yourmod>/__init__.py  # leaf: your schema module
+modules/<yourmod>/karrio/server/<yourmod>/__init__.py                # leaf: your module root
+```
+
+**Rule of thumb:** if a directory path already exists in another installed module (e.g., `modules/graph/karrio/server/graph/`), do NOT create an `__init__.py` at that same path in your extension module. Only the **leaf directory** unique to your module gets `__init__.py`.
+
+### Core Hook Points
+
+| Hook | Location | Purpose |
+|------|----------|---------|
+| `@pre_processing` | `karrio.server.core.utils` | Append validators to serializer pipelines |
+| `AppConfig.ready()` | Django app startup | Register hooks, signal handlers |
+| `pkgutil.iter_modules()` | `graph/schema.py`, `admin/schema.py` | Auto-discover GraphQL schemas |
+| `importlib.util.find_spec()` | `settings/base.py` | Auto-discover settings modules |
+| `KARRIO_URLS` | `settings/base.py` | Register REST URL patterns |
+| `huey` task registry | `karrio.server.events.task_definitions` | Auto-discovered background tasks |
+
+## Creating a New Extension Module
+
+1. Create directory: `modules/<name>/karrio/server/<name>/`.
+2. Add `apps.py` with `AppConfig` and optional `ready()` hook.
+3. Add `karrio/server/settings/<name>.py` for auto-discovery.
+4. Add GraphQL schemas under `karrio/server/graph/schemas/<name>/` or `karrio/server/admin/schemas/<name>/` (admin is OSS-side; NOT `ee/insiders/modules/admin`).
+5. **Do NOT add `__init__.py` to shared namespace paths** (e.g., `karrio/server/graph/`, `karrio/server/admin/`) — only the leaf directory unique to your module gets `__init__.py` (see "Namespace Packages" above).
+6. Add tests under `modules/<name>/karrio/server/<name>/tests/`.
+7. **Add `karrio.server.<name>.tests` to `bin/run-server-tests`** — without this, tests pass locally but never run in CI.
+8. **Add `-e ./modules/<name>` to `requirements.build.txt`** — without this the module is not installed in Docker images and schema discovery silently skips it.
+9. Use the `create-extension-module` skill for scaffolding.
+
+## Connectors vs Extension Modules
+
+Carrier connectors under `modules/connectors/*/` follow a separate structure documented in [`carrier-integration.md`](./carrier-integration.md) — use `./bin/cli sdk add-extension` to scaffold. Do NOT use the extension-module pattern for carriers.
diff --git a/.claude/rules/testing.md b/.claude/rules/testing.md
@@ -1,43 +1,156 @@
 # Testing Guidelines
 
-## Commands
+## Mandatory Testing Rule
+
+Every feature, bug fix, or behavioral change MUST include tests. No PR should be merged without test coverage for the changed behavior.
+
+## Non-Negotiable Code Style Rules
+
+### Imports Always at the Top
+
+**Never import inside a function or test method.** All imports belong at the top of the file.
+
+```python
+# ✅ CORRECT — imports at file top
+import re
+from unittest.mock import patch
+from karrio.server.manager.signals import trackers_bulk_updated
+from karrio.server.manager.serializers.tracking import bulk_save_trackers
+
+class TestMyFeature(APITestCase):
+    def test_something(self):
+        ...
+
+# ❌ WRONG — imports inside test methods
+class TestMyFeature(APITestCase):
+    def test_something(self):
+        from unittest.mock import patch          # never
+        import re                                # never
+```
+
+### Avoid Mocks Except for External Services
+
+Tests should use **real DB objects, real signal dispatch, and real handler execution**. Only mock calls to **external services** — carrier API requests, third-party HTTP calls, Redis/queue tasks.
+
+```python
+# ✅ CORRECT — mock only the external task that would hit Redis/network
+with patch("karrio.server.events.task_definitions.broadcast_tracking_event") as mock_broadcast:
+    trackers_bulk_updated.send(
+        sender=models.Tracking,
+        changed_trackers=[(tracker, ["status", "updated_at"])],
+    )
+mock_broadcast.assert_called_once()
+
+# ❌ WRONG — mocking the entire signal or Django machinery
+with patch("karrio.server.manager.signals.trackers_bulk_updated") as mock_signal:
+    ...
+```
+
+## Test Commands
 
 ```bash
 source bin/activate-env
 
 # SDK + all connectors
 ./bin/run-sdk-tests
 
-# Single carrier
+# Single carrier (most common local flow)
 python -m unittest discover -v -f modules/connectors/<carrier>/tests
 
 # Server (Django)
 ./bin/run-server-tests
 
 # Single Django module
 karrio test --failfast karrio.server.<module>.tests
+
+# Frontend tests
+cd apps/dashboard && pnpm test
+
+# TypeScript type checking
+cd apps/dashboard && pnpm tsc --noEmit
 ```
 
 ## Key Rules
-- Always run tests from the repository root
-- Always match existing test coding style
-- We do NOT use pytest anywhere — `unittest` for SDK, `karrio test` (Django) for server
-- Test files: `test_<feature>.py` with classes `Test<Module><Feature>`
-
-## Carrier Integration Tests (4-method pattern)
-1. `test_create_<feature>_request` — unified model → carrier request
-2. `test_<get_feature>` — proxy URL/method verification
+
+- Always run tests from the repository root.
+- Always match existing test coding style.
+- **NEVER use pytest** — `unittest` for SDK, `karrio test` (Django) for server.
+- Test files: `test_<feature>.py` with classes `Test<Module><Feature>`.
+- **Always add `print(response.data)` before assertions** when debugging — remove once tests pass.
+- **Use `mock.ANY`** for dynamic fields (id, created_at, updated_at).
+- **Use `self.maxDiff = None`** in `setUp()` for full diff output.
+
+## SDK Carrier Integration Tests — 4-method Pattern
+
+Every carrier feature requires 4 tests:
+
+1. `test_create_<feature>_request` — unified model → carrier request payload
+2. `test_get_<feature>` — proxy URL/method verification (HTTP call inspection)
 3. `test_parse_<feature>_response` — carrier response → unified model
 4. `test_parse_error_response` — error handling
 
-## Django Test Pattern
-- Debug: add `print(response.data)` BEFORE assertions, remove when tests pass
-- Create objects via API requests, not direct model manipulation
-- Use `self.assertResponseNoErrors(response)` first
-- Single comprehensive assertion: `self.assertDictEqual` with full response
-- Use `mock.ANY` for dynamic fields (id, created_at, updated_at)
+```python
+class TestCarrierFeature(unittest.TestCase):
+    def setUp(self):
+        self.maxDiff = None
+
+    @patch("karrio.mappers.<carrier>.proxy.lib.request")
+    def test_get_rates(self, mock_request):
+        mock_request.return_value = RESPONSE_JSON
+        parsed_response, messages = (
+            karrio.Rating.fetch(self.RateRequest).from_(gateway).parse()
+        )
+        print(lib.to_dict(parsed_response))  # always print before assert
+        self.assertListEqual(lib.to_dict(parsed_response), ParsedRateResponse)
+```
+
+## Django Server Test Pattern
+
+- Debug: add `print(response.data)` BEFORE assertions, remove when tests pass.
+- Create objects via API requests, not direct model manipulation.
+- Use `self.assertResponseNoErrors(response)` first for GraphQL.
+- Single comprehensive assertion: `self.assertDictEqual` with full response.
+
+```python
+class TestFeatureName(TestCase):
+    fixtures = ["fixtures"]  # or specific fixtures
+
+    def test_query_or_mutation(self):
+        response = self.query(QUERY_STRING, operation_name="OperationName")
+        response_data = response.data
+
+        # print(response_data)  # during debug, remove when passing
+
+        self.assertResponseNoErrors(response)
+        self.assertDictEqual(response_data, EXPECTED_RESPONSE)
+```
 
 ## Fixture Pattern
-- Module-level constants: `Payload`, `RequestData`, `Response`, `ParsedResponse`, `ErrorResponse`
-- `cached_auth` dict for OAuth carriers
-- `gateway` instance in `fixture.py`
+
+- Module-level constants in `fixture.py`: `Payload`, `RequestData`, `Response`, `ParsedResponse`, `ErrorResponse`.
+- `cached_auth` dict for OAuth carriers.
+- `gateway` instance in `fixture.py`.
+- `lib.to_dict()` strips `None` and empty strings — expected fixtures shouldn't include them.
+
+## E2E Test Data
+
+- Use `@ngneat/falso` for generating fake test data (names, companies, emails, phones) in frontend E2E tests — never hardcode personal data.
+- Keep carrier-functional fields (country codes, zip codes, cities, addresses, weights) as fixed valid values — carrier APIs validate these combinations.
+
+## Migration Testing
+
+- Data migrations: verify data integrity with `RunPython` + reverse code.
+- Always test that migration is reversible when possible.
+- Test ordering: ensure dependencies are correct.
+- `HUEY["immediate"] = True` in test settings — Huey tasks run synchronously.
+
+## What to Test
+
+| Change Type | Required Tests |
+|-------------|----------------|
+| New GraphQL mutation | `karrio test` with `assertResponseNoErrors` + response validation |
+| New REST endpoint | DRF test with status code + response body |
+| Model change | Migration test + serializer test |
+| Carrier integration | 4-method pattern per feature (rate, ship, track) |
+| Bug fix | Regression test proving the fix |
+| Hook / extension | Test that hook fires and validates correctly |
diff --git a/.claude/skills/create-extension-module/SKILL.md b/.claude/skills/create-extension-module/SKILL.md
@@ -0,0 +1,287 @@
+# Skill: Create Extension Module
+
+Scaffold a new karrio extension module that hooks into core without modifying core code. Karrio is modular by design — `modules/core`, `modules/graph`, `modules/admin` form the server core, `modules/connectors/*` are carrier plugins, and everything else (`modules/orders`, `modules/data`, `modules/documents`, `modules/events`, `modules/pricing`, `modules/manager`, …) is an auto-discovered extension module following the pattern below.
+
+## When to Use
+
+- New domain logic (a new resource, workflow, or integration)
+- Extending the GraphQL schema with new types / mutations
+- Adding REST endpoints for new resources
+- Registering signal handlers, hook functions, or Huey tasks at startup
+
+**Do NOT use this pattern for carrier connectors** — they live in `modules/connectors/*` and are scaffolded via `./bin/cli sdk add-extension`. See `.claude/skills/carrier-integration/SKILL.md` and `.claude/rules/carrier-integration.md`.
+
+## Prerequisites
+
+Read these first:
+
+- `.claude/rules/extension-patterns.md` — namespace-package caveats, dependency-direction rule, hook points table
+- `.claude/skills/django-rest-api/SKILL.md` — REST view / router / serializer conventions
+- `.claude/skills/django-graphql/SKILL.md` — Strawberry GraphQL conventions
+
+Study these existing modules — they are the canonical examples, use them as templates:
+
+- `modules/orders/karrio/server/orders/` — REST + GraphQL + signals (the most complete extension module reference)
+- `modules/documents/karrio/server/documents/` — REST + Huey tasks for document generation
+- `modules/events/karrio/server/events/` — webhook delivery + Huey task registration
+- `modules/data/karrio/server/data/` — import / export module with REST views
+- `modules/pricing/karrio/server/pricing/` — admin-scoped pricing with markups and fees
+
+## Steps
+
+### 1. Create the module directory
+
+```bash
+mkdir -p modules/<name>/karrio/server/<name>
+mkdir -p modules/<name>/karrio/server/settings
+```
+
+Optional sub-packages (create only what you need):
+
+```bash
+mkdir -p modules/<name>/karrio/server/<name>/serializers
+mkdir -p modules/<name>/karrio/server/<name>/tests
+mkdir -p modules/<name>/karrio/server/<name>/migrations
+mkdir -p modules/<name>/karrio/server/graph/schemas/<name>    # only if adding GraphQL
+mkdir -p modules/<name>/karrio/server/admin/schemas/<name>    # only if adding admin GraphQL
+```
+
+**Namespace-package rule (critical):** the only `__init__.py` files you create are inside the **leaf** directories unique to your module — i.e. `karrio/server/<name>/__init__.py`, `karrio/server/<name>/tests/__init__.py`, `karrio/server/graph/schemas/<name>/__init__.py`, etc. Never create `__init__.py` at `karrio/`, `karrio/server/`, `karrio/server/graph/`, `karrio/server/graph/schemas/`, `karrio/server/admin/`, or `karrio/server/admin/schemas/` — those paths are owned by core modules and must stay as implicit namespace packages. Adding an `__init__.py` there shadows the core package and silently breaks `pkgutil.iter_modules()` discovery. See `.claude/rules/extension-patterns.md` for details.
+
+Verify by looking at `modules/orders/karrio/` — there is no `__init__.py` at `karrio/` or `karrio/server/`, only inside `karrio/server/orders/` and its sub-packages.
+
+### 2. Create the AppConfig
+
+```python
+# modules/<name>/karrio/server/<name>/apps.py
+from django.apps import AppConfig
+from django.utils.translation import gettext_lazy as _
+
+
+class <Name>Config(AppConfig):
+    name = "karrio.server.<name>"
+    verbose_name = _("<Name>")
+    default_auto_field = "django.db.models.BigAutoField"
+
+    def ready(self):
+        from karrio.server.core import utils
+        from karrio.server.<name> import signals  # only if you have signals
+
+        @utils.skip_on_commands()
+        def _init():
+            signals.register_signals()
+
+        _init()
+```
+
+Karrio conventions (see `modules/orders/karrio/server/orders/apps.py`):
+
+- Wrap registration in `@utils.skip_on_commands()` — this prevents signal / hook registration from running during `migrate`, `collectstatic`, `makemigrations`, etc. Without it you get noisy side-effects (or outright failures) when running management commands on a fresh database.
+- Wrap `verbose_name` in `gettext_lazy` so the admin UI can be translated.
+- Import signals lazily inside `ready()`, never at module top-level — Django is not fully initialized yet when `apps.py` is imported.
+
+### 3. Register signal / hook handlers
+
+```python
+# modules/<name>/karrio/server/<name>/signals.py
+import karrio.server.<name>.models as models
+from django.db.models import signals
+from karrio.server.core import utils
+from karrio.server.core.logging import logger
+
+
+def register_signals():
+    signals.post_save.connect(_on_save, sender=models.Widget)
+    signals.post_delete.connect(_on_delete, sender=models.Widget)
+    logger.info("Signal registration complete", module="karrio.<name>")
+
+
+@utils.disable_for_loaddata
+def _on_save(sender, instance, created, **kwargs):
+    ...
+
+
+@utils.disable_for_loaddata
+def _on_delete(sender, instance, **kwargs):
+    ...
+```
+
+`@utils.disable_for_loaddata` prevents signals from firing during fixture loading (test setup, `loaddata`). See the orders module's `signals.py` for a full-featured example that touches related models.
+
+To hook into a core serializer's validation pipeline, append to `pre_process_functions`:
+
+```python
+# inside register_signals() or a separate hooks.py
+from karrio.server.manager.serializers import ShipmentSerializer
+from karrio.server.<name> import validators
+
+ShipmentSerializer.pre_process_functions.append(validators.validate_widget_link)
+```
+
+### 4. Add settings auto-discovery
+
+```python
+# modules/<name>/karrio/server/settings/<name>.py
+# ruff: noqa: F403, F405, I001
+from karrio.server.settings.base import *  # noqa
+
+INSTALLED_APPS += ["karrio.server.<name>"]
+KARRIO_URLS += ["karrio.server.<name>.urls"]  # only if the module has REST endpoints
+```
+
+`apps/api/karrio/server/settings/__init__.py` iterates its known module names with `importlib.util.find_spec(...)` and imports `karrio.server.settings.<name>` when the module is installed. Your settings file must follow that exact path — `modules/<name>/karrio/server/settings/<name>.py` — for discovery to work.
+
+If your extension is a completely new module not already listed in `apps/api/karrio/server/settings/__init__.py`, add a matching `find_spec` guard there as a separate PR (this edits core and needs review). Karrio's current guards cover `graph`, `orders`, `data`, `admin`, `huey`, `servicebus`, `main` — check the file when adding a new one.
+
+### 5. Add REST endpoints (if needed)
+
+Follow `.claude/skills/django-rest-api/SKILL.md`. At minimum:
+
+- `modules/<name>/karrio/server/<name>/router.py` — `router = DefaultRouter(trailing_slash=False)`
+- `modules/<name>/karrio/server/<name>/urls.py` — `app_name = "karrio.server.<name>"`, mount `router.urls` at `v1/`
+- `modules/<name>/karrio/server/<name>/views.py` — views extending `karrio.server.core.views.api.GenericAPIView` / `APIView`, with a unique 5-char `ENDPOINT_ID`, `@openapi.extend_schema(...)` annotations, and self-registration via `router.urls.append(path(...))`
+
+### 6. Add GraphQL schemas (if needed)
+
+Follow `.claude/skills/django-graphql/SKILL.md`. Four files under a schemas sub-package:
+
+```
+modules/<name>/karrio/server/graph/schemas/<name>/        # tenant-scoped
+├── __init__.py    # Query + Mutation classes + extra_types = [] (thin interface)
+├── types.py       # @strawberry.type with resolve / resolve_list static methods
+├── inputs.py      # @strawberry.input filters + mutation inputs
+└── mutations.py   # @strawberry.type mutations with mutate() static methods
+```
+
+For admin-scoped (system) schemas use `modules/<name>/karrio/server/admin/schemas/<name>/` instead. `modules/graph/karrio/server/graph/schema.py` auto-discovers both via `pkgutil.iter_modules()` — no registration required.
+
+`extra_types: list = []` is required in every schema `__init__.py` even if empty — `schema.py` reads it unconditionally.
+
+### 7. Add `pyproject.toml`
+
+Match the orders module's structure (`modules/orders/pyproject.toml`):
+
+```toml
+[build-system]
+requires = ["setuptools>=61.0"]
+build-backend = "setuptools.build_meta"
+
+[project]
+name = "karrio_server_<name>"
+version = "2026.1.29"  # keep in sync with apps/api/karrio/server/VERSION
+description = "Multi-carrier shipping API <name> module"
+readme = "README.md"
+requires-python = ">=3.11"
+license = "LGPL-3.0"
+authors = [
+    {name = "karrio", email = "hello@karrio.io"}
+]
+classifiers = [
+    "Programming Language :: Python :: 3",
+]
+dependencies = [
+    "karrio_server_core",
+    "karrio_server_graph",     # if adding GraphQL
+    "karrio_server_manager",   # if importing from manager models
+]
+
+[project.urls]
+Homepage = "https://github.com/karrioapi/karrio"
+
+[tool.setuptools]
+zip-safe = false
+include-package-data = true
+
+[tool.setuptools.package-dir]
+"" = "."
+
+[tool.setuptools.packages.find]
+exclude = ["tests.*", "tests"]
+namespaces = true
+```
+
+`namespaces = true` is mandatory — karrio uses PEP 420 namespace packages across modules.
+
+### 8. Add tests
+
+Tests live in a `tests/` **directory** (not a single `tests.py`):
+
+```
+modules/<name>/karrio/server/<name>/tests/
+├── __init__.py         # re-exports test classes for karrio test discovery
+├── base.py             # optional: shared fixture class extending APITestCase / GraphTestCase
+├── test_<resource>.py  # REST tests
+└── test_<feature>.py   # GraphQL / signal tests
+```
+
+Use the right base class:
+
+- REST: `karrio.server.core.tests.APITestCase` (see `modules/core/karrio/server/core/tests/base.py`)
+- GraphQL: `karrio.server.graph.tests.GraphTestCase` (see `modules/graph/karrio/server/graph/tests/base.py`)
+
+Both provide `setUpTestData` with a superuser, API token, and seeded carrier connections.
+
+```python
+# modules/<name>/karrio/server/<name>/tests/test_widgets.py
+import json
+from django.urls import reverse
+from rest_framework import status
+from karrio.server.core.tests import APITestCase
+
+
+class TestWidgets(APITestCase):
+    def test_create_widget(self):
+        url = reverse("karrio.server.<name>:widget-list")
+        response = self.client.post(url, {"name": "Hello"})
+        # print(response.data)  # DEBUG — remove when passing
+        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
+```
+
+### 9. Register in build / dev / CI
+
+All three files must be updated — missing any of them means the module is silently skipped:
+
+| File | Purpose |
+| --- | --- |
+| `requirements.build.txt` | Installs the module in prod Docker images. Without this, the module never reaches staging / production. |
+| `requirements.server.dev.txt` | Installs the module in local dev environments. Without this, `./bin/run-server-tests` skips it locally. |
+| `bin/run-server-tests` | Adds `karrio.server.<name>.tests` to the Django test-runner invocation. Without this, tests pass locally but never run in CI. |
+
+Add a line like `-e ./modules/<name>` to both requirements files, and add `karrio.server.<name>.tests \` to the `$KARRIO_TEST --failfast` invocation in `bin/run-server-tests`.
+
+### 10. Install in development
+
+```bash
+source bin/activate-env
+pip install -e modules/<name>
+./bin/run-server-tests            # full server suite
+karrio test --failfast karrio.server.<name>.tests   # just your module
+```
+
+## Verification
+
+```bash
+# 1. Module imports
+python -c "import karrio.server.<name>; print('OK')"
+
+# 2. Settings auto-discovery picked it up (INSTALLED_APPS, KARRIO_URLS)
+python -c "from django.conf import settings; print('karrio.server.<name>' in settings.INSTALLED_APPS)"
+
+# 3. Django migrations generate
+karrio makemigrations <name>
+karrio migrate <name>
+
+# 4. GraphQL schema registration (if added)
+python -c "from karrio.server.graph.schema import schema; print(schema)"
+
+# 5. REST endpoints reachable (if added)
+./bin/start
+curl -H "Authorization: Token <tkn>" http://localhost:5002/api/v1/widgets
+```
+
+If `pkgutil.iter_modules()` silently skips your GraphQL schema, the usual culprits are:
+
+1. A stray `__init__.py` at `modules/<name>/karrio/server/graph/` or `.../schemas/` — delete it.
+2. A circular import between `types.py`, `mutations.py`, and `utils.py` — `schema.py` catches the `ImportError` and moves on (check `karrio.server.core.logging` output).
+3. The module isn't installed — `pip install -e modules/<name>` and confirm in `pip list`.
+4. `requirements.build.txt` missing the `-e ./modules/<name>` line — schema discovery works locally but staging / prod silently omit the module.
diff --git a/.claude/skills/django-graphql/SKILL.md b/.claude/skills/django-graphql/SKILL.md
@@ -0,0 +1,464 @@
+# Skill: Django GraphQL Development
+
+Add queries, mutations, types, and inputs to karrio's Strawberry GraphQL schema.
+
+## When to Use
+
+- Adding new GraphQL queries or mutations
+- Creating new Strawberry types for existing Django models
+- Extending the base (tenant) or admin (system) graph
+- Adding GraphQL endpoints from an extension module (e.g. `orders`, `pricing`, `documents`)
+
+## Architecture
+
+```
+┌──────────────────────────────────────────────────────────────┐
+│                    GraphQL Request                           │
+│                                                              │
+│  Client ──POST /graphql──> schema.py ──> Query/Mutation      │
+│                                                              │
+│  ┌────────────────────────────────────────────────────────┐  │
+│  │  schema.py:                                            │  │
+│  │    pkgutil.iter_modules(schemas.__path__)              │  │
+│  │    → collects Query, Mutation, extra_types per module  │  │
+│  │    → class Query(*QUERIES):  pass                      │  │
+│  │    → class Mutation(*MUTATIONS):  pass                 │  │
+│  └────────────────────────┬───────────────────────────────┘  │
+│                           │                                   │
+│       ┌───────────────────┼───────────────────┐              │
+│       ▼                   ▼                   ▼               │
+│  ┌──────────┐     ┌──────────┐     ┌──────────────────┐      │
+│  │schemas/  │     │<ext>/    │     │admin/schemas/    │      │
+│  │base/     │     │schemas/  │     │base/             │      │
+│  │  __init__│     │  <ext>/  │     │  __init__        │      │
+│  │  types   │     │          │     │  types           │      │
+│  │  inputs  │     │          │     │  inputs          │      │
+│  │  mutations│     │          │     │  mutations       │      │
+│  └────┬─────┘     └──────────┘     └──────────────────┘      │
+│       │                                                       │
+│       ▼                                                       │
+│  Model.access_by(request)  ──>  DRF Serializer  ──>  save()  │
+└──────────────────────────────────────────────────────────────┘
+```
+
+Relevant files:
+
+- `modules/graph/karrio/server/graph/schema.py` — auto-discovery via `pkgutil.iter_modules`
+- `modules/graph/karrio/server/graph/schemas/base/` — canonical tenant schema (users, shipments, trackers, carriers, rate sheets, metafields, …)
+- `modules/admin/karrio/server/admin/schemas/base/` — canonical system-admin schema
+- `modules/graph/karrio/server/graph/utils.py` — `BaseInput`, `BaseMutation`, `Paginated`, `Connection[T]`, `paginated_connection`, `is_unset`, `authentication_required`, `password_required`, `error_wrapper`
+- `modules/admin/karrio/server/admin/utils.py` — `staff_required`, `superuser_required`
+
+## Two Schema Domains
+
+| Aspect           | Base graph (tenant)                 | Admin graph (system)                |
+| ---------------- | ----------------------------------- | ----------------------------------- |
+| URL              | `/graphql`                          | `/admin/graphql`                    |
+| Scope            | Tenant (per-org)                    | System-wide (staff / superuser)     |
+| Auth decorator   | `@utils.authentication_required`    | + `@admin.staff_required` on top    |
+| Model queries    | `Model.access_by(info.context.request)` | `Model.objects.all()`            |
+| Schema location  | `modules/graph/karrio/server/graph/schemas/`       | `modules/admin/karrio/server/admin/schemas/` |
+| Extension location | `modules/<name>/karrio/server/graph/schemas/<name>/` | `modules/<name>/karrio/server/admin/schemas/<name>/` |
+
+## File Layout (4-file pattern)
+
+Every schema module (base, admin, or extension) follows the same thin-interface layout. See `.claude/rules/extension-patterns.md` for the dependency rules between these files — circular imports cause silent schema registration failures.
+
+```
+schemas/<name>/
+├── __init__.py    # Query + Mutation classes + extra_types (thin interface, REQUIRED)
+├── types.py       # @strawberry.type definitions with resolve/resolve_list
+├── inputs.py      # @strawberry.input Filter + Mutation inputs
+└── mutations.py   # @strawberry.type mutation classes with mutate()
+```
+
+## Step-by-Step: Add a New Feature
+
+### Step 1 — Define inputs (`inputs.py`)
+
+```python
+import typing
+import strawberry
+
+import karrio.server.graph.utils as utils
+
+
+# Filter input — extends Paginated (gives offset + first)
+@strawberry.input
+class WidgetFilter(utils.Paginated):
+    keyword: typing.Optional[str] = strawberry.UNSET
+    status: typing.Optional[typing.List[str]] = strawberry.UNSET
+    metadata_key: typing.Optional[str] = strawberry.UNSET
+    metadata_value: typing.Optional[utils.JSON] = strawberry.UNSET
+
+
+# Mutation input — extends BaseInput (gives to_dict() + pagination())
+@strawberry.input
+class CreateWidgetMutationInput(utils.BaseInput):
+    name: str
+    description: typing.Optional[str] = strawberry.UNSET
+    metadata: typing.Optional[utils.JSON] = strawberry.UNSET
+
+
+@strawberry.input
+class UpdateWidgetMutationInput(utils.BaseInput):
+    id: str
+    name: typing.Optional[str] = strawberry.UNSET
+    description: typing.Optional[str] = strawberry.UNSET
+    metadata: typing.Optional[utils.JSON] = strawberry.UNSET
+```
+
+Karrio conventions:
+
+- Optional fields default to `strawberry.UNSET`, never `None`.
+- Filters extend `utils.Paginated` (see `modules/graph/karrio/server/graph/utils.py`).
+- Mutation inputs extend `utils.BaseInput`; the `.to_dict()` method strips `UNSET` values.
+- Use typed enums from `karrio.server.graph.utils` (e.g. `utils.ShipmentStatusEnum`, `utils.CarrierNameEnum`) over raw strings whenever the value is enumerable.
+
+### Step 2 — Define types (`types.py`)
+
+```python
+import typing
+import strawberry
+from strawberry.types import Info
+
+import karrio.server.graph.utils as utils
+import karrio.server.core.filters as filters
+import karrio.server.graph.schemas.base.inputs as inputs
+import karrio.server.manager.models as manager  # or your extension module's models
+
+
+@strawberry.type
+class WidgetType:
+    id: str
+    name: str
+    description: typing.Optional[str] = None
+    metadata: typing.Optional[utils.JSON] = None
+    created_at: typing.Optional[str] = None
+
+    # Computed field — resolved per instance, `self` is the model
+    @strawberry.field
+    def display_name(self: manager.Widget) -> str:
+        return f"{self.name} ({self.id})"
+
+    # Single-item resolver
+    @staticmethod
+    @utils.authentication_required
+    def resolve(info: Info, id: str) -> typing.Optional["WidgetType"]:
+        return (
+            manager.Widget.access_by(info.context.request)
+            .filter(id=id)
+            .first()
+        )
+
+    # List resolver with pagination + filtering
+    @staticmethod
+    @utils.authentication_required
+    def resolve_list(
+        info: Info,
+        filter: typing.Optional[inputs.WidgetFilter] = strawberry.UNSET,
+    ) -> utils.Connection["WidgetType"]:
+        _filter = filter if not utils.is_unset(filter) else inputs.WidgetFilter()
+        queryset = filters.WidgetFilter(
+            _filter.to_dict(),
+            manager.Widget.access_by(info.context.request),
+        ).qs
+        return utils.paginated_connection(queryset, **_filter.pagination())
+```
+
+Karrio conventions:
+
+- Single-item resolver returns `Optional[Type]`; list resolver returns `utils.Connection[Type]` (karrio's paginated wrapper, not Relay's).
+- Always use `Model.access_by(info.context.request)` in the base graph — this enforces tenant isolation. Never use `Model.objects.all()` here.
+- Use `utils.is_unset(filter)` to check the sentinel — `None`/truthiness checks do not work.
+- Factory methods that construct the type from a dict/record belong on the type itself as `@staticmethod parse(...)` — never in `utils.py` (that would create a circular import; see `.claude/rules/extension-patterns.md`).
+
+### Step 3 — Define mutations (`mutations.py`)
+
+```python
+import typing
+import strawberry
+from strawberry.types import Info
+
+import karrio.server.graph.utils as utils
+import karrio.server.graph.serializers as serializers
+import karrio.server.graph.schemas.base.types as types
+import karrio.server.graph.schemas.base.inputs as inputs
+import karrio.server.manager.models as manager
+from karrio.server.serializers import process_dictionaries_mutations
+
+
+@strawberry.type
+class CreateWidgetMutation(utils.BaseMutation):
+    widget: typing.Optional[types.WidgetType] = None
+
+    @staticmethod
+    @utils.authentication_required
+    def mutate(
+        info: Info, **input: inputs.CreateWidgetMutationInput
+    ) -> "CreateWidgetMutation":
+        serializer = serializers.WidgetModelSerializer(
+            data=input,
+            context=info.context.request,
+        )
+        serializer.is_valid(raise_exception=True)
+        return CreateWidgetMutation(widget=serializer.save())  # type: ignore
+
+
+@strawberry.type
+class UpdateWidgetMutation(utils.BaseMutation):
+    widget: typing.Optional[types.WidgetType] = None
+
+    @staticmethod
+    @utils.authentication_required
+    def mutate(
+        info: Info, **input: inputs.UpdateWidgetMutationInput
+    ) -> "UpdateWidgetMutation":
+        instance = manager.Widget.access_by(info.context.request).get(id=input["id"])
+        serializer = serializers.WidgetModelSerializer(
+            instance,
+            partial=True,
+            data=process_dictionaries_mutations(["metadata"], input, instance),
+            context=info.context.request,
+        )
+        serializer.is_valid(raise_exception=True)
+        return UpdateWidgetMutation(widget=serializer.save())  # type: ignore
+```
+
+Karrio conventions:
+
+- Inherit from `utils.BaseMutation` to get the `errors` field for free.
+- Mutations that require a password use `@utils.password_required` in addition to `@utils.authentication_required` (see `CreateAPIKeyMutation` in `mutations.py` for a reference).
+- For JSON fields (`metadata`, `options`, `config`), route the payload through `process_dictionaries_mutations([...], input, instance)` — this merges partial dict updates instead of replacing them.
+- Delegate validation + save to DRF serializers in `karrio.server.graph.serializers` (or a `karrio.server.<module>.serializers` for extension modules). Mutation bodies stay short.
+- For generic delete mutations, reuse `mutations.DeleteMutation.mutate(info, model=..., validator=...)` as in the base graph's `delete_parcel` / `delete_metafield`.
+
+### Step 4 — Wire up schema (`__init__.py`)
+
+Keep `__init__.py` as a **thin interface** — Query fields use `strawberry.field(resolver=...)`, Mutation methods are one-liners that delegate to `mutations.X.mutate(info, **input.to_dict())`. No business logic here.
+
+```python
+import typing
+import strawberry
+from strawberry.types import Info
+
+import karrio.server.graph.utils as utils
+import karrio.server.graph.schemas.base.types as types
+import karrio.server.graph.schemas.base.inputs as inputs
+import karrio.server.graph.schemas.base.mutations as mutations
+
+extra_types: list = []  # REQUIRED even if empty
+
+
+@strawberry.type
+class Query:
+    widget: typing.Optional[types.WidgetType] = strawberry.field(
+        resolver=types.WidgetType.resolve
+    )
+    widgets: utils.Connection[types.WidgetType] = strawberry.field(
+        resolver=types.WidgetType.resolve_list
+    )
+
+
+@strawberry.type
+class Mutation:
+    @strawberry.mutation
+    def create_widget(
+        self, info: Info, input: inputs.CreateWidgetMutationInput
+    ) -> mutations.CreateWidgetMutation:
+        return mutations.CreateWidgetMutation.mutate(info, **input.to_dict())
+
+    @strawberry.mutation
+    def update_widget(
+        self, info: Info, input: inputs.UpdateWidgetMutationInput
+    ) -> mutations.UpdateWidgetMutation:
+        return mutations.UpdateWidgetMutation.mutate(info, **input.to_dict())
+```
+
+Auto-discovery: `modules/graph/karrio/server/graph/schema.py` iterates `schemas/` via `pkgutil.iter_modules()` and collects `Query`, `Mutation`, and `extra_types` from every sub-package. No manual registration — but the module must be installed (`-e ./modules/<name>` in `requirements.build.txt`) and opt in via `modules/<name>/karrio/server/settings/<name>.py`.
+
+### Step 5 — Add the Django filter
+
+```python
+# modules/<module>/karrio/server/<module>/filters.py
+import karrio.server.filters as filters  # NOT django_filters directly
+import karrio.server.manager.models as manager
+
+
+class WidgetFilter(filters.FilterSet):
+    keyword = filters.CharFilter(method="keyword_filter")
+    status = filters.CharInFilter(field_name="status", lookup_expr="in")
+    metadata_key = filters.CharInFilter(
+        field_name="metadata", method="metadata_key_filter"
+    )
+    order_by = filters.OrderingFilter(fields={"created_at": "created_at"})
+
+    class Meta:
+        model = manager.Widget
+        fields: list = []
+
+    def keyword_filter(self, queryset, name, value):
+        return queryset.filter(name__icontains=value)
+
+    def metadata_key_filter(self, queryset, name, value):
+        return queryset.filter(metadata__has_key=value)
+```
+
+`karrio.server.filters` re-exports `django_filters` plus karrio-specific filters (`CharInFilter`, …) — see `modules/core/karrio/server/filters/abstract.py`.
+
+### Step 6 — Add the serializer
+
+Serializers live in `modules/<module>/karrio/server/<module>/serializers/` (or a single `serializers.py`). For tenant-scoped models, wrap with `@owned_model_serializer` — it links the instance to `request.user.org` automatically.
+
+```python
+from rest_framework import serializers
+from karrio.server.serializers import owned_model_serializer
+import karrio.server.manager.models as manager
+
+
+@owned_model_serializer
+class WidgetModelSerializer(serializers.ModelSerializer):
+    class Meta:
+        model = manager.Widget
+        exclude = ["created_at", "updated_at", "created_by"]
+```
+
+For system-scoped (admin) serializers, don't wrap; set `created_by` manually in `.create()`:
+
+```python
+class SystemWidgetModelSerializer(serializers.ModelSerializer):
+    class Meta:
+        model = manager.SystemWidget
+        exclude = ["created_at", "updated_at", "created_by"]
+
+    def create(self, validated_data, **kwargs):
+        validated_data["created_by"] = self.context.user
+        return super().create(validated_data)
+```
+
+### Step 7 — Add tests
+
+Tests use `karrio.server.graph.tests.GraphTestCase` (see `modules/graph/karrio/server/graph/tests/base.py`) — it creates class-level user, token, and carrier fixtures via `setUpTestData`.
+
+```python
+from unittest import mock
+from karrio.server.graph.tests import GraphTestCase
+
+
+class TestWidgetSchema(GraphTestCase):
+
+    def test_create_widget(self):
+        response = self.query(
+            """
+            mutation create_widget($data: CreateWidgetMutationInput!) {
+              create_widget(input: $data) {
+                widget { id name }
+                errors { field messages }
+              }
+            }
+            """,
+            operation_name="create_widget",
+            variables=CREATE_DATA,
+        )
+        self.assertResponseNoErrors(response)
+        self.assertDictEqual(response.data, CREATE_RESPONSE)
+
+    def test_list_widgets(self):
+        response = self.query(
+            """
+            query widgets { widgets { edges { node { id name } } } }
+            """,
+            operation_name="widgets",
+        )
+        self.assertResponseNoErrors(response)
+
+
+CREATE_DATA = {"data": {"name": "Test widget"}}
+CREATE_RESPONSE = {
+    "data": {
+        "create_widget": {
+            "widget": {"id": mock.ANY, "name": "Test widget"},
+            "errors": None,
+        }
+    }
+}
+```
+
+Run tests:
+
+```bash
+karrio test --failfast karrio.server.<module>.tests
+```
+
+Debug tip: add `print(response.data)` before `self.assertDictEqual(...)` when diagnosing failures, then remove it. `lib.to_dict()` strips `None` and empty strings — expected fixtures should not include them.
+
+## Admin Graph Differences
+
+Admin schemas live under `modules/admin/karrio/server/admin/schemas/` and in extension modules under `modules/<name>/karrio/server/admin/schemas/<name>/`.
+
+```python
+# types.py in an admin schema — no access_by(), add staff_required
+import karrio.server.admin.utils as admin
+import karrio.server.graph.utils as utils
+
+
+@strawberry.type
+class SystemWidgetType:
+    @staticmethod
+    @utils.authentication_required
+    @admin.staff_required
+    def resolve(info: Info, id: str) -> typing.Optional["SystemWidgetType"]:
+        return manager.SystemWidget.objects.filter(id=id).first()
+
+    @staticmethod
+    @utils.authentication_required
+    @admin.staff_required
+    def resolve_list(
+        info: Info,
+        filter: typing.Optional[inputs.SystemWidgetFilter] = strawberry.UNSET,
+    ) -> utils.Connection["SystemWidgetType"]:
+        _filter = filter if not utils.is_unset(filter) else inputs.SystemWidgetFilter()
+        queryset = filters.SystemWidgetFilter(
+            _filter.to_dict(),
+            manager.SystemWidget.objects.all(),  # no access_by
+        ).qs
+        return utils.paginated_connection(queryset, **_filter.pagination())
+```
+
+Use `admin.superuser_required` for mutations that must be restricted to superusers only.
+
+## N+1 Prevention
+
+Always push `select_related` / `prefetch_related` into the model manager so that both REST and GraphQL benefit automatically.
+
+```python
+class WidgetManager(models.Manager):
+    def get_queryset(self):
+        return (
+            super().get_queryset()
+            .select_related("created_by")
+            .prefetch_related("tags", "services")
+        )
+```
+
+Inside a resolver that touches the same related field twice (e.g. returning computed fields that reuse `self.created_by`), call `.select_related` explicitly on the queryset produced by `access_by`.
+
+## Extension Module GraphQL
+
+To contribute GraphQL from `modules/<name>/`:
+
+1. Create `modules/<name>/karrio/server/graph/schemas/<name>/` with the 4-file layout above.
+2. **Do not** create `__init__.py` anywhere above the leaf `<name>/` directory — shared paths (`karrio/server/graph/`, `karrio/server/graph/schemas/`) must remain implicit namespace packages, otherwise they shadow the core modules. See `.claude/rules/extension-patterns.md`.
+3. Add `-e ./modules/<name>` to `requirements.build.txt` (Docker / prod) **and** `requirements.server.dev.txt` (dev). Without both, schema discovery silently skips your module.
+4. Add `karrio.server.<name>.tests` to `bin/run-server-tests` so CI picks it up.
+5. Create `modules/<name>/karrio/server/settings/<name>.py` with `INSTALLED_APPS += ["karrio.server.<name>"]` so settings auto-discovery picks up the module (see `apps/api/karrio/server/settings/__init__.py`).
+
+For admin-scoped extensions, use `modules/<name>/karrio/server/admin/schemas/<name>/` instead of `graph/schemas/<name>/`.
+
+## Karrio Conventions Recap
+
+- `import karrio.lib as lib` — never legacy `DP`/`SF`/`NF`/`DF`/`XP`.
+- User-facing strings wrap in `gettext_lazy` as `_("...")`.
+- `self.maxDiff = None` in `setUp()` (already done in `GraphTestCase`).
+- Use `unittest` / `karrio test`, never `pytest`.
+- Don't hand-build the final `schema.Schema(...)` — `modules/graph/karrio/server/graph/schema.py` owns that; just export `Query`, `Mutation`, and `extra_types` from your module.
diff --git a/.claude/skills/django-rest-api/SKILL.md b/.claude/skills/django-rest-api/SKILL.md
@@ -0,0 +1,469 @@
+# Skill: Django REST API Development
+
+Add REST endpoints that follow karrio's view, serializer, router, and OpenAPI conventions.
+
+## When to Use
+
+- Adding new REST API endpoints to a core or extension module
+- Creating CRUD + custom-action views for a model
+- Wiring a new resource into the karrio URL namespace
+- Producing OpenAPI metadata for the public karrio-api spec
+
+## Architecture
+
+```
+┌────────────────────────────────────────────────────────────────┐
+│                       REST API Request                         │
+│                                                                │
+│  Client ──> /api/v1/<resource> ──> <module>/urls.py            │
+│                                    ↳ include(router.urls)      │
+│                                                                │
+│  ┌───────────────────────────────┐   ┌───────────────────────┐ │
+│  │ core.views.api.GenericAPIView │   │ core.views.api.APIView │ │
+│  │   (list + create)             │   │   (detail CRUD +      │ │
+│  │   get_queryset() → access_by  │   │    custom actions)    │ │
+│  │   filter_queryset()           │   │                       │ │
+│  │   paginate_queryset()         │   │   Model.access_by(req)│ │
+│  └──────────┬────────────────────┘   └────────┬──────────────┘ │
+│             │                                 │                │
+│             ▼                                 ▼                │
+│  ┌──────────────────────────────────────────────────────────┐  │
+│  │  Serializer.map(data=request.data, context=request)      │  │
+│  │    .save().instance                                      │  │
+│  └──────────────────────────┬───────────────────────────────┘  │
+│                             ▼                                  │
+│  Response(Entity(instance).data, status=...)                   │
+└────────────────────────────────────────────────────────────────┘
+```
+
+Relevant files:
+
+- `modules/manager/karrio/server/manager/views/shipments.py` — canonical reference (full CRUD + rate + purchase + cancel + documents)
+- `modules/orders/karrio/server/orders/views.py` — extension-module reference
+- `modules/core/karrio/server/core/views/api.py` — `GenericAPIView`, `APIView`, `LoggingMixin`
+- `modules/core/karrio/server/core/authentication.py` — `AccessMixin`, token / JWT / OAuth2 authenticators
+- `modules/core/karrio/server/serializers/abstract.py` — `Serializer`, `EntitySerializer`, `PaginatedResult`, `owned_model_serializer`
+- `modules/core/karrio/server/core/serializers.py` — `ErrorResponse`, `ErrorMessages`, enums (`ShipmentStatus`, …)
+- `modules/core/karrio/server/filters/abstract.py` — `FilterSet`, `CharInFilter`, `DateTimeFilter`
+- `modules/core/karrio/server/openapi.py` — `extend_schema` decorator for OpenAPI metadata
+
+## URL Convention
+
+```
+/api/v1/<resource>                    → GenericAPIView: GET (list) + POST (create)
+/api/v1/<resource>/<str:pk>           → APIView: GET + PATCH/PUT + DELETE
+/api/v1/<resource>/<str:pk>/<action>  → APIView: POST (custom action)
+```
+
+All endpoints live under `/api/v1/` (the `urls.py` mounts `router.urls` at `v1/`).
+
+## Step-by-Step: Add CRUD Endpoints
+
+### Step 1 — Create the module router
+
+```python
+# modules/<module>/karrio/server/<module>/router.py
+from rest_framework.routers import DefaultRouter
+
+router = DefaultRouter(trailing_slash=False)
+```
+
+Each module instantiates its own `DefaultRouter`. Views append themselves to `router.urls` at module load time (self-registering pattern — see next step).
+
+### Step 2 — Wire `urls.py`
+
+```python
+# modules/<module>/karrio/server/<module>/urls.py
+"""
+karrio server <module> urls
+"""
+from django.urls import include, path
+from karrio.server.<module>.views import router
+
+app_name = "karrio.server.<module>"
+urlpatterns = [
+    path("v1/", include(router.urls)),
+]
+```
+
+The import side-effect of `from karrio.server.<module>.views import router` triggers view modules to `router.urls.append(...)` themselves. `app_name` must match the dotted module path — `reverse("karrio.server.<module>:<name>")` uses this namespace.
+
+### Step 3 — Define serializers
+
+Serializers use karrio's 3-tier pattern (input / entity / model) plus `PaginatedResult` for list responses. Lay out:
+
+```
+modules/<module>/karrio/server/<module>/serializers/
+├── __init__.py     # re-exports
+├── base.py         # Data + Entity serializers (shapes)
+└── <resource>.py   # ModelSerializer + helpers (mutations)
+```
+
+```python
+# serializers/base.py
+from rest_framework import serializers
+from karrio.server.serializers import (
+    Serializer,
+    EntitySerializer,
+    PaginatedResult,
+    process_dictionaries_mutations,
+    owned_model_serializer,
+)
+import karrio.server.<module>.models as models
+
+
+# 1) Input data shape (what the client POSTs)
+class WidgetData(Serializer):
+    name = serializers.CharField(required=True)
+    description = serializers.CharField(required=False, allow_blank=True)
+    metadata = serializers.PlainDictField(required=False, allow_null=True)
+
+
+# 2) Output entity shape (response body) — inherits input + adds id/timestamps
+class Widget(EntitySerializer, WidgetData):
+    object_type = serializers.CharField(default="widget")
+
+
+# 3) Paginated list (auto-generated wrapper with count/next/previous/results)
+#    Conventionally instantiated in the view module instead of here — see Step 4.
+```
+
+```python
+# serializers/widget.py
+@owned_model_serializer
+class WidgetSerializer(WidgetData):
+    def create(self, validated_data, **kwargs) -> models.Widget:
+        return models.Widget.objects.create(**validated_data)
+
+    def update(self, instance, validated_data, **kwargs) -> models.Widget:
+        data = process_dictionaries_mutations(["metadata"], validated_data, instance)
+        for key, val in data.items():
+            if hasattr(instance, key):
+                setattr(instance, key, val)
+        instance.save()
+        return instance
+```
+
+Karrio conventions:
+
+- `WidgetData` (inputs) stays free of id / timestamps — used as request schema.
+- `Widget` (entity) inherits `WidgetData` and adds the fields `EntitySerializer` provides (id, object_type, created_at, updated_at).
+- `@owned_model_serializer` attaches `created_by` and calls `link_org(...)` for multi-tenancy. Never omit it for tenant-scoped models.
+- Use `Serializer.map(data=..., context=request).save().instance` in views — this is karrio's idiomatic create/update call (see `modules/core/karrio/server/serializers/abstract.py`). `.map(instance, data=...)` auto-sets `partial=True`.
+- For JSON fields (`metadata`, `options`, `config`), always route through `process_dictionaries_mutations([...], payload, instance)` — it merges partial updates instead of clobbering.
+
+### Step 4 — Create views
+
+```python
+# modules/<module>/karrio/server/<module>/views.py
+from django.urls import path
+from rest_framework import status
+from rest_framework.request import Request
+from rest_framework.response import Response
+from rest_framework.pagination import LimitOffsetPagination
+from django_filters.rest_framework import DjangoFilterBackend
+
+from karrio.server.core.views.api import GenericAPIView, APIView
+from karrio.server.serializers import PaginatedResult, process_dictionaries_mutations
+from karrio.server.<module>.router import router
+from karrio.server.<module>.serializers import (
+    Widget,
+    WidgetData,
+    WidgetSerializer,
+)
+import karrio.server.<module>.models as models
+import karrio.server.<module>.filters as filters
+import karrio.server.openapi as openapi
+from karrio.server.core.serializers import ErrorResponse
+
+ENDPOINT_ID = "$$$$$"  # 5-char unique hash — keeps operation_id stable & collision-free
+Widgets = PaginatedResult("WidgetList", Widget)
+
+
+class WidgetList(GenericAPIView):
+    pagination_class = type(
+        "CustomPagination", (LimitOffsetPagination,), dict(default_limit=20)
+    )
+    filter_backends = (DjangoFilterBackend,)
+    filterset_class = filters.WidgetFilters
+    serializer_class = Widgets
+    model = models.Widget
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}list",
+        extensions={"x-operationId": "listWidgets"},
+        summary="List all widgets",
+        responses={200: Widgets(), 500: ErrorResponse()},
+    )
+    def get(self, _: Request):
+        """Retrieve all widgets."""
+        widgets = self.filter_queryset(self.get_queryset())
+        response = self.paginate_queryset(Widget(widgets, many=True).data)
+        return self.get_paginated_response(response)
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}create",
+        extensions={"x-operationId": "createWidget"},
+        summary="Create a widget",
+        request=WidgetData(),
+        responses={201: Widget(), 400: ErrorResponse(), 500: ErrorResponse()},
+    )
+    def post(self, request: Request):
+        """Create a new widget instance."""
+        widget = (
+            WidgetSerializer.map(data=request.data, context=request).save().instance
+        )
+        return Response(Widget(widget).data, status=status.HTTP_201_CREATED)
+
+
+class WidgetDetails(APIView):
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}retrieve",
+        extensions={"x-operationId": "retrieveWidget"},
+        summary="Retrieve a widget",
+        responses={200: Widget(), 404: ErrorResponse(), 500: ErrorResponse()},
+    )
+    def get(self, request: Request, pk: str):
+        widget = models.Widget.access_by(request).get(pk=pk)
+        return Response(Widget(widget).data)
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}update",
+        extensions={"x-operationId": "updateWidget"},
+        summary="Update a widget",
+        request=WidgetData(),
+        responses={200: Widget(), 400: ErrorResponse(), 404: ErrorResponse()},
+    )
+    def patch(self, request: Request, pk: str):
+        widget = models.Widget.access_by(request).get(pk=pk)
+        payload = WidgetData.map(data=request.data).data
+        update = (
+            WidgetSerializer.map(
+                widget,
+                context=request,
+                data=process_dictionaries_mutations(["metadata"], payload, widget),
+            )
+            .save()
+            .instance
+        )
+        return Response(Widget(update).data)
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}discard",
+        extensions={"x-operationId": "discardWidget"},
+        summary="Delete a widget",
+        responses={200: Widget(), 404: ErrorResponse()},
+    )
+    def delete(self, request: Request, pk: str):
+        widget = models.Widget.access_by(request).get(pk=pk)
+        widget.delete(keep_parents=True)
+        return Response(Widget(widget).data)
+
+
+# Self-register at module load time — urls.py imports this module so router.urls is populated.
+router.urls.append(path("widgets", WidgetList.as_view(), name="widget-list"))
+router.urls.append(
+    path("widgets/<str:pk>", WidgetDetails.as_view(), name="widget-details")
+)
+```
+
+Karrio conventions:
+
+- **Base classes**: always `karrio.server.core.views.api.GenericAPIView` / `APIView`, never raw DRF `generics.GenericAPIView` / `views.APIView`. Karrio's base classes inject `LoggingMixin`, token / JWT / OAuth2 auth, throttling, and `access_by`-aware `get_queryset()`.
+- **`ENDPOINT_ID`**: set a 5-character prefix (e.g. `"$$$$$"`, `"&&&&&"`, `"@@@@@"`) at the top of each view module. It is concatenated with `list` / `create` / `retrieve` / `update` / `discard` etc. to keep operation-IDs unique across modules. Duplicates silently break the OpenAPI schema.
+- **`extensions={"x-operationId": "camelCaseName"}`**: provides a stable, human-readable operation id for the public OpenAPI spec and SDK generation.
+- **`extend_schema(request=..., responses={...: ErrorResponse()})`**: document both input and error shapes. `ErrorResponse` and `ErrorMessages` come from `karrio.server.core.serializers`.
+- **Filtering**: `filter_backends = (DjangoFilterBackend,)` + `filterset_class = filters.WidgetFilters`. The filterset lives in your module's `filters.py` and extends `karrio.server.filters.FilterSet`.
+- **Pagination**: subclass `LimitOffsetPagination` inline via `type("CustomPagination", (LimitOffsetPagination,), dict(default_limit=20))` — default limit 20 matches the rest of karrio.
+- **Paginated serializer**: `PaginatedResult("WidgetList", Widget)` factory generates a `{count, next, previous, results}` wrapper. Attach it as `serializer_class` on the list view.
+- **Tenant scoping**: `GenericAPIView.get_queryset()` calls `self.model.access_by(request)` when `model` is set (see `modules/core/karrio/server/core/views/api.py:99`). For `APIView` detail endpoints, call `Model.access_by(request).get(pk=pk)` manually — this is enforced everywhere (e.g. `shipments.py:120`, `orders/views.py:99`).
+- **Route registration**: append to `router.urls` at module level. Prefer `path(...)` over `re_path(...)` unless you need regex groups (e.g. file extensions, see the `ShipmentDocs` example).
+
+### Step 5 — Register the module
+
+Extension modules opt in via their own settings file:
+
+```python
+# modules/<module>/karrio/server/settings/<module>.py
+from karrio.server.settings.base import *  # noqa
+
+KARRIO_URLS += ["karrio.server.<module>.urls"]
+INSTALLED_APPS += ["karrio.server.<module>"]
+```
+
+`apps/api/karrio/server/settings/__init__.py` uses `importlib.util.find_spec()` to conditionally import this file, so it runs only when the module is actually installed.
+
+Then:
+
+- Add `-e ./modules/<module>` to `requirements.build.txt` (prod Docker) **and** `requirements.server.dev.txt` (dev).
+- Add `karrio.server.<module>.tests` to `bin/run-server-tests` so CI picks it up.
+
+See `.claude/rules/extension-patterns.md` for the full checklist.
+
+## Advanced Patterns
+
+### Custom action endpoint
+
+Custom actions are POST endpoints under `/<resource>/<pk>/<action>`. The canonical example is shipment `cancel` / `purchase` / `rates` (`modules/manager/karrio/server/manager/views/shipments.py:163-286`).
+
+```python
+class WidgetArchive(APIView):
+
+    @openapi.extend_schema(
+        tags=["Widgets"],
+        operation_id=f"{ENDPOINT_ID}archive",
+        extensions={"x-operationId": "archiveWidget"},
+        summary="Archive a widget",
+        request=None,
+        responses={200: Widget(), 404: ErrorResponse()},
+    )
+    def post(self, request: Request, pk: str):
+        widget = models.Widget.access_by(request).get(pk=pk)
+        widget.is_archived = True
+        widget.save(update_fields=["is_archived"])
+        return Response(Widget(widget).data)
+
+
+router.urls.append(
+    path("widgets/<str:pk>/archive", WidgetArchive.as_view(), name="widget-archive")
+)
+```
+
+### Fallback lookup by `request_id`
+
+Several karrio endpoints accept either the primary key or the idempotency key stored in `instance.meta["request_id"]` — see `ShipmentCancel` and `OrderCancel`:
+
+```python
+qs = models.Widget.access_by(request)
+try:
+    widget = qs.get(pk=pk)
+except models.Widget.DoesNotExist:
+    widget = qs.filter(meta__request_id=pk).order_by("-created_at").first()
+
+if widget is None:
+    raise models.Widget.DoesNotExist()
+```
+
+### Filtering with `filters.py`
+
+```python
+# modules/<module>/karrio/server/<module>/filters.py
+import karrio.server.filters as filters
+from django.db.models import Q
+import karrio.server.<module>.models as models
+import karrio.server.<module>.serializers as serializers
+
+
+class WidgetFilters(filters.FilterSet):
+    keyword = filters.CharFilter(method="keyword_filter")
+    status = filters.MultipleChoiceFilter(
+        field_name="status",
+        choices=[(s.value, s.value) for s in list(serializers.WidgetStatus)],
+    )
+    created_after = filters.DateTimeFilter(field_name="created_at", lookup_expr="gte")
+    created_before = filters.DateTimeFilter(field_name="created_at", lookup_expr="lte")
+    metadata_key = filters.CharInFilter(
+        field_name="metadata", method="metadata_key_filter"
+    )
+
+    parameters = [
+        # Optional: OpenAPI parameter hints — see ShipmentFilters for the full pattern
+    ]
+
+    class Meta:
+        model = models.Widget
+        fields: list = []
+
+    def keyword_filter(self, queryset, name, value):
+        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))
+
+    def metadata_key_filter(self, queryset, name, value):
+        return queryset.filter(metadata__has_key=value)
+```
+
+`karrio.server.filters` re-exports `django_filters.rest_framework` plus karrio helpers (`CharInFilter`). In the view, reference the filter class and pass `filters.ShipmentFilters.parameters` to `extend_schema(parameters=...)` to inherit OpenAPI parameter metadata.
+
+### Document / file download
+
+For label / invoice downloads, extend `django_downloadview.VirtualDownloadView` and mix `AccessMixin`:
+
+```python
+from karrio.server.core.authentication import AccessMixin
+from django_downloadview import VirtualDownloadView
+
+
+class WidgetDocs(AccessMixin, VirtualDownloadView):
+    @openapi.extend_schema(exclude=True)  # exclude from public spec
+    def get(self, request, pk, doc="file", format="pdf", **kwargs):
+        ...
+```
+
+See `ShipmentDocs` in `manager/views/shipments.py:288-352` for the full pattern (resource-token validation, `lib.failsafe` ZPL-to-PDF conversion, `X-Frame-Options: ALLOWALL`).
+
+### N+1 prevention in views
+
+Push `select_related` / `prefetch_related` into the model manager's default queryset so both list + detail benefit automatically:
+
+```python
+class WidgetManager(models.Manager):
+    def get_queryset(self):
+        return (
+            super().get_queryset()
+            .select_related("created_by")
+            .prefetch_related("tags")
+        )
+```
+
+`GenericAPIView.get_queryset()` calls `model.access_by(request)`, which goes through your custom manager — no need to override on a per-view basis.
+
+## Testing REST Endpoints
+
+Tests use `karrio.server.core.tests.APITestCase` (see `modules/core/karrio/server/core/tests/base.py`) — it creates a class-level superuser, API token, and carrier fixtures.
+
+```python
+import json
+from django.http.response import HttpResponse
+from django.urls import reverse
+from rest_framework import status
+from karrio.server.core.tests import APITestCase
+
+
+class TestWidgetFixture(APITestCase):
+    def create_widget(self) -> tuple[HttpResponse, dict]:
+        url = reverse("karrio.server.<module>:widget-list")
+        response = self.client.post(url, WIDGET_DATA)
+        return response, json.loads(response.content)
+
+
+class TestWidgets(TestWidgetFixture):
+    def test_create_widget(self):
+        response, data = self.create_widget()
+        # print(data)  # DEBUG — remove before committing
+        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
+        self.assertDictEqual(data, WIDGET_RESPONSE)
+
+
+WIDGET_DATA = {"name": "Test widget"}
+WIDGET_RESPONSE = {...}
+```
+
+Run:
+
+```bash
+karrio test --failfast karrio.server.<module>.tests
+./bin/run-server-tests                       # the whole server suite
+```
+
+Karrio testing conventions:
+
+- No `pytest` anywhere — `unittest` for SDK, `karrio test` for server (Django).
+- `self.maxDiff = None` is already set by `APITestCase.setUp`.
+- Always use `reverse("karrio.server.<module>:<url-name>")` — hardcoding paths like `/api/v1/widgets` breaks under URL-prefix changes.
+- `lib.to_dict(...)` strips `None` / empty strings — expected fixtures should mirror that.
+- Add `print(response.data)` before the assertion while diagnosing failures, then remove it when the test passes (see `.claude/rules/testing.md`).
diff --git a/.claude/skills/review-implementation/SKILL.md b/.claude/skills/review-implementation/SKILL.md
@@ -39,49 +39,98 @@ ls PRDs/
 git diff main...HEAD --name-only | grep -i test
 ```
 
-- [ ] Every new mutation/query has a corresponding test
+- [ ] Every new mutation/query/endpoint has a corresponding test
 - [ ] Every model change has a migration test
 - [ ] Tests use `assertResponseNoErrors` + `assertDictEqual` pattern
 - [ ] No `pytest` usage anywhere in new code
 - [ ] `mock.ANY` used for dynamic fields (id, timestamps)
-- [ ] Carrier tests follow 4-method pattern (if carrier work)
+- [ ] Carrier tests follow the 4-method pattern (if carrier work)
+- [ ] Imports at top of test file — never inside a test method
 
-### 4. Code Quality Check
+### 4. Extension Pattern Check
+
+- [ ] New domain logic lives in `modules/<name>/`, not sprinkled across `modules/core` / `modules/graph` / `modules/manager`
+- [ ] Hooks used where applicable (`@pre_processing`, `AppConfig.ready()`)
+- [ ] New modules follow the pattern in `.claude/rules/extension-patterns.md`
+- [ ] Module registered in `requirements.build.txt` (`-e ./modules/<name>`) AND in `bin/run-server-tests`
+
+### 5. Code Quality Check
 
 Review each changed file for:
 
-- [ ] Uses `import karrio.lib as lib` (not legacy utilities)
-- [ ] Functional style (list comprehensions, map/filter)
-- [ ] No bare exceptions, mutable defaults, `any` types
-- [ ] Django: `OwnedEntity` for tenant-scoped, N+1 prevention
-- [ ] GraphQL: `utils.Connection[T]` for lists, proper decorators
-- [ ] No manually edited auto-generated files
+- [ ] Uses `import karrio.lib as lib` — no legacy `DP`/`SF`/`NF`/`DF`/`XP`
+- [ ] Functional style (list comprehensions, `map`/`filter`) rather than imperative loops
+- [ ] No bare `except:` / `except Exception:` — specific exceptions only
+- [ ] No mutable default arguments
+- [ ] No `any` types in TypeScript
+- [ ] Django: `OwnedEntity` for tenant-scoped models, plain `Model` for system models
+- [ ] GraphQL: `utils.Connection[T]` for lists, `@authentication_required` on resolvers
+- [ ] No manually edited auto-generated files (`mapper.py`, `karrio/schemas/<carrier>/*`, `packages/karriojs/api/generated/*`)
+- [ ] User-facing strings wrapped in `gettext`
+
+### 6. N+1 Query Prevention Check
+
+**CRITICAL**: N+1 queries are the #1 performance killer. Check every changed model, serializer, and view. Full patterns in `.claude/rules/django-patterns.md`.
+
+**New models:**
+- [ ] Custom manager with `get_queryset()` that applies `select_related` / `prefetch_related`
+- [ ] ForeignKey fields have `select_related` in the manager
+- [ ] Reverse FK / M2M fields have `prefetch_related` in the manager
+
+**Serializers / GraphQL types:**
+- [ ] No FK access (e.g., `obj.carrier.name`) without corresponding `select_related` in the queryset
+- [ ] No reverse FK iteration (e.g., `obj.items.all()`) without `prefetch_related`
+- [ ] Computed `@strawberry.field` methods don't trigger per-row queries
+
+**Views / Resolvers:**
+- [ ] List views use optimized querysets (via manager or explicit `.select_related()`)
+- [ ] No `Model.objects.get(pk=pk)` inside loops — batch with `filter(pk__in=pks)`
 
-### 5. Migration Safety Check (if applicable)
+**Bulk operations:**
+- [ ] No `for x in data: Model.objects.create()` — use `bulk_create()`
+- [ ] No `for x in qs: x.save()` — use `bulk_update()`
 
-- [ ] Operations ordered correctly
+**Red flags to grep for:**
+
+```bash
+git diff main...HEAD -U0 | grep -E '\.(save|create)\(' | head -20
+git diff main...HEAD -U0 | grep -E '\.objects\.(get|filter)' | head -20
+git diff main...HEAD -U0 | grep -E '\.all\(\)' | head -20
+```
+
+### 7. Migration Safety Check (if migrations exist)
+
+- [ ] Operations ordered correctly (create table before data migration before column removal)
 - [ ] Data migrations preserve existing data
-- [ ] No `RunSQL` — Django operations only
+- [ ] Dependencies include all prerequisite migrations
+- [ ] No `RunSQL` — uses Django operations only
 - [ ] Works across SQLite, PostgreSQL, MySQL
+- [ ] Rolling-deploy safe (no removals that crash running pods on older code)
 
-### 6. Security Check
+### 8. Security Check
 
-- [ ] No hardcoded secrets
-- [ ] Tenant isolation (queries filtered by org)
-- [ ] Input validation at boundaries
+- [ ] No hardcoded secrets or credentials
+- [ ] Tenant isolation: all queries filtered by `org=request.user.org`
+- [ ] No raw SQL injection vectors
+- [ ] Input validation at system boundaries (serializers, GraphQL inputs)
+- [ ] Sensitive fields not logged / tracked in request recordings
 
 ## Output Format
 
+Report findings as:
+
 ```
 ## Review Summary
 
 ### Status: PASS / NEEDS CHANGES
 
 ### Findings
 1. [PASS] PRD compliance — all requirements met
-2. [FAIL] Missing test for delete mutation
-3. [WARN] Consider using mixin for shared logic
+2. [FAIL] Missing test for `delete_rate_sheet` mutation
+3. [WARN] Consider using mixin pattern for shared serializer logic
+4. [FAIL] `obj.carrier.name` accessed in serializer without `select_related`
 
 ### Required Actions
-- Add test for delete mutation
+- Add test for delete mutation in `modules/<module>/karrio/server/<module>/tests/`
+- Add `select_related("carrier")` to the serializer's base queryset
 ```
diff --git a/.claude/skills/run-tests/SKILL.md b/.claude/skills/run-tests/SKILL.md
@@ -0,0 +1,94 @@
+# Skill: Run Tests
+
+Execute the appropriate test suites based on what was changed.
+
+## When to Use
+
+- After implementing a feature or fix
+- Before creating a commit or PR
+- When validating that changes don't break existing functionality
+
+## Determine What to Test
+
+```bash
+git diff --name-only HEAD
+git diff --name-only --cached   # staged changes
+git diff --name-only main...HEAD  # whole branch vs main
+```
+
+## Test Commands by Area
+
+### SDK / Connectors
+
+```bash
+source bin/activate-env
+
+# All SDK + connector tests (slow; full coverage)
+./bin/run-sdk-tests
+
+# Single carrier (fast; local flow)
+python -m unittest discover -v -f modules/connectors/<carrier>/tests
+
+# Single module
+python -m unittest discover -v -f modules/sdk/karrio/core/tests
+```
+
+### Server Modules (Django)
+
+```bash
+# All server tests
+./bin/run-server-tests
+
+# Single module (fast, --failfast stops on first error)
+karrio test --failfast karrio.server.<module>.tests
+
+# Common modules:
+karrio test --failfast karrio.server.graph.tests     # Base GraphQL
+karrio test --failfast karrio.server.admin.tests     # Admin GraphQL
+karrio test --failfast karrio.server.manager.tests   # Shipments / trackers REST
+karrio test --failfast karrio.server.providers.tests # Carrier connections
+karrio test --failfast karrio.server.pricing.tests   # Markups / fees
+karrio test --failfast karrio.server.orders.tests    # Orders
+karrio test --failfast karrio.server.events.tests    # Webhooks / events
+karrio test --failfast karrio.server.documents.tests # Documents / labels
+karrio test --failfast karrio.server.data.tests      # Imports / exports
+```
+
+### Frontend (Dashboard)
+
+```bash
+cd apps/dashboard && pnpm test
+cd apps/dashboard && pnpm tsc --noEmit   # type-checking only
+cd apps/dashboard && pnpm build          # full production build
+```
+
+## Decision Table
+
+| Files changed | Command |
+|---|---|
+| `modules/sdk/` | `./bin/run-sdk-tests` |
+| `modules/connectors/<carrier>/` | `python -m unittest discover -v -f modules/connectors/<carrier>/tests` |
+| `modules/graph/` | `karrio test --failfast karrio.server.graph.tests` |
+| `modules/admin/` | `karrio test --failfast karrio.server.admin.tests` |
+| `modules/manager/` | `karrio test --failfast karrio.server.manager.tests` |
+| `modules/orders/` | `karrio test --failfast karrio.server.orders.tests` |
+| `modules/events/` | `karrio test --failfast karrio.server.events.tests` |
+| `modules/documents/` | `karrio test --failfast karrio.server.documents.tests` |
+| `modules/core/` | `./bin/run-server-tests` (broad impact) |
+| `modules/<new-extension>/` | `karrio test --failfast karrio.server.<name>.tests` (after registering in `bin/run-server-tests`) |
+| `apps/dashboard/` | `cd apps/dashboard && pnpm test && pnpm tsc --noEmit` |
+| Multiple areas | `./bin/run-sdk-tests && ./bin/run-server-tests` |
+
+## Debugging Failures
+
+1. Add `print(response.data)` (or `print(lib.to_dict(parsed_response))`) before the failing assertion.
+2. Run a single test: `karrio test --failfast karrio.server.<module>.tests.<TestClass>.<test_method>`.
+3. Check for missing fixtures, seed data, or cached auth.
+4. Remove `print` statements once tests pass.
+
+## Tips
+
+- `HUEY["immediate"] = True` in test settings — Huey tasks run synchronously. Don't mock them unless you're testing failure paths.
+- `lib.to_dict()` strips `None` and empty strings — expected fixtures shouldn't include them.
+- `lib.failsafe()` swallows exceptions — remove it temporarily to see the underlying error during debug.
+- `str(None)` is `"None"` (not `None`) — always guard with a truthy check first.
diff --git a/AGENTS.md b/AGENTS.md
@@ -7,11 +7,33 @@
 
 ## Context Priority
 
-1. **Read this file first** for repository conventions
-2. For carrier integrations, consult `CARRIER_INTEGRATION_GUIDE.md`
-3. Check PRDs in `PRDs/` folder for feature architecture decisions
-4. Review existing code patterns before implementing new features
-5. **Search for existing utilities before writing new code**
+Load context in this order — later items override/refine earlier ones:
+
+1. **`CLAUDE.md`** (lean, project-specific) and this `AGENTS.md` (comprehensive reference) — the two sources of truth for project conventions.
+2. **`.claude/rules/*.md`** (scoped rules) — load the rule that matches what you're doing:
+   - `code-style.md` — naming, imports, formatting
+   - `testing.md` — unittest / `karrio test`, no pytest, 4-method carrier test pattern
+   - `git-workflow.md` — commits, submodules, changelog
+   - `commit-conventions.md` — `type(scope): summary` format
+   - `django-patterns.md` — multi-tenancy, N+1, migrations, Huey
+   - `carrier-integration.md` — connector structure, definition of done
+   - `extension-patterns.md` — "extend, don't modify core"; namespace-package rules
+   - `prd-and-review.md` — PRD-first workflow, fresh-context review gates
+3. **`.claude/skills/<name>/SKILL.md`** (step-by-step guides) — invoke by user or by another skill:
+   - `create-prd` — write PRDs with ASCII diagrams before non-trivial features
+   - `create-extension-module` — scaffold a new `modules/<name>/` extension
+   - `django-graphql` — schema layout + auto-discovery + test patterns
+   - `django-rest-api` — view / serializer / router patterns
+   - `carrier-integration` — full carrier connector implementation
+   - `run-tests` — pick the right test command for the changed files
+   - `review-implementation` — fresh-context review checklist
+   - `debugging` — request lifecycle, debugging commands, common pitfalls
+   - `project-setup` — environment setup, running servers, schema generation
+   - `release` — version bumping, package sync, frozen requirements, changelog
+4. **PRDs in `PRDs/`** — feature architecture decisions and active workstreams (e.g. `RELEASE_2026_5_PLATFORM_UPGRADE.md`, `SUBTREE_SYNC_WORKFLOW.md`).
+5. **Carrier integrations** — consult `CARRIER_INTEGRATION_GUIDE.md` and the existing carriers under `modules/connectors/*/`.
+6. **Existing code patterns** — review before implementing; prefer reuse via `karrio.lib.*` and existing hooks.
+7. **Search for existing utilities before writing new code.**
 
 ---
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -46,22 +46,28 @@ npm run build                                                    # Turbo build a
 ## Detailed Rules
 
 Scoped rules are in `.claude/rules/`:
-- `code-style.md` — naming, imports, formatting
-- `testing.md` — test commands, patterns, fixtures
+- `code-style.md` — naming, imports, formatting, i18n
+- `testing.md` — test commands, patterns, fixtures, imports-at-top rule
 - `git-workflow.md` — commits, submodules, changelog
+- `commit-conventions.md` — `type(scope): summary` format, branch naming
 - `django-patterns.md` — multi-tenancy, N+1, migrations, Huey jobs
 - `carrier-integration.md` — connector structure, definition of done
+- `extension-patterns.md` — "extend, don't modify core" + namespace-package rules
 - `prd-and-review.md` — PRD-first workflow, fresh-context review gates
 
 ## Skills
 
 Skills in `.claude/skills/` provide step-by-step guides:
 - `carrier-integration/` — Full carrier connector implementation (5 phases)
-- `release/` — Version bumping, package sync, frozen requirements, changelog
+- `create-extension-module/` — Scaffold a new `modules/<name>/` extension with AppConfig + auto-discovery
+- `create-prd/` — Write PRDs with ASCII diagrams before non-trivial features
 - `debugging/` — Request lifecycle, debugging commands, common pitfalls
+- `django-graphql/` — Schema layout, auto-discovery, mutation/query patterns
+- `django-rest-api/` — View / serializer / router patterns
 - `project-setup/` — Environment setup, running servers, schema generation
-- `create-prd/` — Write PRDs with ASCII diagrams before non-trivial features
+- `release/` — Version bumping, package sync, frozen requirements, changelog
 - `review-implementation/` — Fresh-context review checklist for quality gates
+- `run-tests/` — Decision table: which test command for the changed files
 
 ## Full Reference
 
PATCH

echo "Gold patch applied."
