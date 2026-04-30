# chore: add Cursor rules for speculative execution

Source: [tetsuo-ai/AgenC#316](https://github.com/tetsuo-ai/AgenC/pull/316)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/anchor.mdc`
- `.cursor/rules/runtime.mdc`
- `.cursor/rules/speculation.mdc`
- `.cursorrules`

## What to add / change

## Summary

Adds Cursor IDE rules for the speculative execution system.

## Files Added

- `.cursorrules` - Main rules file with project overview, architecture, and speculation components
- `.cursor/rules/speculation.mdc` - Rules specific to speculation development
- `.cursor/rules/anchor.mdc` - Rules for Anchor/Solana program development  
- `.cursor/rules/runtime.mdc` - Rules for TypeScript runtime development

## Key Content

- Critical invariant documentation (proof ordering)
- Component hierarchy for speculation system
- Build commands
- Testing patterns
- Common development patterns

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
