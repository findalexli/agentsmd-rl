"""
Task: opencode-tool-registry-effect-native
Repo: anomalyco/opencode @ d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3
PR:   anomalyco/opencode#19363

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/opencode"
REGISTRY = Path(REPO) / "packages/opencode/src/tool/registry.ts"
PLUGIN = Path(REPO) / "packages/opencode/src/plugin/index.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


def _strip_comments(code: str) -> str:
    """Remove single-line comments, block comments, and string literals."""
    s = re.sub(r"//[^\n]*", "", code)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    s = re.sub(r"'[^']*'", "''", s)
    s = re.sub(r'"[^"]*"', '""', s)
    s = re.sub(r"`[^`]*`", "``", s)
    return s


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node subprocess
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_facade_in_state_init():
    """Module-level Config/Plugin facades must not be called in InstanceState.make."""
    r = _run_node("""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');

const makeIdx = code.indexOf('InstanceState.make');
if (makeIdx === -1) {
  console.error('FAIL: Cannot find InstanceState.make');
  process.exit(1);
}

const endIdx = code.indexOf('return { custom }', makeIdx);
if (endIdx === -1) {
  console.error('FAIL: Cannot find end of InstanceState.make block');
  process.exit(1);
}
const block = code.slice(makeIdx, endIdx + 20);

