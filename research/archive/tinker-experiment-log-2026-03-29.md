# Tinker + E2B Experiment Log — 2026-03-29

## Setup

- **Model**: nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16 (MoE, 12B active)
- **Training**: GRPO via Tinker API (LoRA rank 32, LR 1e-5)
- **Sandboxes**: E2B (Pro plan, 100 concurrent limit)
- **Tasks**: 47 of 86 Harbor tasks (39 blocked by E2B template build rate limit)
- **Config**: group_size=4, groups_per_batch=8, max_turns=200, max_trajectory_tokens=128K

## Timeline

| Time | Event |
|------|-------|
| 17:52 | Cloned repos: SkyRL, tinker, tinker-cookbook, harbor-train, harbor |
| 18:57 | First e2e smoke test passed (Qwen3-8B, 1 task, 1 step) |
| 19:08 | First Nemotron run — crashed: E2B template build rate limit (429) |
| 19:09 | Pre-built templates: 83/86 cached, 3 failed (429) |
| 19:10 | Second run — crashed: stale template alias (404 on sandbox create) |
| 19:11 | Third run — crashed: 96 orphaned sandboxes eating concurrent quota |
| 19:38 | Fixed: killed orphans, but test.sh exit_code=-1 on every rollout |
| 19:44 | Root-caused: E2B runs as `user`, not `root`. Two permission issues |
| 20:13 | **Successful run launched** with root user fix + chmod 777 |
| 21:18 | Step 0 eval completed (8 rollouts). Train sampling in progress |

## Key Issues & Fixes

### 1. E2B template build rate limit (429)
- **Symptom**: `RateLimitException: max 20 concurrent template builds`
- **Cause**: First run tried to build all 86 templates simultaneously
- **Fix**: Pre-build script (`scripts/prebuild_e2b_templates.py`) with concurrency=5
- **Gotcha**: Even after deleting stuck templates, the rate limit persisted for 30+ min. Needed E2B support to reset. 39 templates still blocked at end of day.

### 2. Orphaned sandboxes blocking quota
- **Symptom**: All API calls returning 429, even single sandbox creation
- **Cause**: Crashed training runs left 90+ sandboxes alive (E2B sandboxes have 1hr-24hr TTL)
- **Fix**: `DELETE /sandboxes/{id}` for all running sandboxes via REST API
- **Lesson**: Always clean up sandboxes on crash. Add cleanup to error handlers.

### 3. E2B runs as `user`, not `root`
- **Symptom**: `test.sh exit_code=-1`, no reward file, `cd /root: Permission denied`
- **Cause**: E2B default user is `user`. Tinker-cookbook assumes Modal (runs as root). Two sub-issues:
  - (a) `HarborReward` uses `workdir="/root"` — inaccessible to non-root
  - (b) `/logs/verifier/` created by root in Dockerfile — non-root can't write reward.txt
- **Fix**: Run all commands as `user="root"` and `chmod 777 /logs/verifier` on sandbox creation. This matches Harbor's own E2B environment implementation.

### 4. Sandbox creation throttle slows training
- **Symptom**: Step 0 taking >2 hours. 14 min per group of 4 rollouts.
- **Cause**: Semaphore(15) + sleep(1.0) per sandbox creation, added to avoid 429s
- **Root cause**: Groups are processed sequentially. Each group creates 4 sandboxes (4 seconds of sleep), runs rollouts, then destroys them. Next group can't start until previous finishes.
- **Fix for next run**: Semaphore(50), no sleep. Templates are pre-built so creation is instant. E2B Pro allows 100 concurrent.

## Architecture Decisions

### Why tinker-cookbook over SkyRL?
- No local GPUs. Tinker API handles all GPU work (LoRA training on their clusters).
- SkyRL requires local GPU cluster (Ray + vLLM + FSDP/Megatron).
- Tinker-cookbook has a `harbor_rl` recipe that almost works out of the box.

### Why E2B over Modal?
- User already has E2B account and API key.
- Harbor natively supports E2B as sandbox provider.
- Required writing an E2B adapter (`scripts/e2b_sandbox.py`) since tinker-cookbook only ships Modal.

### Custom code in this repo (not modifying upstream)
- `scripts/e2b_sandbox.py` — E2BSandbox implementing SandboxInterface
- `scripts/train_harbor_e2b.py` — Self-contained training script with E2BHarborEnvGroupBuilder + E2BHarborDatasetBuilder (avoids `modal.Image` dependency in upstream harbor_env.py)
- `scripts/prebuild_e2b_templates.py` — One-time template warmup

