#!/usr/bin/env bash
set -uo pipefail

mkdir -p /logs/verifier

REGRESSION_DST=/workspace/openai-agents-js/packages/agents-openai/test/regression.test.ts

cat > "$REGRESSION_DST" <<'REGRESSION_EOF'
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
REGRESSION_EOF

pytest -v --tb=short /tests/test_outputs.py
PYTEST_RC=$?

if [ $PYTEST_RC -eq 0 ]; then
  echo 1 > /logs/verifier/reward.txt
else
  echo 0 > /logs/verifier/reward.txt
fi

exit 0
