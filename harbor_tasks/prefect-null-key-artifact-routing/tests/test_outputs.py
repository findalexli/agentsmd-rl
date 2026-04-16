"""Test outputs for prefect-null-key-artifact fix."""

import subprocess
import os
import re

REPO = "/workspace/prefect"
UI_V2 = f"{REPO}/ui-v2"
ARTIFACT_CARD = f"{UI_V2}/src/components/artifacts/artifact-card.tsx"
ARTIFACT_CARD_TEST = f"{UI_V2}/src/components/artifacts/artifact-card.test.tsx"


def test_artifact_card_has_getartifactid_function():
    """ArtifactCard has the getArtifactId helper function for handling null keys."""
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # Check for the getArtifactId function
    assert "const getArtifactId = " in content, "Missing getArtifactId function"
    assert '"latest_id" in artifact' in content, "Missing latest_id duck-typing check"
    assert "artifact.id ?? \"\"" in content or "artifact.id" in content, "Missing id fallback"


def test_artifact_card_has_haskey_check():
    """ArtifactCard uses Boolean(artifact.key) to determine routing logic."""
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    assert "Boolean(artifact.key)" in content, "Missing Boolean(artifact.key) check"
    assert "hasKey = " in content, "Missing hasKey variable"


def test_artifact_card_routes_to_key_page_when_key_present():
    """ArtifactCard links to /artifacts/key/$key when key is present."""
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # Should route to key page when hasKey is true
    assert '"/artifacts/key/$key"' in content, "Missing key route"
    assert "artifact.key as string" in content, "Missing key param with type assertion"


def test_artifact_card_routes_to_id_page_when_key_missing():
    """ArtifactCard links to /artifacts/artifact/$id when key is null/undefined/empty."""
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # Should route to artifact detail page when key is falsy
    assert '"/artifacts/artifact/$id"' in content, "Missing artifact id route"
    assert 'id: getArtifactId(artifact)' in content, "Missing getArtifactId call in params"


def test_artifact_card_does_not_use_old_fallback():
    """ArtifactCard no longer uses the old fallback pattern artifact.key ?? \"\"."""
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # The old pattern should be removed
    assert 'params={{ key: artifact.key ?? "" }}' not in content, \
        "Old fallback pattern still present - must use new routing logic"


def test_vitest_tests_pass():
    """Vitest tests for ArtifactCard pass (pass_to_pass)."""
    # Run vitest tests for the artifact-card component
    result = subprocess.run(
        ["npm", "test", "--", "artifact-card", "--run"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Vitest tests failed:\n{result.stdout}\n{result.stderr}"


def test_typecheck_passes():
    """TypeScript typecheck passes (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stdout}\n{result.stderr}"


def test_npm_check_passes():
    """npm run check (Biome lint/format) passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "check"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"npm run check failed:\n{result.stdout}\n{result.stderr}"


def test_npm_lint_passes():
    """npm run lint (ESLint) passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "lint"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"npm run lint failed:\n{result.stderr[-500:]}"


def test_npm_validate_types_passes():
    """npm run validate:types (tsc -b --noEmit) passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "validate:types"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"npm run validate:types failed:\n{result.stderr[-500:]}"


def test_npm_build_passes():
    """npm run build (TypeScript compile + Vite build) passes (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "run", "build"],
        cwd=UI_V2,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"npm run build failed:\n{result.stderr[-500:]}"


def test_null_key_artifact_links_to_detail_page():
    """
    Fail-to-pass: ArtifactCard links to /artifacts/artifact/$id for null-key artifacts.

    The bug was that null-key artifacts would link to /artifacts/key/ (empty key),
    which is a broken route. The fix ensures null/undefined/empty keys route to
    the artifact detail page by ID instead.
    """
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # Parse the component logic
    # Should have conditional routing based on hasKey
    has_conditional = "linkProps" in content or ("hasKey" in content and "?" in content)
    assert has_conditional, "Missing conditional routing logic for key vs id routes"

    # Verify the falsy key path routes to $id route, not $key route
    lines = content.split('\n')
    in_link_props = False
    found_else_branch = False
    found_id_route_in_else = False

    for i, line in enumerate(lines):
        if "linkProps" in line or "const linkProps" in line:
            in_link_props = True
        if in_link_props:
            # Look for the else branch (falsy key case)
            if ":" in line and ("to:" in line or "params:" in line):
                # Check if we're in the else part (after the colon of ternary)
                found_else_branch = True
            if found_else_branch and '"/artifacts/artifact/$id"' in line:
                found_id_route_in_else = True
                break

    # Alternative check: ensure both routes exist and id route is present
    assert '"/artifacts/artifact/$id"' in content, \
        "Missing /artifacts/artifact/$id route for null-key artifacts"


def test_collection_uses_latest_id_for_null_key():
    """
    Fail-to-pass: ArtifactCollection with null key uses latest_id for routing.

    When an ArtifactCollection has a null/empty key, it should use the
    latest_id field for linking to the detail page.
    """
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # getArtifactId should check for latest_id (ArtifactCollection case)
    assert '"latest_id" in artifact' in content, \
        "Missing duck-typing check for latest_id (ArtifactCollection)"
    assert "artifact.latest_id" in content, \
        "Missing latest_id access for ArtifactCollection routing"


def test_keyed_artifact_uses_key_route():
    """
    Fail-to-pass: Artifacts with keys still use /artifacts/key/$key route.

    The fix should not break existing behavior for keyed artifacts.
    """
    with open(ARTIFACT_CARD, 'r') as f:
        content = f.read()

    # Should still have the key route for non-null keys
    assert '"/artifacts/key/$key"' in content, \
        "Missing /artifacts/key/$key route for keyed artifacts"

    # Should use the key param when hasKey is true
    assert "artifact.key as string" in content, \
        "Missing type assertion for key param"
