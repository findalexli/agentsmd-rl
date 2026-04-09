# Simplify PR Finalize Comment to Two Collapsible Sections

## Problem

The `post-pr-finalize-comment.ps1` script currently creates PR finalization comments with per-review collapsible sections (Review 1, Review 2, etc.) that accumulate over time. This format:
1. Creates clutter on PRs with multiple reviews
2. Uses legacy parameters `ReviewNumber` and `ReviewDescription` that complicate the API
3. Merges new reviews with old content instead of replacing them
4. Lacks a direct way to specify title issues when not using a summary file

## Expected Behavior

Refactor `post-pr-finalize-comment.ps1` to:
1. Create a single PR finalization comment with two dedicated collapsible sections:
   - **Title section**: Shows current title, issues (if any), and recommended title
   - **Description section**: Shows assessment, missing elements, and suggested description
2. Remove `ReviewNumber` and `ReviewDescription` parameters (no longer needed)
3. Add `TitleIssues` parameter for direct specification of title problems
4. Replace the "merge reviews" behavior with complete comment replacement
5. Update `TitleStatus` auto-detection to look for explicit status in Title Assessment section
6. Update SKILL.md documentation to reflect the new format

## Files to Look At

- `.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1` — Main script that needs refactoring
- `.github/skills/ai-summary-comment/SKILL.md` — Documentation that describes the old format

## Key Changes Required

### In post-pr-finalize-comment.ps1:
1. Remove `ReviewNumber` and `ReviewDescription` from parameters
2. Add `TitleIssues` parameter
3. Simplify auto-detection logic (remove review number detection, change TitleStatus detection)
4. Build two separate `$titleSection` and `$descSection` instead of single `$reviewSection`
5. Replace comment body construction to use `$titleSection` + `$descSection` instead of accumulating reviews
6. Remove overall status calculation
7. Update parameter validation (remove ReviewDescription requirement)

### In SKILL.md:
1. Update "Separate PR Finalization Comment" section to describe the new two-section format
2. Remove references to numbered reviews
