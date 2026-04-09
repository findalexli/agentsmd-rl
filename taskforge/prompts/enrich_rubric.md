# Enrich Rubric Rules

Add rubric rules to an existing task's eval_manifest.yaml by discovering the repo's agent config files.

## Context

Read `/workspace/task/status.json` if it exists — the `nodes` section has notes from previous steps. Update the `rubric_enrichment` node in status.json when done.

## Input

Task files at `/workspace/task/`.

## Goal

Repos with agent instruction files (CLAUDE.md, AGENTS.md, SKILL.md, .cursorrules, etc.) contain rules about coding style, conventions, and practices. These rules should be captured as `rubric` entries in eval_manifest.yaml so the rubric judge can evaluate whether a solution follows them.

## Steps

### 1. Read the task files

- `eval_manifest.yaml` — check existing rubric rules and source PR info
- `solution/solve.sh` — the gold patch (shows which files changed)
- `environment/Dockerfile` — tells you the repo and base commit
- `task.toml` — may have `source_repo` and `source_pr`

### 2. Discover agent config files

From the Dockerfile or task.toml, extract the repo URL and base commit. Then discover ALL agent config files:

```bash
# Method 1: Read from task.toml (most reliable)
REPO=$(python3 -c "import tomllib; t=tomllib.load(open('/workspace/task/task.toml','rb')); print(t.get('source_repo',''))" 2>/dev/null)
COMMIT=$(python3 -c "import tomllib; t=tomllib.load(open('/workspace/task/task.toml','rb')); print(t.get('base_commit',''))" 2>/dev/null)

# Method 2: Fallback to Dockerfile parsing if task.toml doesn't have it
if [ -z "$REPO" ]; then
  REPO=$(grep -oP 'github\.com/\K[^/]+/[^/.\s]+' /workspace/task/environment/Dockerfile | head -1)
fi
if [ -z "$COMMIT" ]; then
  COMMIT=$(grep -oP '(?:git checkout |git fetch.*origin )\K[a-f0-9]{7,}' /workspace/task/environment/Dockerfile | head -1)
fi

# List all config files at the base commit
gh api "repos/$REPO/git/trees/$COMMIT?recursive=1" \
  --jq '.tree[] | select(.path | test("CLAUDE\\.md|AGENTS\\.md|SKILL\\.md|\\.cursorrules|\\.cursor/rules|copilot-instructions\\.md|CONVENTIONS\\.md")) | .path'
```

### 3. Fetch and read each config file

```bash
gh api "repos/$REPO/contents/$PATH?ref=$COMMIT" --jq '.content' | base64 -d
```

Read the FULL content of each file. If more than 5 config files are found, prioritize files in the same directory tree as the changed files (from solve.sh), plus the root-level configs. Read at most 5 files total to stay focused.

### 4. Extract relevant rules

For each config file, identify rules that apply to the PR's changed files (from solve.sh):

**Classify each rule:**
- **Soft/subjective rules → rubric entry** (e.g., "Follow existing code style", "Use descriptive variable names", "Document public APIs")
- **Programmatic rules → already covered by agent_config checks** (skip if already in eval_manifest)
- **Irrelevant rules** (e.g., "Use feature branches for PRs") → skip

**Extract 1-5 rubric rules** per task. Prefer fewer high-quality rules over padding with generic ones. Prefer rules that:
- Apply to the specific files/language the PR changes
- Are verifiable by reading the gold solution
- Come from the closest-scoped config (subdirectory > root)

### 5. Add rubric entries to eval_manifest.yaml

```yaml
rubric:
  - rule: "Follow existing code style. Check neighboring files for patterns."
    source:
      path: "CLAUDE.md"
      lines: "45"
      commit: "abc123def"
  - rule: "Use comments to explain invariants, not narrate code."
    source:
      path: ".claude/skills/dev/SKILL.md"
      lines: "12-15"
      commit: "abc123def"
```

**IMPORTANT**: 
- `source.path` must be the repo-relative path to the config file
- `source.commit` must be the base commit (before the PR)
- `source.lines` should point to the actual line(s) containing the rule
- Do NOT invent rules that aren't in the config files
- Do NOT duplicate rules already in the rubric section

### 6. Optionally add `reference` field (agentmd-edit tasks only)

Only populate `reference` when the PR itself modifies a config/doc file AND the rubric rule is about that specific edit. For pure style/convention rules (e.g., "follow existing code style"), leave `reference` empty — the judge evaluates those by reading the rule text against the agent's diff.

```yaml
rubric:
  - rule: "Document new CLI commands in SKILL.md"
    source:
      path: ".claude/skills/cli-dev/SKILL.md"
      lines: "8-12"
      commit: "abc123"
    reference: |
      ## CLI Commands
      - `route` - Set up network route mocking
      - `route-list` - List active routes
      - `unroute` - Remove routes
```

### 7. Update status.json

```python
import json
status = json.load(open('/workspace/task/status.json'))
if 'nodes' not in status:
    status['nodes'] = {}
status['nodes']['rubric_enrichment'] = {
    "status": "ok",
    "configs_found": ["CLAUDE.md", ".claude/skills/dev/SKILL.md"],
    "rules_added": 3,
    "notes": "Added 3 rubric rules from CLAUDE.md and SKILL.md"
}
json.dump(status, open('/workspace/task/status.json', 'w'), indent=2)
```

## What NOT to do

- Do NOT modify tests, Dockerfile, solve.sh, or instruction.md
- Do NOT add rules that aren't traceable to an actual config file
- Do NOT add duplicate rules
- Do NOT leave rubric empty if the repo has agent config files
