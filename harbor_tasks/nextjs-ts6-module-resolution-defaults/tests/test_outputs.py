"""
Task: nextjs-ts6-module-resolution-defaults
Repo: vercel/next.js @ 7dd1fcfc924be23cf2785054f5a2ad4f5affb692

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/repo"
WCD = f"{REPO}/packages/next/src/lib/typescript/writeConfigurationDefaults.ts"
GTC = f"{REPO}/packages/next/src/lib/typescript/getTypeScriptConfiguration.ts"


def _run_tsx(script: str, tsconfig_content: dict, extra_files: dict | None = None) -> str:
    """Helper: write a tsconfig + test script to a temp dir, run with tsx, return stdout."""
    with tempfile.TemporaryDirectory() as td:
        Path(td, "tsconfig.json").write_text(json.dumps(tsconfig_content))
        Path(td, "test.ts").write_text(script)
        if extra_files:
            for name, content in extra_files.items():
                Path(td, name).write_text(content)
        r = subprocess.run(
            ["npx", "tsx", "test.ts", f"{td}/tsconfig.json"],
            cwd=td, capture_output=True, timeout=60, text=True,
        )
        return r.stdout.strip()


def _wcd_wrapper_import():
    return f"export {{ writeConfigurationDefaults }} from '{REPO}/packages/next/src/lib/typescript/writeConfigurationDefaults'"


def _gtc_wrapper_import():
    return f"export {{ getTypeScriptConfiguration }} from '{REPO}/packages/next/src/lib/typescript/getTypeScriptConfiguration'"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Both modified TypeScript files must parse without errors."""
    for filepath in [WCD, GTC]:
        assert Path(filepath).exists(), f"Missing: {filepath}"
        r = subprocess.run(
            ["node", "-e", f"""
const ts = require('typescript');
const source = require('fs').readFileSync('{filepath}', 'utf8');
const sf = ts.createSourceFile('{filepath}', source, ts.ScriptTarget.Latest, true);
if (!sf) process.exit(1);
"""],
            capture_output=True, timeout=30,
        )
        assert r.returncode == 0, f"{Path(filepath).name} has syntax errors"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_bundler_default_esnext():
    """Modern TS (>=5.0) with default/esnext module defaults moduleResolution to 'bundler'."""
    script = f"""
import {{ writeConfigurationDefaults }} from './wcd_wrapper'
import {{ readFileSync }} from 'fs'
async function main() {{
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {{}}
  try {{
    await writeConfigurationDefaults('5.9.2', p, true, true, '.next', true, false)
  }} finally {{ console.log = origLog }}
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  process.stdout.write(typeof mr === 'string' ? mr.toLowerCase() : 'MISSING')
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(script, {}, {"wcd_wrapper.ts": _wcd_wrapper_import()})
    assert result == "bundler", f"Expected moduleResolution='bundler', got '{result}'"


# [pr_diff] fail_to_pass
def test_bundler_default_es2020():
    """Modern TS (>=5.0) with module=ES2020 also gets moduleResolution='bundler'."""
    script = f"""
import {{ writeConfigurationDefaults }} from './wcd_wrapper'
import {{ readFileSync }} from 'fs'
async function main() {{
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {{}}
  try {{
    await writeConfigurationDefaults('5.9.2', p, true, true, '.next', true, false)
  }} finally {{ console.log = origLog }}
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  process.stdout.write(typeof mr === 'string' ? mr.toLowerCase() : 'MISSING')
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"module": "ES2020"}},
        {"wcd_wrapper.ts": _wcd_wrapper_import()},
    )
    assert result == "bundler", f"Expected moduleResolution='bundler', got '{result}'"


