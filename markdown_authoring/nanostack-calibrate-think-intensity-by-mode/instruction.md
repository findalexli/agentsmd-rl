# Calibrate /think intensity by mode

Source: [garagon/nanostack#8](https://github.com/garagon/nanostack/pull/8)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `think/SKILL.md`

## What to add / change

## Summary

- Added Founder mode (full pushback, opt-in only) for experienced entrepreneurs
- Recalibrated Startup mode to respect stated pain points, challenge scope not experience
- Reinforced Builder mode as minimal interrogation, focus on simplest solution
- Auto-detects mode from how the user frames the problem
- New rule: "Direct and respectful is the target"

## Context

Ran a real case (Twitter bookmark search) and the original intensity felt like an interrogation for a clear personal pain point. The anti-sycophancy rules were calibrated for YC-style founder pushback but alienate users who know their problem and want help scoping the solution.

## Test plan

- [ ] User says "I have this problem" -> defaults to Startup mode (no pain questioning)
- [ ] User says "tear this apart" -> activates Founder mode (full pushback)
- [ ] User says "I need to build a tool for X" -> defaults to Builder mode

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
