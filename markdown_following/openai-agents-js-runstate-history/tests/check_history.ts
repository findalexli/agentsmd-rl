/**
 * Oracle checks for the RunState.history getter contract.
 *
 * Run via: tsx check_history.ts
 * Each check prints `CHECK <name>: PASS` or `CHECK <name>: FAIL <reason>`.
 * Exit code is 0 only when every check passes.
 */

import * as assert from 'node:assert/strict';
import { RunState } from './src/runState';
import { RunContext } from './src/runContext';
import { Agent } from './src/agent';
import { RunMessageOutputItem } from './src/items';

const TEST_MSG = {
  id: '123',
  status: 'completed' as const,
  type: 'message' as const,
  role: 'assistant' as const,
  content: [
    {
      type: 'output_text' as const,
      text: 'Hello World',
      providerData: { annotations: [] },
    },
  ],
};

type Check = () => Promise<void> | void;

const checks: Record<string, Check> = {
  string_input_with_generated_item: () => {
    const ctx = new RunContext();
    const agent = new Agent({ name: 'HistAgent' });
    const state = new RunState(ctx, 'input', agent, 1);
    state._generatedItems.push(new RunMessageOutputItem(TEST_MSG, agent));
    const history = (state as unknown as { history: unknown }).history;
    assert.ok(Array.isArray(history), 'history must be an array');
    assert.deepStrictEqual(history, [
      { type: 'message', role: 'user', content: 'input' },
      TEST_MSG,
    ]);
  },

  string_input_no_generated_items: () => {
    const ctx = new RunContext();
    const agent = new Agent({ name: 'HistAgent3' });
    const state = new RunState(ctx, 'just the input', agent, 2);
    const history = (state as unknown as { history: unknown }).history;
    assert.deepStrictEqual(history, [
      { type: 'message', role: 'user', content: 'just the input' },
    ]);
  },

  array_input_preserves_order: () => {
    const ctx = new RunContext();
    const agent = new Agent({ name: 'HistAgent4' });
    const inputItems = [
      { type: 'message' as const, role: 'user' as const, content: 'hello' },
      { type: 'message' as const, role: 'user' as const, content: 'world' },
    ];
    const state = new RunState(ctx, inputItems as any, agent, 1);
    state._generatedItems.push(new RunMessageOutputItem(TEST_MSG, agent));
    const history = (state as unknown as { history: unknown[] }).history;
    assert.deepStrictEqual(history, [...inputItems, TEST_MSG]);
  },

  preserved_after_serialization: async () => {
    const ctx = new RunContext();
    const agent = new Agent({ name: 'HistAgent2' });
    const state = new RunState(ctx, 'input', agent, 1);
    state._generatedItems.push(new RunMessageOutputItem(TEST_MSG, agent));
    const restored = await RunState.fromString(agent, state.toString());
    const original = (state as unknown as { history: unknown }).history;
    const after = (restored as unknown as { history: unknown }).history;
    assert.ok(
      Array.isArray(original) && original.length === 2,
      'state.history must be a 2-element array (input + generated item)',
    );
    assert.ok(
      Array.isArray(after) && after.length === 2,
      'restored.history must be a 2-element array (input + generated item)',
    );
    assert.deepStrictEqual(after, original);
    assert.deepStrictEqual(after, [
      { type: 'message', role: 'user', content: 'input' },
      TEST_MSG,
    ]);
  },
};

async function main(): Promise<number> {
  let failures = 0;
  for (const [name, fn] of Object.entries(checks)) {
    try {
      await fn();
      console.log(`CHECK ${name}: PASS`);
    } catch (err) {
      failures += 1;
      const msg =
        err instanceof Error
          ? `${err.name}: ${err.message}`
          : String(err);
      console.log(`CHECK ${name}: FAIL ${msg}`);
    }
  }
  return failures === 0 ? 0 : 1;
}

main().then((code) => process.exit(code));
