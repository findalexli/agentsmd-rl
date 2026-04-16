# Exclude-Newer Package Configuration for Workspace Components

## Problem

When installing pre-release versions of Airflow packages, the installation script uses `--exclude-newer` with the current datetime to restrict package selection. This causes issues with workspace packages (local monorepo packages) because they may have timestamps that don't align with external package constraints.

The `scripts/in_container/install_airflow_and_providers.py` script passes `--exclude-newer` with a dynamically-generated datetime for pre-release installations. When a datetime is passed to `--exclude-newer`, workspace packages may fail to install correctly because their timestamps differ from the exclusion threshold.

Additionally, there's no programmatic way to identify all workspace component names from `pyproject.toml`. The `[tool.uv.sources]` section defines workspace components where entries have `workspace = true`, but no function exists to extract these names.

## Requirements

### 1. Workspace Component Extraction

Create a function that extracts all workspace component names from `[tool.uv.sources]` in `pyproject.toml`. The function should:
- Read the TOML configuration from the appropriate file
- Access the `[tool.uv.sources]` section
- Filter entries where the value is a dict with `workspace = true`
- Return a sorted list of the workspace component names

### 2. Configuration Section Markers

Define marker constants for automatically-generated `exclude-newer-package` configuration sections. The markers should:
- Include `START_EXCLUDE_NEWER_PACKAGE` and `END_EXCLUDE_NEWER_PACKAGE` constants
- Include a pip-specific variant with `START_EXCLUDE_NEWER_PACKAGE_PIP` or similar naming
- Contain descriptive text indicating these sections are automatically generated
- Reference `update_airflow_pyproject_toml.py` as the generating script in the marker text

### 3. Simplified Pre-release Installation

Remove the datetime-based `--exclude-newer` argument from pre-release installation commands in `scripts/in_container/install_airflow_and_providers.py`. After the fix:
- Pre-release installations should use `--pre` without the dynamic datetime-based `--exclude-newer` argument
- The old pattern `--exclude-newer` with `datetime.now().isoformat()` should no longer appear in the installation commands
- The exclusion configuration will instead be handled via static `pyproject.toml` settings

## Files to Modify

- `scripts/ci/prek/update_airflow_pyproject_toml.py` - Add workspace extraction functionality and configuration markers
- `scripts/in_container/install_airflow_and_providers.py` - Remove datetime-based --exclude-newer usage from pre-release installation commands
