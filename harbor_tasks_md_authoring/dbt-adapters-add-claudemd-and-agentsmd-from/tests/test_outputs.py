"""Behavioral checks for dbt-adapters-add-claudemd-and-agentsmd-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/dbt-adapters")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '> **Note:** `pre-commit` is managed as a hatch environment dependency — you do not need to install it globally. `hatch run setup` installs it inside the hatch virtualenv and registers the git hooks. `' in text, "expected to find: " + '> **Note:** `pre-commit` is managed as a hatch environment dependency — you do not need to install it globally. `hatch run setup` installs it inside the hatch virtualenv and registers the git hooks. `'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'Integration tests live in `tests/functional/`. They require a `test.env` file with credentials (never commit this file). See `test.env.example` for required variables.' in text, "expected to find: " + 'Integration tests live in `tests/functional/`. They require a `test.env` file with credentials (never commit this file). See `test.env.example` for required variables.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'The `dbt-adapters/src/dbt/adapters/catalogs/` package provides a plugin system for external table formats (Apache Iceberg, etc.):' in text, "expected to find: " + 'The `dbt-adapters/src/dbt/adapters/catalogs/` package provides a plugin system for external table formats (Apache Iceberg, etc.):'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Credentials:** `account`, `user`, `password`, `database`, `warehouse`, `role`, `schema`, `authenticator`, `private_key_path`, `private_key_passphrase`, `oauth_client_id`, `oauth_client_secret`, `cli' in text, "expected to find: " + '**Credentials:** `account`, `user`, `password`, `database`, `warehouse`, `role`, `schema`, `authenticator`, `private_key_path`, `private_key_passphrase`, `oauth_client_id`, `oauth_client_secret`, `cli'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '`BaseSimpleMaterializations`, `BaseEmpty`, `BaseEphemeral`, `BaseSnapshotTimestamp`, `BaseSnapshotCheck`, `BaseIncremental`, `BaseGenericTests`, `BaseSingularTests`, `BaseAdapterMethod`, `BaseValidate' in text, "expected to find: " + '`BaseSimpleMaterializations`, `BaseEmpty`, `BaseEphemeral`, `BaseSnapshotTimestamp`, `BaseSnapshotCheck`, `BaseIncremental`, `BaseGenericTests`, `BaseSingularTests`, `BaseAdapterMethod`, `BaseValidate'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '**Credentials:** `s3_staging_dir`, `s3_tmp_table_dir`, `region_name`, `database`, `schema`, `work_group`, `aws_profile_name`, `aws_access_key_id`, `aws_secret_access_key`, `poll_interval`, `num_retrie' in text, "expected to find: " + '**Credentials:** `s3_staging_dir`, `s3_tmp_table_dir`, `region_name`, `database`, `schema`, `work_group`, `aws_profile_name`, `aws_access_key_id`, `aws_secret_access_key`, `poll_interval`, `num_retrie'[:80]