## Results (Step 0 Eval, pre-training baseline)

Note: These are pre-training results — the Nemotron 120B base model without any RL fine-tuning. Some tasks already score 1.0, meaning the base model can solve them out of the box. The RL training signal comes from the tasks where it partially fails (0.15-0.95) or fully fails (0.0).

| Reward | Count | Pct |
|--------|-------|-----|
| 1.0 | 15+ | ~47% |
| 0.7-0.95 | ~8 | ~25% |
| 0.15-0.55 | ~2 | ~6% |
| 0.0 | 4 | ~12% |

Mean reward ~0.72 on eval. The high baseline means:
- Tasks scoring 1.0 already contribute no learning signal (GRPO advantage = 0 when all rollouts in a group succeed)
- The real training value comes from tasks with mixed outcomes (some rollouts pass, some fail within the same group)
- May need harder tasks or more diverse task set to get meaningful RL signal

## Cost Analysis

### Tinker API Pricing (Nemotron-3-Super-120B-A12B-BF16)

| Operation | Price per M tokens |
|-----------|-------------------|
| Prefill (input) | $0.38 |
| Sample (generation) | $0.96 |
| Train (forward_backward) | $1.16 |

### Actual spend (~1.5 hours into run, step 0 eval + partial step 0 train)

| Metric | Value |
|--------|-------|
| Total spend | ~$15 |
| Input tokens | ~52M |
| Output tokens | ~1M |
| Estimated prefill cost | 52 × $0.38 = ~$19.76 |
| Estimated sample cost | 1 × $0.96 = ~$0.96 |

Note: The 52:1 input/output ratio is extreme — the model reads far more context (system prompt + tool schemas + conversation history + bash output per turn) than it generates. Multi-turn rollouts compound this because the full history is re-sent each turn.

### Projected cost per full epoch (6 steps × 47 tasks)

Rough extrapolation from step 0 partial data:
- Step 0 eval (8 rollouts) + partial train (~12 of 32 rollouts) = ~$15, ~53M tokens
- Full step 0 (8 eval + 32 train = 40 rollouts) ≈ ~$50
- Full epoch (6 steps × 40 rollouts = 240 rollouts) ≈ ~$300
- **Cost per rollout ≈ ~$1.25**

### Cost optimization levers
- Reduce `max_turns` (200 → 50 would cut context accumulation dramatically)
- Reduce `group_size` (4 → 2, fewer rollouts per task but weaker advantage estimation)
- Use a smaller model (Qwen3-30B-A3B at $0.06/$0.18/$0.18 would be ~6x cheaper)
- Filter out tasks where base model already scores 1.0 (no learning signal anyway)

## Performance Profile

| Phase | Duration | Bottleneck |
|-------|----------|------------|
| Tinker session init | ~10s | One-time LoRA adapter creation |
| E2B sandbox creation | ~2s per sandbox | API call + container spin-up |
| E2B sandbox cleanup | <1s | DELETE API call |
| Model sampling (per turn) | ~30s | Tinker API, 120B model inference |
| Bash execution (per turn) | ~1-5s | E2B command execution |
| test.sh grading | ~5-10s | Runs in sandbox |
| GRPO gradient update | ~3s | Tinker forward_backward + optim_step |
| Full eval batch (8 groups × 1) | ~1 hour | Sequential groups + throttle |
| Full train batch (8 groups × 4) | ~1.5-2 hours | Sequential groups, 200 max turns |
| Full step (eval + train + grad) | ~2.5-3 hours | Dominated by sampling time |

### Sandbox lifecycle notes
- Sandboxes are created per-group, per-rollout (not pooled across groups)
- Each group creates `group_size` sandboxes, runs rollouts, then destroys them
- Groups are processed **sequentially** — group N+1 waits for group N to finish
- Orphaned sandboxes from crashed runs stay alive until their TTL expires (up to 24h on Pro)
- **Always clean up sandboxes after crashes**: `DELETE /sandboxes/{id}` via REST API
- The 1/sec creation throttle added 40+ seconds overhead per step; removed for next run

## TODO for Next Run

- [ ] Remove sandbox creation throttle (Semaphore 50, no sleep) — already in code
- [ ] Build remaining 39 E2B templates (need E2B support to reset rate limit)
- [ ] Add W&B logging (WANDB_API_KEY already in .env)
- [ ] Investigate ATIF trajectory.json export for Harbor viewer compatibility
- [ ] Consider adding Claude-Code-style tools (Read, Write, Edit) beyond just bash
- [ ] Add sandbox cleanup on crash/interrupt (signal handler)
