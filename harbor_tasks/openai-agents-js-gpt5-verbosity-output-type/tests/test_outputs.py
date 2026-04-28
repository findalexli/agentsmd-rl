import subprocess
import os
import textwrap

REPO = "/workspace/openai-agents-js"


def _write_and_run_vitest(test_code, test_id):
    """Write a vitest test file, run it, clean up, return subprocess result."""
    test_file = os.path.join(
        REPO, f"packages/agents-openai/test/scaffold_{test_id}.test.ts"
    )
    try:
        with open(test_file, "w") as f:
            f.write(test_code)
        return subprocess.run(
            [
                "npx",
                "vitest",
                "run",
                f"packages/agents-openai/test/scaffold_{test_id}.test.ts",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_response_format_verbosity():
    """getResponseFormat passes verbosity through and does not leak text to top level."""
    test_code = textwrap.dedent(
        """\
    import { describe, it, expect, vi, beforeAll } from 'vitest';
    import { OpenAIResponsesModel } from '../src/openaiResponsesModel';
    import { setTracingDisabled, withTrace } from '@openai/agents-core';
    import type OpenAI from 'openai';

    describe('getResponseFormat verbosity and outputType', () => {
      beforeAll(() => {
        setTracingDisabled(true);
      });

      it('passes text verbosity through when outputType is "text"', async () => {
        await withTrace('test', async () => {
          const fakeResponse = {
            id: 'res1',
            usage: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
            output: [{ id: 'm1', type: 'message', status: 'completed', content: [{ type: 'output_text', text: 'hi' }], role: 'assistant' }],
          };
          const createMock = vi.fn().mockResolvedValue(fakeResponse);
          const fakeClient = { responses: { create: createMock } } as unknown as OpenAI;
          const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

          await model.getResponse({
            systemInstructions: 'inst',
            input: 'hello',
            modelSettings: {
              providerData: {
                text: { verbosity: 'low' },
                reasoning_effort: 'minimal',
              },
            },
            tools: [],
            outputType: 'text',
            handoffs: [],
            tracing: false,
            signal: undefined,
          } as any);

          const [args] = createMock.mock.calls[0];
          expect(args.text).toBeDefined();
          expect(args.text).toEqual({ verbosity: 'low' });
        });
      });

      it('merges verbosity with structured output format', async () => {
        await withTrace('test', async () => {
          const fakeResponse = {
            id: 'res2',
            usage: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
            output: [{ id: 'm2', type: 'message', status: 'completed', content: [{ type: 'output_text', text: 'ok' }], role: 'assistant' }],
          };
          const createMock = vi.fn().mockResolvedValue(fakeResponse);
          const fakeClient = { responses: { create: createMock } } as unknown as OpenAI;
          const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

          const outputType = {
            type: 'json_schema',
            json_schema: { name: 'test', schema: { type: 'object', properties: {} } },
          };

          await model.getResponse({
            systemInstructions: 'inst',
            input: 'test',
            modelSettings: {
              providerData: {
                text: { verbosity: 'low' },
              },
            },
            tools: [],
            outputType,
            handoffs: [],
            tracing: false,
            signal: undefined,
          } as any);

          const [args] = createMock.mock.calls[0];
          expect(args.text).toBeDefined();
          expect(args.text.format).toEqual(outputType);
          expect(args.text.verbosity).toBe('low');
        });
      });

      it('does not spread text key to top level of request body', async () => {
        await withTrace('test', async () => {
          const fakeResponse = {
            id: 'res3',
            usage: { input_tokens: 1, output_tokens: 1, total_tokens: 2 },
            output: [{ id: 'm3', type: 'message', status: 'completed', content: [{ type: 'output_text', text: 'ok' }], role: 'assistant' }],
          };
          const createMock = vi.fn().mockResolvedValue(fakeResponse);
          const fakeClient = { responses: { create: createMock } } as unknown as OpenAI;
          const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

          await model.getResponse({
            systemInstructions: 'inst',
            input: 'test',
            modelSettings: {
              providerData: {
                text: { verbosity: 'low' },
                reasoning_effort: 'minimal',
              },
            },
            tools: [],
            outputType: 'text',
            handoffs: [],
            tracing: false,
            signal: undefined,
          } as any);

          const [args] = createMock.mock.calls[0];
          expect(args.text).toEqual({ verbosity: 'low' });
          expect((args as any).reasoning_effort).toBe('minimal');
        });
      });
    });
    """
    )

    r = _write_and_run_vitest(test_code, "response_format_verbosity")
    assert r.returncode == 0, (
        f"vitest tests failed (returncode={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_response_format_verbosity_nested_schema():
    """getResponseFormat merges verbosity with a nested json_schema output format."""
    test_code = textwrap.dedent(
        """\
    import { describe, it, expect, vi, beforeAll } from 'vitest';
    import { OpenAIResponsesModel } from '../src/openaiResponsesModel';
    import { setTracingDisabled, withTrace } from '@openai/agents-core';
    import type OpenAI from 'openai';

    describe('getResponseFormat nested schema with verbosity', () => {
      beforeAll(() => {
        setTracingDisabled(true);
      });

      it('merges verbosity with nested json_schema output format', async () => {
        await withTrace('test', async () => {
          const fakeResponse = {
            id: 'res_nested',
            usage: { input_tokens: 2, output_tokens: 3, total_tokens: 5 },
            output: [{ id: 'm_nested', type: 'message', status: 'completed', content: [{ type: 'output_text', text: 'result' }], role: 'assistant' }],
          };
          const createMock = vi.fn().mockResolvedValue(fakeResponse);
          const fakeClient = { responses: { create: createMock } } as unknown as OpenAI;
          const model = new OpenAIResponsesModel(fakeClient, 'gpt-5');

          const outputType = {
            type: 'json_schema',
            json_schema: {
              name: 'weather_report',
              schema: {
                type: 'object',
                properties: {
                  city: { type: 'string' },
                  temperature: { type: 'number' },
                  conditions: { type: 'string' },
                },
                required: ['city', 'temperature'],
              },
            },
          };

          await model.getResponse({
            systemInstructions: 'You are a weather assistant.',
            input: 'What is the weather in Seattle?',
            modelSettings: {
              providerData: {
                text: { verbosity: 'high' },
                reasoning_effort: 'medium',
              },
            },
            tools: [],
            outputType,
            handoffs: [],
            tracing: false,
            signal: undefined,
          } as any);

          const [args] = createMock.mock.calls[0];
          expect(args.text).toBeDefined();
          expect(args.text.format).toEqual(outputType);
          expect(args.text.verbosity).toBe('high');
          expect((args as any).reasoning_effort).toBe('medium');
        });
      });
    });
    """
    )

    r = _write_and_run_vitest(test_code, "nested_schema_verbosity")
    assert r.returncode == 0, (
        f"vitest tests failed (returncode={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-2000:]}"
    )


def test_build_check():
    """TypeScript build check passes for the agents-openai package."""
    r = subprocess.run(
        ["pnpm", "-F", "agents-openai", "build-check"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"build-check failed (returncode={r.returncode}):\n"
        f"STDOUT:\n{r.stdout[-1000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
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