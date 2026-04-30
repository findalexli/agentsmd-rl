# feat: add Android Modern Development Bundle (Compose + Coroutines)

Source: [sickn33/antigravity-awesome-skills#118](https://github.com/sickn33/antigravity-awesome-skills/pull/118)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/android-jetpack-compose-expert/SKILL.md`
- `skills/kotlin-coroutines-expert/SKILL.md`

## What to add / change

This PR introduces a Modern Android Development bundle with two high-quality skills:

1. **android-jetpack-compose-expert**: Comprehensive guide for modern UI development with Jetpack Compose, covering State Management (MVI), Navigation Type Safety, and Performance Optimization.
2. **kotlin-coroutines-expert**: Best practices for structured concurrency, Flow usage, and error handling in Kotlin.

Both skills have been validated locally using `scripts/validate_skills.py` and follow the V4 Quality Standards (When to use, Examples, Best Practices).

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
