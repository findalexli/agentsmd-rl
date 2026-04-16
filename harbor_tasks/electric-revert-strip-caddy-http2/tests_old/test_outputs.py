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

import pytest

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


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# -----------------------------------------------------------------------------


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
    # Verify caddyPlugin is imported
    assert "caddyPlugin" in content, "vite.config.ts must import caddyPlugin"
    # Verify caddyPlugin is instantiated (allowing whitespace variations)
    import re
    assert re.search(r'caddyPlugin\s*\(\s*\)', content), \
        "vite.config.ts must instantiate caddyPlugin()"
    # Verify server.host is set to true (allowing 'as const' or trailing comments)
    # Accepts: host: true, host: true as const, host: true /* comment */
    assert re.search(r'host\s*:\s*true\b', content), \
        "vite.config.ts must set server.host to true"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# -----------------------------------------------------------------------------


def test_agents_md_http2_proxy_tip():
    """AGENTS.md slow shapes tip must mention HTTP/2 proxy, not outdated version upgrade."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    import re
    # The old text was: "Fixed by default in `@electric-sql/client` v1.0.13+ UPGRADE!"
    # Verify the outdated text is gone
    assert not re.search(r'v1\.0\.13.*?UPGRADE', content), \
        "AGENTS.md should not have outdated v1.0.13 UPGRADE text"
    # Verify HTTP/2 proxy is mentioned in context of slow shapes
    # Look for the slow shapes section mentioning both HTTP/2 and proxy together
    assert re.search(r'HTTP/2.*?proxy', content, re.IGNORECASE), \
        "AGENTS.md must mention HTTP/2 and proxy in the slow shapes tip"



def test_readme_documents_caddy():
    """README must document Caddy with HTTP/2 multiplexing explanation and setup."""
    readme = Path(EXAMPLE_DIR) / "README.md"
    content = readme.read_text()
    import re
    # Verify Caddy is mentioned with HTTP/2 context
    assert re.search(r'Caddy.*?HTTP/2', content, re.IGNORECASE | re.DOTALL), \
        "README must explain Caddy with HTTP/2"
    # Must explain the connection limit problem (either explicitly or via HTTP/2 multiplexing)
    assert re.search(r'(multiplex|connection.limit|6.concurrent|6.simultaneous)',
                     content, re.IGNORECASE), \
        "README must explain the HTTP/1.1 connection limit problem"
    # Verify caddy trust appears as a code block or command (not just in prose)
    # This ensures it's documented as an instruction, not just mentioned
    assert re.search(r'```[^`]*caddy\s+trust', content, re.IGNORECASE), \
        "README must include caddy trust as a code/instruction block"


# -----------------------------------------------------------------------------
# Pass-to-pass (static) — regression guard
# -----------------------------------------------------------------------------

def test_vite_config_still_has_existing_plugins():
    """vite.config.ts must retain all existing plugins (tanstack, react, tailwind)."""
    config_path = Path(EXAMPLE_DIR) / "vite.config.ts"
    content = config_path.read_text()
    assert "tanstackStart" in content, "Must still use tanstackStart plugin"
    assert "viteReact" in content, "Must still use viteReact plugin"
    assert "tailwindcss" in content, "Must still use tailwindcss plugin"


# -----------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD verification
# These run actual CI commands found in the repo's GitHub workflows
# -----------------------------------------------------------------------------

def test_repo_stylecheck_all():
    """Repo-wide stylecheck passes (pass_to_pass).

    Runs `pnpm run stylecheck-all` which executes eslint across all packages
    and examples, as configured in the root package.json CI.
    """
    # Install pnpm and dependencies
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Install dependencies (without --frozen-lockfile as the fix may update package.json)
    r = subprocess.run(
        ["pnpm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    # Run stylecheck
    r = subprocess.run(
        ["pnpm", "run", "stylecheck-all"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"stylecheck-all failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_typescript_client_stylecheck():
    """TypeScript client package stylecheck passes (pass_to_pass).

    Runs `pnpm run stylecheck` in packages/typescript-client as per CI workflow.
    """
    pkg_dir = f"{REPO}/packages/typescript-client"
    # Install pnpm and dependencies
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["pnpm", "run", "stylecheck"],
        capture_output=True, text=True, timeout=120, cwd=pkg_dir,
    )
    assert r.returncode == 0, f"typescript-client stylecheck failed:\n{r.stderr[-500:]}"


def test_repo_typescript_client_typecheck():
    """TypeScript client package typecheck passes (pass_to_pass).

    Runs `pnpm run typecheck` in packages/typescript-client as per CI workflow.
    """
    pkg_dir = f"{REPO}/packages/typescript-client"
    # Install pnpm and dependencies
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["pnpm", "run", "typecheck"],
        capture_output=True, text=True, timeout=120, cwd=pkg_dir,
    )
    assert r.returncode == 0, f"typescript-client typecheck failed:\n{r.stderr[-500:]}"


def test_repo_tanstack_plugin_syntax():
    """New vite-plugin-caddy.ts has valid JavaScript/TypeScript syntax (pass_to_pass).

    Runs `node --check` on the new plugin file to verify basic syntax is valid.
    This test passes trivially if the file doesn't exist yet (pre-fix state).
    """
    plugin_path = Path(f"{EXAMPLE_DIR}/src/vite-plugin-caddy.ts")
    if not plugin_path.exists():
        return  # File doesn't exist at base commit, test passes trivially

    r = subprocess.run(
        ["node", "--check", str(plugin_path)],
        capture_output=True, text=True, timeout=30, cwd=EXAMPLE_DIR,
    )
    assert r.returncode == 0, f"Plugin syntax check failed:\n{r.stderr[-500:]}"


def test_repo_tanstack_plugin_lint():
    """New vite-plugin-caddy.ts passes eslint (pass_to_pass).

    Runs `npx eslint` on the new plugin file as per the example's CI configuration.
    This test passes trivially if the file doesn't exist yet (pre-fix state).
    """
    plugin_path = Path(f"{EXAMPLE_DIR}/src/vite-plugin-caddy.ts")
    if not plugin_path.exists():
        return  # File doesn't exist at base commit, test passes trivially

    # Install pnpm and dependencies (without --frozen-lockfile as the fix may update package.json)
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npx", "eslint", "src/vite-plugin-caddy.ts"],
        capture_output=True, text=True, timeout=60, cwd=EXAMPLE_DIR,
    )
    assert r.returncode == 0, f"Plugin lint failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_tanstack_plugin_format():
    """New vite-plugin-caddy.ts passes prettier formatting check (pass_to_pass).

    Runs `npx prettier --check` on the new plugin file as per the example's CI configuration.
    This test passes trivially if the file doesn't exist yet (pre-fix state).
    """
    plugin_path = Path(f"{EXAMPLE_DIR}/src/vite-plugin-caddy.ts")
    if not plugin_path.exists():
        return  # File doesn't exist at base commit, test passes trivially

    # Install pnpm and dependencies (without --frozen-lockfile as the fix may update package.json)
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    r = subprocess.run(
        ["pnpm", "install", "--ignore-scripts"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"

    r = subprocess.run(
        ["npx", "prettier", "--check", "src/vite-plugin-caddy.ts"],
        capture_output=True, text=True, timeout=60, cwd=EXAMPLE_DIR,
    )
    assert r.returncode == 0, f"Plugin format check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"
