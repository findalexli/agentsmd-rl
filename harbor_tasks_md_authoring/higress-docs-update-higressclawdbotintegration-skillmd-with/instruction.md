# docs: update higress-clawdbot-integration SKILL.md with config subcommand hot-reload

Source: [higress-group/higress#3431](https://github.com/higress-group/higress/pull/3431)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/higress-clawdbot-integration/SKILL.md`

## What to add / change

## Description

This PR updates `higress-clawdbot-integration/SKILL.md` to document the new `config` subcommand with hot-reload support.

## Changes

### New Documentation Sections

1. **Managing API Keys** - New section showing how to use `config` subcommand:
   - `config list` - View all configured API keys (with masking)
   - `config add` - Add or update an API key (hot-reload)
   - `config remove` - Remove an API key (hot-reload)

2. **Step 6 in Workflow** - Added optional step for managing API keys after deployment

3. **Example 4** - New example showing API key management workflow with hot-reload emphasis

4. **Provider List** - Documented all supported provider names and aliases

### Key Updates

- **Hot-reload emphasis**: All sections highlight that changes take effect immediately
- **No restart needed**: Clear documentation that config changes don't require container restart
- **Provider aliases**: Show both primary and alias names (e.g., `dashscope`/`qwen`)
- **Updated numbering**: Renumbered Example 4 → Example 5 (Clawdbot integration)

## Related PR
This documentation update corresponds to the implementation PR with hot-reload:
- higress-standalone: https://github.com/higress-group/higress-standalone/pull/233

## Benefits
- Clear guidance on managing API keys with hot-reload
- Better user experience for `get-ai-gateway.sh` script
- Complete documentation of new config subcommand
- Emphasizes zero-downtime configuration updates

## Testing
- [x] Markdown syntax is 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
