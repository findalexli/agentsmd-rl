# feat(skills): add team-builder skill

Source: [affaan-m/everything-claude-code#501](https://github.com/affaan-m/everything-claude-code/pull/501)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/team-builder/SKILL.md`

## What to add / change

## Summary
Interactive agent picker skill that dynamically discovers agent markdown files organized by domain subdirectories, presents a browsable menu, lets users compose custom teams, and dispatches selected agents in parallel with synthesized results.

Fills a gap in the current skill collection: there's no way to browse and compose agent teams on the fly. Users either need to remember which agents exist or manually invoke them one by one.

## Type
- [x] Skill
- [ ] Agent
- [ ] Hook
- [ ] Command

## Key Features
- **Dynamic discovery** — globs agent directories, no hardcoded lists. Adding a new `.md` file auto-adds it to the menu.
- **Flexible selection** — accepts domain numbers ("1,3"), agent names ("security + seo"), or "all from [domain]"
- **Parallel dispatch** — spawns all selected agents simultaneously via the Agent tool
- **Synthesis** — highlights agreements, tensions, and next steps across agent outputs
- **Generic** — works with any collection of agent markdown files, not tied to a specific agent set

## Testing
- Tested with 12 agent files across 5 domains (engineering, sales, marketing, support, specialized)
- Verified dynamic discovery picks up new files without skill edits
- Tested parallel dispatch with 2-4 agents simultaneously
- Validated fuzzy name matching and domain number selection

## Checklist
- [x] Follows format guidelines
- [x] Tested with Claude Code
- [x] No sensitive info (API keys, paths)
- [x] Clear descriptions
- [x] Focused on one domain


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
