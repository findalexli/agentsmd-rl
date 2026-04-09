# Enhance pr-finalize skill with code review phase and safety rules

## Problem

The pr-finalize skill currently only verifies PR title and description match the implementation. It lacks:
1. A code review phase to catch best practice violations before merge
2. Safety rules preventing AI agents from approving or requesting changes on PRs
3. Integration with Review-PR.ps1 script for multi-phase workflows

The post-pr-finalize-comment.ps1 script only supports Title and Description sections, not Code Review findings.

## Expected Behavior

1. **pr-finalize SKILL.md** should include:
   - Two-phase workflow (Title/Description + Code Review)
   - CRITICAL rules: NEVER use `--approve` or `--request-changes`
   - Code review focus areas and output format

2. **Review-PR.ps1** should:
   - Change default from interactive to non-interactive mode
   - Replace `-NoInteractive` switch with `-Interactive` switch
   - Add `-RunFinalize` and `-PostSummaryComment` switches
   - Add git safety rules (NEVER run git checkout/push)
   - Support 3-phase workflow display

3. **post-pr-finalize-comment.ps1** should:
   - Add `CodeReviewStatus` parameter (Passed/IssuesFound/Skipped)
   - Add `CodeReviewFindings` parameter
   - Include third collapsible section for code review
   - Auto-extract code review from summary file or code-review.md

4. **ai-summary-comment/SKILL.md** should document the new Code Review section

5. **copilot-instructions.md** should update pr-finalize skill description

## Files to Modify

- `.github/skills/pr-finalize/SKILL.md` — Add code review phase and safety rules
- `.github/scripts/Review-PR.ps1` — Refactor interactive mode, add phase switches
- `.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1` — Add code review section
- `.github/skills/ai-summary-comment/SKILL.md` — Document code review parameters
- `.github/copilot-instructions.md` — Update pr-finalize description and safety note
