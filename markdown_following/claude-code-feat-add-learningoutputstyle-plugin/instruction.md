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

## Plugin Manifest Schema

The `.claude-plugin/plugin.json` file must be valid JSON with these fields:
- `name`: exactly `"learning-output-style"`
- `version`: exactly `"1.0.0"`
- `description`: must contain the word `"Learning"`
- `author`: must be an object with a `name` subfield (e.g., `"author": { "name": "..." }`)

## Hook Configuration Schema

The `hooks/hooks.json` file must be valid JSON with this structure:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "<path-to-script>"
          }
        ]
      }
    ]
  }
}
```

The `command` value must reference `session-start.sh`.

## Session-Start Hook Output

The `hooks-handlers/session-start.sh` script must:
1. Be executable (have execute permission)
2. Output valid JSON to stdout
3. Output JSON must contain a `hookSpecificOutput` object with:
   - `hookEventName`: must be `"SessionStart"`
   - `additionalContext`: must contain the word `"learning"` (case-insensitive) and the word `"Insight"` (with capital I)

## README Requirements

The `README.md` file must contain:
- A level-1 heading: `# Learning Style Plugin`
- A section titled: `What it does`
- A section titled: `How it works`
- Mention of the `SessionStart` hook

## Repository Configuration

The repository root (`.gitignore`) must contain an entry for `.DS_Store` (macOS system file).

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
