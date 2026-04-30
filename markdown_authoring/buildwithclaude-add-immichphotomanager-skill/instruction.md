# Add immich-photo-manager skill

Source: [davepoon/buildwithclaude#113](https://github.com/davepoon/buildwithclaude/pull/113)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/immich-photo-manager/SKILL.md`

## What to add / change

## Summary
Claude Code plugin that connects to self-hosted Immich photo libraries for AI-powered management — search, album curation, duplicate detection, and health audits through natural conversation.

## Component Details
- **Name**: immich-photo-manager
- **Type**: Skill
- **Category**: specialized-domains

## Testing
- [x] Ran validation (`npm test`) — all passed
- [x] Tested functionality with live Immich instance
- [x] No overlap with existing components
- [x] Plugin scanner: 100/100 (A - Excellent)

## Examples

```
"How healthy is my photo library?"
→ Scans 28,000 assets, reports metadata coverage, storage breakdown, recommendations

"Create albums for everywhere I've traveled"
→ GPS clustering creates dozens of geographic albums automatically

"Find duplicates"
→ Perceptual hashing catches re-encoded copies across Apple Photos and Google Takeout imports
```

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
