"""
Task: openclaw-msteams-stream-reset
Repo: openclaw/openclaw @ 4752aca926624efdeb62f2f43b606f5090be8903
PR:   56071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = os.path.join(REPO, "extensions/msteams/src/reply-stream-controller.ts")

# ---------------------------------------------------------------------------
# Node.js behavioral test infrastructure
#
# Uses --experimental-strip-types to run the actual .ts module natively,
# with a custom ESM loader to mock the TeamsHttpStream dependency.
# ---------------------------------------------------------------------------

_MOCK_STREAM_JS = """\
let _instances = [];
export class TeamsHttpStream {
    constructor(opts) {
        this.hasContent = false;
        this.isFinalized = false;
        this._opts = opts;
        _instances.push(this);
    }
    update(text) { this.hasContent = true; }
    async finalize() { this.isFinalized = true; }
    async sendInformativeUpdate(text) {}
}
export function getInstances() { return _instances; }
export function clearInstances() { _instances = []; }
"""


def _run_node_test(test_body):
    """Run a behavioral test against the real TypeScript module via Node.js."""
    assert Path(TARGET).exists(), f"Target file not found: {TARGET}"

    with tempfile.TemporaryDirectory() as tmpdir:
        mock_path = os.path.join(tmpdir, "mock-streaming.mjs")
        mock_url = "file://" + mock_path
        target_url = "file://" + TARGET

        Path(mock_path).write_text(_MOCK_STREAM_JS)

        # ESM loader: intercept streaming-message import → mock
        loader_src = (
            "const MOCK = '__MOCK__';\n"
            "export async function resolve(specifier, context, nextResolve) {\n"
            "  if (specifier.includes('streaming-message')) {\n"
            "    return { url: MOCK, shortCircuit: true };\n"
            "  }\n"
            "  if (/runtime-api|monitor-types|sdk-types/.test(specifier)) {\n"
            "    return { url: MOCK, shortCircuit: true };\n"
            "  }\n"
            "  return nextResolve(specifier, context);\n"
            "}\n"
        ).replace("__MOCK__", mock_url)
        loader_path = os.path.join(tmpdir, "loader.mjs")
        Path(loader_path).write_text(loader_src)

        # Test harness: import real module, expose helpers
        test_src = (
            "import { createTeamsReplyStreamController } from '__TARGET__';\n"
            "import { getInstances, clearInstances } from '__MOCK__';\n"
            "\n"
            "function makeCtrl(conversationType = 'personal') {\n"
            "  clearInstances();\n"
            "  return createTeamsReplyStreamController({\n"
            "    conversationType,\n"
            "    context: { sendActivity: async () => ({ id: 'a' }) },\n"
            "    feedbackLoopEnabled: false,\n"
            "    log: { debug: () => {} },\n"
            "  });\n"
            "}\n"
            "\n"
            "__BODY__\n"
        ).replace("__TARGET__", target_url).replace("__MOCK__", mock_url).replace("__BODY__", test_body)

        test_path = os.path.join(tmpdir, "test.mjs")
        Path(test_path).write_text(test_src)

        r = subprocess.run(
            [
                "node",
                "--experimental-strip-types",
                "--no-warnings",
                "--loader", "file://" + loader_path,
                test_path,
            ],
            capture_output=True,
            timeout=30,
        )

        stdout = r.stdout.decode().strip()
        stderr = r.stderr.decode().strip()
        if r.returncode != 0:
            raise AssertionError(
                f"Node.js behavioral test failed (exit {r.returncode}):\n"
                f"stdout: {stdout}\nstderr: {stderr}"
            )
        try:
            return json.loads(stdout.split("\n")[-1])
        except (json.JSONDecodeError, IndexError) as exc:
            raise AssertionError(
                f"Could not parse Node.js output as JSON:\n{stdout}\nstderr: {stderr}"
            ) from exc


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_stream_received_tokens_reset():
    """After first-segment suppression, subsequent segments use fallback delivery.

    The core bug: streamReceivedTokens stays true forever, causing all text
    segments after tool calls to be silently suppressed.
    """
    results = _run_node_test(
        "const results = {};\n"
        "for (const [label, texts] of [\n"
        "    ['pair1', ['Hello world', 'After tool call']],\n"
        "    ['pair2', ['First analysis', 'Continued response with more detail']],\n"
        "    ['pair3', ['Short', 'A much longer follow-up segment with many details']],\n"
        "]) {\n"
        "    const ctrl = makeCtrl();\n"
        "    ctrl.onPartialReply({ text: texts[0] });\n"
        "    const r1 = ctrl.preparePayload({ text: texts[0] });\n"
        "\n"
        "    // Second segment WITHOUT onPartialReply — simulates tool call gap\n"
        "    const r2 = ctrl.preparePayload({ text: texts[1] });\n"
        "\n"
        "    results[label] = {\n"
        "        first_suppressed: r1 === undefined,\n"
        "        second_returned: r2 !== undefined,\n"
        "        second_text_correct: r2?.text === texts[1],\n"
        "    };\n"
        "}\n"
        "console.log(JSON.stringify(results));\n"
    )
    for label, r in results.items():
        assert r["first_suppressed"], f"{label}: first segment was not suppressed"
        assert r["second_returned"], (
            f"{label}: second segment was suppressed — "
            "streamReceivedTokens not reset after first suppression"
        )
        assert r["second_text_correct"], f"{label}: second segment text was altered"


# [pr_diff] fail_to_pass
def test_is_finalized_guard():
    """Finalized stream never re-suppresses fallback delivery.

    Even if onPartialReply fires after stream finalization (setting
    streamReceivedTokens back to true), preparePayload must check
    isFinalized and return the payload instead of suppressing.
    """
    results = _run_node_test(
        "const results = {};\n"
        "for (const [label, texts] of [\n"
        "    ['case1', ['Segment A', 'Segment B']],\n"
        "    ['case2', ['Analysis part 1', 'Analysis part 2 with more text']],\n"
        "    ['case3', ['x', 'A longer second segment']],\n"
        "]) {\n"
        "    const ctrl = makeCtrl();\n"
        "\n"
        "    // First segment streamed\n"
        "    ctrl.onPartialReply({ text: texts[0] });\n"
        "    const r1 = ctrl.preparePayload({ text: texts[0] });\n"
        "\n"
        "    // onPartialReply fires AGAIN for second segment tokens\n"
        "    // This sets streamReceivedTokens back to true\n"
        "    ctrl.onPartialReply({ text: texts[1] });\n"
        "\n"
        "    // preparePayload: isFinalized guard must prevent re-suppression\n"
        "    const r2 = ctrl.preparePayload({ text: texts[1] });\n"
        "\n"
        "    results[label] = {\n"
        "        first_suppressed: r1 === undefined,\n"
        "        second_returned: r2 !== undefined,\n"
        "        second_text: r2?.text === texts[1],\n"
        "    };\n"
        "}\n"
        "console.log(JSON.stringify(results));\n"
    )
    for label, r in results.items():
        assert r["first_suppressed"], f"{label}: first segment not suppressed"
        assert r["second_returned"], (
            f"{label}: second segment suppressed despite stream being finalized — "
            "isFinalized guard is missing from preparePayload"
        )
        assert r["second_text"], f"{label}: second segment text was altered"


# [pr_diff] fail_to_pass
def test_pending_finalize_awaited():
    """stream.finalize() is called eagerly in preparePayload.

    The fix calls stream.finalize() when suppressing a text segment so the
    stream is finalized immediately, not deferred to the outer finalize().
    """
    results = _run_node_test(
        "async function run() {\n"
        "    const results = {};\n"
        "    for (const [label, text] of [\n"
        "        ['a', 'Hello world'],\n"
        "        ['b', 'Some other text'],\n"
        "        ['c', 'Third test case'],\n"
        "    ]) {\n"
        "        const ctrl = makeCtrl();\n"
        "        const instances = getInstances();\n"
        "        const stream = instances[instances.length - 1];\n"
        "\n"
        "        ctrl.onPartialReply({ text });\n"
        "        ctrl.preparePayload({ text });\n"
        "\n"
        "        // Wait for async finalize to resolve\n"
        "        await new Promise(r => setImmediate(r));\n"
        "        const earlyFinalized = stream.isFinalized;\n"
        "\n"
        "        // Controller finalize should complete without error\n"
        "        await ctrl.finalize();\n"
        "\n"
        "        results[label] = {\n"
        "            early_finalized: earlyFinalized,\n"
        "            final_finalized: stream.isFinalized,\n"
        "        };\n"
        "    }\n"
        "    console.log(JSON.stringify(results));\n"
        "}\n"
        "run();\n"
    )
    for label, r in results.items():
        assert r["early_finalized"], (
            f"{label}: stream not finalized after preparePayload — "
            "stream.finalize() should be called eagerly in preparePayload"
        )
        assert r["final_finalized"], f"{label}: stream not finalized after controller.finalize()"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_single_segment_suppression_preserved():
    """Normal single-segment streaming suppression still works.

    When stream has content and streamReceivedTokens is true, the first
    preparePayload call suppresses non-media payloads and strips text from
    media payloads.
    """
    results = _run_node_test(
        "// Test 1: text-only payload is suppressed\n"
        "const ctrl1 = makeCtrl();\n"
        "ctrl1.onPartialReply({ text: 'Streamed content' });\n"
        "const textOnly = ctrl1.preparePayload({ text: 'Streamed content' });\n"
        "\n"
        "// Test 2: media payload strips text but keeps media\n"
        "const ctrl2 = makeCtrl();\n"
        "ctrl2.onPartialReply({ text: 'With image' });\n"
        "const media = ctrl2.preparePayload({\n"
        "    text: 'With image',\n"
        "    mediaUrl: 'https://example.com/image.png',\n"
        "});\n"
        "\n"
        "// Test 3: multiple media URLs\n"
        "const ctrl3 = makeCtrl();\n"
        "ctrl3.onPartialReply({ text: 'Gallery' });\n"
        "const multiMedia = ctrl3.preparePayload({\n"
        "    text: 'Gallery',\n"
        "    mediaUrls: ['https://example.com/a.png', 'https://example.com/b.png'],\n"
        "});\n"
        "\n"
        "console.log(JSON.stringify({\n"
        "    text_suppressed: textOnly === undefined,\n"
        "    media_passed: media !== undefined,\n"
        "    media_text_stripped: media?.text === undefined,\n"
        "    media_url_kept: media?.mediaUrl === 'https://example.com/image.png',\n"
        "    multi_media_passed: multiMedia !== undefined,\n"
        "    multi_media_text_stripped: multiMedia?.text === undefined,\n"
        "}));\n"
    )
    assert results["text_suppressed"], "Text-only payload was not suppressed"
    assert results["media_passed"], "Media payload was suppressed entirely"
    assert results["media_text_stripped"], "Text not stripped from media payload"
    assert results["media_url_kept"], "Media URL was removed"
    assert results["multi_media_passed"], "Multi-media payload was suppressed"
    assert results["multi_media_text_stripped"], "Text not stripped from multi-media payload"


# [pr_diff] pass_to_pass
def test_group_chat_passthrough():
    """Group chats (no stream) pass through all payloads unchanged."""
    results = _run_node_test(
        "const results = {};\n"
        "for (const [label, payload] of [\n"
        "    ['text', { text: 'Hello' }],\n"
        "    ['media', { text: 'See this', mediaUrl: 'https://example.com/img.png' }],\n"
        "    ['empty', { text: '' }],\n"
        "]) {\n"
        "    const ctrl = makeCtrl('groupChat');\n"
        "    ctrl.onPartialReply({ text: 'tokens' });\n"
        "    const result = ctrl.preparePayload(payload);\n"
        "    results[label] = {\n"
        "        returned: result !== undefined,\n"
        "        matches: JSON.stringify(result) === JSON.stringify(payload),\n"
        "    };\n"
        "}\n"
        "console.log(JSON.stringify(results));\n"
    )
    for label, r in results.items():
        assert r["returned"], f"{label}: group chat payload was suppressed"
        assert r["matches"], f"{label}: group chat payload was modified"


# [static] pass_to_pass
def test_not_stub():
    """File must have real implementation, not be gutted."""
    src = Path(TARGET).read_text()
    lines = [
        l.strip() for l in src.splitlines()
        if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")
    ]
    assert len(lines) >= 40, f"Only {len(lines)} non-trivial lines — file looks gutted"

    assert "createTeamsReplyStreamController" in src, "Main factory function removed"
    assert re.search(r"export\s+function\s+createTeamsReplyStreamController", src), (
        "createTeamsReplyStreamController is not exported"
    )
    for method in ("onPartialReply", "preparePayload", "finalize", "onReplyStart"):
        assert method in src, f"{method} method removed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:16 @ 4752aca926624efdeb62f2f43b606f5090be8903
def test_no_cross_boundary_imports():
    """Extension code must not import from core src/ via relative paths.

    CLAUDE.md:16 — extension production code should treat openclaw/plugin-sdk/*
    as the public surface; do not import core src/** directly.
    """
    ext_dir = os.path.join(REPO, "extensions/msteams/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    if re.search(r"^import .* from ['\"]\.\.\/\.\.\/\.\.\/src\/", line):
                        violations.append(f"{filepath}:{i}: {line.strip()}")

    assert not violations, (
        "Cross-boundary imports from core src/ found:\n" + "\n".join(violations[:5])
    )


# [agent_config] pass_to_pass — CLAUDE.md:104 @ 4752aca926624efdeb62f2f43b606f5090be8903
def test_no_ts_nocheck():
    """Must not add @ts-nocheck or inline lint suppressions."""
    src = Path(TARGET).read_text()
    assert "@ts-nocheck" not in src, "Found @ts-nocheck — fix root cause instead"
    assert "eslint-disable" not in src, "Found eslint-disable suppression"


# [agent_config] pass_to_pass — CLAUDE.md:108 @ 4752aca926624efdeb62f2f43b606f5090be8903
def test_no_sdk_self_import():
    """Extension must not self-import via openclaw/plugin-sdk/msteams.

    CLAUDE.md:108 — inside an extension package, do not import that same
    extension via openclaw/plugin-sdk/<extension> from production files.
    """
    ext_dir = os.path.join(REPO, "extensions/msteams/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    if re.search(
                        r"^import .* from ['\"]openclaw/plugin-sdk/msteams",
                        line,
                    ):
                        violations.append(f"{filepath}:{i}: {line.strip()}")

    assert not violations, (
        "SDK self-import found in msteams extension:\n" + "\n".join(violations[:5])
    )
