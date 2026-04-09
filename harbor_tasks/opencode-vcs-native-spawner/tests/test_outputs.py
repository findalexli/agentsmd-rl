"""
Task: opencode-vcs-native-spawner
Repo: anomalyco/opencode @ b242a8d8e42839496c7213d020e8cba19a76e111
PR:   #19361

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
VCS_TS = Path(REPO) / "packages/opencode/src/project/vcs.ts"


def _read_vcs():
    assert VCS_TS.exists(), "vcs.ts is missing"
    return VCS_TS.read_text()


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo directory."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def _code_lines(src: str) -> list[str]:
    """Return non-comment, non-blank lines."""
    lines = []
    for line in src.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//") or stripped.startswith("*"):
            continue
        lines.append(line)
    return lines


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_vcs_file_nontrivial():
    """vcs.ts must exist with >= 40 lines of implementation."""
    src = _read_vcs()
    lines = src.splitlines()
    assert len(lines) >= 40, f"vcs.ts too short ({len(lines)} lines)"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_effect_promise():
    """Effect.promise must not appear — it bypasses Effect's scope and interruption model."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Strip single-line comments and check remaining code for Effect.promise
const lines = src.split('\n');
const codeLines = lines.filter(l => {
    const t = l.trim();
    return t && !t.startsWith('//') && !t.startsWith('*');
});

