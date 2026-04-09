"""
Task: react-eprh-prepare-for-700
Repo: facebook/react @ 9724e3e66e4ad3cc82c728e5c732c21986825b06
PR:   34757

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path
import re
import json

REPO = "/workspace/react"
INDEX_TS = Path(REPO) / "packages/eslint-plugin-react-hooks/src/index.ts"
PACKAGE_JSON = Path(REPO) / "packages/eslint-plugin-react-hooks/package.json"
README_MD = Path(REPO) / "packages/eslint-plugin-react-hooks/README.md"
CHANGELOG_MD = Path(REPO) / "packages/eslint-plugin-react-hooks/CHANGELOG.md"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests
# ---------------------------------------------------------------------------

def test_recommended_config_rules():
    """recommended config must use allRuleConfigs (compiler rules), not basicRuleConfigs."""
    content = INDEX_TS.read_text()

    # Extract config entries - look for patterns like 'config-name': { ... rules: variableName }
    # Match both 'quoted' and unquoted keys
    entries = re.findall(
        r'["\']?([\w/\'.-]+?)["\']?\s*:\s*\{[^}]*rules:\s*(\w+)',
        content,
    )
    config_map = dict(entries)
    print(f"Config entries: {config_map}")

    assert 'recommended' in config_map, "'recommended' config not found in configs object"
    assert config_map['recommended'] == 'allRuleConfigs', \
        f"'recommended' uses {config_map['recommended']}, expected allRuleConfigs"


def test_legacy_configs_not_in_configs_object():
    """Legacy configs (recommended-legacy, recommended-latest-legacy, flat/recommended) must be removed."""
    content = INDEX_TS.read_text()

    # Extract all quoted config key names from the entire file
    all_keys = re.findall(r"'([\w/'.-]+?)'\s*:", content)

    removed = ['recommended-legacy', 'recommended-latest-legacy', 'flat/recommended']
    for cfg in removed:
        assert cfg not in all_keys, f"removed config '{cfg}' still present as config key"


def test_plugin_meta_version_field():
    """Plugin meta object must include a version field with a semver string."""
    content = INDEX_TS.read_text()

    # Find the meta block in the plugin definition
    meta_match = re.search(r'meta\s*:\s*\{([\s\S]*?)\}', content)
    assert meta_match, "could not find plugin meta block"

    meta_body = meta_match.group(1)

    # Check for a version field with a semver-like value
    version_match = re.search(r"version\s*:\s*['\"](\d+\.\d+\.\d+)['\"]", meta_body)
    assert version_match, f"no version field with semver value in meta: {meta_body.strip()}"


def test_package_json_version_bumped():
    """package.json version must be >= 7.0.0 (bumped from 5.x/6.x)."""
    pkg = json.load(open(PACKAGE_JSON))
    version = pkg.get('version', '')
    parts = version.split('.')
    major = int(parts[0]) if parts else 0

    assert major >= 7, f"package.json version is {version}, expected >= 7.0.0"


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


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repo CI/CD checks that should pass on base commit
# ---------------------------------------------------------------------------

def test_repo_index_ts_syntax():
    """Repo's eslint-plugin index.ts has valid TypeScript syntax (pass_to_pass)."""
    content = INDEX_TS.read_text()

    # Check for basic TypeScript structure
    required_patterns = [
        r'const\s+\w+\s*=',
        r'export\s+default',
        r'rules',
        r'configs',
        r'meta',
    ]

    for pattern in required_patterns:
        assert re.search(pattern, content), f"Missing pattern: {pattern}"

    # Verify balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, \
        f"Unbalanced braces - {open_braces} open, {close_braces} close"


def test_repo_package_json_valid():
    """Repo's eslint-plugin package.json is valid JSON (pass_to_pass)."""
    pkg = json.load(open(PACKAGE_JSON))

    # Verify required fields exist
    required_fields = ['name', 'version', 'description', 'main']
    for field in required_fields:
        assert field in pkg, f"Missing required field: {field}"

    # Verify name is correct
    assert pkg['name'] == 'eslint-plugin-react-hooks', \
        f"Unexpected package name: {pkg['name']}"


def test_repo_readme_structure():
    """Repo's eslint-plugin README.md has expected structure (pass_to_pass)."""
    content = README_MD.read_text()

    # Check for expected sections (title may have backticks)
    required_sections = [
        r'eslint-plugin-react-hooks',
        r'## Installation',
        r'## Flat Config',
        r'## Legacy Config',
    ]

    for pattern in required_sections:
        assert re.search(pattern, content, re.IGNORECASE), f"Missing section: {pattern}"

    # Check for recommended config references
    assert 'recommended' in content, "No 'recommended' config references found"


def test_repo_changelog_exists():
    """Repo's eslint-plugin CHANGELOG.md exists and has structure (pass_to_pass)."""
    assert CHANGELOG_MD.exists(), "CHANGELOG.md does not exist"

    content = CHANGELOG_MD.read_text()

    # Check for version headers
    version_pattern = r'##\s+\d+\.\d+\.\d+'
    versions = re.findall(version_pattern, content)

    assert versions, "No version headers found in CHANGELOG"


def test_repo_fixtures_exist():
    """Repo's eslint fixtures exist and have valid structure (pass_to_pass)."""
    fixtures = ['eslint-v6', 'eslint-v7', 'eslint-v8']
    count = 0

    for fixture in fixtures:
        eslintrc = Path(REPO) / f'fixtures/{fixture}/.eslintrc.json'
        if eslintrc.exists():
            config = json.loads(eslintrc.read_text())
            count += 1

    assert count > 0, "No valid eslint fixtures found"
