# Add daggr agent Skill

Source: [gradio-app/daggr#16](https://github.com/gradio-app/daggr/pull/16)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/daggr/SKILL.md`

## What to add / change

Seems to work quite well in a new dir that doesn't know anything about Daggr @abidlabs 

<img width="1144" height="1169" alt="image" src="https://github.com/user-attachments/assets/40d5e7d6-6b89-48f1-9f45-cdaeea71f860" />


## Summary
- Adds a project-level agent skill following the [agentskills spec](https://github.com/agentskills/agentskills)
- Teaches AI agents how to build daggr workflows

## What the skill covers
- Node types: `GradioNode`, `FnNode`, `InferenceNode`
- Port connections and data flow patterns
- `ItemList` for parallel/scattered execution
- Common patterns (image generation, TTS, image-to-video, ffmpeg composition)
- Workflow checklist: finding Spaces, checking APIs, handling file outputs
- Debugging tips

## Test plan
- [ ] Verify skill is discovered by agents working in the repo
- [ ] Test that an agent can build a simple workflow using the skill

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
