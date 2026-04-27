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


# --- Helpers ---

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
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8'); "
        "if (c.includes('caddyPlugin') || c.includes('vite-plugin-caddy')) { "
        "  console.error('STILL_HAS_CADDY'); process.exit(1); "
        "} "
        "console.log('CLEAN');"
    )
    assert r.returncode == 0, f"vite.config.ts still references caddy: {r.stderr}"
    assert "CLEAN" in r.stdout


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
    r = _run_node(
        "const fs = require('fs'); "
        "const pkg = JSON.parse(fs.readFileSync('examples/tanstack-db-web-starter/package.json', 'utf8')); "
        "const dep = pkg.dependencies['@electric-sql/client']; "
        "if (!dep) { console.error('MISSING_DEP'); process.exit(1); } "
        "const m = dep.match(/(\\d+)\\.(\\d+)\\.(\\d+)/); "
        "if (!m) { console.error('BAD_VERSION:', dep); process.exit(1); } "
        "const [maj, min, pat] = [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])]; "
        "if (maj < 1 || (maj === 1 && min < 0) || (maj === 1 && min === 0 && pat < 13)) { "
        "  console.error('VERSION_TOO_LOW:', dep); process.exit(1); "
        "} "
        "console.log('OK:', dep);"
    )
    assert r.returncode == 0, f"Version check failed: {r.stderr}"
    assert "OK:" in r.stdout


def test_client_version_bumped_burn():
    """burn example must use @electric-sql/client ^1.0.13 or later."""
    r = _run_node(
        "const fs = require('fs'); "
        "const pkg = JSON.parse(fs.readFileSync('examples/burn/assets/package.json', 'utf8')); "
        "const dep = pkg.dependencies['@electric-sql/client']; "
        "if (!dep) { console.error('MISSING_DEP'); process.exit(1); } "
        "const m = dep.match(/(\\d+)\\.(\\d+)\\.(\\d+)/); "
        "if (!m) { console.error('BAD_VERSION:', dep); process.exit(1); } "
        "const [maj, min, pat] = [parseInt(m[1]), parseInt(m[2]), parseInt(m[3])]; "
        "if (maj < 1 || (maj === 1 && min < 0) || (maj === 1 && min === 0 && pat < 13)) { "
        "  console.error('VERSION_TOO_LOW:', dep); process.exit(1); "
        "} "
        "console.log('OK:', dep);"
    )
    assert r.returncode == 0, f"Version check failed: {r.stderr}"
    assert "OK:" in r.stdout


def test_vite_config_no_host_true():
    """vite.config.ts should not set server.host: true (was for Caddy networking)."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8'); "
        "const serverHost = /server\\s*:\\s*\\{[^}]*host\\s*:\\s*true[^}]*\\}/; "
        "if (serverHost.test(c)) { "
        "  console.error('HAS_HOST_TRUE'); process.exit(1); "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"vite.config.ts still has host: true: {r.stderr}"
    assert "OK" in r.stdout


# --- Fail-to-pass: Config/documentation changes ---


def test_agents_md_updated_gotcha():
    """Root AGENTS.md gotcha #3 should reflect subdomain sharding fix, not Caddy."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('AGENTS.md', 'utf8'); "
        "if (c.includes('HTTP/2 proxy (Caddy/nginx)')) { "
        "  console.error('STILL_HAS_CADDY_PROXY'); process.exit(1); "
        "} "
        "if (!c.includes('1.0.13')) { "
        "  console.error('MISSING_VERSION'); process.exit(1); "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"AGENTS.md check failed: {r.stderr}"
    assert "OK" in r.stdout


