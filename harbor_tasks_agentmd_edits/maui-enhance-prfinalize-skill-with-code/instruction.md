# Enhance pr-finalize Skill with Code Review Phase and Safety Rules

## Problem

The `pr-finalize` skill (`.github/skills/pr-finalize/SKILL.md`) currently only verifies that PR titles and descriptions match the actual implementation. It has no code review capability and no safety guardrails to prevent AI agents from approving or blocking PRs.

The `Review-PR.ps1` script (`.github/scripts/Review-PR.ps1`) runs in interactive mode by default and has no way to chain additional skills (like pr-finalize or ai-summary-comment) after the main PR agent review completes. It also lacks safety rules preventing agents from modifying git state.

The `post-pr-finalize-comment.ps1` script only supports Title and Description sections in the PR finalization comment — there's no way to include code review findings.

## Expected Behavior

1. **pr-finalize SKILL.md** should define a two-phase workflow: (1) Title & Description review, and (2) Code Review for best practices. It must include critical safety rules: agents must NEVER use `--approve` or `--request-changes` flags on PRs, and must NEVER post comments directly (analysis only — posting is done via the ai-summary-comment skill).

2. **Review-PR.ps1** should:
   - Default to non-interactive mode (with an opt-in `-Interactive` switch instead of the current `-NoInteractive` opt-out)
   - Support `-RunFinalize` to chain the pr-finalize skill after the main review
   - Support `-PostSummaryComment` to chain the ai-summary-comment skill after all phases
   - Include git safety rules in the agent prompt (never checkout, push, reset, etc.)

3. **post-pr-finalize-comment.ps1** should accept `-CodeReviewStatus` and `-CodeReviewFindings` parameters, and build a third collapsible Code Review section in the PR comment alongside Title and Description.

4. **copilot-instructions.md** should update the pr-finalize skill description to mention code review, and add a CRITICAL note about never using `--approve` or `--request-changes`.

5. **ai-summary-comment SKILL.md** should document the updated three-section format (Title, Description, Code Review) and document the PR Finalize Comment Script usage.

## Files to Look At

- `.github/skills/pr-finalize/SKILL.md` — skill definition, needs two-phase workflow and safety rules
- `.github/scripts/Review-PR.ps1` — PR review orchestration script, needs new params and safety rules
- `.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1` — comment builder, needs Code Review section
- `.github/copilot-instructions.md` — agent instructions, needs updated pr-finalize description
- `.github/skills/ai-summary-comment/SKILL.md` — skill docs, needs three-section documentation
