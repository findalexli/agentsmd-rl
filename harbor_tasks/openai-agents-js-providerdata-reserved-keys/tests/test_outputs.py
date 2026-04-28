"""Verifier tests for openai/openai-agents-js#1064.

Tests the chat completions converter no longer lets providerData overwrite
SDK-authored canonical envelope fields like role/content/tool_calls/etc.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/openai-agents-js")
PKG = REPO / "packages" / "agents-openai"
F2P_TEST_DST = PKG / "test" / "_harbor_f2p.test.ts"

# Behavioural f2p test, written into the package at test time so vitest can
# resolve workspace imports the same way the existing test suite does.
F2P_TS = """import { describe, test, expect } from 'vitest';
import {
  extractAllAssistantContent,
  extractAllUserContent,
  itemsToMessages,
} from '../src/openaiChatCompletionsConverter';
import { protocol } from '@openai/agents-core';

describe('harbor f2p: providerData reserved-key filtering', () => {
  test('user message providerData cannot overwrite role or content envelope', () => {
    const items: protocol.ModelItem[] = [
      {
        type: 'message',
        role: 'user',
        content: 'real-user',
        providerData: {
          role: 'assistant',
          content: 'override-user',
          customUser: true,
        },
      } as protocol.UserMessageItem,
    ];
    const msgs = itemsToMessages(items);
    expect(msgs).toHaveLength(1);
    const msg = msgs[0] as any;
    expect(msg.role).toBe('user');
    expect(typeof msg.content === 'string' || Array.isArray(msg.content)).toBe(
      true,
    );
    if (typeof msg.content === 'string') {
      expect(msg.content).not.toBe('override-user');
    }
    expect(msg.customUser).toBe(true);
  });

  test('system message providerData cannot overwrite role or content envelope', () => {
    const items: protocol.ModelItem[] = [
      {
        type: 'message',
        role: 'system',
        content: 'system-prompt',
        providerData: {
          role: 'user',
          content: 'override-system',
          customSystem: true,
        },
      } as protocol.SystemMessageItem,
    ];
    const msgs = itemsToMessages(items);
    expect(msgs).toHaveLength(1);
    const msg = msgs[0] as any;
    expect(msg.role).toBe('system');
    expect(msg.content).toBe('system-prompt');
    expect(msg.customSystem).toBe(true);
  });

  test('function_call providerData cannot overwrite role/content/tool_calls envelope', () => {
    const items: protocol.ModelItem[] = [
      {
        type: 'function_call',
        id: 'item1',
        callId: 'call1',
        name: 'real_fn',
        arguments: '{}',
        status: 'completed',
        providerData: {
          role: 'tool',
          content: 'override-assistant',
          tool_calls: [{ id: 'override' }],
          type: 'function',
          function: {
            name: 'override_name',
            arguments: '{"override":true}',
            extraNested: true,
          },
          customAssistant: true,
        },
      } as protocol.FunctionCallItem,
    ];
    const msgs = itemsToMessages(items);
    expect(msgs).toHaveLength(1);
    const asst = msgs[0] as any;
    expect(asst.role).toBe('assistant');
    expect(asst.tool_calls).toHaveLength(1);
    const call = asst.tool_calls[0];
    expect(call.id).toBe('call1');
    expect(call.type).toBe('function');
    expect(call.function.name).toBe('real_fn');
    expect(call.function.arguments).toBe('{}');
    expect(call.function.extraNested).toBe(true);
    expect(call.customAssistant).toBe(true);
  });

  test('function_call_result providerData cannot overwrite role/tool_call_id/content envelope', () => {
    const items: protocol.ModelItem[] = [
      {
        type: 'function_call_result',
        id: 'item2',
        name: 'fn',
        callId: 'call1',
        status: 'completed',
        output: 'real-output',
        providerData: {
          role: 'assistant',
          tool_call_id: 'override-call',
          content: 'override-tool',
          extraTool: true,
        },
      } as protocol.FunctionCallResultItem,
    ];
    const msgs = itemsToMessages(items);
    expect(msgs).toHaveLength(1);
    const tool = msgs[0] as any;
    expect(tool.role).toBe('tool');
    expect(tool.tool_call_id).toBe('call1');
    expect(tool.content).toBe('real-output');
    expect(tool.extraTool).toBe(true);
  });

  test('extractAllUserContent input_text providerData cannot overwrite type/text', () => {
    const userContent: protocol.UserMessageItem['content'] = [
      {
        type: 'input_text',
        text: 'real-text',
        providerData: {
          type: 'override_type',
          text: 'override_text',
          extraText: true,
        },
      },
    ];
    const out = extractAllUserContent(userContent) as any[];
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe('text');
    expect(out[0].text).toBe('real-text');
    expect(out[0].extraText).toBe(true);
  });

  test('extractAllUserContent input_image providerData cannot overwrite url', () => {
    const userContent: protocol.UserMessageItem['content'] = [
      {
        type: 'input_image',
        image: 'http://real-image',
        providerData: {
          type: 'override_image',
          image_url: { url: 'http://override', detail: 'high' },
          extraImage: true,
        },
      },
    ];
    const out = extractAllUserContent(userContent) as any[];
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe('image_url');
    expect(out[0].image_url.url).toBe('http://real-image');
    expect(out[0].image_url.detail).toBe('high');
    expect(out[0].extraImage).toBe(true);
  });

  test('extractAllUserContent audio providerData cannot overwrite data', () => {
    const userContent: protocol.UserMessageItem['content'] = [
      {
        type: 'audio',
        audio: 'real-audio',
        providerData: {
          type: 'override_audio',
          input_audio: { data: 'override', foo: 'bar' },
          extraAudio: true,
        },
      },
    ];
    const out = extractAllUserContent(userContent) as any[];
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe('input_audio');
    expect(out[0].input_audio.data).toBe('real-audio');
    expect(out[0].input_audio.foo).toBe('bar');
    expect(out[0].extraAudio).toBe(true);
  });

  test('extractAllAssistantContent output_text providerData cannot overwrite type/text', () => {
    const asstContent: protocol.AssistantMessageItem['content'] = [
      {
        type: 'output_text',
        text: 'real-asst',
        providerData: {
          type: 'override',
          text: 'override-asst',
          extraAsst: true,
        },
      },
    ];
    const out = extractAllAssistantContent(asstContent) as any[];
    expect(out).toHaveLength(1);
    expect(out[0].type).toBe('text');
    expect(out[0].text).toBe('real-asst');
    expect(out[0].extraAsst).toBe(true);
  });
});
"""


def _run(cmd, **kwargs):
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    kwargs.setdefault("cwd", REPO)
    kwargs.setdefault("timeout", 600)
    return subprocess.run(cmd, **kwargs)


def _ensure_built():
    """Make sure dist/ is up-to-date so workspace imports resolve."""
    core_dist = REPO / "packages" / "agents-core" / "dist" / "index.mjs"
    openai_dist = PKG / "dist" / "index.mjs"
    if not core_dist.exists() or not openai_dist.exists():
        r = _run(["pnpm", "build"], timeout=600)
        assert r.returncode == 0, (
            f"pnpm build failed:\nstdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
        )


def _drop_f2p_test():
    F2P_TEST_DST.parent.mkdir(parents=True, exist_ok=True)
    F2P_TEST_DST.write_text(F2P_TS)


def _remove_f2p_test():
    if F2P_TEST_DST.exists():
        F2P_TEST_DST.unlink()


# ---------- fail-to-pass: behavioural test for the bug ----------

def test_provider_data_reserved_keys_filtered():
    """f2p: providerData must not overwrite canonical envelope fields."""
    _ensure_built()
    _drop_f2p_test()
    try:
        r = _run(
            [
                "pnpm",
                "exec",
                "vitest",
                "run",
                "--no-coverage",
                "--project",
                "@openai/agents-openai",
                "test/_harbor_f2p.test.ts",
            ],
            timeout=600,
        )
        assert r.returncode == 0, (
            "Harbor f2p vitest failed.\n"
            f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-1500:]}"
        )
    finally:
        _remove_f2p_test()


# ---------- pass-to-pass: existing repo CI/CD ----------

def test_repo_unit_tests_pass():
    """p2p: repo's existing vitest unit tests for agents-openai pass."""
    _ensure_built()
    _remove_f2p_test()
    r = _run(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "--no-coverage",
            "--project",
            "@openai/agents-openai",
        ],
        timeout=600,
    )
    assert r.returncode == 0, (
        "Existing agents-openai vitest suite failed.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-1500:]}"
    )


