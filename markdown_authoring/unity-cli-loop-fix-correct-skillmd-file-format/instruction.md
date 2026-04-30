# fix: correct SKILL.md file format

Source: [hatayama/unity-cli-loop#535](https://github.com/hatayama/unity-cli-loop/pull/535)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-project-info/SKILL.md`
- `Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-version/SKILL.md`
- `Packages/src/Editor/Api/McpTools/CaptureWindow/SKILL.md`
- `Packages/src/Editor/Api/McpTools/ClearConsole/SKILL.md`
- `Packages/src/Editor/Api/McpTools/Compile/SKILL.md`
- `Packages/src/Editor/Api/McpTools/ControlPlayMode/SKILL.md`
- `Packages/src/Editor/Api/McpTools/ExecuteDynamicCode/SKILL.md`
- `Packages/src/Editor/Api/McpTools/ExecuteMenuItem/SKILL.md`
- `Packages/src/Editor/Api/McpTools/FindGameObjects/SKILL.md`
- `Packages/src/Editor/Api/McpTools/FocusUnityWindow/SKILL.md`
- `Packages/src/Editor/Api/McpTools/GetHierarchy/SKILL.md`
- `Packages/src/Editor/Api/McpTools/GetLogs/SKILL.md`
- `Packages/src/Editor/Api/McpTools/GetMenuItems/SKILL.md`
- `Packages/src/Editor/Api/McpTools/RunTests/SKILL.md`
- `Packages/src/Editor/Api/McpTools/UnitySearch/SKILL.md`
- `Packages/src/Editor/Api/McpTools/UnitySearchProviderDetails/SKILL.md`

## What to add / change

## Summary
- Fix formatting issues in SKILL.md files across 16 skill definitions
- Ensures consistent format for skill discoverability

## Changes
- CLI-only skills: uloop-get-project-info, uloop-get-version
- MCP tools: CaptureWindow, ClearConsole, Compile, ControlPlayMode, ExecuteDynamicCode, ExecuteMenuItem, FindGameObjects, FocusUnityWindow, GetHierarchy, GetLogs, GetMenuItems, RunTests, UnitySearch, UnitySearchProviderDetails

## Test Plan
- [x] Verify SKILL.md files are properly formatted
- [ ] Confirm skills are correctly discovered by Claude Code

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Quoted the description field in SKILL.md front matter across 16 skills to fix parsing issues. This makes skill discovery consistent and reliable.

- **Bug Fixes**
  - Updated 16 SKILL.md files (2 CLI-only, 14 MCP tools) to quote description values.
  - Prevents YAML parse errors from colons/parentheses and restores skill discoverability.

<sup>Written for commit 4bccdb959630d260f34df4531799f4a8fee8444a. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->



<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary

This PR corrects formatting inconsistencies in SKILL.md files across 16 skill definitions to ensure consistent format for skill discoverability by Claude Code.

## Changes

All changes involve converting the `description` field in YAML front matter from unquoted 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
