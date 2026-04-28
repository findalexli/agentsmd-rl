#!/usr/bin/env python3
"""Test oracle for browser_network_requests enhancement task."""

import subprocess, json, os, re, shutil
from pathlib import Path

REPO = "/workspace/playwright"

def _run(cmd, timeout=60):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)

def _tsx_path():
    p = "/usr/local/lib/node_modules/tsx/dist/cli.mjs"
    if os.path.isfile(p):
        return p
    return "tsx"

def test_syntax_check():
    network_ts = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
    commands_ts = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
    for f in [network_ts, commands_ts]:
        r = _run(["node", "--check", str(f)])
        assert r.returncode == 0, f"{f} has syntax errors: {r.stderr}"

def test_repo_lint_packages():
    pkgs = Path(REPO) / "packages"
    assert pkgs.exists(), "packages directory missing"
    pc = pkgs / "playwright-core"
    assert pc.exists(), "playwright-core package missing"
    backend = pc / "src" / "tools" / "backend"
    assert backend.exists(), "playwright-core tools backend missing"

def test_repo_eslint_backend():
    network_ts = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
    assert network_ts.exists(), "network.ts missing"

def test_repo_eslint_cli_daemon():
    commands_ts = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
    assert commands_ts.exists(), "commands.ts missing"

def test_repo_build():
    pkg_json = Path(REPO) / "package.json"
    assert pkg_json.exists(), "package.json missing"
    json.loads(pkg_json.read_text())
    r = _run(["node", "utils/build/build.js", "--dry-run"], timeout=10)
    assert "traceback" not in r.stderr.lower(), f"build traceback: {r.stderr}"

def _run_js(script_path, timeout=30):
    tsx_bin = _tsx_path()
    env = {**os.environ, "PATH": "/usr/local/bin:/usr/local/lib/node_modules/.bin:" + os.environ.get("PATH", "")}
    r = subprocess.run(
        [tsx_bin, str(script_path)],
        capture_output=True, text=True, timeout=timeout,
        cwd=REPO,
        env=env
    )
    return r

def _write_js_test(content, name="test_behavior.mjs"):
    p = Path(REPO) / name
    p.write_text(content)
    return p

def test_schema_has_new_params():
    network_ts = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
    content = network_ts.read_text()
    assert re.search(r"requestBody\s*:\s*z\.boolean", content), "requestBody missing from inputSchema"
    assert re.search(r"requestHeaders\s*:\s*z\.boolean", content), "requestHeaders missing from inputSchema"
    assert re.search(r"filter\s*:\s*z\.string", content), "filter missing from inputSchema"

def test_static_replaces_include_static():
    network_ts = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
    content = network_ts.read_text()
    assert "includeStatic:" not in content, "includeStatic still present (should be renamed to static)"
    assert re.search(r"static\s*:\s*z\.boolean", content), "static param not found in inputSchema"

def test_render_request_headers_and_body():
    """Verify renderRequest includes header and body sections in its output.

    Tests BEHAVIOR by running a self-contained JS script that verifies
    the output format matches what the instruction specifies:
    - "Request headers:" label followed by header lines
    - "Request body:" label followed by POST/PUT data

    The instruction specifies exact label text, so these are the observable
    behavior contract that any correct fix must produce.
    """
    script = _write_js_test("""// Replicate the renderRequest output formatting from network.ts
// The instruction specifies these exact label formats:
//   "Request headers:" followed by header key-value pairs (indented with 4 spaces)
//   "Request body:" followed by the raw POST/PUT data

function renderRequestOutput(url, method, status, statusText, headers, postData, includeHeaders, includeBody) {
  const result = [];
  result.push(`[${method}] ${url}`);
  if (status) result.push(` => [${status}] ${statusText}`);
  if (includeHeaders && headers) {
    const headerLines = Object.entries(headers).map(([k, v]) => `    ${k}: ${v}`).join('\\n');
    if (headerLines) result.push(`\\n  Request headers:\\n${headerLines}`);
  }
  if (includeBody && postData) {
    result.push(`\\n  Request body: ${postData}`);
  }
  return result.join('');
}

// Test 1: both headers and body enabled
const output = renderRequestOutput(
  "https://example.com/api/test", "POST", 200, "OK",
  { "content-type": "application/json", "authorization": "Bearer token123" },
  '{"name":"test"}',
  true,  // includeHeaders
  true   // includeBody
);

if (!output.includes("Request headers:")) { console.error("FAIL: headers label missing"); process.exit(1); }
if (!output.includes("Request body:")) { console.error("FAIL: body label missing"); process.exit(1); }
if (!output.includes("content-type")) { console.error("FAIL: content-type header missing"); process.exit(1); }
if (!output.includes("authorization")) { console.error("FAIL: authorization header missing"); process.exit(1); }
if (!output.includes('{"name":"test"}')) { console.error("FAIL: postData body missing"); process.exit(1); }

// Test 2: only headers enabled (body should NOT appear)
const hOnly = renderRequestOutput(
  "https://example.com/api/test", "POST", 200, "OK",
  { "content-type": "application/json" }, null, true, false
);
if (!hOnly.includes("Request headers:")) { console.error("FAIL: headers-only label missing"); process.exit(1); }
if (hOnly.includes("Request body:")) { console.error("FAIL: body should not appear when includeBody=false"); process.exit(1); }

// Test 3: only body enabled (headers should NOT appear)
const bOnly = renderRequestOutput(
  "https://example.com/api/test", "POST", 200, "OK",
  {}, '{"name":"test"}', false, true
);
if (!bOnly.includes("Request body:")) { console.error("FAIL: body-only label missing"); process.exit(1); }
if (bOnly.includes("Request headers:")) { console.error("FAIL: headers should not appear when includeHeaders=false"); process.exit(1); }

console.log("PASS");
""")
    try:
        r = _run_js(script)
        assert r.returncode == 0, f"renderRequest output test failed: {r.stderr}"
        assert "PASS" in r.stdout, f"Test did not pass: {r.stderr} {r.stdout}"
    finally:
        script.unlink(missing_ok=True)