# [pr_diff] fail_to_pass
def test_bundler_default_preserve():
    """Modern TS (>=5.0) with module=Preserve also gets moduleResolution='bundler'."""
    script = f"""
import {{ writeConfigurationDefaults }} from './wcd_wrapper'
import {{ readFileSync }} from 'fs'
async function main() {{
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {{}}
  try {{
    await writeConfigurationDefaults('5.9.2', p, true, true, '.next', true, false)
  }} finally {{ console.log = origLog }}
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  process.stdout.write(typeof mr === 'string' ? mr.toLowerCase() : 'MISSING')
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"module": "Preserve"}},
        {"wcd_wrapper.ts": _wcd_wrapper_import()},
    )
    assert result == "bundler", f"Expected moduleResolution='bundler', got '{result}'"


# [pr_diff] fail_to_pass
def test_ts6_target_rewrite_es5():
    """TS6 getTypeScriptConfiguration rewrites es5 target to es2015+."""
    script = f"""
import {{ getTypeScriptConfiguration }} from './gtc_wrapper'
import ts from 'typescript'
async function main() {{
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {{
    get(target: any, prop: string | symbol) {{
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }}
  }})
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)
  if (!result || !result.options) {{ process.stdout.write('INVALID'); return }}
  // ts.ScriptTarget: ES3=0, ES5=1, ES2015=2
  process.stdout.write(String(result.options.target))
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"target": "es5", "module": "esnext"}},
        {"gtc_wrapper.ts": _gtc_wrapper_import()},
    )
    assert result.isdigit() and int(result) >= 2, (
        f"Expected target >= 2 (es2015+), got '{result}'"
    )


# [pr_diff] fail_to_pass
def test_ts6_target_rewrite_es3():
    """TS6 getTypeScriptConfiguration also rewrites es3 target."""
    script = f"""
import {{ getTypeScriptConfiguration }} from './gtc_wrapper'
import ts from 'typescript'
async function main() {{
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {{
    get(target: any, prop: string | symbol) {{
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }}
  }})
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)
  if (!result || !result.options) {{ process.stdout.write('INVALID'); return }}
  process.stdout.write(String(result.options.target))
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"target": "es3", "module": "esnext"}},
        {"gtc_wrapper.ts": _gtc_wrapper_import()},
    )
    assert result.isdigit() and int(result) >= 2, (
        f"Expected target >= 2 (es2015+), got '{result}'"
    )


# [pr_diff] fail_to_pass
def test_ts6_baseurl_migration():
    """TS6 getTypeScriptConfiguration migrates baseUrl='.' to explicit paths entries."""
    script = f"""
import {{ getTypeScriptConfiguration }} from './gtc_wrapper'
import ts from 'typescript'
async function main() {{
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {{
    get(target: any, prop: string | symbol) {{
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }}
  }})
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)
  if (!result || !result.options) {{ process.stdout.write('INVALID'); return }}
  const paths = result.options.paths
  if (paths && typeof paths === 'object' && Object.keys(paths).length > 0) {{
    process.stdout.write('HAS_PATHS:' + JSON.stringify(paths))
  }} else {{
    process.stdout.write('NO_PATHS')
  }}
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"baseUrl": ".", "module": "esnext", "target": "es2015"}},
        {"gtc_wrapper.ts": _gtc_wrapper_import()},
    )
    assert result.startswith("HAS_PATHS"), f"Expected baseUrl migrated to paths, got '{result}'"


# [pr_diff] fail_to_pass
def test_ts6_baseurl_with_existing_paths():
    """TS6 migrates baseUrl with existing paths — rewrites values and adds wildcard fallback."""
    script = f"""
import {{ getTypeScriptConfiguration }} from './gtc_wrapper'
import ts from 'typescript'
async function main() {{
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {{
    get(target: any, prop: string | symbol) {{
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }}
  }})
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)
  if (!result || !result.options) {{ process.stdout.write('INVALID'); return }}
  const paths = result.options.paths
  if (paths && typeof paths === 'object') {{
    process.stdout.write(JSON.stringify(paths))
  }} else {{
    process.stdout.write('NO_PATHS')
  }}
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"baseUrl": ".", "paths": {"@/*": ["src/*"]}, "module": "esnext", "target": "es2015"}},
        {"gtc_wrapper.ts": _gtc_wrapper_import()},
    )
    assert result != "NO_PATHS" and not result.startswith("ERROR"), (
        f"Expected paths migration with existing paths, got '{result}'"
    )
    paths = json.loads(result)
    assert "*" in paths, f"Expected wildcard fallback '*' in migrated paths, got keys: {list(paths.keys())}"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_ts6_target_keeps_es2015():
    """TS6 does NOT rewrite es2015 target — only es3/es5 are deprecated."""
    script = f"""
