# Add coding-mojo skill

Source: [oaustegard/claude-skills#447](https://github.com/oaustegard/claude-skills/pull/447)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `coding-mojo/SKILL.md`

## What to add / change

Wrapper skill for Mojo development in Claude.ai containers.

## What it does
- Installs Mojo (pip install modular) and handles container setup
- Documents v26.2 syntax corrections from hands-on testing
- Routes to Modular's official skills (github.com/modular/skills) for deep language content

## Key design decisions
- **Wrapper, not duplicate**: Modular maintains authoritative syntax correction skills. This skill handles what they don't: container installation, constraints, benchmarking patterns.
- **Correction table**: Captures the most common pretrained errors verified hands-on in 26.2
- **Companion skill fetch**: If Modular skills aren't installed locally, provides curl pattern to fetch them from GitHub

## Tested
- Installation: pip install modular ✓
- Inline execution: mojo -e ✓
- File compilation: mojo build ✓
- Benchmark pattern: fib(90) Python 7µs vs Mojo 34ns (~200x) ✓

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
