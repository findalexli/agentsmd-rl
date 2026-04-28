"""
Task: lobechat-swr-useactionswr-fallback-data
Repo: lobehub/lobe-chat @ 959c210e869803545d451c3019e178966188ef17
PR:   11514

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"


def test_swr_module_loads():
    """SWR module can be loaded and exports all expected hooks as functions."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # Check that expected hooks are exported
    expected_exports = [
        "export const useClientDataSWR",
        "export const useOnlyFetchOnceSWR",
        "export const useActionSWR",
    ]
    for export in expected_exports:
        assert export in content, f"Missing export: {export}"


def test_repo_swr_unit_tests():
    """Repo unit tests for SWR module pass (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx vitest run src/libs/swr/ --silent=passed-only"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"SWR unit tests failed:\n{r.stderr[-1000:]}"


def test_repo_swr_lint():
    """Repo ESLint passes on SWR module (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx eslint src/libs/swr/index.ts"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_repo_swr_prettier():
    """Repo Prettier check passes on SWR module (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c", "npm install -g pnpm && pnpm install --ignore-scripts >/dev/null 2>&1 && npx prettier --check src/libs/swr/index.ts"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


def test_use_action_swr_no_auto_fetch():
    """useActionSWR must not auto-fetch on mount and must provide initial data."""
    test_file = Path(REPO) / "src" / "libs" / "swr" / "_eval_action_swr.test.ts"
    test_code = """\
import { renderHook, act } from '@testing-library/react';
import { createElement } from 'react';
import { SWRConfig } from 'swr';
import { useActionSWR } from './index';

describe('useActionSWR behavioral', () => {
  it('should not auto-fetch on mount and should provide initial data', async () => {
    const fetcher = vi.fn().mockImplementation(() => new Promise(() => {}));
    const uniqueKey = 'eval-test-' + Date.now() + '-' + Math.random();

    // Isolate cache so no stale data interferes
    const wrapper = ({ children }: { children: React.ReactNode }) =>
      createElement(SWRConfig, { value: { provider: () => new Map() } }, children);

    const { result } = renderHook(
      () => (useActionSWR as any)(uniqueKey, fetcher),
      { wrapper }
    );

    // Allow async effects to settle
    await act(async () => {
      await new Promise(r => setTimeout(r, 200));
    });

    // data should be defined (not undefined) on mount - indicates initial/fallback data
    expect(result.current.data).toBeDefined();

    // Fetcher should NOT be called on mount - no auto-fetch
    expect(fetcher).not.toHaveBeenCalled();
  });
});
"""
    test_file.write_text(test_code)
    try:
        r = subprocess.run(
            ["npx", "vitest", "run", str(test_file), "--reporter=verbose"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        assert r.returncode == 0, (
            f"useActionSWR behavioral test failed:\n"
            f"STDOUT:\n{r.stdout[-2000:]}\n"
            f"STDERR:\n{r.stderr[-1000:]}"
        )
    finally:
        test_file.unlink(missing_ok=True)


def test_swr_comments_english_only():
    """SWR module comments are in English, not Chinese."""
    swr_file = Path(REPO) / "src" / "libs" / "swr" / "index.ts"
    content = swr_file.read_text()

    # CJK Unified Ideographs range
    chinese_chars = [c for c in content if "一" <= c <= "鿿"]
    assert len(chinese_chars) == 0, (
        f"Found {len(chinese_chars)} Chinese characters in SWR module"
    )


def test_claude_md_references_linear_mdc():
    """CLAUDE.md references .cursor/rules/linear.mdc for Linear rules."""
    claude_md = Path(REPO) / "CLAUDE.md"
    content = claude_md.read_text()

    # Should reference the external file
    assert ".cursor/rules/linear.mdc" in content, (
        "CLAUDE.md should reference .cursor/rules/linear.mdc"
    )

    # Should NOT have the full inline rules
    assert "Retrieve issue details" not in content, (
        "CLAUDE.md should not contain full inline Linear rules"
    )
    assert "Per-Issue Completion Rule" not in content, (
        "CLAUDE.md should not contain Per-Issue Completion Rule section"
    )


def test_linear_mdc_exists_with_rules():
    """File .cursor/rules/linear.mdc exists with Linear issue management rules."""
    linear_mdc = Path(REPO) / ".cursor" / "rules" / "linear.mdc"
    assert linear_mdc.exists(), ".cursor/rules/linear.mdc file must exist"

    content = linear_mdc.read_text()

    # Check for distinctive Linear rules content
    assert "alwaysApply: true" in content, (
        "linear.mdc should have alwaysApply frontmatter"
    )
    assert "Linear Issue Management" in content, (
        "linear.mdc should have Linear Issue Management heading"
    )
    assert "Completion Comment" in content, (
        "linear.mdc should have Completion Comment section"
    )
    assert "Per-Issue Completion Rule" in content, (
        "linear.mdc should have Per-Issue Completion Rule"
    )
    assert "In Review" in content, (
        "linear.mdc should mention In Review status"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_database_lint():
    """pass_to_pass | CI job 'Test Database' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_test_client_db():
    """pass_to_pass | CI job 'Test Database' → step 'Test Client DB'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:client-db'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Client DB' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_database_test_coverage():
    """pass_to_pass | CI job 'Test Database' → step 'Test Coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @lobechat/database test:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_packages_test_packages_with_coverage():
    """pass_to_pass | CI job 'Test Packages' → step 'Test packages with coverage'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run --filter $package test:coverage'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test packages with coverage' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_desktop_app_typecheck_desktop():
    """pass_to_pass | CI job 'Test Desktop App' → step 'Typecheck Desktop'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm type-check'], cwd=os.path.join(REPO, 'apps/desktop'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck Desktop' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_desktop_app_test_desktop_client():
    """pass_to_pass | CI job 'Test Desktop App' → step 'Test Desktop Client'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=os.path.join(REPO, 'apps/desktop'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Test Desktop Client' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_desktop_next_bundle_build_desktop_next_js_bundle():
    """pass_to_pass | CI job 'Build desktop Next bundle' → step 'Build desktop Next.js bundle'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run desktop:build-electron'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build desktop Next.js bundle' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")