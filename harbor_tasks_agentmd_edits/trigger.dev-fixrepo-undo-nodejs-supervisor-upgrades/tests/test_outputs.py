"""
Task: trigger.dev-fixrepo-undo-nodejs-supervisor-upgrades
Repo: triggerdotdev/trigger.dev @ 0b0df071bff0ffb91a4ff90767b32289608480c0
PR:   2895

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/trigger.dev"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dockerfile_no_arch_specific_digest():
    """docker/Dockerfile must not use the architecture-specific digest."""
    dockerfile = Path(REPO) / "docker" / "Dockerfile"
    content = dockerfile.read_text()
    # The broken arch-specific digest from the base commit
    assert "f52726bba3d47831859be141b4a57d3f7b93323f8fddfbd8375386e2c3b72319" not in content, \
        "Dockerfile still uses the architecture-specific digest that causes CI failures"


# [pr_diff] fail_to_pass
def test_dockerfile_uses_minor_version_tag():
    """docker/Dockerfile should use node:20.20-bullseye-slim (minor), not 20.20.0 (patch)."""
    dockerfile = Path(REPO) / "docker" / "Dockerfile"
    content = dockerfile.read_text()
    # Look for the ARG line — should NOT pin to patch version 20.20.0
    arg_match = re.search(r'ARG\s+NODE_IMAGE\s*=\s*node:(\S+)', content)
    assert arg_match, "Could not find ARG NODE_IMAGE line in Dockerfile"
    image_ref = arg_match.group(1)
    assert "20.20.0" not in image_ref, \
        f"Dockerfile pins to patch version 20.20.0: {image_ref}. Should use minor version (e.g., 20.20)"


# [pr_diff] fail_to_pass
def test_containerfile_no_arch_specific_digest():
    """apps/supervisor/Containerfile must not use the architecture-specific digest."""
    containerfile = Path(REPO) / "apps" / "supervisor" / "Containerfile"
    content = containerfile.read_text()
    assert "bcccf7410b77ca7447d292f616c7b0a89deff87e335fe91352ea04ce8babf50f" not in content, \
        "Containerfile still uses the architecture-specific digest"


# [pr_diff] fail_to_pass
def test_containerfile_not_pinned_to_22_22_0():
    """apps/supervisor/Containerfile should not pin to node:22.22.0-alpine."""
    containerfile = Path(REPO) / "apps" / "supervisor" / "Containerfile"
    content = containerfile.read_text()
    assert "22.22.0" not in content, \
        "Containerfile still pins to node 22.22.0 which should be reverted"


# [pr_diff] fail_to_pass
def test_nvmrc_not_v22_22_0():
    """apps/supervisor/.nvmrc should not specify v22.22.0."""
    nvmrc = Path(REPO) / "apps" / "supervisor" / ".nvmrc"
    content = nvmrc.read_text().strip()
    assert content != "v22.22.0", \
        ".nvmrc still specifies v22.22.0 which should be reverted"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — sanity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass


# [static] pass_to_pass


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
