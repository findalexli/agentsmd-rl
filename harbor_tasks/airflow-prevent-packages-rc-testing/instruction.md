# Fix RC Testing: Prevent Incompatible Packages

## Problem

When testing Release Candidate (RC) versions of Airflow and providers, the installation script uses `pip install --pre` to allow pre-release versions. This causes test failures because it can pull in newer, incompatible packages that were published after the RC was built.

The pip `--exclude-newer` option (available in pip 21.0+) allows specifying an ISO format timestamp to exclude packages published after that time. The installation script needs to use this option when installing pre-release versions to prevent incompatible package upgrades.

## Task

Modify `scripts/in_container/install_airflow_and_providers.py` to include pip's `--exclude-newer` option with a current ISO format timestamp when installing pre-release versions.

## Details

The target file contains pre-release installation logic that currently only uses `--pre` when the installation spec indicates a pre-release version is being installed. This logic needs to also use `--exclude-newer` with the current timestamp (in ISO format) to prevent newer packages from being pulled in.

Additionally, the console print messages about allowing pre-release versions should be updated to accurately reflect that both `--pre` and `--exclude-newer` are being used.

## Requirements

- The fix must use pip's `--exclude-newer` option with a current ISO format timestamp
- All pre-release installation paths in the file must be updated consistently
- The console print messages should accurately reflect what's being done
- The solution should follow the existing code style and patterns in the file
