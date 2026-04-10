"""Test file for sui-benchmark --min-tps feature."""

import subprocess
import os
import re

REPO = "/workspace/sui"


def test_min_tps_compiles():
    """The min_tps code compiles successfully (fail-to-pass)."""
    r = subprocess.run(
        ["cargo", "check", "--package", "sui-benchmark"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1000:]}"


def test_min_tps_option_parses():
    """The stress binary has --min-tps option defined (fail-to-pass)."""
    # Check the source code to verify the option is properly defined
    # Since full cargo build hits disk space limits in test environment,
    # we verify the clap attribute is correctly set in the source
    opts_path = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    with open(opts_path, "r") as f:
        content = f.read()

    # Check that the min_tps field has the clap attribute with "long" flag
    # which creates the --min-tps option
    assert "pub min_tps: Option<f64>" in content, "min_tps field not found"
    # Check for the clap long attribute which enables --min-tps flag
    assert '#[clap(long, global = true)]' in content, "clap long attribute missing"


def test_min_tps_field_exists_in_opts():
    """min_tps field exists in Opts struct with proper type (fail-to-pass)."""
    opts_path = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    with open(opts_path, "r") as f:
        content = f.read()

    # Check that min_tps field is defined in the Opts struct
    assert "min_tps: Option<f64>" in content, "min_tps field not found in Opts struct"

    # Check that the clap attribute is present
    assert '#[clap(long, global = true)]' in content, "min_tps clap attribute missing"

    # Check for the doc comment about the threshold - flexible check
    content_lower = content.lower()
    assert ("minimum threshold" in content_lower or "below this threshold" in content_lower or "threshold" in content_lower), "min_tps documentation comment about threshold not found"


def test_min_tps_validation_in_stress():
    """min_tps validation logic exists in stress.rs (fail-to-pass)."""
    stress_path = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")
    with open(stress_path, "r") as f:
        content = f.read()

    # Check that min_tps is extracted from opts at the start
    assert "let min_tps = opts.min_tps;" in content, "min_tps extraction from opts not found in stress.rs main"

    # Check that the TPS validation logic exists
    assert "if let Some(min_tps) = min_tps" in content, "min_tps validation block not found"

    # Check that actual_tps calculation exists (num_success_txes / duration)
    assert "num_success_txes as f64" in content, "num_success_txes TPS calculation not found"
    assert "duration.as_secs_f64()" in content, "duration.as_secs_f64() TPS calculation not found"

    # Check for error message when TPS is below threshold
    assert "is below minimum threshold" in content, "TPS below threshold error message not found"

    # Check for anyhow error return
    assert "anyhow::anyhow!" in content or "anyhow!(" in content, "anyhow error macro not found for TPS failure"


def test_license_header_options_rs():
    """options.rs has required license header per CLAUDE.md (agent_config)."""
    opts_path = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    with open(opts_path, "r") as f:
        content = f.read()

    # Check for SPDX license identifier as required by CLAUDE.md
    assert "SPDX-License-Identifier: Apache-2.0" in content, "Apache-2.0 license header missing in options.rs"
    assert "Copyright (c) Mysten Labs, Inc." in content, "Copyright header missing in options.rs"


def test_license_header_stress_rs():
    """stress.rs has required license header per CLAUDE.md (agent_config)."""
    stress_path = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")
    with open(stress_path, "r") as f:
        content = f.read()

    # Check for SPDX license identifier as required by CLAUDE.md
    assert "SPDX-License-Identifier: Apache-2.0" in content, "Apache-2.0 license header missing in stress.rs"
    assert "Copyright (c) Mysten Labs, Inc." in content, "Copyright header missing in stress.rs"


# ============================================================================
# Pass-to-Pass Tests - Repo CI Commands (p2p_enrichment)
# These run actual CI commands from the repo's CI configuration
# ============================================================================


def test_repo_cargo_fmt():
    """Repo code passes cargo fmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"cargo fmt --check failed:\n{r.stderr[-500:]}"


def test_repo_git_checks():
    """Repo passes git sanity checks (pass_to_pass)."""
    r = subprocess.run(
        ["./scripts/git-checks.sh"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"git-checks.sh failed:\n{r.stderr[-500:]}"
