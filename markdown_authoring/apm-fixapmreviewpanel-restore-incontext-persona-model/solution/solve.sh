#!/usr/bin/env bash
set -euo pipefail

cd /workspace/apm

# Idempotency guard
if grep -qF "(progressive-disclosure skill model -- no sub-agent dispatch). Routing" ".apm/skills/apm-review-panel/SKILL.md" && grep -qF "(progressive-disclosure skill model -- no sub-agent dispatch). Routing" ".github/skills/apm-review-panel/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.apm/skills/apm-review-panel/SKILL.md b/.apm/skills/apm-review-panel/SKILL.md
@@ -9,10 +9,12 @@ description: >-
 
 # APM Review Panel -- Expert Review Orchestration
 
-The panel is fixed at **5 mandatory specialists + 1 conditional auth
-specialist + 1 arbiter = up to 7 agents producing 7 verdict blocks**.
-Routing chooses *which* personas execute; it never changes which
-headings appear in the final verdict.
+The panel is fixed at **5 mandatory specialist lenses + 1 conditional
+auth lens + 1 arbiter lens = up to 7 persona sections in one verdict
+comment**. You play each lens in turn from inside a single agent loop
+(progressive-disclosure skill model -- no sub-agent dispatch). Routing
+chooses *which* lenses execute; it never changes which headings appear
+in the final verdict.
 
 ## Agent roster
 
@@ -50,8 +52,8 @@ headings appear in the final verdict.
 Auth Expert is the only conditional panelist. Activate `auth-expert`
 if either rule below matches.
 
-1. **Fast-path file trigger.** Dispatch immediately when the PR
-   changes any of:
+1. **Fast-path file trigger.** Activate the Auth Expert lens
+   immediately when the PR changes any of:
    - `src/apm_cli/core/auth.py`
    - `src/apm_cli/core/token_manager.py`
    - `src/apm_cli/core/azure_cli.py`
@@ -62,7 +64,7 @@ if either rule below matches.
    - `src/apm_cli/deps/registry_proxy.py`
 
 2. **Fallback self-check.** If no fast-path file matched, answer this
-   before dispatch:
+   before activating the lens:
 
    > Does this PR change authentication behavior, token management,
    > credential resolution, host classification used by `AuthResolver`,
@@ -72,9 +74,10 @@ if either rule below matches.
 
 Routing rule:
 
-- **YES** -> dispatch `auth-expert` and capture its findings.
+- **YES** -> take the Auth Expert lens (per the Persona pass
+  procedure) and capture its findings.
 - **NO**  -> record `Auth Expert inactive reason: <one sentence
-  citing the touched files>` in working notes; do not dispatch.
+  citing the touched files>` in working notes; do not take the lens.
 - Never use wildcard heuristics like `*auth*`, `*token*`, or
   `*credential*` as the sole trigger.
 
@@ -145,74 +148,70 @@ A non-trivial change passes when:
 
 ## Notes
 
-- **Do not open linked persona files in the orchestrator thread.**
-  Treat the roster links as dispatch targets only -- each sub-agent
-  loads its own `.agent.md` in its own context window. Pre-loading
-  persona content into the orchestrator defeats Reduced Scope and
-  Progressive Disclosure.
-- This skill orchestrates only; persona detail lives in the linked
-  `.agent.md` files.
+- This skill orchestrates a panel **in your own context** -- you are
+  the only agent. You load each persona's `.agent.md` reference file
+  on demand (progressive disclosure), assume that persona's lens to
+  produce its findings, then move to the next persona. Do NOT spawn
+  sub-agents (no `task` tool dispatch) -- the panel is a sequence of
+  reasoning passes inside one agent loop, not a multi-agent fan-out.
+- Persona detail lives in the linked `.agent.md` files. Read each
+  one when you switch to that persona; do not pre-load all of them.
 
 ## Execution checklist
 
 When this skill is activated for a PR review, work through these
-steps in order. Do not skip ahead and do not emit any output before
-the final step.
+steps in order, in a single agent loop. Do not skip ahead and do not
+emit any output before the final step.
 
 1. Read the PR context (title, body, labels, changed files, diff).
    The orchestrating workflow already fetches this with `gh pr view`
    / `gh pr diff` -- do not re-fetch.
 2. Resolve the **Auth Expert conditional case** using the rule in
    "Conditional panelist: Auth Expert" above. Record either an
-   activation decision (and proceed to dispatch in step 3) or an
-   `Auth Expert inactive reason: <one sentence>` in working notes.
-3. Execute the **Dispatch contract** (below) for each mandatory
-   persona, plus `auth-expert` if step 2 activated it. One sub-agent
-   per persona, one at a time. Do NOT try to play multiple personas
-   in one reasoning pass.
+   activation decision (and proceed to step 3) or an `Auth Expert
+   inactive reason: <one sentence>` in working notes.
+3. For each mandatory persona (plus `auth-expert` if activated),
+   follow the **Persona pass procedure** below, one persona at a
+   time. Do not try to play multiple personas in a single pass.
 4. Run the **pre-arbitration completeness gate**:
-   - Findings exist for the 5 mandatory specialists (Python
-     Architect, CLI Logging Expert, DevX UX Expert, Supply Chain
-     Security Expert, OSS Growth Hacker).
+   - Findings exist in working notes for the 5 mandatory specialists
+     (Python Architect, CLI Logging Expert, DevX UX Expert, Supply
+     Chain Security Expert, OSS Growth Hacker).
    - Exactly one of `Auth Expert findings` or `Auth Expert inactive
