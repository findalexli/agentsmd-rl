import json

with open('/workspace/task/status.json', 'r') as f:
    data = json.load(f)

if 'p2p_enrichment' not in data.get('nodes', {}):
    data.setdefault('nodes', {})['p2p_enrichment'] = {}

data['nodes']['p2p_enrichment']['notes'] = 'Failed to build Docker image task-env. The build failed with: "no space left on device" during layer extraction. Stopped as instructed.'
data['nodes']['p2p_enrichment']['status'] = 'docker_build_failed'

with open('/workspace/task/status.json', 'w') as f:
    json.dump(data, f, indent=2)
