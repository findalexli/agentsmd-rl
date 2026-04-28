import json
import os
import subprocess

REPO = "/workspace/workers-sdk"
PKG_JSON_PATH = os.path.join(REPO, "packages/vite-plugin-cloudflare/package.json")
AGENTS_MD_PATH = os.path.join(REPO, "packages/vite-plugin-cloudflare/AGENTS.md")


def test_vite8_peer_dependency():
    """peerDependencies.vite includes ^8.0.0 (fail_to_pass)."""
    with open(PKG_JSON_PATH) as f:
        pkg = json.load(f)

    peer_vite = pkg["peerDependencies"]["vite"]
    ranges = [r.strip() for r in peer_vite.split("||")]

    # At least one range in the disjunction must satisfy a Vite 8.x version
    v8_ok = any("8" in r for r in ranges)
    assert v8_ok, f"peerDependencies.vite '{peer_vite}' does not include Vite 8 support"


def test_agents_md_vite8_stable():
    """AGENTS.md describes Vite 8 as stable, not beta (fail_to_pass)."""
    with open(AGENTS_MD_PATH) as f:
        content = f.read()

    assert "Vite 6/7/8 in CI" in content, (
        "AGENTS.md should say 'Vite 6/7/8 in CI' (stable), not 'Vite 6/7/8-beta in CI'"
    )
    assert "8-beta" not in content, (
        "AGENTS.md should not reference Vite 8 as beta"
    )


def test_package_json_parseable():
    """package.json is valid JSON parseable by Node.js (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e", "JSON.parse(require('fs').readFileSync('packages/vite-plugin-cloudflare/package.json','utf8')); console.log('ok')"],
        cwd=REPO, capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"Node failed to parse package.json: {r.stderr}"
    assert "ok" in r.stdout

def test_vite_peer_dep_retains_v6_v7():
    """peerDependencies.vite retains ^6.1.0 and ^7.0.0 (pass_to_pass)."""
    with open(PKG_JSON_PATH) as f:
        pkg = json.load(f)
    peer_vite = pkg["peerDependencies"]["vite"]
    assert "^6.1.0" in peer_vite, (
        f"peerDependencies.vite '{peer_vite}' must retain ^6.1.0"
    )
    assert "^7.0.0" in peer_vite, (
        f"peerDependencies.vite '{peer_vite}' must retain ^7.0.0"
    )