def test_repo_lint_passes():
    """p2p: repo's ESLint passes (AGENTS.md mandates `pnpm lint` clean)."""
    r = _run(["pnpm", "lint"], timeout=600)
    assert r.returncode == 0, (
        "pnpm lint failed.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-1500:]}"
    )


def test_repo_build_check_passes():
    """p2p: TypeScript build-check across the workspace passes."""
    r = _run(
        ["pnpm", "-F", "@openai/agents-openai", "build-check"], timeout=600
    )
    assert r.returncode == 0, (
        "build-check failed.\n"
        f"stdout:\n{r.stdout[-3000:]}\nstderr:\n{r.stderr[-1500:]}"
    )

# === PR-added f2p tests — verify the agent added the PR's test cases and they pass ===

def test_pr_added_extractAllUserContent_preserves_extras_but_ignor():
    """f2p: PR-added test 'extractAllUserContent preserves extras but ignores reserved providerData fields' exists and passes."""
    _ensure_built()
    _remove_f2p_test()
    test_file = "test/openaiChatCompletionsConverter.test.ts"
    test_name = "extractAllUserContent preserves extras but ignores reserved providerData fields"
    r = _run([
        "pnpm", "exec", "vitest", "run", "--no-coverage",
        "--project", "@openai/agents-openai",
        "--reporter", "verbose",
        test_file,
    ])
    assert r.returncode == 0, (
        f"Vitest run for {test_file} failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}")
    assert test_name in r.stdout, (
        f"PR-added test '{test_name}' not found in vitest output.\n"
        f"stdout: {r.stdout[-2000:]}")

