"""Verification tests for openai/openai-agents-js#1124.

Approach: append two new `it(...)` blocks to the upstream
`run.stream.test.ts`. Each new block reproduces the streamed
output-guardrail scenario but asserts a *single* invariant, so the f2p
checks fail independently if the agent fixes one symptom but not the
other.

f2p (fail at base, pass after the runtime fix):
  - test_currentStep_cleared_after_streamed_output_guardrail:
    `result.state._currentStep?.type` is no longer
    `'next_step_final_output'`.
  - test_finaloutput_undefined_after_streamed_output_guardrail:
    `result.finalOutput` is `undefined` and reading it logs the standard
    warning.

p2p (pass on both base and post-fix):
  - test_repo_typecheck_agents_core: `pnpm -F @openai/agents-core run
    build-check`.
  - test_existing_input_guardrail_stream_test: sibling streaming test
    exercising the input-guardrail path is unaffected.
"""

from __future__ import annotations

import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path("/workspace/openai-agents-js")
AGENTS_CORE = REPO / "packages" / "agents-core"
TEST_FILE = AGENTS_CORE / "test" / "run.stream.test.ts"

# We splice two new `it(...)` blocks into the existing `describe` that the
# scenario lives in. These are independent of any pre-existing assertions
# in the file, so each can fail independently.
NEW_IT_CURRENTSTEP_NAME = (
    "scaffold-1124: hides _currentStep after output guardrail trips"
)
NEW_IT_FINALOUTPUT_NAME = (
    "scaffold-1124: hides finalOutput after output guardrail trips"
)

NEW_IT_BLOCKS = textwrap.dedent("""\

      it('scaffold-1124: hides _currentStep after output guardrail trips', async () => {
        vi
          .spyOn(sessionPersistence, 'saveStreamInputToSession')
          .mockResolvedValue();
        vi
          .spyOn(sessionPersistence, 'saveStreamResultToSession')
          .mockResolvedValue();

        const guardrail = {
          name: 'output-block',
          execute: vi.fn().mockResolvedValue({
            tripwireTriggered: true,
            outputInfo: { reason: 'pii' },
          }),
        };

        const session = createSessionMock();
        const agent = new Agent({
          name: 'StreamOutputGuardrailHideStep',
          model: new ImmediateStreamingModel({
            output: [fakeModelMessage('PII: 123-456-7890')],
            usage: new Usage(),
          }),
          outputGuardrails: [guardrail],
        });

        const result = await run(agent, 'filter me', { stream: true, session });

        await expect(result.completed).rejects.toBeInstanceOf(
          OutputGuardrailTripwireTriggered,
        );

        expect(result.state._currentStep?.type).not.toBe('next_step_final_output');
      });

      it('scaffold-1124: hides finalOutput after output guardrail trips', async () => {
        vi
          .spyOn(sessionPersistence, 'saveStreamInputToSession')
          .mockResolvedValue();
        vi
          .spyOn(sessionPersistence, 'saveStreamResultToSession')
          .mockResolvedValue();

        const guardrail = {
          name: 'output-block',
          execute: vi.fn().mockResolvedValue({
            tripwireTriggered: true,
            outputInfo: { reason: 'pii' },
          }),
        };

        const session = createSessionMock();
        const agent = new Agent({
          name: 'StreamOutputGuardrailHideOutput',
          model: new ImmediateStreamingModel({
            output: [fakeModelMessage('PII: 123-456-7890')],
            usage: new Usage(),
          }),
          outputGuardrails: [guardrail],
        });

        const result = await run(agent, 'filter me', { stream: true, session });
        const warnSpy = vi.spyOn(logger, 'warn').mockImplementation(() => {});

        await expect(result.completed).rejects.toBeInstanceOf(
          OutputGuardrailTripwireTriggered,
        );

        expect(result.finalOutput).toBeUndefined();
        expect(warnSpy).toHaveBeenCalledWith(
          'Accessed finalOutput before agent run is completed.',
        );
      });
""")

