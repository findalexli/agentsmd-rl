# Remove Redundant Tests Phase from PR Agent Workflow

## Problem

The PR agent workflow in `.github/agents/pr.md` currently has 5 phases: Pre-Flight, Tests, Gate, Fix, Report. The "Tests" phase (Phase 2) is redundant with the Gate phase — Gate already fails if tests don't exist or don't catch the bug, and test creation can be invoked from Gate if needed. This adds unnecessary complexity and cognitive overhead to the workflow.

## Expected Behavior

The workflow should be simplified to 4 phases by removing the standalone Tests phase:

1. **Pre-Flight** — Context gathering
2. **Gate** — Verify tests exist and catch the issue (absorbs the essential checks from the old Tests phase)
3. **Fix** — Multi-model fix exploration
4. **Report** — Final recommendation

All phase numbering, references, and documentation across the repository must be updated consistently. The PowerShell scripts that process phase data must also be updated to remove Tests phase handling.

## Files to Look At

- `.github/agents/pr.md` — Main PR agent definition (phases 1-2, was 1-3)
- `.github/agents/pr/PLAN-TEMPLATE.md` — Reusable checklist for the workflow
- `.github/agents/pr/post-gate.md` — Post-gate phases (now 3-4, was 4-5)
- `.github/README-AI.md` — Documentation for AI agents
- `.github/copilot-instructions.md` — Copilot agent descriptions
- `.github/scripts/Review-PR.ps1` — Script that launches the PR review workflow
- `.github/skills/ai-summary-comment/` — Skills that process and display phase data (scripts, SKILL.md, IMPROVEMENTS.md, NO-EXTERNAL-REFERENCES-RULE.md)

After making the code changes, update all relevant documentation and agent instruction files to reflect the simplified 4-phase workflow. Every reference to "5-phase", "Phase 2: Tests", or the old phase numbering should be corrected.
