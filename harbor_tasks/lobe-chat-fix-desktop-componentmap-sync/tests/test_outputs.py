"""Tests for lobe-chat-fix-desktop-componentmap-sync"""
import json
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"

DESKTOP_COMPONENTMAP = f"{REPO}/src/routes/(main)/settings/features/componentMap.desktop.ts"
WEB_COMPONENTMAP = f"{REPO}/src/routes/(main)/settings/features/componentMap.ts"
DESKTOP_ROUTER = f"{REPO}/src/spa/router/desktopRouter.config.desktop.tsx"
WEB_ROUTER = f"{REPO}/src/spa/router/desktopRouter.config.tsx"

_deps_installed = False

def _ensure_deps():
    global _deps_installed
    if _deps_installed:
        return
    subprocess.run(["npm", "install", "-g", "pnpm"], capture_output=True, timeout=60)
    subprocess.run(["pnpm", "install"], capture_output=True, timeout=300, cwd=REPO)
    _deps_installed = True

def _extract_component_map_keys(file_path: str) -> set[str]:
    script = f"""
import {{ componentMap }} from '{file_path}';
console.log(JSON.stringify(Object.keys(componentMap)));
"""
    r = subprocess.run(["npx", "tsx", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    if r.returncode != 0:
        return _fallback_extract_ts_object_keys(file_path)
    return set(json.loads(r.stdout.strip()))

def _fallback_extract_ts_object_keys(file_path: str) -> set[str]:
    script = f"""
import * as ts from 'typescript';
import * as fs from 'fs';
const sourceCode = fs.readFileSync('{file_path}', 'utf8');
const sourceFile = ts.createSourceFile('temp.ts', sourceCode, ts.ScriptTarget.Latest, true);
function findObjectKeys(node) {{
    if (ts.isObjectLiteralExpression(node)) {{
        return node.properties
            .filter(p => ts.isPropertyAssignment(p))
            .map(p => p.name?.getText(sourceFile))
            .filter(name => !!name);
    }}
    let keys = [];
    ts.forEachChild(node, child => {{
        const childKeys = findObjectKeys(child);
        if (childKeys.length > 0) keys = childKeys;
    }});
    return keys;
}}
const keys = findObjectKeys(sourceFile);
console.log(JSON.stringify(keys));
"""
    r = subprocess.run(["npx", "tsx", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    if r.returncode != 0:
        return _regex_extract_settings_tabs_keys(file_path)
    return set(json.loads(r.stdout.strip()))

def _regex_extract_settings_tabs_keys(file_path: str) -> set[str]:
    content = Path(file_path).read_text()
    import re
    keys = set()
    for match in re.finditer(r'\[SettingsTabs\.(\w+)\]', content):
        keys.add(match.group(1))
    return keys

def _extract_router_paths(file_path: str) -> set[str]:
    script = f"""
import {{ desktopRoutes }} from '{file_path}';
function extractPaths(routes) {{
    const paths = [];
    function traverse(routeList) {{
        for (const route of routeList || []) {{
            if (route.path) paths.push(route.path);
            if (route.children) traverse(route.children);
        }}
    }}
    traverse(routes);
    return paths;
}}
console.log(JSON.stringify(extractPaths(desktopRoutes)));
"""
    r = subprocess.run(["npx", "tsx", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    if r.returncode != 0:
        return _fallback_extract_router_paths(file_path)
    return set(json.loads(r.stdout.strip()))

def _fallback_extract_router_paths(file_path: str) -> set[str]:
    script = f"""
import * as ts from 'typescript';
import * as fs from 'fs';
const sourceCode = fs.readFileSync('{file_path}', 'utf8');
const sourceFile = ts.createSourceFile('temp.tsx', sourceCode, ts.ScriptTarget.Latest, true);
function findPathProperties(node) {{
    const paths = [];
    function visit(node) {{
        if (ts.isPropertyAssignment(node) &&
            node.name.getText(sourceFile) === 'path' &&
            ts.isStringLiteral(node.initializer)) {{
            paths.push(node.initializer.text);
        }}
        ts.forEachChild(node, visit);
    }}
    visit(node);
    return paths;
}}
const paths = findPathProperties(sourceFile);
console.log(JSON.stringify(paths));
"""
    r = subprocess.run(["npx", "tsx", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    if r.returncode != 0:
        return _regex_extract_paths(file_path)
    return set(json.loads(r.stdout.strip()))

def _regex_extract_paths(file_path: str) -> set[str]:
    content = Path(file_path).read_text()
    import re
    paths = set()
    for match in re.finditer(r'path:\s*["\']([^"\']+)["\']', content):
        paths.add(match.group(1))
    return paths

# Fail-to-pass code behavior tests

def test_componentmap_desktop_has_stats():
    keys = _extract_component_map_keys(DESKTOP_COMPONENTMAP)
    assert "Stats" in keys, f"componentMap.desktop.ts missing Stats. Has: {sorted(keys)}"

def test_componentmap_desktop_has_creds():
    keys = _extract_component_map_keys(DESKTOP_COMPONENTMAP)
    assert "Creds" in keys, f"componentMap.desktop.ts missing Creds. Has: {sorted(keys)}"

def test_componentmap_desktop_keys_match_web():
    web_keys = _extract_component_map_keys(WEB_COMPONENTMAP)
    desktop_keys = _extract_component_map_keys(DESKTOP_COMPONENTMAP)
    missing = web_keys - desktop_keys
    assert missing == set(), f"componentMap.desktop.ts missing keys: {sorted(missing)}"

def test_desktop_router_has_onboarding_route():
    paths = _extract_router_paths(DESKTOP_ROUTER)
    assert "/onboarding" in paths, f"Missing /onboarding route. Paths: {sorted(paths)}"

def test_desktop_router_paths_match_web():
    web_paths = _extract_router_paths(WEB_ROUTER)
    desktop_paths = _extract_router_paths(DESKTOP_ROUTER)
    web_toplevel = {p for p in web_paths if p.startswith("/")}
    desktop_toplevel = {p for p in desktop_paths if p.startswith("/")}
    missing = web_toplevel - desktop_toplevel
    assert missing == set(), f"Desktop router missing paths: {sorted(missing)}"

# Fail-to-pass config/documentation tests

def test_react_skill_documents_desktop_sync_rule():
    skill_path = Path(f"{REPO}/.agents/skills/react/SKILL.md")
    content = skill_path.read_text()
    has_sync = ".desktop" in content and ("sync" in content.lower() or "pair" in content.lower() or "drift" in content.lower())
    assert has_sync, "react/SKILL.md must document the .desktop file sync rule"

def test_spa_routes_skill_documents_desktop_parity():
    skill_path = Path(f"{REPO}/.agents/skills/spa-routes/SKILL.md")
    content = skill_path.read_text()
    has_parity = "desktopRouter.config.desktop" in content and ("both" in content.lower() or "parity" in content.lower() or "drift" in content.lower())
    assert has_parity, "spa-routes/SKILL.md must document desktop router parity"

def test_code_review_skill_has_spa_routing_check():
    skill_path = Path(f"{REPO}/.agents/skills/code-review/SKILL.md")
    content = skill_path.read_text()
    has_spa = "desktopRouter" in content and ("SPA" in content or "routing" in content.lower())
    assert has_spa, "code-review/SKILL.md must include SPA/routing section"

# Fail-to-pass import verification tests

def test_componentmap_desktop_exports_stats_component():
    script = f"""
const fs = require('fs');
const content = fs.readFileSync('{DESKTOP_COMPONENTMAP}', 'utf8');
const hasImport = /import\\s+Stats\\s+from/.test(content);
const hasEntry = /\\[SettingsTabs\\.Stats\\]/.test(content);
console.log(JSON.stringify({{hasStats: hasImport && hasEntry}}));
"""
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0, f"node failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result.get("hasStats"), "componentMap.desktop.ts does not import or map Stats"

def test_componentmap_desktop_exports_creds_component():
    script = f"""
const fs = require('fs');
const content = fs.readFileSync('{DESKTOP_COMPONENTMAP}', 'utf8');
const hasImport = /import\\s+Creds\\s+from/.test(content);
const hasEntry = /\\[SettingsTabs\\.Creds\\]/.test(content);
console.log(JSON.stringify({{hasCreds: hasImport && hasEntry}}));
"""
    r = subprocess.run(["node", "-e", script], capture_output=True, text=True, timeout=30, cwd=REPO)
    assert r.returncode == 0, f"node failed: {r.stderr[-500:]}"
    result = json.loads(r.stdout.strip())
    assert result.get("hasCreds"), "componentMap.desktop.ts does not import or map Creds"

# Pass-to-pass repo tests

def test_repo_eslint_componentmap_desktop():
    _ensure_deps()
    r = subprocess.run(["npx", "eslint", DESKTOP_COMPONENTMAP, "--quiet"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"ESLint failed: {r.stderr[-500:]}"

def test_repo_eslint_desktop_router():
    _ensure_deps()
    r = subprocess.run(["npx", "eslint", DESKTOP_ROUTER, "--quiet"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"ESLint failed: {r.stderr[-500:]}"

def test_repo_stylelint_componentmap_desktop():
    _ensure_deps()
    r = subprocess.run(["npx", "stylelint", DESKTOP_COMPONENTMAP, "--quiet"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Stylelint failed: {r.stderr[-500:]}"

def test_repo_stylelint_desktop_router():
    _ensure_deps()
    r = subprocess.run(["npx", "stylelint", DESKTOP_ROUTER, "--quiet"], capture_output=True, text=True, timeout=120, cwd=REPO)
    assert r.returncode == 0, f"Stylelint failed: {r.stderr[-500:]}"

def test_repo_prettier_componentmap_desktop():
    _ensure_deps()
    r = subprocess.run(["npx", "prettier", "--check", DESKTOP_COMPONENTMAP], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Prettier failed: {r.stderr[-500:]}"

def test_repo_prettier_desktop_router():
    _ensure_deps()
    r = subprocess.run(["npx", "prettier", "--check", DESKTOP_ROUTER], capture_output=True, text=True, timeout=60, cwd=REPO)
    assert r.returncode == 0, f"Prettier failed: {r.stderr[-500:]}"

def test_repo_files_exist():
    required_files = [
        f"{REPO}/src/routes/(main)/settings/features/componentMap.ts",
        f"{REPO}/src/routes/(main)/settings/features/componentMap.desktop.ts",
        f"{REPO}/src/spa/router/desktopRouter.config.tsx",
        f"{REPO}/src/spa/router/desktopRouter.config.desktop.tsx",
    ]
    for f in required_files:
        assert Path(f).exists(), f"Required file does not exist: {f}"
