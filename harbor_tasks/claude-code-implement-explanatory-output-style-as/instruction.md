# Implement Explanatory Output Style as a Plugin

## Problem

Claude Code previously had an "Explanatory" output style setting that was deprecated. Users who relied on this feature for educational insights about implementation choices need an alternative way to enable this behavior.

## Expected Behavior

Create a plugin that recreates the deprecated Explanatory output style as a SessionStart hook. The plugin should:

1. Add a new plugin directory at `plugins/explanatory-output-style/`
2. Create a plugin manifest at `.claude-plugin/plugin.json` with name "explanatory-output-style"
3. Create a hook handler at `hooks-handlers/session-start.sh` that outputs valid JSON with educational instructions
4. Create a hooks configuration at `hooks/hooks.json` that registers the SessionStart hook
5. Include a README.md documenting the plugin's purpose and usage

The session-start.sh script must output a JSON object containing:
- `hookSpecificOutput.hookEventName`: "SessionStart"
- `hookSpecificOutput.additionalContext`: Instructions for explanatory mode with educational insights, including formatting with backticks for insight sections

## Files to Look At

- No existing files need modification (this is a new plugin creation)
- Reference existing plugins in the `plugins/` directory for structure patterns
