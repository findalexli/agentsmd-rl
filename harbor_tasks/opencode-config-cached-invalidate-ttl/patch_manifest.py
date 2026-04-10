import yaml

with open('/workspace/task/eval_manifest.yaml', 'r') as f:
    data = yaml.safe_load(f)

# Filter out the "destructuring" rule
new_rubric = []
for r in data.get('rubric', []):
    if 'destructuring' not in r['rule']:
        new_rubric.append(r)

data['rubric'] = new_rubric

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
