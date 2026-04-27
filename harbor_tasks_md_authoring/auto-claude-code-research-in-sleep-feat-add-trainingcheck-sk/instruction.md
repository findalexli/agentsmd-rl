# feat: add training-check skill — WandB-based training quality monitoring

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#65](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/65)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/training-check/SKILL.md`

## What to add / change

## Summary

Adds a `training-check` skill that periodically reads WandB metrics during training to catch quality issues early — before a broken run wastes hours of GPU time.

**The gap:** Existing monitoring (`/monitor-experiment`, watchdog) checks if the process is alive and GPUs are active, but doesn't check if training is actually making progress. A run with NaN loss, diverging gradients, or degrading eval metrics will look "healthy" to process-level monitoring.

**The fix:** `training-check` reads WandB metrics (loss trend, eval metrics, NaN/Inf, gradient norms) and makes a judgment: clearly fine → continue; clearly bad → stop; ambiguous → escalate to Codex MCP for a second opinion.

## What's Added

### `skills/training-check/SKILL.md`

**3-step workflow:**
1. **Read WandB metrics** — loss trend, eval metrics, NaN/Inf, spikes, lr schedule, gradient norm. Falls back to log file via SSH if WandB is unreachable.
2. **CC judgment** — clear signals (NaN, divergence, good progress) are acted on directly without Codex.
3. **Codex judgment** (only when unsure) — ambiguous cases (flat loss, noisy metrics, slightly below baseline) are escalated to Codex MCP for a second opinion.

**Adaptive check interval:** starts at 10 min, increases to 60 min when consistently healthy. Resets to 10 min after any anomaly.

## How It Fits (Two-Layer Monitoring)

| Layer | Tool | What it checks | Frequency |
|-------|------|----------------|-----------|
| Process health | watchdog.py / `/monitor-e

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
