# agentsmd-rl

See [README.md](README.md) for project overview, research question, and task list.

## Repository Structure

```
claude-code-rl-w-tinker/    # RL training library (proxy + GRPO + Tinker API)
  anthropic_proxy.py        #   Anthropic→Tinker proxy, captures logprobs at generation time
  train.py                  #   Training loop: Harbor Trial → GRPO → Tinker forward_backward
  harbor_tokenization.py    #   Multi-turn chat tokenization for RL
  test_*.py                 #   Unit + e2e + logprob fidelity tests
taskforge/                  # Task construction toolkit
  models.py                 #   Pydantic: EvalManifest, Check, RubricRule, SourceRef
  config.py                 #   Shared config patterns, is_config_file(), extract_config_hunks()
  pipeline.py               #   Parallel pipeline orchestrator (claude -p)
  judge.py                  #   LLM judge for config edit rubric
  e2b.py                    #   E2B sandbox validation
  templates/task_template/  #   Task template with placeholders (copied by /scaffold-task)
harbor_tasks/               # Benchmark tasks: code-only bug fixes (~420)
harbor_tasks_agentmd_edits/ # Benchmark tasks: code + config edits (~236)
  <task>/
    instruction.md          #   Agent reads this (bug description, not the fix)
    task.toml               #   Metadata (difficulty, timeouts, resources)
    eval_manifest.yaml      #   Checks + rubric rules with source traceability
    environment/Dockerfile  #   Clones repo at pre-fix commit
    solution/solve.sh       #   Gold patch (idempotent)
    tests/test.sh           #   Deterministic tests → /logs/verifier/reward.txt
scripts/                    # Shell orchestrators for overnight batch pipelines
research/                   # Research docs and analysis
```

## Task Selection Criteria

Tasks must come from repos that have agent instruction files (Tier 1):
- `CLAUDE.md`, `AGENTS.md`, `CONVENTIONS.md` (at any level)
- `.claude/rules/*.md` (modular path-scoped rules)
- `.claude/skills/*/SKILL.md` (skills with frontmatter)
- `.claude/agents/*.md` (custom subagent definitions)
- `.cursorrules`, `.cursor/rules/`, `.github/copilot-instructions.md`

Tier 2 files (README.md, CONTRIBUTING.md) are only relevant when paired with a Tier 1 rule.

And satisfy standard requirements:
- Public repo, specific base commit, no secrets/accounts needed
- CPU-testable (no GPU required for verification)
- Fix is non-trivial but contained (1-5 files changed)

## Adding a New Task

1. `/scaffold-task owner/repo#PR_NUMBER` — create task from a PR (includes test audit + rubric extraction)
2. `/validate-task <task-name>` — Docker oracle test (build, nop=0, gold=1)

## Evaluation Architecture

### Scoring: Binary

All checks must pass → reward `1`. Any check fails → reward `0`.
This matches every major SWE benchmark (SWE-bench, Terminal Bench, SWE-smith, R2E-Gym).

### The atom: Check

Every assertion in test.sh is a `Check` (Pydantic model in `taskforge/models.py`) with:
- `id`: slug identifier (e.g., `empty_stem_gets_fallback`)
- `type`: `fail_to_pass` (must fail on base, pass on fix) or `pass_to_pass` (must pass always)
- `origin`: where it came from — `pr_diff`, `repo_tests`, `agent_config`, `static`
- `source`: `SourceRef` (path + lines + commit) — **required** when `origin == agent_config`

### eval_manifest.yaml

Declares all checks and rubric rules. Schema version `2.0`. See `taskforge/models.py` for the Pydantic models: `EvalManifest`, `Check`, `RubricRule`, `SourceRef`, `SourcePR`.

```yaml
version: "2.0"
source:
  repo: owner/repo
  pr: 123
  base_commit: abc123

checks:
  - id: crash_on_none
    type: fail_to_pass
    origin: pr_diff
    description: Function crashes when input is None

  - id: no_wildcard_imports
    type: fail_to_pass
    origin: agent_config
    description: No wildcard imports
    source:
      path: AGENTS.md
      lines: "30"
      commit: abc123

rubric:  # Soft rules → LLM judge (when LLM_JUDGE=1)
  - rule: "Be consistent with the style of the surrounding code."
    source:
      path: AGENTS.md
      lines: "45"
      commit: abc123
```

### Source attribution

Every check with `origin: agent_config` MUST have a `source` pointing to the exact file and line range. Use **full repo-relative paths** (`extensions/CLAUDE.md`, not `CLAUDE.md`).

### Output

test.sh writes `1` or `0` to `/logs/verifier/reward.txt`.

**CRITICAL**: Reward MUST be written to `/logs/verifier/reward.txt` — this is a Docker bind mount that Harbor's verifier reads. Writing to `/tests/reward.txt`, `/workspace/reward.txt`, or any other path will silently fail.

## Rubric Source Traceability

Known repos with multiple config files — always enumerate before citing:
- `openclaw/openclaw`: root + `extensions/`, `src/channels/`, `src/plugins/`, `src/gateway/protocol/`
- `anomalyco/opencode`: root + `packages/app/`, `packages/opencode/`, `packages/desktop/`
- `pytorch/pytorch`: root + `torch/_dynamo/`

Enumerate with: `gh api repos/OWNER/REPO/git/trees/COMMIT?recursive=1 --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md")) | .path'`
