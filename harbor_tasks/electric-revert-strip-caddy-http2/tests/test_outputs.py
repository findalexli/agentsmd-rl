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
    """vite.config.ts must import and use caddyPlugin with host enabled.

    Evaluates the config module with stubbed external dependencies via a custom
    Node module loader, then inspects the resulting config object for the caddy
    plugin and server.host setting.
    """
    config_path = Path(EXAMPLE_DIR) / "vite.config.ts"
    assert config_path.exists(), "vite.config.ts must exist"

    loader_path = Path(EXAMPLE_DIR) / "_eval_loader.mjs"
    register_path = Path(EXAMPLE_DIR) / "_eval_register.mjs"
    test_path = Path(EXAMPLE_DIR) / "_eval_config_test.ts"

    try:
        # Custom module loader: stubs npm packages, resolves @/ path alias
        loader_path.write_text(
            'const STUBS = {\n'
            """  "vite": 'export function defineConfig(c) { return c; }',\n"""
            """  "@tanstack/react-start/plugin/vite": 'export function tanstackStart() { return { name: "tanstackStart" } }',\n"""
            """  "@vitejs/plugin-react": 'export default function viteReact() { return { name: "viteReact" } }',\n"""
            """  "vite-tsconfig-paths": 'export default function viteTsConfigPaths() { return { name: "viteTsConfigPaths" } }',\n"""
            """  "@tailwindcss/vite": 'export default function tailwindcss() { return { name: "tailwindcss" } }',\n"""
            '};\n'
            'export function resolve(specifier, context, next) {\n'
            '  if (specifier in STUBS) {\n'
            '    return { url: "data:text/javascript," + encodeURIComponent(STUBS[specifier]), shortCircuit: true };\n'
            '  }\n'
            '  if (specifier.startsWith("@/")) {\n'
            '    const parentDir = new URL("./", context.parentURL).href;\n'
            '    const resolved = new URL("src/" + specifier.slice(2) + ".ts", parentDir).href;\n'
            '    return { url: resolved, shortCircuit: true };\n'
            '  }\n'
            '  return next(specifier, context);\n'
            '}\n'
        )

        register_path.write_text(
            'import { register } from "node:module";\n'
            'register("./_eval_loader.mjs", import.meta.url);\n'
        )

        test_path.write_text(
            'const configModule = await import("./vite.config.ts");\n'
            'const config = configModule.default;\n'
            'const plugins = (config?.plugins || []).flat().filter(Boolean);\n'
            'const names = plugins.map((p: any) => p?.name).filter(Boolean);\n'
            'console.log(JSON.stringify({\n'
            '  pluginNames: names,\n'
            '  hasCaddyPlugin: names.includes("vite-plugin-caddy"),\n'
            '  hostEnabled: config?.server?.host === true,\n'
            '}));\n'
        )

        result = subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings",
             "--import", "./_eval_register.mjs", str(test_path)],
            capture_output=True, text=True, timeout=30, cwd=EXAMPLE_DIR,
        )
        assert result.returncode == 0, f"Config evaluation failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["hasCaddyPlugin"], "Config must include a plugin named 'vite-plugin-caddy'"
        assert data["hostEnabled"], "Config must set server.host to true"
    finally:
        for p in (loader_path, register_path, test_path):
            p.unlink(missing_ok=True)


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — documentation behavior tests
# These execute Node scripts that parse markdown structure and validate content.
# -----------------------------------------------------------------------------


