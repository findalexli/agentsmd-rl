# Strengthen Plan-first enforcement in azure-prepare to prevent deployment pipeline failures

Source: [microsoft/GitHub-Copilot-for-Azure#1760](https://github.com/microsoft/GitHub-Copilot-for-Azure/pull/1760)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugin/skills/azure-prepare/SKILL.md`

## What to add / change

When the agent skips or defers creating `.azure/deployment-plan.md` during `azure-prepare`, both `azure-validate` and `azure-deploy` fail since they depend on that file as their source of truth.

## Changes

**`plugin/skills/azure-prepare/SKILL.md`** (version `1.1.8` → `1.1.11`)

- **Rule #1** — Upgraded from a passive guideline to an explicit `⛔ MANDATORY` directive using a **skeleton-first** approach: write an initial `.azure/deployment-plan.md` skeleton to disk immediately (before any code generation or execution begins), then populate it progressively as Phase 1 analysis and research unfold, and finalize it at Step 6. Names the downstream consequence directly:
  > *"azure-validate and azure-deploy depend on it and will fail without it."*
  This resolves an internal ordering conflict where the previous wording ("before any analysis or research begins") contradicted STEP 0 (Specialized Technology Check) and Phase 1 Steps 1–5, which require analysis before the plan can be finalized.

- **PLAN-FIRST WORKFLOW section** — Updated Step 2 to "CREATE SKELETON" with explicit sequencing: skeleton first → populate via Phase 1 steps 1–5 → finalize at Step 6. Retained the file-write tool requirement and the explicit failure consequence block: *"Skipping the plan file creation will cause azure-validate and azure-deploy to fail. This requirement has no exceptions."*

- **Phase 1 Step 6 (Finalize Plan)** — Relabelled from "Write Plan" to "Finalize Plan" and marked `⛔ (MANDATORY)`. Clarifi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
