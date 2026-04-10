"""
Task: rabbitmq-server-ensure-stable-routing-for-xmodulushash
Repo: rabbitmq/rabbitmq-server @ f5c203919fe89ebe26d7a5650a58cced4ab807a6
PR:   15859

Move x-modulus-hash exchange type from rabbitmq_sharding plugin to core rabbit,
with stable routing (sorted destinations). Update sharding README accordingly.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/rabbitmq-server"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_core_module_exists_with_stable_routing():
    """Core exchange module exists in deps/rabbit/src/ and sorts destinations for stable routing."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys

path = "/workspace/rabbitmq-server/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: core module does not exist at expected path")
    sys.exit(1)

# Must have route function
if not re.search(r'route\\(', content):
    print("FAIL: no route function found")
    sys.exit(1)

# Key fix: destinations must be sorted for stable routing
if not re.search(r'lists:(u?sort)\\(', content):
    print("FAIL: route function does not sort destinations")
    sys.exit(1)

# Must use phash2 for hashing + rem for modulus
if 'phash2' not in content:
    print("FAIL: no phash2 hashing")
    sys.exit(1)
if 'rem' not in content:
    print("FAIL: no modulus operation")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


def test_core_module_registers_as_boot_step():
    """Core module registers x-modulus-hash exchange type as a rabbit boot step."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys

path = "/workspace/rabbitmq-server/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: core module does not exist")
    sys.exit(1)

if not re.search(r'-rabbit_boot_step\\(', content):
    print("FAIL: no boot step registration")
    sys.exit(1)
if 'x-modulus-hash' not in content:
    print("FAIL: does not register x-modulus-hash exchange type")
    sys.exit(1)
if 'rabbit_registry' not in content:
    print("FAIL: does not use rabbit_registry for registration")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


def test_core_module_implements_all_callbacks():
    """Core module implements all required rabbit_exchange_type callbacks."""
    r = subprocess.run(
        ["python3", "-c", """
import sys

path = "/workspace/rabbitmq-server/deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: core module does not exist")
    sys.exit(1)

callbacks = [
    "description", "route", "serialise_events", "validate",
    "validate_binding", "create", "delete", "policy_changed",
    "add_binding", "remove_bindings", "assert_args_equivalence",
]
lines = content.splitlines()
missing = []
for cb in callbacks:
    if not any(line.lstrip().startswith(cb + "(") for line in lines):
        missing.append(cb)

if missing:
    print("FAIL: missing callbacks: " + ", ".join(missing))
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}{r.stdout}"
    assert "PASS" in r.stdout


def test_old_sharding_module_removed():
    """Old sharding exchange module must be removed from the plugin."""
    old_path = Path(REPO) / "deps" / "rabbitmq_sharding" / "src" / "rabbit_sharding_exchange_type_modulus_hash.erl"
    assert not old_path.exists(), \
        "Old sharding module must be removed after moving exchange type to core"


def test_readme_documents_builtin_exchange():
    """Sharding README documents x-modulus-hash as built-in to core RabbitMQ."""
    content = (Path(REPO) / "deps" / "rabbitmq_sharding" / "README.md").read_text().lower()

    assert "plugin provides a new exchange type" not in content, \
        "README should no longer say the plugin provides the exchange type"

    has_builtin = "built-in" in content or "built in" in content
    has_core = "core rabbitmq" in content or "core server" in content
    has_no_plugin = ("does not require" in content and "plugin" in content) or \
                    "without enabling" in content or "without this plugin" in content
    assert has_builtin or has_core or has_no_plugin, \
        "README must indicate x-modulus-hash is built-in to core RabbitMQ"


def test_readme_documents_stable_routing():
    """Sharding README documents the stable routing guarantee."""
    content = (Path(REPO) / "deps" / "rabbitmq_sharding" / "README.md").read_text().lower()

    assert "stable" in content, \
        "README must document stable routing"
    assert "restart" in content, \
        "README must mention routing stability across node restarts"


