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

## Plugin Manifest Requirements

The plugin manifest at `plugins/explanatory-output-style/.claude-plugin/plugin.json` must be valid JSON with these fields:
- `name`: must be `"explanatory-output-style"`
- `version`: version string (e.g. `"1.0.0"`)
- `description`: human-readable description of the plugin's purpose
- `author`: either a string or an object with author information

## Hooks Configuration Schema

The hooks configuration at `plugins/explanatory-output-style/hooks/hooks.json` must be valid JSON with this structure:
- Top-level key `hooks` containing an object
- Under `hooks`, a key `SessionStart` containing an array of hook group objects
- Each hook group object has a `hooks` array
- Each hook in that array is an object with `type: "command"` and a `command` string containing `"session-start.sh"`

Example structure:
```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          { "type": "command", "command": "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/session-start.sh" }
        ]
      }
    ]
  }
}
```

## SessionStart Hook Script

The script at `plugins/explanatory-output-style/hooks-handlers/session-start.sh` must:
- Be executable (have a shebang like `#!/bin/bash` or `#!/usr/bin/env bash`)
- Output valid JSON to stdout when executed
- The JSON must contain a `hookSpecificOutput` object with:
  - `hookSpecificOutput.hookEventName`: must be the string `"SessionStart"`
  - `hookSpecificOutput.additionalContext`: educational instructions for explanatory mode
- The additionalContext text must mention: "explanatory", "insight", "educational", and include backtick formatting
