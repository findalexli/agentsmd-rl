#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code

# Idempotent: skip if plugin already exists
if [ -d "plugins/explanatory-output-style" ]; then
    echo "Plugin already exists."
    exit 0
fi

# Create plugin directory structure
mkdir -p plugins/explanatory-output-style/.claude-plugin
mkdir -p plugins/explanatory-output-style/hooks-handlers
mkdir -p plugins/explanatory-output-style/hooks

# Create plugin.json
cat > plugins/explanatory-output-style/.claude-plugin/plugin.json << 'EOF'
{
  "name": "explanatory-output-style",
  "version": "1.0.0",
  "description": "Adds educational insights about implementation choices and codebase patterns (mimics the deprecated Explanatory output style)",
  "author": {
    "name": "Dickson Tsai",
    "email": "dickson@anthropic.com"
  }
}
EOF

# Create session-start.sh
cat > plugins/explanatory-output-style/hooks-handlers/session-start.sh << 'EOF'
#!/bin/bash

# Output the explanatory mode instructions as additionalContext
# This mimics the deprecated Explanatory output style

cat << 'INNEREOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "You are in 'explanatory' output style mode, where you should provide educational insights about the codebase as you help with the user's task.\n\nYou should be clear and educational, providing helpful explanations while remaining focused on the task. Balance educational content with task completion. When providing insights, you may exceed typical length constraints, but remain focused and relevant.\n\n## Insights\nIn order to encourage learning, before and after writing code, always provide brief educational explanations about implementation choices using (with backticks):\n\"`★ Insight ─────────────────────────────────────`\n[2-3 key educational points]\n`─────────────────────────────────────────────────`\"\n\nThese insights should be included in the conversation, not in the codebase. You should generally focus on interesting insights that are specific to the codebase or the code you just wrote, rather than general programming concepts. Do not wait until the end to provide insights. Provide them as you write code."
  }
}
INNEREOF

exit 0
EOF

# Make script executable
chmod +x plugins/explanatory-output-style/hooks-handlers/session-start.sh

# Create hooks.json
cat > plugins/explanatory-output-style/hooks/hooks.json << 'EOF'
{
  "description": "Explanatory mode hook that adds educational insights instructions",
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "${CLAUDE_PLUGIN_ROOT}/hooks-handlers/session-start.sh"
          }
        ]
      }
    ]
  }
}
EOF

# Create README.md
cat > plugins/explanatory-output-style/README.md << 'EOF'
# Explanatory Output Style Plugin

This plugin recreates the deprecated Explanatory output style as a SessionStart
hook.

WARNING: Do not install this plugin unless you are fine with incurring the token
cost of this plugin's additional instructions and output.

## What it does

When enabled, this plugin automatically adds instructions at the start of each
session that encourage Claude to:

1. Provide educational insights about implementation choices
2. Explain codebase patterns and decisions
3. Balance task completion with learning opportunities

## How it works

The plugin uses a SessionStart hook to inject additional context into every
session. This context instructs Claude to provide brief educational explanations
before and after writing code, formatted as:

```
`★ Insight ─────────────────────────────────────`
[2-3 key educational points]
`─────────────────────────────────────────────────`
```

## Usage

Once installed, the plugin activates automatically at the start of every
session. No additional configuration is needed.

The insights focus on:

- Specific implementation choices for your codebase
- Patterns and conventions in your code
- Trade-offs and design decisions
- Codebase-specific details rather than general programming concepts

## Migration from Output Styles

This plugin replaces the deprecated "Explanatory" output style setting. If you
previously used:

```json
{
  "outputStyle": "Explanatory"
}
```

You can now achieve the same behavior by installing this plugin instead.

More generally, this SessionStart hook pattern is roughly equivalent to
CLAUDE.md, but it is more flexible and allows for distribution through plugins.

Note: Output styles that involve tasks besides software development, are better
expressed as
[subagents](https://docs.claude.com/en/docs/claude-code/sub-agents), not as
SessionStart hooks. Subagents change the system prompt while SessionStart hooks
add to the default system prompt.

## Managing changes

- Disable the plugin - keep the code installed on your device
- Uninstall the plugin - remove the code from your device
- Update the plugin - create a local copy of this plugin to personalize this
  plugin
  - Hint: Ask Claude to read
    https://docs.claude.com/en/docs/claude-code/plugins.md and set it up for
    you!
EOF

echo "Plugin created successfully."

# Git add and commit so judge can detect the changes
git add plugins/explanatory-output-style/
git commit -m "Add explanatory-output-style plugin" --quiet