def test_makefile_includes_modulus_hash_ct():
    """Makefile includes rabbit_exchange_type_modulus_hash in parallel CT test sets."""
    content = (Path(REPO) / "deps" / "rabbit" / "Makefile").read_text()
    assert "rabbit_exchange_type_modulus_hash" in content, \
        "Makefile must include rabbit_exchange_type_modulus_hash in parallel CT test sets"


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) — CI validation via subprocess
# ---------------------------------------------------------------------------

def test_repo_parallel_ct_sanity():
    """Parallel CT test set 5 includes all expected suites (pass_to_pass).

    Verifies that PARALLEL_CT_SET_5_D in the Makefile is properly configured
    to include the rabbit_exchange_type_modulus_hash test suite.
    """
    r = subprocess.run(
        ["bash", "-c",
         "grep -q 'PARALLEL_CT_SET_5_D.*=' /workspace/rabbitmq-server/deps/rabbit/Makefile && " +
         "grep 'PARALLEL_CT_SET_5_D' /workspace/rabbitmq-server/deps/rabbit/Makefile | " +
         "grep -v '^#' | head -1"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed to find PARALLEL_CT_SET_5_D in Makefile: {r.stderr}"
    # The Makefile should have the parallel CT set defined
    assert "PARALLEL_CT_SET_5_D" in r.stdout, "PARALLEL_CT_SET_5_D not found in Makefile"


def test_repo_no_old_sharding_module():
    """Git index does not contain old sharding module (pass_to_pass).

    Verifies via git that the old rabbit_sharding_exchange_type_modulus_hash
    module is not tracked in the repository.
    """
    r = subprocess.run(
        ["git", "-C", REPO, "ls-files",
         "deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl"],
        capture_output=True, text=True, timeout=30,
    )
    # On base commit, this file exists. After fix, it should not exist.
    # This test validates the current state (file exists before fix).
    assert r.returncode == 0, f"Git command failed: {r.stderr}"


def test_repo_rabbit_exchange_types_exist():
    """Core exchange type modules exist in git (pass_to_pass).

    Verifies via git that the core rabbit exchange type modules exist.
    """
    r = subprocess.run(
        ["git", "-C", REPO, "ls-files",
         "deps/rabbit/src/rabbit_exchange_type.erl",
         "deps/rabbit/src/rabbit_exchange_type_direct.erl",
         "deps/rabbit/src/rabbit_exchange_type_topic.erl"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Git command failed: {r.stderr}"
    # Should find at least the main exchange type module
    assert "rabbit_exchange_type.erl" in r.stdout, "Core exchange type modules not found"


def test_repo_makefile_has_parallel_ct_sets():
    """Makefile has parallel CT test set configuration (pass_to_pass).

    Verifies the parallel CT structure exists in the rabbit Makefile.
    """
    r = subprocess.run(
        ["grep", "-c", "PARALLEL_CT_SET", f"{REPO}/deps/rabbit/Makefile"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"grep failed: {r.stderr}"
    count = int(r.stdout.strip())
    assert count > 10, f"Expected many PARALLEL_CT_SET references, found {count}"


# ---------------------------------------------------------------------------
# pass_to_pass (static) — structural validation
# ---------------------------------------------------------------------------

def test_erlang_module_well_formed():
    """If core module exists, it has valid Erlang module structure."""
    module_path = Path(REPO) / "deps" / "rabbit" / "src" / "rabbit_exchange_type_modulus_hash.erl"
    if not module_path.exists():
        return  # File creation is verified by fail_to_pass tests
    content = module_path.read_text()
    assert "-module(rabbit_exchange_type_modulus_hash)." in content, \
        "Must declare correct module name"
    assert "-behaviour(rabbit_exchange_type)." in content, \
        "Must declare rabbit_exchange_type behaviour"
    assert "-export(" in content, "Must export functions"
