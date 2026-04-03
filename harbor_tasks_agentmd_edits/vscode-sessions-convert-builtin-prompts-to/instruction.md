# Consolidate built-in prompts into skills and add UI Integration badges

## Problem

The Sessions app currently has two parallel customization discovery systems: built-in prompts (`.prompt.md` files in `vs/sessions/prompts/`) and built-in skills (`SKILL.md` files in `vs/sessions/skills/`). This is redundant — skills already have richer metadata (name validation, description parsing, `disableModelInvocation`, `userInvocable`) making prompts the weaker abstraction.

Additionally, some built-in skills drive toolbar UI elements (e.g., `act-on-feedback` powers the Submit Feedback button, `generate-run-commands` powers the Run button). Users who override these skills in the AI Customization editor have no way to know they're affecting a UI surface — they discover it by accident.

## Expected Behavior

1. **All 6 built-in prompt files should be converted to skills**: Move each `.prompt.md` from `vs/sessions/prompts/` to `vs/sessions/skills/{name}/SKILL.md` with proper SKILL.md frontmatter (`name`, `description`).

2. **Remove the built-in prompts discovery system** from `AgenticPromptsService` in `promptsService.ts`. The `BUILTIN_PROMPTS_URI`, `_builtinPromptsCache`, `getBuiltinPromptFiles()`, and `discoverBuiltinPrompts()` should all be removed. The `listPromptFiles()` method should early-return for non-skill types instead of branching.

3. **Add a "UI Integration" badge** to the customizations editor for skills that have direct UI integrations (toolbar buttons, menu items). This requires:
   - Adding a `getSkillUIIntegrations(): ReadonlyMap<string, string>` method to the `IAICustomizationWorkspaceService` interface
   - Implementing it in the Sessions workspace service with mappings for the relevant skill names and their tooltip descriptions
   - Implementing it as an empty map in the core VS Code workspace service (no-op)
   - Having the list widget look up skill names and display a "UI Integration" badge with tooltip

4. **Update the architecture documentation** (`src/vs/sessions/AI_CUSTOMIZATIONS.md`) to reflect the prompts-to-skills consolidation and document the new UI Integration badge feature.

## Files to Look At

- `src/vs/sessions/contrib/chat/browser/promptsService.ts` — the `AgenticPromptsService` with built-in prompts discovery to remove
- `src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts` — Sessions workspace service, needs `getSkillUIIntegrations` implementation
- `src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts` — interface definition
- `src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts` — core implementation (empty map)
- `src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts` — list widget, needs badge rendering
- `src/vs/sessions/prompts/` — existing prompt files to convert
- `src/vs/sessions/skills/` — target directory for converted SKILL.md files
- `src/vs/sessions/AI_CUSTOMIZATIONS.md` — architecture documentation to update
