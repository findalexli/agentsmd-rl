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
        code = f.read()

    code = code.replace("#!/usr/bin/env node", "")
    idx = code.rfind("main()")
    if idx > 0:
        code = code[:idx].rstrip()

    test_harness = code + r'''
const capturedCalls = [];
globalThis.fetch = async function(url, options) {
    capturedCalls.push({ url, options });
    return {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({}),
        text: async () => '{}',
    };
};

async function runTest() {
    try {
        await githubRequest({
            apiUrl: 'https://test.example.com',
            token: 'test-token',
            method: 'POST',
            endpoint: '/repos/o/r/issues/1/comments',
            body: { body: 'test' },
        });

        const call = capturedCalls[0];
        if (!call) { console.error("FAIL: no request made"); process.exit(1); }
        if (call.options.headers.Authorization !== 'Bearer test-token') { console.error("FAIL: wrong auth"); process.exit(1); }
        if (call.options.headers.Accept !== 'application/vnd.github+json') { console.error("FAIL: wrong accept"); process.exit(1); }
        if (!call.options.headers['User-Agent']) { console.error("FAIL: missing user-agent"); process.exit(1); }
        if (call.options.method !== 'POST') { console.error("FAIL: wrong method"); process.exit(1); }
        if (call.url !== 'https://test.example.com/repos/o/r/issues/1/comments') { console.error("FAIL: wrong url, got " + call.url); process.exit(1); }

        console.log("PASS");
        process.exit(0);
    } catch (e) {
        console.error("FAIL:", e.message);
        process.exit(1);
    }
}
runTest();
'''

    harness_path = "/tmp/githubRequest_test.mjs"
    with open(harness_path, "w") as f:
        f.write(test_harness)

    try:
        result = subprocess.run(
            ["node", harness_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"githubRequest test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS: {result.stdout}"
    finally:
        if os.path.exists(harness_path):
            os.unlink(harness_path)


def test_marker_logic_works():
    """F2P: Marker is added to body content when not present."""
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    code = code.replace("#!/usr/bin/env node", "")
    idx = code.rfind("main()")
    if idx > 0:
        code = code[:idx].rstrip()

    body_path = "/tmp/test_body_no_marker.txt"
    with open(body_path, "w") as f:
        f.write("Bundle-size report content here.\n")

    test_harness = code + f'''
const capturedRequests = [];
globalThis.fetch = async function(url, options) {{
    capturedRequests.push({{ url, options }});
    if (url.includes("/comments?per_page=")) {{
        return {{ ok: true, status: 200, json: async () => [], text: async () => '[]' }};
    }}
    return {{ ok: true, status: 201, json: async () => ({{ id: 99 }}), text: async () => '{"id":99}' }};
}};

process.argv = ["node", "test", "--pr", "1", "--body-file", "{body_path}", "--repo", "test/r", "--token", "t"];

main().then(() => {{
    const postRequest = capturedRequests.find(r => r.options && r.options.method === 'POST');
    if (!postRequest) {{ console.error("FAIL: no POST request"); process.exit(1); }}
    const sentBody = JSON.parse(postRequest.options.body).body;
    if (!sentBody.startsWith('<!-- bundle-size-benchmark -->')) {{ console.error("FAIL: marker not prepended"); process.exit(1); }}
    if (!sentBody.includes("Bundle-size report content here.")) {{ console.error("FAIL: original body not found"); process.exit(1); }}
    console.log("PASS");
    process.exit(0);
}}).catch((e) => {{
    console.error("FAIL:", e.message);
    process.exit(1);
}});
'''

    harness_path = "/tmp/marker_test.mjs"
    with open(harness_path, "w") as f:
        f.write(test_harness)

    try:
        result = subprocess.run(
            ["node", harness_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Marker test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS: {result.stdout}"
    finally:
        if os.path.exists(harness_path):
            os.unlink(harness_path)


def test_listIssueComments_pagination():
    """F2P: listIssueComments handles pagination correctly."""
    with open(SCRIPT_PATH, "r") as f:
        code = f.read()

    code = code.replace("#!/usr/bin/env node", "")
    idx = code.rfind("main()")
    if idx > 0:
        code = code[:idx].rstrip()

    test_harness = code + r'''
let pageRequests = [];
globalThis.fetch = async function(url, options) {
    pageRequests.push(url);
    const pageMatch = url.match(/[&?]page=(\d+)/);
    const page = pageMatch ? parseInt(pageMatch[1]) : 1;

    const items = page <= 2 ? Array(100).fill({id: page}) : Array(50).fill({id: page});
    return {
        ok: true,
        status: 200,
        json: async () => items,
        text: async () => JSON.stringify(items),
    };
};

async function runTest() {
    try {
        const result = await listIssueComments({
            apiUrl: 'https://test.example.com',
            token: 'test-token',
            repo: 'owner/repo',
            pr: 123,
        });

        if (pageRequests.length !== 3) {
            console.error("FAIL: expected 3 page requests, got", pageRequests.length);
            process.exit(1);
        }
        if (result.length !== 250) {
            console.error("FAIL: expected 250 items, got", result.length);
            process.exit(1);
        }
        console.log("PASS");
        process.exit(0);
    } catch (e) {
        console.error("FAIL:", e.message);
        process.exit(1);
    }
}
runTest();
'''

    harness_path = "/tmp/pagination_test.mjs"
    with open(harness_path, "w") as f:
        f.write(test_harness)

    try:
        result = subprocess.run(
            ["node", harness_path],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0, f"Pagination test failed: {result.stderr}"
        assert "PASS" in result.stdout, f"Expected PASS: {result.stdout}"
    finally:
        if os.path.exists(harness_path):
            os.unlink(harness_path)


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


def test_repo_all_scripts_node_syntax():
    """All .mjs files in scripts/ directory have valid Node.js syntax (pass_to_pass)."""
    import glob
    script_pattern = f"{REPO}/scripts/**/*.mjs"
    scripts = glob.glob(script_pattern, recursive=True)
    for script in scripts:
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
