# feat: improve skill description specificity and content conciseness

Source: [AvdLee/Swift-Concurrency-Agent-Skill#31](https://github.com/AvdLee/Swift-Concurrency-Agent-Skill/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `swift-concurrency/SKILL.md`

## What to add / change

Hullo @AvdLee 👋

I ran `swift-concurrency` through `tessl skill review` at work and found some targeted improvements to push the scores up. Here's the before/after:

![score_card](https://github.com/popey/Swift-Concurrency-Agent-Skill/blob/improve/skill-review-optimization/score_card.png?raw=true)

| Skill | Before | After | Change |
|-------|--------|-------|--------|
| swift-concurrency | 81% | 100% | +19% |

<details><summary>Summary of changes</summary>

- **Description**: Replaced vague "Expert guidance on" opener with concrete action verbs (diagnose data races, convert callback-based code, implement actor isolation, resolve Sendable issues, guide Swift 6 migration) — improved specificity from 2/3 to 3/3
- **Project settings**: Consolidated duplicate "Recommended Tools for Analysis" and "Project Settings Intake" sections into a single reference table (SwiftPM vs Xcode side-by-side) — saves ~20 lines of redundancy
- **Concurrency tool selection**: Replaced 6 individual code blocks (each with redundant "Use for:" comments) with a concise selection table covering async/await, async let, TaskGroup, Task, Actor, @MainActor
- **Migration workflow**: Added explicit Migration Validation Loop (Build → Fix → Rebuild → Test → Proceed) for safer incremental migration — this addressed the reviewer's feedback on missing validation feedback loops
- **Best Practices**: Merged into the Verification Checklist to eliminate the overlap between the two sections and added acti

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
