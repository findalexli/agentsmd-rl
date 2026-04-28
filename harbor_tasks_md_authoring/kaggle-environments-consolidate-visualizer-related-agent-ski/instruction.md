# Consolidate visualizer related agent skills

Source: [Kaggle/kaggle-environments#861](https://github.com/Kaggle/kaggle-environments/pull/861)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-environment/SKILL.md`
- `.agents/skills/create-open-spiel-visualizer/SKILL.md`
- `.agents/skills/create-visualizer/SKILL.md`
- `.agents/skills/create-visualizer/visualizer-style-guide.md`
- `.agents/skills/onboard-open-spiel-game/SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

There was a bunch of overlap between the skills I had been experimenting with for visualizers and what we already had. This consolidates that information into a single skill and adds a general visualizer style guide. 

The style guide is really basic right now and I expect it to evolve as the Go v2 visualizer comes off its own branch and becomes the sole option (this will let us borrow more assets). I think it doesn't really need adjustments for mobile breakpoints but we can keep iterating on that if needed.

I anticipate there will be a follow up PR to this that focuses on really making that onboard OpenSpiel skill work e2e, but I need to learn a little more about proxies to confirm I'm doing it right (@c-h-i-a-m-a-k-a if ye have time today that would be great)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
