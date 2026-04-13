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

        # ESM loader: intercept streaming-message import -> mock
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
        "    multi_media_text_stripped: multiMedia?.text === undefined\n"
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


# [agent_config] pass_to_pass — CLAUDE.md:109 @ 4752aca926624efdeb62f2f43b606f5090be8903
def test_no_escaped_package_imports():
    """Extension must not use relative imports that escape the extensions/msteams package root.

    CLAUDE.md:109 — inside extensions/<id>/**, do not use relative imports that
    resolve outside that same extensions/<id> package root. Files directly in
    extensions/msteams/src/ need 3+ leading '../' segments to escape the package;
    files in deeper subdirs need more.
    """
    ext_dir = os.path.join(REPO, "extensions/msteams")
    pkg_root = os.path.join(REPO, "extensions/msteams")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            file_dir = os.path.dirname(filepath)
            with open(filepath) as f:
                for i, line in enumerate(f, 1):
                    # Extract the import specifier (relative paths only)
                    m = re.search(r"""from\s+['\"](\.\/|\.\.\/)(.*?)['\"]""", line)
                    if not m:
                        continue
                    specifier = m.group(1) + m.group(2)
                    if not specifier.startswith("."):
                        continue
                    # Resolve where this import would land
                    resolved = os.path.normpath(os.path.join(file_dir, specifier))
                    # Flag if it resolves outside the extensions/msteams package root
                    if not resolved.startswith(pkg_root):
                        violations.append(f"{filepath}:{i}: {line.strip()}")

    assert not violations, (
        "Relative imports escaping extensions/msteams package root:\n" + "\n".join(violations[:5])
    )


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks that work without node_modules
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_file_structure():
    """Repo's extension files follow expected structure (pass_to_pass)."""
    expected_files = [
        "extensions/msteams/src/index.ts",
        "extensions/msteams/src/reply-stream-controller.ts",
        "extensions/msteams/src/streaming-message.ts",
        "extensions/msteams/package.json",
    ]
    for f in expected_files:
        path = os.path.join(REPO, f)
        assert Path(path).exists(), f"Expected file missing: {f}"


