# fix(ai-workflow): finalize linked issue after PR merge

Source: [bitsocialnet/5chan#1047](https://github.com/bitsocialnet/5chan/pull/1047)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.codex/skills/review-and-merge-pr/SKILL.md`
- `.cursor/skills/review-and-merge-pr/SKILL.md`

## What to add / change

Add the missing post-merge cleanup step to the tracked review-and-merge skill.

- verify the PR's linked issue actually closed after merge
- close the linked issue manually if automation did not
- ensure the linked issue's project item is present and moved to `Done`
- report linked issue/project finalization explicitly in the merge summary

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk documentation/workflow-only changes; no production code paths or data handling are modified.
> 
> **Overview**
> Enhances the `review-and-merge-pr` skill by adding an explicit post-merge step to **verify the PR’s linked closing issue is closed**, close it manually if needed, and ensure the related `5chan` project item exists and is moved to `Done` (with `gh`/`jq` command examples).
> 
> Updates the skill metadata and renumbers the workflow so the final report now includes whether the linked issue was confirmed closed and the project item was confirmed `Done`.
> 
> <sup>Written by [Cursor Bugbot](https://cursor.com/dashboard?tab=bugbot) for commit a5258051107bfe167a31a6597a69ab81970d9a2c. This will update automatically on new commits. Configure [here](https://cursor.com/dashboard?tab=bugbot).</sup>
<!-- /CURSOR_SUMMARY -->

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

## Release Notes

* **Documentation**
  * Enhanced the PR review and merge workflow guide with clearer post-merge procedures, including automated steps for

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
