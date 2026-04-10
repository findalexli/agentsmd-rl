import yaml
with open('/workspace/task/eval_manifest.yaml', 'r') as f:
    data = yaml.safe_load(f)

data['checks'].extend([
    {
        'id': 'test_repo_ruff_check_migrations_dir',
        'description': 'Repo\'s ruff linting passes on entire migrations dir',
        'type': 'pass_to_pass',
        'origin': 'repo_tests'
    },
    {
        'id': 'test_repo_ruff_format_migrations_dir',
        'description': 'Repo\'s ruff formatting passes on entire migrations dir',
        'type': 'pass_to_pass',
        'origin': 'repo_tests'
    },
    {
        'id': 'test_repo_pyflakes_migrations_dir',
        'description': 'Repo\'s pyflakes static analysis passes on entire migrations dir',
        'type': 'pass_to_pass',
        'origin': 'repo_tests'
    },
    {
        'id': 'test_repo_python_compile_migrations_dir',
        'description': 'Repo\'s entire migrations dir compiles as valid Python',
        'type': 'pass_to_pass',
        'origin': 'repo_tests'
    }
])

with open('/workspace/task/eval_manifest.yaml', 'w') as f:
    yaml.dump(data, f, sort_keys=False)
