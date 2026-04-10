import yaml

with open("/workspace/task/eval_manifest.yaml", "r") as f:
    manifest = yaml.safe_load(f)

manifest["checks"].extend([
    {
        "id": "repo_delivery_resolve_media_retry",
        "type": "pass_to_pass",
        "origin": "repo_tests",
        "description": "Repo's delivery resolve-media-retry tests pass"
    },
    {
        "id": "repo_helpers",
        "type": "pass_to_pass",
        "origin": "repo_tests",
        "description": "Repo's helpers tests pass"
    },
    {
        "id": "repo_lane_delivery",
        "type": "pass_to_pass",
        "origin": "repo_tests",
        "description": "Repo's lane delivery tests pass"
    },
    {
        "id": "repo_send",
        "type": "pass_to_pass",
        "origin": "repo_tests",
        "description": "Repo's send tests pass"
    }
])

with open("/workspace/task/eval_manifest.yaml", "w") as f:
    yaml.dump(manifest, f, sort_keys=False, default_flow_style=False)
