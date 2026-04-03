"""
Task: rabbitmq-modulus-hash-core-stable-routing
Repo: rabbitmq/rabbitmq-server @ 713ecee4846a2816cf828e877820f0f509674f67
PR:   15849

Move the x-modulus-hash exchange type from the rabbitmq_sharding plugin
to core rabbit, add stable routing via sorted destinations, and update
the sharding plugin README accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/rabbitmq-server"

CORE_MODULE = Path(REPO) / "deps" / "rabbit" / "src" / "rabbit_exchange_type_modulus_hash.erl"
SHARDING_MODULE = Path(REPO) / "deps" / "rabbitmq_sharding" / "src" / "rabbit_sharding_exchange_type_modulus_hash.erl"
SHARDING_README = Path(REPO) / "deps" / "rabbitmq_sharding" / "README.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code changes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_module_exists_and_exports_route():
    """Core rabbit must have an x-modulus-hash exchange module that exports route/3."""
    assert CORE_MODULE.exists(), (
        f"Expected {CORE_MODULE.relative_to(REPO)} to exist"
    )
    content = CORE_MODULE.read_text()
    assert "-module(rabbit_exchange_type_modulus_hash)" in content, (
        "Module must declare -module(rabbit_exchange_type_modulus_hash)"
    )
    # route must be exported (either in -export list or via export_all)
    assert "route" in content, "Module must export a route function"


# [pr_diff] fail_to_pass
def test_route_sorts_destinations_for_stability():
    """The route function must sort destinations to guarantee stable routing."""
    assert CORE_MODULE.exists(), (
        f"Expected {CORE_MODULE.relative_to(REPO)} to exist"
    )
    content = CORE_MODULE.read_text()
    # Extract the route function body (from 'route(' to the next top-level function)
    # The key behavioral change: destinations must be sorted before selection
    has_sort = "lists:sort" in content or "lists:usort" in content
    assert has_sort, (
        "The route function must sort destinations (lists:sort or lists:usort) "
        "to ensure stable routing across node restarts"
    )


# [pr_diff] fail_to_pass
def test_boot_step_registers_in_core():
    """Core module must have a rabbit_boot_step registering x-modulus-hash."""
    assert CORE_MODULE.exists(), (
        f"Expected {CORE_MODULE.relative_to(REPO)} to exist"
    )
    content = CORE_MODULE.read_text()
    assert "rabbit_boot_step" in content, (
        "Core module must have a -rabbit_boot_step attribute"
    )
    assert "x-modulus-hash" in content, (
        "Boot step must register the <<\"x-modulus-hash\">> exchange type"
    )


# [pr_diff] fail_to_pass
def test_sharding_plugin_no_longer_registers_exchange():
    """The sharding plugin must NOT register x-modulus-hash (avoid duplicate)."""
    if not SHARDING_MODULE.exists():
        # File deleted entirely — that's the cleanest solution
        return
    content = SHARDING_MODULE.read_text()
    # If the file still exists, it must not have a boot_step for x-modulus-hash
    has_boot_step = "rabbit_boot_step" in content and "x-modulus-hash" in content
    assert not has_boot_step, (
        "Sharding plugin must not register x-modulus-hash exchange type "
        "(it is now registered in core rabbit)"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — module structure
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_module_implements_behaviour():
    """Core module must implement the rabbit_exchange_type behaviour with all callbacks."""
    assert CORE_MODULE.exists(), (
        f"Expected {CORE_MODULE.relative_to(REPO)} to exist"
    )
    content = CORE_MODULE.read_text()
    assert content.strip(), "Module file must not be empty"
    assert "-behaviour(rabbit_exchange_type)" in content or "-behavior(rabbit_exchange_type)" in content, (
        "Must declare the rabbit_exchange_type behaviour"
    )
    for callback in ["description", "validate", "create", "delete",
                     "add_binding", "remove_bindings", "policy_changed"]:
        assert callback in content, f"Must implement {callback} callback"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
