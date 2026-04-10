import yaml
import json

with open('/workspace/task/eval_manifest.yaml', 'r') as f:
    manifest = yaml.safe_load(f)

if 'rubric' not in manifest or manifest['rubric'] is None:
    manifest['rubric'] = []

manifest['rubric'].append({
    "rule": "Follow the Mintlify documentation structure (e.g., placing core documentation in docs/, guides in guides/) when modifying documentation.",
    "source": {
        "path": "docs/mintlify/CLAUDE.md",
        "lines": "5-13",
        "commit": "ab4a15df0055b65b8c2fa6e3ce1115d55ecfad22"
    }
})

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, sort_keys=False)

with open('/workspace/task/status.json', 'r') as f:
    status = json.load(f)

if 'nodes' not in status:
    status['nodes'] = {}

status['nodes']['rubric_enrichment'] = {
    "status": "ok",
    "configs_found": ["docs/mintlify/AGENTS.md", "docs/mintlify/CLAUDE.md"],
    "rules_added": 1,
    "notes": "Added 1 conditional rubric rule from docs/mintlify/CLAUDE.md. The config file is specific to documentation, so the rule is formulated to apply only if documentation is modified."
}

with open('/workspace/task/status.json', 'w') as f:
    json.dump(status, f, indent=2)

print("Updated both files successfully.")
