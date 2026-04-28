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

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_check_for_releasable_changes_check_cli_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check CLI for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'cd cli\n# Get the latest CLI version tag dynamically\nLATEST_VERSION=$(git tag -l | grep -E \'^[0-9]+\\.[0-9]+\\.[0-9]+$\' | sort -V | tail -n1 || echo "0.0.0")\n\n# Check if there are any releasable changes by generating changelog\nCHANGELOG=$(git cliff --include-path "cli/**/*" --include-path ".xcode-version-releases" --include-path "Package.swift" --include-path "Package.resolved" --config cliff.toml --repository "../" 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  NEXT_VERSION=$(git cliff --include-path "cli/**/*" --include-path ".xcode-version-releases" --include-path "Package.swift" --include-path "Package.resolved" --config cliff.toml --repository "../" --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\nelse\n  NEXT_VERSION="$LATEST_VERSION"\nfi\n\necho "Latest CLI version: $LATEST_VERSION"\necho "Next CLI version: $NEXT_VERSION"\n\n# Validate that next version is actually newer\nif [ "$NEXT_VERSION" = "$LATEST_VERSION" ]; then\n  echo "No CLI version change detected (versions are equal)"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\nelif [ "$(printf \'%s\\n\' "$LATEST_VERSION" "$NEXT_VERSION" | sort -V | head -n1)" = "$NEXT_VERSION" ]; then\n  echo "ERROR: Next version ($NEXT_VERSION) is older than latest version ($LATEST_VERSION)"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\nelse\n  echo "CLI version bump detected: $LATEST_VERSION -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check CLI for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_app_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check App for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", 'cd app\n# Get the latest app version tag\nLATEST_VERSION=$(git tag -l | grep -E "^app@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --include-path "app/**/*" --include-path "mise/tasks/app/**/*" --config cliff.toml --repository "../" 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --include-path "app/**/*" --include-path "mise/tasks/app/**/*" --config cliff.toml --repository "../" 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --include-path "app/**/*" --include-path "mise/tasks/app/**/*" --config cliff.toml --repository "../" --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --include-path "app/**/*" --include-path "mise/tasks/app/**/*" --config cliff.toml --repository "../" --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#app@}"\n  else\n    NEXT_VERSION="0.1.0"\n  fi\nfi\n\n# Add app@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == app@* ]]; then\n  # If it already has app@ prefix, extract just the version number and re-add single prefix\n  VERSION_NUM="${NEXT_VERSION#app@}"\n  # Remove any additional app@ prefixes\n  while [[ "$VERSION_NUM" == app@* ]]; do\n    VERSION_NUM="${VERSION_NUM#app@}"\n  done\n  NEXT_VERSION="app@$VERSION_NUM"\nelse\n  NEXT_VERSION="app@$NEXT_VERSION"\nfi\n\necho "Latest App version: ${LATEST_VERSION:-none}"\necho "Next App version: $NEXT_VERSION"\n\n# Validate and compare versions\nif [ -z "$LATEST_VERSION" ]; then\n  # No previous version, this is the first release\n  echo "First App release: $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#app@}" >> "$GITHUB_OUTPUT"\nelif [ "$NEXT_VERSION" = "$LATEST_VERSION" ]; then\n  echo "No App version change detected (versions are equal)"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#app@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "App version bump detected: $LATEST_VERSION -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#app@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check App for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_server_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check Server for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", '# Get the latest server version tag\nLATEST_VERSION=$(git tag -l | grep -E "^server@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --include-path "server/**/*" --config server/cliff.toml --repository "." 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --include-path "server/**/*" --config server/cliff.toml --repository "." 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --include-path "server/**/*" --config server/cliff.toml --repository "." --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --include-path "server/**/*" --config server/cliff.toml --repository "." --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#server@}"\n  else\n    echo "No server tags or server-scoped commits found, defaulting to initial version"\n    NEXT_VERSION="0.1.0"\n  fi\nfi\n\n# Add server@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == server@* ]]; then\n  # If it already has server@ prefix, extract just the version number and re-add single prefix\n  VERSION_NUM="${NEXT_VERSION#server@}"\n  # Remove any additional server@ prefixes\n  while [[ "$VERSION_NUM" == server@* ]]; do\n    VERSION_NUM="${VERSION_NUM#server@}"\n  done\n  NEXT_VERSION="server@$VERSION_NUM"\nelse\n  NEXT_VERSION="server@$NEXT_VERSION"\nfi\n\necho "Latest Server version: ${LATEST_VERSION:-none}"\necho "Next Server version: $NEXT_VERSION"\n\n# Compare versions to determine if release is needed\nif [ "$LATEST_VERSION" != "$NEXT_VERSION" ]; then\n  echo "Server version bump detected: ${LATEST_VERSION:-none} -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#server@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "No Server version change detected"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#server@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Server for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_cache_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check Cache for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", '# Get the latest cache version tag\nLATEST_VERSION=$(git tag -l | grep -E "^cache@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --include-path "cache/**/*" --config cache/cliff.toml --repository "." 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --include-path "cache/**/*" --config cache/cliff.toml --repository "." 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --include-path "cache/**/*" --config cache/cliff.toml --repository "." --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --include-path "cache/**/*" --config cache/cliff.toml --repository "." --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#cache@}"\n  else\n    echo "No cache tags or cache-scoped commits found, defaulting to initial version"\n    NEXT_VERSION="0.1.0"\n  fi\nfi\n\n# Add cache@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == cache@* ]]; then\n  # If it already has cache@ prefix, extract just the version number and re-add single prefix\n  VERSION_NUM="${NEXT_VERSION#cache@}"\n  # Remove any additional cache@ prefixes\n  while [[ "$VERSION_NUM" == cache@* ]]; do\n    VERSION_NUM="${VERSION_NUM#cache@}"\n  done\n  NEXT_VERSION="cache@$VERSION_NUM"\nelse\n  NEXT_VERSION="cache@$NEXT_VERSION"\nfi\n\necho "Latest Cache version: ${LATEST_VERSION:-none}"\necho "Next Cache version: $NEXT_VERSION"\n\n# Compare versions to determine if release is needed\nif [ "$LATEST_VERSION" != "$NEXT_VERSION" ]; then\n  echo "Cache version bump detected: ${LATEST_VERSION:-none} -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#cache@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "No Cache version change detected"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#cache@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Cache for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_gradle_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check Gradle for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", '# Get the latest gradle version tag\nLATEST_VERSION=$(git tag -l | grep -E "^gradle@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --config gradle/cliff.toml --repository "." 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --config gradle/cliff.toml --repository "." 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --config gradle/cliff.toml --repository "." --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --config gradle/cliff.toml --repository "." --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#gradle@}"\n  else\n    echo "No gradle tags or gradle-scoped commits found, defaulting to initial version"\n    NEXT_VERSION="0.1.0"\n  fi\nfi\n\n# Add gradle@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == gradle@* ]]; then\n  # If it already has gradle@ prefix, extract just the version number and re-add single prefix\n  VERSION_NUM="${NEXT_VERSION#gradle@}"\n  # Remove any additional gradle@ prefixes\n  while [[ "$VERSION_NUM" == gradle@* ]]; do\n    VERSION_NUM="${VERSION_NUM#gradle@}"\n  done\n  NEXT_VERSION="gradle@$VERSION_NUM"\nelse\n  NEXT_VERSION="gradle@$NEXT_VERSION"\nfi\n\necho "Latest Gradle version: ${LATEST_VERSION:-none}"\necho "Next Gradle version: $NEXT_VERSION"\n\n# Compare versions to determine if release is needed\nif [ "$LATEST_VERSION" != "$NEXT_VERSION" ]; then\n  echo "Gradle version bump detected: ${LATEST_VERSION:-none} -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#gradle@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "No Gradle version change detected"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#gradle@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Gradle for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_skills_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check Skills for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", '# Get the latest skills version tag\nLATEST_VERSION=$(git tag -l | grep -E "^skills@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --include-path "skills/**/*" --config skills/cliff.toml --repository "." 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --include-path "skills/**/*" --config skills/cliff.toml --repository "." 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --include-path "skills/**/*" --config skills/cliff.toml --repository "." --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --include-path "skills/**/*" --config skills/cliff.toml --repository "." --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#skills@}"\n  else\n    echo "No skills tags or skills-scoped commits found, defaulting to initial version"\n    NEXT_VERSION="0.1.0"\n  fi\nfi\n\n# Add skills@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == skills@* ]]; then\n  # If it already has skills@ prefix, extract just the version number and re-add single prefix\n  VERSION_NUM="${NEXT_VERSION#skills@}"\n  # Remove any additional skills@ prefixes\n  while [[ "$VERSION_NUM" == skills@* ]]; do\n    VERSION_NUM="${VERSION_NUM#skills@}"\n  done\n  NEXT_VERSION="skills@$VERSION_NUM"\nelse\n  NEXT_VERSION="skills@$NEXT_VERSION"\nfi\n\necho "Latest Skills version: ${LATEST_VERSION:-none}"\necho "Next Skills version: $NEXT_VERSION"\n\n# Compare versions to determine if release is needed\nif [ "$LATEST_VERSION" != "$NEXT_VERSION" ]; then\n  echo "Skills version bump detected: ${LATEST_VERSION:-none} -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#skills@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "No Skills version change detected"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#skills@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Skills for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_releasable_changes_check_noora_for_releasable_changes():
    """pass_to_pass | CI job 'Check for releasable changes' → step 'Check Noora for releasable changes'"""
    r = subprocess.run(
        ["bash", "-lc", '# Get the latest noora version tag\nLATEST_VERSION=$(git tag -l | grep -E "^noora@[0-9]+\\.[0-9]+\\.[0-9]+$" | sort -V | tail -n1)\n\n# Check if there are any releasable changes by generating changelog\nif [ -n "$LATEST_VERSION" ]; then\n  CHANGELOG=$(git cliff --include-path "noora/**/*" --config noora/cliff.toml --repository "." 2>/dev/null -- ${LATEST_VERSION}..HEAD || echo "")\nelse\n  CHANGELOG=$(git cliff --include-path "noora/**/*" --config noora/cliff.toml --repository "." 2>/dev/null || echo "")\nfi\n\n# Only bump version if there are actual release notes\nif echo "$CHANGELOG" | sed -n \'/<!-- RELEASE NOTES START -->/,/<!-- generated by git-cliff -->/p\' | grep -qE \'^\\*\'; then\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION=$(git cliff --include-path "noora/**/*" --config noora/cliff.toml --repository "." --bumped-version 2>/dev/null -- ${LATEST_VERSION}..HEAD)\n  else\n    NEXT_VERSION=$(git cliff --include-path "noora/**/*" --config noora/cliff.toml --repository "." --bumped-version 2>/dev/null)\n  fi\nelse\n  if [ -n "$LATEST_VERSION" ]; then\n    NEXT_VERSION="${LATEST_VERSION#noora@}"\n  else\n    echo "No noora tags or noora-scoped commits found, defaulting to initial version"\n    NEXT_VERSION="0.73.0"\n  fi\nfi\n\n# Add noora@ prefix if not present and remove any duplicate prefixes\nif [[ "$NEXT_VERSION" == noora@* ]]; then\n  VERSION_NUM="${NEXT_VERSION#noora@}"\n  while [[ "$VERSION_NUM" == noora@* ]]; do\n    VERSION_NUM="${VERSION_NUM#noora@}"\n  done\n  NEXT_VERSION="noora@$VERSION_NUM"\nelse\n  NEXT_VERSION="noora@$NEXT_VERSION"\nfi\n\necho "Latest Noora version: ${LATEST_VERSION:-none}"\necho "Next Noora version: $NEXT_VERSION"\n\n# Compare versions to determine if release is needed\nif [ "$LATEST_VERSION" != "$NEXT_VERSION" ]; then\n  echo "Noora version bump detected: ${LATEST_VERSION:-none} -> $NEXT_VERSION"\n  echo "should-release=true" >> "$GITHUB_OUTPUT"\n  echo "next-version=$NEXT_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${NEXT_VERSION#noora@}" >> "$GITHUB_OUTPUT"\nelse\n  echo "No Noora version change detected"\n  echo "should-release=false" >> "$GITHUB_OUTPUT"\n  echo "next-version=$LATEST_VERSION" >> "$GITHUB_OUTPUT"\n  echo "next-version-number=${LATEST_VERSION#noora@}" >> "$GITHUB_OUTPUT"\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check Noora for releasable changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")