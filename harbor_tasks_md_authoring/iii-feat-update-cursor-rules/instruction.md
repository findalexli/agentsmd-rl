# feat: update cursor rules

Source: [iii-hq/iii#985](https://github.com/iii-hq/iii/pull/985)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/api-steps.mdc`
- `packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/event-steps.mdc`
- `packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/motia-config.mdc`
- `packages/snap/src/cursor-rules/dot-files/.cursor/rules/motia/realtime-streaming.mdc`

## What to add / change

## Summary
<!-- Provide a short summary of your changes and the motivation behind them. -->

## Related Issues
<!-- List any related issues, e.g. Fixes #123 or Closes #456 -->

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Refactor
- [ ] Other (please describe):

## Checklist
- [ ] I have read the [CONTRIBUTING.md](https://github.com/MotiaDev/motia/blob/main/CONTRIBUTING.md)
- [ ] My code follows the code style of this project
- [ ] I have added tests where applicable
- [ ] I have tested my changes locally
- [ ] I have linked relevant issues
- [ ] I have added screenshots for UI changes (if applicable)

## Screenshots (if applicable)
<!-- Add before/after screenshots or GIFs here -->

## Additional Context
<!-- Add any other context or information about the PR here --> 

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> Adds a Motia configuration guide and updates API/Event/Stream rules to support Zod or JSON Schema, plus stream auth/access control types and examples.
> 
> - **Motia Docs (Cursor Rules)**:
>   - **New**: `motia-config.mdc` with full app config guide (plugins, adapters, stream auth, Express customization) and examples.
>   - **API Steps (`api-steps.mdc`)**:
>     - Add `ZodInput`/`StepSchemaInput`; `bodySchema` and `responseSchema` now accept Zod or JSON Schema.
>     - Define `ApiResponse` and refine `ApiRouteHandler` typing; minor Zod example fix for `z.record`.
>   - **Event Steps (`event-steps.mdc`)**:
>     -

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
