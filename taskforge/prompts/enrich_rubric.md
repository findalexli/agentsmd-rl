# Enrich Rubric Rules (Deep Analysis)

Your job: add **high-quality, PR-specific** rubric rules to eval_manifest.yaml. Generic rules are worthless — every rule must be directly evaluable by reading this PR's diff against a specific config file instruction.

## Context

Read `/workspace/task/status.json` if it exists — the `nodes` section has notes from previous steps. Update the `rubric_enrichment` node in status.json when done.

## Input

Task files at `/workspace/task/`. The full source repo is cloned at `/workspace/repo/` at the base commit.

## Phase 1: Understand the Gold Solution

**This is the most important step.** You cannot write relevant rubric rules without deeply understanding what the PR changes.

```bash
# Read the gold patch — understand EXACTLY what files changed and how
cat /workspace/task/solution/solve.sh

# Read the PR instruction to understand intent
cat /workspace/task/instruction.md
```

Write down:
- Which files does solve.sh modify? (exact paths)
- What is the nature of each change? (new function, bug fix, config change, new test, documentation update)
- What languages/frameworks are involved?
- Does the PR modify any config/doc files (CLAUDE.md, AGENTS.md, README.md, etc.)?

## Phase 2: Discover and Read Config Files

```bash
# Find all agent config files in the repo
find /workspace/repo -maxdepth 4 \
  \( -name "CLAUDE.md" -o -name "AGENTS.md" -o -name "SKILL.md" \
     -o -name ".cursorrules" -o -name "copilot-instructions.md" \
     -o -name "CONVENTIONS.md" \) \
  | grep -v node_modules | head -10

# Also check .claude directory
find /workspace/repo -path "*/.claude/*" -name "*.md" | grep -v node_modules | head -10
```

If `/workspace/repo/` doesn't exist, fall back to extracting repo/commit from task.toml or Dockerfile and using `gh api`:
```bash
REPO=$(python3 -c "import tomllib; t=tomllib.load(open('/workspace/task/task.toml','rb')); print(t.get('source_repo',''))" 2>/dev/null)
COMMIT=$(python3 -c "import tomllib; t=tomllib.load(open('/workspace/task/task.toml','rb')); print(t.get('base_commit',''))" 2>/dev/null)
gh api "repos/$REPO/git/trees/$COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|copilot-instructions\\.md|CONVENTIONS\\.md|\\.claude/")) | .path'
```

Read the FULL content of each config file (up to 5 files, prioritize files closest to changed paths).

## Phase 3: Cross-Reference — The Critical Filter

For EACH rule in each config file, apply this filter:

**Q1: Does this rule apply to the specific files/language this PR touches?**
- A rule about "Python imports" is irrelevant if the PR only touches TypeScript files.
- A rule about "test structure" is irrelevant if the PR doesn't touch tests.
- A rule about "commit messages" or "PR workflow" is NEVER relevant (not evaluable from diff).

**Q2: Can a judge verify this rule by reading the PR's diff?**
- "Use descriptive variable names" — too vague, a judge can't objectively evaluate this. REJECT.
- "All new public APIs must have JSDoc comments" — specific and verifiable. KEEP.
- "Error messages should include the operation that failed" — verifiable. KEEP.

**Q3: Does the gold solution actually demonstrate compliance (or violation) of this rule?**
- Read the actual diff from solve.sh. Does it add code that relates to this rule?
- If the gold solution doesn't touch anything related to the rule, the rule is irrelevant to THIS PR.

## Phase 4: Draft Rubric Rules

Extract **1-5 rubric rules** that passed ALL three filters. For each rule:

- Write it as a **specific, evaluable statement** tied to what this PR does
- Include the exact config file path and line numbers as source
- If the PR modifies a config/doc file AND a rubric rule is about that specific edit, include the `reference` field with the expected content

**GOOD rules** (specific, tied to this PR):
- "New Bazel rules should use the project's custom macros from //tools:defaults.bzl rather than native rules" (when PR adds Bazel targets)
- "Error handling in API endpoints must use the project's AppError class, not raw HTTP exceptions" (when PR adds an endpoint)
- "New CLI subcommands must be documented in the SKILL.md commands section" (when PR adds a CLI command AND the config file says to do this)

