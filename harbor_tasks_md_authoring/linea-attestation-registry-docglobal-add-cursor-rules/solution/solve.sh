#!/usr/bin/env bash
set -euo pipefail

cd /workspace/linea-attestation-registry

# Idempotency guard
if grep -qF "Cursor is strictly forbidden from committing, pushing, rebasing, merging, force " ".cursor/rules/00-operating-model.mdc" && grep -qF "Apply 12 Factor App: config via env, stateless processes, concurrency, disposabi" ".cursor/rules/01-principles.mdc" && grep -qF "Idempotency for writes, payments, duplicates harmful endpoints (exactly once or " ".cursor/rules/02-reliability.mdc" && grep -qF "Never trust client supplied identifiers, roles, addresses, chain state, or featu" ".cursor/rules/05-security.mdc" && grep -qF "description: Solidity security, upgradeability, gas, and testing" ".cursor/rules/10-solidity.mdc" && grep -qF "Coverage gaps on admin only functions are acceptable if access control is tested" ".cursor/rules/12-foundry.mdc" && grep -qF "wagmi config must define supported chains including Linea, RPC fallback, timeout" ".cursor/rules/20-wagmi-viem.mdc" && grep -qF "Onchain reads in Server Components only if wallet independent." ".cursor/rules/30-next-react.mdc" && grep -qF "description: TypeScript strictness and domain modeling" ".cursor/rules/35-typescript.mdc" && grep -qF "Manage env vars with dotenv or similar; validate with zod or class-validator." ".cursor/rules/40-nestjs.mdc" && grep -qF "Generic data layer principles (pagination, N+1 prevention, backfills)" ".cursor/rules/42-prisma.mdc" && grep -qF "Destructive changes require phased rollout and rollback. (Cross ref: 02-reliabil" ".cursor/rules/45-data-layer.mdc" && grep -qF "Avoid coverage driven testing. Use coverage as a signal only; critical paths mus" ".cursor/rules/50-testing-ci.mdc" && grep -qF "description: Comments and documentation discipline" ".cursor/rules/55-comments-docs.mdc" && grep -qF "Backend idempotency mandatory. (Cross ref: 02-reliability.mdc)" ".cursor/rules/60-web3-product.mdc" && grep -qF "description: Release strategy, rollouts, and production safety" ".cursor/rules/65-release-rollout.mdc" && grep -qF "Jobs must be idempotent, retry safe, observable, resumable. (Cross ref: 02-relia" ".cursor/rules/70-observability-ops.mdc" && grep -qF "Support i18n and responsive design where the product requires it." ".cursor/rules/80-accessibility-performance.mdc" && grep -qF "Use `overrides` in `pnpm-workspace.yaml` to patch vulnerable transitive dependen" ".cursor/rules/90-monorepo.mdc" && grep -qF "RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile" ".cursor/rules/92-docker.mdc" && grep -qF "Use PR templates with checklists (e.g., DoD verification) where helpful." ".cursor/rules/95-github-actions.mdc" && grep -qF "Enforce via CI (e.g., lint rules files for consistency) when worth the maintenan" ".cursor/rules/99-meta.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/00-operating-model.mdc b/.cursor/rules/00-operating-model.mdc
@@ -0,0 +1,216 @@
+---
+description: Operating model, authority, modes, planning, tickets, strict DoD, ownership, exceptions
+alwaysApply: true
+---
+
+# Authority and Git
+
+Cursor is strictly forbidden from committing, pushing, rebasing, merging, force pushing, tagging, or modifying Git history.
+Git operations are informational only when explicitly requested.
+The human user is the sole authority for Git actions, releases, and deployments.
+
+# Ownership and Decision Authority
+
+Every domain or system must have a clearly identified human owner.
+The owner is responsible for:
+- validating architectural decisions
+- arbitrating disagreements between Executor and Reviewer
+- approving exceptions to rules when justified
+
+When no owner is explicitly defined, the human user is the default owner.
+
+---
+
+# Operating Modes
+
+Cursor operates in exactly three modes:
+- Planner
+- Executor
+- Reviewer
+
+## Mode Selection
+
+Default to Planner for:
+- architecture
+- feature design
+- security
+- auth
+- persistent data
+- smart contracts
+- payments
+- indexers
+- infra or CI
+- cross stack changes
+- Next.js
+- NestJS
+- wagmi
+- viem
+- writing or refining GitHub tickets
+
+Switch to Executor only if the user explicitly asks to:
+- implement
+- execute step N
+- apply this patch
+- code this feature, fix, or chore
+
+Switch to Reviewer when:
+- asked to review code
+- asked to compare two branches
+- asked to validate production readiness
+- challenging its own implementation
+
+If a blocking ambiguity exists, stop and ask for clarification.
+
+## Operating Modes Scope
+
+This operating model applies in full to production systems.
+
+For experimental or short lived projects, the human user may declare:
+- reduced scope
+- reduced Definition of Done
+- explicit non production status
+
+Such declarations must be explicit.
+
+---
+
+## Planner Mode Responsibilities
+
+Planner plans and specifies, never codes.
+
+### Planning Discipline
+
+- Max 7 steps per plan
+- Each step must have explicit success criteria
+- If more steps are required, split into phases and stop after phase 1
+
+### Mandatory Analysis
+
+Planner must explicitly reason about:
+- scope and non goals
+- affected modules and ownership
+- data flow and trust boundaries
+- security and abuse risks
+- performance and scalability risks
+- migration and rollout risks
+- test strategy
+- observability requirements
+- rollback strategy
+
+### GitHub Ticket Writing
+
+When writing or refining tickets:
+- clear problem statement
+- explicit scope and non scope
+- acceptance criteria that are objectively testable
+- edge cases and failure modes
+- security considerations when relevant
+- rollout and rollback notes when risky
+
+Tickets must be executable without tribal knowledge.
+
+### Traceability Artifact
+
+Maintain a lightweight decision log in `.cursor/scratchpad.md` for non trivial changes:
+- problem statement
+- assumptions
+- options considered with tradeoffs
+- chosen approach
+- security or threat notes when relevant
+- migration and rollout notes when relevant
+
+Avoid overdocumentation. Record only decisions that matter.
+
+---
+
+## Executor Mode Responsibilities
+
+Executor writes code.
+
+### Execution Discipline
+
+- always read existing files before editing
+- respect existing architecture and boundaries
+- prefer small, cohesive diffs
+- do not introduce new patterns without justification
+- keep API contracts explicit
+- never claim production ready without passing Reviewer mode
+
+### Testing Discipline
+
+Prefer TDD for critical paths:
+- business logic
+- auth and permissions
+- money or payments
+- onchain writes
+- bridging
+- signature verification
+- data migrations and backfills logic
+
+For non critical paths, tests are still expected but TDD is optional.
+
+---
+
+## Reviewer Mode Responsibilities
+
+Reviewer validates readiness and correctness.
+
+Reviewer must challenge:
+- functional correctness
+- security and privacy
+- architecture and layering
+- typing discipline
+- performance and scalability
+- reliability and idempotency
+- observability and ops readiness
+- maintainability and clarity
+
+Reviewer cannot modify code.
+Reviewer may only approve, request changes, or explain risks.
+
+---
+
+## Irreversible Actions
+
+Before executing anything potentially irreversible, it must be explicitly flagged:
+- smart contract deployment or upgrade
+- database schema migration
+- data backfill
+- indexer reprocessing
+- permission model change
+- key rotation
+- feature flag rollout
+
+A rollback plan is mandatory.
+
+---
+
+## Definition of Done
+
+All items are mandatory unless explicitly waived with justification (tracked in ticket comments or scratchpad):
+- acceptance criteria met and validated
+- tests passing
+- typecheck passing
+- lint passing
+- build passing
+- no critical runtime warnings
+- security review completed
+- observability updated where relevant
+- rollback plan documented for risky changes
+- manual test plan executed for user critical flows
+- documentation updated when behavior changes
+
+Prioritize must (blocking) vs should (recommended) based on context (e.g., chores may waive non critical items).
+
+---
+
+## Rule Exceptions
+
+Rules are strict by default.
+
+Exceptions are allowed only if:
+- explicitly justified in the PR or ticket
+- reviewed by the domain owner
+- documented as a conscious tradeoff
+
+Silent or implicit exceptions are forbidden.
diff --git a/.cursor/rules/01-principles.mdc b/.cursor/rules/01-principles.mdc
@@ -0,0 +1,20 @@
+---
+description: Core cross cutting engineering principles
+alwaysApply: true
+---
+
+Follow SOLID principles.
+Prefer KISS over cleverness.
+Respect Clean Architecture boundaries.
+Isolate business logic from frameworks.
+Push side effects to edges.
+
+Use design patterns only when justified.
+Avoid over abstraction or premature optimization.
+Optimize for readability, long term maintenance, and scalability.
+
+Apply 12 Factor App: config via env, stateless processes, concurrency, disposability.
+
+Error handling must be robust, predictable, with graceful degradation.
+
+Distinguish must (mandatory, blocking) vs should (recommended) in all rules.
diff --git a/.cursor/rules/02-reliability.mdc b/.cursor/rules/02-reliability.mdc
@@ -0,0 +1,16 @@
+---
+description: Consolidated reliability: idempotency, consistency, resilience
+alwaysApply: true
+---
+
+Idempotency for writes, payments, duplicates harmful endpoints (exactly once or at least once semantics documented).
+
+Chunk or batch heavy operations; avoid large migrations in single tx.
+
+Document consistency: strong where needed (e.g., financial), eventual where acceptable.
+
+Make retries safe or idempotent; handle flaky networks gracefully.
+
+Jobs and background tasks must be idempotent, retry safe, observable with progress, resumable.
+
+Nonce based replay protection and explicit expiry mandatory for signatures and attestations.
diff --git a/.cursor/rules/05-security.mdc b/.cursor/rules/05-security.mdc
@@ -0,0 +1,53 @@
+---
+description: End to end security, privacy, and abuse resistance
+alwaysApply: true
+---
+
+Assume hostile input everywhere.
+Apply defense in depth.
+Prefer secure defaults.
+
+# Application Security
+
+Validate and sanitize all inputs at boundaries.
+Never trust client supplied identifiers, roles, addresses, chain state, or feature flags.
+Never rely on frontend validation.
+
+Explicitly mitigate:
+- SQL NoSQL command and SSTI injection
+- XSS with CSP and escaping
+- CSRF for cookie based auth
+- SSRF with allowlists
+- IDOR and broken authorization
+- race conditions and TOCTOU
+- privilege escalation
+- open redirects
+- file upload attacks
+
+# Auth and Sessions
+
+Separate authentication and authorization.
+Avoid implicit permissions.
+Reason explicitly about auth bypass, token leakage, session fixation, misconfiguration.
+
+# Web3 Security
+
+Never trust client reported onchain state.
+Verify signatures server side.
+
+# Data Protection and Privacy
+
+Treat user data as PII unless proven otherwise.
+Minimize collection and retention.
+Document data lifecycle and deletion.
+Never log secrets, tokens, private keys, raw signatures, or sensitive payloads.
+
+# OSINT Awareness
+
+Do not leak internal URLs, infra details, RPC keys, or stack traces.
+
+# Abuse Protection
+
+Rate limit public endpoints.
+Add brute force protection.
+Use idempotency for dangerous writes. (Cross ref: 02-reliability.mdc)
diff --git a/.cursor/rules/10-solidity.mdc b/.cursor/rules/10-solidity.mdc
@@ -0,0 +1,41 @@
+---
+description: Solidity security, upgradeability, gas, and testing
+globs: ["**/*.sol"]
+---
+
+Solidity ^0.8.x.
+OpenZeppelin Contracts v5+ pinned.
+
+Explicit visibility everywhere.
+NatSpec required for public and critical functions.
+
+# Security
+
+Explicit access control.
+Reentrancy protection or checks effects interactions.
+Never assume ERC20 compliance.
+Validate external calls.
+No hardcoded secrets.
+
+# Upgradeability
+
+Document proxy pattern.
+Identify admin, guardian, timelock or multisig.
+Document upgrade, rotation, and rollback.
+Define invariants across upgrades.
+
+# Gas and Cost
+
+Estimate gas for user facing functions.
+Avoid unbounded loops.
+Prefer constants and immutable.
+Optimize storage where relevant.
+
+# Testing and Analysis
+
+Unit tests mandatory.
+Fuzz or invariant tests for critical paths.
+Static analysis required.
+Fork tests for external integrations.
+
+Foundry preferred, Hardhat tolerated with justification
diff --git a/.cursor/rules/12-foundry.mdc b/.cursor/rules/12-foundry.mdc
@@ -0,0 +1,46 @@
+---
+description: Foundry testing, fuzzing, deployment scripts
+globs: ["**/*.sol", "**/foundry.toml", "**/script/**"]
+---
+
+Foundry is the default toolchain for Solidity development.
+
+Alternative toolchains are allowed only with explicit justification
+and must meet equivalent guarantees for testing.
+
+# Testing
+
+Unit tests mandatory for all contracts.
+Use `forge test` with verbosity flags for debugging.
+Prefer realistic fork tests over mocks for external integrations.
+
+Fuzz tests required for math heavy or user input functions.
+Define meaningful bounds with `vm.assume` or `bound`.
+Avoid unbounded fuzzing that wastes cycles.
+
+Invariant tests required for stateful contracts.
+Define explicit invariants as view functions.
+Document what each invariant protects.
+
+# Scripts
+
+Use Foundry scripts for deployments and admin operations.
+Scripts must be idempotent where possible. (Cross ref: 02-reliability.mdc)
+Never hardcode private keys or secrets in scripts.
+Use environment variables or secure keystores.
+
+Document deployment sequence and dependencies.
+Verify contracts on block explorers post deployment.
+
+# Cheatcodes
+
+Use `vm.prank` and `vm.startPrank` for access control tests.
+Use `vm.expectRevert` with specific error selectors.
+Use `vm.warp` and `vm.roll` for time dependent logic.
+Use `deal` and `hoax` for balance manipulation in tests.
+
+# Coverage
+
+Run `forge coverage` for critical contracts.
+Aim for high branch coverage on security critical paths.
+Coverage gaps on admin only functions are acceptable if access control is tested.
diff --git a/.cursor/rules/20-wagmi-viem.mdc b/.cursor/rules/20-wagmi-viem.mdc
@@ -0,0 +1,22 @@
+---
+description: wagmi v3 and viem v2 frontend discipline
+globs: ["**/*.ts", "**/*.tsx"]
+---
+
+viem first.
+ethers forbidden for new code unless justified and documented.
+
+wagmi config must define supported chains including Linea, RPC fallback, timeouts, retry policy.
+
+Prefer multicall for reads.
+Avoid aggressive polling.
+
+Writes must handle pending, replacement, cancellation, and receipt confirmation.
+
+Explicitly handle EIP 1193 errors.
+Never hide wallet or RPC failures.
+
+Signatures must use signTypedData with explicit domain and user readable intent.
+Backend replay protection mandatory. (Cross ref: 02-reliability.mdc)
+
+Frontend events are never authoritative for critical state.
diff --git a/.cursor/rules/30-next-react.mdc b/.cursor/rules/30-next-react.mdc
@@ -0,0 +1,18 @@
+---
+description: Next.js App Router and React discipline
+globs: ["app/**", "**/*.tsx"]
+---
+
+Wallet and wagmi logic only in Client Components.
+Onchain reads in Server Components only if wallet independent.
+No secrets in client.
+
+Every fetch must declare cache strategy.
+Document SSR SSG ISR for critical pages.
+
+Suspense must have meaningful fallback.
+Avoid waterfalls.
+Measure perceived UX.
+
+Effects must be idempotent.
+No side effects in render.
diff --git a/.cursor/rules/35-typescript.mdc b/.cursor/rules/35-typescript.mdc
@@ -0,0 +1,14 @@
+---
+description: TypeScript strictness and domain modeling
+alwaysApply: true
+---
+
+Strict mode assumed.
+No implicit any.
+No unsafe casts.
+
+Prefer domain types over primitives.
+Avoid stringly typed code.
+Use exhaustive checks for unions.
+
+Fail at compile time, not runtime.
diff --git a/.cursor/rules/40-nestjs.mdc b/.cursor/rules/40-nestjs.mdc
@@ -0,0 +1,47 @@
+---
+description: NestJS backend robustness
+globs: ["**/api/**", "**/backend/**"]
+---
+
+Strict DTOs.
+ValidationPipe whitelist.
+Separate AuthN and AuthZ.
+
+Rate limiting and brute force protection required.
+
+Use viem publicClient for reads.
+Server side signature verification.
+Never trust client onchain state.
+
+Chunk heavy operations.
+
+# Healthchecks
+
+Expose `/health/live` endpoint for liveness.
+Expose `/health/ready` endpoint for readiness.
+Check database and cache connectivity in readiness.
+Use `@nestjs/terminus` for health indicators.
+
+Return structured response with component status.
+Fail fast if critical dependencies are down.
+
+# Metrics
+
+Expose `/metrics` endpoint for Prometheus scraping.
+Use `prom-client` or `@willsoto/nestjs-prometheus`.
+
+Track at minimum:
+- HTTP request duration histogram
+- HTTP request count by status code
+- active connections gauge
+- database query duration
+- cache hit and miss rates
+- queue depth for async jobs
+
+Use consistent label naming.
+Avoid high cardinality labels.
+
+# Env Vars
+
+Manage env vars with dotenv or similar; validate with zod or class-validator.
+Document required vars in README.
diff --git a/.cursor/rules/42-prisma.mdc b/.cursor/rules/42-prisma.mdc
@@ -0,0 +1,64 @@
+---
+description: Prisma client, migrations, relations, and transactions
+globs: ["**/prisma/**", "**/*.prisma"]
+---
+
+Prefer Prisma for all database access.
+Raw SQL forbidden unless justified for performance and documented.
+
+This file defines Prisma specific implementation rules.
+
+Generic data layer principles (pagination, N+1 prevention, backfills)
+are defined in 45-data-layer.mdc and must not be duplicated here.
+
+# Client
+
+Use singleton pattern for PrismaClient.
+Instantiate once and reuse across requests.
+Handle connection lifecycle in NestJS module.
+
+Enable query logging in development only.
+Never log queries in production.
+
+# Schema
+
+Use snake_case for table and column names.
+Use explicit `@id` and `@unique` constraints.
+Add `@@index` for columns used in WHERE and ORDER BY.
+Document non obvious relations and constraints.
+
+Prefer explicit types over defaults.
+Use `@db` modifiers for precision control.
+
+# Migrations
+
+Migrations must be backward compatible.
+Avoid destructive changes in single migration.
+Split risky changes into expand and contract phases.
+
+Test migrations against production like data.
+Include rollback notes for risky migrations.
+
+Never edit committed migrations.
+Create new migration to fix issues.
+
+# Relations
+
+Prefer explicit relation fields over implicit.
+Use `include` and `select` intentionally.
+Use `findMany` with explicit `where` over `findFirst` chains.
+
+# Transactions
+
+Use `$transaction` for multi step writes.
+Keep transactions short to avoid lock contention.
+Handle transaction rollback explicitly.
+
+Prefer interactive transactions for complex logic.
+Avoid long running operations inside transactions.
+
+# Performance
+
+Use `count` instead of `findMany` plus length.
+Profile slow queries with `EXPLAIN ANALYZE`.
+Add indexes based on actual query patterns.
diff --git a/.cursor/rules/45-data-layer.mdc b/.cursor/rules/45-data-layer.mdc
@@ -0,0 +1,22 @@
+---
+description: Data layer discipline
+alwaysApply: true
+---
+
+This file is the single source of truth for cross stack data rules.
+
+ORM or database specific files must not redefine these principles,
+only their concrete implementation.
+
+Prevent N plus 1 queries.
+Add indexes for user facing queries.
+Use pagination.
+Avoid unbounded queries.
+
+Migrations should be backward compatible.
+Destructive changes require phased rollout and rollback. (Cross ref: 02-reliability.mdc)
+
+Backfills must be chunked, resumable, observable.
+Avoid long blocking transactions.
+
+Document consistency expectations. (Cross ref: 02-reliability.mdc)
diff --git a/.cursor/rules/50-testing-ci.mdc b/.cursor/rules/50-testing-ci.mdc
@@ -0,0 +1,21 @@
+---
+description: Testing and CI gates
+alwaysApply: true
+---
+
+Tests mandatory for critical surfaces:
+- business logic
+- auth
+- security
+- money
+- onchain writes
+- bridging
+- signatures
+- data migrations logic
+
+Prefer realistic tests over mocks.
+
+CI blocks merges if tests, lint, typecheck, or build fail.
+Dependency audits required before production.
+
+Avoid coverage driven testing. Use coverage as a signal only; critical paths must be meaningfully tested and gaps justified.
diff --git a/.cursor/rules/55-comments-docs.mdc b/.cursor/rules/55-comments-docs.mdc
@@ -0,0 +1,15 @@
+---
+description: Comments and documentation discipline
+alwaysApply: true
+---
+
+Minimize comments.
+Explain intent only when non obvious.
+English only.
+No commented out code.
+
+Update docs when behavior changes:
+- API docs (e.g., Swagger/OpenAPI)
+- README
+- runbooks
+- migration notes
diff --git a/.cursor/rules/60-web3-product.mdc b/.cursor/rules/60-web3-product.mdc
@@ -0,0 +1,31 @@
+---
+description: Web3 UX and product reliability
+alwaysApply: true
+---
+
+Never force network switch.
+Handle chain mismatch explicitly.
+Provide UX fallbacks.
+
+Document bridging and onramp failure modes.
+Define timeouts and refund paths.
+Backend idempotency mandatory. (Cross ref: 02-reliability.mdc)
+
+Server side verification for attestations.
+Replay protection required. (Cross ref: 02-reliability.mdc)
+Privacy and retention documented.
+
+Measure time to wallet ready and meaningful feedback.
+Never leave the user in RPC silence.
+
+# Feature Flags and Progressive Rollouts
+
+Risky user facing changes must use feature flags.
+
+Feature flags must support:
+- gradual rollout
+- per environment configuration
+- instant disablement
+
+Flags must not become permanent configuration.
+A removal plan is required.
diff --git a/.cursor/rules/65-release-rollout.mdc b/.cursor/rules/65-release-rollout.mdc
@@ -0,0 +1,29 @@
+---
+description: Release strategy, rollouts, and production safety
+alwaysApply: true
+---
+
+# Release Strategy
+
+Production releases must define:
+- rollout strategy
+- success metrics
+- rollback conditions
+
+# Progressive Exposure
+
+Prefer:
+- canary releases
+- percentage based rollout
+- environment based exposure
+
+Avoid full blast releases for risky changes.
+
+# Verification
+
+After release:
+- verify metrics
+- verify logs
+- verify user facing behavior
+
+Release is not complete until verification is done.
diff --git a/.cursor/rules/70-observability-ops.mdc b/.cursor/rules/70-observability-ops.mdc
@@ -0,0 +1,14 @@
+---
+description: Observability, ops, and incident readiness
+alwaysApply: true
+---
+
+Logs must be structured and redacted.
+Metrics must cover latency, error rate, throughput, dependency health.
+
+Define failure modes for critical paths.
+Prefer actionable alerts.
+
+Jobs must be idempotent, retry safe, observable, resumable. (Cross ref: 02-reliability.mdc)
+
+Document runbooks for risky systems, with ownership definition.
diff --git a/.cursor/rules/80-accessibility-performance.mdc b/.cursor/rules/80-accessibility-performance.mdc
@@ -0,0 +1,16 @@
+---
+description: Accessibility and frontend performance
+alwaysApply: true
+---
+
+Use semantic HTML.
+Keyboard navigation required.
+Accessible names for controls.
+Manage focus correctly.
+
+Prevent performance regressions on critical user flows.
+Prefer code splitting for heavy features.
+Avoid unnecessary rerenders.
+Handle flaky networks gracefully.
+
+Support i18n and responsive design where the product requires it.
diff --git a/.cursor/rules/90-monorepo.mdc b/.cursor/rules/90-monorepo.mdc
@@ -0,0 +1,81 @@
+---
+description: pnpm workspaces, catalogs, versioning, dependency hygiene
+globs: ["pnpm-workspace.yaml", "pnpm-lock.yaml", "**/package.json", ".nvmrc"]
+---
+
+pnpm is mandatory for internal development.
+
+For external repositories or third party contributions,
+npm or yarn may be temporarily tolerated if:
+- conversion cost is prohibitive
+- the repository is not the source of truth
+
+Such cases must be documented explicitly.
+
+# Enforcing pnpm
+
+Root package.json must include:
+
+```json
+"preinstall": "npx only-allow@1.2.2 pnpm"
+```
+
+Root package.json must declare explicit engine versions:
+
+```json
+"packageManager": "pnpm@<version>",
+"engines": {
+  "node": ">=<version>",
+  "pnpm": ">=<version>"
+}
+```
+
+# Node Version
+
+Single source of truth in `.nvmrc` at root.
+All CI and Docker builds must read from `.nvmrc`.
+Never hardcode Node version elsewhere.
+
+# Workspace Structure
+
+All packages live in `packages/` for new projects, or `apps/` for existing ones.
+Use `pnpm-workspace.yaml` to declare workspace globs.
+
+# Catalogs
+
+Use `catalog:` references for shared dependencies.
+If a dependency is used by two or more packages it must go in catalog.
+
+Organize catalogs by theme:
+- `default` for tooling (eslint, prettier, typescript)
+- `blockchain` for viem, wagmi
+- `nestjs` for NestJS stack
+- `next15` for Next.js stack
+- `react19` for React stack
+- `prisma` for Prisma stack
+- `security` for audit tools
+- `common` for shared utilities
+
+Bump catalog versions in one place to update all consumers.
+
+# Overrides
+
+Use `overrides` in `pnpm-workspace.yaml` to patch vulnerable transitive dependencies.
+Document why each override exists.
+Remove overrides when upstream fixes land.
+
+# Dependency Hygiene
+
+Run `pnpm update --interactive --latest` for major bumps.
+Run `pnpm dedupe` after major upgrades.
+Use `minimumReleaseAge` to avoid bleeding edge packages.
+
+Add dependencies to the package that uses them.
+Avoid hoisting unless explicitly needed.
+Run `pnpm install` from root only.
+
+# Lock File
+
+Lock file must be committed and up to date.
+Review lock file changes in PRs for unexpected additions.
+Never manually edit `pnpm-lock.yaml`.
diff --git a/.cursor/rules/92-docker.mdc b/.cursor/rules/92-docker.mdc
@@ -0,0 +1,77 @@
+---
+description: Docker multi stage builds, security, caching
+globs: ["**/Dockerfile", "**/docker-compose*.yaml"]
+---
+
+Multi stage builds mandatory.
+Minimize final image size and attack surface.
+
+# Node Version
+
+Read Node version from `.nvmrc` via build arg.
+Never hardcode Node version in Dockerfile.
+
+```dockerfile
+ARG NODE_VERSION=lts
+FROM node:${NODE_VERSION}-alpine AS base
+```
+
+CI must pass `--build-arg NODE_VERSION=$(cat .nvmrc)`.
+
+# Non Root User
+
+Never run as root in production.
+Create dedicated user and group with explicit IDs.
+
+```dockerfile
+RUN addgroup --system --gid 1001 nodejs && \
+    adduser --system --uid 1001 nodejs
+USER nodejs
+```
+
+Use `--chown` when copying files to set ownership.
+Final stage must declare `USER` before `CMD`.
+
+# Build Stages
+
+Use named stages for clarity:
+- `base` for shared setup
+- `pruner` for dependency isolation
+- `builder` for compilation
+- `runner` for production
+
+Prune workspace dependencies before build.
+Copy only necessary artifacts to final stage.
+
+# Caching
+
+Use pnpm store cache for faster builds:
+
+```dockerfile
+RUN --mount=type=cache,id=pnpm,target=/pnpm/store pnpm install --frozen-lockfile
+```
+
+Use `--prefer-offline` when possible.
+Enable Docker BuildKit caching in CI.
+
+# Security
+
+Alpine is preferred by default.
+
+Debian slim images are allowed when:
+- required by native dependencies
+- security patches are better supported
+- explicitly documented and reviewed
+
+Install only required system packages.
+Remove build tools from final stage.
+Never copy secrets or credentials into image.
+Never install dev dependencies in runner stage.
+
+Scan images for vulnerabilities before push.
+
+# Reproducibility
+
+Use `--frozen-lockfile` for deterministic installs.
+Pin base image versions in production builds.
+Document required build args.
diff --git a/.cursor/rules/95-github-actions.mdc b/.cursor/rules/95-github-actions.mdc
@@ -0,0 +1,86 @@
+---
+description: GitHub Actions security, performance, conventions
+globs: [".github/workflows/*.yml", ".github/actions/**"]
+---
+
+Principle of least privilege for all workflows.
+Fail fast and fail loud.
+
+# Permissions
+
+Declare minimal permissions at workflow level.
+Default to `contents: read` only.
+
+```yaml
+permissions:
+  contents: read
+```
+
+Add permissions only when required:
+- `pull-requests: read` for change detection
+- `packages: write` for container registry
+- `id-token: write` for OIDC
+
+Never use `permissions: write-all`.
+Document why each permission is needed.
+
+# Secrets
+
+Never echo or log secrets.
+Use OIDC for cloud auth when available.
+Prefer GitHub environments for secret scoping.
+Rotate secrets on suspected exposure.
+
+# Node Version
+
+Use custom action to read `.nvmrc`:
+
+```yaml
+- uses: ./.github/actions/get-node-version
+  id: get-node-version
+```
+
+Pass version to setup and Docker build steps.
+Never hardcode Node version in workflows.
+
+# Change Detection
+
+Skip jobs when files are unchanged.
+Use `dorny/paths-filter` or similar.
+Include dependency files in filters:
+- `pnpm-workspace.yaml`
+- `pnpm-lock.yaml`
+- `.nvmrc`
+
+Create skip jobs to satisfy branch protection.
+
+# Reusable Components
+
+Extract common steps into composite actions in `.github/actions/`.
+Use a `setup-env` action for consistent environment.
+Avoid duplicating setup logic across workflows.
+
+# Caching
+
+Cache pnpm store across runs.
+Cache Docker layers with `type=gha`.
+Use `--frozen-lockfile` for reproducibility.
+
+# Job Structure
+
+Use `needs` for explicit dependencies.
+Use `if` conditions to skip unnecessary work.
+Use matrix for parallel test execution.
+Name jobs clearly for status checks.
+
+# Security Scanning
+
+Enable Dependabot for updates.
+
+# Branch Protection
+
+Require status checks before merge.
+Require PR reviews for protected branches.
+Never allow force push to main branches.
+
+Use PR templates with checklists (e.g., DoD verification) where helpful.
diff --git a/.cursor/rules/99-meta.mdc b/.cursor/rules/99-meta.mdc
@@ -0,0 +1,12 @@
+---
+description: Meta rules for governance and updates
+alwaysApply: true
+---
+
+Version rules files with Git tags and changelog.
+Review annually or on major tool changes (e.g., Solidity upgrades).
+
+Track waivers and justifications in PRs and tickets.
+Update rules via PR with team review.
+
+Enforce via CI (e.g., lint rules files for consistency) when worth the maintenance cost.
PATCH

echo "Gold patch applied."
