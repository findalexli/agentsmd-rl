"""Behavioral tests for tuist/tuist#10086 — registry-router origin additions.

The PR extends ORIGINS in `infra/registry-router/src/index.ts` and the
companion docs in `infra/AGENTS.md`. We exercise the worker module by
transpiling its TypeScript with the bundled tsc, exporting ORIGINS and
sortedByDistance via an appended `export {...}`, dynamic-importing the
result, and asserting on actual return values from sortedByDistance.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/tuist")
INDEX_TS = REPO / "infra" / "registry-router" / "src" / "index.ts"
INFRA_AGENTS_MD = REPO / "infra" / "AGENTS.md"
EXTRACT_HELPER = Path("/opt/test-helpers/extract_origins.cjs")


def _load_runtime_state():
    """Run the Node helper and return parsed JSON {origins, sortedProbes}."""
    r = subprocess.run(
        ["node", str(EXTRACT_HELPER), str(INDEX_TS)],
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"extract_origins.cjs failed (rc={r.returncode}):\n"
        f"--- stdout ---\n{r.stdout}\n--- stderr ---\n{r.stderr}"
    )
    return json.loads(r.stdout)


# -------------------------- pass-to-pass (repo CI) -------------------------- #

def test_repo_typecheck():
    """`tsc --noEmit` succeeds on the worker source (the package's CI command)."""
    r = subprocess.run(
        ["npx", "--no-install", "tsc", "--noEmit"],
        cwd=REPO / "infra" / "registry-router",
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"tsc --noEmit failed:\n--- stdout ---\n{r.stdout}\n"
        f"--- stderr ---\n{r.stderr}"
    )


def test_existing_origins_still_present():
    """The 6 pre-existing origins must still be in the routing table."""
    state = _load_runtime_state()
    hosts = {o["host"] for o in state["origins"]}
    pre_existing = {
        "cache-eu-central.tuist.dev",
        "cache-eu-north.tuist.dev",
        "cache-us-east.tuist.dev",
        "cache-us-west.tuist.dev",
        "cache-ap-southeast.tuist.dev",
        "cache-sa-west.tuist.dev",
    }
    missing = pre_existing - hosts
    assert not missing, f"Pre-existing origins removed: {missing}"


def test_routing_picks_known_continental_origins():
    """Routing for known points still resolves to the correct continent.

    Frankfurt -> cache-eu-central, Portland -> cache-us-west, Singapore ->
    cache-ap-southeast, Santiago -> cache-sa-west. These are pre-existing and
    must stay correct after the PR.
    """
    state = _load_runtime_state()
    expected = {
        "frankfurt":  "cache-eu-central.tuist.dev",
        "portland":   "cache-us-west.tuist.dev",
        "singapore":  "cache-ap-southeast.tuist.dev",
        "santiago":   "cache-sa-west.tuist.dev",
    }
    for label, want in expected.items():
        nearest = state["sortedProbes"][label][0]
        assert nearest == want, (
            f"From {label}, nearest origin is {nearest!r}; expected {want!r}"
        )


# ----------------------------- fail-to-pass -------------------------------- #

def test_au_east_origin_added():
    """An Australian east-coast origin (cache-au-east.tuist.dev) is registered.

    Coordinates must place it in eastern Australia so geo-routing actually
    picks it for AU/Oceania traffic. Loose bounds: anywhere in the
    Australian-east band (lat -45..-25, lon 140..160).
    """
    state = _load_runtime_state()
    matches = [o for o in state["origins"] if o["host"] == "cache-au-east.tuist.dev"]
    assert len(matches) == 1, (
        f"Expected exactly one cache-au-east.tuist.dev origin, got {len(matches)}: "
        f"{[o['host'] for o in state['origins']]}"
    )
    o = matches[0]
    assert -45.0 <= o["lat"] <= -25.0, f"au-east lat {o['lat']} not in eastern-AU band"
    assert 140.0 <= o["lon"] <= 160.0, f"au-east lon {o['lon']} not in eastern-AU band"


def test_us_east_2_origin_added():
    """A second us-east origin (cache-us-east-2.tuist.dev) is registered in Ashburn."""
    state = _load_runtime_state()
    matches = [o for o in state["origins"] if o["host"] == "cache-us-east-2.tuist.dev"]
    assert len(matches) == 1, (
        f"Expected exactly one cache-us-east-2.tuist.dev origin, got {len(matches)}: "
        f"{[o['host'] for o in state['origins']]}"
    )
    o = matches[0]
    # Ashburn area: roughly 35..45 N, -85..-70 W
    assert 35.0 <= o["lat"] <= 45.0, f"us-east-2 lat {o['lat']} not in US east band"
    assert -85.0 <= o["lon"] <= -70.0, f"us-east-2 lon {o['lon']} not in US east band"


def test_us_east_3_origin_added():
    """A third us-east origin (cache-us-east-3.tuist.dev) is registered in Ashburn."""
    state = _load_runtime_state()
    matches = [o for o in state["origins"] if o["host"] == "cache-us-east-3.tuist.dev"]
    assert len(matches) == 1, (
        f"Expected exactly one cache-us-east-3.tuist.dev origin, got {len(matches)}: "
        f"{[o['host'] for o in state['origins']]}"
    )
    o = matches[0]
    assert 35.0 <= o["lat"] <= 45.0, f"us-east-3 lat {o['lat']} not in US east band"
    assert -85.0 <= o["lon"] <= -70.0, f"us-east-3 lon {o['lon']} not in US east band"


def test_sydney_routes_to_au_east():
    """A request from Sydney must now resolve to cache-au-east as the nearest origin.

    Before the PR the closest origin for Sydney was Singapore (~6300 km); after
    adding au-east in Sydney the nearest is au-east (~0 km).
    """
    state = _load_runtime_state()
    sydney_sorted = state["sortedProbes"]["sydney"]
    assert sydney_sorted[0] == "cache-au-east.tuist.dev", (
        f"From Sydney, nearest origin is {sydney_sorted[0]!r}; "
        f"expected 'cache-au-east.tuist.dev'. Full ranking: {sydney_sorted}"
    )


def test_australian_cities_route_to_au_east():
    """Multiple Australian cities (not just Sydney) prefer cache-au-east.

    Tests that the new origin's coordinates are sensible enough to attract
    Melbourne and Brisbane traffic too — defending against an agent putting
    au-east at, say, the wrong lat/lon.
    """
    state = _load_runtime_state()
    for city in ("melbourne", "brisbane"):
        ranked = state["sortedProbes"][city]
        assert ranked[0] == "cache-au-east.tuist.dev", (
            f"From {city}, nearest origin is {ranked[0]!r}; expected "
            f"'cache-au-east.tuist.dev'. Full ranking: {ranked}"
        )


def test_ashburn_routes_to_us_east_family():
    """A request near Ashburn resolves to one of the cache-us-east* origins.

    Three of them now share Ashburn coordinates so we don't pin which one is
    first — only that the three are clustered at the top of the ranking.
    """
    state = _load_runtime_state()
    ashburn_top3 = set(state["sortedProbes"]["ashburn"][:3])
    expected_family = {
        "cache-us-east.tuist.dev",
        "cache-us-east-2.tuist.dev",
        "cache-us-east-3.tuist.dev",
    }
    assert ashburn_top3 == expected_family, (
        f"From Ashburn, top-3 origins are {ashburn_top3}; "
        f"expected the three us-east variants {expected_family}"
    )


def test_infra_agents_md_lists_new_origins():
    """infra/AGENTS.md documents the three new origins.

    The repo's intent-layer rule (see root AGENTS.md "Intent Layer
    Maintenance") requires keeping AGENTS.md consistent with the code under
    its scope; the file already has an "Origins:" bullet list and that list
    must include every host registered in ORIGINS.
    """
    text = INFRA_AGENTS_MD.read_text()
    # Origins are formatted as "- `cache-XXX.tuist.dev`" bullets.
    bullets = set(re.findall(r"`(cache-[a-z0-9-]+\.tuist\.dev)`", text))
    for new_host in (
        "cache-au-east.tuist.dev",
        "cache-us-east-2.tuist.dev",
        "cache-us-east-3.tuist.dev",
    ):
        assert new_host in bullets, (
            f"infra/AGENTS.md does not list {new_host}; "
            f"the Origins section must enumerate every host. Found: {sorted(bullets)}"
        )
