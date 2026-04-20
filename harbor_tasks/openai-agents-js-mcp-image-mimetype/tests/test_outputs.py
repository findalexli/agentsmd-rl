"""
Benchmark tests for openai-agents-js PR #1071
Fix: preserve MCP image mimeType in tool outputs

Tests verify that MCP image outputs using mimeType (not mediaType) are correctly
converted to proper data URLs rather than forwarding raw base64.
"""

import subprocess
import os
import sys

REPO = "/workspace/openai-agents-js"


def _run(cmd, timeout=300, cwd=None):
    """Run a command and return the CompletedProcess."""
    cwd = cwd or REPO
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )


# ──────────────────────────────────────────────
# fail-to-pass tests (MUST fail on base commit)
# ──────────────────────────────────────────────


def test_mcp_image_top_level_mimetype_jpeg():
    """
    MCP image output with mimeType='image/jpeg' at top level should produce
    a proper data:image/jpeg;base64,... URL via getToolCallOutputItem.
    On base commit, raw base64 is returned instead.
    """
    test_code = """
import { getToolCallOutputItem } from './packages/agents-core/src/runner/toolExecution';
import { Buffer } from 'node:buffer';

const call = { callId: 'c1', name: 'screenshot', arguments: '{}' };
const b64 = Buffer.from('test-image-data').toString('base64');

const result = getToolCallOutputItem(call, {
  type: 'image',
  data: b64,
  mimeType: 'image/jpeg',
} as any);

const img = result.output[0];
if (img.type !== 'input_image') {
  console.error('FAIL: wrong type', img.type);
  process.exit(1);
}
if (!String(img.image).startsWith('data:image/jpeg;base64,')) {
  console.error('FAIL: not a data URL, got:', img.image);
  process.exit(1);
}
if (!String(img.image).endsWith(b64)) {
  console.error('FAIL: base64 data missing from URL');
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"Top-level mimeType jpeg test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout


def test_mcp_image_top_level_mimetype_png():
    """
    MCP image output with mimeType='image/png' at top level should produce
    a proper data:image/png;base64,... URL. Tests different mime type than jpeg.
    """
    test_code = """
import { getToolCallOutputItem } from './packages/agents-core/src/runner/toolExecution';
import { Buffer } from 'node:buffer';

const call = { callId: 'c2', name: 'screenshot', arguments: '{}' };
const b64 = Buffer.from('PNG-RAW-BYTES').toString('base64');

const result = getToolCallOutputItem(call, {
  type: 'image',
  data: b64,
  mimeType: 'image/png',
} as any);

