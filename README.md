# agentsmd-rl

RL environments from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Research Question

> Do AI coding agents perform differently on repositories that contain human-written agent guidance files? And can we use this signal for better RL training?

Every major SWE benchmark (SWE-Gym, SWE-rebench V2, SWE-Universe, SWE-Next) mines PRs from GitHub to build training environments. None of them control for whether the repository already had agent instruction files at task time. This is an unmeasured confounder that could affect both evaluation scores and post-training outcomes.

See [research/agent-manifest-confounding.md](research/agent-manifest-confounding.md) for the full analysis.

## What This Repo Contains

### `harbor_tasks/`

Harbor-compatible benchmark tasks mined from recent PRs in repos with agent configs:

| Task | Source Repo | PR | Agent Config |
|------|-------------|-----|-------------|
| sglang-detokenizer-unbound-fix | sgl-project/sglang | #21471 | `.claude/skills/` |
| sglang-benchmark-empty-prompt | sgl-project/sglang | #21492 | `.claude/skills/` |
| sglang-hfrunner-hang-fix | sgl-project/sglang | #21582 | `.claude/skills/` |
| sglang-lscpu-topology-fix | sgl-project/sglang | #18520 | `.claude/skills/` |
| vllm-tool-parser-indexerror | vllm-project/vllm | #37958 | `CLAUDE.md` -> `AGENTS.md` |
| vllm-triton-cache-autotuning | vllm-project/vllm | #37188 | `CLAUDE.md` -> `AGENTS.md` |

Each task has:
- `instruction.md` -- what the agent sees
- `environment/Dockerfile` -- repo at the pre-fix commit (CPU-only, no GPU needed)
- `tests/test.sh` -- multi-grader verification -> `reward.json`
- `rubric.yaml` -- LLM rubric rules with source traceability to repo's agent config files
- `task.toml` -- Harbor metadata

### `research/`

- [agent-manifest-confounding.md](research/agent-manifest-confounding.md) -- analysis of agent config files as unmeasured confounders in SWE benchmarks
- [mvp-roadmap.md](research/mvp-roadmap.md) -- MVP architecture with dual-reward evaluation (execution + instruction adherence)
- [test-design-audit.md](research/test-design-audit.md) -- audit of test.sh design against OpenAI's SWE-bench Verified critique

## Running Tasks

Requires [Harbor](https://github.com/laude-institute/harbor):

```bash
# Build Docker image
docker build -t harbor-<task>:latest harbor_tasks/<task>/environment/

# Run with an agent
harbor run -p harbor_tasks/<task> -a claude-code -m claude-opus-4-6 -n 1
harbor run -p harbor_tasks/<task> -a terminus-2 -m anthropic/claude-opus-4-6 -n 1
```

## Evaluation Architecture

Multi-grader evaluation per task, following [Anthropic's agent eval guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). Each task's `test.sh` writes named metrics to `/logs/verifier/reward.json`:

```json
{"behavioral": 0.6, "regression": 0.2, "style": 0.1, "static_analysis": 0.1}
```

### Grader tiers

| Grader | Type | Weight | What it checks |
|--------|------|--------|----------------|
| **Fail-to-pass behavioral** | Deterministic | >=60% | Bug is fixed (implementation-agnostic) |
| **Pass-to-pass regression** | Deterministic | ~10-20% | Existing behavior not broken |
| **Static analysis** | Deterministic | ~10% | ruff/mypy pass on changed files |
| **LLM rubric** (planned) | Model-based | ~10% | Instruction adherence (ICR) |

### Design principles

Following [OpenAI's critique of SWE-bench Verified](https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/):

- **No narrow tests** that enforce specific variable names or API choices from the gold patch
- Accept multiple valid implementations -- test BEHAVIOR, not STRUCTURE
- Structural AST checks are supplementary only (<=40% weight)

See [research/test-design-audit.md](research/test-design-audit.md) for the full audit.

## Differentiation from Existing Work

| What | Who Does It | Do We? |
|------|------------|--------|
| Mine PRs -> Docker environments | SWE-rebench, SWE-Universe, SWE-Next, ... | Yes (standard) |
| Fail-to-pass test verification | SWE-bench (all variants) | Yes (standard) |
| RL training from PR environments | SWE-Gym, SWE-RL, DeepSWE, ... | Planned |
| **Filter for repos with agent configs** | **Nobody** | **Yes (novel)** |
| **Dual reward: execution + instruction adherence** | **Nobody** | **Planned (novel)** |
| **Measure agent-config confounding** | **Nobody** | **Yes (novel)** |

## Status

Early stage. 6 pilot tasks validated with Claude Code and Terminus 2 on Harbor (both score 1.0 with Opus 4.6).
