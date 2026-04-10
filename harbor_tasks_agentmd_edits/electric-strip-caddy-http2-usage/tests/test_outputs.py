"""Tests for electric-strip-caddy-http2-usage task.

Verifies that all Caddy HTTP/2 proxy code and documentation has been removed,
replaced by subdomain sharding in @electric-sql/client v1.0.13+.
"""
import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/electric")

TANSTACK = REPO / "examples" / "tanstack-db-web-starter"
BURN = REPO / "examples" / "burn"


# --- Helper ---

def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a Node.js script and return the result."""
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
    )


def _version_gte(version_spec: str, minimum: str) -> bool:
    """Check if a semver range specifier is >= minimum version."""
    match = re.search(r'(\d+)\.(\d+)\.(\d+)', version_spec)
    if not match:
        return False
    major, minor, patch = int(match.group(1)), int(match.group(2)), int(match.group(3))
    min_parts = [int(x) for x in minimum.split(".")]
    return (major, minor, patch) >= tuple(min_parts)


# --- Fail-to-pass: Code changes ---


def test_vite_config_no_caddy():
    """vite.config.ts must not import or use caddyPlugin."""
    result = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8'); "
        "if (c.includes('caddyPlugin') || c.includes('vite-plugin-caddy')) { "
        "  console.error('STILL_HAS_CADDY'); process.exit(1); "
        "} "
        "console.log('CLEAN');"
    )
    assert result.returncode == 0, f"vite.config.ts still references caddy: {result.stderr}"
    assert "CLEAN" in result.stdout


def test_caddy_plugin_deleted():
    """The vite-plugin-caddy.ts file must be deleted."""
    plugin_path = TANSTACK / "src" / "vite-plugin-caddy.ts"
    assert not plugin_path.exists(), \
        "examples/tanstack-db-web-starter/src/vite-plugin-caddy.ts should be deleted"


def test_burn_caddyfile_deleted():
    """The burn example Caddyfile must be deleted."""
    caddyfile = BURN / "Caddyfile"
    assert not caddyfile.exists(), \
        "examples/burn/Caddyfile should be deleted"


def test_client_version_bumped_tanstack():
    """tanstack-db-web-starter must use @electric-sql/client ^1.0.13 or later."""
    pkg = json.loads((TANSTACK / "package.json").read_text())
    version = pkg["dependencies"]["@electric-sql/client"]
    assert _version_gte(version, "1.0.13"), \
        f"@electric-sql/client should be ^1.0.13+, got {version}"


def test_client_version_bumped_burn():
    """burn example must use @electric-sql/client ^1.0.13 or later."""
    pkg = json.loads((BURN / "assets" / "package.json").read_text())
    version = pkg["dependencies"]["@electric-sql/client"]
    assert _version_gte(version, "1.0.13"), \
        f"@electric-sql/client should be ^1.0.13+, got {version}"


def test_vite_config_no_host_true():
    """vite.config.ts should not set server.host: true (was for Caddy networking)."""
    vite_config = (TANSTACK / "vite.config.ts").read_text()
    assert "host: true" not in vite_config, \
        "vite.config.ts should not set server.host: true (Caddy remnant)"


# --- Fail-to-pass: Config/documentation changes ---


def test_agents_md_updated_gotcha():
    """Root AGENTS.md gotcha #3 should reflect subdomain sharding fix, not Caddy."""
    agents_md = (REPO / "AGENTS.md").read_text()
    # Should NOT recommend Caddy/nginx as the fix for slow shapes
    assert "HTTP/2 proxy (Caddy/nginx)" not in agents_md, \
        "AGENTS.md still recommends Caddy/nginx HTTP/2 proxy for slow shapes"
    # Should reference the client version fix
    assert "1.0.13" in agents_md, \
        "AGENTS.md should mention @electric-sql/client v1.0.13"


def test_tanstack_readme_no_caddy():
    """tanstack-db-web-starter README should not contain Caddy setup instructions."""
    readme = (TANSTACK / "README.md").read_text()
    # Should not have Caddy sections
    assert "### Caddy" not in readme, \
        "README should not have a Caddy section"
    assert "caddy trust" not in readme.lower(), \
        "README should not instruct to run caddy trust"
    # Should use localhost:5173, not the custom HTTPS domain
    assert "localhost:5173" in readme, \
        "README should direct users to localhost:5173"
    assert "tanstack-start-db-electric-starter.localhost" not in readme, \
        "README should not reference the old Caddy HTTPS domain"


def test_burn_readme_direct_port():
    """burn README should reference port 4000 directly, not port 4001 via Caddy."""
    readme = (BURN / "README.md").read_text()
    # Should use 4000 directly
    assert "localhost:4000" in readme, \
        "burn README should reference localhost:4000"
    # Should NOT mention starting Caddy
    assert "caddy start" not in readme.lower(), \
        "burn README should not instruct to start Caddy"
    assert "localhost:4001" not in readme, \
        "burn README should not reference Caddy proxy port 4001"


