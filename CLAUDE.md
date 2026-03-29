# agentsmd-rl

RL environments from repositories with agent instruction files (AGENTS.md, CLAUDE.md, .cursorrules).

## Repository Structure

```
harbor_tasks/           # Harbor-compatible benchmark tasks
  <task>/
    instruction.md      # Agent reads this (bug description, not the fix)
    task.toml           # Metadata (difficulty, timeouts, resources)
    environment/Dockerfile  # Clones repo at pre-fix commit
    tests/test.sh       # Fail-to-pass verification (0.0-1.0 reward)
research/               # Research docs and analysis
```

## Running Tasks

```bash
# Build and run with Harbor
docker build -t harbor-<task>:latest harbor_tasks/<task>/environment/
harbor run -p harbor_tasks/<task> -a claude-code -m claude-opus-4-6 -n 1
harbor run -p harbor_tasks/<task> -a terminus-2 -m anthropic/claude-opus-4-6 -n 1
```

## Task Design Philosophy

Following OpenAI's SWE-bench Verified critique:

- **Fail-to-pass behavioral tests** as the primary tier (implementation-agnostic)
- **Pass-to-pass regression tests** to prevent breakage
- **Structural AST checks** only as supplementary partial-credit (<=40% weight)
- **No narrow tests** that enforce specific variable names or API choices from the gold patch
- Accept multiple valid implementations -- test BEHAVIOR, not STRUCTURE

## Task Selection Criteria

Tasks must come from repos that have agent instruction files:
- CLAUDE.md, AGENTS.md, .claude/skills/, .cursorrules, .github/copilot-instructions.md

And satisfy standard requirements:
- Public repo, specific base commit, no secrets/accounts needed
- CPU-testable (no GPU required for verification)
- Fix is non-trivial but contained (1-5 files changed)

## Adding a New Task

Use `/scaffold-task owner/repo#PR_NUMBER` to create a task from a PR.

Then validate: `/validate-task <task-name>` and `/audit-tests <task-name>`.

## Open Concerns

### Contamination
Tasks sourced from popular public repos (sglang 44k stars, vllm 50k stars) carry contamination risk. Frontier models may have seen the PRs during training. Mitigations:
- Use very recent PRs (< 2 weeks old)
- Run contamination probes (can the model reproduce the gold patch?)
- Target less-popular repos when possible

### Agent config confounding
The core research question: repos with AGENTS.md may be systematically different from repos without. See research/agent-manifest-confounding.md.