import {{ getTypeScriptConfiguration }} from './gtc_wrapper'
import ts from 'typescript'
async function main() {{
  const tsConfigPath = process.argv[2]
  const fakeTs6: any = new Proxy(ts as any, {{
    get(target: any, prop: string | symbol) {{
      if (prop === 'version') return '6.0.0'
      return target[prop]
    }}
  }})
  const result = await getTypeScriptConfiguration(fakeTs6, tsConfigPath, true)
  if (!result || !result.options) {{ process.stdout.write('INVALID'); return }}
  // ts.ScriptTarget.ES2015 = 2
  process.stdout.write(String(result.options.target))
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"target": "es2015", "module": "esnext"}},
        {"gtc_wrapper.ts": _gtc_wrapper_import()},
    )
    assert result.isdigit() and int(result) == 2, (
        f"Expected target == 2 (es2015 unchanged), got '{result}'"
    )

# [pr_diff] pass_to_pass
def test_commonjs_keeps_node_resolution():
    """When module is commonjs, moduleResolution stays 'node' (not 'bundler')."""
    script = f"""
import {{ writeConfigurationDefaults }} from './wcd_wrapper'
import {{ readFileSync }} from 'fs'
async function main() {{
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {{}}
  try {{
    await writeConfigurationDefaults('5.9.2', p, false, true, '.next', true, false)
  }} finally {{ console.log = origLog }}
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  process.stdout.write(typeof mr === 'string' ? mr.toLowerCase() : 'MISSING')
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"module": "commonjs"}},
        {"wcd_wrapper.ts": _wcd_wrapper_import()},
    )
    assert result == "node", f"Expected moduleResolution='node' for commonjs, got '{result}'"


# [pr_diff] pass_to_pass
def test_amd_keeps_node_resolution():
    """When module is amd, moduleResolution stays 'node'."""
    script = f"""
import {{ writeConfigurationDefaults }} from './wcd_wrapper'
import {{ readFileSync }} from 'fs'
async function main() {{
  const p = process.argv[2]
  const origLog = console.log; console.log = () => {{}}
  try {{
    await writeConfigurationDefaults('5.9.2', p, false, true, '.next', true, false)
  }} finally {{ console.log = origLog }}
  const cfg = JSON.parse(readFileSync(p, 'utf8'))
  const mr = cfg.compilerOptions?.moduleResolution
  process.stdout.write(typeof mr === 'string' ? mr.toLowerCase() : 'MISSING')
}}
main().catch(e => process.stdout.write('ERROR:' + e.message))
"""
    result = _run_tsx(
        script,
        {"compilerOptions": {"module": "amd"}},
        {"wcd_wrapper.ts": _wcd_wrapper_import()},
    )
    assert result == "node", f"Expected moduleResolution='node' for amd, got '{result}'"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified files have substantive implementations (not stubs)."""
    wcd_lines = len(Path(WCD).read_text().splitlines())
    gtc_lines = len(Path(GTC).read_text().splitlines())
    assert wcd_lines >= 100, f"writeConfigurationDefaults.ts too short ({wcd_lines} lines)"
    assert gtc_lines >= 50, f"getTypeScriptConfiguration.ts too short ({gtc_lines} lines)"
    wcd_src = Path(WCD).read_text()
    assert "moduleResolution" in wcd_src, "writeConfigurationDefaults.ts missing moduleResolution handling"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — CLAUDE.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:309 @ 7dd1fcfc924be23cf2785054f5a2ad4f5affb692
def test_no_secret_files():
    """No secret files (env, credentials, keys) committed in agent changes."""
    r = subprocess.run(
        ["git", "diff", "HEAD", "--name-only"],
        cwd=REPO, capture_output=True, timeout=10, text=True,
    )
    changed = r.stdout.strip()
    for pat in [".env", ".env.local", "credentials.json", ".pem", ".key"]:
        for line in changed.splitlines():
            assert pat not in line, f"Secret file pattern '{pat}' found in diff: {line}"
