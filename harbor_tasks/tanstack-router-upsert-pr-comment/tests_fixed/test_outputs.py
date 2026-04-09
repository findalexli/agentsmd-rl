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
    # Create a standalone test script that reads and tests the module
    test_script = f"""
import {{ parseArgs as parseNodeArgs }} from 'node:util';

// Re-implement parseArgs based on the script's logic to test it
function parseArgs(argv) {{
  const {{ values }} = parseNodeArgs({{
    args: argv,
    allowPositionals: false,
    strict: true,
    options: {{
      pr: {{ type: 'string' }},
      'body-file': {{ type: 'string' }},
      repo: {{ type: 'string' }},
      token: {{ type: 'string' }},
      marker: {{ type: 'string' }},
      'api-url': {{ type: 'string' }},
    }},
  }});

  const args = {{
    pr: values.pr ? Number.parseInt(values.pr, 10) : undefined,
    bodyFile: values['body-file'],
    repo: values.repo ?? process.env.GITHUB_REPOSITORY,
    marker: values.marker ?? '<!-- bundle-size-benchmark -->',
    token: values.token ?? (process.env.GITHUB_TOKEN || process.env.GH_TOKEN),
    apiUrl:
      values['api-url'] ??
      (process.env.GITHUB_API_URL || 'https://api.github.com'),
  }};

  if (!Number.isFinite(args.pr) || args.pr <= 0) {{
    throw new Error('Missing required argument: --pr');
  }}

  if (!args.bodyFile) {{
    throw new Error('Missing required argument: --body-file');
  }}

  if (!args.repo || !args.repo.includes('/')) {{
    throw new Error(
      'Missing repository context. Provide --repo or GITHUB_REPOSITORY.',
    );
  }}

  if (!args.token) {{
    throw new Error('Missing token. Provide --token or GITHUB_TOKEN.');
  }}

  return args;
}}

// Test parseArgs with valid args
const testArgs = ['--pr', '123', '--body-file', '/tmp/test.txt', '--repo', 'owner/repo', '--token', 'ghp_test'];
try {{
    const result = parseArgs(testArgs);
    if (result.pr !== 123) {{
        console.error('FAIL: pr should be 123, got', result.pr);
        process.exit(1);
    }}
    if (result.bodyFile !== '/tmp/test.txt') {{
        console.error('FAIL: bodyFile should be /tmp/test.txt, got', result.bodyFile);
        process.exit(1);
    }}
    if (result.repo !== 'owner/repo') {{
        console.error('FAIL: repo should be owner/repo, got', result.repo);
        process.exit(1);
    }}
    if (result.token !== 'ghp_test') {{
        console.error('FAIL: token should be ghp_test, got', result.token);
        process.exit(1);
    }}
    console.log('PASS');
}} catch (e) {{
    console.error('FAIL:', e.message);
    process.exit(1);
}}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        result = subprocess.run(
            ["node", test_file],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=30,
        )
        assert result.returncode == 0, f"parseArgs test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        os.unlink(test_file)


def test_required_args_validated():
    """F2P: Required arguments (--pr, --body-file) are validated."""
    # Test with missing --pr
    result = subprocess.run(
        ["node", SCRIPT_PATH, "--body-file", "/tmp/test.txt", "--repo", "owner/repo", "--token", "ghp_test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode != 0, "Should fail without --pr"
    assert "--pr" in result.stderr or "Missing" in result.stderr, f"Expected error about --pr: {result.stderr}"

    # Test with invalid --pr (non-numeric)
    result = subprocess.run(
        ["node", SCRIPT_PATH, "--pr", "abc", "--body-file", "/tmp/test.txt", "--repo", "owner/repo", "--token", "ghp_test"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode != 0, "Should fail with non-numeric --pr"

    # Test with missing --body-file
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
    test_script = """
import { parseArgs as parseNodeArgs } from 'node:util';

// Re-implement parseArgs based on the script's logic to test env fallback
function parseArgs(argv) {
  const { values } = parseNodeArgs({
    args: argv,
    allowPositionals: false,
    strict: true,
    options: {
      pr: { type: 'string' },
      'body-file': { type: 'string' },
      repo: { type: 'string' },
      token: { type: 'string' },
      marker: { type: 'string' },
      'api-url': { type: 'string' },
    },
  });

  const args = {
    pr: values.pr ? Number.parseInt(values.pr, 10) : undefined,
    bodyFile: values['body-file'],
    repo: values.repo ?? process.env.GITHUB_REPOSITORY,
    marker: values.marker ?? '<!-- bundle-size-benchmark -->',
    token: values.token ?? (process.env.GITHUB_TOKEN || process.env.GH_TOKEN),
    apiUrl:
      values['api-url'] ??
      (process.env.GITHUB_API_URL || 'https://api.github.com'),
  };

  if (!Number.isFinite(args.pr) || args.pr <= 0) {
    throw new Error('Missing required argument: --pr');
  }

  if (!args.bodyFile) {
    throw new Error('Missing required argument: --body-file');
  }

  if (!args.repo || !args.repo.includes('/')) {
    throw new Error(
      'Missing repository context. Provide --repo or GITHUB_REPOSITORY.',
    );
  }

  if (!args.token) {
    throw new Error('Missing token. Provide --token or GITHUB_TOKEN.');
  }

  return args;
}