def test_tanstack_readme_no_caddy():
    """tanstack-db-web-starter README should not contain Caddy setup instructions."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/README.md', 'utf8'); "
        "if (c.includes('### Caddy')) { "
        "  console.error('HAS_CADDY_SECTION'); process.exit(1); "
        "} "
        "if (c.toLowerCase().includes('caddy trust')) { "
        "  console.error('HAS_CADDY_TRUST'); process.exit(1); "
        "} "
        "if (!c.includes('localhost:5173')) { "
        "  console.error('MISSING_LOCALHOST_5173'); process.exit(1); "
        "} "
        "if (c.includes('tanstack-start-db-electric-starter.localhost')) { "
        "  console.error('HAS_OLD_DOMAIN'); process.exit(1); "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"tanstack README check failed: {r.stderr}"
    assert "OK" in r.stdout


def test_burn_readme_direct_port():
    """burn README should reference port 4000 directly, not port 4001 via Caddy."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/burn/README.md', 'utf8'); "
        "if (!c.includes('localhost:4000')) { "
        "  console.error('MISSING_LOCALHOST_4000'); process.exit(1); "
        "} "
        "if (c.toLowerCase().includes('caddy start')) { "
        "  console.error('HAS_CADDY_START'); process.exit(1); "
        "} "
        "if (c.includes('localhost:4001')) { "
        "  console.error('HAS_OLD_PORT_4001'); process.exit(1); "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"burn README check failed: {r.stderr}"
    assert "OK" in r.stdout


def test_troubleshooting_docs_subdomain_sharding():
    """website troubleshooting docs should describe subdomain sharding, not Caddy setup."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('website/docs/guides/troubleshooting.md', 'utf8'); "
        "if (!c.toLowerCase().includes('subdomain sharding')) { "
        "  console.error('MISSING_SUBDOMAIN_SHARDING'); process.exit(1); "
        "} "
        "if (!c.includes('1.0.13')) { "
        "  console.error('MISSING_VERSION'); process.exit(1); "
        "} "
        "if (c.includes('run Caddy')) { "
        "  console.error('HAS_RUN_CADDY'); process.exit(1); "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"troubleshooting.md check failed: {r.stderr}"
    assert "OK" in r.stdout


# --- Pass-to-pass ---


def test_vite_config_valid():
    """vite.config.ts should be readable and non-empty."""
    r = _run_node(
        "const fs = require('fs'); "
        "const c = fs.readFileSync('examples/tanstack-db-web-starter/vite.config.ts', 'utf8'); "
        "console.log('OK, length:', c.length);"
    )
    assert r.returncode == 0, f"Failed to read vite.config.ts: {r.stderr}"
    assert "OK, length:" in r.stdout


def test_tanstack_vite_config_parses():
    """tanstack vite.config.ts should be parseable JavaScript/TypeScript (pass_to_pass)."""
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
    r = _run_node(
        "const fs = require('fs'); "
        "const files = ["
        "  'examples/tanstack-db-web-starter/package.json',"
        "  'examples/burn/assets/package.json'"
        "]; "
        "for (const f of files) { "
        "  const pkg = JSON.parse(fs.readFileSync(f, 'utf8')); "
        "  if (!pkg.dependencies) { console.error('NO_DEPS:', f); process.exit(1); } "
        "  if (!pkg.dependencies['@electric-sql/client']) { "
        "    console.error('NO_CLIENT:', f); process.exit(1); "
        "  } "
        "} "
        "console.log('OK');"
    )
    assert r.returncode == 0, f"package.json check failed: {r.stderr}"
    assert "OK" in r.stdout


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


# --- New repo_tests pass-to-pass gates (CI/CD enrichment) ---


def test_typescript_client_typecheck():
    """TypeScript client package typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm 2>/dev/null && pnpm install --ignore-scripts 2>/dev/null "
         "&& cd packages/typescript-client && pnpm run typecheck"],
        capture_output=True, text=True, timeout=600, cwd=str(REPO),
    )
    assert r.returncode == 0, f"typescript-client typecheck failed:\n{r.stderr[-500:]}"


def test_typescript_client_build():
    """TypeScript client package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm 2>/dev/null && pnpm install --ignore-scripts 2>/dev/null "
         "&& cd packages/typescript-client && pnpm run build"],
        capture_output=True, text=True, timeout=600, cwd=str(REPO),
    )
    assert r.returncode == 0, f"typescript-client build failed:\n{r.stderr[-500:]}"



def test_repo_lockfile_valid():
    """pnpm-lock.yaml is valid and installable (pass_to_pass)."""
    r = subprocess.run(
        ["bash", "-c",
         "npm install -g pnpm 2>/dev/null && pnpm install --ignore-scripts 2>/dev/null"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert r.returncode == 0, f"pnpm install failed:\n{r.stderr[-500:]}"
