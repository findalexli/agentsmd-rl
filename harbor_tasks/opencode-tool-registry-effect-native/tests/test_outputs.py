"""
Task: opencode-tool-registry-effect-native
Repo: anomalyco/opencode @ d2bfa92e7438eb7ac7c4e2d72fca708f27c52ba3
PR:   anomalyco/opencode#19363

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

AST-only because: TypeScript + Effect framework deps not installed in container.
"""

import re
from pathlib import Path

REPO = "/workspace/opencode"
REGISTRY = Path(REPO) / "packages/opencode/src/tool/registry.ts"
PLUGIN = Path(REPO) / "packages/opencode/src/plugin/index.ts"


def _strip_comments(code: str) -> str:
    """Remove single-line comments, block comments, and string literals."""
    s = re.sub(r"//[^\n]*", "", code)
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.DOTALL)
    s = re.sub(r'"[^"]*"', '""', s)
    s = re.sub(r"'[^']*'", "''", s)
    s = re.sub(r"`[^`]*`", "``", s)
    return s


def _state_init_block(code: str) -> str:
    """Extract the InstanceState.make closure body."""
    match = re.search(r"InstanceState\.make.*?return\s*\{", code, re.DOTALL)
    assert match, "Cannot find InstanceState.make block"
    return match.group(0)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_no_facade_in_state_init():
    """Module-level Config/Plugin facades must not be called in InstanceState.make."""
    code = _strip_comments(REGISTRY.read_text())
    block = _state_init_block(code)

    # Check Effect.promise blocks don't wrap facades
    promise_blocks = list(re.finditer(r"Effect\.promise\s*\(", block))
    for pb in promise_blocks:
        nearby = block[pb.start() : pb.start() + 500]
        assert not any(
            facade in nearby
            for facade in ["Config.directories", "Config.waitForDependencies", "Plugin.list"]
        ), "Config/Plugin facades still wrapped in Effect.promise in state init"

    # Module-level facades must not be called directly either (should use yielded instance)
    for facade in ["Config.directories()", "Config.waitForDependencies()", "Plugin.list()"]:
        assert facade not in block, (
            f"Module-level facade {facade} called directly in state init "
            "— should use yielded service instance"
        )


# [pr_diff] fail_to_pass
def test_all_is_effectful():
    """all() must be an Effect function (Effect.fn or Effect.gen), not async."""
    code = _strip_comments(REGISTRY.read_text())
    assert not re.search(
        r"\basync\s+function\s+all\s*\(", code
    ), "all() is still a plain async function"
    # Positive: must be defined via Effect.fn or Effect.gen
    has_effect_fn = bool(re.search(r"\ball\s*=\s*Effect\.fn\b", code))
    has_effect_gen = bool(re.search(r"\ball\s*=\s*Effect\.gen\b", code))
    assert has_effect_fn or has_effect_gen, (
        "all() is not defined as Effect.fn or Effect.gen"
    )


# [pr_diff] fail_to_pass
def test_effect_concurrency():
    """Promise.all replaced with Effect.forEach or Effect.all for concurrent tool init."""
    code = _strip_comments(REGISTRY.read_text())
    assert "Promise.all" not in code, "Promise.all still used in registry.ts"
    # Positive: Effect concurrency primitive must be present
    has_foreach = "Effect.forEach" in code
    has_effect_all = bool(re.search(r"Effect\.all\s*\(", code))
    assert has_foreach or has_effect_all, (
        "No Effect concurrency primitive (Effect.forEach or Effect.all) found"
    )


# [pr_diff] fail_to_pass
def test_services_yielded_in_layer():
    """Config.Service and Plugin.Service must be obtained via Effect dependency graph."""
    code = _strip_comments(REGISTRY.read_text())
    for svc in ["Config.Service", "Plugin.Service"]:
        esc = re.escape(svc)
        has_yield = bool(re.search(rf"yield\*?\s+.*{esc}", code))
        has_service = bool(re.search(rf"Effect\.service\s*\(\s*{esc}", code))
        has_context = bool(re.search(rf"Context\.get\s*\(\s*{esc}", code))
        assert has_yield or has_service or has_context, (
            f"{svc} not obtained via Effect dependency graph"
        )


# [pr_diff] fail_to_pass
def test_plugin_default_layer_exported():
    """Plugin module must export defaultLayer for layer composition."""
    code = _strip_comments(PLUGIN.read_text())
    exported = bool(
        re.search(r"\bexport\s+(const|let|var)\s+defaultLayer\b", code)
        or re.search(r"\bexport\s*\{[^}]*\bdefaultLayer\b", code)
    )
    assert exported, "Plugin.defaultLayer is not exported"


# [pr_diff] fail_to_pass
def test_registry_default_layer_exported():
    """ToolRegistry must export a composed defaultLayer providing dependencies."""
    code = _strip_comments(REGISTRY.read_text())
    exported = bool(
        re.search(r"\bexport\s+(const|let|var)\s+defaultLayer\b", code)
        or re.search(r"\bexport\s*\{[^}]*\bdefaultLayer\b", code)
    )
    assert exported, "ToolRegistry.defaultLayer is not exported"


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
    for name in ["register", "ids", "tools"]:
        has_export = bool(
            re.search(rf"\bexport\s+(async\s+)?function\s+{name}\b", code)
            or re.search(rf"\bexport\s+(const|let)\s+{name}\b", code)
        )
        assert has_export, f"Public facade '{name}' is not exported"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:21 @ d2bfa92
def test_effect_fn_usage():
    """Service methods should use Effect.fn for named/traced effects (>= 3 uses)."""
    code = _strip_comments(REGISTRY.read_text())
    count = len(re.findall(r"Effect\.fn\s*\(", code))
    assert count >= 3, f"Effect.fn used only {count} times (expected >= 3)"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:21 @ d2bfa92
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
