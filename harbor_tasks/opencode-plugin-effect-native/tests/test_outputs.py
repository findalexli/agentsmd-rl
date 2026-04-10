"""
Task: opencode-plugin-effect-native
Repo: anomalyco/opencode @ bb8d2cdd108618c1057a8890ac1e655198db866e
PR:   #19365

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"
PLUGIN_FILE = f"{REPO}/packages/opencode/src/plugin/index.ts"
TEST_FILE = f"{REPO}/packages/opencode/test/plugin/auth-override.test.ts"


def _read(path: str) -> str:
    return Path(path).read_text()


def _plugin_src() -> str:
    return _read(PLUGIN_FILE)


def _instance_state_body(src: str) -> str:
    """Extract the InstanceState.make closure body for scoped checks."""
    make_idx = src.index("InstanceState.make")
    # Find the body up to the bus subscription (end of make closure logic)
    m = re.search(
        r"InstanceState\.make.*?\n([\s\S]+?)(?=\n\s*//\s*Subscribe to bus|\n\s*yield\* bus\.subscribe)",
        src,
    )
    assert m, "Could not find InstanceState.make body"
    return m.group(1)


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


def _ensure_bun() -> str:
    """Ensure bun is available, installing it if necessary. Returns bun path."""
    bun_path = Path.home() / ".bun" / "bin" / "bun"
    if not bun_path.exists():
        # Install bun with required dependencies
        subprocess.run(
            ["apt-get", "update", "-qq"],
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["apt-get", "install", "-y", "-qq", "unzip"],
            capture_output=True, timeout=60,
        )
        subprocess.run(
            ["bash", "-c", "curl -fsSL https://bun.sh/install | bash"],
            capture_output=True, check=True, timeout=120,
        )
    return str(bun_path)


def _bun_env() -> dict:
    """Return environment dict with bun in PATH."""
    bun_dir = str(Path.home() / ".bun" / "bin")
    env = dict(os.environ)
    env["PATH"] = f"{bun_dir}:{env.get('PATH', '')}"
    return env


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_plugin_file_exists():
    """Target file exists and has substantial content."""
    src = _plugin_src()
    assert len(src) > 500, "plugin/index.ts is too small — likely a stub"


# [static] pass_to_pass
def test_not_stub():
    """InstanceState.make closure contains real Effect logic, not a stub."""
    src = _plugin_src()
    assert "InstanceState.make" in src
    # Must have InstanceState factory with real content (hooks, plugin loading, etc.)
    assert "hooks" in src, "No hooks array — plugin service is a stub"
    assert "INTERNAL_PLUGINS" in src, "No INTERNAL_PLUGINS reference — plugin loading missing"
    assert len(src) > 3000, "plugin/index.ts too small — likely a stub"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_no_monolithic_effect_promise():
    """The InstanceState.make closure must NOT wrap all logic in a single Effect.promise(async () => {...}).

    The fix breaks the monolithic promise into individual yield* statements.
    """
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/opencode/src/plugin/index.ts', 'utf8');

const makeIdx = src.indexOf('InstanceState.make');
if (makeIdx === -1) { console.error('InstanceState.make not found'); process.exit(1); }
const section = src.slice(makeIdx, makeIdx + 3000);

// Find Effect.promise(async ...) blocks — the monolithic pattern.
// On the fix, Effect.promise uses () => (not async), so only async blocks are suspect.
let searchFrom = 0;
while (true) {
    const idx = section.indexOf('Effect.promise(async', searchFrom);
    if (idx === -1) break;

    const braceIdx = section.indexOf('{', idx + 'Effect.promise(async'.length);
    if (braceIdx === -1) { searchFrom = idx + 1; continue; }

    let depth = 1, pos = braceIdx + 1;
    while (pos < section.length && depth > 0) {
        if (section[pos] === '{') depth++;
        else if (section[pos] === '}') depth--;
        pos++;
    }
    const body = section.slice(braceIdx, pos);

    if (body.includes('Config.get()')) {
        console.error('Config.get() still inside Effect.promise(async) — monolithic wrapper not removed');
        process.exit(1);
    }
    if (body.includes('INTERNAL_PLUGINS')) {
        console.error('Plugin loading loop still inside single Effect.promise(async) — not broken out');
        process.exit(1);
    }
    searchFrom = pos;
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_config_service_yielded_directly():
    """Config.Service must be yielded in the Effect generator instead of using Config.get() async facade."""
    src = _plugin_src()
    assert re.search(r"yield\*\s+Config\.Service", src), \
        "Config.Service not yielded — still using async facade"
    assert "Config.get()" not in src, \
        "Config.get() async facade still present — should yield Config.Service and call .get() on it"


# [pr_diff] fail_to_pass
def test_plugin_loading_uses_effect_try_promise():
    """Internal plugin loading errors must use Effect.tryPromise instead of .catch().
    # AST-only because: TypeScript/Effect service — cannot import or execute from Python
    """
    src = _plugin_src()
    # Scope to the INTERNAL_PLUGINS for-loop inside InstanceState.make, not the
    # array definition or the prepPlugin helper (which legitimately uses .catch).
    loop_match = re.search(
        r"for\s*\(\s*const\s+plugin\s+of\s+INTERNAL_PLUGINS\s*\)([\s\S]*?)(?=\n\s*const\s+plugins\s*=)",
        src,
    )
    assert loop_match, "Could not find the for-of INTERNAL_PLUGINS loop"
    loop_body = loop_match.group(1)
    assert ".catch(" not in loop_body, \
        "Plugin loading still uses .catch() — should use Effect.tryPromise"
    assert "Effect.tryPromise" in loop_body, \
        "Plugin loading doesn't use Effect.tryPromise for error handling"


# [pr_diff] fail_to_pass
def test_trigger_yields_hooks_individually():
    """The trigger helper must yield each hook call individually, not batch in one Effect.promise."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/opencode/src/plugin/index.ts', 'utf8');

