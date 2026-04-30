# chore(all): Add a SKILL.md file for working with insta snapshots.

Source: [oxc-project/oxc#18957](https://github.com/oxc-project/oxc/pull/18957)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/insta-snapshots/SKILL.md`

## What to add / change

I find that AI Agent tools really like using insta incorrectly (e.g. https://github.com/oxc-project/oxc/pull/18953#discussion_r2766636555), so this will hopefully give them some direction. See https://agentskills.io for more info.

This was generated with Claude Code, but then reviewed and revised a good amount by me.

I used `.agents/skills/` as the directory, as it's supported by VS Code (soon), Codex, Cursor (soon), and a bunch of other tools (not Claude Code yet, I assume it'll be supported soon). The skill is only loaded into the context when the LLM thinks it's relevant, etc. etc. blah blah AI stuff.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
