# feat(skills): add pytorch-patterns skill

Source: [affaan-m/everything-claude-code#550](https://github.com/affaan-m/everything-claude-code/pull/550)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/pytorch-patterns/SKILL.md`

## What to add / change

## Summary
Adds a comprehensive `pytorch-patterns` skill covering best practices for PyTorch development.
Includes device-agnostic code, reproducibility, model patterns, training loop setups (with AMP constraints), DataLoader best practices, caching gradients, and common anti-patterns.
This serves as the knowledge foundation complementary to the `pytorch-build-resolver` agent.

## Type
- [x] Skill

## Testing
Tested formatting and structure against existing skills (python-patterns, golang-patterns). Code examples verified for syntax and logic.

## Checklist
- [x] Follows format guidelines
- [x] Tested with Claude Code
- [x] No sensitive info (API keys, paths)
- [x] Clear descriptions

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds the `pytorch-patterns` skill with clear, practical PyTorch best practices for models, training, data, performance, and checkpointing. This complements the `pytorch-build-resolver` by providing a reference for idiomatic, reproducible code.

- **New Features**
  - Device-agnostic patterns and full reproducibility setup.
  - Clean `nn.Module` structure and explicit weight init.
  - Training/validation loops with AMP, grad clipping, and `zero_grad(set_to_none=True)`.
  - DataLoader best practices (workers, pinning, persistence) and custom collate for variable-length data.
  - Checkpointing that saves full training state and uses `weights_only=True` on load.
  - Performance tips: AMP via `torch.amp`, gradient checkp

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
