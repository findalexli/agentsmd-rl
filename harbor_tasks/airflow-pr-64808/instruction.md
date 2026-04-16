# Fix group/extra bug in initialize_virtualenv

The `scripts/tools/initialize_virtualenv.py` script builds `uv sync` command-line arguments
incorrectly when the user specifies extras like `dev,graphviz`. Currently it uses `--group`
for every item, but dependency groups and optional extras must be distinguished:

- Items defined in the `[dependency-groups]` section of `pyproject.toml` must use
  `--group <name>`
- Items defined in the `[project.optional-dependencies]` section must use
  `--extra <name>`

For example, given extras `dev,graphviz,otel`:
- `dev` is a dependency group → should produce `--group dev`
- `graphviz` and `otel` are optional extras → should produce `--extra graphviz --extra otel`

The script is located at `scripts/tools/initialize_virtualenv.py` in the Airflow repository.

## Symptom

When a user passes a comma-separated list of extras to the script, all items are passed
to `uv sync` with `--group`, even those that are optional extras. The correct behavior is:
- Parse `pyproject.toml` to determine which items are dependency groups vs optional extras
- Items in `[dependency-groups]` use `--group <name>`
- Items in `[project.optional-dependencies]` use `--extra <name>`

The dependency groups currently defined in the Airflow `pyproject.toml` include: `dev`, `docs`,
`docs-gen`, `leveldb`. The optional extras currently defined include: `graphviz`, `otel`,
`all-core`, `async`, `kerberos`, and many provider-specific extras.
