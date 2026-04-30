# docs: mark OpenClaw commands as interactive in SKILL.md

Source: [higress-group/higress#3478](https://github.com/higress-group/higress/pull/3478)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/higress-openclaw-integration/SKILL.md`

## What to add / change

## Problem

The `openclaw models auth login --provider higress` command is interactive and cannot be executed by AI agents directly.

## Changes

### Step 3 Updated

Added warning and separated commands for user to run manually:

```markdown
**⚠️ Tell user to run the following commands manually in their terminal (interactive commands, cannot be executed by AI agent):**

\`\`\`bash
# Step 1: Enable the plugin
openclaw plugins enable higress

# Step 2: Configure provider (interactive)
openclaw models auth login --provider higress --set-default

# Step 3: Restart OpenClaw gateway to apply changes
openclaw gateway restart
\`\`\`
```

### Important Notes Updated

Changed note #3 to clarify that these commands are interactive and must be run by the user manually.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
