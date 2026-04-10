import json
import os

with open('/workspace/task/status.json', 'r') as f:
    status = json.load(f)

status['nodes']['p2p_enrichment']['notes'] = 'Docker build failed: go.mod requires go >= 1.25.0 (running go 1.24.13). Stopped to let the validate agent fix Docker issues later, as per instructions.'

os.remove('/workspace/task/status.json')

with open('/workspace/task/status.json', 'w') as f:
    json.dump(status, f, indent=2)
