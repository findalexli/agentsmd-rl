"""Tests for workers-sdk local explorer agent prompt feature."""

import subprocess
import os
import sys

REPO = "/workspace/workers-sdk"


def _run_ts(code: str) -> subprocess.CompletedProcess:
    """Run TypeScript code via tsx in the repo directory."""
    return subprocess.run(
        ["tsx", "-e", code],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO,
    )


def test_module_exports_get_local_explorer_api_endpoint():
    """The agent-prompt module exports getLocalExplorerApiEndpoint."""
    code = """
import { getLocalExplorerApiEndpoint } from "./packages/local-explorer-ui/src/utils/agent-prompt";
if (typeof getLocalExplorerApiEndpoint !== "function") throw new Error("not a function");
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_module_exports_create_local_explorer_prompt():
    """The agent-prompt module exports createLocalExplorerPrompt."""
    code = """
import { createLocalExplorerPrompt } from "./packages/local-explorer-ui/src/utils/agent-prompt";
if (typeof createLocalExplorerPrompt !== "function") throw new Error("not a function");
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_module_exports_copy_text_to_clipboard():
    """The agent-prompt module exports copyTextToClipboard."""
    code = """
import { copyTextToClipboard } from "./packages/local-explorer-ui/src/utils/agent-prompt";
if (typeof copyTextToClipboard !== "function") throw new Error("not a function");
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_get_local_explorer_api_endpoint_joins_origin_and_path():
    """getLocalExplorerApiEndpoint concatenates origin and apiPath."""
    code = """
import { getLocalExplorerApiEndpoint } from "./packages/local-explorer-ui/src/utils/agent-prompt";
const r1 = getLocalExplorerApiEndpoint("http://localhost:8787", "/cdn-cgi/explorer/api");
if (r1 !== "http://localhost:8787/cdn-cgi/explorer/api") throw new Error("got: " + r1);
const r2 = getLocalExplorerApiEndpoint("https://example.com", "/v1/data");
if (r2 !== "https://example.com/v1/data") throw new Error("got: " + r2);
const r3 = getLocalExplorerApiEndpoint("http://0.0.0.0:3000", "/api/explorer");
if (r3 !== "http://0.0.0.0:3000/api/explorer") throw new Error("got: " + r3);
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_create_local_explorer_prompt_fills_template():
    """createLocalExplorerPrompt injects the API endpoint into the template."""
    code = """
import { createLocalExplorerPrompt } from "./packages/local-explorer-ui/src/utils/agent-prompt";
const prompt = createLocalExplorerPrompt("http://test.local:9999/api");
if (!prompt.includes("API endpoint: http://test.local:9999/api")) throw new Error("missing endpoint in:\\n" + prompt);
if (!prompt.includes("Fetch the OpenAPI schema from http://test.local:9999/api")) throw new Error("missing fetch instruction in:\\n" + prompt);
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_create_local_explorer_prompt_includes_service_list():
    """The prompt template mentions all expected Cloudflare services."""
    code = """
import { createLocalExplorerPrompt } from "./packages/local-explorer-ui/src/utils/agent-prompt";
const prompt = createLocalExplorerPrompt("http://x:1/a");
if (!prompt.includes("KV, R2, D1, Durable Objects, and Workflows")) throw new Error("missing service list in:\\n" + prompt);
if (!prompt.includes("OpenAPI schema")) throw new Error("missing OpenAPI schema mention in:\\n" + prompt);
if (!prompt.includes("Explorer API")) throw new Error("missing Explorer API mention in:\\n" + prompt);
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_copy_text_to_clipboard_calls_write_text():
    """copyTextToClipboard calls the provided clipboard's writeText method."""
    code = """
import { copyTextToClipboard } from "./packages/local-explorer-ui/src/utils/agent-prompt";

(async () => {
    let called = false;
    let calledText = null;
    const mockClipboard = {
        writeText: (text) => { called = true; calledText = text; return Promise.resolve(); }
    };

    await copyTextToClipboard("hello world", mockClipboard);
    if (!called) throw new Error("writeText was not called");
    if (calledText !== "hello world") throw new Error("writeText called with: " + calledText);

    // Test with different text
    called = false; calledText = null;
    await copyTextToClipboard("another prompt text", mockClipboard);
    if (!called) throw new Error("writeText was not called (2nd call)");
    if (calledText !== "another prompt text") throw new Error("writeText called with: " + calledText);

    console.log("OK");
})();
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_template_has_no_placeholder_residue():
    """createLocalExplorerPrompt replaces all {{apiEndpoint}} placeholders."""
    code = """
