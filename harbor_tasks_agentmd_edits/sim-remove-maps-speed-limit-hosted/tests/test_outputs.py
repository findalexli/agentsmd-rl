"""
Task: sim-remove-maps-speed-limit-hosted
Repo: simstudioai/sim @ f161c261ef8fd77ff327a4e41104317ad00b7b08
PR:   3521

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/sim"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass

    assert speed_limits.exists(), "speed_limits.ts must exist"
    assert google_maps.exists(), "google_maps.ts must exist"
    assert skill_md.exists(), "SKILL.md must exist"

    sl_content = speed_limits.read_text()
    gm_content = google_maps.read_text()

    assert "googleMapsSpeedLimitsTool" in sl_content, \
        "speed_limits.ts must export googleMapsSpeedLimitsTool"
    assert "GoogleMapsBlock" in gm_content, \
        "google_maps.ts must export GoogleMapsBlock"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_hosting_removed_from_speed_limits():
    """Speed limits tool must not have a hosting config (deprecated Roads API)."""
    content = Path(REPO, "apps/sim/tools/google_maps/speed_limits.ts").read_text()
    # The hosting object with envKeyPrefix, byokProviderId, pricing, rateLimit must be gone
    assert "envKeyPrefix" not in content, \
        "speed_limits.ts should not contain envKeyPrefix (hosting config must be removed)"
    assert "byokProviderId" not in content, \
        "speed_limits.ts should not contain byokProviderId (hosting config must be removed)"
    assert "requestsPerMinute" not in content, \
        "speed_limits.ts should not contain requestsPerMinute (hosting rateLimit must be removed)"


# [pr_diff] fail_to_pass
def test_apikey_has_dual_subblocks():
    """Google Maps block must have two apiKey subblocks (one hosted, one always-visible)."""
    content = Path(REPO, "apps/sim/blocks/blocks/google_maps.ts").read_text()
    # Count occurrences of apiKey subblock declarations
    apikey_count = len(re.findall(r"""id:\s*['"]apiKey['"]""", content))
    assert apikey_count >= 2, \
        f"Expected at least 2 apiKey subblocks, found {apikey_count}. " \
        "Need one hosted (hideWhenHosted) and one always-visible for speed_limits."


# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass

    # Find all apiKey subblock starts
    apikey_indices = [i for i, line in enumerate(lines)
                      if re.search(r"id:\s*['\"]apiKey['\"]", line)]

    # For each apiKey subblock, inspect the surrounding lines (~12 lines covers the block)
    found_non_hosted_with_speed_limits = False
    for idx in apikey_indices:
        block_text = '\n'.join(lines[max(0, idx - 1):min(len(lines), idx + 12)])
        has_hide_when_hosted = 'hideWhenHosted' in block_text
        has_speed_limits_cond = bool(re.search(
            r"""value:\s*['"]speed_limits['"]""", block_text
        ))
        if not has_hide_when_hosted and has_speed_limits_cond:
            found_non_hosted_with_speed_limits = True

    assert found_non_hosted_with_speed_limits, \
        "Must have an apiKey subblock without hideWhenHosted that shows for speed_limits"


# ---------------------------------------------------------------------------
# Config edit — SKILL.md documentation update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must document the concept of excluding operations from hosted keys
    assert "exclud" in content_lower, \
        "SKILL.md should document excluding operations from hosted key support"

    # Must mention the duplicate apiKey subblock pattern
    assert "duplicate" in content_lower or "two" in content_lower or "opposing" in content_lower, \
        "SKILL.md should describe the duplicate/paired apiKey subblock technique"

    # Must reference the condition pattern with not: true
    assert "not: true" in content or "not:true" in content, \
        "SKILL.md should show the condition negation pattern (not: true)"

    # Must mention removing the hosting config from the tool
    assert "hosting" in content_lower and ("remove" in content_lower or "no hosting" in content_lower), \
        "SKILL.md should explain removing the hosting config from the tool definition"


# [config_edit] fail_to_pass

    # Must reference at least one real block/tool as a concrete example
    has_google_maps_ref = "google_maps" in content_lower or "google maps" in content_lower
    has_exa_ref = bool(re.search(r'\bexa\b', content_lower))  # word boundary to avoid "example"

    assert has_google_maps_ref or has_exa_ref, \
        "SKILL.md should reference at least one concrete implementation " \
        "(e.g., Google Maps speed_limits or Exa research)"
