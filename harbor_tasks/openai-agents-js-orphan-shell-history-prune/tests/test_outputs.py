"""Oracle tests for openai/openai-agents-js#1102.

The fix moves orphan-tool-call pruning out of `prepareModelInputItems` and
into a shared helper (`getContinuationOutputItems`) that is also used by
`getTurnInput`. As a result, `RunResult.history` and `RunState.history` no
longer leak orphan hosted-shell calls into continuation inputs.

We exercise the runtime behavior with a self-contained Vitest oracle file
that we drop into the agents-core package's test directory at run time, then
run vitest against it. We also include pass-to-pass checks for the
pre-existing test file and a TypeScript build-check.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-core"
ORACLE_NAME = "__oracle_orphan_shell__.test.ts"
ORACLE_PATH = PKG / "test" / ORACLE_NAME

ORACLE_TS = r"""
import { beforeAll, describe, it, expect } from 'vitest';
import { Agent } from '../src/agent';
import { RunToolCallItem } from '../src/items';
import { RunState } from '../src/runState';
import { RunContext } from '../src/runContext';
import { Runner, getTurnInput } from '../src/run';
import { shellTool } from '../src/tool';
import * as protocol from '../src/types/protocol';
import { Usage } from '../src/usage';
import {
  setDefaultModelProvider,
  setTracingDisabled,
} from '../src';
import { FakeModelProvider, fakeModelMessage } from './stubs';
import type {
  AgentInputItem,
  Model,
  ModelRequest,
  ModelResponse,
} from '../src';

// eslint-disable-next-line @typescript-eslint/no-empty-object-type
interface TurnResponse extends ModelResponse {}

class TrackingModel implements Model {
  public requests: ModelRequest[] = [];
  constructor(private readonly responses: TurnResponse[]) {}
  async getResponse(request: ModelRequest): Promise<ModelResponse> {
    const clonedInput: string | AgentInputItem[] =
      typeof request.input === 'string'
        ? request.input
        : (JSON.parse(JSON.stringify(request.input)) as AgentInputItem[]);
    this.requests.push({ ...request, input: clonedInput });
    const response = this.responses.shift();
    if (!response) {
      throw new Error('No response configured');
    }
    return response;
  }
  getStreamedResponse(_request: ModelRequest): AsyncIterable<protocol.StreamEvent> {
    throw new Error('Not implemented');
  }
}

const buildResponse = (
  items: protocol.ModelItem[],
  responseId?: string,
): ModelResponse => ({
  output: JSON.parse(JSON.stringify(items)) as protocol.ModelItem[],
  usage: new Usage(),
  responseId,
});

function getRequestInputItems(request: ModelRequest): AgentInputItem[] {
  return Array.isArray(request.input) ? request.input : [];
}

describe('orphan_shell_pruning', () => {
  beforeAll(() => {
    setTracingDisabled(true);
    setDefaultModelProvider(new FakeModelProvider());
  });

  it('getTurnInput_drops_orphan_shell', () => {
    const agent = new Agent({ name: 'A' });
    const orphanShellCall = new RunToolCallItem(
      {
        type: 'shell_call',
        callId: 'shell_orphan_unit',
        status: 'completed',
        action: { commands: ['echo hi'] },
      } satisfies protocol.ShellCallItem,
      agent,
    );

    const result = getTurnInput('hello', [orphanShellCall]);
    expect(result).toEqual([
      { type: 'message', role: 'user', content: 'hello' },
    ]);
    expect(result.some((item) => item.type === 'shell_call')).toBe(false);
  });

  it('runState_history_drops_orphan_shell', () => {
    const context = new RunContext();
    const agent = new Agent({ name: 'HistAgentShellOrphan' });
    const state = new RunState(context, 'input', agent, 1);
    state._generatedItems.push(
      new RunToolCallItem(
        {
          type: 'shell_call',
          callId: 'shell_orphan_state',
          status: 'completed',
          action: { commands: ['echo hi'] },
        },
        agent,
      ),
    );

    expect(state.history).toEqual([
      { type: 'message', role: 'user', content: 'input' },
    ]);
    expect(state.history.some((item) => item.type === 'shell_call')).toBe(false);
  });

  it('continuation_does_not_reintroduce_orphan_shell', async () => {
    const hostedShell = shellTool({ environment: { type: 'container_auto' } });
    const model = new TrackingModel([
      buildResponse(
        [
          {
            type: 'shell_call',
            callId: 'call-shell-1',
            status: 'completed',
            action: { commands: ['echo hi'] },
          } satisfies protocol.ShellCallItem,
        ],
        'resp-shell-1',
      ),
      buildResponse([fakeModelMessage('done')], 'resp-shell-2'),
      buildResponse([fakeModelMessage('continued from result')], 'resp-shell-3'),
      buildResponse([fakeModelMessage('continued from state')], 'resp-shell-4'),
    ]);

    const agent = new Agent({
      name: 'HostedShellAgent',
      model,
      tools: [hostedShell],
    });
    const runner = new Runner();
    const firstResult = await runner.run(agent, 'user_message');

    expect(firstResult.history.some((item) => item.type === 'shell_call')).toBe(false);
    expect(
      firstResult.state.history.some((item) => item.type === 'shell_call'),
    ).toBe(false);

    await runner.run(agent, firstResult.history);
    await runner.run(agent, firstResult.state.history);

    expect(model.requests).toHaveLength(4);
    const continuedFromResult = getRequestInputItems(model.requests[2]);
    const continuedFromState = getRequestInputItems(model.requests[3]);

    expect(continuedFromResult.some((item) => item.type === 'shell_call')).toBe(false);
    expect(continuedFromState.some((item) => item.type === 'shell_call')).toBe(false);
    expect(continuedFromResult).toEqual(firstResult.history);
    expect(continuedFromState).toEqual(firstResult.state.history);
  });
});
""".lstrip()


def _write_oracle() -> None:
    ORACLE_PATH.write_text(ORACLE_TS)


def _cleanup_oracle() -> None:
    ORACLE_PATH.unlink(missing_ok=True)


def _run_vitest(test_filter: str, test_path: str = f"test/{ORACLE_NAME}") -> subprocess.CompletedProcess:
    """Run vitest against a single file, optionally filtering by test name."""
    return subprocess.run(
        [
            "pnpm",
            "-F",
            "@openai/agents-core",
            "exec",
            "vitest",
            "run",
            test_path,
            "-t",
            test_filter,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )


def _assert_passed(r: subprocess.CompletedProcess, expected_test_name: str) -> None:
    """Assert vitest succeeded — vitest's exit code is the sole signal."""
    assert r.returncode == 0, (
        f"vitest exited with {r.returncode} for filter '{expected_test_name}'.\n"
        f"---stdout---\n{r.stdout[-2000:]}\n---stderr---\n{r.stderr[-2000:]}"
    )