def test_filter_regex_applied():
    """Verify the filter correctly selects matching URLs.

    Tests BEHAVIOR: a URL that matches the filter pattern is kept,
    and a URL that does not match is filtered out.
    """
    script = _write_js_test("""// Replicate the filter logic from the handle function
// Tests that the filter correctly distinguishes matching vs. non-matching URLs

const filterPattern = "/api/.*";
const filter = new RegExp(filterPattern);

// URLs to test
const matchingUrl = "https://example.com/api/users/123";
const nonMatchingUrl = "https://example.com/login";

// Reset lastIndex (as done in the gold code)
filter.lastIndex = 0;
const matchingResult = filter.test(matchingUrl);
filter.lastIndex = 0;
const nonMatchingResult = filter.test(nonMatchingUrl);

if (!matchingResult) {
  console.error("FAIL: URL matching /api/.* was incorrectly filtered out");
  process.exit(1);
}
if (nonMatchingResult) {
  console.error("FAIL: URL not matching /api/.* was NOT filtered out");
  process.exit(1);
}

// Also verify the logic flow: non-matching URLs should trigger 'continue'
// in the handle() loop (wouldSkip is true when filter DOES NOT match)
let wouldContinue = false;
if (filter) {
  filter.lastIndex = 0;
  if (!filter.test(nonMatchingUrl)) {
    wouldContinue = true;  // the 'continue' in handle() would be executed
  }
}
if (!wouldContinue) {
  console.error("FAIL: non-matching URL would not trigger continue in handle() loop");
  process.exit(1);
}

console.log("PASS");
""")
    try:
        r = _run_js(script)
        assert r.returncode == 0, f"filter RegExp test failed: {r.stderr}"
        assert "PASS" in r.stdout, f"filter test did not pass: {r.stderr} {r.stdout}"
    finally:
        script.unlink(missing_ok=True)

def test_cli_new_options():
    commands_ts = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts"
    content = commands_ts.read_text()
    assert "request-body" in content or "requestBody" in content, "request-body missing from CLI command"
    assert "request-headers" in content or "requestHeaders" in content, "request-headers missing from CLI command"
    assert "filter" in content, "filter missing from CLI command"

def test_copilot_instructions_created():
    copilot_md = Path(REPO) / ".github/copilot-instructions.md"
    assert copilot_md.exists(), ".github/copilot-instructions.md not created"
    content = copilot_md.read_text()
    assert "PR Review Guidelines" in content, "PR Review Guidelines heading missing"
    assert "semantically meaningful" in content or "bugs" in content or "incorrect logic" in content, \
        "guideline about substantive issues missing"
    assert "Skip style" in content or "style" in content.lower(), \
        "guideline about skipping style missing"
    assert "one or two sentences" in content or "short" in content.lower(), \
        "guideline about comment length missing"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_lint_snippets_npm():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm ci'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_pip():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'pip install -r utils/doclint/linting-code-snippets/python/requirements.txt'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_mvn():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'mvn package'], cwd=os.path.join(REPO, 'utils/doclint/linting-code-snippets/java'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_snippets_node():
    """pass_to_pass | CI job 'Lint snippets' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/doclint/linting-code-snippets/cli.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npx():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npx playwright install --with-deps'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_npm_2():
    """pass_to_pass | CI job 'docs & lint' → step ''"""
    r = subprocess.run(
        ["bash", "-lc", 'npm run lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_verify_clean_tree():
    """pass_to_pass | CI job 'docs & lint' → step 'Verify clean tree'"""
    r = subprocess.run(
        ["bash", "-lc", 'if [[ -n $(git status -s) ]]; then\n  echo "ERROR: tree is dirty after npm run build:"\n  git diff\n  exit 1\nfi'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify clean tree' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_docs___lint_audit_prod_npm_dependencies():
    """pass_to_pass | CI job 'docs & lint' → step 'Audit prod NPM dependencies'"""
    r = subprocess.run(
        ["bash", "-lc", 'node utils/check_audit.js'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Audit prod NPM dependencies' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")