import { createLocalExplorerPrompt } from "./packages/local-explorer-ui/src/utils/agent-prompt";
const prompt = createLocalExplorerPrompt("http://x:1/a");
if (prompt.includes("{{apiEndpoint}}")) throw new Error("unreplaced placeholder found in:\\n" + prompt);
console.log("OK");
"""
    r = _run_ts(code)
    assert r.returncode == 0, f"FAIL: {r.stderr}"


def test_repo_directory_structure_intact():
    """Base repo has expected directory structure (pass_to_pass)."""
    assert os.path.isdir(os.path.join(REPO, "packages", "local-explorer-ui", "src"))
    assert os.path.isfile(os.path.join(REPO, "packages", "local-explorer-ui", "package.json"))
    assert os.path.isfile(os.path.join(REPO, "packages", "local-explorer-ui", "vitest.config.mts"))


def test_index_tsx_integrates_agent_prompt():
    """Homepage route imports agent-prompt utilities and renders prompt card."""
    path = os.path.join(REPO, "packages", "local-explorer-ui", "src", "routes", "index.tsx")
    with open(path) as f:
        content = f.read()
    assert "agent-prompt" in content, "index.tsx must import from agent-prompt module"
    assert "useLoaderData" in content, "index.tsx must use loader data for prompt"
    assert "Copy prompt for agent" in content, "index.tsx must render the prompt card"


def test_package_json_has_kumo_version_bump():
    """package.json has @cloudflare/kumo updated to ^1.18.0."""
    import json
    path = os.path.join(REPO, "packages", "local-explorer-ui", "package.json")
    with open(path) as f:
        pkg = json.load(f)
    assert pkg["dependencies"]["@cloudflare/kumo"] == "^1.18.0", \
        f"Expected ^1.18.0, got {pkg['dependencies']['@cloudflare/kumo']}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build():
    """pass_to_pass | CI job 'build' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build --filter="./packages/*"'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_upload_packages():
    """pass_to_pass | CI job 'build' → step 'Upload packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register .github/prereleases/upload.mjs'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Upload packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_cleanup_test_projects_cleanup_e2e_test_projects():
    """pass_to_pass | CI job 'Cleanup Test Projects' → step 'Cleanup E2E test projects'"""
    r = subprocess.run(
        ["bash", "-lc", 'node -r esbuild-register tools/e2e/e2eCleanup.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Cleanup E2E test projects' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_builds_api_endpoint_from_origin_and_api_path():
    """fail_to_pass | PR added test 'builds api endpoint from origin and api path' in 'packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "builds api endpoint from origin and api path" 2>&1 || npx vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "builds api endpoint from origin and api path" 2>&1 || pnpm jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "builds api endpoint from origin and api path" 2>&1 || npx jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "builds api endpoint from origin and api path" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'builds api endpoint from origin and api path' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_generates_prompt_text_with_resolved_api_endpoint():
    """fail_to_pass | PR added test 'generates prompt text with resolved api endpoint' in 'packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "generates prompt text with resolved api endpoint" 2>&1 || npx vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "generates prompt text with resolved api endpoint" 2>&1 || pnpm jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "generates prompt text with resolved api endpoint" 2>&1 || npx jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "generates prompt text with resolved api endpoint" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'generates prompt text with resolved api endpoint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_copies_prompt_text_to_clipboard():
    """fail_to_pass | PR added test 'copies prompt text to clipboard' in 'packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "copies prompt text to clipboard" 2>&1 || npx vitest run "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "copies prompt text to clipboard" 2>&1 || pnpm jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "copies prompt text to clipboard" 2>&1 || npx jest "packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts" -t "copies prompt text to clipboard" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'copies prompt text to clipboard' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
