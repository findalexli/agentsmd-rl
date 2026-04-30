#!/usr/bin/env bash
set -euo pipefail

cd /workspace/octocode-mcp

# Idempotency guard
if grep -qF "description: \"Flexible system-engineering skill for technical code understanding" "skills/octocode-engineer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/octocode-engineer/SKILL.md b/skills/octocode-engineer/SKILL.md
@@ -1,40 +1,36 @@
 ---
 name: octocode-engineer
-description: "System-aware engineering skill for understanding code, safe changes, refactoring, and architecture review with AST, LSP, and scanner tools. Use this before planning and for general task support when an agent must understand structure, flows, blast radius, and architectural risk before acting."
+description: "Flexible system-engineering skill for technical code understanding, project/feature deep dives, bug investigation, quality and architecture analysis, and safe delivery from research and RFC/planning through implementation and verification."
 ---
 
 # Octocode Engineer
 
 This skill helps an agent investigate, change, and verify a codebase with system awareness.
 
-Use this skill before planning or implementation. Treat it as the agent organizer for understanding the system first, then acting with a senior-architect mindset.
+Use this skill as the main engineering organizer when you need to understand a system deeply, make safe decisions, and execute with architecture awareness.
 
-Default operating mode:
+Motivation: high-quality architectural investigation improves delivery velocity, project resilience, and long-term maintainability.
+
+Suggested operating flow (adapt as needed):
 1. Start with local Octocode tools for discovery and scope.
-2. Use AST to prove structural claims.
-3. Use LSP and scanner results to understand semantics, blast radius, and architecture.
-4. Summarize the system, flows, features, and constraints in your own reasoning.
-5. Only then decide whether to ask, plan, explain, or edit.
+2. Use LSP to resolve semantics and blast radius.
+3. Use scanner output for architecture, critical paths, and risk concentration.
+4. Use AST to prove structural claims that matter.
+5. Summarize the system, flows, features, and constraints.
+6. Decide whether to ask, plan, explain, or edit.
 
 ## What This Skill Does
 
 Use this skill to:
 - organize investigation and decision-making for almost any engineering task
-- understand the main flows, summarize the system clearly, and identify what features and capabilities actually exist
-- stay aware of which local Octocode, LSP, AST, scanner, and project tools are available before choosing an approach
-- understand how a feature, bug, or module really works
-- trace definitions, callers, callees, imports, and shared contracts
-- find architectural issues such as cycles, chokepoints, coupling, hotspots, and layer violations
-- validate structural code smells with AST tools instead of weak text guesses
-- push toward clean code, clean modular architecture, strong contracts, and low duplication
-- check efficiency problems such as avoidable `O(n^2)` work, repeated scans, repeated queries, and wasteful flows
-- flag rigid, naive, brittle, or clearly unnecessary code paths before they spread
-- prevent patchy fixes that work locally but make the system harder to extend later
-- improve both delivery velocity and long-term quality through smarter flows and better structure
-- check build and configuration when needed or requested, including module-system mistakes such as incorrect ESM/CJS usage
-- plan safer refactors with blast-radius awareness
-- check that important critical aspects are documented when behavior, contracts, architecture, or operations depend on them
-- verify that a change did not create new code-quality, architecture, or test-quality problems
+- map real behavior and ownership, not just file-level code snippets
+- trace call flow, blast radius, and critical paths before changes
+- validate contracts/protocols across APIs, events, storage, and shared DTOs
+- detect code and architecture smells with structural proof
+- assess modularity/layering, coupling, duplication, and change risk
+- check efficiency, build/config, reliability, observability, rollout safety, and data correctness
+- validate docs/RFC/design claims against real implementation behavior
+- guide safe implementation and verification with clear evidence and confidence
 
 This is not only a code-editing skill.
 It is a structure, architecture, and flow-analysis skill that also supports coding.
@@ -44,73 +40,59 @@ It applies to any system, and is especially effective for Node/TypeScript and Py
 ## When To Use It
 
 Use this skill when the user asks to:
+- understand a technical codebase, project area, or feature end-to-end
 - understand code before changing it
+- do a deep dive into behavior, flow, ownership, or architecture
 - fix a bug in shared or unclear code
 - refactor a module, package, or cross-file flow
 - review code quality, architecture, or technical debt
