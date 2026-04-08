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

import subprocess
from pathlib import Path

REPO = "/workspace/rabbitmq-server"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Python script in the repo directory."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core exchange module structure
# ---------------------------------------------------------------------------

def test_core_module_valid_exchange_type():
    """Core module must be a valid Erlang exchange type with correct structure."""
    r = _run_py(r"""
import re, sys

path = "deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: core module does not exist", file=sys.stderr)
    sys.exit(1)

# Verify module declaration
if not re.search(r'-module\(rabbit_exchange_type_modulus_hash\)', content):
    print("FAIL: missing -module(rabbit_exchange_type_modulus_hash)", file=sys.stderr)
    sys.exit(1)

# Verify behaviour declaration
if not re.search(r'-behaviou?r\(rabbit_exchange_type\)', content):
    print("FAIL: missing rabbit_exchange_type behaviour", file=sys.stderr)
    sys.exit(1)

# Extract exported function names from -export lists
exports = re.findall(r'-export\(\[([^\]]+)\]\)', content, re.DOTALL)
export_text = ' '.join(exports)
required = ['description', 'route', 'serialise_events', 'validate',
            'validate_binding', 'create', 'delete', 'policy_changed',
            'add_binding', 'remove_bindings', 'assert_args_equivalence']
missing = [f for f in required if f not in export_text]
if missing:
    print(f"FAIL: missing exports: {missing}", file=sys.stderr)
    sys.exit(1)

# Verify boot step registers x-modulus-hash
if not re.search(r'-rabbit_boot_step\(', content):
    print("FAIL: missing -rabbit_boot_step", file=sys.stderr)
    sys.exit(1)
if 'x-modulus-hash' not in content:
    print("FAIL: boot step must register x-modulus-hash", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Core module validation failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_route_sorts_destinations_for_stability():
    """Route function must sort destinations before selecting to ensure stable routing."""
    r = _run_py(r"""
import re, sys

path = "deps/rabbit/src/rabbit_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: core module does not exist", file=sys.stderr)
    sys.exit(1)

# Extract the route function body
route_match = re.search(
    r'^route\(.+?\)\s*->\s*\n(.*?)(?=^[a-z]\w*\(|\Z)',
    content, re.MULTILINE | re.DOTALL
)
if not route_match:
    print("FAIL: could not find route/3 function", file=sys.stderr)
    sys.exit(1)

route_body = route_match.group(0)

# Must call lists:sort (or lists:usort) in route body
has_sort = 'lists:sort' in route_body or 'lists:usort' in route_body
if not has_sort:
    print("FAIL: route function does not sort destinations", file=sys.stderr)
    sys.exit(1)

# Must use lists:nth for selection after sorting
if 'lists:nth' not in route_body:
    print("FAIL: route function does not use lists:nth for selection", file=sys.stderr)
    sys.exit(1)

# Sort must appear before nth (stable routing requires sort-then-select)
sort_pos = min(
    route_body.find('lists:sort') if 'lists:sort' in route_body else float('inf'),
    route_body.find('lists:usort') if 'lists:usort' in route_body else float('inf'),
)
nth_pos = route_body.find('lists:nth')
if sort_pos > nth_pos:
    print("FAIL: sort must happen before nth selection", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"Route stability validation failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — sharding plugin deregistration
# ---------------------------------------------------------------------------

def test_sharding_plugin_deregistered():
    """Sharding plugin must not register x-modulus-hash (avoid duplicate)."""
    r = _run_py(r"""
import sys

path = "deps/rabbitmq_sharding/src/rabbit_sharding_exchange_type_modulus_hash.erl"
try:
    content = open(path).read()
except FileNotFoundError:
    print("PASS: sharding module deleted")
    sys.exit(0)

# If file still exists, it must NOT have a boot_step for x-modulus-hash
if 'rabbit_boot_step' in content and 'x-modulus-hash' in content:
    print("FAIL: sharding plugin still registers x-modulus-hash", file=sys.stderr)
    sys.exit(1)

print("PASS: sharding module exists but does not register x-modulus-hash")
""")
    assert r.returncode == 0, f"Sharding deregistration check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — README documentation updates
# ---------------------------------------------------------------------------

def test_readme_documents_builtin_exchange():
    """README must reflect x-modulus-hash as a built-in/core exchange type."""
    r = _run_py(r"""
import sys

path = "deps/rabbitmq_sharding/README.md"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: README.md does not exist", file=sys.stderr)
    sys.exit(1)

# Old text must NOT be present
if 'The plugin provides a new exchange type' in content:
    print("FAIL: README still says plugin provides the exchange type", file=sys.stderr)
    sys.exit(1)

# Must describe x-modulus-hash as built-in or core
content_lower = content.lower()
is_builtin = ('built-in' in content_lower or 'builtin' in content_lower or
              'core rabbitmq' in content_lower or 'core exchange' in content_lower)
if not is_builtin:
    print("FAIL: README does not describe x-modulus-hash as built-in/core", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"README built-in check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_documents_stable_routing():
    """README must document the stable routing guarantee."""
    r = _run_py(r"""
import sys

path = "deps/rabbitmq_sharding/README.md"
try:
    content = open(path).read()
except FileNotFoundError:
    print("FAIL: README.md does not exist", file=sys.stderr)
    sys.exit(1)

content_lower = content.lower()

# Must mention stable routing
if 'stable routing' not in content_lower and 'stable' not in content_lower:
    print("FAIL: README does not mention stable routing", file=sys.stderr)
    sys.exit(1)

# Must tie stability to same routing key -> same queue or node restarts
has_guarantee = ('same routing key' in content_lower or
                 'same destination' in content_lower or
                 'node restart' in content_lower)
if not has_guarantee:
    print("FAIL: README does not document the routing stability guarantee", file=sys.stderr)
    sys.exit(1)

print("PASS")
""")
    assert r.returncode == 0, f"README stable routing check failed: {r.stderr}"
    assert "PASS" in r.stdout
