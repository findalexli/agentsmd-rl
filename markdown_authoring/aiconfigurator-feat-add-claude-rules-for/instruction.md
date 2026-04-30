# feat: Add claude rules for generator to improve robustness

Source: [ai-dynamo/aiconfigurator#663](https://github.com/ai-dynamo/aiconfigurator/pull/663)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/generator-development.md`
- `.claude/rules/generator/config_schema.md`
- `.claude/rules/generator/cross_module_impact.md`
- `.claude/rules/generator/debugging.md`
- `.claude/rules/generator/guard_rails.md`
- `.claude/rules/generator/new_backend_version.md`
- `.claude/rules/generator/rule_authoring.md`
- `.claude/rules/generator/template_authoring.md`
- `.claude/rules/generator/testing.md`
- `AGENTS.md`

## What to add / change

#### Overview:

To ensure that AI-generated code aligns more closely with our requirements and to prevent new bugs from being introduced as the code evolves, added corresponding rules.


<!-- This is an auto-generated comment: release notes by coderabbit.ai -->
## Summary by CodeRabbit

* **Documentation**
  * Added comprehensive generator development references: pipeline workflow, configuration and template guidance, cross-module impact and guard rails, debugging and rule/template authoring best practices, backend-version update steps, and layered testing guidance.

Note: Documentation-only updates; no user-facing functionality changed.
<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
