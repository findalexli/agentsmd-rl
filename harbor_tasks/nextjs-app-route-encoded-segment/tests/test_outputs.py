"""
Task: nextjs-app-route-encoded-segment
Repo: vercel/next.js @ 56d75a0b77f2ceda8ea747810275da8e0a9a3d71
PR:   91603

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/next.js"
TARGET_FILE = "packages/next/src/shared/lib/router/routes/app.ts"


def _parse_route(pathname: str) -> dict:
    """Run parseAppRoute via tsx and return {names, types, segmentCount}."""
    # Escape backticks and backslashes for template literal safety
    safe = pathname.replace("\\", "\\\\").replace("`", "\\`").replace("$", "\\$")
    code = textwrap.dedent(f"""\
        import {{ parseAppRoute }} from './packages/next/src/shared/lib/router/routes/app.js'
        const route = parseAppRoute(`{safe}`, false)
        const names = route.dynamicSegments.map((s: any) => s.param.paramName)
        const types = route.dynamicSegments.map((s: any) => s.param.type)
        console.log(JSON.stringify({{ names, types, segmentCount: route.segments.length }}))
    """)
    script = Path("/tmp/_test_route.ts")
    script.write_text(code)
    r = subprocess.run(
        ["tsx", str(script)],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"tsx failed:\n{r.stderr.decode()}"
    return json.loads(r.stdout.decode().strip())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript file must parse without errors."""
    r = subprocess.run(
        ["tsx", "--eval", f"import './{TARGET_FILE}'; console.log('OK')"],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, f"Import failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_encoded_single_dynamic():
    """Encoded single dynamic placeholder %5B...%5D is recognized."""
    # Test with several different param names
    r1 = _parse_route("/vercel/%5BprojectSlug%5D")
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/app/%5Bid%5D")
    assert "id" in r2["names"]

    r3 = _parse_route("/users/%5BuserId%5D/profile")
    assert "userId" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_multiple_dynamic():
    """Multiple encoded placeholders in same path both recognized."""
    r1 = _parse_route("/%5BteamSlug%5D/project/%5BprojectSlug%5D")
    assert "teamSlug" in r1["names"]
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/%5Borg%5D/%5Brepo%5D/%5Bbranch%5D")
    assert "org" in r2["names"]
    assert "repo" in r2["names"]
    assert "branch" in r2["names"]

    r3 = _parse_route("/api/%5Bversion%5D/users/%5BuserId%5D")
    assert "version" in r3["names"]
    assert "userId" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_mixed_segments():
    """Mixed encoded and non-encoded dynamic segments both recognized."""
    r1 = _parse_route("/[teamSlug]/%5BprojectSlug%5D")
    assert "teamSlug" in r1["names"]
    assert "projectSlug" in r1["names"]

    r2 = _parse_route("/%5Borg%5D/[repo]/[branch]")
    assert "org" in r2["names"]
    assert "repo" in r2["names"]
    assert "branch" in r2["names"]

    r3 = _parse_route("/[locale]/%5Bpage%5D/[section]")
    assert "locale" in r3["names"]
    assert "page" in r3["names"]
    assert "section" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_catchall_segment():
    """Encoded catchall segment %5B...slug%5D is recognized as dynamic."""
    r1 = _parse_route("/%5B...slug%5D")
    assert "slug" in r1["names"]

    r2 = _parse_route("/docs/%5B...path%5D")
    assert "path" in r2["names"]

    r3 = _parse_route("/%5B...segments%5D")
    assert "segments" in r3["names"]


# [pr_diff] fail_to_pass
def test_encoded_optional_catchall():
    """Encoded optional catchall %5B%5B...slug%5D%5D is recognized."""
    r1 = _parse_route("/%5B%5B...slug%5D%5D")
    assert "slug" in r1["names"]

    r2 = _parse_route("/docs/%5B%5B...path%5D%5D")
    assert "path" in r2["names"]

    r3 = _parse_route("/api/%5B%5B...rest%5D%5D")
    assert "rest" in r3["names"]


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_normal_dynamic_segments():
    """Non-encoded dynamic segments still work correctly."""
    r1 = _parse_route("/blog/[slug]/[id]")
    assert "slug" in r1["names"]
    assert "id" in r1["names"]

    r2 = _parse_route("/[locale]/dashboard")
    assert "locale" in r2["names"]

    r3 = _parse_route("/[...catchall]")
    assert "catchall" in r3["names"]

    r4 = _parse_route("/[[...optional]]")
    assert "optional" in r4["names"]


# [pr_diff] pass_to_pass
def test_static_segments():
    """Static segments are parsed correctly with no false dynamic matches."""
    r1 = _parse_route("/about/contact")
    assert r1["names"] == [], f"Expected no dynamic segments, got {r1['names']}"

    r2 = _parse_route("/api/health")
    assert r2["names"] == []

    r3 = _parse_route("/docs/getting-started/installation")
    assert r3["names"] == []


# [pr_diff] pass_to_pass
def test_malformed_encoding_no_crash():
    """Malformed URL encoding does not crash."""
    # Unclosed bracket encoding
    r1 = _parse_route("/test/%5Bparam")
    assert isinstance(r1["names"], list)

    # Partial percent encoding
    r2 = _parse_route("/test/%5")
    assert isinstance(r2["names"], list)

    # Random percent signs
    r3 = _parse_route("/test/100%25complete")
    assert isinstance(r3["names"], list)


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:302-309 @ 56d75a0
def test_no_hardcoded_secrets():
    """No hardcoded secret values in modified file (AGENTS.md:302-309)."""
    content = Path(f"{REPO}/{TARGET_FILE}").read_text()
    assert not re.search(
        r'(api[_-]?key|secret|token|password|credential)\s*[:=]\s*["\']',
        content,
        re.IGNORECASE,
    ), "Hardcoded secret values found"

