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

# === Execution-mined f2p tests (taskforge.exec_f2p_miner) ===
# Source: dual-pass exec at base vs gold inside the task's docker image
# Test command: pnpm --filter @lobechat/database test:client-db
# 0 fail→pass + 50 pass→pass test name(s) discovered.

def test_exec_p2p_messagemodel_query_performance_should_query_500_messages_within_50ms(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MessageModel.query performance > should query 500 messages within 50ms '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_messagemodel_query_with_messagegroup_aggregation_query_without_compression_group(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'MessageModel.query with MessageGroup aggregation > query without compression groups > should return all messages when no compression groups exist '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_topicimporterrepo_importtopic_simple_format_array_without_parentid_should_import(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'TopicImporterRepo.importTopic > simple format (array without parentId) > should import messages and build linear parentId chain '
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___agent_test_ts_81_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/agent.test.ts (81 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___aimodel_test_ts_19_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/aiModel.test.ts (19 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___aiprovider_test_ts_23_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/aiProvider.test.ts (23 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___apikey_test_ts_30_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/apiKey.test.ts (30 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___asynctask_test_ts_7_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/asyncTask.test.ts (7 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___chatgroup_test_ts_40_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/chatGroup.test.ts (40 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___chunk_test_ts_28_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/chunk.test.ts (28 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___document_test_ts_17_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/document.test.ts (17 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___drizzlemigration_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/drizzleMigration.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___embedding_test_ts_13_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/embedding.test.ts (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___file_test_ts_48_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/file.test.ts (48 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___generation_test_ts_29_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/generation.test.ts (29 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___generationbatch_test_ts_27_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/generationBatch.test.ts (27 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___generationtopic_test_ts_18_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/generationTopic.test.ts (18 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___knowledgebase_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/knowledgeBase.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_create_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.create.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_delete_test_ts_27_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.delete.test.ts (27 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_query_test_ts_60_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.query.test.ts (60 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_stats_test_ts_24_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.stats.test.ts (24 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_thread_query_test_ts_12_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.thread-query.test.ts (12 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_message_update_test_ts_46_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/message.update.test.ts (46 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_messagewithtask_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/messageWithTask.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_querywithmessagegroup_perf_test_ts_2_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/queryWithMessageGroup.perf.test.ts (2 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___messages_querywithmessagegroup_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/messages/queryWithMessageGroup.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___oauthhandoff_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/oauthHandoff.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___plugin_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/plugin.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___session_test_ts_55_tests_1_skipped(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/session.test.ts (55 tests | 1 skipped)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___sessiongroup_test_ts_8_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/sessionGroup.test.ts (8 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___thread_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/thread.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topicdocument_test_ts_26_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topicDocument.test.ts (26 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topicshare_test_ts_23_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topicShare.test.ts (23 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topics_topic_create_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topics/topic.create.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topics_topic_delete_test_ts_14_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topics/topic.delete.test.ts (14 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topics_topic_query_test_ts_46_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topics/topic.query.test.ts (46 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topics_topic_stats_test_ts_13_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topics/topic.stats.test.ts (13 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___topics_topic_update_test_ts_6_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/topics/topic.update.test.ts (6 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___user_test_ts_30_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/user.test.ts (30 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___usermemories_test_ts_52_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/userMemories.test.ts (52 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models___tests___usermemoryidentity_test_ts_9_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/__tests__/userMemoryIdentity.test.ts (9 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models_usermemory___tests___context_test_ts_16_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/userMemory/__tests__/context.test.ts (16 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models_usermemory___tests___experience_test_ts_16_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/userMemory/__tests__/experience.test.ts (16 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models_usermemory___tests___identity_test_ts_21_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/userMemory/__tests__/identity.test.ts (21 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_models_usermemory___tests___preference_test_ts_16_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/models/userMemory/__tests__/preference.test.ts (16 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_repositories_agentgroup_index_test_ts_35_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/repositories/agentGroup/index.test.ts (35 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_repositories_agentmigration___tests___agentmigrationrepo_test_ts_15_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/repositories/agentMigration/__tests__/agentMigrationRepo.test.ts (15 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_repositories_aiinfra_index_test_ts_52_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/repositories/aiInfra/index.test.ts (52 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

def test_exec_p2p_src_repositories_compression_index_test_ts_20_tests(_run_cmd=None):
    # Discovered p2p (passed at both base and gold): 'src/repositories/compression/index.test.ts (20 tests)'
    pass  # placeholder — recorded in manifest under origin: exec_diff

