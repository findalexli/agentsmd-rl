"""
Task: openai-agents-js-fix-propagate-providerdata-for-functioncall
Repo: openai-agents-js @ 85b6c896ea19d8f859ba86f3993054a832a93c64
PR:   746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/openai-agents-js"
CONVERTER = "packages/agents-openai/src/openaiChatCompletionsConverter.ts"


def _run_tsx(script: str, *, timeout: int = 60) -> subprocess.CompletedProcess:
    """Write a temp .ts file, run it with tsx, clean up."""
    test_file = Path(REPO) / "__harbor_tmp_test.ts"
    test_file.write_text(script)
    try:
        return subprocess.run(
            ["npx", "tsx", str(test_file)],
            cwd=REPO,
            capture_output=True,
            timeout=timeout,
        )
    finally:
        test_file.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_providerdata_propagated():
    """function_call providerData fields appear on the converted assistant message."""
    r = _run_tsx("""\
import { itemsToMessages } from './packages/agents-openai/src/openaiChatCompletionsConverter';

const items = [{
    type: 'function_call' as const,
    id: '1',
    callId: 'call1',
    name: 'myFunc',
    arguments: '{"x":1}',
    status: 'in_progress' as const,
    providerData: { custom_field: 'value', another: 123 },
}];

const msgs = itemsToMessages(items as any);
const asst = msgs[0] as any;

if (asst.custom_field !== 'value') {
    console.error('custom_field not found on assistant msg:', JSON.stringify(asst));
    process.exit(1);
}
if (asst.another !== 123) {
    console.error('another not found on assistant msg:', JSON.stringify(asst));
    process.exit(1);
}
""")
    assert r.returncode == 0, \
        f"providerData not propagated to assistant message:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# [pr_diff] fail_to_pass
def test_providerdata_multiple_calls_merged():
    """providerData from multiple function_calls merged into a single assistant message."""
    r = _run_tsx("""\
import { itemsToMessages } from './packages/agents-openai/src/openaiChatCompletionsConverter';

const items = [
    {
        type: 'function_call' as const,
        id: '1', callId: 'call1', name: 'f1',
        arguments: '{}', status: 'in_progress' as const,
        providerData: { from_first: true },
    },
    {
        type: 'function_call' as const,
        id: '2', callId: 'call2', name: 'f2',
        arguments: '{}', status: 'in_progress' as const,
        providerData: { from_second: true },
    },
];

const msgs = itemsToMessages(items as any);
const asst = msgs[0] as any;

if (asst.from_first !== true) {
    console.error('from_first missing:', JSON.stringify(asst));
    process.exit(1);
}
if (asst.from_second !== true) {
    console.error('from_second missing:', JSON.stringify(asst));
    process.exit(1);
}
if (!asst.tool_calls || asst.tool_calls.length !== 2) {
    console.error('expected 2 tool_calls:', JSON.stringify(asst));
    process.exit(1);
}
""")
    assert r.returncode == 0, \
        f"Multiple providerData not merged:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must contain build-check somewhere in the PR submission instructions
    assert "build-check" in content, \
        "CONTRIBUTING.md should mention 'build-check' in the contribution workflow"

    # The build-check command should appear in a code block alongside build/test/lint
    lines = content.split("\n")
    found = False
    for line in lines:
        if "build-check" in line and ("pnpm" in line or "build" in line):
            found = True
            break
    assert found, \
        "CONTRIBUTING.md should have 'build-check' in a pnpm command sequence"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression check
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_function_call_without_providerdata():
    """function_call items without providerData still convert correctly."""
    r = _run_tsx("""\
import { itemsToMessages } from './packages/agents-openai/src/openaiChatCompletionsConverter';

const items = [{
    type: 'function_call' as const,
    id: '1',
    callId: 'call1',
    name: 'f',
    arguments: '{}',
    status: 'in_progress' as const,
}];

const msgs = itemsToMessages(items as any);
const asst = msgs[0] as any;

if (asst.role !== 'assistant') {
    console.error('expected assistant role:', JSON.stringify(asst));
    process.exit(1);
}
if (!asst.tool_calls || asst.tool_calls.length !== 1) {
    console.error('expected 1 tool_call:', JSON.stringify(asst));
    process.exit(1);
}
if (asst.tool_calls[0].function.name !== 'f') {
    console.error('wrong function name:', JSON.stringify(asst));
    process.exit(1);
}
""")
    assert r.returncode == 0, \
        f"function_call without providerData broke:\n{r.stdout.decode()}\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — upstream tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_existing_converter_tests_pass():
    """Upstream converter test suite still passes after changes."""
    r = subprocess.run(
        ["npx", "vitest", "run",
         "packages/agents-openai/test/openaiChatCompletionsConverter.test.ts",
         "--reporter=verbose", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        timeout=120,
    )
    assert r.returncode == 0, \
        f"Upstream tests failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
