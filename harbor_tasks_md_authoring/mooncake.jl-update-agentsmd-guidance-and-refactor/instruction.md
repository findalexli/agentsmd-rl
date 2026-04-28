# Update AGENTS.md guidance and refactor agent skills

Source: [chalk-lab/Mooncake.jl#1134](https://github.com/chalk-lab/Mooncake.jl/pull/1134)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/inspect/SKILL.md`
- `.claude/skills/ir-inspect/SKILL.md`
- `.claude/skills/minimise/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

- Updates AGENTS.md with guidance on canonical test utilities (`test_rule`, `test_tangent_splitting`, `test_data`) and minimal-diff discipline.
- Adds a `minimise` skill for pruning fixes and tests to the smallest correct diff.
- Renames the `ir-inspect` skill to `inspect` and tightens its description.

Split from #1132.

<!-- managed-pr-summary:start -->

## CI Summary — GitHub Actions



### Documentation Preview

Mooncake.jl documentation for PR #1134 is available at:
https://chalk-lab.github.io/Mooncake.jl/previews/PR1134/

### Performance

Performance Ratio:
Ratio of time to compute gradient and time to compute function.
Warning: results are very approximate! See [here](https://github.com/chalk-lab/Mooncake.jl/tree/main/bench#inter-framework-benchmarking) for more context.
```
┌────────────────────────────┬──────────┬──────────┬─────────────┬─────────┬─────────────┬────────┐
│                      Label │   Primal │ Mooncake │ MooncakeFwd │  Zygote │ ReverseDiff │ Enzyme │
│                     String │   String │   String │      String │  String │      String │ String │
├────────────────────────────┼──────────┼──────────┼─────────────┼─────────┼─────────────┼────────┤
│                   sum_1000 │ 180.0 ns │     1.67 │        1.61 │   0.667 │        3.39 │   6.23 │
│                  _sum_1000 │ 952.0 ns │     6.85 │        1.02 │  4620.0 │        34.3 │   1.08 │
│               sum_sin_1000 │  8.52 μs │     3.47 │        1.48 │     1.3 │         8.9 │   1.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