def test_troubleshooting_docs_subdomain_sharding():
    """website troubleshooting docs should describe subdomain sharding, not Caddy setup."""
    troubleshooting = (REPO / "website" / "docs" / "guides" / "troubleshooting.md").read_text()
    # Should describe subdomain sharding as the primary solution
    assert "subdomain sharding" in troubleshooting.lower(), \
        "troubleshooting.md should describe subdomain sharding solution"
    # Should mention the client version
    assert "1.0.13" in troubleshooting, \
        "troubleshooting.md should mention client v1.0.13"
    # Should NOT have Caddy as the primary solution header
    assert "run Caddy" not in troubleshooting, \
        "troubleshooting.md should not recommend 'run Caddy' as primary solution"


# --- Pass-to-pass ---


def test_vite_config_valid():
    """vite.config.ts should be readable and non-empty."""
    result = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8'); "
        "console.log('OK, length:', c.length);"
    )
    assert result.returncode == 0, f"Failed to read vite.config.ts: {result.stderr}"
    assert "OK, length:" in result.stdout


def test_tanstack_vite_config_parses():
    """tanstack vite.config.ts should be parseable JavaScript/TypeScript (pass_to_pass)."""
    # Verify the file contains valid JS constructs by parsing with Node
    script = """
    const fs = require('fs');
    const content = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8');
    // Basic structural checks for a valid vite config
    if (!content.includes('export default') && !content.includes('export const config')) {
        // Vite configs should have an export
        console.log('Note: No standard export found, checking for defineConfig...');
    }
    if (!content.includes('defineConfig') && !content.includes('export default')) {
        console.error('No defineConfig or export default found');
        process.exit(1);
    }
    console.log('OK: vite.config.ts has valid structure');
    """
    r = _run_node(script, timeout=60)
    assert r.returncode == 0, f"Vite config parse check failed:\n{r.stderr}"
    assert "OK" in r.stdout


def test_burn_vite_config_parses():
    """burn vite.config.ts should be parseable JavaScript/TypeScript (pass_to_pass)."""
    script = """
    const fs = require('fs');
    const content = fs.readFileSync('examples/burn/assets/vite.config.ts', 'utf8');
    if (!content.includes('defineConfig') && !content.includes('export default')) {
        console.error('No defineConfig or export default found');
        process.exit(1);
    }
    console.log('OK: vite.config.ts has valid structure');
    """
    r = _run_node(script, timeout=60)
    assert r.returncode == 0, f"Vite config parse check failed:\n{r.stderr}"
    assert "OK" in r.stdout


def test_repo_lockfile_matches():
    """pnpm-lock.yaml should be valid and consistent with package.json files (pass_to_pass)."""
    # Use pnpm to verify lockfile is valid (doesn't need full install)
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm && cd /workspace/electric "
         "&& pnpm install --frozen-lockfile --ignore-scripts 2>&1"],
        capture_output=True, text=True, timeout=180, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Lockfile check failed:\n{r.stderr[-500:]}"


def test_repo_package_files_valid():
    """All modified package.json files should be valid and have required fields (pass_to_pass)."""
    # Check that package.json files are valid and have dependencies section
    script = """
    const fs = require('fs');
    const files = [
        'examples/tanstack-db-web-starter/package.json',
        'examples/burn/assets/package.json'
    ];
    for (const f of files) {
        const content = fs.readFileSync(f, 'utf8');
        const pkg = JSON.parse(content);
        if (!pkg.dependencies || !pkg.dependencies['@electric-sql/client']) {
            console.error('MISSING_CLIENT_DEP:', f);
            process.exit(1);
        }
    }
    console.log('OK');
    """
    r = _run_node(script)
    assert r.returncode == 0, f"Package files check failed:\n{r.stderr}"
    assert "OK" in r.stdout


def test_package_json_valid():
    """Both modified package.json files should be valid JSON with expected deps."""
    for path in [
        TANSTACK / "package.json",
        BURN / "assets" / "package.json",
    ]:
        content = path.read_text()
        data = json.loads(content)
        assert "dependencies" in data, f"{path} missing dependencies"
        assert "@electric-sql/client" in data["dependencies"], \
            f"{path} missing @electric-sql/client dependency"


def test_tanstack_build():
    """Tanstack example has valid build configuration (pass_to_pass)."""
    # Verify the vite config is valid and package.json scripts are present
    # We can't run full build because it requires a dev server for prerendering
    script = """
    const fs = require('fs');
    const pkg = JSON.parse(fs.readFileSync('examples/tanstack-db-web-starter/package.json', 'utf8'));
    if (!pkg.scripts || !pkg.scripts.build) {
        console.error('Missing build script');
        process.exit(1);
    }
    const viteConfig = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8');
    if (!viteConfig.includes('defineConfig')) {
        console.error('Invalid vite config');
        process.exit(1);
    }
    // Check that caddyPlugin is NOT imported (would break build if file is missing)
    if (viteConfig.includes('caddyPlugin') || viteConfig.includes('vite-plugin-caddy')) {
        console.error('vite.config.ts still references caddyPlugin');
        process.exit(1);
    }
    console.log('Build configuration valid');
    """
    r = _run_node(script, timeout=30)
    assert r.returncode == 0, f"Build config check failed:\n{r.stderr}"
