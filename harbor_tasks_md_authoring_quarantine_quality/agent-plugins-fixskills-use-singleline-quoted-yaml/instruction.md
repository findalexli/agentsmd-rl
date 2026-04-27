# fix(skills): use single-line quoted YAML for skill description

Source: [awslabs/agent-plugins#10](https://github.com/awslabs/agent-plugins/pull/10)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/deploy-on-aws/skills/deploy/SKILL.md`

## What to add / change

## Summary
Fix SKILL.md description parsing bug where Claude Code displays the plugin name instead of the actual skill description.

## Problem
Claude Code's skill parser doesn't correctly handle YAML multi-line block scalars (`>`). When the description uses this format, parsing fails silently and Claude falls back to displaying the plugin name.

**Before (broken):**
```yaml
description: >
  Deploy applications to AWS. Triggers on: "deploy to AWS", "host on AWS"...
```
Shows: `Deploy infrastructure to AWS (from plugin:deploy-on-aws@awslabs-agent-plugins).`

**After (fixed):**
```yaml
description: "Deploy applications to AWS. Triggers on: deploy to AWS, host on AWS..."
```
Shows the full description text.

## Why Quotes Are Needed
The description contains colons (e.g., `Triggers on:`). Without quotes, YAML interprets these as key-value separators, causing a parsing error.

## Test Plan
1. Add marketplace: `/plugin marketplace add scoropeza/agent-plugins --ref fix/skill-description-parsing`
2. Install plugin: `/plugin install deploy-on-aws@awslabs-agent-plugins`
3. Ask Claude: "List your skills with their names and descriptions"
4. Verify the deploy skill shows the full description, not just the plugin name

## Screenshots
| Before | After |
|--------|-------|
| Generic plugin name as description | Full description text displayed |

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