# ────────────────────── Fail-to-pass (oracle) tests ──────────────────────


def test_get_turn_input_drops_orphan_shell_call():
    """f2p: getTurnInput must drop orphan hosted shell calls from generated items."""
    _write_oracle()
    try:
        r = _run_vitest("getTurnInput_drops_orphan_shell")
        _assert_passed(r, "getTurnInput_drops_orphan_shell")
    finally:
        _cleanup_oracle()


def test_run_state_history_drops_orphan_shell_call():
    """f2p: RunState.history must filter out orphan hosted shell calls."""
    _write_oracle()
    try:
        r = _run_vitest("runState_history_drops_orphan_shell")
        _assert_passed(r, "runState_history_drops_orphan_shell")
    finally:
        _cleanup_oracle()


def test_continuation_does_not_reintroduce_orphan_shell_call():
    """f2p: continuing a run from result.history / state.history must not
    re-send orphan hosted shell calls to the model."""
    _write_oracle()
    try:
        r = _run_vitest("continuation_does_not_reintroduce_orphan_shell")
        _assert_passed(r, "continuation_does_not_reintroduce_orphan_shell")
    finally:
        _cleanup_oracle()


# ───────────────────────── Pass-to-pass (regression) ──────────────────────


def test_existing_run_utils_tests_pass():
    """p2p: pre-existing getTurnInput unit tests still pass after the fix."""
    r = subprocess.run(
        [
            "pnpm",
            "-F",
            "@openai/agents-core",
            "exec",
            "vitest",
            "run",
            "test/run.utils.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"existing run.utils.test.ts failed with code {r.returncode}:\n"
        f"---stdout---\n{r.stdout[-2000:]}\n---stderr---\n{r.stderr[-2000:]}"
    )


def test_existing_run_state_tests_pass():
    """p2p: pre-existing RunState tests still pass after the fix."""
    r = subprocess.run(
        [
            "pnpm",
            "-F",
            "@openai/agents-core",
            "exec",
            "vitest",
            "run",
            "test/runState.test.ts",
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"existing runState.test.ts failed with code {r.returncode}:\n"
        f"---stdout---\n{r.stdout[-2000:]}\n---stderr---\n{r.stderr[-2000:]}"
    )


def test_agents_core_typecheck():
    """p2p: agents-core build-check (tsc --noEmit) must pass — the AGENTS.md
    verification stack requires `pnpm -r build-check`."""
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-core", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert r.returncode == 0, (
        f"build-check failed with code {r.returncode}:\n"
        f"---stdout---\n{r.stdout[-3000:]}\n---stderr---\n{r.stderr[-2000:]}"
    )


def test_agents_core_lint_clean():
    """p2p: AGENTS.md mandates `pnpm lint` for code changes. Run on the
    items.ts file we touched plus the package directory to keep this fast."""
    r = subprocess.run(
        ["pnpm", "lint", "packages/agents-core/src/runner/items.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"eslint failed with code {r.returncode}:\n"
        f"---stdout---\n{r.stdout[-3000:]}\n---stderr---\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build:ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")