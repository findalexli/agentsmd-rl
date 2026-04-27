# Improve the `monitor-run` skill

The repository at `/workspace/prime-rl` ships agent skills in `skills/`
(symlinked to `.claude/skills/`). The current `skills/monitor-run/SKILL.md`
exists but is a flat reference dump that does not actually tell an agent
*what to do* when asked to monitor a training run — it only describes
where files live. We want to rewrite it into an actionable runbook.

Rewrite **`skills/monitor-run/SKILL.md`** so it teaches an agent how to
monitor an ongoing prime-rl training run end-to-end.

## What the rewrite must include

Preserve the existing YAML frontmatter (`name: monitor-run` and the
`description:` field) at the top of the file unchanged.

Restructure the body into two top-level sections:

1. `## Runbook` — what the agent should *do*, in order.
2. `## Reference` — background detail (output dir layout, log paths,
   metric tables, processes, errors-and-warnings guidance).

### Runbook contents

The runbook must walk the agent through:

- **On launch**: gather context (configs, processes, current step) and
  write an initial summary into `{output_dir}/STATUS.md`.
- **Recurring check-ins**: by default check in every **1 hour** (the
  researcher can override). At each check-in the agent verifies
  processes are alive, scans logs for errors/warnings, notes the
  current step and key metrics, and **appends** an entry to
  `{output_dir}/STATUS.md`. Always append — never overwrite previous
  entries.
- **STATUS.md entry format**: each entry must include at minimum a
  `**Step**` field (current step / max steps) and a `**Health**` field
  (`Healthy | Degraded | Down`), plus short progress / stability /
  performance / notes summaries.
- **Restarting a run**: never run launch or kill commands directly from
  the agent's shell. Instead, dispatch them to the tmux **Launcher**
  window using `tmux send-keys` so the researcher can see exactly what
  was executed. Include a small bash snippet showing how to obtain the
  current tmux session name and `send-keys` to the `Launcher` window.

### Reference contents

The reference section must cover:

- The output directory and tmux session conventions (where the resolved
  configs live, where to find the Launcher window).
- The `{output_dir}/configs/` TOML layout (in particular `rl.toml`).
- The log directory layout under `{output_dir}/logs/` for trainer,
  orchestrator, inference, and per-env servers/workers, plus the
  loguru log-line format.
- Metric tables grouped into **Progress** (reward, seq_len, truncation,
  eval scores, etc.), **Stability** (mismatch_kl, entropy,
  optim/grad_norm), and **Performance** (trainer / orchestrator step
  timings and bottleneck-attribution metrics, env server lag, vLLM
  inference pressure).
- A vLLM live-metrics subsection that shows how to query the running
  inference server's Prometheus endpoint (`/metrics` on the inference
  port) and calls out at least the KV-cache pressure metric
  `vllm:gpu_cache_usage_perc`.
- An **Errors and warnings** subsection (`### Errors and warnings`)
  that explains how to scan all logs for `WARNING` and `ERROR` lines
  (e.g. with `grep -E "WARNING|ERROR"`), and what kinds of issues
  typically show up in env workers, the orchestrator, the trainer, and
  inference.
- A processes subsection summarizing the prime-rl process tree
  (Launcher → Inference / Orchestrator / Trainer).

## Constraints

- Edit only `skills/monitor-run/SKILL.md`. Do not modify other files.
- Keep the rewrite focused on RL training runs (the skill is meant for
  monitoring an in-flight `uv run rl ...` run).
- The file must remain valid UTF-8 markdown with balanced ``` code
  fences.
- Do not change the YAML frontmatter's `name` or `description` fields.

## Why this matters

Per the repo's `AGENTS.md`, skills under `skills/` "teach agents how to
handle specific workflows" and you are responsible for "making implicit
knowledge explicit". The current file lists facts about logs and
metrics but does not give an agent a procedure to actually monitor a
run — what to write down, when to check in, or how to safely restart.
The rewrite turns this skill from a reference into an executable
runbook.