**BAD rules** (reject these):
- "Follow existing code style" — too vague, not a specific convention
- "Write clean, maintainable code" — subjective noise, not actionable
- "Be consistent with surrounding code" — no concrete check
- "Add appropriate tests" — out of scope (tests are separate checks)
- "Use feature branches" — process rule, not evaluable from diff

## Phase 5: Self-Critique and Revise

Before writing to eval_manifest.yaml, review each drafted rule:

1. **Re-read solve.sh** — does this rule relate to the language/files/patterns the gold solution touches?
2. **Imagine you are the judge** reading the diff + this rule. Could you give a clear PASS/FAIL? If not, the rule is too vague.
3. **Check for duplicates** — don't repeat rules already in eval_manifest.yaml

**Keep rules that are**:
- Specific coding conventions (naming, error handling patterns, import style) that apply to the changed files' language
- Documentation requirements that apply when certain types of changes are made
- Architectural patterns (e.g., "use the project's custom macros" or "avoid try/catch") that a judge can verify in the diff

**Remove rules that are**:
- Pure process rules (PR workflow, branch naming, commit messages) — not evaluable from code diff
- Completely subjective with no concrete check ("write clean code")
- About file types/languages not touched by this PR

A recurring repo convention like "prefer single-word variable names" or "avoid try/catch" IS a valid rubric rule if the PR touches code where it applies — the judge checks the diff against the rule. Do NOT reject rules just because they apply broadly within the repo.

## Phase 6: Write to eval_manifest.yaml

**CRITICAL**: Use `python3` to read, merge, and write the YAML file. Do NOT use the Edit tool for YAML — it's error-prone. Always use this exact pattern:

```bash
python3 << 'PYEOF'
import yaml

# Read existing manifest
with open('/workspace/task/eval_manifest.yaml') as f:
    manifest = yaml.safe_load(f)

# Build new rubric rules
new_rules = [
    {
        "rule": "Specific, evaluable rule text tied to this PR",
        "source": {
            "path": "CLAUDE.md",       # repo-relative path to the config file
            "lines": "45-48",          # actual line(s) containing the rule
            "commit": "abc123def",     # base commit (before the PR)
        }
    },
    {
        "rule": "Another specific rule",
        "source": {
            "path": ".claude/skills/dev/SKILL.md",
            "lines": "12",
            "commit": "abc123def",
        },
        # reference: ONLY for agentmd-edit tasks where PR modifies this config file
        "reference": "Expected content that should be added"
    },
]

# Merge: keep existing rules, append new ones (no duplicates)
existing = manifest.get('rubric') or []
existing_texts = {r['rule'] if isinstance(r, dict) else r for r in existing}
for rule in new_rules:
    if rule['rule'] not in existing_texts:
        existing.append(rule)
manifest['rubric'] = existing

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"Wrote {len(existing)} rubric rules to eval_manifest.yaml")
PYEOF
```

Adapt the `new_rules` list to your actual rules. Include `reference` field only for agentmd-edit tasks where the PR modifies the config file itself.

**IMPORTANT**:
- `source.path` must be the repo-relative path to the config file
- `source.commit` must be the base commit
- `source.lines` should point to the actual line(s) containing the rule
- Do NOT invent rules that aren't in the config files
- Do NOT add generic filler rules

## Phase 7: Update status.json

Use `python3` to merge (do NOT overwrite existing nodes):

```bash
python3 << 'PYEOF'
import json

with open('/workspace/task/status.json') as f:
    status = json.load(f)

if 'nodes' not in status:
    status['nodes'] = {}

status['nodes']['rubric_enrichment'] = {
    "status": "ok",
    "configs_found": ["CLAUDE.md", ".claude/skills/dev/SKILL.md"],
    "rules_added": 2,
    "rules_rejected": 5,
    "rejection_reasons": "3 too generic, 2 not applicable to changed files",
    "notes": "Added 2 rules specific to the Bazel build changes in this PR"
}

with open('/workspace/task/status.json', 'w') as f:
    json.dump(status, f, indent=2)
PYEOF
```

## What NOT to do

- Do NOT modify tests, Dockerfile, solve.sh, or instruction.md
- Do NOT add rules that aren't traceable to an actual config file
- Do NOT add duplicate rules
- Do NOT add generic rules that could apply to any PR
- Do NOT add rules about PR workflow, commit messages, or branching
- Do NOT pad with filler to hit a rule count — 0 relevant rules is a valid outcome
