"""
Task: workers-sdk-createcloudflare-add-nodejs-version-check
Repo: workers-sdk @ 0de69890c8503bb67e391e7ad5578c7001b7798e
PR:   cloudflare/workers-sdk#13243

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/workers-sdk"
C3 = Path(REPO) / "packages" / "create-cloudflare"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_bin_shim_rejects_old_node():
    """bin/c3.js must exit with error when Node.js version is too old."""
    bin_path = C3 / "bin" / "c3.js"
    assert bin_path.exists(), "bin/c3.js must exist"
    # Mock process.versions.node to 18.0.0 and require the shim
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '18.0.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0, (
        f"Expected non-zero exit for old Node, got {result.returncode}"
    )
    assert "requires at least" in result.stderr.lower(), (
        f"Expected version error message 'requires at least' in stderr, got: {result.stderr[:300]}"
    )


def test_bin_shim_error_mentions_user_version():
    """Error message must tell the user which version they are running."""
    bin_path = C3 / "bin" / "c3.js"
    assert bin_path.exists(), "bin/c3.js must exist"
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '16.3.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert result.returncode != 0
    assert "16.3.0" in result.stderr, (
        f"Error should mention the user's Node version 16.3.0, got: {result.stderr[:300]}"
    )


def test_bin_shim_suggests_version_manager():
    """Error message should suggest at least one Node version manager."""
    bin_path = C3 / "bin" / "c3.js"
    assert bin_path.exists(), "bin/c3.js must exist"
    script = (
        "Object.defineProperty(process, 'versions', "
        "{value: {...process.versions, node: '18.0.0'}});"
        f"require({json.dumps(str(bin_path))});"
    )
    result = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    stderr_lower = result.stderr.lower()
    assert "volta" in stderr_lower or "nvm" in stderr_lower or "fnm" in stderr_lower, (
        f"Error should suggest a version manager (volta/nvm/fnm), got: {result.stderr[:300]}"
    )


def test_bin_shim_passes_current_node():
    """bin/c3.js must exist and NOT show version error when Node >= 20."""
    bin_path = C3 / "bin" / "c3.js"
    assert bin_path.exists(), "bin/c3.js must exist"
    result = subprocess.run(
        ["node", str(bin_path)],
        capture_output=True, text=True, timeout=15,
        cwd=str(C3),
    )
    # dist/cli.js may not exist so it might error, but NOT with version message
    assert "requires at least" not in result.stderr.lower(), (
        f"Should not show version error on Node >= 20: {result.stderr[:300]}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — verify repo CI/CD still works
# ---------------------------------------------------------------------------


def test_c3_typecheck():
    """C3 package TypeScript typecheck passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            pnpm run build --filter='@cloudflare/workers-utils' --filter='@cloudflare/codemod' --filter='@cloudflare/mock-npm-registry' > /dev/null 2>&1 &&
            cd packages/create-cloudflare &&
            pnpm run build > /dev/null 2>&1 &&
            pnpm run check:type
        """],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert result.returncode == 0, f"C3 typecheck failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_c3_unit_tests():
    """C3 package unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            pnpm run build --filter='@cloudflare/workers-utils' --filter='@cloudflare/codemod' --filter='@cloudflare/mock-npm-registry' > /dev/null 2>&1 &&
            cd packages/create-cloudflare &&
            pnpm run build > /dev/null 2>&1 &&
            pnpm run test:ci
        """],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert result.returncode == 0, f"C3 unit tests failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_catalog_validation():
    """Repo catalog usage validation passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            node -r esbuild-register tools/deployments/validate-catalog-usage.ts
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Catalog validation failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_package_deps_validation():
    """Repo package dependencies validation passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            node -r esbuild-register tools/deployments/validate-package-dependencies.ts
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Package deps validation failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_c3_lint():
    """C3 package linting passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            pnpm run build --filter='@cloudflare/workers-utils' --filter='@cloudflare/codemod' --filter='@cloudflare/mock-npm-registry' > /dev/null 2>&1 &&
            cd packages/create-cloudflare &&
            pnpm oxlint --deny-warnings --type-aware
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"C3 lint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_c3_format():
    """C3 package formatting passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            pnpm oxfmt --check packages/create-cloudflare/src
        """],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert result.returncode == 0, f"C3 format check failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_fixtures_validation():
    """Repo fixtures validation passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            node -r esbuild-register tools/deployments/validate-fixtures.ts
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Fixtures validation failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_private_packages_validation():
    """Repo private packages validation passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            node -r esbuild-register tools/deployments/validate-private-packages.ts
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Private packages validation failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_workflow_action_pinning():
    """Repo GitHub workflow action pinning validation passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            node -r esbuild-register tools/github-workflow-helpers/validate-action-pinning.ts
        """],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Workflow action pinning validation failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


def test_repo_lint():
    """Repo-wide linting passes (pass_to_pass)."""
    result = subprocess.run(
        ["bash", "-c", """
            cd /workspace/workers-sdk &&
            corepack enable &&
            pnpm install --frozen-lockfile > /dev/null 2>&1 &&
            pnpm run check:lint
        """],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"Repo lint failed:\n{result.stderr[-500:]}\n{result.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — AGENTS.md must document the bin shim
# ---------------------------------------------------------------------------

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_vite_plugin_e2e_bump_package_versions():
    """pass_to_pass | CI job 'Vite Plugin E2E' → step 'Bump package versions'"""
    r = subprocess.run(
        ["bash", "-lc", 'node .github/changeset-version.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Bump package versions' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_vite_plugin_e2e_run_vite_plugin_e2e_tests():
    """pass_to_pass | CI job 'Vite Plugin E2E' → step 'Run Vite plugin E2E tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:e2e -F @cloudflare/vite-plugin --log-order=stream'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Vite plugin E2E tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_local_explorer_ui_e2e_build_wrangler():
    """pass_to_pass | CI job 'Local Explorer UI E2E' → step 'Build wrangler'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm turbo build --filter wrangler'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build wrangler' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_local_explorer_ui_e2e_run_local_explorer_ui_e2e_tests():
    """pass_to_pass | CI job 'Local Explorer UI E2E' → step 'Run Local Explorer UI E2E tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test:e2e -F @cloudflare/local-explorer-ui --log-order=stream'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Local Explorer UI E2E tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_wrangler_e2e_run_wrangler_e2e_tests():
    """pass_to_pass | CI job 'Wrangler E2E' → step 'Run Wrangler E2E tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:e2e:wrangler'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Wrangler E2E tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_wrangler_e2e_run_getplatformproxy_remote_bindings_e2e():
    """pass_to_pass | CI job 'Wrangler E2E' → step 'Run getPlatformProxy() remote-bindings e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:e2e -F @fixture/get-platform-proxy-remote-bindings'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run getPlatformProxy() remote-bindings e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_tests_run_tests_tools_only():
    """pass_to_pass | CI job 'Tests' → step 'Run tests (tools only)'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm run test:ci --log-order=stream --filter="@cloudflare/tools"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests (tools only)' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")