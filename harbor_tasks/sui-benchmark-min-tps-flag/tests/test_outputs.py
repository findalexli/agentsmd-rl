"""Tests for the --min-tps flag in sui-benchmark stress binary."""

import subprocess
import re
import os

REPO = "/workspace/sui"


def test_min_tps_flag_exists_in_options():
    """Test that min_tps field exists in Opts struct (fail-to-pass)."""
    options_file = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")

    with open(options_file, 'r') as f:
        content = f.read()

    # Check that min_tps field is defined with correct type
    assert "min_tps: Option<f64>" in content, "min_tps field not found in Opts struct"
    # Check that clap attribute exists (clap converts min_tps to --min-tps flag)
    assert "#[clap(long, global = true)]" in content, "clap attribute not found for min_tps"


def test_min_tps_cli_doc_comment():
    """Test that min_tps has proper documentation comment (fail-to-pass)."""
    options_file = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")

    with open(options_file, 'r') as f:
        content = f.read()

    # Check that min_tps has a doc comment explaining its purpose
    assert "If set, the stress binary will exit with a non-zero status code if the" in content, \
        "min_tps doc comment not found or incomplete"
    assert "achieved TPS is below this threshold" in content, \
        "min_tps threshold description not found"


def test_min_tps_logic_in_stress():
    """Test that min_tps validation logic exists in stress.rs (fail-to-pass)."""
    stress_file = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")

    with open(stress_file, 'r') as f:
        content = f.read()

    # Check that min_tps is extracted from opts at the start of main
    assert "let min_tps = opts.min_tps;" in content, "min_tps extraction not found in main"

    # Check that TPS validation logic exists
    assert "if let Some(min_tps) = min_tps" in content, "min_tps validation check not found"

    # Check that error is returned when TPS is below threshold
    assert "TPS {actual_tps:.2} is below minimum threshold {min_tps}" in content, \
        "TPS below threshold error message not found"


def test_min_tps_calculation_logic():
    """Test that the TPS calculation logic is correct (fail-to-pass)."""
    stress_file = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")

    with open(stress_file, 'r') as f:
        content = f.read()

    # Check that actual TPS is calculated from benchmark_stats
    assert "benchmark_stats.num_success_txes as f64" in content, \
        "num_success_txes not used in TPS calculation"
    assert "benchmark_stats.duration.as_secs_f64()" in content, \
        "duration not used in TPS calculation"

    # Check that duration has safety guard against division by zero
    assert ".max(1.0)" in content, "Duration safety guard (.max(1.0)) not found"


def test_license_headers_preserved():
    """Test that license headers are preserved (pass-to-pass)."""
    options_file = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    stress_file = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")

    for filepath in [options_file, stress_file]:
        with open(filepath, 'r') as f:
            content = f.read()

        assert "Copyright (c) Mysten Labs, Inc." in content, \
            f"License header missing in {filepath}"
        assert "SPDX-License-Identifier: Apache-2.0" in content, \
            f"SPDX license identifier missing in {filepath}"


def test_no_dead_code_allowed():
    """Test that no dead_code suppressions were added (pass-to-pass)."""
    options_file = os.path.join(REPO, "crates/sui-benchmark/src/options.rs")
    stress_file = os.path.join(REPO, "crates/sui-benchmark/src/bin/stress.rs")

    for filepath in [options_file, stress_file]:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check that no lint suppressions were added
        assert "#![allow(dead_code)]" not in content, \
            f"dead_code suppression found in {filepath}"
        assert "#[allow(dead_code)]" not in content, \
            f"dead_code suppression found in {filepath}"
        assert "#[allow(unused)]" not in content, \
            f"unused suppression found in {filepath}"


def test_repo_rustfmt():
    """Repo code passes rustfmt check (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "fmt", "--", "--check"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Rustfmt check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_cargo_check_sui_benchmark():
    """Repo's sui-benchmark crate compiles (pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "sui-benchmark"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Cargo check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
