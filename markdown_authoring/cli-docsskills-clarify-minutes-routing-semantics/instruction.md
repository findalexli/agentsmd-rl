# docs(skills): clarify minutes routing semantics

Source: [larksuite/cli#591](https://github.com/larksuite/cli/pull/591)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/lark-minutes/SKILL.md`
- `skills/lark-minutes/references/lark-minutes-download.md`
- `skills/lark-minutes/references/lark-minutes-search.md`
- `skills/lark-vc/SKILL.md`
- `skills/lark-vc/references/lark-vc-recording.md`
- `skills/lark-vc/references/lark-vc-search.md`

## What to add / change

## Summary

Clarify the routing between VC meeting notes and minutes metadata in the skill docs.
Also refine the natural-language guidance for "participated minutes" so agents do not under-fetch owner-owned minutes.

## Changes

- clarify that minute metadata requests should route through `vc +recording` and `minutes minutes get`, rather than `vc +notes`
- update the minutes search guidance so "participated minutes" defaults to the union of owner and participant results
- fix the incorrect `minute_token` source in the minutes download reference
- update the VC search/recording references to point to the correct follow-up commands for minutes metadata vs notes content

## Test Plan

- [x] Reviewed the updated skill and reference docs in the branch diff
- [x] Ran `git diff --check`
- [x] Verified the documented command routing with local CLI help / dry-run checks
- [x] Ran `go test ./...`

## Related Issues

- None

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Documentation**
  * Clarified workflows for retrieving meeting minutes metadata and content.
  * Updated command guidance to distinguish between meeting notes and minute information retrieval.
  * Reorganized routing rules to properly separate search, basic info, and transcript/summary queries.
  * Improved documentation on obtaining minute metadata before fetching full content.

<!-- end of auto-generated comment: release notes by coderabbi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
