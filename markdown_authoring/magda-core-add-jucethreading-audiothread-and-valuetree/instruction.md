# Add juce-threading, audio-thread, and valuetree Claude skills

Source: [Conceptual-Machines/magda-core#668](https://github.com/Conceptual-Machines/magda-core/pull/668)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/audio-thread/SKILL.md`
- `.claude/skills/juce-threading/SKILL.md`
- `.claude/skills/valuetree/SKILL.md`

## What to add / change

Three new skills covering JUCE/C++ patterns used in the codebase:
- juce-threading: threading model, component lifecycle, RAII patterns
- audio-thread: real-time safety, lock-free communication, metering
- valuetree: ValueTree basics, CachedValue, serialization in TE plugins

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
