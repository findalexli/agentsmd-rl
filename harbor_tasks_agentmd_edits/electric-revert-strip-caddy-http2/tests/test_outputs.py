"""
Task: electric-revert-strip-caddy-http2
Repo: electric-sql/electric @ 617b429f0f8b9b78bed42b897092e065cf993e35
PR:   3225

Tests verify both code (Vite Caddy plugin) and config (AGENTS.md, README.md) changes.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/electric"
EXAMPLE_DIR = f"{REPO}/examples/tanstack-db-web-starter"


def _run_ts(script: str, cwd: str = EXAMPLE_DIR, timeout: int = 30) -> subprocess.CompletedProcess:
    """Write a temp TS script and run it with node --experimental-strip-types."""
    script_path = Path(cwd) / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings", str(script_path)],
            capture_output=True, text=True, timeout=timeout, cwd=cwd,
        )
    finally:
        script_path.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------

def test_vite_plugin_exports():
    """vite-plugin-caddy.ts must export caddyPlugin returning a valid Vite plugin."""
    plugin_path = Path(EXAMPLE_DIR) / "src/vite-plugin-caddy.ts"
    assert plugin_path.exists(), "vite-plugin-caddy.ts must exist"

    result = _run_ts(
        "import { caddyPlugin } from './src/vite-plugin-caddy.ts'\n"
        "const plugin = caddyPlugin()\n"
        "console.log(JSON.stringify({\n"
        "  name: plugin.name,\n"
        "  hasConfigureServer: typeof plugin.configureServer === 'function',\n"
        "  hasBuildEnd: typeof plugin.buildEnd === 'function',\n"
        "}))\n"
    )
    assert result.returncode == 0, f"Plugin import/execution failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["name"] == "vite-plugin-caddy", \
        f"Expected plugin name 'vite-plugin-caddy', got '{data['name']}'"
    assert data["hasConfigureServer"], "Plugin must have configureServer method"
    assert data["hasBuildEnd"], "Plugin must have buildEnd method"


def test_vite_config_uses_caddy():
    """vite.config.ts must import and use caddyPlugin with host enabled."""
    config_path = Path(EXAMPLE_DIR) / "vite.config.ts"
    assert config_path.exists(), "vite.config.ts must exist"

    content = config_path.read_text()
    assert "caddyPlugin" in content, "vite.config.ts must import caddyPlugin"
    assert "caddyPlugin()" in content, "vite.config.ts must instantiate caddyPlugin()"
    assert "host: true" in content, "vite.config.ts must set server.host to true"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

def test_agents_md_http2_proxy_tip():
    """AGENTS.md slow shapes tip must mention HTTP/2 proxy, not outdated version upgrade."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    # The old text was: "Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!"
    assert "HTTP/2" in content, "AGENTS.md must mention HTTP/2 in the slow shapes tip"
    assert "proxy" in content.lower(), \
        "AGENTS.md must mention proxy as the fix for slow shapes"
    assert "UPGRADE!" not in content, \
        "AGENTS.md should not have outdated v1.0.13 UPGRADE text"


def test_readme_documents_caddy():
    """README must document Caddy with HTTP/2 multiplexing explanation and setup."""
    readme = Path(EXAMPLE_DIR) / "README.md"
    content = readme.read_text()
    assert "Caddy" in content, "README must mention Caddy"
    assert "HTTP/2" in content, "README must explain HTTP/2 benefit"
    # Must explain the connection limit problem
    assert ("multiplex" in content.lower()
            or "connection limit" in content.lower()
            or "6 concurrent" in content.lower()
            or "6 simultaneous" in content.lower()), \
        "README must explain the HTTP/1.1 connection limit problem"
    assert "caddy trust" in content.lower(), \
        "README must include caddy trust setup instruction"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# ---------------------------------------------------------------------------

def test_vite_config_still_has_existing_plugins():
    """vite.config.ts must retain all existing plugins (tanstack, react, tailwind)."""
    config_path = Path(EXAMPLE_DIR) / "vite.config.ts"
    content = config_path.read_text()
    assert "tanstackStart" in content, "Must still use tanstackStart plugin"
    assert "viteReact" in content, "Must still use viteReact plugin"
    assert "tailwindcss" in content, "Must still use tailwindcss plugin"
