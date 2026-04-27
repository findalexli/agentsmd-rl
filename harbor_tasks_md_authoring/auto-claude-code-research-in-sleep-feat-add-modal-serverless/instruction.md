# feat: add Modal serverless GPU support (gpu: modal)

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#107](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/107)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/experiment-bridge/SKILL.md`
- `skills/monitor-experiment/SKILL.md`
- `skills/run-experiment/SKILL.md`
- `skills/serverless-modal/SKILL.md`

## What to add / change

## Summary

- Adds a new `serverless-modal` skill for running GPU workloads on [Modal](https://modal.com) — a serverless GPU cloud with zero-config deployment (no SSH, no Docker, auto scale-to-zero)
- Integrates `gpu: modal` as a fourth GPU mode in `run-experiment` alongside `gpu: local`, `gpu: remote`, and `gpu: vast`
- Updates `experiment-bridge` and `monitor-experiment` for Modal awareness (lifecycle rules, monitoring via `modal app logs`)
- **Task-driven GPU selection** — same pattern as `vast-gpu`: analyze model size → estimate VRAM → pick GPU → estimate cost → confirm with user before running
- Auto scale-to-zero: billing stops the instant code finishes. No manual instance destruction needed (unlike vast.ai)
- Includes 6 code patterns: one-shot training, web API, vLLM inference, batch parallel, LoRA fine-tuning, multi-GPU distributed

### Free tier & cost protection

- **Without card**: $5/month free credit
- **With card (recommended)**: $30/month free credit — bind a payment method at https://modal.com/settings
- **SECURITY**: Always bind cards on the official Modal website. NEVER enter payment info through CLI tools
- **Spending limit**: Set a workspace spending limit (Settings → Usage → Spending Limit) to cap costs — Modal auto-pauses workloads when hit

### Files changed

| File | Change |
|------|--------|
| `skills/serverless-modal/SKILL.md` | **New** — full Modal skill (auth, pricing, VRAM guide, 6 patterns, cost estimation, CLI reference, CLAUDE.md integration, 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
