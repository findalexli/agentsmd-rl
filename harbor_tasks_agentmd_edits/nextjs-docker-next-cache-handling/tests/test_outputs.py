"""Tests for nextjs-docker-next-cache-handling: Dockerfile .next cache handling fix.

The PR removes a BuildKit cache mount on .next/cache that trapped fetch cache
in a volume unreachable by the runner stage, adds mkdir/chown for .next in the
runner stage so prerender cache is writable, and updates the README docs.
"""
import re
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/workspace/next.js")


def _read_file(rel_path: str) -> str:
    p = REPO / rel_path
    assert p.exists(), f"{p} does not exist"
    return p.read_text()


def _get_stage_content(content: str, stage_name: str) -> str:
    """Extract all lines from a named Dockerfile stage."""
    lines = content.split("\n")
    result = []
    in_stage = False
    for line in lines:
        if re.match(
            rf"^FROM\s+\S+\s+as\s+{re.escape(stage_name)}", line, re.IGNORECASE
        ):
            in_stage = True
            continue
        if line.startswith("FROM") and in_stage:
            break
        if in_stage:
            result.append(line)
    return "\n".join(result)


# ---------------------------------------------------------------------------
# F2P — Code tests (Dockerfile behavioral changes)
# ---------------------------------------------------------------------------


def test_dockerfile_no_buildkit_cache_mount():
    """BuildKit cache mount on .next/cache must be removed from the build RUN."""
    content = _read_file("examples/with-docker/Dockerfile")
    for line in content.split("\n"):
        stripped = line.strip()
        # Only actual RUN instructions, not comments mentioning the mount
        if stripped.startswith("RUN --mount=type=cache,target=/app/.next/cache"):
            assert False, (
                "RUN instruction should not use BuildKit cache mount on /app/.next/cache"
            )