def test_pr_added_preserves_extra_providerData_without_letting_it_():
    """f2p: PR-added test 'preserves extra providerData without letting it overwrite canonical envelopes' exists and passes."""
    _ensure_built()
    _remove_f2p_test()
    test_file = "test/openaiChatCompletionsConverter.test.ts"
    test_name = "preserves extra providerData without letting it overwrite canonical envelopes"
    r = _run([
        "pnpm", "exec", "vitest", "run", "--no-coverage",
        "--project", "@openai/agents-openai",
        "--reporter", "verbose",
        test_file,
    ])
    assert r.returncode == 0, (
        f"Vitest run for {test_file} failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}")
    assert test_name in r.stdout, (
        f"PR-added test '{test_name}' not found in vitest output.\n"
        f"stdout: {r.stdout[-2000:]}")

def test_pr_added_removes_reserved_keys_without_touching_other_val():
    """f2p: PR-added test 'removes reserved keys without touching other values' exists and passes."""
    _ensure_built()
    _remove_f2p_test()
    test_file = "test/utils/providerData.test.ts"
    test_name = "removes reserved keys without touching other values"
    r = _run([
        "pnpm", "exec", "vitest", "run", "--no-coverage",
        "--project", "@openai/agents-openai",
        "--reporter", "verbose",
        test_file,
    ])
    assert r.returncode == 0, (
        f"Vitest run for {test_file} failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-2000:]}\nstderr: {r.stderr[-1000:]}")
    assert test_name in r.stdout, (
        f"PR-added test '{test_name}' not found in vitest output.\n"
        f"stdout: {r.stdout[-2000:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_extractAllUserContent_preserves_extras_but_ignor():
    """fail_to_pass | PR added test 'extractAllUserContent preserves extras but ignores reserved providerData fields' in 'packages/agents-openai/test/openaiChatCompletionsConverter.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "extractAllUserContent preserves extras but ignores reserved providerData fields" 2>&1 || npx vitest run "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "extractAllUserContent preserves extras but ignores reserved providerData fields" 2>&1 || pnpm jest "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "extractAllUserContent preserves extras but ignores reserved providerData fields" 2>&1 || npx jest "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "extractAllUserContent preserves extras but ignores reserved providerData fields" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'extractAllUserContent preserves extras but ignores reserved providerData fields' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_preserves_extra_providerData_without_letting_it_():
    """fail_to_pass | PR added test 'preserves extra providerData without letting it overwrite canonical envelopes' in 'packages/agents-openai/test/openaiChatCompletionsConverter.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "preserves extra providerData without letting it overwrite canonical envelopes" 2>&1 || npx vitest run "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "preserves extra providerData without letting it overwrite canonical envelopes" 2>&1 || pnpm jest "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "preserves extra providerData without letting it overwrite canonical envelopes" 2>&1 || npx jest "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts" -t "preserves extra providerData without letting it overwrite canonical envelopes" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'preserves extra providerData without letting it overwrite canonical envelopes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_removes_reserved_keys_without_touching_other_val():
    """fail_to_pass | PR added test 'removes reserved keys without touching other values' in 'packages/agents-openai/test/utils/providerData.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-openai/test/utils/providerData.test.ts" -t "removes reserved keys without touching other values" 2>&1 || npx vitest run "packages/agents-openai/test/utils/providerData.test.ts" -t "removes reserved keys without touching other values" 2>&1 || pnpm jest "packages/agents-openai/test/utils/providerData.test.ts" -t "removes reserved keys without touching other values" 2>&1 || npx jest "packages/agents-openai/test/utils/providerData.test.ts" -t "removes reserved keys without touching other values" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'removes reserved keys without touching other values' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
