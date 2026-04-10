"""
Task: biome-md-last-hardline
Repo: biome @ 0bc2198735230c3bad14a831652543bd304fa0d6
PR:   9856

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/biome"

# Pre-built test binaries from Docker image (avoids rebuild disk space issues)
PREBUILT_DIR = f"{REPO}/target/debug/deps"
PRETTIER_TESTS_BIN = f"{PREBUILT_DIR}/prettier_tests-a6b733937f766aac"
SPEC_TESTS_BIN = f"{PREBUILT_DIR}/spec_tests-eb1a2b4fc04afb19"
QUICK_TEST_BIN = f"{PREBUILT_DIR}/quick_test-bd8b494489ee3ad7"


def _run_prebuilt_test(binary_path: str, test_filter: str = "", timeout: int = 600) -> subprocess.CompletedProcess:
    cmd = [binary_path]
    if test_filter:
        cmd.extend([test_filter, "--test-threads=1"])
    else:
        cmd.append("--test-threads=1")
    return subprocess.run(cmd, cwd=REPO, capture_output=True, timeout=timeout)


# [static] pass_to_pass
def test_cargo_check():
    """Formatter crate compiles without errors."""
    env = os.environ.copy()
    env["CARGO_INCREMENTAL"] = "0"
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_formatter"],
        cwd=REPO, capture_output=True, timeout=600, env=env,
    )
    assert r.returncode == 0, f"Compilation failed:\n{r.stderr.decode()[-2000:]}"


# [repo_tests] pass_to_pass
def test_markdown_formatter_tests():
    """Repo's markdown formatter prettier tests pass (pass_to_pass)."""
    r = _run_prebuilt_test(PRETTIER_TESTS_BIN, "", timeout=600)
    assert r.returncode == 0, f"Markdown formatter prettier tests failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass
def test_markdown_parser_check():
    """Markdown parser crate compiles without errors (pass_to_pass)."""
    env = os.environ.copy()
    env["CARGO_INCREMENTAL"] = "0"
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_parser"],
        cwd=REPO, capture_output=True, text=True, timeout=120, env=env,
    )
    assert r.returncode == 0, f"Markdown parser check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_markdown_formatter_spec_tests():
    """Repo's markdown formatter spec tests pass (pass_to_pass)."""
    r = _run_prebuilt_test(SPEC_TESTS_BIN, "formatter", timeout=600)
    assert r.returncode == 0, f"Markdown formatter spec tests failed:\n{r.stderr.decode()[-500:]}"


# [repo_tests] pass_to_pass - Additional test for markdown syntax crate
def test_markdown_syntax_check():
    """Markdown syntax crate compiles without errors (pass_to_pass)."""
    env = os.environ.copy()
    env["CARGO_INCREMENTAL"] = "0"
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_syntax"],
        cwd=REPO, capture_output=True, text=True, timeout=120, env=env,
    )
    assert r.returncode == 0, f"Markdown syntax check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - Additional test for markdown factory crate
def test_markdown_factory_check():
    """Markdown factory crate compiles without errors (pass_to_pass)."""
    env = os.environ.copy()
    env["CARGO_INCREMENTAL"] = "0"
    r = subprocess.run(
        ["cargo", "check", "-p", "biome_markdown_factory"],
        cwd=REPO, capture_output=True, text=True, timeout=120, env=env,
    )
    assert r.returncode == 0, f"Markdown factory check failed:\n{r.stderr[-500:]}"


# [pr_diff] fail_to_pass
def test_single_last_hardline():
    """Single-line paragraph: trailing hard line break spaces removed."""
    r = _run_prebuilt_test(QUICK_TEST_BIN, "test_single_last_hardline", timeout=600)
    assert r.returncode == 0, f"Test failed:\n{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"


# [pr_diff] fail_to_pass
def test_multi_last_hardline():
    """Multi-line paragraph: last hard line removed, middle preserved."""
    r = _run_prebuilt_test(QUICK_TEST_BIN, "test_multi_last_hardline", timeout=600)
    assert r.returncode == 0, f"Test failed:\n{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"


# [pr_diff] fail_to_pass
def test_varied_last_hardline():
    """Different paragraph content to prevent hardcoded solutions."""
    r = _run_prebuilt_test(QUICK_TEST_BIN, "test_varied_last_hardline", timeout=600)
    assert r.returncode == 0, f"Test failed:\n{r.stdout.decode()[-1000:]}\n{r.stderr.decode()[-1000:]}"
