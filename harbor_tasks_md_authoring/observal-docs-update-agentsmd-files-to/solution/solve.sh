#!/usr/bin/env bash
set -euo pipefail

cd /workspace/observal

# Idempotency guard
if grep -qF "The web frontend is a Next.js 16 / React 19 app in `web/`. It uses four route gr" "AGENTS.md" && grep -qF "**Critical constraint:** Core must NEVER import from `ee/`. Dependency is strict" "ee/AGENTS.md" && grep -qF "- **Design system:** OKLCH color space with 5 themes (light, dark, midnight, for" "web/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -10,7 +10,9 @@ All API routes accept either UUID or name for path parameters. Admin review cont
 
 The MCP validator supports multiple frameworks: FastMCP, standard MCP SDK (Python), TypeScript SDK (`@modelcontextprotocol/sdk`), and Go SDK (`mcp-go`). There is no framework enforcement - all MCP implementations are accepted.
 
-The web frontend is a Next.js 16 / React 19 app in `web/`. It uses three route groups: `(auth)` for login, `(registry)` for the public-facing agent browser, component library, and agent builder, and `(admin)` for the admin dashboard, traces, eval, review, and user management. The frontend has a custom OKLCH design system with 5 themes (light, dark, midnight, forest, sunset), three typefaces (Archivo for display, Albert Sans for body, JetBrains Mono for code), and a 4pt spacing scale. It uses shadcn/ui components, Recharts for charts, TanStack Query for data fetching, and TanStack Table for sortable/filterable tables. Shared API response types live in `web/src/lib/types.ts`. The GraphQL API at `/api/v1/graphql` is the read layer for telemetry data; REST endpoints serve everything else.
+The platform generates portable agent configs for 8 IDEs: Claude Code, Cursor, Gemini CLI, Kiro, VS Code, Codex CLI, GitHub Copilot, and OpenCode. The agent builder (`services/agent_builder.py`) and agent resolver (`services/agent_resolver.py`) compose and validate component bundles into IDE-specific output formats.
+
+The web frontend is a Next.js 16 / React 19 app in `web/`. It uses four route groups: `(auth)` for login, `(registry)` for the public-facing agent browser, component library, and agent builder, `(admin)` for the admin dashboard, eval, review, alerts, user management, and settings, and `(user)` for user-scoped trace views. The frontend has a custom OKLCH design system with 5 themes (light, dark, midnight, forest, sunset), three typefaces (Archivo for display, Albert Sans for body, JetBrains Mono for code), and a 4pt spacing scale. It uses shadcn/ui components, Recharts for charts, TanStack Query for data fetching, and TanStack Table for sortable/filterable tables. Shared API response types live in `web/src/lib/types.ts`. The GraphQL API at `/api/v1/graphql` is the read layer for telemetry data; REST endpoints serve everything else.
 
 ## CLI structure
 
@@ -21,6 +23,7 @@ observal
 ├── pull                     # install complete agent (primary workflow)
 ├── scan                     # detect and instrument IDE configs
 ├── use / profile            # swap IDE configs from git-hosted profiles
+├── uninstall                # tear down Docker stack, remove repo and config
 ├── auth                     # init, login, logout, whoami, status
 ├── config                   # show, set, path, alias, aliases
 ├── registry                 # component registry parent group
@@ -37,8 +40,10 @@ observal
 ├── admin                    # admin commands
 │   ├── settings, set, users
 │   ├── penalties, penalty-set, weights, weight-set
+│   ├── canaries, canary-add, canary-reports, canary-delete
 │   ├── review               #   list, show, approve, reject
 │   └── eval                 #   run, scorecards, show, compare, aggregate
