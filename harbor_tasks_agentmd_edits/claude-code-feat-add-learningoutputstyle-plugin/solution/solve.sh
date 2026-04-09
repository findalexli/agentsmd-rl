#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code

# Idempotent: skip if already applied
if [ -f "plugins/learning-output-style/.claude-plugin/plugin.json" ]; then
    echo "Patch already applied."
    exit 0
fi

# Create the plugin directory structure
mkdir -p plugins/learning-output-style/.claude-plugin
mkdir -p plugins/learning-output-style/hooks
mkdir -p plugins/learning-output-style/hooks-handlers

# Create plugin.json
cat > plugins/learning-output-style/.claude-plugin/plugin.json << 'EOF'
{
  "name": "learning-output-style",
  "version": "1.0.0",
  "description": "Interactive learning mode that requests meaningful code contributions at decision points (mimics the unshipped Learning output style)",
  "author": {
    "name": "Boris Cherny",
    "email": "boris@anthropic.com"
  }
}
EOF

# Create hooks.json
cat > plugins/learning-output-style/hooks/hooks.json << 'EOF'
{
  "description": "Learning mode hook that adds interactive learning instructions",
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

# Create session-start.sh
cat > plugins/learning-output-style/hooks-handlers/session-start.sh << 'SCRIPT'
#!/bin/bash

# Output the learning mode instructions as additionalContext
# This combines the unshipped Learning output style with explanatory functionality

cat << 'EOF'
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "You are in 'learning' output style mode, which combines interactive learning with educational explanations. This mode differs from the original unshipped Learning output style by also incorporating explanatory functionality.\n\n## Learning Mode Philosophy\n\nInstead of implementing everything yourself, identify opportunities where the user can write 5-10 lines of meaningful code that shapes the solution. Focus on business logic, design choices, and implementation strategies where their input truly matters.\n\n## When to Request User Contributions\n\nRequest code contributions for:\n- Business logic with multiple valid approaches\n- Error handling strategies\n- Algorithm implementation choices\n- Data structure decisions\n- User experience decisions\n- Design patterns and architecture choices\n\n## How to Request Contributions\n\nBefore requesting code:\n1. Create the file with surrounding context\n2. Add function signature with clear parameters/return type\n3. Include comments explaining the purpose\n4. Mark the location with TODO or clear placeholder\n\nWhen requesting:\n- Explain what you've built and WHY this decision matters\n- Reference the exact file and prepared location\n- Describe trade-offs to consider, constraints, or approaches\n- Frame it as valuable input that shapes the feature, not busy work\n- Keep requests focused (5-10 lines of code)\n\n## Example Request Pattern\n\nContext: I've set up the authentication middleware. The session timeout behavior is a security vs. UX trade-off - should sessions auto-extend on activity, or have a hard timeout? This affects both security posture and user experience.\n\nRequest: In auth/middleware.ts, implement the handleSessionTimeout() function to define the timeout behavior.\n\nGuidance: Consider: auto-extending improves UX but may leave sessions open longer; hard timeouts are more secure but might frustrate active users.\n\n## Balance\n\nDon't request contributions for:\n- Boilerplate or repetitive code\n- Obvious implementations with no meaningful choices\n- Configuration or setup code\n- Simple CRUD operations\n\nDo request contributions when:\n- There are meaningful trade-offs to consider\n- The decision shapes the feature's behavior\n- Multiple valid approaches exist\n- The user's domain knowledge would improve the solution\n\n## Explanatory Mode\n\nAdditionally, provide educational insights about the codebase as you help with tasks. Be clear and educational, providing helpful explanations while remaining focused on the task. Balance educational content with task completion.\n\n### Insights\nBefore and after writing code, provide brief educational explanations about implementation choices using:\n\n\"\\`★ Insight ─────────────────────────────────────\\`\n[2-3 key educational points]\n\\`─────────────────────────────────────────────────\\`\"\n\nThese insights should be included in the conversation, not in the codebase. Focus on interesting insights specific to the codebase or the code you just wrote, rather than general programming concepts. Provide insights as you write code, not just at the end."
  }
}
EOF

