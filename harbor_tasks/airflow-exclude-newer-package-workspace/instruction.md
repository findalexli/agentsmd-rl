# Task: Add exclude-newer-package=false for all workspace components

## Problem

The Airflow project uses `uv` as its package manager with a workspace configuration. Currently, when installing pre-release or locally-built packages, the `exclude-newer` time-based restriction (set to "4 days") can cause resolution issues for workspace packages.

The `exclude-newer` setting prevents uv from selecting packages newer than a specified date, but this should NOT apply to workspace packages that are built locally or installed from source.

## What you need to do

1. **Add `exclude-newer-package = false` entries** in `pyproject.toml` for ALL workspace components in both:
   - `[tool.uv.exclude-newer-package]` section
   - `[tool.uv.pip.exclude-newer-package]` section

   Workspace components are defined in `[tool.uv.sources]` with `workspace = true`.

2. **Update `scripts/ci/prek/update_airflow_pyproject_toml.py`** to auto-generate these entries:
   - Add a function `get_all_workspace_component_names()` that reads workspace components from `[tool.uv.sources]`
   - Add marker constants for the sections (`START_EXCLUDE_NEWER_PACKAGE`, `END_EXCLUDE_NEWER_PACKAGE`, etc.)
   - Call `insert_documentation()` to generate entries for both sections

3. **Update `scripts/in_container/install_airflow_and_providers.py`**:
   - Remove the `--exclude-newer` flag with `datetime.now().isoformat()` from the installation commands
   - The exclusion is now handled by pyproject.toml configuration instead

4. **Update `scripts/ci/docker-compose/remove-sources.yml`**:
   - Add a mount for `pyproject.toml` so uv configuration is available in the container

## Key files to modify

- `/workspace/airflow/pyproject.toml` - add exclude-newer-package entries
- `/workspace/airflow/scripts/ci/prek/update_airflow_pyproject_toml.py` - auto-generation logic
- `/workspace/airflow/scripts/in_container/install_airflow_and_providers.py` - remove datetime-based exclude-newer
- `/workspace/airflow/scripts/ci/docker-compose/remove-sources.yml` - mount pyproject.toml

## Hints

- Look at how other auto-generated sections are handled in `update_airflow_pyproject_toml.py` (e.g., provider workspace members)
- The pattern for auto-generated sections uses `insert_documentation()` with start/end markers
- The `[tool.uv.sources]` section in pyproject.toml lists all workspace packages
- Each workspace package should have `exclude-newer-package = false` set explicitly
