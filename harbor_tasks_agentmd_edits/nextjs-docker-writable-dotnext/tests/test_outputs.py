"""
Task: nextjs-docker-writable-dotnext
Repo: vercel/next.js @ 15fcfb9ce4ec73c6ff8d08d72201726b983127fa
PR:   90651

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path
import json
import re

REPO = "/workspace/next.js"
DOCKERFILE = f"{REPO}/examples/with-docker/Dockerfile"
DOCKERFILE_BUN = f"{REPO}/examples/with-docker/Dockerfile.bun"
README = f"{REPO}/examples/with-docker/README.md"


def _get_stage_lines(dockerfile_path: str, stage_name: str) -> list[str]:
    """Extract lines from a specific Dockerfile stage."""
    lines = Path(dockerfile_path).read_text().splitlines()
    stage_lines = []
    in_stage = False
    for line in lines:
        stripped = line.strip()
        # Detect stage start: FROM ... AS <name> (case-insensitive)
        if stripped.upper().startswith("FROM") and f"AS {stage_name.upper()}" in line.upper().replace("  ", " "):
            in_stage = True
            stage_lines.append(line)
            continue
        # Detect next stage start
        if in_stage and stripped.upper().startswith("FROM"):
            break
        if in_stage:
            stage_lines.append(line)
    return stage_lines


def _get_build_stage_lines(dockerfile_path: str) -> list[str]:
    """Extract lines from the builder stage."""
    return _get_stage_lines(dockerfile_path, "builder")


def _get_runner_stage_lines(dockerfile_path: str) -> list[str]:
    """Extract lines from the runner stage."""
    return _get_stage_lines(dockerfile_path, "runner")


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_dockerfile_syntax_valid():
    """Dockerfiles have valid structure and single-line RUN commands parse correctly."""
    for df_path in [DOCKERFILE, DOCKERFILE_BUN]:
        content = Path(df_path).read_text()
        lines = content.splitlines()
        # Must have FROM lines (valid Dockerfile)
        assert any(line.strip().startswith("FROM") for line in lines), f"No FROM in {df_path}"
        # Check single-line RUN commands for shell syntax errors
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped.startswith("RUN") or stripped.startswith("RUN --mount"):
                continue
            cmd = stripped[3:].strip()
            # Skip empty, comments, and multi-line continuations
            if not cmd or cmd.startswith("#") or cmd.endswith("\\"):
                continue
            result = subprocess.run(
                ["sh", "-n", "-c", cmd],
                capture_output=True, text=True, timeout=10,
            )
            assert result.returncode == 0, (
                f"Shell syntax error in {df_path}:{i}: {cmd}\n{result.stderr}"
            )


# [static] pass_to_pass
def test_standalone_copy_intact():
    """COPY .next/standalone and .next/static still present (regression check)."""
    for df_path in [DOCKERFILE, DOCKERFILE_BUN]:
        content = Path(df_path).read_text()
        assert "COPY --from=builder" in content, f"Missing COPY --from=builder in {df_path}"
        assert ".next/standalone" in content, f"Missing .next/standalone COPY in {df_path}"
        assert ".next/static" in content, f"Missing .next/static COPY in {df_path}"


# [repo_tests] pass_to_pass
def test_dockerfile_lint():
    """Repo's Dockerfile passes dockerfilelint validation (pass_to_pass)."""
    # Install dockerfilelint
    r = subprocess.run(
        ["npm", "install", "-g", "dockerfilelint"],
        capture_output=True, text=True, timeout=120,
    )
    # Run dockerfilelint on both Dockerfiles
    for df_path in [DOCKERFILE, DOCKERFILE_BUN]:
        r = subprocess.run(
            ["dockerfilelint", df_path],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"dockerfilelint failed for {df_path}:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_dockerfile_hadolint():
    """Repo's Dockerfile passes hadolint validation (pass_to_pass)."""
    # Download hadolint binary
    hadolint_path = "/tmp/hadolint"
    r = subprocess.run(
        ["curl", "-sL", "-o", hadolint_path,
         "https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to download hadolint: {r.stderr}"

    r = subprocess.run(["chmod", "+x", hadolint_path], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Failed to chmod hadolint: {r.stderr}"

    # Run hadolint on both Dockerfiles
    for df_path in [DOCKERFILE, DOCKERFILE_BUN]:
        r = subprocess.run(
            [hadolint_path, df_path],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"hadolint failed for {df_path}:\n{r.stdout}\n{r.stderr}"


# [static] pass_to_pass
def test_package_json_valid():
    """package.json files are valid JSON (pass_to_pass)."""
    for pkg_path in [
        f"{REPO}/examples/with-docker/package.json",
        f"{REPO}/examples/with-docker-export-output/package.json",
    ]:
        content = Path(pkg_path).read_text()
        try:
            json.loads(content)
        except json.JSONDecodeError as e:
            assert False, f"Invalid JSON in {pkg_path}: {e}"


# [static] pass_to_pass
def test_compose_yml_valid():
    """compose.yml files have valid YAML structure (pass_to_pass)."""
    # Basic YAML validation - check structure without pyyaml
    for compose_path in [
        f"{REPO}/examples/with-docker/compose.yml",
        f"{REPO}/examples/with-docker-export-output/compose.yml",
    ]:
        content = Path(compose_path).read_text()
        lines = content.splitlines()

        # Check for YAML structural validity
        prev_indent = 0
        for i, line in enumerate(lines, 1):
            if not line.strip() or line.strip().startswith("#"):
                continue

            # Calculate indentation
            indent = len(line) - len(line.lstrip())

            # YAML uses 2-space indentation typically
            # Indentation should not increase by more than 2 spaces at a time
            if indent > prev_indent and indent - prev_indent > 2:
                # Allow this only if previous line ended with :
                prev_line = lines[i - 2] if i > 1 else ""
                if not prev_line.rstrip().endswith(":"):
                    assert False, f"Invalid indentation jump at {compose_path}:{i}"

            # Check for tab characters (invalid in YAML)
            assert "\t" not in line, f"Tab character found in {compose_path}:{i}"

            prev_indent = indent

        # Must have required YAML keys for a valid compose file
        assert "version:" in content or "services:" in content, (
            f"compose.yml missing required structure (version or services)"
        )


# [repo_tests] pass_to_pass
def test_dockerfile_export_output_lint():
    """with-docker-export-output Dockerfiles pass dockerfilelint validation (pass_to_pass)."""
    # Ensure dockerfilelint is installed
    r = subprocess.run(
        ["npm", "install", "-g", "dockerfilelint"],
        capture_output=True, text=True, timeout=120,
    )
    # Run dockerfilelint on both Dockerfiles
    for df_path in [
        f"{REPO}/examples/with-docker-export-output/Dockerfile",
        f"{REPO}/examples/with-docker-export-output/Dockerfile.serve",
    ]:
        r = subprocess.run(
            ["dockerfilelint", df_path],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"dockerfilelint failed for {df_path}:\n{r.stdout}"


# [repo_tests] pass_to_pass
def test_dockerfile_export_output_hadolint():
    """with-docker-export-output Dockerfiles pass hadolint validation (pass_to_pass)."""
    # Download hadolint binary
    hadolint_path = "/tmp/hadolint"
    r = subprocess.run(
        ["curl", "-sL", "-o", hadolint_path,
         "https://github.com/hadolint/hadolint/releases/download/v2.12.0/hadolint-Linux-x86_64"],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Failed to download hadolint: {r.stderr}"

    r = subprocess.run(["chmod", "+x", hadolint_path], capture_output=True, text=True, timeout=10)
    assert r.returncode == 0, f"Failed to chmod hadolint: {r.stderr}"

    # Run hadolint on both Dockerfiles
    for df_path in [
        f"{REPO}/examples/with-docker-export-output/Dockerfile",
        f"{REPO}/examples/with-docker-export-output/Dockerfile.serve",
    ]:
        r = subprocess.run(
            [hadolint_path, df_path],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"hadolint failed for {df_path}:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_readme_export_output_prettier():
    """with-docker-export-output/README.md passes prettier formatting check (pass_to_pass)."""
    readme_path = f"{REPO}/examples/with-docker-export-output/README.md"
    r = subprocess.run(
        ["npx", "prettier", "--check", readme_path],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for export-output README:\n{r.stdout}\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_dockerfile_runner_creates_dotnext():
    """Runner stage must create .next directory with correct ownership."""
    runner_lines = _get_runner_stage_lines(DOCKERFILE)
    runner_text = "\n".join(runner_lines)

    has_mkdir = any("mkdir .next" in line and line.strip().startswith("RUN") for line in runner_lines)
    has_chown = any("chown node:node .next" in line and line.strip().startswith("RUN") for line in runner_lines)

    assert has_mkdir, "Runner stage missing 'RUN mkdir .next'"
    assert has_chown, "Runner stage missing 'RUN chown node:node .next'"

    # Verify mkdir command actually works (execute the extracted command)
    with tempfile.TemporaryDirectory() as tmpdir:
        result = subprocess.run(
            ["sh", "-c", f"cd {tmpdir} && mkdir .next && test -d .next"],
            capture_output=True, text=True, timeout=10,
        )
        assert result.returncode == 0, f"mkdir .next command failed: {result.stderr}"


# [pr_diff] fail_to_pass
def test_dockerfile_build_no_cache_mount():
    """Build stage RUN command must NOT mount cache on .next/cache."""
    content = Path(DOCKERFILE).read_text()
    lines = content.splitlines()

    # Find the RUN line that does the build (npm run build / yarn build / pnpm build)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("RUN") and "npm run build" in content[max(0, content.find(stripped)):content.find(stripped) + 500]:
            # Check this RUN block doesn't have --mount=type=cache,target=/app/.next/cache
            # Collect the full RUN block (may span multiple lines with backslash)
            block = stripped
            j = i + 1
            while j < len(lines) and lines[j - 1].rstrip().endswith("\\"):
                block += "\n" + lines[j]
                j += 1
            assert "--mount=type=cache,target=/app/.next/cache" not in block, (
                "Build RUN command still has cache mount on .next/cache"
            )
            # Found the build block, no need to check further
            return

    # Fallback: just verify no cache mount on .next/cache in the entire file
    assert "--mount=type=cache,target=/app/.next/cache" not in content, (
        "Dockerfile still has cache mount on .next/cache"
    )


# [pr_diff] fail_to_pass
def test_dockerfile_bun_creates_dotnext():
    """Dockerfile.bun runner stage must also create .next with correct ownership."""
    runner_lines = _get_runner_stage_lines(DOCKERFILE_BUN)
    runner_text = "\n".join(runner_lines)

    has_mkdir = any("mkdir .next" in line and line.strip().startswith("RUN") for line in runner_lines)
    has_chown = any("chown bun:bun .next" in line and line.strip().startswith("RUN") for line in runner_lines)

    assert has_mkdir, "Dockerfile.bun runner stage missing 'RUN mkdir .next'"
    assert has_chown, "Dockerfile.bun runner stage missing 'RUN chown bun:bun .next'"


# ---------------------------------------------------------------------------
# Config/documentation update tests (REQUIRED for agentmd-edit tasks)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_writable_dotnext():
    """README.md must document the writable .next directory feature."""
    readme = Path(README)
    assert readme.exists(), "README.md not found"
    content = readme.read_text().lower()

    # Check for key concepts: writable, .next, directory/node user
    assert "writable" in content and ".next" in content, (
        "README should mention writable .next directory"
    )
    assert "prerender cache" in content or "runtime cache" in content, (
        "README should explain that .next is writable for prerender/runtime cache"
    )


# [pr_diff] fail_to_pass
def test_readme_describes_cache_tradeoff():
    """README.md must explain the BuildKit cache mount tradeoff."""
    readme = Path(README)
    content = readme.read_text()

    # The README should explain that the .next/cache mount is optional
    # and describe the tradeoff (speed vs fetch cache in final image)
    has_optional_mount = (
        ("optional" in content.lower() or "uncomment" in content.lower() or "opt-in" in content.lower())
        and ".next/cache" in content
    ) or (
        # Or the highlights section mentions the change
        "cache" in content.lower() and "rebuilds" in content.lower()
    )

    assert has_optional_mount, (
        "README should describe the .next/cache mount as optional and explain the tradeoff"
    )


# [repo_tests] pass_to_pass
def test_readme_prettier():
    """README.md passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", README],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for README:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_compose_prettier():
    """compose.yml passes prettier formatting check (pass_to_pass)."""
    compose_path = f"{REPO}/examples/with-docker/compose.yml"
    r = subprocess.run(
        ["npx", "prettier", "--check", compose_path],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed for compose.yml:\n{r.stdout}\n{r.stderr}"
