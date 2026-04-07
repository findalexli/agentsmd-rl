"""
Task: lobe-chat-fix-desktop-componentmap-sync
Repo: lobehub/lobe-chat @ 991de25b9757697553e1180096d8e1d5b8c0d83a
PR:   13243

The Electron desktop componentMap and desktopRouter config drifted from their
web counterparts, causing blank pages at /settings/stats, /settings/creds,
and /onboarding. The fix adds the missing entries and updates skill docs.
"""

import json
import subprocess
from pathlib import Path

REPO = "/workspace/lobe-chat"

DESKTOP_COMPONENTMAP = (
    f"{REPO}/src/routes/(main)/settings/features/componentMap.desktop.ts"
)
WEB_COMPONENTMAP = (
    f"{REPO}/src/routes/(main)/settings/features/componentMap.ts"
)
DESKTOP_ROUTER = (
    f"{REPO}/src/spa/router/desktopRouter.config.desktop.tsx"
)
WEB_ROUTER = (
    f"{REPO}/src/spa/router/desktopRouter.config.tsx"
)


def _node_extract_keys(file_path: str) -> set[str]:
    """Use Node.js to extract SettingsTabs.XXX keys from a componentMap file."""
    script = f"""
    const fs = require('fs');
    const src = fs.readFileSync('{file_path}', 'utf8');
    const re = /SettingsTabs\\.(\\w+)/g;
    const keys = new Set();
    let m;
    while ((m = re.exec(src)) !== null) keys.add(m[1]);
    console.log(JSON.stringify([...keys].sort()));
    """
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    return set(json.loads(r.stdout.strip()))


def _node_extract_paths(file_path: str) -> set[str]:
    """Use Node.js to extract route paths from a router config file."""
    script = f"""
    const fs = require('fs');
    const src = fs.readFileSync('{file_path}', 'utf8');
    // Match path: 'value' and path: "value" patterns
    const re = /path:\\s*['"]([^'"]+)['"]/g;
    const paths = new Set();
    let m;
    while ((m = re.exec(src)) !== null) paths.add(m[1]);
    console.log(JSON.stringify([...paths].sort()));
    """
    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )
    assert r.returncode == 0, f"Node failed: {r.stderr}"
    return set(json.loads(r.stdout.strip()))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavior tests
# ---------------------------------------------------------------------------


def test_componentmap_desktop_has_stats():
    """componentMap.desktop.ts must include Stats entry."""
    keys = _node_extract_keys(DESKTOP_COMPONENTMAP)
    assert "Stats" in keys, f"componentMap.desktop.ts missing Stats. Has: {sorted(keys)}"


def test_componentmap_desktop_has_creds():
    """componentMap.desktop.ts must include Creds entry."""
    keys = _node_extract_keys(DESKTOP_COMPONENTMAP)
    assert "Creds" in keys, f"componentMap.desktop.ts missing Creds. Has: {sorted(keys)}"


def test_componentmap_desktop_keys_match_web():
    """Desktop componentMap keys must be a superset of web componentMap keys."""
    web_keys = _node_extract_keys(WEB_COMPONENTMAP)
    desktop_keys = _node_extract_keys(DESKTOP_COMPONENTMAP)
    missing = web_keys - desktop_keys
    assert missing == set(), (
        f"componentMap.desktop.ts is missing keys that componentMap.ts has: {sorted(missing)}"
    )


def test_desktop_router_has_onboarding_route():
    """desktopRouter.config.desktop.tsx must include /onboarding path."""
    paths = _node_extract_paths(DESKTOP_ROUTER)
    assert "/onboarding" in paths, f"Missing /onboarding route. Paths: {sorted(paths)}"


def test_desktop_router_paths_match_web():
    """Desktop router must register all top-level paths that the web router has."""
    web_paths = _node_extract_paths(WEB_ROUTER)
    desktop_paths = _node_extract_paths(DESKTOP_ROUTER)
    web_toplevel = {p for p in web_paths if p.startswith("/")}
    desktop_toplevel = {p for p in desktop_paths if p.startswith("/")}
    missing = web_toplevel - desktop_toplevel
    assert missing == set(), (
        f"Desktop router missing top-level paths present in web router: {sorted(missing)}"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_react_skill_documents_desktop_sync_rule():
    """react/SKILL.md must document the .desktop file sync rule."""
    skill_path = Path(f"{REPO}/.agents/skills/react/SKILL.md")
    content = skill_path.read_text()
    has_sync = ".desktop" in content and ("sync" in content.lower() or "pair" in content.lower() or "drift" in content.lower())
    assert has_sync, (
        "react/SKILL.md must document the .desktop file sync rule "
        "(mention .desktop variants and sync/drift/pair)"
    )


def test_spa_routes_skill_documents_desktop_parity():
    """spa-routes/SKILL.md must document desktop router parity requirement."""
    skill_path = Path(f"{REPO}/.agents/skills/spa-routes/SKILL.md")
    content = skill_path.read_text()
    has_parity = (
        "desktopRouter.config.desktop" in content
        and ("both" in content.lower() or "parity" in content.lower() or "drift" in content.lower())
    )
    assert has_parity, (
        "spa-routes/SKILL.md must mention desktopRouter.config.desktop.tsx "
        "and require editing both files (both/parity/drift)"
    )


def test_code_review_skill_has_spa_routing_check():
    """code-review/SKILL.md must include SPA/routing section for desktopRouter pair."""
    skill_path = Path(f"{REPO}/.agents/skills/code-review/SKILL.md")
    content = skill_path.read_text()
    has_spa = (
        "desktopRouter" in content
        and ("SPA" in content or "routing" in content.lower())
    )
    assert has_spa, (
        "code-review/SKILL.md must include SPA/routing section "
        "mentioning desktopRouter pair checking"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_componentmap_desktop_imports_stats():
    """componentMap.desktop.ts must have an import for Stats module."""
    content = Path(DESKTOP_COMPONENTMAP).read_text()
    assert "import Stats from" in content or "import Stats" in content, (
        "componentMap.desktop.ts must import the Stats component"
    )


def test_componentmap_desktop_imports_creds():
    """componentMap.desktop.ts must have an import for Creds module."""
    content = Path(DESKTOP_COMPONENTMAP).read_text()
    assert "import Creds from" in content or "import Creds" in content, (
        "componentMap.desktop.ts must import the Creds component"
    )
