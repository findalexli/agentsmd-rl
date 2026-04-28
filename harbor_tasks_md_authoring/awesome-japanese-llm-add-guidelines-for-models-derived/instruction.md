# Add guidelines for models derived from Japanese continual pre-training models

Source: [llm-jp/awesome-japanese-llm#588](https://github.com/llm-jp/awesome-japanese-llm/pull/588)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

- Add clarification to CLAUDE.md for handling models derived from Japanese continual pre-training models (Swallow, ELYZA, Nekomata, youko, etc.)
- Key rules added:
  1. Such models should be placed in the **継続事前学習** section, even if they only perform instruction tuning
  2. The base model column should record the **original architecture** (e.g., "Llama 3.1"), NOT the intermediate Japanese model name (e.g., "Llama 3.1 Swallow")

This addresses the classification confusion encountered when adding MedExamDoc-Llama-3.1-Swallow-8B-Instruct-v0.5.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