-     reason` exists in working notes (neither = incomplete; both =
-     inconsistent routing).
-   - The Python Architect return contains the OO / class mermaid
+     reason` exists (neither = incomplete; both = inconsistent
+     routing).
+   - The Python Architect notes contain the OO / class mermaid
      diagram, the execution-flow mermaid diagram, and the Design
      patterns subsection declared in
      `../../agents/python-architect.agent.md`.
-   - No persona return is missing or empty.
-   If any check fails, re-invoke the missing persona and repeat the
-   gate. Do not proceed to step 5 until the gate passes.
-5. Run the CEO arbitration pass over the collected findings **as
-   yourself** (the orchestrator). Do NOT dispatch a separate sub-agent
-   for arbitration -- you are the arbiter. CEO arbitration may run
+   - No persona section is missing or empty.
+   If any check fails, redo that persona's pass and repeat the gate.
+   Do not proceed to step 5 until the gate passes.
+5. Take the **APM CEO** lens (load
+   `../../agents/apm-ceo.agent.md`) and arbitrate over the collected
+   findings -- still in your own context. CEO arbitration may run
    only after the completeness gate has passed.
 6. Now (and only now) load `assets/verdict-template.md` and fill it
    in with the collected findings + arbitration.
 7. Emit the filled template as exactly ONE comment via the workflow's
-   `safe-outputs.add-comment` channel. You (the orchestrator) write
-   the comment; never delegate emission to a sub-agent and never call
-   the GitHub API directly.
-
-### Dispatch contract
-
-For each persona being dispatched, run this exact procedure:
-
-1. Dispatch one sub-agent for that persona only -- never chain
-   multiple personas inside a single sub-agent invocation.
-2. Pass only:
-   - the PR title and body summary,
-   - the relevant diff context for that persona's scope,
-   - why this persona is in scope (or, for Auth Expert, the rule
-     that activated it),
-   - the required return shape (findings only; never the final
-     comment text and never top-level verdict headings).
-3. Capture the raw return in working notes under
-   `<persona-name>: <findings>` or, for an inactive Auth Expert,
-   `Auth Expert inactive reason: <one sentence>`.
-4. Do not summarise unopened persona files yourself; do not paste
-   persona file contents into the orchestrator context.
+   `safe-outputs.add-comment` channel. Never call the GitHub API
+   directly. This is the ONLY output emission for the entire panel
+   run -- no per-persona comments, no progress comments.
+
+### Persona pass procedure
+
+For each persona, run this exact procedure in your own context:
+
+1. Open the persona's `.agent.md` file (linked in the roster) and
+   read its scope, lens, anti-patterns, and required return shape.
+2. From that persona's lens, review the PR title/body/diff against
+   the scope declared in the file.
+3. Write the findings to working notes under
+   `<persona-name>: <findings>` (or, for an inactive Auth Expert,
+   `Auth Expert inactive reason: <one sentence>`).
+4. Drop the persona lens before moving on. Do not emit any comment
+   from inside a persona pass; persona findings stay in working
+   notes until step 7 synthesizes them.
 
 ## Output contract
 
@@ -254,13 +253,11 @@ into per-persona noise.
   as a fallback. The asset path is the same relative to the skill
   root (`assets/verdict-template.md`) in both layouts -- prefer the
   `.github/...` path when present.
-- **No persona simulation in the orchestrator thread, and no persona
-  pre-loading.** Each persona has its own `.agent.md` for a reason
-  -- spinning up a sub-agent invocation gives that persona a fresh,
-  focused context window. Pasting persona file contents into the
-  orchestrator, or trying to be all personas in one reasoning pass,
-  is the most common cause of dropped findings, mixed voices, and
-  per-persona comment spillover.
+- **No multi-persona-in-one-pass.** Each persona has its own
+  `.agent.md` for a reason -- read it when you take that lens, write
+  the findings, then drop the lens before moving on. Trying to be all
+  personas in one reasoning pass is the most common cause of dropped
+  findings and mixed voices.
 - **Single-emission discipline is fragile under interruption.** If
   you find yourself wanting to "post a quick partial verdict and
   then update it", don't. Buffer in working notes; emit once.
