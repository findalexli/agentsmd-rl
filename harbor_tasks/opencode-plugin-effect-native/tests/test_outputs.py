"""
Task: opencode-plugin-effect-native
Repo: anomalyco/opencode @ bb8d2cdd108618c1057a8890ac1e655198db866e
PR:   #19365

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
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
    src = _plugin_src()
    make_idx = src.index("InstanceState.make")
    after_make = src[make_idx:make_idx + 3000]
    # Each Effect.promise should be small (dynamic import, single hook call) — not contain
    # Config.get(), plugin loops, or other heavy logic
    effect_promises = list(re.finditer(r"Effect\.promise\s*\(\s*(?:async\s*)?\(\)\s*=>", after_make))
    for ep in effect_promises:
        start = ep.end()
        depth = 1
        pos = start
        while pos < len(after_make) and depth > 0:
            if after_make[pos] == "(":
                depth += 1
            elif after_make[pos] == ")":
                depth -= 1
            pos += 1
        promise_body = after_make[start:pos]
        assert "Config.get()" not in promise_body, \
            "Config.get() still inside Effect.promise — monolithic wrapper not removed"
        assert "INTERNAL_PLUGINS" not in promise_body, \
            "Plugin loading loop still inside single Effect.promise — not broken out"


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
    src = _plugin_src()
    # trigger is: const trigger = Effect.fn("Plugin.trigger")(function* <...>(...) { ... return output })
    trigger_match = re.search(
        r'Effect\.fn\(\s*"Plugin\.trigger"\s*\)\s*\(\s*function\*[\s\S]*?return\s+output\s*\}',
        src,
    )
    assert trigger_match, "Could not find Plugin.trigger function"
    trigger_body = trigger_match.group(0)
    # Old pattern: Effect.promise(async () => { for ... await fn() }) — one promise wrapping loop
    # New pattern: for loop with yield* Effect.promise(() => fn(input, output)) per hook
    promises = list(re.finditer(r"Effect\.promise\s*\(", trigger_body))
    if promises:
        for_match = re.search(r"for\s*\(", trigger_body)
        assert for_match, "trigger must have a for loop over hooks"
        for p in promises:
            assert p.start() > for_match.start(), \
                "Effect.promise wraps the for loop — should be inside it (per-hook yield)"


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
    src = _plugin_src()
    # Find the config hook notification section
    config_hook_match = re.search(
        r"(?:Notify|notify|config hook|plugin config)[\s\S]{0,500}?\.config\?\.",
        src, re.IGNORECASE,
    )
    if not config_hook_match:
        config_hook_match = re.search(r"hook\b[\s\S]{0,100}?\.config\?\.", src)
    assert config_hook_match, "Could not find config hook notification section"
    start = max(0, config_hook_match.start() - 200)
    end = min(len(src), config_hook_match.end() + 500)
    section = src[start:end]
    assert "try {" not in section or "Effect.tryPromise" in section, \
        "Config hook still uses try/catch — should use Effect.tryPromise"
    assert "Effect.ignore" in section, \
        "Config hook errors not piped through Effect.ignore"


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


# [agent_config] pass_to_pass — AGENTS.md:13 @ bb8d2cdd108618c1057a8890ac1e655198db866e
def test_limited_as_any_usage():
    """Usage of 'as any' should be minimal (max 3 in the plugin file).

    AGENTS.md:13: 'Avoid using the any type'
    """
    src = _plugin_src()
    count = len(re.findall(r"\bas\s+any\b", src))
    assert count <= 3, f"Found {count} 'as any' casts — AGENTS.md says avoid the any type (max 3 allowed)"
