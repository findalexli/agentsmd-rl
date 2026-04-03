"""
Task: rabbitmq-server-ensure-stable-routing-for-xmodulushash
Repo: rabbitmq/rabbitmq-server @ f5c203919fe89ebe26d7a5650a58cced4ab807a6
PR:   15859

Move x-modulus-hash exchange type from rabbitmq_sharding plugin to core rabbit,
with stable routing (sorted destinations). Update sharding README accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/rabbitmq-server"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_erlang_module_well_formed():
    """Core exchange module has valid Erlang module structure."""
    module_path = Path(REPO) / "deps" / "rabbit" / "src" / "rabbit_exchange_type_modulus_hash.erl"
    if not module_path.exists():
        return  # File not yet created; f2p tests verify existence
    content = module_path.read_text()
    # Must declare the correct module name
    assert re.search(r"-module\(rabbit_exchange_type_modulus_hash\)\.", content), \
        "Module must declare -module(rabbit_exchange_type_modulus_hash)"
    # Must declare the behaviour
    assert re.search(r"-behaviour\(rabbit_exchange_type\)\.", content), \
        "Module must declare -behaviour(rabbit_exchange_type)"
    # Must have export declarations
    assert "-export(" in content, "Module must export functions"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_module_routes_with_sorting():
    """The core exchange module must sort destinations for stable routing."""
    module_path = Path(REPO) / "deps" / "rabbit" / "src" / "rabbit_exchange_type_modulus_hash.erl"
    content = module_path.read_text()

    # The route function must exist
    assert re.search(r"route\(", content), "Module must implement route/3"

    # The key fix: destinations must be sorted before selecting one.
    # This guarantees stable routing across node restarts.
    # Accept lists:sort or lists:usort as valid sorting approaches.
    assert re.search(r"lists:(u?sort)\(", content), \
        "Route function must sort destinations for stable routing (lists:sort or lists:usort)"

    # Must use modulus hashing to pick the destination
    assert "rem" in content, "Route function must use modulus (rem) to pick destination"
    assert "phash2" in content or "erlang:phash2" in content, \
        "Route function must use phash2 for hashing"


# [pr_diff] fail_to_pass
def test_core_module_registers_exchange():
    """The core module registers x-modulus-hash as a boot step in rabbit."""
    module_path = Path(REPO) / "deps" / "rabbit" / "src" / "rabbit_exchange_type_modulus_hash.erl"
    content = module_path.read_text()

    # Must register x-modulus-hash exchange type
    assert "x-modulus-hash" in content, \
        "Module must register the x-modulus-hash exchange type"

    # Must be a rabbit boot step (not sharding boot step)
    assert re.search(r"-rabbit_boot_step\(", content), \
        "Module must register as a rabbit boot step"

    # Must register with rabbit_registry
    assert "rabbit_registry" in content, \
        "Module must register exchange type with rabbit_registry"


# [pr_diff] fail_to_pass

    required_callbacks = [
        "description",
        "route",
        "serialise_events",
        "validate",
        "validate_binding",
        "create",
        "delete",
        "policy_changed",
        "add_binding",
        "remove_bindings",
        "assert_args_equivalence",
    ]

    for callback in required_callbacks:
        assert re.search(rf"^{callback}\(", content, re.MULTILINE), \
            f"Module must implement {callback} callback"


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # The README must no longer say "the plugin provides" the exchange type.
    # It should indicate the exchange is built-in / core / available without the plugin.
    content_lower = content.lower()

    # Must mention the exchange is built-in or part of core RabbitMQ
    has_builtin = "built-in" in content_lower or "built in" in content_lower
    has_core = "core rabbitmq" in content_lower or "core server" in content_lower
    has_no_plugin = ("does not require" in content_lower and "plugin" in content_lower) or \
                    "without enabling" in content_lower or "without this plugin" in content_lower
    assert has_builtin or has_core or has_no_plugin, \
        "README must indicate x-modulus-hash is built-in to core RabbitMQ, not provided by the plugin"

    # Must NOT say "the plugin provides" the exchange type anymore
    assert "plugin provides a new exchange type" not in content_lower, \
        "README should no longer say the plugin provides the exchange type"


# [config_edit] fail_to_pass

    # Must mention stable routing
    assert "stable" in content_lower, \
        "README must document stable routing"

    # Must mention that same routing key goes to same queue
    has_same_queue = "same" in content_lower and ("queue" in content_lower or "destination" in content_lower)
    assert has_same_queue, \
        "README must explain that messages with the same routing key go to the same queue"

    # Must mention this works across restarts
    has_restart = "restart" in content_lower
    assert has_restart, \
        "README must mention routing stability across node restarts"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:comments_style

    for i, line in enumerate(content.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("%%") or stripped.startswith("%"):
            continue
        # Check for inline comments: non-comment code followed by %% comment
        match = re.search(r'%%', line)
        if match:
            before = line[:match.start()].strip()
            if before:
                assert False, \
                    f"Line {i}: inline comment violates CLAUDE.md rule (comments above the line): {stripped}"
