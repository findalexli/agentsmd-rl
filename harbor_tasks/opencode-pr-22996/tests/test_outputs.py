"""Behavioral tests for the ConfigParse split refactor.

Each test is implemented by:
  1. copying a tiny self-contained `bun:test` driver from `/tests/` into
     `/workspace/opencode/packages/opencode/test/`,
  2. invoking `bun test <driver>` from `packages/opencode/`,
  3. asserting the bun process exits 0.

The bun drivers exercise the new `ConfigParse.jsonc(...)` /
`ConfigParse.schema(...)` API and the new single-options-object signature
of `ConfigVariable.substitute(...)`. Each driver uses real call paths
(no mocks) and asserts on observable return values.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PACKAGE = f"{REPO}/packages/opencode"
TEST_DIR = f"{PACKAGE}/test"
TESTS_INPUT = "/tests"


def _run_bun_test(driver_basename: str, dest_basename: str, timeout: int = 120) -> subprocess.CompletedProcess:
    src = os.path.join(TESTS_INPUT, driver_basename)
    dst = os.path.join(TEST_DIR, dest_basename)
    Path(TEST_DIR).mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)
    result = subprocess.run(
        ["bun", "test", f"test/{dest_basename}"],
        cwd=PACKAGE,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return result


def test_jsonc_parses_jsonc_text():
    """ConfigParse.jsonc(text, source) parses JSONC and returns the raw object."""
    r = _run_bun_test("check_jsonc.test.ts", "scaffold_check_jsonc.test.ts")
    assert r.returncode == 0, (
        f"ConfigParse.jsonc behavioral checks failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_schema_validates_with_zod():
    """ConfigParse.schema(schema, data, source) validates pre-parsed data with zod."""
    r = _run_bun_test("check_schema.test.ts", "scaffold_check_schema.test.ts")
    assert r.returncode == 0, (
        f"ConfigParse.schema behavioral checks failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_substitute_takes_options_object():
    """ConfigVariable.substitute now takes a single options object that includes 'text'."""
    r = _run_bun_test("check_substitute.test.ts", "scaffold_check_substitute.test.ts")
    assert r.returncode == 0, (
        f"ConfigVariable.substitute behavioral checks failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_old_combined_apis_removed():
    """ConfigParse.parse and ConfigParse.load no longer exist; jsonc/schema do."""
    r = _run_bun_test("check_removed.test.ts", "scaffold_check_removed.test.ts")
    assert r.returncode == 0, (
        f"Old API removal checks failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_repo_config_tests_pass():
    """The repo's own config test file (test/config/config.test.ts) still passes.

    This is a pass_to_pass check: it exercises the public Config service end-to-end
    and only stays green if the agent's parse-step refactor preserved behavior
    AND updated the in-repo tests to call the new ConfigParse API.
    """
    r = subprocess.run(
        ["bun", "test", "test/config/config.test.ts", "--timeout", "30000"],
        cwd=PACKAGE,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"Repo config tests failed.\n"
        f"--- stdout ---\n{r.stdout[-3000:]}\n--- stderr ---\n{r.stderr[-3000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_prepare():
    """pass_to_pass | CI job 'build-tauri' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_unit_run_unit_tests():
    """fail_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")