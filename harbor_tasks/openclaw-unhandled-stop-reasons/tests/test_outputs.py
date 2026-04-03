"""
Task: openclaw-unhandled-stop-reasons
Repo: openclaw/openclaw @ 664680318eea98172c7d25405c20f5e3eadfd0e2
PR:   56639

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/openclaw"
RECOVERY_MODULE = "src/agents/pi-embedded-runner/run/attempt.stop-reason-recovery.ts"
ATTEMPT_MODULE = "src/agents/pi-embedded-runner/run/attempt.ts"


def _run_node(script: str, timeout: int = 15) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _build_extraction_preamble() -> str:
    """Extract pure functions from the recovery module for direct testing.

    We strip TS-only syntax so Node can eval the function bodies.
    AST-only because: module imports @mariozechner/pi-agent-core, pi-ai, and
    stream-message-shared which are not installed in the test container.
    """
    return textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync('%s/%s', 'utf8');

        // Strip TS-only syntax so Node can eval function bodies
        function stripTS(code) {
            return code
                .replace(/import\\s+.*?from\\s+['"][^'"]+['"];?/g, '')
                .replace(/export\\s+/g, '')
                .replace(/:\\s*[A-Za-z][\\w<>\\[\\]|&?, ]*(?=[)},;{=\\n])/g, '')
                .replace(/<[A-Z][\\w<>\\[\\]|&?, ]*>/g, '')
                .replace(/as\\s+const/g, '')
                .replace(/as\\s+\\{[^}]*\\}/g, '')
                .replace(/as\\s+unknown/g, '')
                .replace(/\\btype\\b\\s+\\w+/g, '')
                ;
        }

        function extractFn(name) {
            const re = new RegExp('function\\\\s+' + name + '\\\\s*(?:<[^>]*>)?\\\\s*\\\\(');
            const idx = src.search(re);
            if (idx === -1) throw new Error('Function ' + name + ' not found');
            let braces = 0, i = idx;
            while (i < src.length) {
                if (src[i] === '{') braces++;
                if (src[i] === '}') { braces--; if (braces === 0) { i++; break; } }
                i++;
            }
            return src.substring(idx, i);
        }

        // Extract the regex constant
        const reMatch = src.match(/const\\s+UNHANDLED_STOP_REASON_RE\\s*=\\s*\\/.*?\\/[gim]*;/);
        const reDecl = reMatch ? reMatch[0] : '';

        const formatFn = extractFn('formatUnhandledStopReasonErrorMessage');
        const normalizeFn = extractFn('normalizeUnhandledStopReasonMessage');
        const patchFn = extractFn('patchUnhandledStopReasonInAssistantMessage');

        const code = stripTS([reDecl, formatFn, normalizeFn, patchFn].join('\\n\\n'));
        eval(code);
    """) % (REPO, RECOVERY_MODULE)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_recovery_module_exists():
    """Recovery module file exists and exports the wrapper function."""
    p = Path(REPO) / RECOVERY_MODULE
    assert p.exists(), f"{RECOVERY_MODULE} does not exist"
    src = p.read_text()
    assert "wrapStreamFnHandleSensitiveStopReason" in src, (
        "Missing wrapStreamFnHandleSensitiveStopReason export"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_sync_throw_normalized():
    """normalizeUnhandledStopReasonMessage converts 'Unhandled stop reason: sensitive'
    into a user-friendly message mentioning 'sensitive'."""
    preamble = _build_extraction_preamble()
    script = preamble + textwrap.dedent("""\

        const result = normalizeUnhandledStopReasonMessage(
            'Unhandled stop reason: sensitive'
        );
        if (!result) {
            console.error('FAIL: returned undefined for matching input');
            process.exit(1);
        }
        if (!result.includes('sensitive')) {
            console.error('FAIL: result does not mention the stop reason: ' + result);
            process.exit(1);
        }
        if (!result.toLowerCase().includes('unhandled stop reason')) {
            console.error('FAIL: result does not explain the problem: ' + result);
            process.exit(1);
        }
        console.log('OK: ' + result);
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_varied_stop_reasons():
    """normalizeUnhandledStopReasonMessage works for multiple stop reason values."""
    preamble = _build_extraction_preamble()
    script = preamble + textwrap.dedent("""\

        const reasons = ['sensitive', 'refusal_policy', 'unknown_xyz', 'content_filter', 'safety'];
        for (const reason of reasons) {
            const msg = 'Unhandled stop reason: ' + reason;
            const result = normalizeUnhandledStopReasonMessage(msg);
            if (!result) {
                console.error('FAIL: returned undefined for: ' + msg);
                process.exit(1);
            }
            if (!result.includes(reason)) {
                console.error('FAIL: result missing reason "' + reason + '": ' + result);
                process.exit(1);
            }
        }
        // Also verify case-insensitive matching
        const upper = normalizeUnhandledStopReasonMessage('UNHANDLED STOP REASON: CaseMixed');
        if (!upper || !upper.includes('CaseMixed')) {
            console.error('FAIL: case-insensitive match failed');
            process.exit(1);
        }
        console.log('OK: all reasons handled');
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"


# [pr_diff] fail_to_pass
def test_patch_mutates_assistant_message():
    """patchUnhandledStopReasonInAssistantMessage rewrites errorMessage and sets
    stopReason to 'error' on a matching assistant message object."""
    preamble = _build_extraction_preamble()
    script = preamble + textwrap.dedent("""\

        // Test with 'sensitive'
        const msg1 = {
            role: 'assistant',
            errorMessage: 'Unhandled stop reason: sensitive',
            stopReason: 'unknown',
        };
        patchUnhandledStopReasonInAssistantMessage(msg1);
        if (msg1.stopReason !== 'error') {
            console.error('FAIL: stopReason not set to error: ' + msg1.stopReason);
            process.exit(1);
        }
        if (!msg1.errorMessage.includes('sensitive')) {
            console.error('FAIL: errorMessage not rewritten: ' + msg1.errorMessage);
            process.exit(1);
        }
        if (msg1.errorMessage === 'Unhandled stop reason: sensitive') {
            console.error('FAIL: errorMessage unchanged (should be user-friendly)');
            process.exit(1);
        }

        // Test with 'refusal_policy'
        const msg2 = {
            role: 'assistant',
            errorMessage: 'Unhandled stop reason: refusal_policy',
            stopReason: 'end_turn',
        };
        patchUnhandledStopReasonInAssistantMessage(msg2);
        if (msg2.stopReason !== 'error') {
            console.error('FAIL: stopReason not set to error for refusal_policy');
            process.exit(1);
        }
        if (!msg2.errorMessage.includes('refusal_policy')) {
            console.error('FAIL: errorMessage missing refusal_policy');
            process.exit(1);
        }

        console.log('OK: ' + JSON.stringify(msg1) + ' | ' + JSON.stringify(msg2));
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — non-matching errors pass through
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_nonmatching_errors_ignored():
    """normalizeUnhandledStopReasonMessage returns undefined for non-matching strings."""
    preamble = _build_extraction_preamble()
    script = preamble + textwrap.dedent("""\

        const inputs = [
            'Network timeout',
            'Connection refused',
            'Rate limit exceeded',
            '',
            'Some other error with stop in it',
            'Handled stop reason: end_turn',
            'stop reason sensitive',
        ];
        for (const input of inputs) {
            const result = normalizeUnhandledStopReasonMessage(input);
            if (result !== undefined) {
                console.error('FAIL: should be undefined for: ' + input + ', got: ' + result);
                process.exit(1);
            }
        }
        // Also test non-string inputs
        for (const input of [null, undefined, 42, {}, []]) {
            const result = normalizeUnhandledStopReasonMessage(input);
            if (result !== undefined) {
                console.error('FAIL: should be undefined for non-string: ' + input);
                process.exit(1);
            }
        }
        console.log('OK: all non-matching inputs returned undefined');
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"


# [pr_diff] pass_to_pass
def test_patch_skips_nonmatching_message():
    """patchUnhandledStopReasonInAssistantMessage leaves non-matching messages untouched."""
    preamble = _build_extraction_preamble()
    script = preamble + textwrap.dedent("""\

        const msg = {
            role: 'assistant',
            errorMessage: 'Some other error',
            stopReason: 'end_turn',
        };
        patchUnhandledStopReasonInAssistantMessage(msg);

        if (msg.stopReason !== 'end_turn') {
            console.error('FAIL: stopReason changed: ' + msg.stopReason);
            process.exit(1);
        }
        if (msg.errorMessage !== 'Some other error') {
            console.error('FAIL: errorMessage changed: ' + msg.errorMessage);
            process.exit(1);
        }
        // Also test with non-object inputs (should not crash)
        patchUnhandledStopReasonInAssistantMessage(null);
        patchUnhandledStopReasonInAssistantMessage(undefined);
        patchUnhandledStopReasonInAssistantMessage('string');
        patchUnhandledStopReasonInAssistantMessage(42);
        console.log('OK: non-matching messages untouched');
    """)
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — integration with attempt.ts
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: attempt.ts imports dozens of heavy deps (pi-agent-core,
# pi-ai, etc.) that are not installed in the test container.
def test_attempt_wires_wrapper():
    """attempt.ts imports the recovery module and applies the wrapper to streamFn."""
    p = Path(REPO) / ATTEMPT_MODULE
    assert p.exists(), f"{ATTEMPT_MODULE} does not exist"
    src = p.read_text()

    assert "stop-reason-recovery" in src, (
        "attempt.ts does not import the stop-reason-recovery module"
    )
    assert "wrapStreamFnHandleSensitiveStopReason" in src, (
        "attempt.ts does not reference wrapStreamFnHandleSensitiveStopReason"
    )
    # Verify the wrapper is applied to streamFn (not just imported)
    assert "wrapStreamFnHandleSensitiveStopReason(" in src, (
        "wrapStreamFnHandleSensitiveStopReason is imported but never called"
    )


# ---------------------------------------------------------------------------
# Anti-stub (static, pass_to_pass)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: module imports @mariozechner/pi-agent-core, pi-ai which
# are not installed in the test container.
def test_not_stub():
    """Recovery module has real logic (regex, try/catch, re-throw, stream handling)."""
    src = (Path(REPO) / RECOVERY_MODULE).read_text()
    lines = [l for l in src.splitlines()
             if l.strip() and not l.strip().startswith("//") and not l.strip().startswith("*")]
    assert len(lines) > 40, f"Module too short ({len(lines)} non-comment lines) — likely a stub"
    assert "catch" in src, "No catch block found"
    assert "throw" in src, "No re-throw found"
    # Must handle both stream events and sync throws
    assert "Symbol.asyncIterator" in src or "asyncIterator" in src, "Missing async iterator handling"
    assert "normalizeUnhandledStopReasonMessage" in src, "Missing normalize function"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:104 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_no_ts_nocheck():
    """Modified files must not contain @ts-nocheck or @ts-ignore (CLAUDE.md:104)."""
    targets = [RECOVERY_MODULE, ATTEMPT_MODULE]
    violations = []
    for t in targets:
        p = Path(REPO) / t
        if not p.exists():
            continue
        content = p.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            if "@ts-nocheck" in line or "@ts-ignore" in line:
                violations.append(f"{t}:{i}: {line.strip()}")
    assert not violations, "Found @ts-nocheck/@ts-ignore:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — CLAUDE.md:104 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_no_lint_suppressions():
    """Modified files must not contain inline lint suppression comments (CLAUDE.md:104)."""
    suppression_patterns = [
        r"eslint-disable",
        r"oxlint-ignore",
        r"tslint:disable",
    ]
    targets = [RECOVERY_MODULE, ATTEMPT_MODULE]
    violations = []
    for t in targets:
        p = Path(REPO) / t
        if not p.exists():
            continue
        content = p.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            for pattern in suppression_patterns:
                if re.search(pattern, line):
                    violations.append(f"{t}:{i}: {line.strip()}")
    assert not violations, "Found lint suppressions:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — CLAUDE.md:111 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_no_prototype_mutation():
    """Modified files must not share behavior via prototype mutation (CLAUDE.md:111)."""
    mutation_patterns = [
        r"\.prototype\.",
        r"Object\.defineProperty\([^,]+\.prototype",
        r"applyPrototypeMixins",
    ]
    targets = [RECOVERY_MODULE]
    violations = []
    for t in targets:
        p = Path(REPO) / t
        if not p.exists():
            continue
        content = p.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            for pattern in mutation_patterns:
                if re.search(pattern, line):
                    violations.append(f"{t}:{i}: {line.strip()}")
    assert not violations, "Found prototype mutation:\n" + "\n".join(violations)


# [agent_config] pass_to_pass — CLAUDE.md:102 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_esm_imports_only():
    """Recovery module must use ESM imports, not CommonJS require() (CLAUDE.md:102)."""
    p = Path(REPO) / RECOVERY_MODULE
    assert p.exists(), f"{RECOVERY_MODULE} does not exist"
    content = p.read_text()
    # Check for CommonJS patterns
    cjs_patterns = [
        (r'\brequire\s*\(', "require()"),
        (r'\bmodule\.exports\b', "module.exports"),
        (r'\bexports\.\w+', "exports.*"),
    ]
    violations = []
    for i, line in enumerate(content.splitlines(), 1):
        # Skip comments
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        for pattern, desc in cjs_patterns:
            if re.search(pattern, line):
                violations.append(f"{RECOVERY_MODULE}:{i}: {desc} — {stripped}")
    assert not violations, "Found CommonJS patterns (must use ESM):\n" + "\n".join(violations)


# [agent_config] pass_to_pass — CLAUDE.md:116 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_file_size_limit():
    """Recovery module must stay under ~700 LOC (CLAUDE.md:116)."""
    p = Path(REPO) / RECOVERY_MODULE
    assert p.exists(), f"{RECOVERY_MODULE} does not exist"
    loc = len(p.read_text().splitlines())
    assert loc <= 700, f"{RECOVERY_MODULE} is {loc} lines (limit ~700)"


# [agent_config] pass_to_pass — CLAUDE.md:106 @ 664680318eea98172c7d25405c20f5e3eadfd0e2
def test_no_dynamic_import_mixing():
    """Modified files must not use dynamic await import() alongside static imports
    for the same module (CLAUDE.md:106 dynamic import guardrail)."""
    targets = [RECOVERY_MODULE, ATTEMPT_MODULE]
    violations = []
    for t in targets:
        p = Path(REPO) / t
        if not p.exists():
            continue
        content = p.read_text()
        for i, line in enumerate(content.splitlines(), 1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            if re.search(r'\bawait\s+import\s*\(', line):
                violations.append(f"{t}:{i}: {stripped}")
    assert not violations, (
        "Found dynamic await import() in production files that use static imports "
        "(violates CLAUDE.md:106 dynamic import guardrail):\n" + "\n".join(violations)
    )
