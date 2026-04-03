# Fix registry incremental build processing all providers

## Problem

The `breeze registry extract-data --provider <name>` command is supposed to run an incremental build that only extracts data for the specified provider(s). However, while `extract_metadata.py` correctly receives the `--provider` flag, the other two extraction scripts (`extract_parameters.py` and `extract_connections.py`) do not receive it. This causes incremental builds to scan all ~99 providers and process ~1625 modules for parameters and connections, even when only a single provider was requested.

Additionally, when running in incremental mode, the `merge_registry_data.py` script crashes if the `modules.json` file doesn't exist — which happens when `--provider` mode skips module extraction.

## Expected Behavior

When `--provider` is specified:
1. All three extraction scripts should receive and respect the `--provider` flag, only processing the requested provider(s)
2. The merge script should handle a missing `modules.json` gracefully, treating it as empty and preserving existing modules for other providers

After fixing the code, update the relevant documentation (`registry/AGENTS.md` and `registry/README.md`) to reflect how incremental builds actually work now — particularly around the S3 sync behavior that avoids overwriting real data with incomplete stubs from non-target providers.

## Files to Look At

- `dev/breeze/src/airflow_breeze/commands/registry_commands.py` — builds the command string that runs the extraction scripts inside breeze
- `dev/registry/merge_registry_data.py` — merges incremental extraction results with existing S3 data
- `dev/registry/extract_connections.py` — extracts connection metadata; already supports `--provider` but wasn't receiving it
- `registry/AGENTS.md` — agent guidelines documenting the registry deployment architecture
- `registry/README.md` — documents the incremental build flow including merge and S3 sync steps
