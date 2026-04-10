import json

with open('/task/status.json', 'r') as f:
    data = json.load(f)

data['nodes']['p2p_enrichment']['notes'] = 'Added test_repo_datapack_and_train_controller running pytest on tests/test_datapack.py and tests/test_train_controller.py. Also relies on existing ruff format/lint tests.'

with open('/task/status.json', 'w') as f:
    json.dump(data, f, indent=2)
