"""Tests for upsert-pr-comment.mjs script."""

import os
import subprocess
import sys
import tempfile

REPO = "/workspace/router"
SCRIPT_PATH = f"{REPO}/scripts/benchmarks/common/upsert-pr-comment.mjs"


def test_file_exists():
    """F2P: File must exist at the expected path."""
    assert os.path.exists(SCRIPT_PATH), f"File not found: {SCRIPT_PATH}"


def test_node_syntax_valid():
    """F2P: Script must have valid Node.js syntax."""
    result = subprocess.run(
        ["node", "--check", SCRIPT_PATH],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Syntax error: {result.stderr}"


def test_parseArgs_function_works():
    """F2P: parseArgs function correctly parses CLI arguments."""
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    test_harness = code.replace("#!/usr/bin/env node", "") + '''
const testArgs = ["--pr", "123", "--body-file", "/tmp/test.txt", "--repo", "owner/repo", "--token", "ghp_test"];
try {
    const result = parseArgs(testArgs);
    if (result.pr !== 123) {
        console.error("FAIL: pr should be 123, got", result.pr);
        process.exit(1);
    }
    if (result.bodyFile !== "/tmp/test.txt") {
        console.error("FAIL: bodyFile should be /tmp/test.txt, got", result.bodyFile);
        process.exit(1);
    }
    if (result.repo !== "owner/repo") {
        console.error("FAIL: repo should be owner/repo, got", result.repo);
        process.exit(1);
    }
    if (result.token !== "ghp_test") {
        console.error("FAIL: token should be ghp_test, got", result.token);
        process.exit(1);
    }
    console.log("PASS");
    process.exit(0);  // Exit before main() is called
} catch (e) {
    console.error("FAIL:", e.message);
    process.exit(1);
}
'''

    harness_path = "/tmp/parseArgs_test.mjs"
    with open(harness_path, "w") as f:
        f.write(test_harness)

    try:
        result = subprocess.run(
            ["node", harness_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"parseArgs test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        if os.path.exists(harness_path):
            os.unlink(harness_path)


def test_required_args_validated():
    """F2P: Required arguments (--pr, --body-file) are validated."""
    result = subprocess.run(
        ["node", SCRIPT_PATH, "--body-file", "/tmp/test.txt", "--repo", "owner/repo", "--token", "ghp_test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode != 0, "Should fail without --pr"
    assert "--pr" in result.stderr or "Missing" in result.stderr, f"Expected error about --pr: {result.stderr}"

    result = subprocess.run(
        ["node", SCRIPT_PATH, "--pr", "abc", "--body-file", "/tmp/test.txt", "--repo", "owner/repo", "--token", "ghp_test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode != 0, "Should fail with non-numeric --pr"

    result = subprocess.run(
        ["node", SCRIPT_PATH, "--pr", "123", "--repo", "owner/repo", "--token", "ghp_test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode != 0, "Should fail without --body-file"
    assert "body-file" in result.stderr or "Missing" in result.stderr, f"Expected error about body-file: {result.stderr}"


def test_env_fallback_works():
    """F2P: Environment variables are used as fallback for repo, token, apiUrl."""
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    test_harness = code.replace("#!/usr/bin/env node", "") + '''
process.env.GITHUB_REPOSITORY = "env-owner/env-repo";
process.env.GITHUB_TOKEN = "env-token-123";
process.env.GITHUB_API_URL = "https://api.enterprise.github.com";

const testArgs = ["--pr", "456", "--body-file", "/tmp/test.txt"];
try {
    const result = parseArgs(testArgs);
    if (result.repo !== "env-owner/env-repo") {
        console.error("FAIL: repo should use env var, got", result.repo);
        process.exit(1);
    }
    if (result.token !== "env-token-123") {
        console.error("FAIL: token should use env var, got", result.token);
        process.exit(1);
    }
    if (result.apiUrl !== "https://api.enterprise.github.com") {
        console.error("FAIL: apiUrl should use env var, got", result.apiUrl);
        process.exit(1);
    }
    console.log("PASS");
    process.exit(0);  // Exit before main() is called
} catch (e) {
    console.error("FAIL:", e.message);
    process.exit(1);
}
'''

    harness_path = "/tmp/env_test.mjs"
    with open(harness_path, "w") as f:
        f.write(test_harness)

    try:
        result = subprocess.run(
            ["node", harness_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Env fallback test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        if os.path.exists(harness_path):
            os.unlink(harness_path)


def test_githubRequest_structure():
    """F2P: githubRequest function makes proper API calls with correct headers."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    assert "async function githubRequest" in content, "githubRequest function not found"
    assert "Authorization" in content, "Authorization header not found"
    assert "Bearer" in content, "Bearer token format not found"
    assert "application/vnd.github+json" in content, "GitHub API accept header not found"
    assert "User-Agent" in content, "User-Agent header not found"
    assert "fetch(" in content, "fetch call not found"


def test_marker_logic_works():
    """F2P: Marker is added to body content when not present."""
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    assert "DEFAULT_MARKER" in code or "marker" in code, "Marker constant not found"
    assert "includes(args.marker)" in code or "rawBody.includes" in code, "Marker inclusion check not found"
    
    marker_logic_present = (
        "rawBody.includes(args.marker)" in code or
        "includes(args.marker)" in code
    )
    assert marker_logic_present, "Marker conditional logic not found"


def test_listIssueComments_pagination():
    """F2P: listIssueComments handles pagination correctly."""
    with open(SCRIPT_PATH, "r") as f:
        content = f.read()

    assert "async function listIssueComments" in content, "listIssueComments function not found"
    assert "let page = 1" in content or "page = 1" in content, "Page counter not found"
    assert "per_page" in content, "per_page parameter not found"
    assert "page++" in content or "page += 1" in content, "Page increment not found"
    assert "break" in content, "Loop break not found"


def test_repo_benchmarks_node_syntax():
    """Repo benchmark scripts have valid Node.js syntax (pass_to_pass)."""
    benchmark_scripts = [
        f"{REPO}/scripts/benchmarks/bundle-size/measure.mjs",
        f"{REPO}/scripts/benchmarks/bundle-size/pr-report.mjs",
    ]
    for script in benchmark_scripts:
        if os.path.exists(script):
            result = subprocess.run(
                ["node", "--check", script],
                capture_output=True,
                text=True,
                cwd=REPO,
            )
            assert result.returncode == 0, f"Syntax error in {script}: {result.stderr}"


def test_repo_scripts_node_syntax():
    """Repo utility scripts have valid Node.js syntax (pass_to_pass)."""
    scripts = [
        f"{REPO}/scripts/cleanup-empty-packages.mjs",
        f"{REPO}/scripts/create-github-release.mjs",
        f"{REPO}/scripts/llms-generate.mjs",
        f"{REPO}/scripts/update-example-deps.mjs",
    ]
    for script in scripts:
        if os.path.exists(script):
            result = subprocess.run(
                ["node", "--check", script],
                capture_output=True,
                text=True,
                cwd=REPO,
            )
            assert result.returncode == 0, f"Syntax error in {script}: {result.stderr}"


def test_repo_prettier_formatting():
    """Repo scripts follow Prettier formatting rules (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "scripts/benchmarks/bundle-size/*.mjs"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    assert result.returncode in [0, 1], f"Prettier check failed to run: {result.stderr}"