def test_dockerfile_runner_mkdir_executes():
    """The RUN mkdir .next command in the runner stage must be present and executable."""
    content = _read_file("examples/with-docker/Dockerfile")
    runner = _get_stage_content(content, "runner")

    # Find the RUN mkdir instruction
    mkdir_cmd = None
    for line in runner.split("\n"):
        stripped = line.strip()
        if stripped.startswith("RUN mkdir "):
            mkdir_cmd = stripped[4:]  # strip "RUN "
            break

    assert mkdir_cmd is not None, "Runner stage must have a RUN mkdir .next instruction"

    # Actually execute the command to verify it works
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["sh", "-c", f"cd {tmpdir} && {mkdir_cmd}"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        assert result.returncode == 0, f"mkdir command failed: {result.stderr}"
        assert (Path(tmpdir) / ".next").is_dir(), ".next directory should exist"


def test_dockerfile_runner_chown_next():
    """Runner stage must set ownership of .next directory to node user."""
    content = _read_file("examples/with-docker/Dockerfile")
    runner = _get_stage_content(content, "runner")
    assert "chown node:node .next" in runner, (
        "Runner stage must chown .next to node:node for writable prerender cache"
    )


def test_dockerfile_bun_runner_creates_writable_next():
    """Dockerfile.bun runner stage must create .next with correct ownership."""
    content = _read_file("examples/with-docker/Dockerfile.bun")
    runner = _get_stage_content(content, "runner")
    assert "mkdir .next" in runner, (
        "Dockerfile.bun runner must create .next directory"
    )
    assert "chown bun:bun .next" in runner, (
        "Dockerfile.bun runner must chown .next to bun:bun"
    )


# ---------------------------------------------------------------------------
# F2P — Config / documentation update tests
# ---------------------------------------------------------------------------


def test_readme_documents_writable_next_dir():
    """with-docker README must document the writable .next directory feature."""
    readme = _read_file("examples/with-docker/README.md")
    lower = readme.lower()
    # Must mention writable .next directory
    assert "writable" in lower and ".next" in lower, (
        "README should document the writable .next directory"
    )
    # Must explain it's for prerender cache
    assert "prerender" in lower, (
        "README should explain .next directory is for prerender cache"
    )


def test_readme_cache_mount_description_updated():
    """README must explain the .next/cache mount is now optional, not default."""
    readme = _read_file("examples/with-docker/README.md")
    lower = readme.lower()
    # Must describe the cache mount as optional / mention .next/cache
    has_optional_cache = ("optional" in lower and ".next/cache" in lower) or (
        "optional" in lower and "cache mount" in lower
    )
    assert has_optional_cache, (
        "README should explain the .next/cache mount is optional for rebuild speed"
    )


# ---------------------------------------------------------------------------
# P2P — Structural / pass-to-pass tests
# ---------------------------------------------------------------------------


def test_dockerfile_runner_commands_valid_shell():
    """RUN commands in runner stage must have valid shell syntax."""
    content = _read_file("examples/with-docker/Dockerfile")
    runner = _get_stage_content(content, "runner")

    for line in runner.split("\n"):
        stripped = line.strip()
        if stripped.startswith("RUN "):
            cmd = stripped[4:]
            # Skip multiline continuations
            if cmd.endswith("\\"):
                continue
            result = subprocess.run(
                ["sh", "-n", "-c", cmd],
                capture_output=True,
                text=True,
                timeout=5,
            )
            assert result.returncode == 0, (
                f"Invalid shell syntax: {cmd}\n{result.stderr}"
            )


def test_dockerfile_build_command_present():
    """Dockerfile builder stage must have a build command."""
    content = _read_file("examples/with-docker/Dockerfile")
    assert "npm run build" in content or "yarn build" in content, (
        "Dockerfile must have a build command"
    )


# ---------------------------------------------------------------------------
# P2P — Repo CI/CD tests (pass_to_pass gates)
# These tests verify the repo's own CI checks pass on base commit and after fix
# ---------------------------------------------------------------------------


def test_repo_dockerfile_has_required_stages():
    """Repo CI: Dockerfile must have required stages (dependencies, builder, runner)."""
    content = _read_file("examples/with-docker/Dockerfile")
    stages = [m.group(1) for m in re.finditer(r"FROM\s+\S+\s+AS\s+(\w+)", content, re.I)]

    required = ["dependencies", "builder", "runner"]
    missing = [s for s in required if s not in stages]
    assert not missing, f"Missing required stages: {missing}, found: {stages}"


def test_repo_dockerfile_bun_has_required_stages():
    """Repo CI: Dockerfile.bun must have required stages (dependencies, builder, runner)."""
    content = _read_file("examples/with-docker/Dockerfile.bun")
    stages = [m.group(1) for m in re.finditer(r"FROM\s+\S+\s+AS\s+(\w+)", content, re.I)]

    required = ["dependencies", "builder", "runner"]
    missing = [s for s in required if s not in stages]
    assert not missing, f"Missing required stages: {missing}, found: {stages}"


def test_repo_with_docker_example_files_exist():
    """Repo CI: with-docker example must have all required files."""
    required_files = [
        "examples/with-docker/README.md",
        "examples/with-docker/Dockerfile",
        "examples/with-docker/Dockerfile.bun",
        "examples/with-docker/package.json",
        "examples/with-docker/tsconfig.json",
        "examples/with-docker/next.config.ts",
        "examples/with-docker/compose.yml",
    ]

    missing = []
    for rel_path in required_files:
        if not (REPO / rel_path).exists():
            missing.append(rel_path)

    assert not missing, f"Missing required files: {missing}"


def test_repo_with_docker_package_json_valid():
    """Repo CI: with-docker package.json must be private with required scripts."""
    import json

    pkg = json.loads(_read_file("examples/with-docker/package.json"))

    assert pkg.get("private") is True, "with-docker package.json must be private"

    required_scripts = ["dev", "build", "start"]
    scripts = pkg.get("scripts", {})
    missing = [s for s in required_scripts if s not in scripts]
    assert not missing, f"Missing required scripts: {missing}"


def test_repo_with_docker_readme_has_required_sections():
    """Repo CI: with-docker README must have required documentation sections."""
    readme = _read_file("examples/with-docker/README.md")
    lower = readme.lower()

    required_sections = [
        "features",
        "prerequisites",
        "docker compose",
        "docker build",
        "standalone mode",
        "deployment",
    ]

    missing = []
    for section in required_sections:
        if section not in lower:
            missing.append(section)

    assert not missing, f"Missing required README sections: {missing}"


def test_repo_dockerfile_has_multi_stage_build():
    """Repo CI: Dockerfile must use multi-stage build pattern."""
    content = _read_file("examples/with-docker/Dockerfile")

    # Check for FROM statements
    from_count = content.lower().count("from ")
    assert from_count >= 3, f"Expected at least 3 FROM statements for multi-stage build, found {from_count}"

    # Check for COPY --from=builder pattern
    assert "--from=builder" in content, "Dockerfile must copy files from builder stage"


def test_repo_dockerfile_bun_has_multi_stage_build():
    """Repo CI: Dockerfile.bun must use multi-stage build pattern."""
    content = _read_file("examples/with-docker/Dockerfile.bun")

    # Check for FROM statements
    from_count = content.lower().count("from ")
    assert from_count >= 3, f"Expected at least 3 FROM statements for multi-stage build, found {from_count}"

    # Check for COPY --from=builder pattern
    assert "--from=builder" in content, "Dockerfile.bun must copy files from builder stage"