# Distinctive, non-flaky anchors. The first appears exactly once: it's the
# closing `});` of the "output guardrail trips" `it(...)` followed by the
# "does not persist streaming result when the consumer cancels early" `it`.
ANCHOR = (
    "    expect(saveInputSpy).toHaveBeenCalledTimes(1);\n"
    "    expect(saveResultSpy).not.toHaveBeenCalled();\n"
    "    expect(guardrail.execute).toHaveBeenCalledTimes(1);\n"
    "  });\n\n"
    "  it('does not persist streaming result when the consumer cancels early',"
)

PATCH_MARKER = "scaffold-1124: hides _currentStep after output guardrail trips"


def _run(cmd, *, cwd=REPO, timeout=600):
    env = os.environ.copy()
    env.setdefault("CI", "1")
    env.setdefault("NODE_ENV", "test")
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )


def _vitest(test_name_filter: str):
    return _run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--project",
            "@openai/agents-core",
            "test/run.stream.test.ts",
            "-t",
            test_name_filter,
        ],
        timeout=600,
    )


@pytest.fixture(scope="session", autouse=True)
def patch_upstream_test_file():
    """Splice two new `it()` blocks into the upstream stream test once per
    session, then restore the original on teardown."""
    original = TEST_FILE.read_text(encoding="utf-8")

    if PATCH_MARKER not in original:
        if ANCHOR not in original:
            pytest.fail(
                f"Upstream anchor missing in {TEST_FILE}; the test file's "
                "shape changed and the verifier needs updating."
            )
        replacement = (
            "    expect(saveInputSpy).toHaveBeenCalledTimes(1);\n"
            "    expect(saveResultSpy).not.toHaveBeenCalled();\n"
            "    expect(guardrail.execute).toHaveBeenCalledTimes(1);\n"
            "  });\n"
            + NEW_IT_BLOCKS
            + "\n  it('does not persist streaming result when the consumer cancels early',"
        )
        patched = original.replace(ANCHOR, replacement, 1)
        TEST_FILE.write_text(patched, encoding="utf-8")

    yield

    TEST_FILE.write_text(original, encoding="utf-8")


# --------------------------------------------------------------------------
# Fail-to-pass
# --------------------------------------------------------------------------

def test_currentStep_cleared_after_streamed_output_guardrail():
    """fail_to_pass: after an output guardrail trips during a streamed run,
    `result.state._currentStep?.type` must not still be
    `'next_step_final_output'`. Otherwise the runtime keeps reporting that
    the streamed run reached its final-output step despite the guardrail
    rejection."""
    r = _vitest(NEW_IT_CURRENTSTEP_NAME)
    combined = (r.stdout + "\n" + r.stderr)[-3000:]
    assert r.returncode == 0, (
        "_currentStep was still 'next_step_final_output' after the streamed "
        f"output guardrail tripped.\n{combined}"
    )


def test_finaloutput_undefined_after_streamed_output_guardrail():
    """fail_to_pass: `result.finalOutput` must be `undefined` after a
    streamed output guardrail trips, and reading it must log the standard
    'Accessed finalOutput before agent run is completed.' warning."""
    r = _vitest(NEW_IT_FINALOUTPUT_NAME)
    combined = (r.stdout + "\n" + r.stderr)[-3000:]
    assert r.returncode == 0, (
        "finalOutput was still readable (or no warning was logged) after "
        f"the streamed output guardrail tripped.\n{combined}"
    )


# --------------------------------------------------------------------------
# Pass-to-pass
# --------------------------------------------------------------------------

def test_repo_typecheck_agents_core():
    """pass_to_pass: `pnpm -F @openai/agents-core run build-check` (tsc
    --noEmit on tsconfig.test.json) still passes after the agent's edit."""
    r = _run(
        ["pnpm", "-F", "@openai/agents-core", "run", "build-check"],
        timeout=600,
    )
    combined = (r.stdout + "\n" + r.stderr)[-2000:]
    assert r.returncode == 0, f"build-check failed:\n{combined}"


def test_existing_input_guardrail_stream_test():
    """pass_to_pass: the streaming input-guardrail test still passes; the
    fix to the output-guardrail path must not perturb input-guardrail
    handling."""
    r = _vitest("skips persisting streaming input when an input guardrail triggers")
    combined = (r.stdout + "\n" + r.stderr)[-2000:]
    assert r.returncode == 0, (
        "Streaming input-guardrail regression: input guardrail handling "
        f"was disturbed.\n{combined}"
    )
