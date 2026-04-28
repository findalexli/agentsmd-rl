"""Behavior tests for openai-agents-js#362.

Each f2p exercises the bug where the OpenAI Responses model's request
payload silently drops the structured-output `format` whenever the agent
also sets `providerData.text` (e.g. for `verbosity`). The p2p tests are
the existing repo unit tests that must keep passing.
"""

import os
import subprocess
from contextlib import contextmanager

REPO = "/workspace/openai-agents-js"
REGRESSION_DST = f"{REPO}/packages/agents-openai/test/regression.test.ts"
REGRESSION_FILE = "packages/agents-openai/test/regression.test.ts"

REGRESSION_CONTENT = """\
import { describe, it, expect, vi, beforeAll } from 'vitest';
import { OpenAIResponsesModel } from '../src/openaiResponsesModel';
import type OpenAI from 'openai';
import { setTracingDisabled, withTrace } from '@openai/agents-core';

const jsonSchemaOutput = {
  type: 'json_schema' as const,
  name: 'TestSchema',
  strict: true,
  schema: {
    type: 'object' as const,
    properties: {
      title: { type: 'string' },
      description: { type: 'string' },
    },
    required: ['title', 'description'],
    additionalProperties: false,
  },
};

function makeFakeClient() {
  const fakeResponse = {
    id: 'r',
    usage: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
    output: [],
  };
  const createMock = vi.fn().mockResolvedValue(fakeResponse);
  const fakeClient = {
    responses: { create: createMock },
  } as unknown as OpenAI;
  return { fakeClient, createMock };
}

describe('responses API: outputType + providerData.text.verbosity', () => {
  beforeAll(() => {
    setTracingDisabled(true);
  });

  it('preserves response format when verbosity is set alongside structured outputType', async () => {
    await withTrace('test', async () => {
      const { fakeClient, createMock } = makeFakeClient();
      const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

      const request = {
        systemInstructions: undefined,
        input: 'hello',
        modelSettings: {
          providerData: {
            text: { verbosity: 'low' },
          },
        },
        tools: [],
        outputType: jsonSchemaOutput,
        handoffs: [],
        tracing: false,
        signal: undefined,
      };

      await model.getResponse(request as any);
      expect(createMock).toHaveBeenCalledTimes(1);
      const [args] = createMock.mock.calls[0];

      expect(args.text).toBeDefined();
      expect(args.text.format).toEqual(jsonSchemaOutput);
      expect(args.text.verbosity).toBe('low');
    });
  });

  it('flows verbosity through when outputType is text', async () => {
    await withTrace('test', async () => {
      const { fakeClient, createMock } = makeFakeClient();
      const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

      const request = {
        systemInstructions: undefined,
        input: 'hello',
        modelSettings: {
          providerData: {
            text: { verbosity: 'high' },
          },
        },
        tools: [],
        outputType: 'text',
        handoffs: [],
        tracing: false,
        signal: undefined,
      };

      await model.getResponse(request as any);
      const [args] = createMock.mock.calls[0];

      expect(args.text).toBeDefined();
      expect(args.text.verbosity).toBe('high');
      expect(args.text.format).toBeUndefined();
    });
  });

  it('does not double-emit text via top-level providerData spread', async () => {
    await withTrace('test', async () => {
      const { fakeClient, createMock } = makeFakeClient();
      const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

      const request = {
        systemInstructions: undefined,
        input: 'hello',
        modelSettings: {
          providerData: {
            text: { verbosity: 'medium' },
            reasoning: { effort: 'minimal' },
          },
        },
        tools: [],
        outputType: jsonSchemaOutput,
        handoffs: [],
        tracing: false,
        signal: undefined,
      };

      await model.getResponse(request as any);
      const [args] = createMock.mock.calls[0];

      expect(args.text.format).toEqual(jsonSchemaOutput);
      expect(args.text.verbosity).toBe('medium');
      expect(args.reasoning).toEqual({ effort: 'minimal' });
    });
  });

  it('still works when modelSettings has no providerData and outputType is structured', async () => {
    await withTrace('test', async () => {
      const { fakeClient, createMock } = makeFakeClient();
      const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

      const request = {
        systemInstructions: undefined,
        input: 'hello',
        modelSettings: {},
        tools: [],
        outputType: jsonSchemaOutput,
        handoffs: [],
        tracing: false,
        signal: undefined,
      };

      await model.getResponse(request as any);
      const [args] = createMock.mock.calls[0];

      expect(args.text).toEqual({ format: jsonSchemaOutput });
    });
  });
});
"""


@contextmanager
def _regression_file():
    """Temporarily write the regression test file so vitest can find it."""
    os.makedirs(os.path.dirname(REGRESSION_DST), exist_ok=True)
    with open(REGRESSION_DST, "w") as f:
        f.write(REGRESSION_CONTENT)
    try:
        yield
    finally:
        if os.path.exists(REGRESSION_DST):
            os.remove(REGRESSION_DST)


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


def test_responses_format_preserved_with_verbosity():
    """fail_to_pass: structured outputType + providerData.text.verbosity must keep format."""
    with _regression_file():
        r = _run_vitest(
            REGRESSION_FILE,
            name_filter="preserves response format when verbosity is set",
        )
        _assert_vitest_pass(r, "regression: format preserved with verbosity")


def test_responses_text_outputtype_keeps_verbosity():
    """pass_to_pass: outputType='text' + providerData.text.verbosity flows verbosity through (sanity)."""
    with _regression_file():
        r = _run_vitest(
            REGRESSION_FILE,
            name_filter="flows verbosity through when outputType is text",
        )
        _assert_vitest_pass(r, "regression: verbosity flows when outputType is text")


def test_responses_no_double_emit_text():
    """fail_to_pass: providerData.text must not override the format slot at the top level."""
    with _regression_file():
        r = _run_vitest(
            REGRESSION_FILE,
            name_filter="does not double-emit text via top-level providerData spread",
        )
        _assert_vitest_pass(r, "regression: no top-level text override")


def test_responses_structured_no_provider_data():
    """pass_to_pass: structured outputType with no providerData still produces { format } (sanity)."""
    with _regression_file():
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


# === CI-mined tests ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'build' → step 'Run build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
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
