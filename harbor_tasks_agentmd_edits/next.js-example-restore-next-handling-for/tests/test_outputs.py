"""
Task: next.js-example-restore-next-handling-for
Repo: vercel/next.js @ ef993b251cef0a71050515665c26cfd41cdf090f
PR:   90651

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
DOCKERFILE = Path(f"{REPO}/examples/with-docker/Dockerfile")
DOCKERFILE_BUN = Path(f"{REPO}/examples/with-docker/Dockerfile.bun")
README = Path(f"{REPO}/examples/with-docker/README.md")


def _read_dockerfile(path: Path) -> str:
    """Read and return Dockerfile content."""
    return path.read_text()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dockerfile_no_buildkit_cache_mount():
    """Dockerfile build stage no longer uses BuildKit cache mount on .next/cache."""
    content = _read_dockerfile(DOCKERFILE)

    # The problematic line that was removed:
    # RUN --mount=type=cache,target=/app/.next/cache \
    #   if [ -f package-lock.json ]; then \

    # Check that the cache mount on .next/cache is NOT present
    assert "--mount=type=cache,target=/app/.next/cache" not in content, \
        "BuildKit cache mount on .next/cache should be removed (it traps fetch cache in unreachable volume)"


# [pr_diff] fail_to_pass
def test_dockerfile_has_mkdir_chown():
    """Dockerfile runner stage creates writable .next directory with correct ownership."""
    content = _read_dockerfile(DOCKERFILE)

    # The fix adds:
    # RUN mkdir .next
    # RUN chown node:node .next

    assert "RUN mkdir .next" in content, \
        "Runner stage should create .next directory for runtime cache"
    assert "RUN chown node:node .next" in content, \
        "Runner stage should set correct ownership on .next directory"


# [pr_diff] fail_to_pass
def test_dockerfile_has_optional_cache_copy():
    """Dockerfile includes commented line for optional fetch cache persistence."""
    content = _read_dockerfile(DOCKERFILE)

    # The fix adds a commented line:
    # # COPY --from=builder --chown=node:node /app/.next/cache ./.next/cache

    assert "# COPY --from=builder --chown=node:node /app/.next/cache ./.next/cache" in content, \
        "Dockerfile should include commented COPY line for optional fetch cache persistence"


# [pr_diff] fail_to_pass
def test_dockerfile_bun_has_mkdir_chown():
    """Dockerfile.bun runner stage creates writable .next directory with correct ownership."""
    content = _read_dockerfile(DOCKERFILE_BUN)

    # Dockerfile.bun never had the BuildKit mount issue, but needs the mkdir/chown fix
    assert "RUN mkdir .next" in content, \
        "Dockerfile.bun runner stage should create .next directory"
    assert "RUN chown bun:bun .next" in content, \
        "Dockerfile.bun runner stage should set correct ownership on .next directory"


# [pr_diff] fail_to_pass
def test_readme_no_emoji_prefixes():
    """README features list uses plain markdown bullets instead of emoji checkmarks."""
    content = README.read_text()

    # The fix removes emoji checkmarks from features list
    # Before: "- ✅ Multi-stage Docker build..."
    # After: "- Multi-stage Docker build..."

    # Check that the emoji checkmark pattern is NOT in the features section
    features_section_start = content.find("## Features")
    features_section_end = content.find("## Prerequisites")

    if features_section_start != -1 and features_section_end != -1:
        features_section = content[features_section_start:features_section_end]

        # The old version had "- ✅" pattern, new version has just "- " without emoji
        assert "- ✅" not in features_section and "- " in features_section, \
            "README features should use plain markdown bullets without emoji checkmarks"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dockerfile_syntax():
    """Dockerfile has valid syntax (basic structure check)."""
    content = _read_dockerfile(DOCKERFILE)

    # Basic Dockerfile structure checks
    assert "FROM" in content, "Dockerfile must have FROM instruction"
    assert "WORKDIR" in content, "Dockerfile must have WORKDIR instruction"

    # Check for balanced structure - should have multiple stages
    from_count = content.count("\nFROM")
    assert from_count >= 2, f"Expected multi-stage Dockerfile with at least 3 stages, found {from_count + 1}"


# [static] pass_to_pass
def test_dockerfile_bun_syntax():
    """Dockerfile.bun has valid syntax."""
    content = _read_dockerfile(DOCKERFILE_BUN)

    assert "FROM" in content, "Dockerfile.bun must have FROM instruction"
    assert "WORKDIR" in content, "Dockerfile.bun must have WORKDIR instruction"


# [static] pass_to_pass
def test_dockerfile_has_build_stage():
    """Dockerfile has builder stage with npm run build."""
    content = _read_dockerfile(DOCKERFILE)

    # Should have a builder stage
    assert "AS builder" in content or "as builder" in content, \
        "Dockerfile should have a builder stage"

    # Should have build command
    assert "npm run build" in content or "yarn build" in content or "pnpm build" in content, \
        "Dockerfile should have a build command"


# [static] pass_to_pass
def test_dockerfile_has_runner_stage():
    """Dockerfile has runner stage with production server."""
    content = _read_dockerfile(DOCKERFILE)

    # Should have a runner stage
    assert "AS runner" in content or "as runner" in content, \
        "Dockerfile should have a runner stage"

    # Should have production server command
    assert "server.js" in content or "CMD" in content, \
        "Dockerfile should have server command"
