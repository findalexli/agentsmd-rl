"""
Task: openclaw-telegram-empty-reply-crash
Repo: openclaw/openclaw @ eec290e68d6191b4bb85538dd301d50cdbc6650a
PR:   56620

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/openclaw"
TARGET = "extensions/telegram/src/bot/delivery.replies.ts"
TARGET_PATH = f"{REPO}/{TARGET}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_target() -> str:
    return Path(TARGET_PATH).read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_filter_removes_empty_and_whitespace():
    """Filter function correctly removes empty/whitespace-only text chunks."""
    # Use Node.js to extract the filter function and test it behaviorally
    # with diverse inputs. This is a TypeScript file so we execute via Node.
    # AST-only because: TypeScript generics cannot be executed by Python directly;
    # we extract the function body as plain JS and eval it via Node.
    script = r"""
const fs = require('fs');
// argv[2] is the TypeScript source file path (argv[1] is this script)
const src = fs.readFileSync(process.argv[2], 'utf8');

// Find standalone filter function (handles TS generics)
// Must be filterEmptyTelegramTextChunks specifically - the fallback check was
// removed because it was matching unrelated trim() calls in the base code
const funcRegex = /function\s+(filterEmptyTelegramTextChunks)\s*(?:<[^>]*>)?\s*\((\w+)\s*:[^)]*\)\s*(?::[^{]*)?\s*\{([\s\S]*?)\n\}/;
const m = src.match(funcRegex);
if (!m) {
    console.error('No filterEmptyTelegramTextChunks function found');
    process.exit(1);
}

// Rebuild as plain JS function (strip TS types from param)
const [, name, param, body] = m;
let fn;
try {
    fn = new Function(param, body);
} catch (e) {
    console.error('Could not eval filter function: ' + e.message);
    process.exit(1);
}

// Test with varied inputs — agents that hardcode for one case will fail others
const tests = [
    { input: [{text: ''}], expected: 0, label: 'empty string' },
    { input: [{text: '   '}], expected: 0, label: 'spaces only' },
    { input: [{text: '\t\n'}], expected: 0, label: 'tab+newline' },
    { input: [{text: '\r\n  \t'}], expected: 0, label: 'mixed whitespace' },
    { input: [{text: 'hello'}], expected: 1, label: 'normal text' },
    { input: [{text: ''}, {text: 'world'}, {text: '  '}], expected: 1, label: 'mixed: 1 valid of 3' },
    { input: [{text: 'a'}, {text: 'b'}], expected: 2, label: 'two valid' },
    { input: [{text: 'x'}, {text: ' '}, {text: 'y'}, {text: ''}], expected: 2, label: 'two valid of four' },
    { input: [], expected: 0, label: 'empty array' },
    { input: [{text: ' hi '}], expected: 1, label: 'text with surrounding spaces kept' },
];

let failed = 0;
for (const t of tests) {
    const res = fn(t.input);
    if (!Array.isArray(res)) {
        console.error('FAIL [' + t.label + ']: filter did not return an array');
        failed++;
        continue;
    }
    if (res.length !== t.expected) {
        console.error('FAIL [' + t.label + ']: got ' + res.length + ', expected ' + t.expected);
        failed++;
    }
}
if (failed > 0) {
    console.error(failed + ' of ' + tests.length + ' filter tests failed');
    process.exit(1);
}
console.log('All ' + tests.length + ' filter tests passed');
"""
    fd, path = tempfile.mkstemp(suffix=".js")
    try:
        os.write(fd, script.encode())
        os.close(fd)
        r = subprocess.run(
            ["node", path, TARGET_PATH],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"Filter test failed:\n{r.stdout.decode()}\n{r.stderr.decode()}"
        )
    finally:
        os.unlink(path)


# [pr_diff] fail_to_pass
def test_all_delivery_paths_protected():
    """All 3 text delivery paths filter empty/whitespace chunks before sending."""
    src = _read_target()

    # Verify all 3 delivery functions exist
    delivery_funcs = [
        "deliverTextReply",
        "sendPendingFollowUpText",
        "sendTelegramVoiceFallbackText",
    ]
    for func_name in delivery_funcs:
        assert re.search(rf"\bfunction\s+{func_name}\b", src), (
            f"Function {func_name} not found in {TARGET}"
        )

    # Count named filter-function call sites (the definition uses `<` not `(` so
    # it won't match this pattern — only the 3 call sites do).
    # Accept both a named helper and inline .filter(... .trim() ...) approaches.
    named_filter_calls = len(re.findall(r"\b\w*[Ff]ilter\w*Empty\w*\(|\bfilterEmpty\w+\(", src))
    inline_trim_filters = len(re.findall(r"\.filter\([^)]*\.trim\(\)", src))

    total_filter_calls = named_filter_calls + inline_trim_filters
    assert total_filter_calls >= 3, (
        f"Expected filter calls for all 3 delivery paths, "
        f"found {total_filter_calls} (named={named_filter_calls}, inline={inline_trim_filters})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_core_delivery_logic_preserved():
    """Core delivery functions and send/progress patterns still exist."""
    src = _read_target()

    required = [
        (r"function\s+deliverTextReply", "deliverTextReply function"),
        (r"function\s+sendPendingFollowUpText", "sendPendingFollowUpText function"),
        (r"function\s+sendTelegramVoiceFallbackText", "sendTelegramVoiceFallbackText function"),
        (r"sendTelegramText", "sendTelegramText call"),
        (r"markDelivered", "markDelivered call"),
    ]

    for pattern, name in required:
        assert re.search(pattern, src), f"Missing required pattern: {name}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:16 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_cross_boundary_imports():
    """Extension code must not import core src/ internals (CLAUDE.md import boundary rule)."""
    src = _read_target()

    # Check for imports reaching into core src/ or another extension's src/
    bad_patterns = [
        (r'''from\s+['"][\.\./]{3}src/''', "relative import into core src/"),
        (r'''from\s+['"][\.\./]{4}src/''', "deep relative import into core src/"),
        (r'''import\s*\(.*['"][\.\./]{3}src/''', "dynamic import into core src/"),
    ]
    violations = []
    for pattern, desc in bad_patterns:
        matches = re.findall(pattern, src)
        if matches:
            violations.extend(f"{desc}: {m}" for m in matches)

    assert not violations, (
        "Cross-boundary imports violate CLAUDE.md:16 import boundary rule:\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — CLAUDE.md:102 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_any_type_annotation():
    """New code must avoid `any` type; use real types or `unknown` instead."""
    src = _read_target()

    # Find explicit `: any` or `as any` annotations — these violate strict typing.
    # Exclude comments (lines starting with // or inside /* */).
    violations = []
    in_block_comment = False
    for lineno, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if "/*" in stripped:
            in_block_comment = True
        if in_block_comment:
            if "*/" in stripped:
                in_block_comment = False
            continue
        if stripped.startswith("//"):
            continue
        # Match `: any`, `<any>`, `as any` but not words containing "any" like "anyOf"
        if re.search(r'(?::\s*any\b|<any\b|as\s+any\b)', line):
            violations.append(f"  line {lineno}: {stripped}")

    assert not violations, (
        "Uses `any` type (CLAUDE.md:102 — prefer strict typing):\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — CLAUDE.md:104 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_lint_suppressions():
    """Must not add @ts-nocheck or inline lint suppressions without justification."""
    src = _read_target()

    suppressions = []
    for lineno, line in enumerate(src.splitlines(), 1):
        stripped = line.strip()
        if re.search(r'@ts-nocheck', stripped):
            suppressions.append(f"  line {lineno}: @ts-nocheck")
        if re.search(r'@ts-ignore(?!\s*--\s*\w)', stripped):
            # Allow @ts-ignore with explanation comment
            if not re.search(r'@ts-ignore\s*[-—]\s*\S', stripped):
                suppressions.append(f"  line {lineno}: @ts-ignore without explanation")
        if re.search(r'eslint-disable(?!-next-line)', stripped):
            suppressions.append(f"  line {lineno}: eslint-disable (file-wide)")
        if re.search(r'oxlint-disable(?!-next-line)', stripped):
            suppressions.append(f"  line {lineno}: oxlint-disable (file-wide)")

    assert not suppressions, (
        "Lint suppressions violate CLAUDE.md:104:\n" + "\n".join(suppressions)
    )


# [agent_config] pass_to_pass — CLAUDE.md:109 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_extension_package_boundary():
    """Extension must not use relative imports that escape its package root."""
    src = _read_target()

    # extensions/telegram/src/bot/delivery.replies.ts is 4 dirs deep under extensions/telegram/
    # Any relative import with 3+ levels of ../ would escape the extension root
    escaping = re.findall(
        r'''(?:from|import\()\s*['"](\.\.\/\.\.\/\.\.\/[^'"]+)['"]''', src
    )
    assert not escaping, (
        "Relative imports escape extension package boundary (CLAUDE.md:109):\n"
        + "\n".join(escaping)
    )


# [agent_config] pass_to_pass — CLAUDE.md:108 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_extension_sdk_self_import():
    """Extension must not import itself via openclaw/plugin-sdk/telegram from production files."""
    src = _read_target()

    self_imports = re.findall(
        r'''(?:from|import\()\s*['"]openclaw/plugin-sdk/telegram[^'"]*['"]''', src
    )
    assert not self_imports, (
        "Self-import via plugin-sdk detected (CLAUDE.md:108):\n"
        + "\n".join(self_imports)
    )


# [agent_config] pass_to_pass — CLAUDE.md:111 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_prototype_mutation():
    """Must not share class behavior via prototype mutation."""
    src = _read_target()

    proto_patterns = [
        (r'applyPrototypeMixins', "applyPrototypeMixins call"),
        (r'Object\.definePropert(?:y|ies)\s*\([^)]*\.prototype', "Object.defineProperty on prototype"),
        (r'\.prototype\s*=', "prototype assignment"),
        (r'\.prototype\.\w+\s*=', "prototype property assignment"),
    ]

    violations = []
    for pattern, desc in proto_patterns:
        if re.search(pattern, src):
            violations.append(desc)

    assert not violations, (
        "Prototype mutation found (CLAUDE.md:111):\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — CLAUDE.md:228 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_streaming_partial_replies():
    """Must not send streaming/partial replies to Telegram — only final replies."""
    src = _read_target()

    # Check for streaming event patterns that should not dispatch to Telegram
    streaming_patterns = [
        (r'on\w*[Ss]tream', "streaming event handler"),
        (r'partial[Rr]eply', "partial reply dispatch"),
        (r'stream[Cc]hunk', "stream chunk send"),
    ]

    violations = []
    for pattern, desc in streaming_patterns:
        if re.search(pattern, src):
            violations.append(desc)

    # This is a pass_to_pass check — base code should not have streaming,
    # and fix should not introduce it
    assert not violations, (
        "Streaming/partial reply patterns found (CLAUDE.md:228):\n"
        + "\n".join(violations)
    )


# [agent_config] pass_to_pass — CLAUDE.md:106 @ eec290e68d6191b4bb85538dd301d50cdbc6650a
def test_no_dynamic_import_mixing():
    """Do not mix dynamic await import() and static import for the same module in production code."""
    src = _read_target()

    # Static import specifiers: `from 'x'` or side-effect `import 'x'`
    static_imports = set(re.findall(r"""(?:from|import)\s+['\"]([^'\"]+)['\"]""", src))

    # Dynamic import specifiers: import('x') — includes `await import(...)`
    dynamic_imports = set(re.findall(r"""(?<!\w)import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)""", src))

    mixed = static_imports & dynamic_imports
    assert not mixed, (
        "Same modules imported both statically and dynamically violates CLAUDE.md:106:\n"
        + "\n".join(sorted(mixed))
    )


# ---------------------------------------------------------------------------
# Repo CI/CD pass-to-pass tests — ensure base commit passes CI checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_telegram():
    """Repo's oxlint passes on telegram extension (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxlint", "--type-aware", "extensions/telegram/src/bot/delivery.replies.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxlint failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_format_telegram():
    """Repo's oxfmt format check passes on delivery.replies.ts (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "oxfmt", "--check", "extensions/telegram/src/bot/delivery.replies.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"oxfmt format check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_delivery_resolve_media_retry():
    """Repo's delivery resolve-media-retry tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/bot/delivery.resolve-media-retry.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Delivery resolve-media-retry tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_helpers():
    """Repo's helpers tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/bot/helpers.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Helpers tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_lane_delivery():
    """Repo's lane delivery tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/lane-delivery.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Lane delivery tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"

# [repo_tests] pass_to_pass
def test_repo_send():
    """Repo's send tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "exec", "vitest", "run", "extensions/telegram/src/send.test.ts", "--reporter=verbose"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Send tests failed:\n{r.stdout[-1000:]}{r.stderr[-500:]}"
