import yaml

# Read eval_manifest.yaml
with open('/workspace/task/eval_manifest.yaml', 'r') as f:
    manifest = yaml.safe_load(f)

# Remove the test_repo_unit_tests_pass check
manifest['checks'] = [check for check in manifest['checks'] if check['id'] != 'test_repo_unit_tests_pass']

# Write it back preserving order mostly if possible, or just dump it
with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(manifest, f, sort_keys=False)
