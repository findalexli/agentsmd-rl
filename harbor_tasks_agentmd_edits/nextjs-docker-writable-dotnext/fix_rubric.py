import yaml
import json

# Read current manifest
with open('/workspace/task/eval_manifest.yaml') as f:
    manifest = yaml.safe_load(f)

# Build the fixed rubric list - only keeping accurate rules
fixed_rules = [
    {
        "rule": "When editing files in a subdirectory, consult all README.md files in the directory path from repo root to target directory first (per AGENTS.md convention)",
        "source": {"path": "AGENTS.md", "lines": "44-53", "commit": "15fcfb9ce4ec73c6ff8d08d72201726b983127fa"}
    },
    {
        "rule": "Code blocks in documentation must include the filename attribute for all code examples",
        "source": {"path": ".claude/skills/update-docs/references/DOC-CONVENTIONS.md", "lines": "47-102", "commit": "15fcfb9ce4ec73c6ff8d08d72201726b983127fa"}
    },
    {
        "rule": "Documentation updates must pass pnpm lint validation (prettier formatting)",
        "source": {"path": ".claude/skills/update-docs/SKILL.md", "lines": "92-96", "commit": "15fcfb9ce4ec73c6ff8d08d72201726b983127fa"}
    },
]

original_count = len(manifest.get('rubric', []))
manifest['rubric'] = fixed_rules

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, default_flow_style=False, sort_keys=False, allow_unicode=True)

print(f"Fixed rubric: {len(fixed_rules)} rules (was {original_count})")

# Update status.json
with open('/workspace/task/status.json') as f:
    status = json.load(f)

if 'nodes' not in status:
    status['nodes'] = {}

status['nodes']['rubric_fix'] = {
    "status": "ok",
    "rules_kept": 3,
    "rules_removed": 2,
    "rules_added": 0,
    "notes": "Fixed based on Gemini precision/recall feedback - removed 2 hallucinated rules (emoji/callout syntax)"
}

with open('/workspace/task/status.json', 'w') as f:
    json.dump(status, f, indent=2)

print("Updated status.json")
