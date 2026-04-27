# docs: Strengthen guidance to use skill scripts over raw tools

Source: [conorluddy/ios-simulator-skill#3](https://github.com/conorluddy/ios-simulator-skill/pull/3)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skill/SKILL.md`

## What to add / change

## Summary

Add prominent warnings to SKILL.md directing users to prefer the 12 skill scripts instead of running raw `xcrun simctl`, `idb`, or `xcodebuild` commands.

## Changes

- New section after Prerequisites: "⚠️ Important: Use Skill Scripts, Not Raw Tools"
  - Explains the benefits of using skill scripts
  - Lists what you lose by using raw tools
  - Provides a clear example (find & tap button)

- Updated "Integration with Raw Tools" → "When to Use Raw Tools (Advanced)"
  - Changes permissive language ("you can always use them directly")
  - To prescriptive language ("only use for edge cases")
  - Explains the tradeoffs clearly

## Why This Matters

- Prevents AI agents from bypassing skill optimizations
- Helps users understand the value proposition
- Encourages semantic navigation over fragile coordinates
- Promotes token-efficient workflows

## Testing

Updated SKILL.md documentation only, no functional changes.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
