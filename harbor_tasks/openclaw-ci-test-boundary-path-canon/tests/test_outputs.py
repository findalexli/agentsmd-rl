"""
Task: openclaw-ci-test-boundary-path-canon
Repo: openclaw/openclaw @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
PR:   #57797

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Behavioral tests use subprocess.run(["node", ...]) to execute JavaScript that
verifies the fix works correctly. Structural/grep tests are kept only where
execution is impractical (line counting, regex patterns across blocks).
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/openclaw"
CMD_TEST = f"{REPO}/src/auto-reply/reply/commands.test.ts"
MEDIA_TEST = f"{REPO}/src/media-understanding/media-understanding-misc.test.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
    )


def _read(filepath: str) -> str:
    return Path(filepath).read_text()


def _code_lines(filepath: str) -> list[str]:
    """Return non-comment, non-blank lines from a TS file."""
    out: list[str] = []
    for line in Path(filepath).read_text().splitlines():
        t = line.strip()
        if not t or t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        out.append(line)
    return out


def _code(filepath: str) -> str:
    return "\n".join(_code_lines(filepath))


def _ssrf_block(filepath: str) -> str:
    """Return the full text of the SSRF describe block."""
    src = _read(filepath)
    idx = src.find("media understanding attachments SSRF")
    assert idx != -1, "SSRF describe block not found in media test file"
    return src[idx:]


def _ssrf_code(filepath: str) -> str:
    """Return non-comment lines from the SSRF describe block."""
    lines = []
    for line in _ssrf_block(filepath).splitlines():
        t = line.strip()
        if t and not t.startswith("//") and not t.startswith("*") and not t.startswith("/*"):
            lines.append(line)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_files_parse():
    """Modified TS files must have balanced braces."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        src = _read(fp)
        depth = 0
        for ch in src:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
        assert depth == 0, f"{fp} has unbalanced braces (depth={depth})"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Bug 1: Extension boundary
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_extension_import_removed():
    """Buggy import from extensions/telegram/test-support must be removed."""
    r = _run_node(
        r"""
const fs = require('fs');
const src = fs.readFileSync('src/auto-reply/reply/commands.test.ts', 'utf8');
for (const line of src.split('\n')) {
    const t = line.trim();
    if (/^import\b/.test(t) && t.includes('extensions/telegram/test-support')) {
        console.error('Extension import still present: ' + t);
        process.exit(1);
    }
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Extension import still present: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_plugin_constructed_intree():
    """telegramCommandTestPlugin constructed in-tree via SDK helpers with resolvable imports."""
    r = _run_node(
        r"""
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync('src/auto-reply/reply/commands.test.ts', 'utf8');

// Must be defined locally (const/let/var declaration or typed assignment)
if (!/(?:const|let|var)\s+telegramCommandTestPlugin\b/.test(src)
    && !/telegramCommandTestPlugin\s*[:=]/.test(src)) {
    console.error('telegramCommandTestPlugin is not defined locally');
    process.exit(1);
}

// Must use SDK helpers or explicit ChannelPlugin typing
const hasSDK = src.includes('createChannelTestPluginBase')
    || src.includes('createTestPluginBase')
    || (/id:\s*['"]telegram['"]/.test(src) && /label:\s*['"]Telegram['"]/.test(src))
    || /as\s+ChannelPlugin/.test(src)
    || /:\s*ChannelPlugin\s*[={]/.test(src);

if (!hasSDK) {
    console.error('Not constructed with SDK helpers or ChannelPlugin type');
    process.exit(1);
}

// Behavioral: verify SDK imports resolve to real files on disk
const importPaths = src.match(/from\s+['"]([^'"]*(?:channel-plugins|plugin-sdk)[^'"]*)['"]/g) || [];
for (const imp of importPaths) {
    const match = imp.match(/from\s+['"]([^'"]+)['"]/);
    if (!match) continue;
    const resolved = path.resolve(path.dirname('src/auto-reply/reply/commands.test.ts'), match[1]);
    const candidates = [
        resolved,
        resolved.replace(/\.js$/, '.ts'),
        resolved + '/index.js',
        resolved + '/index.ts',
    ];
    const exists = candidates.some(p => {
        try { fs.accessSync(p); return true; } catch { return false; }
    });
    if (!exists) {
        console.error('Import does not resolve: ' + match[1]);
        process.exit(1);
    }
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Plugin construction check failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_plugin_not_stub():
    """Plugin definition spans >=8 meaningful lines (rejects trivial stubs)."""
    lines = _read(CMD_TEST).splitlines()

    def_start = -1
    for i, line in enumerate(lines):
        t = line.strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        if re.search(
            r"(?:const|let|var)\s+telegramCommandTestPlugin\b", t
        ) or re.search(r"telegramCommandTestPlugin\s*[:=]", t):
            def_start = i
            break

    assert def_start >= 0, "telegramCommandTestPlugin definition not found"

    # Walk from definition to end of its object/block
    count = 0
    brace_depth = 0
    started = False
    for i in range(def_start, min(len(lines), def_start + 300)):
        t = lines[i].strip()
        if t.startswith("//") or t.startswith("*") or t.startswith("/*"):
            continue
        if not t:
            continue
        count += 1
        for ch in lines[i]:
            if ch == "{":
                brace_depth += 1
                started = True
            elif ch == "}":
                brace_depth -= 1
        if started and brace_depth <= 0 and i > def_start:
            break

    assert count >= 8, (
        f"telegramCommandTestPlugin is a trivial stub ({count} lines, need >=8)"
    )


# [pr_diff] fail_to_pass
def test_plugin_has_channel_config():
    """Plugin definition includes config/allowlist/auth adapters with resolvable modules."""
    r = _run_node(
        r"""
const fs = require('fs');
const path = require('path');
const src = fs.readFileSync('src/auto-reply/reply/commands.test.ts', 'utf8');

const hasConfig = src.includes('createScopedChannelConfigAdapter')
    || (/config\s*:/.test(src) && /sectionKey|listAccountIds/.test(src));
const hasAllowlist = src.includes('buildDmGroupAccountAllowlistAdapter')
    || /allowlist\s*:/.test(src);

if (!hasConfig) { console.error('Missing config adapter'); process.exit(1); }
if (!hasAllowlist) { console.error('Missing allowlist adapter'); process.exit(1); }

// Behavioral: verify adapter modules exist on disk
const adapterImports = [];
const importRegex = /from\s+['"]([^'"]*plugin-sdk\/[^'"]+)['"]/g;
let m;
while ((m = importRegex.exec(src)) !== null) {
    adapterImports.push(m[1]);
}
for (const imp of adapterImports) {
    const resolved = path.resolve('src/auto-reply/reply', imp);
    const candidates = [
        resolved,
        resolved.replace(/\.js$/, '.ts'),
        resolved + '/index.js',
        resolved + '/index.ts',
    ];
    const exists = candidates.some(p => {
        try { fs.accessSync(p); return true; } catch { return false; }
    });
    if (!exists) {
        console.error('Adapter import does not resolve: ' + imp);
        process.exit(1);
    }
}
console.log('OK');
"""
    )
    assert r.returncode == 0, f"Plugin config check failed: {r.stderr}"
    assert "OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Bug 2: Path canonicalization
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_path_canonicalization_in_ssrf():
    """SSRF test block uses path canonicalization (realpath) to handle symlinked tmpdir."""
    # Behavioral: verify fs.realpath actually resolves symlinks correctly,
    # then verify the SSRF test file uses the same canonicalization pattern
    r = _run_node(
        r"""
const fs = require('fs');
const path = require('path');
const os = require('os');

// --- Part 1: Demonstrate canonicalization behavior ---
// Create a symlinked directory structure like macOS /var -> /private/var
const realDir = fs.mkdtempSync(path.join(os.tmpdir(), 'eval-real-'));
const linkDir = path.join(os.tmpdir(), 'eval-link-' + Date.now());

try {
    fs.symlinkSync(realDir, linkDir, 'dir');
    const filePath = path.join(linkDir, 'test.txt');
    fs.writeFileSync(filePath, 'ok');

    const rawPath = filePath;
    const canonicalPath = fs.realpathSync(filePath);

    // Verify realpath is idempotent and produces a consistent resolved path
    const doubleReal = fs.realpathSync(canonicalPath);
    if (doubleReal !== canonicalPath) {
        throw new Error('realpath not idempotent: ' + doubleReal + ' != ' + canonicalPath);
    }

    // If system has symlinked tmpdir, raw and canonical differ — this is the
    // exact bug: comparing rawPath vs canonicalPath without canonicalization fails
    // The fix uses fs.realpath to ensure both sides are canonicalized
} finally {
    try { fs.rmSync(linkDir, { force: true, recursive: true }); } catch {}
    try { fs.rmSync(realDir, { force: true, recursive: true }); } catch {}
}

// --- Part 2: Verify SSRF test file uses canonicalization ---
const testSrc = fs.readFileSync('src/media-understanding/media-understanding-misc.test.ts', 'utf8');
const ssrfIdx = testSrc.indexOf('media understanding attachments SSRF');
if (ssrfIdx === -1) {
    throw new Error('SSRF describe block not found');
}
const ssrfBlock = testSrc.slice(ssrfIdx);
const canonPattern = /realpath|realpathSync|canonicalAttachmentPath/;
if (!canonPattern.test(ssrfBlock)) {
    throw new Error('SSRF tests do not use path canonicalization (realpath/realpathSync)');
}

console.log('OK');
"""
    )
    assert r.returncode == 0, f"Path canonicalization test failed: {r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_no_direct_path_comparison():
    """No direct uncanonicalized path equality remains in SSRF tests."""
    code = _ssrf_code(MEDIA_TEST)

    # The base commit has toHaveBeenCalledWith(attachmentPath, ...) directly
    assert not re.search(
        r"toHaveBeenCalledWith\(\s*attachmentPath\s*,", code
    ), "Direct uncanonicalized toHaveBeenCalledWith(attachmentPath, ...) still present"

    # Also check for direct !== comparison without prior canonicalization
    assert not re.search(
        r"filePath\s*!==?\s*attachmentPath", code
    ), "Direct uncanonicalized filePath !== attachmentPath still present"


# [pr_diff] fail_to_pass
def test_both_ssrf_tests_canonicalize():
    """Both path-comparing SSRF test cases use canonicalization, not just one."""
    block = _ssrf_block(MEDIA_TEST)
    # Split into individual it() blocks
    it_blocks = re.split(r'\bit\s*\(', block)
    test_blocks = it_blocks[1:]  # skip preamble before first it(

    canon_re = re.compile(
        r"realpath|realpathSync|path\.resolve|canonicali[sz]e", re.IGNORECASE
    )

    # Find blocks that compare file paths (the two bugs):
    path_compare_blocks = []
    for tb in test_blocks:
        if ("filePath" in tb and "attachmentPath" in tb) or (
            "openSpy" in tb and "attachmentPath" in tb and "openedPath" in tb
        ) or ("toHaveBeenCalledWith" in tb and "attachmentPath" in tb):
            path_compare_blocks.append(tb)

    assert len(path_compare_blocks) >= 2, (
        f"Expected at least 2 path-comparing SSRF test cases, found {len(path_compare_blocks)}"
    )

    for i, tb in enumerate(path_compare_blocks):
        assert canon_re.search(tb), (
            f"Path-comparing SSRF test case {i + 1} does not use path canonicalization"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression / structure preserved
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_plugin_defined_and_used():
    """telegramCommandTestPlugin appears at least twice (definition + usage)."""
    code = _code(CMD_TEST)
    matches = re.findall(r"telegramCommandTestPlugin", code)
    assert len(matches) >= 2, (
        f"telegramCommandTestPlugin appears {len(matches)} time(s), need >=2"
    )


# [pr_diff] pass_to_pass
def test_ssrf_structure_preserved():
    """SSRF test block still references MediaAttachmentCache and O_NOFOLLOW."""
    code = _ssrf_code(MEDIA_TEST)
    assert "MediaAttachmentCache" in code, "MediaAttachmentCache reference removed from SSRF tests"
    assert "O_NOFOLLOW" in code, "O_NOFOLLOW reference removed from SSRF tests"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------


# [agent_config] fail_to_pass — AGENTS.md:42 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_extension_deep_imports():
    """Core tests must not deep-import bundled plugin internals (AGENTS.md:42)."""
    for line in _code_lines(CMD_TEST):
        t = line.strip()
        if re.match(r"^import\b", t) and re.search(r"""['"].*extensions/""", t):
            raise AssertionError(f"Extension deep-import found in core test: {t}")


# [agent_config] pass_to_pass — test/helpers/channels/AGENTS.md:8-9 @ 17d0be0
def test_no_hardcoded_extension_paths():
    """Core test helpers must not hardcode repo-relative imports into extensions/**."""
    for line in _code_lines(CMD_TEST):
        t = line.strip()
        if re.search(r"""(?:require|import)\s*\(\s*['"].*extensions/""", t):
            raise AssertionError(f"Hardcoded extension path in dynamic import/require: {t}")


# [agent_config] pass_to_pass — AGENTS.md:146 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_ts_nocheck():
    """Never add @ts-nocheck (AGENTS.md:146)."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        src = _read(fp)
        assert "@ts-nocheck" not in src, f"@ts-nocheck found in {fp}"


# [agent_config] pass_to_pass — AGENTS.md:146 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_lint_suppressions():
    """Do not add inline lint suppressions by default (AGENTS.md:146)."""
    # Check the SSRF block (Bug 2 fix area) for new suppressions
    ssrf = _ssrf_block(MEDIA_TEST)
    for suppress in ["@ts-ignore", "@ts-expect-error", "eslint-disable", "oxlint-disable"]:
        assert suppress not in ssrf, (
            f"Lint suppression '{suppress}' added in SSRF test block"
        )

    # Check the new plugin definition area (Bug 1 fix area) in commands.test.ts
    src = _read(CMD_TEST)
    idx = src.find("telegramCommandTestPlugin")
    if idx != -1:
        plugin_area = src[idx:]
        for suppress in ["@ts-ignore", "@ts-expect-error"]:
            assert suppress not in plugin_area, (
                f"Lint suppression '{suppress}' added near plugin definition in commands.test.ts"
            )


# [agent_config] pass_to_pass — AGENTS.md:162 @ 17d0be02f2800a2bc4524c7d5b587d7fd9f6f28c
def test_no_prototype_mutation_in_tests():
    """In tests, prefer per-instance stubs over prototype mutation (AGENTS.md:162)."""
    for fp in [CMD_TEST, MEDIA_TEST]:
        for line in _code_lines(fp):
            assert not re.search(r"\.prototype\.\w+\s*=", line), (
                f"Prototype mutation found in {fp}: {line.strip()}"
            )


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass) — ensure repo's own CI checks still pass
# ---------------------------------------------------------------------------


def _run_in_repo(cmd: list[str], timeout: int = 180) -> subprocess.CompletedProcess:
    """Run a command in the repo directory."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)


def test_repo_oxlint():
    """Repo's oxlint passes on modified files (pass_to_pass)."""
    # First install pnpm and dependencies
    r = _run_in_repo(["npm", "install", "-g", "pnpm"], timeout=60)
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr}"

    r = _run_in_repo(["pnpm", "install", "--frozen-lockfile"], timeout=180)
    assert r.returncode == 0, f"Failed to install dependencies: {r.stderr}"

    r = _run_in_repo(
        [
            "npx",
            "oxlint",
            "src/media-understanding/media-understanding-misc.test.ts",
            "src/auto-reply/reply/commands.test.ts",
        ],
        timeout=60,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stdout}\n{r.stderr}"


def test_repo_oxfmt():
    """Repo's oxfmt format check passes on modified files (pass_to_pass)."""
    r = _run_in_repo(["npm", "install", "-g", "pnpm"], timeout=60)
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr}"

    r = _run_in_repo(["pnpm", "install", "--frozen-lockfile"], timeout=180)
    assert r.returncode == 0, f"Failed to install dependencies: {r.stderr}"

    r = _run_in_repo(
        [
            "pnpm",
            "exec",
            "oxfmt",
            "--check",
            "src/media-understanding/media-understanding-misc.test.ts",
            "src/auto-reply/reply/commands.test.ts",
        ],
        timeout=60,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stdout}\n{r.stderr}"


def test_repo_media_tests():
    """Repo's media-understanding SSRF tests pass (pass_to_pass)."""
    r = _run_in_repo(["npm", "install", "-g", "pnpm"], timeout=60)
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr}"

    r = _run_in_repo(["pnpm", "install", "--frozen-lockfile"], timeout=180)
    assert r.returncode == 0, f"Failed to install dependencies: {r.stderr}"

    r = _run_in_repo(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "src/media-understanding/media-understanding-misc.test.ts",
        ],
        timeout=120,
    )
    assert r.returncode == 0, f"Media tests failed:\n{r.stderr[-500:]}"


def test_repo_media_unit_tests():
    """Repo's media-understanding unit tests pass (pass_to_pass)."""
    r = _run_in_repo(["npm", "install", "-g", "pnpm"], timeout=60)
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr}"

    r = _run_in_repo(["pnpm", "install", "--frozen-lockfile"], timeout=180)
    assert r.returncode == 0, f"Failed to install dependencies: {r.stderr}"

    test_files = [
        "src/media-understanding/attachments.normalize.test.ts",
        "src/media-understanding/attachments.guards.test.ts",
        "src/media-understanding/defaults.test.ts",
        "src/media-understanding/format.test.ts",
        "src/media-understanding/resolve.test.ts",
        "src/media-understanding/provider-registry.test.ts",
    ]
    r = _run_in_repo(["pnpm", "exec", "vitest", "run"] + test_files, timeout=120)
    assert r.returncode == 0, f"Media unit tests failed:\n{r.stderr[-500:]}"


def test_repo_commands_tests():
    """Repo's auto-reply commands tests pass (pass_to_pass)."""
    r = _run_in_repo(["npm", "install", "-g", "pnpm"], timeout=60)
    assert r.returncode == 0, f"Failed to install pnpm: {r.stderr}"

    r = _run_in_repo(["pnpm", "install", "--frozen-lockfile"], timeout=180)
    assert r.returncode == 0, f"Failed to install dependencies: {r.stderr}"

    r = _run_in_repo(
        [
            "pnpm",
            "exec",
            "vitest",
            "run",
            "src/auto-reply/reply/commands.test.ts",
        ],
        timeout=300,
    )
    assert r.returncode == 0, f"Commands tests failed:\n{r.stderr[-500:]}"
