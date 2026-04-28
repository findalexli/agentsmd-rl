# Add SKILL.md for AI agent customization

Source: [vitorpamplona/amethyst#1699](https://github.com/vitorpamplona/amethyst/pull/1699)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## Summary

This PR adds a `SKILL.md` file to help AI agents (like Claude, GPT, etc.) fork, customize, and build branded versions of Amethyst.

## Why?

With AI coding assistants becoming common, having a structured guide in the repo allows:
- Users to ask their AI agent: "Build me a custom Nostr client based on Amethyst"
- Agents to follow clear, tested instructions
- Lower barrier to entry for customization

## What's Included

The SKILL.md covers:
- **Prerequisites**: Java 21, Android SDK setup
- **Build Workflow**: Clone → Sign → Configure → Build
- **Customizations**: App name, package ID, icons, client tags, relays
- **Troubleshooting**: Common errors and solutions
- **Distribution**: Surge.sh, Zapstore, direct hosting

## Testing

This guide was tested by building a customized Amethyst fork entirely through AI agent instructions.

## Notes

- Focuses on F-Droid builds (no Google Play dependencies)
- All instructions use generic placeholders ("YourAppName", etc.)
- Designed to be agent-readable while still human-friendly

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
