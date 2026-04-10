"""
Task: openclaw-debounce-null-text
Repo: openclaw/openclaw @ 756df2e9554da097679e6c4d3c75deff025098b9
PR:   56573

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import textwrap
from pathlib import Path
import os

REPO = "/workspace/openclaw"
TARGET = "extensions/bluebubbles/src/monitor-debounce.ts"


def _read_target() -> str:
    """Read the target file contents."""
    p = Path(REPO) / TARGET
    assert p.exists(), f"{TARGET} does not exist"
    return p.read_text()


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    """Run a node script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _run_ts_script(ts_code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write TypeScript code to a temp file and run it with --experimental-strip-types."""
    import tempfile
    import os

    # Write the TS code to a temp file
    fd, path = tempfile.mkstemp(suffix='.ts', dir='/tmp')
    try:
        os.write(fd, ts_code.encode('utf-8'))
        os.close(fd)

        # Run with node --experimental-strip-types
        return subprocess.run(
            ["node", "--experimental-strip-types", path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    finally:
        try:
            os.unlink(path)
        except:
            pass


def _build_test_script(test_body: str) -> str:
    """Build a complete TypeScript test script that can run standalone.

    This approach reads the source file and creates a minimal test harness
    by keeping only the function declarations and type definitions, replacing
    the imports with minimal mock types.
    """
    src = _read_target()

    # Create a minimal version of the file with mock types replacing imports
    # Keep everything after the imports but replace the import statements
    lines = src.split('\n')
    result_lines = []

    # Skip import lines - we'll provide mock types
    in_import = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('import '):
            continue
        result_lines.append(line)

    modified_src = '\n'.join(result_lines)

    # Add mock type definitions at the top
    mock_types = '''// Mock type definitions for testing
type NormalizedWebhookMessage = {
  text: string | null | undefined;
  senderId: string;
  senderIdExplicit: boolean;
  isGroup: boolean;
  messageId: string;
  timestamp: number;
  attachments?: any[];
  chatGuid?: string;
  chatIdentifier?: string;
  chatId?: string | number;
  balloonBundleId?: string;
  associatedMessageGuid?: string;
  fromMe?: boolean;
  replyToId?: string;
  replyToBody?: string;
  replyToSender?: string;
};

type BlueBubblesDebounceEntry = {
  message: NormalizedWebhookMessage;
  target: { channelId: string };
};

type WebhookTarget = any;
type BlueBubblesCoreRuntime = any;
type OpenClawConfig = any;

// Stub for core dependency used in resolveBlueBubblesDebounceMs
const core = { channel: { debounce: { resolveInboundDebounceMs: () => 500 } } };

'''

    # Now we need to extract only the functions we need plus any supporting types
    # Find the three functions and the DEFAULT_INBOUND_DEBOUNCE_MS constant
    import re

    def extract_until_matching_brace(start_pattern: str, src: str) -> str:
        """Extract code from start_pattern to the matching closing brace."""
        match = re.search(start_pattern, src)
        if not match:
            return ''

        start = match.start()
        i = match.end()

        # Find first opening brace
        while i < len(src) and src[i] != '{':
            i += 1
        if i >= len(src):
            return ''

        # Count braces
        brace_depth = 0
        while i < len(src):
            if src[i] == '{':
                brace_depth += 1
            elif src[i] == '}':
                brace_depth -= 1
                if brace_depth == 0:
                    return src[start:i+1]
            i += 1
        return ''

    # Extract each function
    normalize_fn = extract_until_matching_brace(
        r'function\s+normalizeDebounceMessageText\s*\(', src)
    sanitize_fn = extract_until_matching_brace(
        r'function\s+sanitizeDebounceEntry\s*\(', src)
    combine_fn = extract_until_matching_brace(
        r'function\s+combineDebounceEntries\s*\(', src)

    # Also extract the DEFAULT_INBOUND_DEBOUNCE_MS constant
    debounce_ms_match = re.search(r'const\s+DEFAULT_INBOUND_DEBOUNCE_MS\s*=\s*\d+;', src)
    debounce_ms = debounce_ms_match.group(0) if debounce_ms_match else 'const DEFAULT_INBOUND_DEBOUNCE_MS = 500;'

    # Build the test script
    return mock_types + '\n' + debounce_ms + '\n\n' + normalize_fn + '\n\n' + sanitize_fn + '\n\n' + combine_fn + '\n' + test_body


def _ensure_deps_installed() -> None:
    """Ensure pnpm dependencies are installed."""
    node_modules = Path(REPO) / "node_modules"
    if not node_modules.exists():
        # Install dependencies
        subprocess.run(
            ["bash", "-c", "cd /workspace/openclaw && corepack enable && corepack prepare pnpm@latest --activate && pnpm install --frozen-lockfile"],
            capture_output=True, text=True, timeout=180, check=True
        )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_file_parses():
    """Target file must be readable and contain combineDebounceEntries."""
    src = _read_target()
    assert "combineDebounceEntries" in src, "combineDebounceEntries function not found"
    r = _run_node(f"require('fs').readFileSync('{REPO}/{TARGET}', 'utf8'); console.log('OK')")
    assert r.returncode == 0, f"File not readable: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_null_text_no_crash():
    """combineDebounceEntries must not crash when entries have null/undefined text.

    Uses multi-entry batches to trigger the combine path where .text.trim() is called.
    """
    test_body = textwrap.dedent("""
        function mkEntry(text: any, id: string, ts: number): BlueBubblesDebounceEntry {
            return {
                message: {
                    text: text, senderId: '+15551234567', senderIdExplicit: true,
                    isGroup: false, messageId: id, timestamp: ts,
                    attachments: []
                },
                target: { channelId: 'ch1' }
            };
        }

        // Multi-entry batches exercise the .trim() code path
        const cases = [
            { entries: [mkEntry(null, 'a', 1000), mkEntry(null, 'b', 2000)], label: 'two-nulls' },
            { entries: [mkEntry(undefined, 'c', 1000), mkEntry(undefined, 'd', 2000)], label: 'two-undefineds' },
            { entries: [mkEntry(null, 'e', 1000), mkEntry(undefined, 'f', 2000)], label: 'null+undefined' },
        ];

        for (const c of cases) {
            try {
                const result = combineDebounceEntries(c.entries);
                if (typeof result.text !== 'string') {
                    console.error('FAIL ' + c.label + ': result.text is ' + typeof result.text);
                    process.exit(1);
                }
            } catch (e: any) {
                console.error('CRASH on ' + c.label + ': ' + e.message);
                process.exit(1);
            }
        }
        console.log('OK');
    """)
    ts_script = _build_test_script(test_body)
    r = _run_ts_script(ts_script)
    assert r.returncode == 0, f"Crashed on null/undefined text entries: {r.stderr}"


# [pr_diff] fail_to_pass
def test_mixed_null_and_valid_entries():
    """Batch with null-text + valid-text entries combines without crash, valid text preserved."""
    test_body = textwrap.dedent("""
        function mkEntry(text: any, id: string, ts: number): BlueBubblesDebounceEntry {
            return {
                message: {
                    text: text, senderId: '+15551234567', senderIdExplicit: true,
                    isGroup: false, messageId: id, timestamp: ts,
                    attachments: []
                },
                target: { channelId: 'ch1' }
            };
        }

        // Case 1: null first, then valid
        const r1 = combineDebounceEntries([
            mkEntry(null, 'msg-null', 1000),
            mkEntry('Hello world', 'msg-valid', 2000),
        ]);
        if (!r1.text.includes('Hello world')) {
            console.error('FAIL case1: valid text lost, got: ' + r1.text);
            process.exit(1);
        }

        // Case 2: valid first, then null
        const r2 = combineDebounceEntries([
            mkEntry('Goodbye', 'msg-v2', 3000),
            mkEntry(null, 'msg-null2', 4000),
        ]);
        if (!r2.text.includes('Goodbye')) {
            console.error('FAIL case2: valid text lost, got: ' + r2.text);
            process.exit(1);
        }

        // Case 3: null sandwiched between two valid
        const r3 = combineDebounceEntries([
            mkEntry('Alpha', 'msg-a', 5000),
            mkEntry(null, 'msg-n', 6000),
            mkEntry('Bravo', 'msg-b', 7000),
        ]);
        if (!r3.text.includes('Alpha') || !r3.text.includes('Bravo')) {
            console.error('FAIL case3: texts lost, got: ' + r3.text);
            process.exit(1);
        }

        console.log('OK');
    """)
    ts_script = _build_test_script(test_body)
    r = _run_ts_script(ts_script)
    assert r.returncode == 0, f"Crashed or lost valid text: {r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_all_null_entries_produce_empty_text():
    """When all entries have null text, combined text is empty string (not crash)."""
    test_body = textwrap.dedent("""
        function mkNull(id: string, ts: number): BlueBubblesDebounceEntry {
            return {
                message: {
                    text: null, senderId: '+15551234567', senderIdExplicit: true,
                    isGroup: false, messageId: id, timestamp: ts,
                    attachments: []
                },
                target: { channelId: 'ch1' }
            };
        }

        // Case 1: two null entries
        const r1 = combineDebounceEntries([mkNull('a', 1000), mkNull('b', 2000)]);
        if (typeof r1.text !== 'string') {
            console.error('FAIL: text is not a string: ' + typeof r1.text);
            process.exit(1);
        }
        if (r1.text.trim() !== '') {
            console.error('FAIL: expected empty text, got: ' + JSON.stringify(r1.text));
            process.exit(1);
        }

        // Case 2: three null entries
        const r2 = combineDebounceEntries([mkNull('c', 3000), mkNull('d', 4000), mkNull('e', 5000)]);
        if (typeof r2.text !== 'string') {
            console.error('FAIL: text is not a string: ' + typeof r2.text);
            process.exit(1);
        }
        if (r2.text.trim() !== '') {
            console.error('FAIL: expected empty text for 3 nulls, got: ' + JSON.stringify(r2.text));
            process.exit(1);
        }

        console.log('OK');
    """)
    ts_script = _build_test_script(test_body)
    r = _run_ts_script(ts_script)
    assert r.returncode == 0, f"Crashed on all-null entries: {r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — valid entries still processed correctly
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_valid_entries_combine_text():
    """Multiple valid-text entries combine correctly (text joined, latest timestamp used)."""
    test_body = textwrap.dedent("""
        function mkEntry(text: string, id: string, ts: number): BlueBubblesDebounceEntry {
            return {
                message: {
                    text: text, senderId: '+15551234567', senderIdExplicit: true,
                    isGroup: false, messageId: id, timestamp: ts,
                    attachments: []
                },
                target: { channelId: 'ch1' }
            };
        }

        // Case 1: two entries
        const r1 = combineDebounceEntries([
            mkEntry('Hello', 'msg-1', 1000),
            mkEntry('World', 'msg-2', 2000),
        ]);
        if (!r1.text.includes('Hello') || !r1.text.includes('World')) {
            console.error('FAIL case1: text not combined: ' + JSON.stringify(r1.text));
            process.exit(1);
        }
        if (r1.timestamp !== 2000) {
            console.error('FAIL case1: timestamp not latest: ' + r1.timestamp);
            process.exit(1);
        }

        // Case 2: three entries
        const r2 = combineDebounceEntries([
            mkEntry('Alpha', 'msg-a', 500),
            mkEntry('Beta', 'msg-b', 1500),
            mkEntry('Gamma', 'msg-c', 3000),
        ]);
        if (!r2.text.includes('Alpha') || !r2.text.includes('Beta') || !r2.text.includes('Gamma')) {
            console.error('FAIL case2: text not combined: ' + JSON.stringify(r2.text));
            process.exit(1);
        }
        if (r2.timestamp !== 3000) {
            console.error('FAIL case2: timestamp not latest: ' + r2.timestamp);
            process.exit(1);
        }

        console.log('OK');
    """)
    ts_script = _build_test_script(test_body)
    r = _run_ts_script(ts_script)
    assert r.returncode == 0, f"Valid entry combination failed: {r.stderr}\n{r.stdout}"


# [pr_diff] pass_to_pass
def test_single_valid_entry_passthrough():
    """A single valid entry is returned as-is without mangling."""
    test_body = textwrap.dedent("""
        function mkEntry(text: string, id: string, ts: number, sender: string, isGroup: boolean): BlueBubblesDebounceEntry {
            return {
                message: {
                    text: text, senderId: sender, senderIdExplicit: true,
                    isGroup: isGroup, messageId: id, timestamp: ts,
                    attachments: []
                },
                target: { channelId: 'ch1' }
            };
        }

        // Case 1: basic message
        const r1 = combineDebounceEntries([mkEntry('Test message', 'msg-solo', 5000, '+15559876543', true)]);
        if (r1.text !== 'Test message') {
            console.error('FAIL case1: text mangled: ' + JSON.stringify(r1.text));
            process.exit(1);
        }
        if (r1.senderId !== '+15559876543') {
            console.error('FAIL case1: senderId changed');
            process.exit(1);
        }

        // Case 2: message with unicode
        const r2 = combineDebounceEntries([mkEntry('Hey! 🙋 How are you?', 'msg-emoji', 9000, '+15550001111', false)]);
        if (r2.text !== 'Hey! 🙋 How are you?') {
            console.error('FAIL case2: text mangled: ' + JSON.stringify(r2.text));
            process.exit(1);
        }

        // Case 3: message with only whitespace
        const r3 = combineDebounceEntries([mkEntry('   ', 'msg-ws', 100, '+15550002222', false)]);
        if (typeof r3.text !== 'string') {
            console.error('FAIL case3: text not a string');
            process.exit(1);
        }

        console.log('OK');
    """)
    ts_script = _build_test_script(test_body)
    r = _run_ts_script(ts_script)
    assert r.returncode == 0, f"Single entry passthrough failed: {r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified file has real debounce logic, not a stub."""
    src = _read_target()
    lines = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")]
    assert len(lines) > 30, f"File too short ({len(lines)} lines) — likely a stub"
    assert "combineDebounceEntries" in src, "combineDebounceEntries missing"
    assert "enqueue" in src, "enqueue method missing"
    assert "flushKey" in src or "flush" in src, "flush method missing"
    assert "debounce" in src.lower(), "No debounce logic found"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:16 @ 756df2e9554da097679e6c4d3c75deff025098b9
def test_no_cross_boundary_imports():
    """Extension code must not import core internals directly (AGENTS.md:16).

    Only checks the target file since that's what the agent modifies.
    """
    src = _read_target()
    violations = []
    for i, line in enumerate(src.splitlines(), 1):
        if 'from "' in line or "from '" in line:
            if "../../../src/" in line or "../../src/plugin-sdk-internal/" in line:
                violations.append(f"{TARGET}:{i}: {line.strip()}")
    assert not violations, "Cross-boundary imports found:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — AGENTS.md:104 @ 756df2e9554da097679e6c4d3c75deff025098b9
def test_no_ts_nocheck():
    """Must not add @ts-nocheck or blanket lint suppressions (AGENTS.md:104)."""
    src = _read_target()
    assert "@ts-nocheck" not in src, "Found @ts-nocheck in target file"
    for i, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if stripped in ("// eslint-disable", "// oxlint-disable"):
            assert False, f"Line {i}: blanket lint suppression: {stripped}"


# [agent_config] pass_to_pass — AGENTS.md:105 @ 756df2e9554da097679e6c4d3c75deff025098b9
def test_no_explicit_any_in_helpers():
    """New helper functions must not use explicit `any` type (AGENTS.md:105).

    normalizeDebounceMessageText and sanitizeDebounceEntry must use `unknown`
    or real types, not `any`.
    """
    import re

    src = _read_target()
    helper_names = ["normalizeDebounceMessageText", "sanitizeDebounceEntry"]
    for fn_name in helper_names:
        idx = src.find(f"function {fn_name}")
        if idx == -1:
            continue  # presence checked by other tests
        # Extract the function body by counting braces
        brace_count = 0
        started = False
        end = idx
        for i in range(idx, len(src)):
            if src[i] == "{":
                brace_count += 1
                started = True
            elif src[i] == "}":
                brace_count -= 1
                if started and brace_count == 0:
                    end = i + 1
                    break
        fn_body = src[idx:end]
        for line in fn_body.splitlines():
            stripped = line.strip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r":\s*any\b", line), (
                f"{fn_name}: explicit `: any` type found (AGENTS.md:105 — use `unknown` or real types):\n  {stripped}"
            )
            assert not re.search(r"\bas\s+any\b", line), (
                f"{fn_name}: `as any` cast found (AGENTS.md:105 — use `unknown` or real types):\n  {stripped}"
            )


