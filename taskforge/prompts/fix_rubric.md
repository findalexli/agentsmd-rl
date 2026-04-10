# Fix Rubric Rules Based on Validation Feedback

A Gemini judge has reviewed the rubric rules in `/workspace/task/eval_manifest.yaml` and found issues. Your job is to fix them based on the feedback below.

## Validation Feedback

Read the feedback file:
```bash
cat /workspace/rubric_feedback.json
```

The feedback contains:
- **Per-rule verdicts**: `accurate`, `partial`, `hallucinated`, or `redundant`
- **Explanations**: WHY each rule got its verdict (quotes actual file content vs what the rule claims)
- **Fix suggestions**: What to do with each rule
- **Missing rules**: Rules the judge thinks should be added (with source paths and line numbers)

## Instructions

### For each rule:

- **accurate**: Keep as-is
- **partial**: Fix the source attribution (correct file path, line numbers) — read the actual file to find the right lines
- **hallucinated**: REMOVE the rule entirely. Do not try to save it.
- **redundant**: REMOVE the rule. It duplicates a hard check (test assertion) and doesn't belong in rubric.

### For missing rules (from recall feedback):

The judge may suggest rules that should be added. For each:
1. Verify the source file exists: `cat /workspace/repo/<path>`
2. Verify the specific lines contain the claimed rule
3. If verified, add to rubric with correct source attribution
4. If not verified, skip it

### Writing the fixed rubric

Use python3 to write (NOT the Edit tool):

```bash
python3 << 'PYEOF'
import yaml

with open('/workspace/task/eval_manifest.yaml') as f:
    manifest = yaml.safe_load(f)

# Build the fixed rubric list
fixed_rules = [
    # Only include rules that are accurate or partial (after fixing)
    # Example:
    # {
    #     "rule": "Prefer single-word variable names for new locals",
    #     "source": {"path": "AGENTS.md", "lines": "28-32", "commit": "abc123"}
    # },
]

manifest['rubric'] = fixed_rules

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"Fixed rubric: {len(fixed_rules)} rules (was {len(manifest.get('rubric', []))})")
PYEOF
```

### Update status.json

```bash
python3 << 'PYEOF'
import json

with open('/workspace/task/status.json') as f:
    status = json.load(f)

if 'nodes' not in status:
    status['nodes'] = {}

status['nodes']['rubric_fix'] = {
    "status": "ok",
    "rules_kept": 0,      # fill in
    "rules_removed": 0,    # fill in
    "rules_added": 0,      # fill in from recall
    "notes": "Fixed based on Gemini precision/recall feedback"
}

with open('/workspace/task/status.json', 'w') as f:
    json.dump(status, f, indent=2)
PYEOF
```

## What NOT to do

- Do NOT keep hallucinated rules — remove them completely
- Do NOT keep redundant rules that duplicate test assertions
- Do NOT invent new rules without verifying them in actual config files
- Do NOT modify tests, Dockerfile, solve.sh, or instruction.md
