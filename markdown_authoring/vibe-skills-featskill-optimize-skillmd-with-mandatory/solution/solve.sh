#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vibe-skills

# Idempotency guard
if grep -qF "Execute from the approved plan. L grade executes serially; XL grade executes wav" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -5,42 +5,53 @@ description: Vibe Code Orchestrator (VCO) is a governed runtime entry that freez
 
 # Vibe Governed Runtime
 
-## Canonical Bootstrap
+## Mandatory Router Invocation With Intent Optimization
 
-If the user invoked `/vibe`, `$vibe`, or `vibe`, enter canonical `vibe` first and do nothing else first.
+When AI activates (reads and acts on) the `vibe` skill, AI MUST call the canonical
+router before entering any governed runtime stage. This is not an automatic trigger --
+it is a mandatory self-discipline requirement.
 
-Bootstrap sequence:
+Canonical router: `scripts/router/resolve-pack-route.ps1`
 
-1. Resolve `skill_root` as the directory that contains this `SKILL.md`.
-2. Resolve `workspace_root` as the current user task working root. This is where governed artifacts should be written when the user is working outside the Vibe installation itself.
-3. Resolve the current host adapter id. Use `codex` in Codex, `claude-code` in Claude Code, `cursor` in Cursor, `windsurf` in Windsurf, `openclaw` in OpenClaw, and `opencode` in OpenCode.
-4. Launch the proof-complete canonical entry before reading repo files, protocol docs, prior run folders, or writing any runtime artifact.
+### Router Input: Extract Core Intent as Keyword Text
 
-POSIX / bash launch:
+When calling the router, AI must NOT pass the raw user prompt, language mix, or full
+context. Instead, AI must extract and distill the core intent into a structured keyword
+text block. This improves router intent hit rate.
 
-```bash
-PYTHONPATH="<skill_root>/apps/vgo-cli/src" \
-python3 -m vgo_cli.main canonical-entry \
-  --repo-root "<skill_root>" \
-  --artifact-root "<workspace_root>" \
-  --host-id "<host_id>" \
-  --entry-id "vibe" \
-  --prompt "<full user request>"
-```
+Prompt extraction rules:
+1. Extract nouns/verbs that describe the WORK TYPE (e.g., "refactor", "debug", "plan", "review", "research", "implement")
+2. Extract nouns that describe the DOMAIN/TECHNOLOGY (e.g., "typescript", "react", "database", "api")
+3. Extract nouns that describe the DELIVERABLE (e.g., "feature", "fix", "migration", "documentation")
+4. Remove filler language, politeness, meta-commentary, and system-level framing
+5. If the user gave explicit constraints or requirements, encode them as keyword tags
 
-Windows PowerShell launch:
+Bad example (raw prompt passed through):
+"Hi! I've been working on a React project lately and sometimes I encounter some performance issues, like component re-rendering problems. Could you help me analyze and give optimization suggestions? Thank you so much!"
 
-```powershell
-$env:PYTHONPATH = "<skill_root>/apps/vgo-cli/src"
-python -m vgo_cli.main canonical-entry `
-  --repo-root "<skill_root>" `
-  --artifact-root "<workspace_root>" `
-  --host-id "<host_id>" `
-  --entry-id "vibe" `
-  --prompt "<full user request>"
-```
+Good example (keyword text extracted):
+"debug performance-react component-re-render optimization analysis coding typescript react"
 
-If `python` is unavailable in Windows PowerShell, use the same invocation with `py -3` instead, for example:
+Required router call steps at vibe entry:
+1. Extract core intent as keyword text (do NOT pass raw prompt)
+2. Call router with extracted keyword text
+3. If route_mode == "confirm_required", present confirm surface to user
+4. If router returns hazard alert or fallback_active, surface it explicitly
+5. If router call fails, report "blocked" with failure reason -- do NOT continue
+
+The fact that the router may internally enter "auto_route" mode does NOT mean the
+router was skipped. The router was called and made that decision. AI must invoke
+it explicitly every time.
+
+## Canonical Bootstrap
+
+Bootstrap sequence (run canonical launch before reading repo files, protocol docs, or writing any artifact):
+
+1. Resolve `skill_root` (directory containing this `SKILL.md`) and `workspace_root` (current task working root; governed artifacts go here when working outside the Vibe installation).
+2. Resolve host adapter id: `codex` in Codex, `claude-code` in Claude Code, `cursor` in Cursor, `windsurf` in Windsurf, `openclaw` in OpenClaw, `opencode` in OpenCode.
+3. Launch the proof-complete canonical entry.
+
+Windows PowerShell launch (primary):
 
 ```powershell
 $env:PYTHONPATH = "<skill_root>/apps/vgo-cli/src"