const found = codeLines.filter(l => l.includes('Effect.promise'));
if (found.length > 0) {
    console.error('Effect.promise found in code:');
    found.forEach(l => console.error('  ' + l.trim()));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"vcs.ts still uses Effect.promise:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_no_util_git_import():
    """The old @/util/git async utility must not be imported."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Parse import lines and check for @/util/git
const importLines = src.split('\n').filter(l => /^\s*import\s/.test(l));
const gitImports = importLines.filter(l => l.includes('@/util/git'));
if (gitImports.length > 0) {
    console.error('Still imports @/util/git:');
    gitImports.forEach(l => console.error('  ' + l.trim()));
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"vcs.ts still imports @/util/git:\n{r.stderr}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_imports_child_process_spawner():
    """Must import ChildProcess/ChildProcessSpawner from effect's process module."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Parse import statements and find ChildProcessSpawner from effect/unstable/process
const importLines = src.split('\n').filter(l => /^\s*import\s/.test(l));
const spawnerImport = importLines.find(l =>
    (l.includes('ChildProcess') || l.includes('ChildProcessSpawner')) &&
    l.includes('effect/unstable/process')
);

if (!spawnerImport) {
    console.error('Missing ChildProcess/ChildProcessSpawner import from effect/unstable/process');
    console.error('Found imports:');
    importLines.forEach(l => console.error('  ' + l.trim()));
    process.exit(1);
}

console.log(JSON.stringify({ import: spawnerImport.trim() }));
""")
    assert r.returncode == 0, f"Missing ChildProcessSpawner import:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert "ChildProcess" in data["import"]


# [pr_diff] fail_to_pass
def test_generator_git_helper_complete():
    """A generator must spawn a child process, read exit code, and extract stdout text."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Extract generator function bodies using brace-depth tracking
const lines = src.split('\n');
const generators = [];
let depth = 0, inGen = false, current = [];

for (const line of lines) {
    if (/function\s*\*/.test(line) && !inGen) {
        inGen = true;
        depth = 0;
        current = [];
    }
    if (inGen) {
        current.push(line);
        depth += (line.match(/{/g) || []).length - (line.match(/}/g) || []).length;
        if (depth <= 0 && current.length > 3) {
            generators.push(current.join('\n'));
            inGen = false;
        }
    }
}

if (generators.length === 0) {
    console.error('No generator functions found in vcs.ts');
    process.exit(1);
}

// Find a generator that spawns a child process, reads exit code, and extracts stdout
const complete = generators.find(g => {
    const hasSpawn = /spawn|ChildProcess\.make/.test(g);
    const hasExit = /\.code\b|\.exitCode\b|exitCode/.test(g);
    const hasOutput = /\.stdout\b|\.text\b|mkString|decodeText/.test(g);
    const hasYield = /yield\s*\*/.test(g);
    return hasSpawn && hasExit && hasOutput && hasYield;
});

if (!complete) {
    console.error('No generator found with spawn+exitCode+stdout chain');
    console.error(`Checked ${generators.length} generator(s)`);
    process.exit(1);
}

console.log(JSON.stringify({ generators: generators.length, status: 'PASS' }));
""")
    assert r.returncode == 0, f"Generator check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "PASS"


# [pr_diff] fail_to_pass
def test_layer_declares_spawner_dependency():
    """The layer type signature must include ChildProcessSpawner as a dependency."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Find 'export const layer' and extract its Layer.Layer<...> type annotation
const layerMatch = src.match(/export\s+const\s+layer.*?Layer\.Layer<[^>]+>/s);
if (!layerMatch) {
    console.error("Could not find 'export const layer' with Layer.Layer<...> type");
    process.exit(1);
}

const typeAnnotation = layerMatch[0];
if (!typeAnnotation.includes('ChildProcessSpawner')) {
    console.error('Layer type does not declare ChildProcessSpawner dependency');
    console.error('Found: ' + typeAnnotation);
    process.exit(1);
}

console.log(JSON.stringify({ type: typeAnnotation.trim(), status: 'PASS' }));
""")
    assert r.returncode == 0, f"Layer type check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "PASS"


# [pr_diff] fail_to_pass
def test_default_layer_provides_spawner():
    """defaultLayer must wire in a concrete spawner (CrossSpawnSpawner or equivalent)."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Check for CrossSpawnSpawner import
const hasImport = /import.*(?:CrossSpawn|cross-spawn-spawner)/i.test(src);
if (!hasImport) {
    console.error('No CrossSpawnSpawner import found');
    process.exit(1);
}

// Check defaultLayer wires in the spawner
const dlIdx = src.indexOf('defaultLayer');
if (dlIdx < 0) {
    console.error('defaultLayer not found');
    process.exit(1);
}

const afterDl = src.slice(dlIdx, dlIdx + 500);
if (!/(?:CrossSpawn|Spawner|spawner)/i.test(afterDl)) {
    console.error('defaultLayer does not reference a spawner implementation');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"defaultLayer spawner check failed:\n{r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — rules from repo config files
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:47 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_uses_child_process_make():
    """Must use ChildProcess.make() to construct child process descriptors (not raw spawn)."""
    r = _run_node(r"""
const fs = require('fs');
const src = fs.readFileSync('packages/opencode/src/project/vcs.ts', 'utf8');

// Verify ChildProcess.make() is called within a generator body
const lines = src.split('\n');
const makeLines = lines.filter(l => /ChildProcess\.make\s*\(/.test(l));
if (makeLines.length === 0) {
    console.error('ChildProcess.make() not found — required by packages/opencode/AGENTS.md');
    process.exit(1);
}

console.log(JSON.stringify({ calls: makeLines.length, status: 'PASS' }));
""")
    assert r.returncode == 0, f"ChildProcess.make() check failed:\n{r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data["status"] == "PASS"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:45 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_platform_api():
    """Must not use raw Node.js child_process or async exec — use Effect services instead."""
    src = _read_vcs()
    for pattern, label in [
        (r"""from\s+['"]child_process['"]""", "raw child_process import"),
        (r"""from\s+['"]node:child_process['"]""", "raw node:child_process import"),
        (r"""\bexec\s*\(""", "raw exec() call"),
        (r"""\bexecSync\s*\(""", "raw execSync() call"),
        (r"""\bspawnSync\s*\(""", "raw spawnSync() call"),
    ]:
        assert not re.search(pattern, src), f"vcs.ts uses {label} — prefer Effect services"


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + style guards
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_public_api_intact():
    """Service public API (layer, defaultLayer, Service, init, branch) must remain."""
    src = _read_vcs()
    assert "export const layer" in src, "Missing 'export const layer'"
    assert "export const defaultLayer" in src, "Missing 'export const defaultLayer'"
    assert "export class Service" in src, "Missing 'export class Service'"
    assert re.search(r"export\s+function\s+init", src), "Missing 'export function init'"
    assert re.search(r"export\s+function\s+branch", src), "Missing 'export function branch'"


# [agent_config] pass_to_pass — AGENTS.md:13 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_any_type():
    """Must not use the 'any' type."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r":\s*any\b", line), f"Found ': any' usage: {line.strip()}"
        assert not re.search(r"\bas\s+any\b", line), f"Found 'as any' usage: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:12 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_try_catch():
    """Must not use try/catch — prefer Effect error handling."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r"\btry\s*\{", line), f"Found try/catch: {line.strip()}"


# [agent_config] pass_to_pass — AGENTS.md:70 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_let_declarations():
    """Must not use let — prefer const with ternaries or early returns."""
    src = _read_vcs()
    code = _code_lines(src)
    for line in code:
        assert not re.search(r"\blet\b", line), f"Found let declaration: {line.strip()}"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:46 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_fs_import():
    """Must not import raw fs/promises — use FileSystem.FileSystem service instead."""
    src = _read_vcs()
    for pattern, label in [
        (r"""from\s+['"]fs/promises['"]""", "fs/promises import"),
        (r"""from\s+['"]node:fs/promises['"]""", "node:fs/promises import"),
        (r"""from\s+['"]node:fs['"]""", "node:fs import"),
        (r"""from\s+['"]fs['"]""", "raw fs import"),
    ]:
        assert not re.search(pattern, src), f"vcs.ts uses {label} — prefer FileSystem.FileSystem"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:48 @ b242a8d8e42839496c7213d020e8cba19a76e111
def test_no_raw_fetch():
    """Must not use raw fetch() — use HttpClient.HttpClient service instead."""
    src = _read_vcs()
    assert not re.search(r"\bfetch\s*\(", src), "vcs.ts uses raw fetch() — prefer HttpClient.HttpClient"
