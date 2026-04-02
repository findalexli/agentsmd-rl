# Plugin skills missing plugin name prefix in slash commands

## Problem

Plugin skills registered through the agent plugin system appear in the chat slash command list without their plugin name prefix. For example, a skill `deploy` from a plugin `my-plugin` shows up as `/deploy` instead of `/my-plugin:deploy`. This is inconsistent with how plugin *commands* behave — commands correctly appear as `/<plugin-name>:<command>`.

The issue is especially problematic when a skill's SKILL.md file includes a `name:` field in its frontmatter. The frontmatter name completely overrides the plugin-prefixed name, so a skill with `name: "run-ci"` in a plugin called `devtools` appears as `/run-ci` rather than `/devtools:run-ci`.

## Expected Behavior

Plugin skills should always include the plugin name prefix in their slash command name, consistent with how plugin commands are named. The canonical form is `<plugin-name>:<skill-name>`, regardless of whether the name comes from the SKILL.md frontmatter or from the skill directory name.

## Files to Look At

- `src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts` — contains the `computeSlashCommandDiscoveryInfo` method that resolves slash command names from prompt/skill files
- `src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts` — contains `getCanonicalPluginCommandId`, the utility that constructs the canonical `<plugin>:<command>` form (already used for plugin commands and hooks)
