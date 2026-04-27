# Add dse-loop skill for autonomous design space exploration

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#6](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/6)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/dse-loop/SKILL.md`

## What to add / change

## Summary

- New `dse-loop` skill for autonomous design space exploration, targeting computer architecture and EDA workflows (gem5, Yosys, Verilator, formal verification, etc.)
- Runs an autonomous loop: run program → analyze results → tune parameters → repeat, until objective is met or timeout
- Infers parameter ranges from source code when user only provides parameter names (no explicit ranges required)
- Domain-aware defaults: powers-of-2 for caches/buffers, geometric series for BMC depths, enumeration for boolean/enum flags
- State persistence via `DSE_STATE.json` + `dse_log.csv` for context window recovery
- Full reporting: convergence curve, parameter sensitivity, Pareto frontier, best configuration

## Motivation

The existing skills cover idea discovery, review loops, and paper writing — but there's no skill for the common architecture/EDA task of sweeping a design space to find optimal configurations. This is a frequent need when tuning microarchitecture parameters, synthesis settings, or formal verification bounds.

## Example usage

```bash
# Minimal — just name the parameters, agent infers ranges from code
/dse-loop "Run gem5 mcf benchmark. Tune: L1D_SIZE, L2_SIZE, ROB_ENTRIES. Objective: maximize IPC. Timeout: 3h"

# Fully specified
/dse-loop "Simulate processor with FIFO_DEPTH [4,8,16,32], ISSUE_WIDTH [1,2,4]. Objective: max throughput/area. Timeout: 2h"
```

## Test plan

- [ ] Verify skill loads without errors in Claude Code (`/dse-loop`)
- [ ] Test with a si

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
