"""
Task: react-eprh-prepare-for-700
Repo: facebook/react @ 9724e3e66e4ad3cc82c728e5c732c21986825b06
PR:   34757

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
INDEX_TS = Path(REPO) / "packages/eslint-plugin-react-hooks/src/index.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via subprocess
# ---------------------------------------------------------------------------

def test_recommended_config_rules():
    """recommended config must use allRuleConfigs (compiler rules), not basicRuleConfigs."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys

content = open('/workspace/react/packages/eslint-plugin-react-hooks/src/index.ts').read()

# Extract config entries from the 'const configs = { ... }' block.
# Each entry has the form:
#   'config-name': {
#     plugins,
#     rules: variableName,
#   },
# or for unquoted keys:
#   configName: {
#     plugins,
#     rules: variableName,
#   },
entries = re.findall(
    r"['\"]?([\\w/'.-]+?)['\"]?\\s*:\\s*\\{\\s*\\n\\s*plugins,?\\s*\\n\\s*rules:\\s*(\\w+)",
    content,
)
config_map = dict(entries)
print(f"Config entries: {config_map}")

if 'recommended' not in config_map:
    print("ERROR: 'recommended' config not found in configs object")
    sys.exit(1)

if config_map['recommended'] != 'allRuleConfigs':
    print(f"ERROR: 'recommended' uses {config_map['recommended']}, expected allRuleConfigs")
    sys.exit(1)

print("PASS")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_legacy_configs_not_in_configs_object():
    """Legacy configs (recommended-legacy, recommended-latest-legacy, flat/recommended) must be removed."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys

content = open('/workspace/react/packages/eslint-plugin-react-hooks/src/index.ts').read()

# Extract all quoted config key names from the entire file
# These appear as 'key-name': { or "key-name": {
all_keys = re.findall(r"'([\\w/'.-]+?)'\\s*:", content)

removed = ['recommended-legacy', 'recommended-latest-legacy', 'flat/recommended']
for cfg in removed:
    if cfg in all_keys:
        print(f"ERROR: removed config '{cfg}' still present as config key")
        sys.exit(1)

print("PASS: no removed configs found")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_plugin_meta_version_field():
    """Plugin meta object must include a version field with a semver string."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys

content = open('/workspace/react/packages/eslint-plugin-react-hooks/src/index.ts').read()

# Find the meta block in the plugin definition
meta_match = re.search(r'meta\\s*:\\s*\\{([\\s\\S]*?)\\}', content)
if not meta_match:
    print("ERROR: could not find plugin meta block")
    sys.exit(1)

meta_body = meta_match.group(1)

# Check for a version field with a semver-like value
version_match = re.search(r"version\\s*:\\s*['\\"](\\d+\\.\\d+\\.\\d+)['\"]", meta_body)
if not version_match:
    print(f"ERROR: no version field with semver value in meta: {meta_body.strip()}")
    sys.exit(1)

print(f"PASS: meta.version = {version_match.group(1)}")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_package_json_version_bumped():
    """package.json version must be >= 7.0.0 (bumped from 5.x/6.x)."""
    r = subprocess.run(
        ["python3", "-c", """
import json, sys

pkg = json.load(open('/workspace/react/packages/eslint-plugin-react-hooks/package.json'))
version = pkg.get('version', '')
parts = version.split('.')
major = int(parts[0]) if parts else 0

if major < 7:
    print(f"ERROR: package.json version is {version}, expected >= 7.0.0")
    sys.exit(1)

print(f"PASS: version = {version}")
"""],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

def test_recommended_latest_still_exists():
    """The 'recommended-latest' config must still be defined."""
    content = INDEX_TS.read_text()
    assert "'recommended-latest'" in content, (
        "index.ts must still define 'recommended-latest' config"
    )


def test_plugin_exports_structure():
    """Plugin must still export rules, configs, and meta."""
    content = INDEX_TS.read_text()
    assert "rules," in content or "rules:" in content, (
        "Plugin must export rules"
    )
    assert "configs," in content or "configs:" in content, (
        "Plugin must export configs"
    )
    assert "meta:" in content or "meta," in content, (
        "Plugin must export meta"
    )