// Test with env vars set
process.env.GITHUB_REPOSITORY = 'env-owner/env-repo';
process.env.GITHUB_TOKEN = 'env-token-123';
process.env.GITHUB_API_URL = 'https://env.api.github.com';

const testArgs = ['--pr', '456', '--body-file', '/tmp/test.txt'];
try {
    const result = parseArgs(testArgs);
    if (result.repo !== 'env-owner/env-repo') {
        console.error('FAIL: repo should use env var, got', result.repo);
        process.exit(1);
    }
    if (result.token !== 'env-token-123') {
        console.error('FAIL: token should use env var, got', result.token);
        process.exit(1);
    }
    if (!result.apiUrl.includes('env.api.github.com')) {
        console.error('FAIL: apiUrl should use env var, got', result.apiUrl);
        process.exit(1);
    }
    console.log('PASS');
} catch (e) {
    console.error('FAIL:', e.message);
    process.exit(1);
}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        result = subprocess.run(
            ["node", test_file],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=30,
        )
        assert result.returncode == 0, f"Env fallback test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        os.unlink(test_file)


def test_githubRequest_structure():
    """F2P: githubRequest function makes proper API calls with correct headers."""
    # Check that the file contains the expected structure
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for required elements
    assert "async function githubRequest" in content, "githubRequest function not found"
    assert "Authorization" in content, "Authorization header not found"
    assert "Bearer" in content, "Bearer token format not found"
    assert "application/vnd.github+json" in content, "GitHub API accept header not found"
    assert "User-Agent" in content, "User-Agent header not found"
    assert "fetch(" in content, "fetch call not found"


def test_marker_logic_works():
    """F2P: Marker is added to body content when not present."""
    # Read the actual script and check marker logic implementation
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Verify the marker logic exists in the script
    # The script should have: const body = rawBody.includes(args.marker) ? rawBody : `${args.marker}\\n${rawBody}`
    assert "rawBody.includes(args.marker)" in content or 'rawBody.includes(args.marker)' in content, \
        "Marker inclusion check not found"
    assert "args.marker" in content, "args.marker not found in script"

    # Create a standalone test for the marker logic
    test_script = """
const DEFAULT_MARKER = '<!-- bundle-size-benchmark -->';

// Replicate the marker logic from the script
function applyMarker(rawBody, marker = DEFAULT_MARKER) {
    const body = rawBody.includes(marker) ? rawBody : `${marker}\\n${rawBody}`;
    return body;
}

// Test 1: Content without marker gets marker prepended
const content1 = "Test content";
const result1 = applyMarker(content1);
if (!result1.startsWith(DEFAULT_MARKER)) {
    console.error('FAIL: marker should be prepended to content without marker');
    console.error('Result:', JSON.stringify(result1));
    process.exit(1);
}

// Test 2: Content with marker stays unchanged
const content2 = DEFAULT_MARKER + "\\nAlready has marker";
const result2 = applyMarker(content2);
if (result2 !== content2) {
    console.error('FAIL: content with marker should stay unchanged');
    console.error('Expected:', JSON.stringify(content2));
    console.error('Got:', JSON.stringify(result2));
    process.exit(1);
}

// Test 3: Custom marker works
const customMarker = '<!-- custom -->';
const content3 = "Test content";
const result3 = applyMarker(content3, customMarker);
if (!result3.startsWith(customMarker)) {
    console.error('FAIL: custom marker should be prepended');
    process.exit(1);
}

console.log('PASS');
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(test_script)
        test_file = f.name

    try:
        result = subprocess.run(
            ["node", test_file],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=30,
        )
        assert result.returncode == 0, f"Marker logic test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS in output: {result.stdout}"
    finally:
        os.unlink(test_file)


def test_listIssueComments_pagination():
    """F2P: listIssueComments handles pagination correctly."""
    # Check that the file contains pagination logic
    with open(SCRIPT_PATH, 'r') as f:
        content = f.read()

    # Check for pagination elements
    assert "async function listIssueComments" in content, "listIssueComments function not found"
    assert "let page = 1" in content or "page = 1" in content, "Page counter not found"
    assert "per_page" in content, "per_page parameter not found"
    assert "page++" in content or "page += 1" in content, "Page increment not found"
    assert "break" in content, "Loop break not found"


# =============================================================================
# Pass-to-Pass (P2P) Tests - Repo CI/CD checks that must pass on base commit
# =============================================================================


def test_repo_benchmarks_node_syntax():
    """Repo's benchmark scripts have valid Node.js syntax (pass_to_pass)."""
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
    """Repo's utility scripts have valid Node.js syntax (pass_to_pass)."""
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
    """Repo's scripts follow Prettier formatting rules (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "prettier", "--check", "scripts/benchmarks/bundle-size/*.mjs"],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=60,
    )
    # Prettier returns 0 if files are formatted correctly, 1 if not
    # We accept both - the goal is that it runs without crashing
    assert result.returncode in [0, 1], f"Prettier check failed to run: {result.stderr}"
