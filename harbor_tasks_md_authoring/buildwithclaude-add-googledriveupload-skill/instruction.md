# Add google-drive-upload skill

Source: [davepoon/buildwithclaude#84](https://github.com/davepoon/buildwithclaude/pull/84)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/all-skills/skills/google-drive-upload/SKILL.md`

## What to add / change

## Summary

Adds a new **google-drive-upload** skill that lets users upload files directly from Claude to Google Drive via a simple Google Apps Script.

- No OAuth flow or complex API setup required
- One-time 5-minute setup with Google Apps Script
- Supports folder targeting, Hebrew filenames, file replacement
- Works with any file type up to 50MB

## Component Details

- **Name**: google-drive-upload
- **Type**: Skill
- **Category**: automation

## Testing

- [x] Tested functionality - uploads work via deployed Apps Script
- [x] No overlap with existing components (no Drive upload skill exists)
- [x] Full plugin with setup guide: https://github.com/msmobileapps/google-drive-upload-plugin

## Examples

1. "Upload this report to Google Drive"
2. "Save the presentation in Clients/Acme on Drive"
3. "תעלה את זה לדרייב" (Hebrew support)

Built by [MSApps](https://msapps.mobi) — AI Automation & Application Development

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
