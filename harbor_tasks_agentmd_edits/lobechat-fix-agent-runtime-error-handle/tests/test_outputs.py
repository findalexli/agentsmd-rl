"""
Task: lobechat-fix-agent-runtime-error-handle
Repo: lobehub/lobe-chat @ 6e2613597800616e3d101e383eca88d46c791588
PR:   12834

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/lobe-chat")


def _run_bun(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp .ts file and run it with bun from the repo root."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_filestore_get_falls_back_to_partials():
    """FileSnapshotStore.get() must fall back to partial snapshots when no completed snapshot exists."""
    result = _run_bun(
        textwrap.dedent("""\
        import { FileSnapshotStore } from './packages/agent-tracing/src/store/file-store';
        import * as fs from 'node:fs/promises';
        import * as path from 'node:path';
        import * as os from 'node:os';

        async function main() {
            const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'tracing-test-'));
            const partialDir = path.join(tmpDir, '.agent-tracing', '_partial');
            await fs.mkdir(partialDir, { recursive: true });

            // Create a partial snapshot (no completed snapshots exist)
            const partialData = {
                traceId: 'trace-abc123def456',
                operationId: 'op-test-123',
                model: 'gpt-4',
                provider: 'openai',
                startedAt: Date.now(),
                steps: [],
                totalTokens: 100,
                totalCost: 0.005,
            };
            await fs.writeFile(
                path.join(partialDir, 'op-test-123.json'),
                JSON.stringify(partialData)
            );

            // Use constructor with rootDir to point to our temp dir
            const store = new FileSnapshotStore(tmpDir);

            // get() with the operationId should fall back to the partial
            const snapshot = await store.get('op-test-123');
            if (snapshot === null) {
                console.log(JSON.stringify({ error: 'Expected fallback to partial, got null' }));
                process.exit(1);
            }

            console.log(JSON.stringify({
                success: true,
                traceId: snapshot.traceId,
                operationId: snapshot.operationId,
                model: snapshot.model,
            }));

            await fs.rm(tmpDir, { recursive: true });
        }
        main().catch(e => {
            console.log(JSON.stringify({ error: e.message }));
            process.exit(1);
        });
    """)
    )
    assert result.returncode == 0, f"Bun script failed: {result.stderr}\nstdout: {result.stdout}"
    data = json.loads(result.stdout.strip())
    assert data.get("success") is True, f"Test failed: {data}"
    assert data["operationId"] == "op-test-123", f"Wrong operationId: {data['operationId']}"
    assert data["traceId"] == "trace-abc123def456", f"Wrong traceId: {data['traceId']}"


def test_filestore_partial_to_snapshot_fills_defaults():
    """partialToSnapshot must fill in default values for missing fields in partial snapshots."""
    result = _run_bun(
        textwrap.dedent("""\
        import { FileSnapshotStore } from './packages/agent-tracing/src/store/file-store';
        import * as fs from 'node:fs/promises';
        import * as path from 'node:path';
        import * as os from 'node:os';

        async function main() {
            const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'tracing-test2-'));
            const partialDir = path.join(tmpDir, '.agent-tracing', '_partial');
            await fs.mkdir(partialDir, { recursive: true });

            // Minimal partial with only identifying fields
            const partialData = {
                traceId: 'trace-minimal-001',
                operationId: 'op-minimal',
            };
            await fs.writeFile(
                path.join(partialDir, 'op-minimal.json'),
                JSON.stringify(partialData)
            );

            const store = new FileSnapshotStore(tmpDir);
            const snapshot = await store.get('op-minimal');
            if (snapshot === null) {
                console.log(JSON.stringify({ error: 'Expected fallback to partial, got null' }));
                process.exit(1);
            }

            // Verify defaults are filled in by partialToSnapshot
            const errors = [];
            if (snapshot.totalSteps !== 0) errors.push(`totalSteps=${snapshot.totalSteps}, expected 0`);
            if (snapshot.totalTokens !== 0) errors.push(`totalTokens=${snapshot.totalTokens}, expected 0`);
            if (snapshot.totalCost !== 0) errors.push(`totalCost=${snapshot.totalCost}, expected 0`);
            if (snapshot.completedAt !== undefined) errors.push('completedAt should be undefined');
            if (snapshot.completionReason !== undefined) errors.push('completionReason should be undefined');
            if (snapshot.error !== undefined) errors.push('error should be undefined');
            if (snapshot.steps.length !== 0) errors.push('steps should be empty array');

            if (errors.length > 0) {
                console.log(JSON.stringify({ error: errors.join('; ') }));
                process.exit(1);
            }

            console.log(JSON.stringify({ success: true, totalSteps: snapshot.totalSteps }));
            await fs.rm(tmpDir, { recursive: true });
        }
        main().catch(e => {
            console.log(JSON.stringify({ error: e.message }));
            process.exit(1);
        });
    """)
    )
    assert result.returncode == 0, f"Bun script failed: {result.stderr}\nstdout: {result.stdout}"
    data = json.loads(result.stdout.strip())
    assert data.get("success") is True, f"Test failed: {data}"


def test_error_handler_resilient_to_redis_failure():
    """executeStep catch block must wrap each infrastructure call in try-catch."""
    service_file = (
        REPO / "src" / "server" / "services" / "agentRuntime" / "AgentRuntimeService.ts"
    )
    content = service_file.read_text()

    # The error handler must catch failures from each infrastructure operation
    # so that onComplete and webhooks still fire even when Redis is down
    assert "catch (publishError" in content, (
        "Error handler must catch publishStreamEvent failures independently"
    )
    assert "catch (loadError" in content, (
        "Error handler must catch loadAgentState failures independently"
    )
    assert "catch (saveError" in content, (
        "Error handler must catch saveAgentState failures independently"
    )
    assert "catch (webhookError" in content, (
        "Error handler must catch triggerCompletionWebhook failures independently"
    )
    # Must have a fallback error state when loadAgentState fails
    assert "finalStateWithError" in content, "Error handler must build finalStateWithError"
    # The variable must be declared with 'let' (not const) since it's assigned in a try-catch
    assert "let finalStateWithError" in content, (
        "finalStateWithError must be declared with let for fallback assignment"
    )


# ---------------------------------------------------------------------------
# Config/documentation update test
# ---------------------------------------------------------------------------


def test_skill_md_documents_inspect_for_partials():
    """Agent tracing SKILL.md must document using inspect command for partial snapshots."""
    skill_md = REPO / ".agents" / "skills" / "agent-tracing" / "SKILL.md"
    content = skill_md.read_text()

    # Must mention using inspect with partial IDs
    assert "partialOperationId" in content, (
        "SKILL.md should document using inspect command with partial operation IDs"
    )

    # Must NOT have standalone "agent-tracing partial inspect" commands
    lines = content.splitlines()
    standalone_partial_inspect = [
        line.strip()
        for line in lines
        if "agent-tracing partial inspect" in line
        and "agent-tracing inspect" not in line.replace("partial inspect", "").strip()
    ]
    assert len(standalone_partial_inspect) == 0, (
        f"SKILL.md should not have standalone 'agent-tracing partial inspect' commands. "
        f"Found: {standalone_partial_inspect}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + anti-stub
# ---------------------------------------------------------------------------


def test_filestore_completed_snapshot_takes_priority():
    """FileSnapshotStore.get() must prefer completed snapshots over partials."""
    result = _run_bun(
        textwrap.dedent("""\
        import { FileSnapshotStore } from './packages/agent-tracing/src/store/file-store';
        import * as fs from 'node:fs/promises';
        import * as path from 'node:path';
        import * as os from 'node:os';

        async function main() {
            const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'tracing-test3-'));
            const tracingDir = path.join(tmpDir, '.agent-tracing');
            const partialDir = path.join(tracingDir, '_partial');
            await fs.mkdir(partialDir, { recursive: true });

            // Create a completed snapshot
            const completedSnapshot = {
                traceId: 'trace-priority-test',
                operationId: 'op-completed',
                model: 'claude-3',
                provider: 'anthropic',
                startedAt: Date.now() - 1000,
                completedAt: Date.now(),
                completionReason: 'done',
                steps: [{ stepIndex: 0, stepType: 'call_llm', executionTimeMs: 500, startedAt: Date.now() - 1000, completedAt: Date.now(), totalCost: 0.01, totalTokens: 50 }],
                totalTokens: 50,
                totalCost: 0.01,
                totalSteps: 1,
            };
            const filename = `2026-01-01T00-00-00.000Z_trace-prior.json`;
            await fs.writeFile(
                path.join(tracingDir, filename),
                JSON.stringify(completedSnapshot)
            );

            // Also create a partial with the same trace ID prefix
            const partialData = {
                traceId: 'trace-priority-test',
                operationId: 'op-partial',
                model: 'gpt-3.5',
            };
            await fs.writeFile(
                path.join(partialDir, 'op-partial.json'),
                JSON.stringify(partialData)
            );

            const store = new FileSnapshotStore(tmpDir);

            // get() should find the completed snapshot first, not the partial
            const snapshot = await store.get('trace-priority-test');
            if (snapshot === null) {
                console.log(JSON.stringify({ error: 'Expected snapshot, got null' }));
                process.exit(1);
            }

            if (snapshot.operationId !== 'op-completed') {
                console.log(JSON.stringify({ error: `Got partial instead of completed: opId=${snapshot.operationId}` }));
                process.exit(1);
            }
            if (snapshot.completionReason !== 'done') {
                console.log(JSON.stringify({ error: 'Should have completionReason=done from completed snapshot' }));
                process.exit(1);
            }

            console.log(JSON.stringify({ success: true, operationId: snapshot.operationId }));
            await fs.rm(tmpDir, { recursive: true });
        }
        main().catch(e => {
            console.log(JSON.stringify({ error: e.message }));
            process.exit(1);
        });
    """)
    )
    assert result.returncode == 0, f"Bun script failed: {result.stderr}\nstdout: {result.stdout}"
    data = json.loads(result.stdout.strip())
    assert data.get("success") is True, f"Test failed: {data}"
    assert data["operationId"] == "op-completed"


def test_typescript_syntax_valid():
    """Modified TypeScript files must parse without obvious syntax errors."""
    ts_files = [
        REPO / "packages" / "agent-tracing" / "src" / "store" / "file-store.ts",
        REPO / "packages" / "agent-tracing" / "src" / "cli" / "partial.ts",
    ]
    for f in ts_files:
        assert f.exists(), f"File not found: {f}"
        content = f.read_text()
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert abs(open_braces - close_braces) <= 1, (
            f"Unbalanced braces in {f.name}: {open_braces} open, {close_braces} close"
        )