@@ -49,120 +60,62 @@ py -3 -m vgo_cli.main canonical-entry `
   --artifact-root "<workspace_root>" `
   --host-id "<host_id>" `
   --entry-id "vibe" `
-  --prompt "<full user request>"
+  --prompt "<extracted keyword intent text>"
 ```
 
-Discoverable wrapper ids still enter canonical `vibe`; only the bounded stop changes:
+If `py -3` is unavailable, try `python` instead.
 
-- `vibe-want` -> add `--requested-stage-stop requirement_doc`
-- `vibe-how` -> add `--requested-stage-stop xl_plan --requested-grade-floor XL`
-- `vibe` and `vibe-do-it` -> add `--requested-stage-stop phase_cleanup`
+Discoverable wrapper ids still enter canonical `vibe`; only the bounded stop changes:
+- `vibe-want` -> `--requested-stage-stop requirement_doc`
+- `vibe-how` -> `--requested-stage-stop xl_plan --requested-grade-floor XL`
+- `vibe` and `vibe-do-it` -> `--requested-stage-stop phase_cleanup`
 
 Hard rules:
-
 - Do not inspect the repo, protocol docs, or prior run outputs before canonical launch returns, except to resolve `skill_root` and current host id.
 - Do not use the Vibe installation root as the governed artifact root when the user asked you to work in another workspace or repository.
 - Do not manually create `outputs/runtime/vibe-sessions/<run-id>/`, `docs/requirements/`, or `docs/plans/` as a substitute for launch.
-- Do not simulate `skeleton_check`, `deep_interview`, `requirement_doc`, `xl_plan`, `plan_execute`, or `phase_cleanup` in chat or shell before canonical launch completes.
-- Do not treat `scripts/runtime/Invoke-VibeCanonicalEntry.ps1` alone as proof-complete canonical entry; it is a bridge used by the canonical launcher, not the canonical launcher itself.
-- Do not claim canonical vibe entry from reading this file, wrapper text, bootstrap text, or old artifacts.
-- Canonical launch claims require `host-launch-receipt.json`, `runtime-input-packet.json`, `governance-capsule.json`, and `stage-lineage.json`.
-- If canonical launch cannot run or cannot emit the required truth artifacts, report `blocked` with the concrete failure reason. Do not silently continue in ordinary mode.
+- Do not simulate stages, claim canonical entry from reading this file or wrapper text, or silently continue if canonical launch fails -- report `blocked` with the concrete failure reason.
 
-Everything below this bootstrap section is reference material to follow only after successful canonical launch.
+Proof of canonical launch requires: `host-launch-receipt.json`, `runtime-input-packet.json`, `governance-capsule.json`, and `stage-lineage.json`.
 
-`vibe` is a host-syntax-neutral skill contract.
-
-`/vibe`, `$vibe`, and agent-invoked `vibe` all mean the same thing: enter the same governed runtime, not different runtime authorities.
-
-## What `vibe` Does
-
-`vibe` is the official governed runtime for tasks that need:
-
-- requirement clarification before execution
-- one-shot autonomous execution with retained governance
-- multi-step planning and implementation
-- multi-agent XL orchestration
-- proof, verification, and mandatory cleanup
-
-This runtime still has one canonical authority: `vibe`.
-
-Hosts may expose discoverable labels such as:
-
-- `Vibe`
-- `Vibe: What Do I Want?`
-- `Vibe: How Do We Do It?`
-- `Vibe: Do It`
-
-Those labels are presentational launch surfaces only.
-They do not create a second runtime.
-
-The user does not choose between `M`, `L`, or `XL` as entry branches.
-Those grades still exist, but only as internal execution strategy, with only `--l` and `--xl` allowed as lightweight public grade-floor overrides.
-
-## When To Use
-
-Use `vibe` when the task is not a trivial one-line edit and you want the system to:
-
-- inspect the repo and active skeleton first
-- clarify or infer intent before building
-- freeze a requirement document
-- generate an XL-style execution plan
-- execute in phases with explicit verification
-- clean up phase artifacts and managed node residue
-
-Do not use `vibe` for:
-
-- casual Q and A
-- simple explanation-only requests
-- tiny edits where governed overhead is unnecessary
+`vibe` is a host-syntax-neutral skill contract. `/vibe`, `$vibe`, and agent-invoked `vibe` all mean the same thing: enter the same governed runtime.
 
 ## Unified Runtime Contract
 
 `vibe` always runs the same 6-stage state machine:
 
-1. `skeleton_check`
-2. `deep_interview`
-3. `requirement_doc`
-4. `xl_plan`
-5. `plan_execute`
-6. `phase_cleanup`
+1. `skeleton_check` -- verify repo shape, prerequisites, and existing artifacts
+2. `deep_interview` -- clarify intent and infer constraints
+3. `requirement_doc` -- freeze the single requirement source under `docs/requirements/`
+4. `xl_plan` -- write execution plan under `docs/plans/`
+5. `plan_execute` -- execute from the frozen plan
+6. `phase_cleanup` -- cleanup temp artifacts, write receipts, delivery-acceptance report
 
-These stages are mandatory.
-They may become lighter for simple work, but they are not skipped as a matter of policy.
+These stages are mandatory. They may become lighter for simple work, but they are not skipped as a matter of policy.
 
-Discoverable wrapper labels may request an earlier terminal stage.
-That changes where the current run stops, not which runtime owns authority.
-The bounded stop targets are:
+Runtime mode: only `interactive_governed` is supported. The system asks high-value questions, confirms frozen requirements, and pauses at plan approval boundaries.
 
+Discoverable wrapper labels may request an earlier terminal stage (that changes where the run stops, not which runtime owns authority):
 - `Vibe: What Do I Want?` -> `requirement_doc`
 - `Vibe: How Do We Do It?` -> `xl_plan`
 - `Vibe` and `Vibe: Do It` -> `phase_cleanup`
 
-Official governed entry also records runtime lineage:
-
+Official governed entry records lineage:
 - root or child entry writes `governance-capsule.json`
 - each validated stage transition appends `stage-lineage.json`
 - child-governed startup validates inherited context through `delegation-envelope.json`
 
-## Runtime Mode
-
-### `interactive_governed`
-
-The only supported governed runtime mode.
-
-Use this when the system should still ask the user high-value questions, confirm frozen requirements, and pause at plan approval boundaries.
+The user does not choose between `M`, `L`, or `XL` as entry branches. Those grades exist only as internal execution strategy; only `--l` and `--xl` are allowed as lightweight public grade-floor overrides.
 
 ## Governor And Specialist Contract
 
 `vibe` owns runtime authority even when the canonical router surfaces a specialist skill.
 
 That means:
-
-- governed `vibe` runs must surface bounded specialist recommendations and must treat router-selected specialist skills as route truth or executable recommendation candidates
+- governed `vibe` runs must surface bounded specialist recommendations and treat router-selected specialist skills as route truth or executable recommendation candidates
 - direct specialist handling should stay in the current host session by default; do not create hidden specialist sub-sessions unless policy explicitly opts back into that bridge path
 - runtime-selected skill remains `vibe` for governed entry
-- eligible specialist help must auto-promote into bounded native-mode assistance by default
+- eligible specialist help MUST be promoted (elevated) into bounded native-mode dispatch as a default governance policy -- this is a required action, not a passive auto-behavior
 - specialist help must preserve the specialist skill's own workflow, inputs, outputs, and validation style
 - specialist help must not create a second requirement doc, second plan surface, or second runtime authority
 
@@ -173,21 +126,11 @@ For XL delegation, `vibe` runs with hierarchy semantics:
 - `root_governed`: the only lane that may freeze canonical requirement and plan surfaces and issue final completion claims
 - `child_governed`: subordinate execution lane that inherits frozen context and emits local receipts only
 
-Child-governed lanes must:
-
-- keep `$vibe` at prompt tail to preserve governed discipline
-- inherit frozen requirement and plan context from the root lane
-- stay within assigned ownership boundaries and write scopes
-- validate a root-authored `delegation-envelope.json` and emit a `delegation-validation-receipt.json` before bounded execution
+Child-governed lanes must: keep `$vibe` at prompt tail, inherit frozen requirement and plan context, stay within assigned ownership boundaries and write scopes, and validate a root-authored `delegation-envelope.json` before bounded execution.
 
-Child-governed lanes must not:
-
-- create a second canonical requirement surface under `docs/requirements/`
-- create a second canonical plan surface under `docs/plans/`
-- publish final completion claims for the full root task
+Child-governed lanes must not: create a second canonical requirement or plan surface, or publish final completion claims for the full root task.
 
 Specialist dispatch under hierarchy:
-
 - `approved_dispatch`: root-approved specialist usage in the frozen plan
 - `local_suggestion`: residual child-detected specialist suggestion that only remains advisory when blocked, degraded, or explicitly forced to escalate
 
@@ -199,163 +142,64 @@ Specialist dispatch under hierarchy:
 - `L`: native serial execution lane for staged work; delegated units stay bounded and sequence-first
 - `XL`: wave-sequential execution with step-level bounded parallelism for independent units only
 
-The governed runtime selects the internal grade after `deep_interview` and before `plan_execute`.
-
-User-facing behavior stays the same regardless of host syntax:
-
-- one governed runtime authority
-- one frozen requirement surface
-- one XL-style plan surface
-- one execution and cleanup contract
-- optional discoverable intent labels that still resolve to canonical `vibe`
-
-Compatibility notes for downstream verification and host adapters:
-
-- `M=single-agent`
-- `L=serial native execution from frozen plan (no blanket fan-out).`
-- `XL=wave-sequential execution; bounded parallelism only inside eligible steps.`
-- XL native lifecycle APIs remain `spawn_agent`/`send_input`/`wait`/`close_agent`
+The governed runtime selects the internal grade after `deep_interview` and before `plan_execute`. User-facing behavior stays the same regardless of host syntax: one governed runtime authority, one frozen requirement surface, one XL-style plan surface, one execution and cleanup contract.
 
 ## Stage Contract
 
 ### 1. `skeleton_check`
 
-Check repo shape, active branch, existing plan or requirement artifacts, and runtime prerequisites before starting.
+Check repo shape, active branch, existing plan or requirement artifacts, and runtime prerequisites before starting. Produce a skeleton receipt.
 
 ### 2. `deep_interview`
 
-Produce a structured intent contract containing:
-
-- goal
-- deliverable
-- constraints
-- acceptance criteria
-- product acceptance criteria
-- manual spot checks
-- completion language policy
-- delivery truth contract
-- non-goals
-- autonomy mode
-- inferred assumptions
-
-In `interactive_governed`, this stage may ask direct questions.
+Produce a structured intent contract containing: goal, deliverable, constraints, acceptance criteria, product acceptance criteria, manual spot checks, completion language policy, delivery truth contract, non-goals, autonomy mode, inferred assumptions. In `interactive_governed`, this stage may ask direct questions.
 
 ### 3. `requirement_doc`
 
-Freeze a single requirement document under `docs/requirements/`.
-
-After this point, execution should trace back to the requirement document rather than to raw chat history.
+Freeze a single requirement document under `docs/requirements/`. After this point, execution traces back to this document rather than to raw chat history.
 
 ### 4. `xl_plan`
 
-Write the execution plan under `docs/plans/`.
-
-The plan must contain:
-
-- internal grade decision
-- wave or batch structure
-- ownership boundaries
-- verification commands
-- delivery acceptance plan
-- completion language rules
-- rollback rules
-- phase cleanup expectations
+Write the execution plan under `docs/plans/`. The plan must contain: internal grade decision, wave or batch structure, ownership boundaries, verification commands, delivery acceptance plan, completion language rules, rollback rules, phase cleanup expectations.
 
 ### 5. `plan_execute`
 
-Execute the approved plan.
-
-L grade executes planned units serially in the native governed lane.
-XL grade executes waves sequentially and may run only independent units in bounded parallel within a step.
-If subagents are spawned, their prompts must end with `$vibe`.
-Governed `vibe` runs must emit specialist recommendations; eligible recommendations must auto-promote into bounded native dispatch units, and only blocked, degraded, or forced-escalation cases should remain `local_suggestion`.
-If subagents run in child-governed lanes, they must inherit root-frozen context and must not reopen canonical requirement or plan truth surfaces.
+Execute from the approved plan. L grade executes serially; XL grade executes waves sequentially with bounded parallel independent units only. Spawned subagent prompts must end with `$vibe`. Bounded specialist recommendations must be promoted into native dispatch units per the skill promotion policy; only blocked, degraded, or forced-escalation cases remain `local_suggestion`. Child-governed lanes inherit root-frozen context and must not reopen canonical requirement or plan truth surfaces.
 
 ### 6. `phase_cleanup`
 
-Cleanup is part of the runtime, not an afterthought.
-
-Each phase must leave behind:
-
-- cleanup receipt
-- temp-file cleanup result
-- node audit or cleanup result
-- proof artifacts needed for later verification
-- delivery-acceptance report proving whether full completion wording is allowed
-
-## Router And Runtime Authority
+Each phase must leave behind: cleanup receipt, temp-file cleanup result, node audit or cleanup result, proof artifacts needed for later verification, delivery-acceptance report proving whether full completion wording is allowed.
 
-The canonical router remains authoritative for route selection.
+## Router Invocation At Entry
 
-`vibe` does not create a second router.
-It consumes the canonical route, confirm, unattended, and overlay surfaces and then executes the governed runtime contract around them.
+See "Mandatory Router Invocation With Intent Optimization" above for the required router call protocol (intent extraction + mandatory invocation). This section covers how vibe consumes the router output.
 
 Rules:
-
-- explicit user tool choice still overrides routing
-- `confirm_required` still uses the existing white-box `user_confirm interface`
-- unattended behavior is mapped into governed runtime mode, not into a separate control plane
+- always extract core intent as keyword text before calling router (never pass raw prompt)
+- explicit user tool choice overrides routing
+- `confirm_required` surfaces via existing user_confirm interface
+- unattended behavior maps to governed runtime mode, not a separate control plane
 - provider-backed intelligence may advise but must not replace route authority
-
-## Compatibility With Process Layers
-
-Other workflow layers may shape discipline, but they must not become a parallel runtime.
-
-Required ownership split:
-
-- canonical router: route authority
-- `vibe`: governed runtime authority
-- host bridge: hidden hook wiring and artifact persistence
-- superpowers or other process helpers: discipline and workflow advice only
-
-Forbidden outcomes:
-
-- second visible startup/runtime prompt surface
-- second requirement freeze surface
-- second execution-plan surface
-- second route authority
+- the router may internally enter "auto_route" mode when confidence exceeds threshold -- this is a router-internal behavior, not evidence that AI skipped the router call
 
 ## Protocol Map
 
 Read these protocols on demand:
-
 - `protocols/runtime.md`: governed runtime contract and stage ownership
 - `protocols/think.md`: planning, research, and pre-execution analysis
 - `protocols/do.md`: coding, debugging, and verification
 - `protocols/review.md`: review and quality gates
 - `protocols/team.md`: XL multi-agent orchestration
-- `protocols/retro.md`: retrospective and learning capture
-
-## Learn And Retro Surface
-
-For LEARN / retrospective work, use the `Context Retro Advisor` vocabulary from `protocols/retro.md`.
-
-- retro outputs should preserve `CER format` artifacts when that protocol is invoked
-- completion-language corrections remain governed and evidence-backed
-
-## Memory Rules
-
-Memory remains runtime-neutral:
-
-- `state_store (runtime-neutral)`: default session memory
-- Serena: explicit decisions only
-- ruflo: optional short-horizon vector memory
-- Cognee: optional long-horizon graph memory
-- episodic memory: disabled in governed routing
+- `protocols/retro.md`: retrospective and learning capture; retro outputs should preserve `CER format` artifacts when that protocol is invoked; completion-language corrections remain governed and evidence-backed
 
 ## Quality Rules
 
-Never claim success without evidence.
-
-Minimum invariants:
-
+Never claim success without evidence. Minimum invariants:
 - verification before completion
 - no silent no-regression claims
 - requirement and plan artifacts remain traceable
 - cleanup receipts are emitted before phase completion is claimed
-- Reading `SKILL.md`, wrapper markdown, or bootstrap text alone is not proof of canonical vibe entry.
-- canonical vibe claims require `host-launch-receipt.json`, `runtime-input-packet.json`, `governance-capsule.json`, and `stage-lineage.json`
-- canonical vibe claims require runtime artifact proof, not SKILL.md-only simulation
+- Reading `SKILL.md`, wrapper markdown, or bootstrap text alone is not proof of canonical vibe entry; canonical vibe claims require `host-launch-receipt.json`, `runtime-input-packet.json`, `governance-capsule.json`, and `stage-lineage.json`
 
 ### Failure Exposure And Fallback Discipline
 
@@ -365,12 +209,10 @@ Minimum invariants:
 - Only introduce or retain fallback / degraded behavior when the active requirement explicitly asks for it.
 - Any allowed fallback or boundary behavior must be explicit, traceable in artifacts or logs, documented in the relevant contract or requirement surface, and easy to disable.
 - Fallback or boundary behavior must not be used to bypass real execution, verification, or root-cause repair.
-- Existing explicit governance boundaries are not themselves violations; this rule targets newly introduced behavior that hides capability loss or papers over a broken primary path.
 
 ## Outputs
 
 The governed runtime should leave behind:
-
 - `outputs/runtime/vibe-sessions/<run-id>/skeleton-receipt.json`
 - `outputs/runtime/vibe-sessions/<run-id>/intent-contract.json`
 - `outputs/runtime/vibe-sessions/<run-id>/runtime-input-packet.json` with `route_snapshot` and specialist surfaces
@@ -383,10 +225,12 @@ The governed runtime should leave behind:
 
 ## Known Boundaries
 
-- the canonical router still owns route selection
+- canonical router must be called at vibe entry (mandatory self-discipline, not auto-trigger); router may enter auto_route mode internally -- this does NOT mean AI skips the router call
+- memory remains runtime-neutral: `state_store` (default session), `Serena` (explicit decisions only), `ruflo` (optional short-horizon), `Cognee` (optional long-horizon), episodic memory disabled in governed routing
 - install or check surfaces should not be rebaselined casually
-- host adapters may shape capability declarations, but must not fork runtime truth
+- host adapters may shape capability declarations but must not fork runtime truth
 - benchmark autonomy does not mean governance-free execution
+- other workflow layers may shape discipline but must not become a parallel runtime; explicitly forbidden: second visible runtime entry surface, second requirement freeze surface, second execution-plan surface, second route authority
 
 ## Maintenance
 
PATCH

echo "Gold patch applied."
