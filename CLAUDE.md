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
  models.py                 #   Pydantic: EvalManifest, Check, RubricRule, DistractorRule, SourceRef
  config.py                 #   Shared config patterns, is_config_file(), extract_config_hunks()
  gemini_rubric_constructor.py  # Gemini structured output rubric gen + Kimi validation loop
  hierarchy_context.py      #   Config hierarchy extractor (root → leaf AGENTS.md)
  pipeline.py               #   Parallel pipeline orchestrator (claude -p)
  judge.py                  #   LLM judge for config edit rubric (Gemini structured output)
  rubric_validator.py       #   Precision/recall validator for rubric rules
  e2b.py                    #   E2B sandbox validation
  templates/task_template/  #   Task template with placeholders (copied by /scaffold-task)
harbor_tasks/               # Benchmark tasks: code-only bug fixes (775)
harbor_tasks_agentmd_edits/ # Benchmark tasks: code + config edits (232, 4-track eval)
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

# Track 1: Hard tests (binary pass/fail via test.sh)
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

# Track 2: Gold config edits (for agentmd-edit tasks)
# Extracted deterministically from solve.sh by config_extract.py
config_edits:
  - path: "AGENTS.md"
    tier: 1            # 1 = agent instruction file, 2 = documentation
    gold_added: "## Writing Standards\nSee style guide..."
    gold_removed: ""

# Track 3: Positive rubric — conventions the gold solution FOLLOWS
rubric:
  - rule: "Prefer single-word variable names for new locals"
    source:
      path: AGENTS.md
      lines: "28-32"
    evidence: "Gold uses `question` not `shouldEnableQuestion`"
    category: naming
    verification: llm_judge           # Gemini evaluates agent diff vs rule

  - rule: "No wildcard imports in TypeScript files"
    source:
      path: AGENTS.md
      lines: "15"
    verification: programmatic        # Baked into test.sh, deterministic
    check_cmd: "! grep -r 'import \\*' /workspace/repo/src/"

# Track 4: Distractors — conventions that create COLLISIONS
distractors:
  - rule: "Inline single-use variables to reduce noise"
    source:
      path: AGENTS.md
      lines: "45-50"
    collision_type: rule_conflict
    why_distracting: "Conflicts with readability; extracted variable clarifies conditional logic"
    severity: medium
```

### Verification methods

| Method | When | How | Cost |
|--------|------|-----|------|
| `programmatic` | Rule is checkable by grep/AST | `check_cmd` in test.sh | Free |
| `llm_judge` | Rule requires judgment | Gemini reads diff vs rule | ~$0.01 |
| `semantic_diff` | Config edit comparison | Gemini compares gold vs agent | ~$0.01 |

Prefer `programmatic` when possible — deterministic, no LLM cost, reproducible. Use `llm_judge` only when the rule requires semantic understanding (style, architecture decisions). `semantic_diff` is only for Track 2 config edits.

### Four evaluation tracks

| Track | What | How | Artifact |
|-------|------|-----|----------|
| 1. Code correctness | Did the agent fix the bug? | test.sh → nop=0, gold=1 | `checks` |
| 2. Config edits | Did the agent update config files correctly? | Gold config vs agent diff (Gemini) | `config_edits` |
| 3. Positive rubric | Does the agent follow relevant conventions? | LLM judge on diff vs rules | `rubric` |
| 4. Distractors | Does the agent ignore irrelevant conventions? | Check agent didn't follow collision rules | `distractors` |

Track 2 gold references are extracted by `taskforge/config_extract.py` at scaffold time — deterministic, no LLM hallucination. Track 3 rubric rules and Track 4 distractors are generated by `taskforge/gemini_rubric_constructor.py` using Gemini structured output (constrained decoding with `responseSchema`) and optionally validated via a Kimi→Gemini→Kimi cross-validation loop.

Distractor collision types: `rule_conflict`, `scope_ambiguity`, `meta_confusion`, `architecture_boundary`, `would_cause_bug`. Severity: `high` (bug), `medium` (waste), `low` (minor confusion).

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
