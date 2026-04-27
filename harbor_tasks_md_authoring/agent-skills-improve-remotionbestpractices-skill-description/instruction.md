# improve remotion-best-practices skill description and quick start

Source: [jdrhyne/agent-skills#8](https://github.com/jdrhyne/agent-skills/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/remotion/SKILL.md`

## What to add / change

hey @jdrhyne, thanks for putting this collection and sharing it publicly. I resonate a lot with the AI native approach your team is taking to build the product. Kudos!

was running your skills through some evals and noticed a few things on remotion-best-practices that were pretty quick to improve (moving from `~59%` to `~100%` agent performance):

- expanded capabilities description + trigger terms like _Remotion, programmatic video, React video, MP4 export_ so agents can match user requests to this skill

- replaced "when to use" section with specific use cases like _creating compositions, animating scenes, embedding audio/video, adding captions_

- added a quick start section with composition example + `2` critical rules (always useCurrentFrame, never CSS transitions). this makes the skill actionable without needing to read the rule files first

these were easy changes to bring the skill in line with what performs well against **Anthropic's best practices**. honest disclosure, I work at a company where we build tooling around this. not a pitch, just fixes that were straightforward to make.

you've got `19` skills here, if you want to do it yourself, evals are free and open to run: [link](https://tessl.io/registry/skills/github/jdrhyne/agent-skills) otherwise happy to make the improvements for you.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