const img = result.output[0];
if (!String(img.image).startsWith('data:image/png;base64,')) {
  console.error('FAIL: not a png data URL, got:', img.image);
  process.exit(1);
}
if (!String(img.image).endsWith(b64)) {
  console.error('FAIL: base64 data missing from URL');
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"Top-level mimeType png test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout


def test_mcp_image_nested_mimetype_gif():
    """
    MCP image output with mimeType inside a nested image.data object should
    produce a proper data URL. On base commit, mimeType on nested objects is ignored.
    """
    test_code = """
import { getToolCallOutputItem } from './packages/agents-core/src/runner/toolExecution';
import { Buffer } from 'node:buffer';

const call = { callId: 'c3', name: 'draw', arguments: '{}' };
const b64 = Buffer.from('nested-gif-data').toString('base64');

const result = getToolCallOutputItem(call, {
  type: 'image',
  image: {
    data: b64,
    mimeType: 'image/gif',
  },
} as any);

const img = result.output[0];
if (!String(img.image).startsWith('data:image/gif;base64,')) {
  console.error('FAIL: not a gif data URL, got:', img.image);
  process.exit(1);
}
if (!String(img.image).endsWith(b64)) {
  console.error('FAIL: base64 data missing from URL');
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"Nested mimeType gif test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout


def test_openai_adapter_mimetype_nested_and_top_level():
    """
    OpenAI Responses adapter should convert ToolOutputImage with mimeType
    into proper data:image/jpeg;base64,... URLs for both nested image objects
    and top-level data+mimeType.
    """
    test_code = """
import { getInputItems } from './packages/agents-openai/src/openaiResponsesModel';
import { Buffer } from 'node:buffer';

const b64 = Buffer.from('adapter-test').toString('base64');

const items = getInputItems([
  {
    type: 'function_call_result',
    callId: 'c6',
    output: { type: 'image', image: { data: b64, mimeType: 'image/jpeg' } },
  },
  {
    type: 'function_call_result',
    callId: 'c7',
    output: { type: 'image', data: b64, mimeType: 'image/jpeg' },
  },
] as any);

// Check nested case
const item0 = items[0] as any;
if (item0.output[0].image_url !== 'data:image/jpeg;base64,' + b64) {
  console.error('FAIL nested: got', item0.output[0].image_url);
  process.exit(1);
}

// Check top-level case
const item1 = items[1] as any;
if (item1.output[0].image_url !== 'data:image/jpeg;base64,' + b64) {
  console.error('FAIL top-level: got', item1.output[0].image_url);
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"OpenAI adapter mimeType test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout


def test_openai_adapter_top_level_mimetype_fallback():
    """
    When mimeType is only at the top level (not on nested image.data),
    the adapter should fall back to top-level mimeType for the data URL.
    """
    test_code = """
import { getInputItems } from './packages/agents-openai/src/openaiResponsesModel';
import { Buffer } from 'node:buffer';

const b64 = Buffer.from('fallback-test').toString('base64');

const items = getInputItems([
  {
    type: 'function_call_result',
    callId: 'c10',
    output: {
      type: 'image',
      image: { data: b64 },
      mimeType: 'image/jpeg',
    },
  },
] as any);

const url = (items[0] as any).output[0].image_url;
if (url !== 'data:image/jpeg;base64,' + b64) {
  console.error('FAIL: got', url);
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"Top-level mimeType fallback test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout


# ──────────────────────────────────────────────
# pass-to-pass tests (SHOULD pass on both base and fixed)
# ──────────────────────────────────────────────


def test_agents_core_test_suite():
    """The full agents-core test suite should pass."""
    r = _run(
        [
            "npx", "vitest", "run",
            "packages/agents-core/test/",
        ],
        timeout=300,
    )
    assert r.returncode == 0, (
        f"agents-core test suite failed.\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_agents_openai_test_suite():
    """The full agents-openai test suite should pass."""
    r = _run(
        [
            "npx", "vitest", "run",
            "packages/agents-openai/test/",
        ],
        timeout=300,
    )
    assert r.returncode == 0, (
        f"agents-openai test suite failed.\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_build():
    """The repo should build successfully."""
    r = _run(["pnpm", "build"], timeout=300)
    assert r.returncode == 0, (
        f"Build failed.\n"
        f"stdout:\n{r.stdout[-1000:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_lint():
    """The repo linter should pass."""
    r = _run(["pnpm", "lint"], timeout=120)
    assert r.returncode == 0, (
        f"Lint failed.\n"
        f"stdout:\n{r.stdout[-1000:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_dist_check():
    """CI checks that generated type declarations are up to date (pass_to_pass)."""
    r = _run(
        ["pnpm", "-r", "-F", "@openai/*", "dist:check"],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"dist:check failed.\n"
        f"stdout:\n{r.stdout[-1000:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_typecheck_agents_core():
    """TypeScript type checking passes for agents-core package (pass_to_pass)."""
    r = _run(
        ["npx", "tsc", "--noEmit", "-p", "packages/agents-core/tsconfig.json"],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"agents-core typecheck failed.\n"
        f"stdout:\n{r.stdout[-1000:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_typecheck_agents_openai():
    """TypeScript type checking passes for agents-openai package (pass_to_pass)."""
    r = _run(
        ["npx", "tsc", "--noEmit", "-p", "packages/agents-openai/tsconfig.json"],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"agents-openai typecheck failed.\n"
        f"stdout:\n{r.stdout[-1000:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_toolExecution_tests():
    """Existing toolExecution tests pass — covers tool output handling (pass_to_pass)."""
    r = _run(
        [
            "npx", "vitest", "run",
            "packages/agents-core/test/runner/toolExecution.test.ts",
        ],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"toolExecution tests failed.\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_repo_openaiResponsesModel_helpers_tests():
    """Existing openaiResponsesModel helper tests pass (pass_to_pass)."""
    r = _run(
        [
            "npx", "vitest", "run",
            "packages/agents-openai/test/openaiResponsesModel.helpers.test.ts",
        ],
        timeout=120,
    )
    assert r.returncode == 0, (
        f"openaiResponsesModel helpers tests failed.\n"
        f"stdout:\n{r.stdout[-1500:]}\nstderr:\n{r.stderr[-500:]}"
    )


def test_openai_adapter_no_double_wrap_data_url():
    """
    When image data is already a data URL and mimeType is also present,
    the adapter should NOT double-wrap the data URL. This is a regression
    guard to ensure the formatInlineData guard works correctly.
    """
    test_code = """
import { getInputItems } from './packages/agents-openai/src/openaiResponsesModel';
import { Buffer } from 'node:buffer';

const b64 = Buffer.from('existing-data').toString('base64');
const dataUrl = 'data:image/jpeg;base64,' + b64;

const items = getInputItems([
  {
    type: 'function_call_result',
    callId: 'c8',
    output: { type: 'image', image: { data: dataUrl, mimeType: 'image/jpeg' } },
  },
] as any);

const url = (items[0] as any).output[0].image_url;
if (url !== dataUrl) {
  console.error('FAIL: double-wrapped or wrong, got:', url);
  process.exit(1);
}
if (url.includes('data:image/jpeg;base64,data:')) {
  console.error('FAIL: double-wrapped detected');
  process.exit(1);
}
console.log('PASS');
"""
    r = _run(["npx", "tsx", "-e", test_code], timeout=60)
    assert r.returncode == 0, (
        f"No double-wrap test failed.\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert "PASS" in r.stdout
