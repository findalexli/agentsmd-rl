# feat: improve monitor-run skill

Source: [PrimeIntellect-ai/prime-rl#2179](https://github.com/PrimeIntellect-ai/prime-rl/pull/2179)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/monitor-run/SKILL.md`

## What to add / change

## Summary
- Restructured into runbook (what to do) + reference (how to do it) sections
- Added STATUS.md format for periodic check-ins with progress/stability/performance summaries
- Added metrics reference tables organized by dynamics, stability, and performance
- Added errors & warnings section with grep patterns and common issues per component
- Added tmux session detection and restart safety instructions
- Added configs section, log format docs, and vLLM metrics endpoint

Start the tmux launcher

```bash
bash scripts/tmux.sh
```

In the `Launcher` window, start the run

```
uv run rl @ configs/alphabet_sort/rl.toml --clean-output-dir
```

Then in the `Claude` window, type `/monitor-run` and watch the magic

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- CURSOR_SUMMARY -->
---

> [!NOTE]
> **Low Risk**
> Low risk documentation-only change that updates operational guidance without modifying runtime code. Main risk is procedural confusion if the new monitoring/restart instructions are misapplied.
> 
> **Overview**
> Rewrites the `monitor-run` skill guide into a clearer *Runbook* (what to do) and *Reference* (how to do it) structure, focused specifically on monitoring RL training runs.
> 
> Adds a `STATUS.md` check-in template and cadence guidance, plus expanded log/metric references (progress/stability/performance), vLLM metrics endpoint hints, and a dedicated errors/warnings section with suggested `grep` patterns.
> 
> Introduces

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
