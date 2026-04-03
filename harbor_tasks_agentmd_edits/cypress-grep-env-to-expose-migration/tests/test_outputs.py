"""
Task: cypress-grep-env-to-expose-migration
Repo: cypress-io/cypress @ eb60ddcec6d92dad8ba1a1d776b249171384aa5e
PR:   33242

Migrates @cypress/grep from Cypress.env() to Cypress.expose() API.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/cypress"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be valid (no unclosed braces/strings)."""
    for relpath in [
        "npm/grep/src/plugin.ts",
        "npm/grep/src/register.ts",
    ]:
        src = Path(REPO) / relpath
        assert src.exists(), f"{relpath} must exist"
        content = src.read_text()
        assert content.count("{") == content.count("}"), \
            f"{relpath} has unbalanced braces"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code change tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_plugin_reads_from_expose():
    """plugin.ts must read filter config from config.expose, not config.env."""
    src = (Path(REPO) / "npm/grep/src/plugin.ts").read_text()

    # The interface should declare an 'expose' property
    assert re.search(r'expose\s*[\?:]', src), \
        "CypressConfigOptions interface must have an 'expose' property"

    # The function should destructure or access config.expose
    assert "config.expose" in src or "{ expose" in src, \
        "plugin() must access config.expose"

    # Should NOT read from config.env for grep values
    assert "env.grep" not in src, \
        "plugin.ts must not read grep from env (should use expose)"
    assert "env.grepTags" not in src, \
        "plugin.ts must not read grepTags from env (should use expose)"


# [pr_diff] fail_to_pass
def test_register_calls_expose():
    """register.ts must use Cypress.expose() instead of Cypress.env()."""
    src = (Path(REPO) / "npm/grep/src/register.ts").read_text()

    assert "Cypress.expose(" in src, \
        "register.ts must call Cypress.expose()"
    # Should not use Cypress.env() for getting/setting grep values
    assert "Cypress.env(" not in src, \
        "register.ts must not call Cypress.env() — use Cypress.expose()"


# [pr_diff] fail_to_pass
def test_peer_dep_updated():
    """package.json peerDependencies.cypress must require >=15.10.0."""
    pkg = json.loads((Path(REPO) / "npm/grep/package.json").read_text())
    cypress_peer = pkg.get("peerDependencies", {}).get("cypress", "")
    assert "15.10" in cypress_peer or "15.11" in cypress_peer or "16" in cypress_peer, \
        f"peerDependencies.cypress should be >=15.10.0, got: {cypress_peer}"


# [pr_diff] fail_to_pass
def test_package_json_scripts_use_expose():
    """package.json npm scripts must use --expose, not --env for grep args."""
    pkg = json.loads((Path(REPO) / "npm/grep/package.json").read_text())
    scripts = pkg.get("scripts", {})
    grep_scripts = {
        name: cmd for name, cmd in scripts.items()
        if "cypress" in cmd.lower() and ("grep" in cmd or "burn" in cmd or "Tags" in cmd)
    }
    assert len(grep_scripts) >= 5, \
        f"Expected at least 5 grep-related scripts, found {len(grep_scripts)}"
    has_expose = False
    for name, cmd in grep_scripts.items():
        assert "--env" not in cmd, \
            f"Script '{name}' still uses --env: {cmd}"
        if "--expose" in cmd:
            has_expose = True
    assert has_expose, "At least one grep script must use --expose"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must have a migration section for v5 -> v6
    assert "v5 to v6" in readme_lower or "v5 → v6" in readme_lower or \
        "from v5" in readme_lower, \
        "README must document the v5 to v6 migration"

    # Migration section must mention the key API change
    assert "expose" in readme_lower, \
        "README migration section must mention 'expose'"


# [config_edit] fail_to_pass

    # Must contain --expose in examples
    assert "--expose" in readme, \
        "README must use --expose in CLI examples"

    # Split by migration section to check main content only
    parts = re.split(r'(?i)###\s+from v5 to v6', readme, maxsplit=1)
    main_content = parts[0]

    # Main content should not use --env in cypress run commands
    for line in main_content.split('\n'):
        if 'npx cypress run' in line and '--env' in line:
            assert False, f"README main content still uses --env in: {line.strip()}"


# [config_edit] fail_to_pass

    # Find the defineConfig example block
    config_match = re.search(
        r'defineConfig\(\{.*?\}\)',
        readme,
        re.DOTALL,
    )
    assert config_match, "README should contain a defineConfig example"
    config_block = config_match.group(0)

    # The config should use expose: for grep settings, not env:
    # Look for lines with grep/filter settings under expose: or env:
    assert "expose:" in config_block, \
        "defineConfig example must use 'expose:' key for grep settings"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_plugin_has_real_logic():
    """plugin.ts must contain real filtering logic, not just a stub."""
    src = (Path(REPO) / "npm/grep/src/plugin.ts").read_text()
    assert "grepFilterSpecs" in src, "plugin must handle grepFilterSpecs"
    assert "shouldTestRun" in src, "plugin must call shouldTestRun"
    assert "specPattern" in src, "plugin must handle specPattern"


# [static] pass_to_pass
def test_register_has_real_logic():
    """register.ts must contain real registration logic, not just a stub."""
    src = (Path(REPO) / "npm/grep/src/register.ts").read_text()
    assert "shouldTestRun" in src, "register must call shouldTestRun"
    assert "parseGrep" in src, "register must call parseGrep"
    assert "grepBurn" in src, "register must handle grepBurn"