# [agent_config] pass_to_pass — AGENTS.md:108 @ 756df2e9554da097679e6c4d3c75deff025098b9
def test_no_self_import_via_plugin_sdk():
    """Target file must not import itself via openclaw/plugin-sdk/bluebubbles (AGENTS.md:108).

    Only checks monitor-debounce.ts — runtime-api.ts is a legitimate barrel re-export file.
    """
    src = _read_target()
    violations = []
    for i, line in enumerate(src.splitlines(), 1):
        if "openclaw/plugin-sdk/bluebubbles" in line:
            violations.append(f"{TARGET}:{i}: {line.strip()}")
    assert not violations, (
        "Self-import via plugin-sdk found:\n" + "\n".join(violations)
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass_to_pass gates — discovered from .github/workflows/ci.yml
# ---------------------------------------------------------------------------

# [repo_ci] pass_to_pass
def test_repo_typescript_check():
    """Repo's TypeScript typecheck passes on target file (pass_to_pass).

    Uses pnpm tsgo (from oxlint-tsgolint package) for fast type checking.
    This ensures the fix doesn't introduce type errors.
    """
    _ensure_deps_installed()
    r = subprocess.run(
        ["./node_modules/.bin/tsgo", f"{REPO}/{TARGET}"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # tsgo returns 0 on success, but may return 2 if tsconfig.json is present
    # with files on command line (TS5112). We accept both 0 and 2 as success
    # as long as there are no actual type errors.
    if r.returncode not in (0, 2):
        assert False, f"TypeScript check failed with exit code {r.returncode}:\n{r.stderr}\n{r.stdout}"
    # Also verify no actual type errors in stderr (TS5xxx other than TS5112)
    for line in r.stderr.splitlines():
        if "error TS" in line and "TS5112" not in line:
            assert False, f"TypeScript error found: {line}\n{r.stderr}"


# [repo_ci] pass_to_pass
def test_repo_bluebubbles_tests():
    """BlueBubbles extension tests pass (pass_to_pass).

    Runs vitest on the bluebubbles extension tests to ensure the fix
    doesn't break existing functionality.
    """
    _ensure_deps_installed()
    r = subprocess.run(
        ["./node_modules/.bin/vitest", "run", "--config", "vitest.extensions.config.ts",
         "--reporter=verbose", "extensions/bluebubbles/src/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"BlueBubbles extension tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-500:]}"


# [repo_ci] pass_to_pass
def test_repo_lint():
    """Repo's oxlint passes on target file (pass_to_pass).

    Runs oxlint type-aware linting on the target file to ensure
    the fix doesn't introduce lint errors.
    """
    _ensure_deps_installed()
    r = subprocess.run(
        ["./node_modules/.bin/oxlint", "--type-aware", f"{REPO}/{TARGET}"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