+- shape architecture decisions before implementation and prepare a strong RFC (https://skills.sh/bgauryy/octocode-mcp/octocode-rfc-generator)
+- research implementation options and produce planning artifacts or design notes
+- validate docs, planning docs, and RFCs against real implementation behavior
+- check docs before planning and re-check docs after implementation
 - investigate build, runtime, package, or configuration issues when they affect behavior or delivery
 - improve maintainability, modularity, contracts, or extensibility
-- validate docs, plans, or RFCs against the real implementation
 - check dead code, test gaps, security risks, or design problems
 - implement a change safely in a non-trivial area
-- prepare for planning by understanding the real system before switching to plan mode
+- prepare for planning by understanding the real system first
+- verify implementation quality and risk after changes land
 
 ## Core Mindset
 
 1. System first, file second.
-2. Understand flows, features, and current system behavior before proposing fixes.
-3. Root causes often live in boundaries, flows, ownership, coupling, build/configuration mistakes, or missing tests, not just in the visible line of code.
-4. Important findings should be validated with at least 2 approaches when possible.
-5. Prefer local Octocode tools first for discovery, scope, and evidence.
-6. Use AST to check structural claims whenever text search may be misleading.
-7. Keep a running system summary in mind: what exists, what owns what, what connects to what, and which tools can prove it.
-8. Report confidence clearly: `confirmed`, `likely`, or `uncertain`.
-9. Prefer clean, modular, contract-driven solutions over local patches.
-10. For medium or large changes, understand blast radius and architecture before editing.
-11. Track meaningful work with tasks or todos when the runtime supports it.
-12. Ask the user at the right checkpoint when scope, risk, or tradeoffs are genuinely unclear.
+2. Prove behavior and blast radius before proposing changes.
+3. Prefer local Octocode discovery, then LSP/scanner, then AST proof.
+4. Validate important claims with at least 2 evidence sources.
+5. Prefer clean modular boundary/contract fixes over local patches.
+6. Use explicit confidence (`confirmed`, `likely`, `uncertain`) for conclusions.
+7. Treat prompt steps as practical checkpoints, not optional suggestions.
+8. Ask the user only at real decision checkpoints.
 
 ## The Main Problem This Skill Solves
 
-A local code read is often not enough.
-A function may look wrong, but the real issue may be:
-- too many callers
-- circular dependencies
-- a shared module doing too much
-- a weak boundary between layers
-- weak or implicit contracts between modules, APIs, or types
-- build or configuration mistakes, such as wrong ESM/CJS assumptions, broken module resolution, or incorrect package wiring
-- inefficient loops, repeated work, or avoidable `O(n^2)` logic
-- rigid or brittle code that is hard to extend without patching around it
-- duplicate logic spread across packages
-- a hidden flow through re-exports, side effects, or orchestration code
-- poor tests around a high-risk path
-- a quick patch that solves today but blocks safe extension tomorrow
-
-Because of that, always look at:
-- summary: what the system does, which features exist, and how the parts connect
-- structure: where code lives and how modules are grouped
-- architecture: dependencies, boundaries, cycles, hotspots, and ownership
-- contracts: TypeScript types, interfaces, DTOs, schemas, and public module boundaries
-- flows: entry points, call chains, data movement, and side effects
-- build/config: package/module format, tsconfig/bundler/runtime assumptions, scripts, env wiring, and compatibility edges
-- quality: clean code, low duplication, CSS hygiene, and maintainable module responsibilities
-- efficiency: algorithmic complexity, repeated work, repeated queries, N+1 patterns, and unnecessary orchestration
-- rigidity: brittle logic, over-coupled decisions, and code that is harder than necessary to extend
-- docs: whether critical setup, contracts, flows, constraints, migrations, and caveats are documented
-- code: the actual implementation details
-
-The target is not just "working code".
-The target is a system that stays extendable, understandable, and fast to change.
+Single-file reading is often misleading. Root causes usually live in boundaries, flow ownership, contracts, architecture pressure, or rollout/runtime assumptions.
+
+Use this skill to produce architecture-safe outcomes, not just passing patches:
+- verify real ownership, dependencies, and call flow
+- verify contracts/protocols, build/runtime assumptions, and migrations
+- verify quality dimensions (efficiency, reliability, observability, data correctness)
+- verify docs/RFC/design claims against implementation
 
 ## Investigation Lenses
 
 | Lens | Main question | Best tools |
 |------|---------------|------------|
 | Layout | Where does this behavior live? | `localViewStructure`, `localFindFiles`, `localSearchCode` |
 | Semantics | What symbol is this and who uses it? | `localSearchCode` -> LSP tools |
+| Critical path | Which execution paths dominate risk, latency, and business impact? | `lspCallHierarchy`, scanner flow output, targeted code read |
+| Contracts & protocols | Are type contracts, API/event schemas, and protocol rules explicit and stable? | `lspGotoDefinition`, `lspFindReferences`, schema/code read, tests |
+| Layering & modularity | Are dependency directions, boundaries, and module responsibilities clean? | scanner graph/architecture output, LSP references, AST checks |
 | Persistence | How is state stored and mutated? | schema files, SQL/Prisma/Mongoose definitions, migration files, repository/storage modules |
 | Efficiency | Is the implementation doing avoidable work or unnecessary complexity? | scanner complexity findings, code read, query/storage access paths, tests/benchmarks when available |
+| Reliability & resilience | Will this hold under failures, retries, partial outages, and retries of retries? | call flow + error handling read + tests + scanner risk signals |
+| Observability & operability | Can operators detect, explain, and recover from failures quickly? | logs/metrics/traces checks, runbook/docs checks, boundary instrumentation read |
+| Rollout & migration safety | Can this ship safely without breaking old producers/consumers? | migration docs, versioned contracts, compatibility checks, feature-flag/release-path review |
+| Data correctness | Are invariants and consistency rules preserved across writes and side effects? | schema + storage logic + transaction/idempotency read + contract tests |
 | Build & Config | Is runtime/build setup correct for this feature or environment? | package/module config, tsconfig, bundler config, scripts, import/export patterns, build errors |
 | Docs | Are critical behaviors, contracts, flows, and operational constraints documented? | docs/readmes, API docs, config docs, migration notes, code comments near boundaries |
 | Structure | Does this pattern really exist? | `scripts/ast/search.js`, `scripts/ast/tree-search.js` |
@@ -203,9 +185,17 @@ Use supporting quality checks when the task touches the relevant surface area.
 | Check | Use it for |
 |------|------------|
 | clean code review | naming, cohesion, responsibility split, readability |
+| code smell review | long methods, primitive obsession, shotgun surgery, feature envy, deep nesting, boolean flag clusters |
+| architecture smell review | god module, cycle-prone broker, unstable abstraction, boundary leakage, sink module, layering drift |
 | contract review | TypeScript types, interfaces, DTOs, schemas, return shapes |
+| type/protocol review | API/event versioning, backward compatibility, serialization safety, optional/null semantics, schema drift |
 | duplication review | repeated logic, near-clones, copy-pasted flows, repeated CSS patterns, general redundancy |
+| modularity/layer review | dependency direction, boundary ownership, cohesion vs coupling, module replaceability, cross-layer imports |
 | efficiency review | avoidable `O(n^2)` work, repeated scans, N+1 calls, wasteful transforms, unnecessary recomputation |
+| reliability/resilience review | retry policy, timeout handling, failure isolation, idempotency, fallback behavior |
+| observability/operability review | logging quality, metric/tracing coverage, diagnosability, alert/runbook readiness |
+| rollout/migration review | feature flags, backwards compatibility windows, rollback path, migration sequencing |
+| data correctness review | invariants, transaction boundaries, consistency model assumptions, duplicate-write safety |
 | rigidity review | brittle condition trees, hard-coded branching, patchy glue code, over-coupled modules, naive solutions |
 | build/config review | ESM/CJS mismatch, bad module resolution, wrong script wiring, incompatible runtime assumptions, broken package setup |
 | docs review | whether critical assumptions, contracts, flows, setup, migrations, and risks are documented where they should be |
@@ -234,26 +224,84 @@ Ask the user when needed at a real checkpoint, especially if:
 
 When asking, be concise and specific. Ask only what is needed to move forward safely.
 
+Use task tracking whenever the work spans research -> planning -> implementation -> verification -> docs/RFC sync.
+
+### 7. Prompt execution contract
+
+Treat the skill prompt as operational policy, not advice.
+
+Use this minimum execution contract:
+- restate the concrete goal and constraints in one short line before doing deep work
+- declare the next tool step and why it is the cheapest proof step
+- separate facts from inference in every checkpoint
+- carry forward concrete identifiers from tools (`lineHint`, paths, symbols, artifact names)
+- run explicit verification after edits; do not assume success from static reading
+- if a gate cannot be satisfied (missing tests, missing schema, missing ownership), report it as a blocker, not a silent skip
+
+Prompt reliability checks:
+- avoid vague status updates; every update should include what was checked and what remains
+- avoid broad claims like "looks fine" without at least one concrete evidence source
+- avoid switching from investigation to edits without a short system/flow summary
+- if 2 refinement attempts fail, stop and ask the user for a decision
+
+Keep this flexible:
+- skip irrelevant checks when they clearly do not apply
+- go deeper only where risk or uncertainty is meaningful
+- choose the lightest evidence path that can prove the conclusion
+
+### 8. Token-efficient execution mode
+
+Default to evidence-rich but compact execution.
+
+Token efficiency rules:
+- use one investigation thread at a time unless independent questions can be batched
+- avoid restating the same evidence in multiple sections; reference the prior checkpoint instead
+- prefer short, structured status updates over long narrative blocks
+- cap optional examples unless they materially change the decision
+- stop research when confidence is sufficient for safe action (`confirmed` or clearly bounded `likely`)
+- when uncertainty remains, ask one precise checkpoint question instead of writing long speculation
+
+Output compression rules:
+- summarize findings as: issue -> evidence -> impact -> action
+- keep confidence markers terse (`confirmed` / `likely` / `uncertain`)
+- report only residual risks that affect implementation, rollout, or contracts
+- avoid duplicating tool command details unless reproducibility is needed
+
+### 9. Script usage policy (cost-aware)
+
+Use scripts as proof tools, not as default heavy steps.
+
+- prefer local/LSP narrowing before broad scanner runs
+- run `scripts/run.js` broad scans for architecture/risk questions, not for single-symbol trivia
+- use scoped scan options when possible before full-repo scans
+- use `scripts/ast/tree-search.js` for fast triage, then `scripts/ast/search.js` only for authoritative confirmation
+- avoid repeating the same scan when the artifact already answers the current question
+- if scan output is stale relative to current edits, re-run only the minimal necessary scope
+
 ## Default Working Order
 
-For any non-trivial task, follow this order:
+For non-trivial tasks, this order is recommended (not mandatory):
 
 1. Clarify the behavior or question.
 2. Create or update tasks/todos if the work is multi-step.
 3. Map the package/module area with local tools.
 4. Trace important symbols with LSP.
-5. Validate and check structural claims with AST tools.
-6. Check architecture, build/configuration, docs, and flow risk with the scanner and relevant project files.
-7. Read the actual code with context.
-8. Summarize the current system, flows, and feature surface before deciding on action.
-9. Pause and ask the user if a real decision checkpoint appears.
-10. Only then decide whether to explain, plan, or edit.
+5. Identify critical paths and failure paths (latency/business-risk/error fanout).
+6. Validate and check structural claims with AST tools.
+7. Check architecture, layering/modularity, contracts/protocols, reliability/observability/rollout/data correctness, build/configuration, docs, and flow risk with the scanner and relevant project files.
+8. Read the actual code with context.
+9. If the task touches design docs or RFCs, validate them against current flows, contracts, and boundaries.
+10. Summarize the current system, flows, feature surface, and critical paths before deciding on action.
+11. Pause and ask the user if a real decision checkpoint appears.
+12. Decide whether to explain, plan, or edit.
 
 Short form:
-`clarify -> track -> layout -> symbols -> structure -> architecture/build/docs -> code -> summarize -> checkpoint -> action`
+`clarify -> track -> layout -> symbols -> structure -> architecture/build/docs -> code -> docs/RFC reality check -> summarize -> checkpoint -> action`
 
 ## How To Use This Skill
 
+Use these flows as templates, not rigid scripts.
+
 ### For code understanding
 
 1. Start with `localViewStructure` or `localFindFiles` to see the area.
@@ -301,61 +349,81 @@ Short form:
 7. Check whether critical architectural constraints are documented.
 8. Report both local code issues and system-level causes.
 
-## Recommended Tool Combos
-
-| Question | Recommended approach |
-|----------|----------------------|
-| Where should I start? | `localViewStructure` + `localFindFiles` |
-| What is this symbol? | `localSearchCode` -> `lspGotoDefinition` |
-| Who uses this shared function/type/export? | `localSearchCode` -> `lspFindReferences` |
-| What is the runtime path? | `localSearchCode` -> `lspCallHierarchy` |
-| Is this smell real? | AST search + targeted code read |
-| Can I prove this structural claim? | AST search/tree-search + targeted code read |
-| Are contracts weak or inconsistent? | LSP on public symbols + code read + scanner/AST signals |
-| Is this implementation inefficient? | scanner complexity signals + code read + persistence/query path review |
-| Is build/config part of the problem? | scripts/config review + import/export patterns + build/type errors + package/module checks |
-| Is this dead code? | `lspFindReferences` + AST import/export check + scanner dead-code signals |
-| Is this module risky to change? | scanner scope + LSP references/call flow + code read |
-| Is the problem architectural? | scanner graph/flow + local structure + LSP on chokepoints |
-| Are important critical aspects documented? | docs/readmes + code boundaries + config/schema/migration docs |
-| Is the codebase losing velocity? | scanner hotspots + duplication/redundancy checks + boundary/contract review |
-| Did the fix actually improve things? | tests + lint/build + scoped scanner + targeted LSP re-check |
+### For design and RFC validation
+
+1. Identify the claims made by the design doc or RFC (scope, boundaries, contracts, rollout, invariants).
+2. Map each claim to real code ownership (modules, entry points, storage, events, APIs).
+3. Verify runtime flow alignment using LSP call flow + scanner flow/graph outputs.
+4. Verify contract alignment (types/schemas/protocol versions/nullability/error semantics).
+5. Verify architecture alignment (layer boundaries, dependency direction, shared module pressure).
+6. Mark each claim as `confirmed`, `likely`, or `uncertain` with evidence.
+7. Report mismatches clearly: missing implementation, divergence, undocumented behavior, risky assumptions.
+8. Propose minimal doc/RFC corrections or implementation follow-ups to restore alignment.
+
+### For implementation duty cycle
+
+1. Before coding: state root cause, blast radius, and target contract/boundary.
+2. During coding: keep changes in the smallest responsible layer; avoid cross-layer leakage.
+3. During coding: run narrow checks per batch (tests/types/lint or focused scanner slice).
+4. After coding: run full relevant verification and re-check affected critical paths.
+5. After coding: re-open docs/RFC sections touched by the change and sync them with reality.
+6. Close with residual risk, follow-ups, and confidence level.
+
+## Quick Tool Routing
+
+Use this compact routing table first; use detailed playbooks in [Tool workflows](./references/tool-workflows.md).
+
+| Question | Route |
+|----------|-------|
+| symbol/ownership | `localSearchCode` -> LSP (`gotoDefinition` / `findReferences`) |
+| callers/callees/critical path | `localSearchCode` -> `lspCallHierarchy` -> targeted read |
+| architecture risk/hotspots | `scripts/run.js` (scoped first, broad when needed) |
+| structural smells/claims | `scripts/ast/tree-search.js` -> `scripts/ast/search.js` |
+| RFC/design/docs alignment | claim-by-claim mapping -> flow/contract/architecture validation |
 
 ## Before / During / After A Change
 
 ### Before
 - understand current behavior and invariants
 - find consumers and callers
-- inspect tests around the changed path
-- check whether the area is a hotspot, cycle member, or shared boundary
-- check whether build/configuration assumptions are part of the behavior
-- check contracts: types, inputs, outputs, schemas, and public APIs
-- check whether critical behavior and constraints are documented
+- identify entry paths, error paths, and critical business/runtime paths
+- inspect tests and scanner signals for hotspot/cycle/shared-boundary risk
+- check contracts/protocols (types, schemas, compatibility, nullability, serialization)
+- check reliability/observability/rollout assumptions (retries, telemetry, migration, rollback)
+- check build/config assumptions that affect runtime behavior
+- check whether critical behavior, constraints, and migration notes are documented
+- if a design doc or RFC exists, map its claims to concrete code ownership before editing
 - check for duplication before adding another branch or helper
-- check for unnecessary complexity or repeated work before accepting the current shape
+- check for unnecessary complexity and nearby code/architecture smells, not only the target line
 - look for an existing local pattern before inventing a new one
 
 ### During
 - keep edits focused
 - preserve boundaries unless the plan intentionally changes them
 - prefer the smallest change that fixes the real issue
 - prefer the cleanest modular fix that keeps the system extendable
-- maintain clear contracts, especially in TypeScript-heavy code
+- maintain clear contracts/protocol compatibility unless an explicit migration is in scope
+- preserve or improve reliability behavior under failure, retries, and partial success
 - keep build/configuration consistent with runtime expectations, especially around ESM/CJS boundaries
-- reduce redundancy and avoid layering new logic on top of rigid or naive code when a cleaner simplification is possible
+- reduce redundancy and avoid layering new logic on rigid code when simplification is possible
+- avoid introducing new smells (deep nesting, flag-parameter branching, over-centralized modules)
 - improve inefficient flows when they are part of the real problem
-- keep CSS clean and scoped if the task touches frontend styling
-- update or flag docs when critical behavior, contracts, setup, migration, or architecture understanding changed
+- keep CSS clean/scoped when frontend styling is touched
+- update or flag docs when behavior, contracts, setup, migration, or architecture understanding changed
+- if design/RFC assumptions were invalid, record the exact mismatch and corrective update
 - if the root cause is structural, say so instead of hiding it behind a cosmetic patch
 
 ### After
 - run the relevant tests
 - run lint and build or type-check as appropriate
-- run CSS checks when styles changed
-- run `knip` when refactors may have left dead exports, files, or deps behind
-- verify build and configuration still match runtime/module expectations
-- re-check changed symbols with LSP after renames or moves
+- run CSS checks when styles changed; run `knip` when refactors may leave dead artifacts
+- verify build/config still match runtime/module expectations
+- re-check changed symbols with LSP after renames/moves
 - run a scoped scanner pass for non-trivial changes
+- re-check critical paths for regressions in behavior, cost, and failure handling
+- verify changed type/protocol contracts with consumers and boundary tests
+- verify reliability/observability/rollout assumptions still hold after the change
+- re-validate relevant design/RFC claims against final implementation behavior
 - verify important critical aspects are documented if the task changed them
 - mention any remaining architectural risk even if the code now works
 
@@ -376,24 +444,17 @@ Examples:
 
 ## Hard Rules
 
-- Never present raw detector output as unquestioned fact.
-- Never guess `lineHint`; get it from `localSearchCode`.
-- Never use `lspCallHierarchy` on non-function symbols.
-- Never judge a shared module by one file read alone.
-- Never skip local Octocode discovery when those tools are available.
-- Never present an important structural claim without checking it with AST when AST can prove it.
-- Never stop at code style if the deeper issue is structure or flow.
-- Never ignore build or configuration evidence when behavior may depend on package/module/runtime setup.
-- Never prefer a quick patch when the real issue is contracts, boundaries, duplication, or architecture.
-- Never ignore obvious inefficiency, redundancy, or rigid code if it materially hurts extensibility or clarity.
-- Never add new duplication if an existing abstraction or module should be improved instead.
-- Never leave critical contract, flow, setup, or migration changes undocumented when documentation is needed.
-- Always check blast radius before changing shared symbols.
-- Always mention architecture, flow, or boundary impact when it matters.
-- Always consider whether the change improves or hurts extensibility and team velocity.
-- Always use task tracking for meaningful multi-step work when the runtime supports it.
-- Always ask the user when a real decision or ambiguity checkpoint blocks safe progress.
-- For medium or large changes, present a plan before making the edit.
+Core guardrails:
+- Do not present raw detector output as unquestioned fact.
+- Do not guess `lineHint`; obtain it from `localSearchCode`.
+- Do not use `lspCallHierarchy` on non-function symbols.
+- Do not judge shared modules from one file read alone.
+- Do not claim design/RFC compliance without claim-by-claim evidence.
+- Do not ignore build/config evidence when runtime behavior may depend on it.
+- Avoid quick patches when the real issue is contracts, boundaries, duplication, or architecture.
+- Check blast radius before changing shared symbols.
+- Re-sync docs/RFCs when implementation changes architecture, contracts, rollout assumptions, or constraints.
+- Ask the user when a real ambiguity or decision checkpoint blocks safe progress.
 
 ## Fallback Mode
 
@@ -413,12 +474,20 @@ A good result from this skill should answer all of these:
 - Is the problem local, structural, or architectural?
 - Is build/configuration part of the issue?
 - Is the implementation efficient enough, or is avoidable complexity hurting it?
+- Is reliability acceptable under failure and retry conditions?
+- Is observability sufficient to debug and operate this path?
+- Is rollout/migration safety clear and reversible?
 - Is the system becoming cleaner, more modular, and easier to extend?
 - Are important critical aspects documented?
 - What is the safest next move?
 
 If the answer only explains one file, it is usually incomplete.
 
+## Companion Skill
+
+Use this with the RFC skill when architecture options, trade-offs, or migration strategy need a formal proposal before coding:
+- [octocode-rfc-generator](https://skills.sh/bgauryy/octocode-mcp/octocode-rfc-generator) — generate a smart RFC from validated system evidence.
+
 ## References
 
 Use these only when needed. Pick the right reference for the situation:
PATCH

echo "Gold patch applied."
