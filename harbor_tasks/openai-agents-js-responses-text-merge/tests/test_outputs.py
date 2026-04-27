"""Behavior tests for openai-agents-js#362.

Each f2p exercises the bug where the OpenAI Responses model's request
payload silently drops the structured-output `format` whenever the agent
also sets `providerData.text` (e.g. for `verbosity`). The p2p tests are
the existing repo unit tests that must keep passing.
"""

import os
import subprocess

REPO = "/workspace/openai-agents-js"
REGRESSION_DST = f"{REPO}/packages/agents-openai/test/regression.test.ts"


def _stage_regression_file():
    # test.sh is responsible for materializing the regression file. Fail loud
    # if it is missing rather than silently regenerating from a stale copy.
    assert os.path.exists(
        REGRESSION_DST
    ), f"regression test fixture missing at {REGRESSION_DST}; test.sh did not stage it"


def _run_vitest(
    test_path: str, name_filter: str | None = None, timeout: int = 300
) -> subprocess.CompletedProcess:
    cmd = ["pnpm", "exec", "vitest", "run", test_path]
    if name_filter:
        cmd += ["-t", name_filter]
    return subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _assert_vitest_pass(result: subprocess.CompletedProcess, label: str):
    tail = (result.stdout or "")[-3000:] + "\n--- STDERR ---\n" + (result.stderr or "")[-1500:]
    assert result.returncode == 0, f"{label} failed (exit={result.returncode}):\n{tail}"


REGRESSION_FILE = "packages/agents-openai/test/regression.test.ts"


def test_responses_format_preserved_with_verbosity():
    """fail_to_pass: structured outputType + providerData.text.verbosity must keep format."""
    _stage_regression_file()
    r = _run_vitest(
        REGRESSION_FILE,
        name_filter="preserves response format when verbosity is set",
    )
    _assert_vitest_pass(r, "regression: format preserved with verbosity")


def test_responses_text_outputtype_keeps_verbosity():
    """pass_to_pass: outputType='text' + providerData.text.verbosity flows verbosity through (sanity)."""
    _stage_regression_file()
    r = _run_vitest(
        REGRESSION_FILE,
        name_filter="flows verbosity through when outputType is text",
    )
    _assert_vitest_pass(r, "regression: verbosity flows when outputType is text")


def test_responses_no_double_emit_text():
    """fail_to_pass: providerData.text must not override the format slot at the top level."""
    _stage_regression_file()
    r = _run_vitest(
        REGRESSION_FILE,
        name_filter="does not double-emit text via top-level providerData spread",
    )
    _assert_vitest_pass(r, "regression: no top-level text override")


def test_responses_structured_no_provider_data():
    """pass_to_pass: structured outputType with no providerData still produces { format } (sanity)."""
    _stage_regression_file()
    r = _run_vitest(
        REGRESSION_FILE,
        name_filter="still works when modelSettings has no providerData and outputType is structured",
    )
    _assert_vitest_pass(r, "regression: structured w/o providerData")


def test_existing_responses_model_tests():
    """pass_to_pass: existing OpenAIResponsesModel unit tests."""
    r = _run_vitest("packages/agents-openai/test/openaiResponsesModel.test.ts", timeout=300)
    _assert_vitest_pass(r, "p2p: openaiResponsesModel.test.ts")


def test_existing_responses_helpers_tests():
    """pass_to_pass: helpers unit tests for the same module."""
    r = _run_vitest(
        "packages/agents-openai/test/openaiResponsesModel.helpers.test.ts", timeout=300
    )
    _assert_vitest_pass(r, "p2p: openaiResponsesModel.helpers.test.ts")


def test_typecheck_agents_openai():
    """pass_to_pass: agents-openai still type-checks."""
    r = subprocess.run(
        ["pnpm", "-F", "@openai/agents-openai", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600,
    )
    tail = (r.stdout or "")[-2000:] + "\n--- STDERR ---\n" + (r.stderr or "")[-1500:]
    assert r.returncode == 0, f"build-check failed:\n{tail}"