// Module-level async facades must NOT appear in the block
const facades = ['Config.directories()', 'Config.waitForDependencies()', 'Plugin.list()'];
for (const facade of facades) {
  if (block.includes(facade)) {
    console.error('FAIL: Module-level facade ' + facade + ' found in InstanceState.make');
    process.exit(1);
  }
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_all_is_effectful():
    """all() must be an Effect function (Effect.fn or Effect.gen), not async."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');

if (/\basync\s+function\s+all\s*\(/.test(code)) {
  console.error('FAIL: all() is still a plain async function');
  process.exit(1);
}

if (/\ball\s*=\s*Effect\.fn\b/.test(code) || /\ball\s*=\s*Effect\.gen\b/.test(code)) {
  console.log('PASS');
} else {
  console.error('FAIL: all() not defined as Effect.fn or Effect.gen');
  process.exit(1);
}
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_effect_concurrency():
    """Promise.all replaced with Effect.forEach or Effect.all for concurrent tool init."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');

if (code.includes('Promise.all')) {
  console.error('FAIL: Promise.all still used in registry.ts');
  process.exit(1);
}

if (!code.includes('Effect.forEach') && !/Effect\.all\s*\(/.test(code)) {
  console.error('FAIL: No Effect concurrency primitive found');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_services_yielded_in_layer():
    """Config.Service and Plugin.Service must be obtained via Effect dependency graph."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');

const layerIdx = code.indexOf('Layer.effect');
if (layerIdx === -1) {
  console.error('FAIL: Cannot find Layer.effect definition');
  process.exit(1);
}

const makeIdx = code.indexOf('InstanceState.make', layerIdx);
if (makeIdx === -1) {
  console.error('FAIL: Cannot find InstanceState.make');
  process.exit(1);
}

// The region between Layer.effect and InstanceState.make must yield both services
const preamble = code.slice(layerIdx, makeIdx);

// Check for yield* Config.Service and yield* Plugin.Service patterns
const hasConfigService = /yield\*\s*Config\.Service/.test(preamble);
const hasPluginService = /yield\*\s*Plugin\.Service/.test(preamble);

if (!hasConfigService) {
  console.error('FAIL: Config.Service not yielded in layer generator before InstanceState.make');
  process.exit(1);
}

if (!hasPluginService) {
  console.error('FAIL: Plugin.Service not yielded in layer generator before InstanceState.make');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_plugin_default_layer_exported():
    """Plugin module must export defaultLayer for layer composition."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/plugin/index.ts', 'utf-8');

if (!/\bexport\s+(const|let|var)\s+defaultLayer\b/.test(code) &&
    !/\bexport\s*\{[^}]*\bdefaultLayer\b/.test(code)) {
  console.error('FAIL: Plugin.defaultLayer is not exported');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# [pr_diff] fail_to_pass
def test_registry_default_layer_exported():
    """ToolRegistry must export a composed defaultLayer providing dependencies."""
    r = _run_node(r"""
import { readFileSync } from 'fs';

const code = readFileSync('packages/opencode/src/tool/registry.ts', 'utf-8');

if (!/\bexport\s+(const|let|var)\s+defaultLayer\b/.test(code) &&
    !/\bexport\s*\{[^}]*\bdefaultLayer\b/.test(code)) {
  console.error('FAIL: ToolRegistry.defaultLayer is not exported');
  process.exit(1);
}

// Must compose Config and Plugin dependencies
if (!code.includes('Config.defaultLayer') || !code.includes('Plugin.defaultLayer')) {
  console.error('FAIL: defaultLayer does not compose Config.defaultLayer and Plugin.defaultLayer');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr}\\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_service_class_preserved():
    """ToolRegistry.Service class definition must still exist."""
    code = REGISTRY.read_text()
    assert "class Service" in code, "Service class missing from registry.ts"


# [pr_diff] pass_to_pass
def test_public_facades_exported():
    """Public facade functions (register, ids, tools) must remain exported."""
    code = _strip_comments(REGISTRY.read_text())
    assert re.search(r"\bexport\s+(async\s+)?function\s+register\b", code), \
        "Public facade 'register' is not exported"
    assert re.search(r"\bexport\s+(async\s+)?function\s+ids\b", code), \
        "Public facade 'ids' is not exported"
    assert re.search(r"\bexport\s+(async\s+)?function\s+tools\b", code), \
        "Public facade 'tools' is not exported"
    # Facades must delegate to the Effect runtime via runPromise
    assert code.count("runPromise") >= 3, \
        "Each facade (register, ids, tools) should call runPromise to delegate to the Effect service"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass
def test_effect_fn_usage():
    """Service methods should use Effect.fn for named/traced effects (>= 3 uses)."""
    code = _strip_comments(REGISTRY.read_text())
    count = len(re.findall(r"Effect\.fn\s*\(", code))
    assert count >= 3, f"Effect.fn used only {count} times (expected >= 3)"


# [agent_config] fail_to_pass — added by fix (not present in base)
def test_effect_fn_untraced_usage():
    """Effect.fnUntraced must be used for internal/anonymous helper effects."""
    code = _strip_comments(REGISTRY.read_text())
    assert "Effect.fnUntraced" in code, "Effect.fnUntraced not found in registry.ts"


# [agent_config] pass_to_pass — AGENTS.md:17 @ d2bfa92
def test_filter_usage():
    """Tool filtering should use .filter() (functional array method)."""
    code = REGISTRY.read_text()
    assert ".filter(" in code, ".filter() not found in registry.ts"


# ---------------------------------------------------------------------------
# Anti-stub (static) — files not gutted
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_not_stub():
    """Modified files must have substantial implementation."""
    reg_lines = len(REGISTRY.read_text().splitlines())
    plug_lines = len(PLUGIN.read_text().splitlines())
    assert reg_lines >= 150, f"registry.ts too short ({reg_lines} lines)"
    assert plug_lines >= 150, f"plugin/index.ts too short ({plug_lines} lines)"


# ---------------------------------------------------------------------------
# Repo CI/CD (pass_to_pass) — ensures base commit functionality is preserved
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (bunx turbo typecheck)."""
    script = """export HOME=/root
export PATH=\"/root/.bun/bin:$PATH\"
if ! command -v bun &>/dev/null; then
  apt-get update -qq && apt-get install -y -qq unzip curl 2>/dev/null
  curl -fsSL https://bun.sh/install | bash -s 'bun-v1.3.11' 2>/dev/null
fi
export PATH=\"/root/.bun/bin:$PATH\"
cd /workspace/opencode && bun install 2>&1 | tail -5
bunx turbo typecheck 2>&1
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_tool_registry_tests():
    """Tool registry tests pass (bun test test/tool/registry.test.ts)."""
    script = """export HOME=/root
export PATH=\"/root/.bun/bin:$PATH\"
if ! command -v bun &>/dev/null; then
  apt-get update -qq && apt-get install -y -qq unzip curl 2>/dev/null
  curl -fsSL https://bun.sh/install | bash -s 'bun-v1.3.11' 2>/dev/null
fi
export PATH=\"/root/.bun/bin:$PATH\"
cd /workspace/opencode && bun install 2>&1 | tail -5
cd packages/opencode && bun test --timeout 30000 test/tool/registry.test.ts 2>&1
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Tool registry tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_opencode_typecheck():
    """Opencode package typecheck passes (bunx turbo typecheck --filter=opencode)."""
    script = """export HOME=/root
export PATH=\"/root/.bun/bin:$PATH\"
if ! command -v bun &>/dev/null; then
  apt-get update -qq && apt-get install -y -qq unzip curl 2>/dev/null
  curl -fsSL https://bun.sh/install | bash -s 'bun-v1.3.11' 2>/dev/null
fi
export PATH=\"/root/.bun/bin:$PATH\"
cd /workspace/opencode && bun install 2>&1 | tail -5
bunx turbo typecheck --filter=opencode 2>&1
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Opencode typecheck failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_effect_tests():
    """Effect-related tests pass (bun test test/effect/)."""
    script = """export HOME=/root
export PATH=\"/root/.bun/bin:$PATH\"
if ! command -v bun &>/dev/null; then
  apt-get update -qq && apt-get install -y -qq unzip curl 2>/dev/null
  curl -fsSL https://bun.sh/install | bash -s 'bun-v1.3.11' 2>/dev/null
fi
export PATH=\"/root/.bun/bin:$PATH\"
cd /workspace/opencode && bun install 2>&1 | tail -5
cd packages/opencode && bun test --timeout 30000 test/effect/ 2>&1
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=180,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Effect tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_tests():
    """Plugin tests pass (bun test test/plugin/)."""
    script = """export HOME=/root
export PATH=\"/root/.bun/bin:$PATH\"
if ! command -v bun &>/dev/null; then
  apt-get update -qq && apt-get install -y -qq unzip curl 2>/dev/null
  curl -fsSL https://bun.sh/install | bash -s 'bun-v1.3.11' 2>/dev/null
fi
export PATH=\"/root/.bun/bin:$PATH\"
cd /workspace/opencode && bun install 2>&1 | tail -5
cd packages/opencode && bun test --timeout 30000 test/plugin/ 2>&1
"""
    r = subprocess.run(
        ["bash", "-c", script],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Plugin tests failed:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


