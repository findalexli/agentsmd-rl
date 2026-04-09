# Add learning-output-style Plugin

## Problem

The Claude Code repository does not have a plugin that recreates the unshipped "Learning" output style. Users who want interactive learning mode (where Claude requests meaningful code contributions at decision points) cannot access this functionality through the plugin system.

## Expected Behavior

Create a new `plugins/learning-output-style/` directory with a complete plugin structure that:
1. Provides a `SessionStart` hook that injects learning mode instructions
2. Includes proper plugin manifest (`plugin.json`)
3. Includes hook configuration (`hooks/hooks.json`)
4. Includes an executable hook handler (`hooks-handlers/session-start.sh`)
5. Includes comprehensive README documentation

The plugin should combine both interactive learning (requesting user code contributions) and explanatory functionality (educational insights about implementation choices).

## Files to Create

1. `plugins/learning-output-style/.claude-plugin/plugin.json` — Plugin manifest with metadata
2. `plugins/learning-output-style/hooks/hooks.json` — Hook configuration for SessionStart
3. `plugins/learning-output-style/hooks-handlers/session-start.sh` — Executable script that outputs learning mode instructions as JSON
4. `plugins/learning-output-style/README.md` — Documentation explaining the plugin's purpose and behavior

## Plugin Structure Reference

Look at the existing `plugins/explanatory-output-style/` directory for a reference implementation. Your plugin should follow the same structure.

## Key Requirements

- The `session-start.sh` script must output valid JSON with a specific structure containing `hookSpecificOutput.hookEventName` and `hookSpecificOutput.additionalContext`
- The script must be executable (chmod +x)
- The `hooks.json` must register the SessionStart hook with type "command"
- The `plugin.json` must include name, version, description, and author fields