diff --git a/.github/skills/apm-review-panel/SKILL.md b/.github/skills/apm-review-panel/SKILL.md
@@ -9,10 +9,12 @@ description: >-
 
 # APM Review Panel -- Expert Review Orchestration
 
-The panel is fixed at **5 mandatory specialists + 1 conditional auth
-specialist + 1 arbiter = up to 7 agents producing 7 verdict blocks**.
-Routing chooses *which* personas execute; it never changes which
-headings appear in the final verdict.
+The panel is fixed at **5 mandatory specialist lenses + 1 conditional
+auth lens + 1 arbiter lens = up to 7 persona sections in one verdict
+comment**. You play each lens in turn from inside a single agent loop
+(progressive-disclosure skill model -- no sub-agent dispatch). Routing
+chooses *which* lenses execute; it never changes which headings appear
+in the final verdict.
 
 ## Agent roster
 
@@ -50,8 +52,8 @@ headings appear in the final verdict.
 Auth Expert is the only conditional panelist. Activate `auth-expert`
 if either rule below matches.
 
-1. **Fast-path file trigger.** Dispatch immediately when the PR
-   changes any of:
+1. **Fast-path file trigger.** Activate the Auth Expert lens
+   immediately when the PR changes any of:
    - `src/apm_cli/core/auth.py`
    - `src/apm_cli/core/token_manager.py`
    - `src/apm_cli/core/azure_cli.py`
@@ -62,7 +64,7 @@ if either rule below matches.
    - `src/apm_cli/deps/registry_proxy.py`
 
 2. **Fallback self-check.** If no fast-path file matched, answer this
-   before dispatch:
+   before activating the lens:
 
    > Does this PR change authentication behavior, token management,
    > credential resolution, host classification used by `AuthResolver`,
@@ -72,9 +74,10 @@ if either rule below matches.
 
 Routing rule:
 
-- **YES** -> dispatch `auth-expert` and capture its findings.
+- **YES** -> take the Auth Expert lens (per the Persona pass
+  procedure) and capture its findings.
 - **NO**  -> record `Auth Expert inactive reason: <one sentence
-  citing the touched files>` in working notes; do not dispatch.
+  citing the touched files>` in working notes; do not take the lens.
 - Never use wildcard heuristics like `*auth*`, `*token*`, or
   `*credential*` as the sole trigger.
 
@@ -145,74 +148,70 @@ A non-trivial change passes when:
 
 ## Notes
 
-- **Do not open linked persona files in the orchestrator thread.**
-  Treat the roster links as dispatch targets only -- each sub-agent
-  loads its own `.agent.md` in its own context window. Pre-loading
-  persona content into the orchestrator defeats Reduced Scope and
-  Progressive Disclosure.
-- This skill orchestrates only; persona detail lives in the linked
-  `.agent.md` files.
+- This skill orchestrates a panel **in your own context** -- you are
+  the only agent. You load each persona's `.agent.md` reference file
+  on demand (progressive disclosure), assume that persona's lens to
+  produce its findings, then move to the next persona. Do NOT spawn
+  sub-agents (no `task` tool dispatch) -- the panel is a sequence of
+  reasoning passes inside one agent loop, not a multi-agent fan-out.
+- Persona detail lives in the linked `.agent.md` files. Read each
+  one when you switch to that persona; do not pre-load all of them.
 
 ## Execution checklist
 
 When this skill is activated for a PR review, work through these
-steps in order. Do not skip ahead and do not emit any output before
-the final step.
+steps in order, in a single agent loop. Do not skip ahead and do not
+emit any output before the final step.
 
 1. Read the PR context (title, body, labels, changed files, diff).
    The orchestrating workflow already fetches this with `gh pr view`
    / `gh pr diff` -- do not re-fetch.
 2. Resolve the **Auth Expert conditional case** using the rule in
    "Conditional panelist: Auth Expert" above. Record either an
-   activation decision (and proceed to dispatch in step 3) or an
-   `Auth Expert inactive reason: <one sentence>` in working notes.
-3. Execute the **Dispatch contract** (below) for each mandatory
-   persona, plus `auth-expert` if step 2 activated it. One sub-agent
-   per persona, one at a time. Do NOT try to play multiple personas
-   in one reasoning pass.
+   activation decision (and proceed to step 3) or an `Auth Expert
+   inactive reason: <one sentence>` in working notes.
+3. For each mandatory persona (plus `auth-expert` if activated),
+   follow the **Persona pass procedure** below, one persona at a
+   time. Do not try to play multiple personas in a single pass.
 4. Run the **pre-arbitration completeness gate**:
-   - Findings exist for the 5 mandatory specialists (Python
-     Architect, CLI Logging Expert, DevX UX Expert, Supply Chain
-     Security Expert, OSS Growth Hacker).
+   - Findings exist in working notes for the 5 mandatory specialists
+     (Python Architect, CLI Logging Expert, DevX UX Expert, Supply
+     Chain Security Expert, OSS Growth Hacker).
    - Exactly one of `Auth Expert findings` or `Auth Expert inactive