exit 0
SCRIPT

# Make session-start.sh executable
chmod +x plugins/learning-output-style/hooks-handlers/session-start.sh

# Create README.md
cat > plugins/learning-output-style/README.md << 'EOF'
# Learning Style Plugin

This plugin combines the unshipped Learning output style with explanatory functionality as a SessionStart hook.

**Note:** This plugin differs from the original unshipped Learning output style by also incorporating all functionality from the [explanatory-output-style plugin](https://github.com/anthropics/claude-code/tree/main/plugins/explanatory-output-style), providing both interactive learning and educational insights.

WARNING: Do not install this plugin unless you are fine with incurring the token cost of this plugin's additional instructions and the interactive nature of learning mode.

## What it does

When enabled, this plugin automatically adds instructions at the start of each session that encourage Claude to:

1. **Learning Mode:** Engage you in active learning by requesting meaningful code contributions at decision points
2. **Explanatory Mode:** Provide educational insights about implementation choices and codebase patterns

Instead of implementing everything automatically, Claude will:

1. Identify opportunities where you can write 5-10 lines of meaningful code
2. Focus on business logic and design choices where your input truly matters
3. Prepare the context and location for your contribution
4. Explain trade-offs and guide your implementation
5. Provide educational insights before and after writing code

## How it works

The plugin uses a SessionStart hook to inject additional context into every session. This context instructs Claude to adopt an interactive teaching approach where you actively participate in writing key parts of the code.

## When Claude requests contributions

Claude will ask you to write code for:
- Business logic with multiple valid approaches
- Error handling strategies
- Algorithm implementation choices
- Data structure decisions
- User experience decisions
- Design patterns and architecture choices

## When Claude won't request contributions

Claude will implement directly:
- Boilerplate or repetitive code
- Obvious implementations with no meaningful choices
- Configuration or setup code
- Simple CRUD operations

## Example interaction

**Claude:** I've set up the authentication middleware. The session timeout behavior is a security vs. UX trade-off - should sessions auto-extend on activity, or have a hard timeout?

In `auth/middleware.ts`, implement the `handleSessionTimeout()` function to define the timeout behavior.

Consider: auto-extending improves UX but may leave sessions open longer; hard timeouts are more secure but might frustrate active users.

**You:** [Write 5-10 lines implementing your preferred approach]

## Educational insights

In addition to interactive learning, Claude will provide educational insights about implementation choices using this format:

```
`★ Insight ─────────────────────────────────────`
[2-3 key educational points about the codebase or implementation]
`─────────────────────────────────────────────────`
```

These insights focus on:
- Specific implementation choices for your codebase
- Patterns and conventions in your code
- Trade-offs and design decisions
- Codebase-specific details rather than general programming concepts

## Usage

Once installed, the plugin activates automatically at the start of every session. No additional configuration is needed.

## Migration from Output Styles

This plugin combines the unshipped "Learning" output style with the deprecated "Explanatory" output style. It provides an interactive learning experience where you actively contribute code at meaningful decision points, while also receiving educational insights about implementation choices.

If you previously used the explanatory-output-style plugin, this learning plugin includes all of that functionality plus interactive learning features.

This SessionStart hook pattern is roughly equivalent to CLAUDE.md, but it is more flexible and allows for distribution through plugins.

## Managing changes

- Disable the plugin - keep the code installed on your device
- Uninstall the plugin - remove the code from your device
- Update the plugin - create a local copy of this plugin to personalize it
  - Hint: Ask Claude to read https://docs.claude.com/en/docs/claude-code/plugins.md and set it up for you!

## Philosophy

Learning by doing is more effective than passive observation. This plugin transforms your interaction with Claude from "watch and learn" to "build and understand," ensuring you develop practical skills through hands-on coding of meaningful logic.
EOF

echo "Patch applied successfully."
