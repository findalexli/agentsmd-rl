#!/usr/bin/env bash
set -euo pipefail

cd /workspace/auto-claude-code-research-in-sleep

# Idempotency guard
if grep -qF "description: Use when main results pass result-to-claim (claim_supported=yes or " "skills/ablation-planner/SKILL.md" && grep -qF "description: Use when experiments complete to judge what claims the results supp" "skills/result-to-claim/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/ablation-planner/SKILL.md b/skills/ablation-planner/SKILL.md
@@ -0,0 +1,122 @@
+---
+name: ablation-planner
+description: Use when main results pass result-to-claim (claim_supported=yes or partial) and ablation studies are needed for paper submission. Codex designs ablations from a reviewer's perspective, CC reviews feasibility and implements.
+argument-hint: [method-description-or-claim]
+allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, mcp__codex__codex, mcp__codex__codex-reply
+---
+
+# Ablation Planner
+
+Systematically design ablation studies that answer the questions reviewers will ask. Codex leads the design (reviewer perspective), CC reviews feasibility and implements.
+
+## Context: $ARGUMENTS
+
+## When to Use
+
+- Main results pass `/result-to-claim` with claim_supported = yes or partial
+- User explicitly requests ablation planning
+- `/auto-review-loop` reviewer identifies missing ablations
+
+## Workflow
+
+### Step 1: Prepare Context
+
+CC reads available project files to build the full picture:
+- Method description and components (from docs/research_contract.md or project CLAUDE.md)
+- Current experiment results (from EXPERIMENT_LOG.md, EXPERIMENT_TRACKER.md, or W&B)
+- Confirmed and intended claims (from result-to-claim output or project notes)
+- Available compute resources (from CLAUDE.md server config, if present)
+
+### Step 2: Codex Designs Ablations
+
+```
+mcp__codex__codex:
+  config: {"model_reasoning_effort": "xhigh"}
+  prompt: |
+    You are a rigorous ML reviewer planning ablation studies.
+    Given this method and results, design ablations that:
+
+    1. Isolate the contribution of each novel component
+    2. Answer questions reviewers will definitely ask
+    3. Test sensitivity to key hyperparameters
+    4. Compare against natural alternative design choices
+
+    Method: [description from project files]
+    Components: [list of removable/replaceable components]
+    Current results: [key metrics from experiments]
+    Claims: [what we claim and current evidence]
+
+    For each ablation, specify:
+    - name: what to change (e.g., "remove module X", "replace Y with Z")
+    - what_it_tests: the specific question this answers
+    - expected_if_component_matters: what we predict if the component is important
+    - priority: 1 (must-run) to 5 (nice-to-have)
+
+    Also provide:
+    - coverage_assessment: what reviewer questions these ablations answer
+    - unnecessary_ablations: experiments that seem useful but won't add insight
+    - suggested_order: run order optimized for maximum early information
+    - estimated_compute: total GPU-hours estimate
+```
+
+### Step 3: Parse Ablation Plan
+
+Normalize Codex response into structured format:
+
+```markdown
+## Ablation Plan
+
+### Component Ablations (highest priority)
+| # | Name | What It Tests | Expected If Matters | Priority |
+|---|------|---------------|---------------------|----------|
+| 1 | remove module X | contribution of X | performance drops on metric Y | 1 |
+| 2 | replace X with simpler Z | value of learned vs fixed | drops, especially on dataset A | 2 |
+
+### Hyperparameter Sensitivity
+| # | Parameter | Values to Test | What It Tests | Priority |
+|---|-----------|---------------|---------------|----------|
+| 3 | lambda | [0.01, 0.1, 1.0] | sensitivity to regularization | 3 |
+
+### Design Choice Comparisons
+| # | Name | What It Tests | Priority |
+|---|------|---------------|----------|
+| 4 | joint vs separate matching | whether joint adds value | 4 |
+
+### Coverage Assessment
+[What reviewer questions these ablations answer]
+
+### Unnecessary Ablations
+[Experiments that seem useful but won't add insight — skip these]
+
+### Run Order
+[Optimized for maximum early information]
+
+### Estimated Compute
+[Total GPU-hours]
+```
+
+### Step 4: CC Reviews Feasibility
+
+Before running anything, CC checks:
+- Compute budget: can we afford all ablations with available GPUs?
+- Code changes: which ablations need code modifications vs config-only changes?
+- Dependencies: which ablations can run in parallel?
+- Cuts: if budget is tight, propose removing lower-priority ablations and ask Codex to confirm
+
+### Step 5: Implement and Run
+
+1. Create configs/scripts for each ablation (config-only changes first)
+2. Smoke test each ablation before full run
+3. Run in suggested order, using descriptive names (e.g., `ablation-no-module-X`)
+4. Track results in EXPERIMENT_LOG.md
+5. After all ablations complete → update findings.md with insights
+
+## Rules
+
+- **Codex leads the design. CC does not pre-filter or bias the ablation list** before Codex sees it. Codex thinks like a reviewer; CC thinks like an engineer.
+- Every ablation must have a clear `what_it_tests` and `expected_if_component_matters`. No "just try it" experiments.
+- Config-only ablations take priority over those needing code changes (faster, less error-prone).
+- If total compute exceeds budget, CC proposes cuts and asks Codex to re-prioritize — don't silently drop ablations.
+- Component ablations (remove/replace) take priority over hyperparameter sweeps.
+- Do not generate ablations for components identical to the baseline (no-op ablations).
+- Record all ablation results in EXPERIMENT_LOG.md, including negative results (component removal had no effect = important finding).
diff --git a/skills/result-to-claim/SKILL.md b/skills/result-to-claim/SKILL.md
@@ -0,0 +1,122 @@
+---
+name: result-to-claim
+description: Use when experiments complete to judge what claims the results support, what they don't, and what evidence is still missing. Codex MCP evaluates results against intended claims and routes to next action (pivot, supplement, or confirm). Use after experiments finish — before writing the paper or running ablations.
+argument-hint: [experiment-description-or-wandb-run]
+allowed-tools: Bash(*), Read, Grep, Glob, Write, Edit, mcp__codex__codex, mcp__codex__codex-reply
+---
+
+# Result-to-Claim Gate
+
+Experiments produce numbers; this gate decides what those numbers *mean*. Collect results from available sources, get a Codex judgment, then auto-route based on the verdict.
+
+## Context: $ARGUMENTS
+
+## When to Use
+
+- After a set of experiments completes (main results, not just sanity checks)
+- Before committing to claims in a paper or review response
+- When results are ambiguous and you need an objective second opinion
+
+## Workflow
+
+### Step 1: Collect Results
+
+Gather experiment data from whatever sources are available in the project:
+
+1. **W&B** (preferred): `wandb.Api().run("<entity>/<project>/<run_id>").history()` — metrics, training curves, comparisons
+2. **EXPERIMENT_LOG.md**: full results table with baselines and verdicts
+3. **EXPERIMENT_TRACKER.md**: check which experiments are DONE vs still running
+4. **Log files**: `ssh server "tail -100 /path/to/training.log"` if no other source
+5. **docs/research_contract.md**: intended claims and experiment design
+
+Assemble the key information:
+- What experiments were run (method, dataset, config)
+- Main metrics and baseline comparisons (deltas)
+- The intended claim these experiments were designed to test
+- Any known confounds or caveats
+
+### Step 2: Codex Judgment
+
+Send the collected results to Codex for objective evaluation:
+
+```
+mcp__codex__codex:
+  config: {"model_reasoning_effort": "xhigh"}
+  prompt: |
+    RESULT-TO-CLAIM EVALUATION
+
+    I need you to judge whether experimental results support the intended claim.
+
+    Intended claim: [the claim these experiments test]
+
+    Experiments run:
+    [list experiments with method, dataset, metrics]
+
+    Results:
+    [paste key numbers, comparison deltas, significance]
+
+    Baselines:
+    [baseline numbers and sources — reproduced or from paper]
+
+    Known caveats:
+    [any confounding factors, limited datasets, missing comparisons]
+
+    Please evaluate:
+    1. claim_supported: yes | partial | no
+    2. what_results_support: what the data actually shows
+    3. what_results_dont_support: where the data falls short of the claim
+    4. missing_evidence: specific evidence gaps
+    5. suggested_claim_revision: if the claim should be strengthened, weakened, or reframed
+    6. next_experiments_needed: specific experiments to fill gaps (if any)
+    7. confidence: high | medium | low
+
+    Be honest. Do not inflate claims beyond what the data supports.
+    A single positive result on one dataset does not support a general claim.
+```
+
+### Step 3: Parse and Normalize
+
+Extract structured fields from Codex response:
+
+```markdown
+- claim_supported: yes | partial | no
+- what_results_support: "..."
+- what_results_dont_support: "..."
+- missing_evidence: "..."
+- suggested_claim_revision: "..."
+- next_experiments_needed: "..."
+- confidence: high | medium | low
+```
+
+### Step 4: Route Based on Verdict
+
+#### `no` — Claim not supported
+
+1. Record postmortem in findings.md (Research Findings section):
+   - What was tested, what failed, hypotheses for why
+   - Constraints for future attempts (what NOT to try again)
+2. Update CLAUDE.md Pipeline Status
+3. Decide whether to pivot to next idea from IDEA_CANDIDATES.md or try an alternative approach
+
+#### `partial` — Claim partially supported
+
+1. Update the working claim to reflect what IS supported
+2. Record the gap in findings.md
+3. Design and run supplementary experiments to fill evidence gaps
+4. Re-run result-to-claim after supplementary experiments complete
+5. **Multiple rounds of `partial` on the same claim** → record analysis in findings.md, consider whether to narrow the claim scope or switch ideas
+
+#### `yes` — Claim supported
+
+1. Record confirmed claim in project notes
+2. If ablation studies are incomplete → trigger `/ablation-planner`
+3. If all evidence is in → ready for paper writing
+
+## Rules
+
+- **Codex is the judge, not CC.** CC collects evidence and routes; Codex evaluates. This prevents post-hoc rationalization.
+- Do not inflate claims beyond what the data supports. If Codex says "partial", do not round up to "yes".
+- A single positive result on one dataset does not support a general claim. Be honest about scope.
+- If `confidence` is low, treat the judgment as inconclusive and add experiments rather than committing to a claim.
+- If Codex MCP is unavailable (call fails), CC makes its own judgment and marks it `[pending Codex review]` — do not block the pipeline.
+- Always record the verdict and reasoning in findings.md, regardless of outcome.
PATCH

echo "Gold patch applied."