def test_agents_md_http2_proxy_tip():
    """AGENTS.md slow shapes tip must mention HTTP/2 proxy, not outdated version upgrade.

    Runs a Node script that parses the numbered tips list in AGENTS.md,
    extracts the slow shapes tip, and checks its content.
    """
    agents_md = Path(REPO) / "AGENTS.md"
    assert agents_md.exists(), "AGENTS.md must exist"

    script_path = Path(EXAMPLE_DIR) / "_eval_agents_analysis.ts"
    script_path.write_text(
        'import { readFileSync } from "fs"\n'
        "\n"
        "const content = readFileSync(process.argv[2], \"utf8\")\n"
        "\n"
        "// Parse numbered list items: 'N. **Title** - description'\n"
        "const tipRegex = /^\\d+\\.\\s+\\*\\*(.+?)\\*\\*\\s*[-\\u2013]\\s*(.+)$/gm\n"
        "let match: RegExpExecArray | null\n"
        "const tips: Record<string, string> = {}\n"
        "while ((match = tipRegex.exec(content)) !== null) {\n"
        "    tips[match[1].trim()] = match[2].trim()\n"
        "}\n"
        "\n"
        "// Find the slow shapes / local dev tip\n"
        "let slowText = \"\"\n"
        "for (const [title, body] of Object.entries(tips)) {\n"
        '    if (title.toLowerCase().includes("slow") || title.toLowerCase().includes("local dev")) {\n'
        "        slowText = body\n"
        "        break\n"
        "    }\n"
        "}\n"
        "\n"
        "console.log(JSON.stringify({\n"
        "    found: !!slowText,\n"
        "    http2: /HTTP.?2/i.test(slowText),\n"
        "    proxy: /proxy/i.test(slowText),\n"
        "    outdated: /v1\\.0\\.13[\\s\\S]*?UPGRADE/.test(slowText),\n"
        "}))\n"
    )

    try:
        result = subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings",
             str(script_path), str(agents_md)],
            capture_output=True, text=True, timeout=10, cwd=EXAMPLE_DIR,
        )
        assert result.returncode == 0, f"Analysis script failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["found"], "AGENTS.md must have a tip about local dev slow shapes"
        assert not data["outdated"], "Tip must not reference outdated v1.0.13 UPGRADE"
        assert data["http2"], "Tip must mention HTTP/2 as part of the solution"
        assert data["proxy"], "Tip must mention proxy as part of the solution"
    finally:
        script_path.unlink(missing_ok=True)


def test_readme_documents_caddy():
    """README must document Caddy with HTTP/2 multiplexing explanation and setup.

    Runs a Node script that parses the README markdown, extracts code blocks,
    and verifies Caddy documentation requirements.
    """
    readme = Path(EXAMPLE_DIR) / "README.md"
    assert readme.exists(), "README.md must exist"

    script_path = Path(EXAMPLE_DIR) / "_eval_readme_analysis.ts"
    script_path.write_text(
        'import { readFileSync } from "fs"\n'
        "\n"
        "const content = readFileSync(process.argv[2], \"utf8\")\n"
        "\n"
        "// Extract fenced code blocks\n"
        "const codeBlocks: string[] = []\n"
        "const codeRegex = /```[\\s\\S]*?```/g\n"
        "let m: RegExpExecArray | null\n"
        "while ((m = codeRegex.exec(content)) !== null) {\n"
        "    codeBlocks.push(m[0])\n"
        "}\n"
        'const codeContent = codeBlocks.join("\\n")\n'
        "\n"
        "console.log(JSON.stringify({\n"
        "    mentionsCaddy: /caddy/i.test(content),\n"
        "    mentionsHttp2: /HTTP.?2/i.test(content),\n"
        "    explainsLimit: /(multiplex|connection.{0,5}limit|6.concurrent|6.simultaneous)/i.test(content),\n"
        "    hasCaddyTrustInCode: /caddy\\s+trust/i.test(codeContent),\n"
        "}))\n"
    )

    try:
        result = subprocess.run(
            ["node", "--experimental-strip-types", "--no-warnings",
             str(script_path), str(readme)],
            capture_output=True, text=True, timeout=10, cwd=EXAMPLE_DIR,
        )
        assert result.returncode == 0, f"Analysis script failed: {result.stderr}"
        data = json.loads(result.stdout.strip())
        assert data["mentionsCaddy"], "README must mention Caddy"
        assert data["mentionsHttp2"], "README must mention HTTP/2"
        assert data["explainsLimit"], "README must explain the HTTP/1.1 connection limit problem"
        assert data["hasCaddyTrustInCode"], "README must include caddy trust in a code block"
    finally:
        script_path.unlink(missing_ok=True)


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
