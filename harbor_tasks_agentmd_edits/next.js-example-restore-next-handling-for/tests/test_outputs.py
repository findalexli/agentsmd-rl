"""
Task: next.js-example-restore-next-handling-for
Repo: vercel/next.js @ 15fcfb9ce4ec73c6ff8d08d72201726b983127fa
PR:   90651

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — Dockerfile code fixes
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dockerfile_no_buildkit_cache_on_next():
    """Dockerfile build step must NOT use --mount=type=cache,target=/app/.next/cache."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile"
    content = dockerfile.read_text()
    # The BuildKit cache mount on .next/cache traps the fetch cache in a volume
    # unreachable by the runner stage. It must be removed from the build RUN.
    assert "--mount=type=cache,target=/app/.next/cache" not in content, (
        "Dockerfile should not mount .next/cache as a BuildKit cache volume "
        "— this traps the fetch cache and makes it unreachable in the runner stage"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_runner_mkdir_next():
    """Dockerfile runner stage must create a writable .next directory owned by node."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile"
    content = dockerfile.read_text()
    # Must have mkdir .next in the runner stage
    assert re.search(r"RUN\s+mkdir\s+\.next", content), (
        "Dockerfile runner stage must create .next directory with 'RUN mkdir .next'"
    )
    # Must chown to node user
    assert re.search(r"RUN\s+chown\s+node:node\s+\.next", content), (
        "Dockerfile runner stage must chown .next to node:node"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_bun_runner_mkdir_next():
    """Dockerfile.bun runner stage must create a writable .next directory owned by bun."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile.bun"
    content = dockerfile.read_text()
    assert re.search(r"RUN\s+mkdir\s+\.next", content), (
        "Dockerfile.bun runner stage must create .next directory with 'RUN mkdir .next'"
    )
    assert re.search(r"RUN\s+chown\s+bun:bun\s+\.next", content), (
        "Dockerfile.bun runner stage must chown .next to bun:bun"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_optional_fetch_cache_copy():
    """Dockerfile should have a commented-out COPY line for .next/cache as opt-in."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile"
    content = dockerfile.read_text()
    # Should have a commented COPY for .next/cache (opt-in for persisting fetch cache)
    assert re.search(r"#\s*COPY\s+--from=builder.*\.next/cache", content), (
        "Dockerfile should include a commented-out COPY line for .next/cache "
        "as opt-in for persisting build-time fetch cache"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_bun_optional_fetch_cache_copy():
    """Dockerfile.bun should have a commented-out COPY line for .next/cache as opt-in."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile.bun"
    content = dockerfile.read_text()
    assert re.search(r"#\s*COPY\s+--from=builder.*\.next/cache", content), (
        "Dockerfile.bun should include a commented-out COPY line for .next/cache "
        "as opt-in for persisting build-time fetch cache"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dockerfile_multistage_structure():
    """Dockerfile retains multi-stage build with dependencies, builder, runner stages."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile"
    content = dockerfile.read_text()
    assert "AS dependencies" in content, "Dockerfile must have 'dependencies' stage"
    assert "AS builder" in content, "Dockerfile must have 'builder' stage"
    assert "AS runner" in content, "Dockerfile must have 'runner' stage"


# [static] pass_to_pass
def test_dockerfile_bun_multistage_structure():
    """Dockerfile.bun retains multi-stage build with dependencies, builder, runner stages."""
    dockerfile = Path(REPO) / "examples" / "with-docker" / "Dockerfile.bun"
    content = dockerfile.read_text()
    assert "AS dependencies" in content, "Dockerfile.bun must have 'dependencies' stage"
    assert "AS builder" in content, "Dockerfile.bun must have 'builder' stage"
    assert "AS runner" in content, "Dockerfile.bun must have 'runner' stage"


# [static] pass_to_pass
def test_dockerfiles_copy_standalone_and_static():
    """Both Dockerfiles must still COPY .next/standalone and .next/static."""
    for name in ["Dockerfile", "Dockerfile.bun"]:
        dockerfile = Path(REPO) / "examples" / "with-docker" / name
        content = dockerfile.read_text()
        assert ".next/standalone" in content, (
            f"{name} must COPY .next/standalone"
        )
        assert ".next/static" in content, (
            f"{name} must COPY .next/static"
        )
