# Simplify PR Finalize Comment to Two Collapsible Sections

## Problem

The `post-pr-finalize-comment.ps1` script in `.github/skills/ai-summary-comment/scripts/` currently produces PR finalization comments with numbered review sections (Review 1, Review 2, etc.). Each review is a single collapsible section that mixes title and description assessment together. When a PR is re-reviewed, the script merges the new review alongside existing ones, making the comment grow and become harder to scan.

The format needs to be simplified: instead of numbered per-review collapsible sections, produce exactly **two** collapsible sections — one for the title assessment and one for the description assessment. When the comment is updated, it should fully replace the previous content rather than accumulating reviews.

## Expected Behavior

1. The finalize comment should have two collapsible `<details>` sections: one for **Title** and one for **Description**, each with its own status indicator.
2. The legacy `ReviewNumber` and `ReviewDescription` parameters should be removed since reviews are no longer numbered.
3. A new `TitleIssues` parameter should be added so title issues can be specified directly.
4. The title status auto-detection from summary files should look for an explicit `**Status:**` field in the `Title Assessment` section, rather than inferring from the presence of issues or recommended titles.
5. When an existing finalize comment is found, it should be fully replaced — not merged with previous reviews.
6. The GitHub API call that fetches existing comments should handle PRs with many comments (the current default page size may miss comments).

After making the code changes, update the skill's documentation (`.github/skills/ai-summary-comment/SKILL.md`) to reflect the new two-section format. The "Separate PR Finalization Comment" section currently describes numbered reviews — it should describe the new Title/Description layout instead.

## Files to Look At

- `.github/skills/ai-summary-comment/scripts/post-pr-finalize-comment.ps1` — the PowerShell script that builds and posts the finalize comment
- `.github/skills/ai-summary-comment/SKILL.md` — skill documentation that describes the comment architecture and format
