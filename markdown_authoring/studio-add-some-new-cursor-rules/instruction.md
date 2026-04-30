# Add some new cursor rules on native apps

Source: [decocms/studio#1644](https://github.com/decocms/studio/pull/1644)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/api-development.mdc`
- `.cursor/rules/data-flow.mdc`
- `.cursor/rules/native-apps-and-views.mdc`
- `.cursor/rules/react-ts.mdc`

## What to add / change

<!-- deno-fmt-ignore-file -->

## What is this contribution about?
> Describe your changes and why they're needed.

## Screenshots/Demonstration
> Add screenshots or a Loom video if your changes affect the UI.

## Review Checklist
- [ ] PR title is clear and descriptive
- [ ] Changes are tested and working
- [ ] Documentation is updated (if needed)
- [ ] No breaking changes 

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added return-type safety guidance: prefer object returns and examples for wrapping nullable values.
  * Clarified organization-context handling, slug-based authorization, and including locator in scoped API calls.
  * Introduced virtual-integration/tool-group patterns, native-app and AI-chat integration guidance, and real-time/react patterns (immediate DOM updates, undo/redo, cross-component events).
  * Updated database guidance (Drizzle preferred; notes on legacy Supabase) and performance best practices (caching, deduplication, pagination).
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