// Find the trigger function by its tracing label
const labelIdx = src.indexOf('"Plugin.trigger"');
if (labelIdx === -1) { console.error('Plugin.trigger function not found'); process.exit(1); }

const chunk = src.slice(labelIdx, labelIdx + 1000);
const returnIdx = chunk.indexOf('return output');
if (returnIdx === -1) { console.error('Could not find return output in trigger'); process.exit(1); }
const trigger = chunk.slice(0, returnIdx + 'return output'.length);

// Old pattern: Effect.promise(async () => { for ... }) — async wrapper around for loop
// New pattern: for loop with yield* Effect.promise(() => fn(...)) per hook
const asyncIdx = trigger.indexOf('async () =>');
const forIdx = trigger.indexOf('for (');
if (asyncIdx !== -1 && forIdx !== -1 && asyncIdx < forIdx) {
    console.error('trigger wraps hooks in Effect.promise(async () => { for ... }) — should yield individually');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_config_default_layer_provided():
    """Config.defaultLayer must be provided in the Plugin's defaultLayer composition."""
    src = _plugin_src()
    layer_match = re.search(r"defaultLayer\s*=.*", src)
    assert layer_match, "Could not find defaultLayer definition"
    assert "Config.defaultLayer" in layer_match.group(0), \
        "Config.defaultLayer not provided in Plugin's defaultLayer — missing layer dependency"


# [pr_diff] fail_to_pass
def test_config_hook_uses_effect_ignore():
    """Config hook error isolation must use Effect.tryPromise piped through Effect.ignore."""
    r = _run_node("""
import { readFileSync } from 'fs';
const src = readFileSync('packages/opencode/src/plugin/index.ts', 'utf8');

// Find the config hook notification section by its error message
const marker = 'plugin config hook failed';
const markerIdx = src.indexOf(marker);
if (markerIdx === -1) { console.error('Config hook error logging not found'); process.exit(1); }

const start = Math.max(0, markerIdx - 500);
const end = Math.min(src.length, markerIdx + marker.length + 500);
const section = src.slice(start, end);

// Must NOT use bare try { ... } catch pattern.
// Note: Effect.tryPromise({ try: ... }) uses 'try:' not 'try {', so this distinguishes them.
if (section.includes('try {') && !section.includes('Effect.tryPromise')) {
    console.error('Config hook still uses try/catch — should use Effect.tryPromise');
    process.exit(1);
}

// Must pipe through Effect.ignore for error isolation
if (!section.includes('Effect.ignore')) {
    console.error('Config hook errors not piped through Effect.ignore');
    process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Node check failed:\n{r.stdout}\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_bus_uses_yielded_service():
    """Error publishing must use the yielded bus service, not the Bus.publish() async facade."""
    src = _plugin_src()
    body = _instance_state_body(src)
    # Bus.publish( is the async facade — the fix uses bus.publish( (yielded instance)
    assert "Bus.publish(" not in body, \
        "Bus.publish() async facade still used in InstanceState.make — should use yielded bus.publish()"
    # Verify the yielded bus instance is actually used for publishing
    assert "bus.publish(" in body or "bus.publish (" in body, \
        "Yielded bus service not used for publishing errors"


# [pr_diff] fail_to_pass
def test_auth_override_test_updated():
    """The auth-override test regex must be updated to match Effect.tryPromise + Effect.ignore pattern."""
    test_src = _read(TEST_FILE)
    assert "Effect.tryPromise" in test_src, \
        "Test file not updated to match Effect.tryPromise pattern"
    assert "Effect.ignore" in test_src, \
        "Test file not updated to match Effect.ignore pattern"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests - actual CI commands)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    bun = _ensure_bun()
    env = _bun_env()
    # Install dependencies first
    r = subprocess.run(
        [bun, "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    if r.returncode != 0:
        # Try without frozen lockfile if it fails
        r = subprocess.run(
            [bun, "install"],
            capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
        )
    r = subprocess.run(
        [bun, "run", "typecheck"],
        capture_output=True, text=True, timeout=600, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_auth_override_test():
    """Repo's auth-override plugin test passes (pass_to_pass).

    This test validates the plugin config hook error isolation pattern,
    which is directly related to the modified plugin/index.ts code.
    """
    bun = _ensure_bun()
    env = _bun_env()
    # Install dependencies first
    r = subprocess.run(
        [bun, "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    if r.returncode != 0:
        r = subprocess.run(
            [bun, "install"],
            capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
        )
    r = subprocess.run(
        [bun, "test", "test/plugin/auth-override.test.ts"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/packages/opencode", env=env,
    )
    assert r.returncode == 0, f"Auth-override test failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_plugin_tests():
    """Repo's plugin tests pass (pass_to_pass).

    Runs all plugin-related tests to verify plugin loading and lifecycle
    functionality remains intact after changes.
    """
    bun = _ensure_bun()
    env = _bun_env()
    # Install dependencies first
    r = subprocess.run(
        [bun, "install", "--frozen-lockfile"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    if r.returncode != 0:
        r = subprocess.run(
            [bun, "install"],
            capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
        )
    r = subprocess.run(
        [bun, "test", "test/plugin/"],
        capture_output=True, text=True, timeout=600, cwd=f"{REPO}/packages/opencode", env=env,
    )
    assert r.returncode == 0, f"Plugin tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Pass-to-pass (regression)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_dynamic_server_import_preserved():
    """Dynamic import of server module must still be present."""
    src = _plugin_src()
    assert 'import("../server/server")' in src or "import('../server/server')" in src, \
        "Dynamic server import was removed — this is needed for lazy loading"


# [repo_tests] pass_to_pass
def test_error_publishing_preserved():
    """Session.Event.Error publishing must still be present for plugin load failures."""
    src = _plugin_src()
    assert "Session.Event.Error" in src, \
        "Session.Event.Error publishing removed — error reporting broken"


# [repo_tests] pass_to_pass
def test_hook_registration_preserved():
    """Hook push/registration logic must still be present."""
    src = _plugin_src()
    body = _instance_state_body(src)
    assert "hooks.push(" in body, \
        "Hook registration (hooks.push) removed — plugins won't register"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:45 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_config_accessed_via_effect_service():
    """Config must be accessed by yielding the Effect service, not via async facade.

    packages/opencode/AGENTS.md:45: 'prefer yielding existing Effect services over dropping down to ad hoc platform APIs'
    """
    src = _plugin_src()
    assert "Config.waitForDependencies()" not in src, \
        "Config.waitForDependencies() async facade still used — should yield Config.Service"
    assert re.search(r"\bconfig\.\w+", src), \
        "No usage of yielded config service instance found"


# [agent_config] fail_to_pass — AGENTS.md:12 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_no_try_catch_in_plugin_service():
    """No try/catch blocks in the InstanceState.make closure.

    AGENTS.md:12: 'Avoid try/catch where possible'
    The fix replaces all try/catch with Effect.tryPromise error handling.
    """
    src = _plugin_src()
    body = _instance_state_body(src)
    # The base code has try { await (hook as any).config?.(cfg) } catch (err) {
    # The fix replaces it with Effect.tryPromise(...).pipe(Effect.ignore)
    try_blocks = list(re.finditer(r"\btry\s*\{", body))
    assert len(try_blocks) == 0, \
        f"Found {len(try_blocks)} try/catch block(s) in InstanceState.make — use Effect.tryPromise instead"


# [agent_config] pass_to_pass — AGENTS.md:70 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_no_let_in_instance_state():
    """No let declarations in InstanceState.make body — prefer const.

    AGENTS.md:70: 'Prefer const over let. Use ternaries or early returns instead of reassignment.'
    """
    src = _plugin_src()
    body = _instance_state_body(src)
    let_decls = list(re.finditer(r"\blet\s+\w", body))
    assert len(let_decls) == 0, \
        f"Found {len(let_decls)} 'let' declaration(s) in InstanceState.make — use const instead"


# [agent_config] pass_to_pass — AGENTS.md:84 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_no_else_in_instance_state():
    """No else statements in InstanceState.make body — use early returns or continue.

    AGENTS.md:84: 'Avoid else statements. Prefer early returns.'
    """
    src = _plugin_src()
    body = _instance_state_body(src)
    else_matches = list(re.finditer(r"\belse\b", body))
    assert len(else_matches) == 0, \
        f"Found {len(else_matches)} 'else' statement(s) in InstanceState.make — avoid else, use early return/continue"


# [agent_config] pass_to_pass — AGENTS.md:13 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_limited_as_any_usage():
    """Usage of 'as any' should be minimal (max 3 in the plugin file).

    AGENTS.md:13: 'Avoid using the any type'
    """
    src = _plugin_src()
    count = len(re.findall(r"\bas\s+any\b", src))
    assert count <= 3, f"Found {count} 'as any' casts — AGENTS.md says avoid the any type (max 3 allowed)"