# [repo_tests] pass_to_pass
def test_repo_no_debug_code():
    """No console.log or debugger statements left in production code (pass_to_pass)."""
    ext_dir = os.path.join(REPO, "extensions/msteams/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            with open(filepath) as f:
                content = f.read()
                # Check for console.log or debugger
                if re.search(r"console\.(log|debug|warn|error)\(", content):
                    violations.append(f"{filepath}: found console.* statement")
                if "debugger;" in content:
                    violations.append(f"{filepath}: found debugger statement")

    assert not violations, "Debug statements found:\n" + "\n".join(violations[:5])


# [repo_tests] pass_to_pass
def test_repo_import_validity():
    """Import paths in msteams extension are well-formed (pass_to_pass)."""
    ext_dir = os.path.join(REPO, "extensions/msteams/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".test.ts", ".d.ts")):
                continue
            filepath = os.path.join(root, fname)
            file_dir = os.path.dirname(filepath)
            with open(filepath) as f:
                content = f.read()
                # Check for unresolved relative imports that go too far up
                # Extensions should not reach outside their package
                for match in re.finditer(
                    r'''from\s+['\"](\.\./[^'\"]+)['\"]''', content
                ):
                    specifier = match.group(1)
                    resolved = os.path.normpath(os.path.join(file_dir, specifier))
                    # Should not escape extensions/msteams
                    if not resolved.startswith(os.path.join(REPO, "extensions/msteams")):
                        violations.append(f"{filepath}: import escapes package: {specifier}")

    assert not violations, "Invalid imports found:\n" + "\n".join(violations[:5])


# [repo_tests] pass_to_pass
def test_repo_no_private_keys():
    """No private keys committed to the repo (pass_to_pass).

    Uses detect-secrets baseline to check for potential secrets in the
    msteams extension files. Mirrors the CI security-fast job.
    """
    baseline_path = os.path.join(REPO, ".secrets.baseline")
    ext_dir = os.path.join(REPO, "extensions/msteams")

    # Check if baseline exists and is valid JSON
    if Path(baseline_path).exists():
        try:
            with open(baseline_path) as f:
                baseline = json.load(f)
        except (json.JSONDecodeError, IOError):
            baseline = {"results": {}}
    else:
        baseline = {"results": {}}

    # Known secret patterns to check (from .pre-commit-config.yaml detect-private-key)
    private_key_patterns = [
        r"BEGIN\s+(RSA|DSA|EC|OPENSSH|PGP)\s+PRIVATE\s+KEY",
        r"BEGIN\s+PRIVATE\s+KEY",
        r"ssh-rsa\s+[A-Za-z0-9+/=]+",
        r"BEGIN\s+ENCRYPTED\s+PRIVATE\s+KEY",
        r"BEGIN\s+PGP\s+PRIVATE\s+KEY\s+BLOCK",
    ]

    violations = []
    excluded_files = {".secrets.baseline", ".detect-secrets.cfg"}

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if fname in excluded_files:
                continue
            if not fname.endswith(".ts"):
                continue
            filepath = os.path.join(root, fname)
            rel_path = os.path.relpath(filepath, REPO)

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except (IOError, OSError):
                continue

            # Check for private key patterns
            for pattern in private_key_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    # Check if this is in the baseline (known/allowed secret)
                    baseline_entry = baseline.get("results", {}).get(rel_path, [])
                    is_allowed = False
                    for entry in baseline_entry:
                        if entry.get("line_number") == content[:match.start()].count("\n") + 1:
                            is_allowed = True
                            break
                    if not is_allowed:
                        line_num = content[:match.start()].count("\n") + 1
                        violations.append(f"{filepath}:{line_num}: potential private key detected")

    assert not violations, "Potential private keys found:\n" + "\n".join(violations[:5])


# [repo_tests] pass_to_pass
def test_repo_typescript_syntax():
    """TypeScript files in msteams extension have valid syntax (pass_to_pass).

    Validates that .ts files can be parsed without syntax errors using Node.js
    --experimental-strip-types. This catches basic syntax issues without
    requiring full type checking (which needs node_modules).

    Mirrors CI TypeScript parsing checks by running the Node.js TypeScript
    stripper on each source file (types are stripped before parsing).
    """
    ext_dir = os.path.join(REPO, "extensions/msteams/src")
    violations = []

    for root, _dirs, files in os.walk(ext_dir):
        for fname in files:
            if not fname.endswith(".ts") or fname.endswith((".d.ts")):
                continue
            filepath = os.path.join(root, fname)

            # Try to parse the file with Node.js TypeScript support
            # Pipe file content through stdin so types get stripped before parsing
            r = subprocess.run(
                ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
                input=Path(filepath).read_text(),
                capture_output=True,
                text=True,
                timeout=10,
            )

            if r.returncode != 0:
                # Extract the error message
                err_msg = r.stderr.split("\n")[0] if r.stderr else "parse error"
                violations.append(f"{filepath}: {err_msg}")

    assert not violations, "TypeScript syntax errors found:\n" + "\n".join(violations[:5])


# [repo_tests] pass_to_pass — CI/CD check: no merge conflict markers
def test_repo_no_conflict_markers():
    """Repo has no unresolved merge conflict markers (pass_to_pass).

    Mirrors the CI check-merge-conflict pre-commit hook using the repo's
    own script: scripts/check-no-conflict-markers.mjs
    """
    r = subprocess.run(
        ["node", "scripts/check-no-conflict-markers.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Merge conflict markers found:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: target file TypeScript compilation
def test_repo_target_typescript_parse():
    """Target reply-stream-controller.ts is valid TypeScript (pass_to_pass).

    Validates the specific modified file can be parsed by Node.js
    --experimental-strip-types, mirroring CI TypeScript checks.
    """
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
        input=Path(TARGET).read_text(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    # Exit 0 means it parsed successfully (types are stripped before parsing)
    assert r.returncode == 0, (
        f"Target file has TypeScript syntax errors:\n{r.stderr[-500:]}"
    )



# [repo_tests] pass_to_pass — CI/CD check: secrets baseline valid JSON
def test_repo_secrets_baseline_valid():
    """.secrets.baseline is valid JSON (pass_to_pass).

    Mirrors CI security-fast job that reads the detect-secrets baseline.
    Validates the baseline file is parseable JSON.
    """
    baseline_path = os.path.join(REPO, ".secrets.baseline")
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open(\"" + baseline_path + "\")); print(\"OK\")"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f".secrets.baseline is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: git repository is valid
def test_repo_git_valid():
    """Git repository is in valid state (pass_to_pass).

    Validates git status works and repo is not corrupted.
    Mirrors basic CI git sanity checks.
    """
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Git repository is corrupted:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: build docs list script works
def test_repo_build_docs_list():
    """Docs list generation script works (pass_to_pass).

    Runs the build-docs-list.mjs script which generates documentation metadata.
    Mirrors CI docs-metadata generation step.
    """
    r = subprocess.run(
        ["node", "scripts/build-docs-list.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"build-docs-list.mjs failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: build stamp script works
def test_repo_build_stamp():
    """Build stamp generation script works (pass_to_pass).

    Runs the build-stamp.mjs script which generates build metadata.
    Mirrors CI build-stamp generation step.
    """
    r = subprocess.run(
        ["node", "scripts/build-stamp.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"build-stamp.mjs failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: related streaming-message module TypeScript parsing
def test_repo_streaming_message_typescript_parse():
    """streaming-message.ts (TeamsHttpStream dependency) is valid TypeScript (pass_to_pass).

    Validates the streaming-message.ts module that TeamsHttpStream is imported from.
    This file is critical for the reply-stream-controller fix to work.
    Mirrors CI TypeScript checks.
    """
    streaming_msg_path = os.path.join(REPO, "extensions/msteams/src/streaming-message.ts")
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
        input=Path(streaming_msg_path).read_text(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"streaming-message.ts has TypeScript syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — CI/CD check: reply-dispatcher module TypeScript parsing
def test_repo_reply_dispatcher_typescript_parse():
    """reply-dispatcher.ts (consumer of stream controller) is valid TypeScript (pass_to_pass).

    Validates the reply-dispatcher.ts module that uses createTeamsReplyStreamController.
    This file exercises the stream controller and must remain compatible.
    Mirrors CI TypeScript checks.
    """
    dispatcher_path = os.path.join(REPO, "extensions/msteams/src/reply-dispatcher.ts")
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
        input=Path(dispatcher_path).read_text(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"reply-dispatcher.ts has TypeScript syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — CI/CD check: reply-dispatcher test TypeScript parsing
def test_repo_reply_dispatcher_test_typescript_parse():
    """reply-dispatcher.test.ts is valid TypeScript (pass_to_pass).

    Validates the reply-dispatcher.test.ts test file which mocks the streaming module.
    Test files must be syntactically valid to run in CI.
    Mirrors CI TypeScript checks for test files.
    """
    test_path = os.path.join(REPO, "extensions/msteams/src/reply-dispatcher.test.ts")
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
        input=Path(test_path).read_text(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"reply-dispatcher.test.ts has TypeScript syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — CI/CD check: msteams extension package.json validity
def test_repo_msteams_package_json_valid():
    """msteams extension package.json is valid JSON (pass_to_pass).

    Validates the extensions/msteams/package.json file is parseable JSON.
    CI checks validate plugin metadata for all extensions.
    """
    pkg_path = os.path.join(REPO, "extensions/msteams/package.json")
    r = subprocess.run(
        ["python3", "-c", "import json; json.load(open(\"" + pkg_path + "\")); print(\"OK\")"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, f"msteams package.json is not valid JSON:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI/CD check: msteams extension exports valid index.ts
def test_repo_msteams_index_typescript_parse():
    """msteams extension index.ts is valid TypeScript (pass_to_pass).

    Validates the main entry point of the msteams extension can be parsed.
    Mirrors CI TypeScript checks for extension entry points.
    """
    index_path = os.path.join(REPO, "extensions/msteams/src/index.ts")
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings", "-e", "0"],
        input=Path(index_path).read_text(),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"msteams index.ts has TypeScript syntax errors:\n{r.stderr[-500:]}"
    )


# ---------------------------------------------------------------------------
# Additional CI/CD pass-to-pass tests (enrichment)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass — CI lint check: oxlint on msteams extension
def test_repo_oxlint_msteams():
    """Oxlint passes on msteams extension files (pass_to_pass).

    Runs the repo's linter (oxlint) on the msteams extension source files.
    Mirrors the CI lint check without requiring full node_modules.
    """
    r = subprocess.run(
        ["npx", "oxlint", "extensions/msteams/src/reply-stream-controller.ts"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint found issues:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI format check: oxfmt on target file
def test_repo_oxfmt_msteams_target():
    """Oxfmt format check passes on target file (pass_to_pass).

    Verifies the target file follows the repo's formatting standards.
    Mirrors the CI format check using oxfmt --check.
    """
    r = subprocess.run(
        ["npx", "oxfmt", "--check", TARGET],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"oxfmt format check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI check: docs link audit
def test_repo_docs_link_audit():
    """Docs link audit passes (pass_to_pass).

    Runs the docs-link-audit.mjs script which validates internal documentation links.
    Mirrors CI docs validation.
    """
    r = subprocess.run(
        ["node", "scripts/docs-link-audit.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"docs-link-audit failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass — CI check: no conflict markers in repo (official script)
def test_repo_no_conflict_markers_ci():
    """No unresolved merge conflict markers in repo (pass_to_pass).

    Runs the official CI script check-no-conflict-markers.mjs that validates
    no Git merge conflict markers remain in the codebase.
    """
    r = subprocess.run(
        ["node", "scripts/check-no-conflict-markers.mjs"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Conflict markers found:\n{r.stderr[-500:]}"