-     reason` exists in working notes (neither = incomplete; both =
-     inconsistent routing).
-   - The Python Architect return contains the OO / class mermaid
+     reason` exists (neither = incomplete; both = inconsistent
+     routing).
+   - The Python Architect notes contain the OO / class mermaid
      diagram, the execution-flow mermaid diagram, and the Design
      patterns subsection declared in
      `../../agents/python-architect.agent.md`.
-   - No persona return is missing or empty.
-   If any check fails, re-invoke the missing persona and repeat the
-   gate. Do not proceed to step 5 until the gate passes.
-5. Run the CEO arbitration pass over the collected findings **as
-   yourself** (the orchestrator). Do NOT dispatch a separate sub-agent
-   for arbitration -- you are the arbiter. CEO arbitration may run
+   - No persona section is missing or empty.
+   If any check fails, redo that persona's pass and repeat the gate.
+   Do not proceed to step 5 until the gate passes.
+5. Take the **APM CEO** lens (load
+   `../../agents/apm-ceo.agent.md`) and arbitrate over the collected
+   findings -- still in your own context. CEO arbitration may run
    only after the completeness gate has passed.
 6. Now (and only now) load `assets/verdict-template.md` and fill it
    in with the collected findings + arbitration.
 7. Emit the filled template as exactly ONE comment via the workflow's
-   `safe-outputs.add-comment` channel. You (the orchestrator) write
-   the comment; never delegate emission to a sub-agent and never call
-   the GitHub API directly.
-
-### Dispatch contract
-
-For each persona being dispatched, run this exact procedure:
-
-1. Dispatch one sub-agent for that persona only -- never chain
-   multiple personas inside a single sub-agent invocation.
-2. Pass only:
-   - the PR title and body summary,
-   - the relevant diff context for that persona's scope,
-   - why this persona is in scope (or, for Auth Expert, the rule
-     that activated it),
-   - the required return shape (findings only; never the final
-     comment text and never top-level verdict headings).
-3. Capture the raw return in working notes under
-   `<persona-name>: <findings>` or, for an inactive Auth Expert,
-   `Auth Expert inactive reason: <one sentence>`.
-4. Do not summarise unopened persona files yourself; do not paste
-   persona file contents into the orchestrator context.
+   `safe-outputs.add-comment` channel. Never call the GitHub API
+   directly. This is the ONLY output emission for the entire panel
+   run -- no per-persona comments, no progress comments.
+
+### Persona pass procedure
+
+For each persona, run this exact procedure in your own context:
+
+1. Open the persona's `.agent.md` file (linked in the roster) and
+   read its scope, lens, anti-patterns, and required return shape.
+2. From that persona's lens, review the PR title/body/diff against
+   the scope declared in the file.
+3. Write the findings to working notes under
+   `<persona-name>: <findings>` (or, for an inactive Auth Expert,
+   `Auth Expert inactive reason: <one sentence>`).
+4. Drop the persona lens before moving on. Do not emit any comment
+   from inside a persona pass; persona findings stay in working
+   notes until step 7 synthesizes them.
 
 ## Output contract
 
@@ -254,13 +253,11 @@ into per-persona noise.
   as a fallback. The asset path is the same relative to the skill
   root (`assets/verdict-template.md`) in both layouts -- prefer the
   `.github/...` path when present.
-- **No persona simulation in the orchestrator thread, and no persona
-  pre-loading.** Each persona has its own `.agent.md` for a reason
-  -- spinning up a sub-agent invocation gives that persona a fresh,
-  focused context window. Pasting persona file contents into the
-  orchestrator, or trying to be all personas in one reasoning pass,
-  is the most common cause of dropped findings, mixed voices, and
-  per-persona comment spillover.
+- **No multi-persona-in-one-pass.** Each persona has its own
+  `.agent.md` for a reason -- read it when you take that lens, write
+  the findings, then drop the lens before moving on. Trying to be all
+  personas in one reasoning pass is the most common cause of dropped
+  findings and mixed voices.
 - **Single-emission discipline is fragile under interruption.** If
   you find yourself wanting to "post a quick partial verdict and
   then update it", don't. Buffer in working notes; emit once.
PATCH

echo "Gold patch applied."