+├── migrate                  # ClickHouse telemetry migration tools
 ├── self                     # upgrade, downgrade
 └── doctor                   # diagnose IDE settings compatibility
 ```
@@ -48,7 +53,7 @@ Deprecated root-level aliases exist for backward compatibility (e.g. `observal s
 ## Commands
 
 ```bash
-# Docker stack (7 services: api, db, clickhouse, redis, worker, web, otel-collector)
+# Docker stack (11 services: init, api, db, clickhouse, redis, worker, web, lb, otel-collector, prometheus, grafana)
 make up                  # start
 make down                # stop
 make rebuild             # rebuild and restart
@@ -66,7 +71,7 @@ make format              # ruff format + ruff fix
 make check               # pre-commit on all files
 make hooks               # install pre-commit hooks
 
-# Tests (526 tests across 18 files, run from observal-server/)
+# Tests (1429 tests across 52 files, run from observal-server/)
 make test                # quick
 make test-v              # verbose
 # or manually:
@@ -98,13 +103,20 @@ cd observal-server && uv run --with pytest --with pytest-asyncio --with pyyaml -
 - `api/routes/admin.py` : Enterprise settings CRUD, user management, role changes, penalty catalog, dimension weights
 - `api/routes/alert.py` : Alert rule CRUD (metric threshold alerts with webhook URLs)
 - `api/routes/scan.py` : `POST /api/v1/scan` bulk registration from IDE config scans; deduplicates by name
+- `api/routes/bulk.py` : Bulk agent creation from scan results
+- `api/routes/jwks.py` : JWKS discovery endpoint for JWT public key distribution
+- `api/routes/otlp.py` : OTLP HTTP receiver; accepts standard `/v1/traces`, `/v1/logs`, `/v1/metrics` and converts to ClickHouse format
+- `api/routes/otel_dashboard.py` : OpenTelemetry-native dashboard queries
+- `api/routes/component_source.py` : Component source CRUD and sync endpoints for git mirror origins
+- `api/routes/config.py` : Server endpoint discovery and public config (eliminates hardcoded URLs)
 
 ### Models (`observal-server/models/`)
 
 - `user.py` : User with UserRole enum (admin, developer, user); API key is hashed with SHA-256
 - `mcp.py` : McpListing, McpValidationResult, McpDownload; ListingStatus enum (shared by all models)
 - `agent.py` : Agent, AgentGoalTemplate, AgentGoalSection, AgentStatus enum
 - `alert.py` : AlertRule (metric threshold alerts with webhook URLs)
+- `alert_history.py` : AlertHistory (fired alert records with resolved timestamps)
 - `skill.py` : SkillListing, SkillDownload
 - `hook.py` : HookListing, HookDownload
 - `prompt.py` : PromptListing, PromptDownload
@@ -115,22 +127,45 @@ cd observal-server && uv run --with pytest --with pytest-asyncio --with pyyaml -
 - `enterprise_config.py` : Key-value enterprise settings
 - `organization.py` : Organization (id, name, slug, created_at, updated_at)
 - `component_source.py` : ComponentSource, Git mirror origins for component discovery
+- `component_bundle.py` : ComponentBundle, bundled component snapshots for portable sharing
 - `agent_component.py` : AgentComponent, polymorphic junction table (agent_id, component_type, component_id); NO FK on component_id
 - `download.py` : AgentDownloadRecord (deduplicated by user_id + fingerprint), ComponentDownloadRecord (not deduplicated)
 - `exporter_config.py` : ExporterConfig, per-org telemetry export settings (grafana, datadog, loki, otel)
+- `password_reset_token.py` : PasswordResetToken, time-limited reset tokens
+- `sanitization.py` : Sanitization rules for telemetry data scrubbing
+- `scoring.py` : Scoring models for eval dimension weights and composite grades
 
 ### Services (`observal-server/services/`)
 
 - `clickhouse.py` : ClickHouse HTTP client; DDL for 5 tables (2 legacy + 3 new); insert/query helpers with parameterized SQL builder; `INIT_SQL` runs on startup
 - `redis.py` : Redis connection, pub/sub (publish/subscribe), eval job queue (enqueue_eval)
 - `config_generator.py` : Generates IDE config snippets per MCP; wraps commands with `observal-shim`; handles stdio vs HTTP transport
 - `agent_config_generator.py` : Generates bundled agent configs (rules file + MCP configs); injects OBSERVAL_AGENT_ID env var
+- `agent_builder.py` : Composes resolved components into portable agent manifests for 8 IDEs
+- `agent_resolver.py` : Looks up and validates all components for an agent; produces ResolvedAgent
 - `sandbox_config_generator.py` : Wraps sandbox execution with `observal-sandbox-run` entry point
 - `skill_config_generator.py` : Emits SessionStart/End hooks for skill activation telemetry
 - `hook_config_generator.py` : Generates IDE-specific HTTP hook configs (Claude Code, Kiro, Cursor)
+- `hook_materializer.py` : Materializes hook definitions into runnable IDE configs
+- `codex_config_generator.py` : Generates Codex CLI-specific agent and MCP configs
 - `mcp_validator.py` : 2-stage validation: clone+inspect (git clone, find entry point, detect framework) + manifest validation. Detects FastMCP, standard MCP SDK (Python), TypeScript SDK, and Go SDK. No framework enforcement.
 - `eval_engine.py` : `EvalBackend` ABC; `LLMJudgeBackend` (Bedrock/OpenAI); `FallbackBackend` (deterministic); 6 managed prompt templates
 - `eval_service.py` : Orchestrates eval runs: fetch traces, run backend, create scorecards
+- `alert_evaluator.py` : Periodic metric threshold checks against ClickHouse; fires webhooks on breach
+- `cache.py` : Caching layer for frequently accessed registry data
+- `crypto.py` : Cryptographic utilities (payload encryption, key derivation)
+- `demo_accounts.py` : Demo/seed account provisioning
+- `download_tracker.py` : Tracks agent and component download metrics
+- `events.py` : Internal event bus for cross-service coordination
+- `git_mirror_service.py` : Git mirroring for component source synchronization
+- `ide_feature_inference.py` : Detects IDE capabilities from config files for smart config generation
+- `jwt_service.py` : JWT signing and verification for token-based auth
+- `registry_telemetry.py` : Telemetry collection for registry operations (installs, searches, etc.)
+- `secrets_redactor.py` : Redacts secrets from telemetry spans before storage
+- `security_events.py` : Security event logging and audit trail
+- `versioning.py` : Component versioning and compatibility checks
+- `webhook_delivery.py` : Webhook HTTP delivery with retry logic and SSRF protection
+- `webhook_signer.py` : HMAC signing for outbound webhook payloads
 
 ### Schemas (`observal-server/schemas/`)
 
@@ -147,11 +182,13 @@ cd observal-server && uv run --with pytest --with pytest-asyncio --with pyyaml -
 - `cmd_hook.py` : `hook_app` subgroup: submit, list, show, install, delete
 - `cmd_prompt.py` : `prompt_app` subgroup: submit, list, show, install, render, delete
 - `cmd_sandbox.py` : `sandbox_app` subgroup: submit, list, show, install, delete
-- `cmd_scan.py` : `observal scan`: auto-detect IDE configs (Cursor, Kiro, VS Code, Claude Code, Gemini CLI), bulk-register MCPs, wrap with observal-shim; `--dry-run`, `--ide`, `--yes` flags
+- `cmd_scan.py` : `observal scan`: auto-detect IDE configs (Claude Code, Cursor, Kiro, VS Code, Gemini CLI, Codex CLI), bulk-register MCPs, wrap with observal-shim; `--dry-run`, `--ide`, `--yes` flags. Auto-detects home dirs when project dir empty.
 - `cmd_pull.py` : `observal pull`: fetch agent config from server, write IDE files (rules, MCP config, agent files) to disk; `--dry-run`, `--dir` flags; merges MCP configs with existing files
 - `cmd_profile.py` : `observal use` + `observal profile`: swap IDE configs from git-hosted profiles; clones/caches profiles, backs up current config, restores via `observal use default`
 - `cmd_ops.py` : `ops_app` subgroup: overview, metrics (--watch), top, traces, spans, rate, feedback, sync. Contains `telemetry_app` (status, test). Also `admin_app` subgroup: settings, set, users, penalties, penalty-set, weights, weight-set, canaries, canary-add, canary-reports, canary-delete. Contains `review_app` (list, show, approve, reject) and `eval_app` (run, scorecards, show, compare, aggregate). Also `self_app` subgroup: upgrade, downgrade
-- `cmd_doctor.py` : `doctor_app`: diagnose IDE settings for Observal compatibility; checks Observal config, server connectivity, IDE configs (Claude Code, Kiro, Cursor, Gemini CLI), env vars, Docker availability, entry points; `--ide` to target specific IDE, `--fix` to show suggested fixes
+- `cmd_doctor.py` : `doctor_app`: diagnose IDE settings for Observal compatibility; checks Observal config, server connectivity, IDE configs (Claude Code, Kiro, Cursor, Gemini CLI, Codex CLI, Copilot, OpenCode), env vars, Docker availability, entry points; `--ide` to target specific IDE, `--fix` to show suggested fixes
+- `cmd_migrate.py` : `migrate_app`: ClickHouse telemetry migration tools for PostgreSQL shallow-copy migrations
+- `cmd_uninstall.py` : `observal uninstall`: tear down Docker stack, remove repo and config files
 - `client.py` : httpx wrapper with get/post/put/delete/health; contextual error messages per status code
 - `config.py` : ~/.observal/config.json management; alias system (@name -> UUID resolution)
 - `render.py` : Shared Rich rendering: status badges, relative timestamps, IDE color tags, star ratings, kv panels, spinners
@@ -161,13 +198,13 @@ cd observal-server && uv run --with pytest --with pytest-asyncio --with pyyaml -
 
 ### Docker (`docker/`)
 
-- `docker-compose.yml` : 8 services: api (8000), db (PostgreSQL 16), clickhouse (8123), redis (6379), worker (arq), web (3000), otel-collector (4317/4318), grafana (3001)
+- `docker-compose.yml` : 11 services: init (migrations), api (8000), db (PostgreSQL 16), clickhouse (8123), redis (6379), worker (arq), web (3000), lb (nginx reverse proxy), otel-collector (4317/4318), prometheus (9090), grafana (3001)
 - `Dockerfile.api` : uv-based Python build
 - `Dockerfile.web` : Node 24-alpine, multi-stage build with standalone output
 
 ### Tests (`tests/`)
 
-- 526 tests across 18 files; all mock external services (no Docker needed to run)
+- 1429 tests across 52 files; all mock external services (no Docker needed to run)
 - `test_clickhouse_phase1.py` : DDL, SQL helpers, insert/query functions
 - `test_ingest_phase2.py` : Ingestion schemas, endpoint, partial failure
 - `test_shim_phase3.py` : JSON-RPC parsing, schema compliance, ShimState, config gen
@@ -186,12 +223,52 @@ cd observal-server && uv run --with pytest --with pytest-asyncio --with pyyaml -
 - `test_structural_scorer.py` : Rule-based structural scoring
 - `test_slm_scorer.py` : LLM-based SLM scoring
 - `test_score_aggregator.py` : Score aggregation and composite grading
+- `test_agent_config_generator.py` : Agent config generation for all IDEs
+- `test_agent_name_lookup.py` : Agent name resolution
+- `test_agent_review.py` : Agent review workflow
+- `test_alert_evaluator.py` : Alert threshold evaluation and webhook firing
+- `test_audit_logging.py` : Audit log creation and queries
+- `test_auth_redis_down.py` : Auth resilience when Redis is unavailable
+- `test_bulk.py` : Bulk agent creation
+- `test_bundles.py` : Component bundle packaging
+- `test_clickhouse_resource_tuning.py` : ClickHouse resource configuration
+- `test_clickhouse_retention.py` : ClickHouse data retention policies
+- `test_cli_errors.py` : CLI error handling and messages
+- `test_config_generator_utils.py` : Config generation utilities
+- `test_constants_sync.py` : Constant synchronization between frontend and backend
+- `test_demo_accounts.py` : Demo account provisioning
+- `test_deployment_guards.py` : Deployment safety checks
+- `test_docker_detection.py` : Docker availability detection
+- `test_draft_workflow.py` : Draft submission workflow
+- `test_endpoint_discovery.py` : Server endpoint discovery
+- `test_enterprise.py` : Enterprise feature gates
+- `test_env_detection_and_config.py` : Environment detection
+- `test_events.py` : Internal event bus
+- `test_field_validation.py` : Input field validation
+- `test_health.py` : Health endpoint behavior
+- `test_ide_config_e2e.py` : End-to-end IDE config generation
+- `test_migrate.py` : Migration tooling
+- `test_migrate_telemetry.py` : Telemetry migration
+- `test_payload_crypto.py` : Payload encryption
+- `test_resilience.py` : Service resilience under failure
+- `test_review_queue.py` : Review queue operations
+- `test_sanitize.py` : Telemetry sanitization
+- `test_scan_kiro_home.py` : Kiro home directory scanning
+- `test_secrets_redactor.py` : Secret redaction in telemetry
+- `test_settings_reconciler.py` : Settings reconciliation
+- `test_skill_config_generator.py` : Skill config generation
+- `test_uninstall.py` : Uninstall command
+- `test_uninstall_windows.py` : Windows uninstall paths
+- `test_versioning.py` : Component versioning
+- `test_webhook_delivery.py` : Webhook delivery and retry
+- `test_webhook_signer_properties.py` : Webhook signer property tests
+- `test_webhook_signer.py` : Webhook HMAC signing
 
 ### Web Frontend (`web/`)
 
 **Design system:** OKLCH color space with 5 themes (light, dark, midnight, forest, sunset). Typography: Archivo (display/headings), Albert Sans (body), JetBrains Mono (code). 4pt base spacing scale. Motion tokens for animations. Defined in `globals.css`.
 
-Three route groups organize the UI by access level:
+Four route groups organize the UI by access level:
 
 **`(auth)/`** - Login and initialization
 - `login/page.tsx` : Email/name login and first-run admin init
@@ -206,34 +283,43 @@ Three route groups organize the UI by access level:
 
 **`(admin)/`** - Admin dashboard (requires admin role)
 - `dashboard/page.tsx` : Overview stats, recent agents, latest traces
-- `traces/page.tsx` : Trace list with filtering
-- `traces/[id]/page.tsx` : Trace detail with resizable span tree + JSON viewer
-- `review/page.tsx` : Admin review queue
+- `review/page.tsx` : Admin review queue with detail sheet
 - `users/page.tsx` : User management
 - `settings/page.tsx` : Enterprise settings
 - `eval/page.tsx` : Eval overview with agent scores
 - `eval/[agentId]/page.tsx` : Eval detail with aggregate chart, dimension radar, penalty accordion
+- `errors/page.tsx` : Error log viewer
+
+**`(user)/`** - User-scoped views (requires auth)
+- `traces/page.tsx` : User trace list with filtering
+- `traces/[id]/page.tsx` : Trace detail with resizable span tree + JSON viewer
 
 **Shared components:**
 - `src/lib/api.ts` : Typed fetch wrapper; all REST + GraphQL calls; auth via localStorage API key
 - `src/lib/types.ts` : Shared TypeScript interfaces for all API responses
 - `src/hooks/use-api.ts` : TanStack Query hooks for every endpoint (queries + mutations)
 - `src/hooks/use-auth.ts` : Auth guard hook (checks API key exists)
 - `src/hooks/use-admin-guard.ts` : Admin role check hook
+- `src/hooks/use-role-guard.ts` : Generic role check hook
+- `src/hooks/use-deployment-config.ts` : Deployment config fetcher (endpoint discovery)
 - `src/hooks/use-mobile.ts` : Mobile viewport detection
 - `src/components/layouts/auth-guard.tsx` : Auth guard wrapper
 - `src/components/layouts/admin-guard.tsx` : Admin guard wrapper
+- `src/components/layouts/role-guard.tsx` : Generic role guard wrapper
 - `src/components/layouts/dashboard-shell.tsx` : Dashboard layout shell
 - `src/components/layouts/page-header.tsx` : Page header with breadcrumbs
 - `src/components/nav/registry-sidebar.tsx` : Unified sidebar with conditional admin section
 - `src/components/nav/command-menu.tsx` : Command palette (Cmd+K)
 - `src/components/nav/nav-user.tsx` : User profile menu
+- `src/components/nav/github-star-banner.tsx` : GitHub star call-to-action banner
 - `src/components/shared/skeleton-layouts.tsx` : Reusable skeletons (TableSkeleton, CardSkeleton, DetailSkeleton, ChartSkeleton)
 - `src/components/shared/error-state.tsx` : Reusable error display with retry
 - `src/components/shared/empty-state.tsx` : Icon + title + description + CTA
+- `src/components/builder/` : Agent builder components (preview panel, sortable component list, validation panel)
 - `src/components/dashboard/` : Stat cards, trend charts, bar lists, heatmap, time range select, no-data/error states
 - `src/components/traces/` : Trace list, trace detail, span tree with collapsible thread lines
-- `src/components/registry/` : Agent card, component card, pull command with IDE selector, install dialog, metrics panel, feedback list, status badge
+- `src/components/registry/` : Agent card, component card, pull command with IDE selector, install dialog, metrics panel, feedback list, status badge, submit component dialog, registry detail, registry table
+- `src/components/review/` : Review detail sheet, validation badges
 - `src/components/eval/` : Eval-specific components
 
 ### Demo (`demo/`)
@@ -266,19 +352,21 @@ NEVER guess or hallucinate library APIs. Lookup docs first to ensure code matche
 - ClickHouse uses ReplacingMergeTree with bloom filter indexes. Queries go through the HTTP interface, not a native driver. The `_query` helper in `clickhouse.py` handles parameterized queries.
 - The shim is the core telemetry collection mechanism. It sits between the IDE and the MCP server, completely transparent. It never modifies messages: only observes. Telemetry is fire-and-forget via async POST; if the server is down, spans are silently dropped.
 - Config generators automatically wrap MCP commands with `observal-shim` for stdio transport or point to `observal-proxy` for HTTP transport. This is how telemetry collection is opt-in per install.
-- The `observal scan` command reads existing IDE config files, bulk-registers found MCP servers via `POST /api/v1/scan`, and rewrites configs to wrap commands with `observal-shim`. It creates timestamped backups before modifying any file. HTTP-transport MCPs are registered but not shimmed (they would need `observal-proxy`).
+- The `observal scan` command reads existing IDE config files, bulk-registers found MCP servers via `POST /api/v1/scan`, and rewrites configs to wrap commands with `observal-shim`. It creates timestamped backups before modifying any file. HTTP-transport MCPs are registered but not shimmed (they would need `observal-proxy`). Supports Claude Code, Cursor, Kiro, VS Code, Gemini CLI, and Codex CLI. Auto-detects home dirs when project dir is empty.
 - GraphQL is the read layer for telemetry data. REST still exists for auth, CRUD, feedback, eval, admin. The GraphQL layer uses DataLoaders to batch ClickHouse queries.
 - Redis serves two purposes: pub/sub for GraphQL subscriptions (live trace/span events) and arq job queue for background eval runs.
 - The eval engine is pluggable. `LLMJudgeBackend` calls Bedrock or OpenAI-compatible endpoints. `FallbackBackend` returns deterministic scores when no LLM is configured. The 6 managed templates are prompt strings, not code.
 - Feedback dual-writes: when a user rates an MCP/agent, it writes to PostgreSQL (for the feedback API) AND ClickHouse scores table (for unified analytics). The ClickHouse write is best-effort.
-- Auth is API key based. Keys are SHA-256 hashed before storage. The `X-API-Key` header is checked on every authenticated request via `get_current_user` dependency. User onboarding uses self-registration (`observal auth register`) or SSO. Fresh servers auto-bootstrap an admin account on first `observal auth login` (zero prompts, localhost-only). The `/health` endpoint returns `initialized: bool` so the CLI knows whether to bootstrap or prompt for credentials. All auth endpoints are rate-limited via slowapi (backed by Redis). OAuth uses a one-time auth code exchange pattern: the callback stores credentials in Redis with a 30s TTL and redirects with an opaque code instead of the raw API key.
+- Auth is API key based. Keys are SHA-256 hashed before storage. The `X-API-Key` header is checked on every authenticated request via `get_current_user` dependency. User onboarding uses self-registration (`observal auth register`) or SSO. Fresh servers auto-bootstrap an admin account on first `observal auth login` (zero prompts, localhost-only). The `/health` endpoint returns `initialized: bool` so the CLI knows whether to bootstrap or prompt for credentials. All auth endpoints are rate-limited via slowapi (backed by Redis). OAuth uses a one-time auth code exchange pattern: the callback stores credentials in Redis with a 30s TTL and redirects with an opaque code instead of the raw API key. JWT signing and verification available via `jwt_service.py` with JWKS endpoint for public key distribution.
 - Install routes use an owner fallback: try approved first, then allow the submitter to install their own pending/rejected items. This lets `observal scan` work. Items are auto-registered as pending and immediately usable by the submitter.
 - The CLI stores config in `~/.observal/config.json`. Aliases are in `~/.observal/aliases.json`. Both are plain JSON. All API path parameters accept UUID or name; the server resolves names via `resolve_listing()` in `deps.py`.
 - All CLI list/show commands support `--output table|json|plain`. Use `--output json` for scripting. Use `--raw` on install commands to pipe config directly to files.
-- The CLI uses nested Typer subgroups: `auth`, `registry` (mcp/skill/hook/prompt/sandbox), `agent`, `ops` (telemetry), `admin` (review/eval), `self`, `config`, `doctor`. Root-level convenience commands: `pull`, `scan`, `uninstall`, `use`, `profile`.
+- The CLI uses nested Typer subgroups: `auth`, `registry` (mcp/skill/hook/prompt/sandbox), `agent`, `ops` (telemetry), `admin` (review/eval), `self`, `config`, `doctor`, `migrate`. Root-level convenience commands: `pull`, `scan`, `uninstall`, `use`, `profile`.
 - Ruff is the Python linter and formatter. Line length is 120. Pre-commit hooks enforce it.
 - The `B008` ruff rule is suppressed because Typer requires function calls in argument defaults (`typer.Option(...)`, `typer.Argument(...)`).
 - The data model is agent-centric. Agents bundle components (MCPs, skills, hooks, prompts, sandboxes) via `agent_components`, a polymorphic junction table with NO foreign key on `component_id` (allows cross-type references). Agent downloads are deduplicated by `(user_id)` and `(fingerprint)` unique constraints; component downloads are not deduplicated. All components support organization ownership via `is_private` + `owner_org_id` fields. Git-based versioning: components require `git_url` + `git_ref` for reproducible installs.
 - The web frontend uses OKLCH color space for perceptually uniform theming. 5 themes are defined in `globals.css` using CSS custom properties. Theme switching is handled by `theme-switcher.tsx`. The design system uses a 4pt spacing scale, semantic color tokens (background, foreground, card, border, primary, secondary, accent, destructive, success, warning, info), and motion tokens for animations.
-- The web frontend proxies all API calls through Next.js rewrites (`/api/v1/*` -> backend). The backend URL is configured via `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`). Auth state (API key, user role) is stored in localStorage. Role-based access is enforced client-side via AuthGuard and AdminGuard components, not Next.js middleware.
-
+- The web frontend proxies all API calls through Next.js rewrites (`/api/v1/*` -> backend). The backend URL is configured via `NEXT_PUBLIC_API_URL` env var (defaults to `http://localhost:8000`). Auth state (API key, user role) is stored in localStorage. Role-based access is enforced client-side via AuthGuard, AdminGuard, and RoleGuard components, not Next.js middleware.
+- Alert rules support metric threshold monitoring with webhook delivery. The `alert_evaluator.py` service runs periodic checks against ClickHouse metrics and fires webhooks (with HMAC signing via `webhook_signer.py` and delivery retries via `webhook_delivery.py`) when thresholds are breached. SSRF protection prevents webhooks to private IP ranges.
+- Telemetry data is scrubbed by `secrets_redactor.py` before ClickHouse storage. Security events are logged via `security_events.py` for audit trails.
+- Server endpoint discovery (`api/routes/config.py`) eliminates hardcoded URLs — clients derive endpoints from server config at runtime.
diff --git a/ee/AGENTS.md b/ee/AGENTS.md
@@ -0,0 +1,88 @@
+# Enterprise Edition
+
+Source-available enterprise features for Observal. Loaded only when `DEPLOYMENT_MODE=enterprise`.
+
+**License:** Separate enterprise license (`ee/LICENSE`). Commercial license required for production. Community contributions NOT accepted into this directory.
+
+**Critical constraint:** Core must NEVER import from `ee/`. Dependency is strictly one-way: `ee/` imports core, never the reverse. The open-source edition must be fully functional without `ee/`.
+
+## How it loads
+
+`observal-server/main.py` calls `register_enterprise(app, settings)` from `ee/__init__.py` which:
+
+1. Validates enterprise config via `config_validator.py`
+2. Mounts EE routes (`/api/v1/sso/saml/*`, `/api/v1/scim/*`, `/api/v1/admin/audit-log*`)
+3. Adds `EnterpriseGuardMiddleware` (returns 503 on EE routes if config is invalid)
+4. Registers audit event bus handlers on `services.events.bus`
+5. Stores config issues in `app.state.enterprise_issues`
+
+## Config validation
+
+Five settings checked on startup. If any fail, issues are stored and the guard middleware blocks EE routes with 503.
+
+| Setting | Requirement |
+|---------|------------|
+| `SECRET_KEY` | Not the default `"change-me-to-a-random-string"` |
+| `OAUTH_CLIENT_ID` | Must be set |
+| `OAUTH_CLIENT_SECRET` | Must be set |
+| `OAUTH_SERVER_METADATA_URL` | Must be set (OIDC discovery) |
+| `FRONTEND_URL` | Not localhost or empty |
+
+## Features
+
+### Audit logging (implemented)
+
+Listens to 8 event types on the core event bus (`services/events.py`):
+- `UserCreated`, `UserDeleted`
+- `LoginSuccess`, `LoginFailure`
+- `RoleChanged`, `SettingsChanged`
+- `AlertRuleChanged`, `AgentLifecycleEvent`
+
+Each event → row in ClickHouse `audit_log` table with actor info, resource details, HTTP metadata, and freeform detail JSON.
+
+**API endpoints (admin-only):**
+- `GET /api/v1/admin/audit-log` — query with filters (actor, action, resource_type, date range), paginated
+- `GET /api/v1/admin/audit-log/export` — CSV download (max 10k rows)
+
+### SAML 2.0 SSO (stub — returns 501)
+
+- `POST /api/v1/sso/saml/login` — initiate SAML login
+- `POST /api/v1/sso/saml/acs` — Assertion Consumer Service callback
+- `GET /api/v1/sso/saml/metadata` — SP metadata
+
+### SCIM 2.0 provisioning (stub — returns 501)
+
+- `GET /api/v1/scim/Users` — list users
+- `POST /api/v1/scim/Users` — create user
+- `GET /api/v1/scim/Users/{user_id}` — get user
+- `PUT /api/v1/scim/Users/{user_id}` — update user
+- `DELETE /api/v1/scim/Users/{user_id}` — delete user
+
+### Plugin registry (placeholder)
+
+`ee/plugins/__init__.py` — future home for Grafana, Prometheus, Datadog, and SIEM integrations.
+
+## Directory layout
+
+```
+ee/
+├── __init__.py                         # register_enterprise() entrypoint
+├── LICENSE                             # Enterprise license
+├── AGENTS.md                           # This file
+├── README.md                           # Public-facing description
+├── docs/
+│   └── cli.md                          # EE configuration reference
+├── observal_server/
+│   ├── middleware/
+│   │   └── enterprise_guard.py         # 503 guard for misconfigured EE routes
+│   ├── routes/
+│   │   ├── __init__.py                 # mount_ee_routes() — mounts all EE routers
+│   │   ├── audit.py                    # Audit log query + CSV export
+│   │   ├── scim.py                     # SCIM 2.0 stubs
+│   │   └── sso_saml.py                # SAML 2.0 stubs
+│   └── services/
+│       ├── audit.py                    # Event bus handlers → ClickHouse audit_log writes
+│       └── config_validator.py         # Startup config validation
+└── plugins/
+    └── __init__.py                     # Future integrations placeholder
+```
diff --git a/web/AGENTS.md b/web/AGENTS.md
@@ -1,5 +1,88 @@
-<!-- BEGIN:nextjs-agent-rules -->
-# This is NOT the Next.js you know
+# Web Frontend
 
-This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
-<!-- END:nextjs-agent-rules -->
+Next.js 16 / React 19 / TypeScript 6 / Tailwind CSS 4 / Playwright 1.59
+
+## Stack
+
+- **Framework:** Next.js 16 with `output: "standalone"` for Docker
+- **UI:** shadcn/ui (`src/components/ui/`), Recharts 3 for charts, TanStack Query for data fetching, TanStack Table for sortable/filterable tables
+- **Design system:** OKLCH color space with 5 themes (light, dark, midnight, forest, sunset). Typography: Archivo (display), Albert Sans (body), JetBrains Mono (code). 4pt spacing scale. Defined in `globals.css`.
+- **API proxy:** Next.js rewrites (`/api/v1/*` → backend). Backend URL via `NEXT_PUBLIC_API_URL` (defaults `http://localhost:8000`).
+- **Auth:** API key + user role in localStorage. Client-side guards (AuthGuard, AdminGuard, RoleGuard), not middleware.
+- **GraphQL:** `/api/v1/graphql` is the read layer for telemetry. REST for everything else. WebSocket subscriptions via `src/lib/graphql-ws.ts`.
+
+## Route groups
+
+```
+src/app/
+├── (auth)/login/               # Login + first-run admin init
+├── (registry)/                 # Public agent browser (requires auth)
+│   ├── page.tsx                #   Registry home (search, trending, top rated)
+│   ├── agents/page.tsx         #   Agent list with search + filters
+│   ├── agents/[id]/page.tsx    #   Agent detail with pull command box
+│   ├── agents/builder/page.tsx #   Agent builder (two-column, component selector, YAML preview)
+│   ├── agents/leaderboard/     #   Agent leaderboard
+│   ├── components/page.tsx     #   Tabbed component browser (MCPs, skills, hooks, prompts, sandboxes)
+│   └── components/[id]/page.tsx#   Component detail
+├── (admin)/                    # Admin dashboard (requires admin role)
+│   ├── dashboard/page.tsx      #   Overview stats, recent agents, latest traces
+│   ├── review/page.tsx         #   Review queue with detail sheet
+│   ├── users/page.tsx          #   User management
+│   ├── settings/page.tsx       #   Enterprise settings
+│   ├── eval/page.tsx           #   Eval overview with agent scores
+│   ├── eval/[agentId]/page.tsx #   Eval detail (aggregate chart, dimension radar, penalty accordion)
+│   └── errors/page.tsx         #   Error log viewer
+└── (user)/                     # User-scoped views (requires auth)
+    ├── traces/page.tsx         #   User trace list with filtering
+    └── traces/[id]/page.tsx    #   Trace detail (resizable span tree + JSON viewer)
+```
+
+## Component directories
+
+```
+src/components/
+├── builder/       # Agent builder (preview panel, sortable component list, validation panel)
+├── dashboard/     # Stat cards, trend charts, bar lists, heatmap, time range select
+├── layouts/       # AuthGuard, AdminGuard, RoleGuard, DashboardShell, PageHeader
+├── nav/           # RegistrySidebar, CommandMenu (Cmd+K), NavUser, GitHubStarBanner
+├── registry/      # AgentCard, ComponentCard, PullCommand, InstallDialog, StatusBadge, SubmitComponentDialog, RegistryTable, RegistryDetail, ReviewForm
+├── review/        # ReviewDetailSheet, ValidationBadges
+├── shared/        # SkeletonLayouts, ErrorState, EmptyState
+├── traces/        # TraceList, TraceDetail, SpanTree
+└── ui/            # shadcn/ui primitives (27 components)
+```
+
+## Key files
+
+- `src/lib/api.ts` : Typed fetch wrapper; all REST + GraphQL calls; auth via localStorage
+- `src/lib/types.ts` : Shared TypeScript interfaces for all API responses
+- `src/lib/graphql-ws.ts` : GraphQL WebSocket subscription client
+- `src/lib/ide-features.ts` : IDE feature detection utilities
+- `src/lib/query-client.ts` : TanStack Query client configuration
+- `src/lib/utils.ts` : Shared utility functions
+- `src/lib/export.ts` : Data export utilities
+- `src/hooks/use-api.ts` : TanStack Query hooks for every endpoint (queries + mutations)
+- `src/hooks/use-auth.ts` : Auth guard hook (checks API key exists)
+- `src/hooks/use-admin-guard.ts` : Admin role check hook
+- `src/hooks/use-role-guard.ts` : Generic role check hook
+- `src/hooks/use-deployment-config.ts` : Deployment config fetcher (endpoint discovery)
+- `src/hooks/use-mobile.ts` : Mobile viewport detection
+- `next.config.ts` : API rewrites, standalone output
+- `playwright.config.ts` : E2E test config (Chromium, port 3000)
+
+## Commands
+
+```bash
+pnpm dev          # dev server on :3000
+pnpm build        # production build
+pnpm lint         # ESLint
+pnpm test:e2e     # Playwright e2e tests (requires running API + Docker stack)
+```
+
+## Conventions
+
+- No Tailwind config file — Tailwind CSS 4 uses `globals.css` for all design tokens
+- Theme switching via `src/components/ui/theme-switcher.tsx`
+- All API response types are centralized in `src/lib/types.ts` — don't define inline types for API data
+- Use TanStack Query hooks from `src/hooks/use-api.ts` for data fetching — don't call `fetch` directly in components
+- Semantic color tokens: background, foreground, card, border, primary, secondary, accent, destructive, success, warning, info
PATCH

echo "Gold patch applied."
