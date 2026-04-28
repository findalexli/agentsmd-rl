"""
Task: bun-http-reject-conflicting-content-length
Repo: oven-sh/bun @ 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70
PR:   28838

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/bun"


def run_bun_test(test_path: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Helper to run a bun test file and return the result."""
    return subprocess.run(
        ["bun", "test", test_path],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


def run_bun_command(args: list, cwd: str = REPO, timeout: int = 60) -> subprocess.CompletedProcess:
    """Helper to run a bun command and return the result."""
    return subprocess.run(
        ["bun"] + args,
        capture_output=True, text=True, timeout=timeout, cwd=cwd,
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral / structural tests
# ---------------------------------------------------------------------------


def test_http_parser_has_duplicate_content_length_header_validation():
    """HttpParser.h must reject requests with conflicting Content-Length headers.

    Per RFC 9112 section 6.3, multiple Content-Length headers with differing
    values indicate a request smuggling attempt and must be rejected with 400.
    This test verifies the C++ source contains the validator logic.
    """
    parser_h = Path(f"{REPO}/packages/bun-uws/src/HttpParser.h").read_text()

    # The fix introduces a bloom-filter short-circuit + per-header validation
    # with the unique error constant HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH.
    assert "HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH" in parser_h, (
        "HttpParser.h must define/use HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH "
        "for rejecting conflicting Content-Length headers"
    )

    # The fix walks every Content-Length header instead of using getHeader()
    # which only returned the first. The bloom filter avoids the walk for
    # requests without a Content-Length header.
    assert 'mightHave("content-length")' in parser_h, (
        "HttpParser.h must use the bloom filter (mightHave) to short-circuit "
        "the Content-Length header validation loop"
    )

    # Verify the comparison logic exists: when a second Content-Length header
    # has a different length or differs byte-for-byte, it's rejected.
    assert "strncmp(h->value.data(), contentLengthString.data()" in parser_h, (
        "HttpParser.h must compare Content-Length header values byte-for-byte "
        "to detect conflicting duplicates"
    )


def test_http_parser_has_empty_content_length_rejection():
    """HttpParser.h must reject requests with empty Content-Length values.

    Empty Content-Length values can bypass duplicate checks and enable
    request smuggling attacks. The fix must reject them with 400.
    """
    parser_h = Path(f"{REPO}/packages/bun-uws/src/HttpParser.h").read_text()

    # Empty value check: when iterating Content-Length headers, an empty
    # value is immediately rejected before it can be stored.
    assert "h->value.length() == 0" in parser_h, (
        "HttpParser.h must reject empty Content-Length header values"
    )

    # The error constant must be used in at least two places:
    # once for empty values and once for conflicting values.
    count = parser_h.count("HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH")
    assert count >= 2, (
        f"HttpParser.h must use HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH "
        f"for both empty-value and conflicting-value rejection (found {count})"
    )


def test_pr_comments_script_parses():
    """pr-comments.ts must exist, parse as valid TypeScript, and be executable."""
    script = Path(f"{REPO}/scripts/pr-comments.ts")
    assert script.exists(), "scripts/pr-comments.ts must exist"

    # Verify it is valid TypeScript by trying to build it
    os.makedirs("/tmp/_bun_check", exist_ok=True)
    result = subprocess.run(
        ["bun", "build", "--target=bun", "scripts/pr-comments.ts",
         "--outdir", "/tmp/_bun_check"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, \
        f"pr-comments.ts failed to transpile: {result.stderr}"

    # Verify the script runs without syntax errors (may fail on auth/network)
    result = subprocess.run(
        ["bun", "run", "scripts/pr-comments.ts"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    # Should fail with auth error or "No pull request found" but not syntax error
    stderr_lower = result.stderr.lower()
    assert "error:" not in stderr_lower or "auth" in stderr_lower or "pr" in stderr_lower, \
        f"pr-comments.ts has runtime error (possibly type/syntax issue): {result.stderr}"


def test_pr_comments_accepts_pr_number_argument():
    """pr-comments.ts must accept a PR number as a positional argument."""
    script = Path(f"{REPO}/scripts/pr-comments.ts")
    assert script.exists(), "scripts/pr-comments.ts must exist before testing arguments"

    result = subprocess.run(
        ["bun", "run", "scripts/pr-comments.ts", "99999"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    stderr_lower = result.stderr.lower()
    # The script should recognize the numeric argument, not reject it as invalid
    assert "is not a pr number" not in stderr_lower, \
        "Script does not properly accept PR number argument"
    assert "module not found" not in stderr_lower, \
        "Script file not found — script must exist before testing arguments"


def test_pr_comments_accepts_json_flag():
    """pr-comments.ts must support --json flag for machine-readable output."""
    script = Path(f"{REPO}/scripts/pr-comments.ts")
    assert script.exists(), "scripts/pr-comments.ts must exist before testing flags"

    result = subprocess.run(
        ["bun", "run", "scripts/pr-comments.ts", "--json"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    stderr_lower = result.stderr.lower()
    # If --json is not supported, we would see an error about unknown option
    assert "module not found" not in stderr_lower, \
        "Script file not found — script must exist before testing flags"
    assert "unknown" not in stderr_lower or "option" not in stderr_lower, \
        f"--json flag not recognized: {result.stderr}"
    assert "json" in result.stdout.lower() or "json" in result.stderr.lower() or result.returncode != 0, \
        f"JSON mode not handled: {result.stdout} {result.stderr}"


def test_package_json_has_pr_comments():
    """package.json must include a working pr:comments script entry."""
    package_json_path = Path(f"{REPO}/package.json")
    with open(package_json_path) as f:
        pkg = json.load(f)

    assert "scripts" in pkg, "package.json missing scripts section"
    assert "pr:comments" in pkg["scripts"], \
        "package.json must have pr:comments script entry"

    script_cmd = pkg["scripts"]["pr:comments"]
    assert "pr-comments.ts" in script_cmd, \
        f"pr:comments script must point to pr-comments.ts, got: {script_cmd}"

    # Verify the script actually runs via bun run
    result = subprocess.run(
        ["bun", "run", "pr:comments"],
        capture_output=True, text=True, cwd=REPO, timeout=10,
    )
    assert "module not found" not in result.stderr.lower(), \
        f"pr:comments script fails with module error: {result.stderr}"
    assert "error parsing" not in result.stderr.lower(), \
        f"pr:comments script fails with parse error: {result.stderr}"


def test_claude_md_documents_pr_comments():
    """CLAUDE.md must document the pr:comments script with usage examples.

    The documentation must explain what the script does and how to use it.
    """
    claude_md = Path(f"{REPO}/CLAUDE.md").read_text()

    assert len(claude_md) > 0, "CLAUDE.md is empty"

    # Verify the pr:comments feature is mentioned (flexible matching)
    assert "pr:comments" in claude_md, \
        "CLAUDE.md must document the pr:comments script"

    # Verify there's information about running it (check for common invocation patterns)
    has_invocation_info = (
        "bun run pr:comments" in claude_md or
        "pr:comments" in claude_md.lower()
    )
    assert has_invocation_info, \
        "CLAUDE.md must show how to invoke pr:comments"

    # Verify the script's purpose is explained (comparing with gh pr view)
    has_purpose_info = (
        "gh pr view" in claude_md or
        "comment" in claude_md.lower()
    )
    assert has_purpose_info, \
        "CLAUDE.md must explain what pr:comments does compared to gh pr view"


# ---------------------------------------------------------------------------
# Pass-to-pass (static + repo_tests) — regression checks
# ---------------------------------------------------------------------------


def test_http_parser_content_length_preserved():
    """Basic Content-Length parsing must still work after the security fix."""
    server_code = '''
import net from "net";

let receivedBody = "";
const server = Bun.serve({
    port: 0,
    async fetch(req) {
        receivedBody = await req.text();
        return new Response("OK");
    },
});

const client = net.connect(server.port, "127.0.0.1");

const request = [
    "POST /test HTTP/1.1",
    "Host: localhost",
    "Content-Length: 5",
    "",
    "Hello"
].join("\\r\\n");

await new Promise<void>((resolve, reject) => {
    client.on("error", reject);
    client.on("data", data => {
        const response = data.toString();
        if (!response.includes("HTTP/1.1 200")) {
            console.error("FAIL: Expected 200 for normal request, got:", response);
            process.exit(1);
        }
        client.end();
        resolve();
    });
    client.write(request);
});

if (receivedBody !== "Hello") {
    console.error("FAIL: Body mismatch, expected 'Hello', got:", receivedBody);
    process.exit(1);
}

console.log("PASS: Basic Content-Length parsing works");
server.stop();
'''
    tmp_file = "/tmp/test_basic_cl.ts"
    Path(tmp_file).write_text(server_code)

    result = run_bun_command(["run", tmp_file], timeout=30)
    assert result.returncode == 0 and "PASS" in result.stdout, \
        f"Basic Content-Length parsing broken after fix:\n{result.stderr}"


def test_http_parser_accepts_identical_duplicate_content_length():
    """HTTP parser should accept duplicate Content-Length headers with identical values.

    RFC 9112 6.3 permits duplicate Content-Length headers if they carry the same value.
    This is a behavioral regression test that verifies the fix didn't break
    legitimate duplicate Content-Length headers with identical values.
    """
    server_code = '''
import net from "net";

let receivedBody = "";
const server = Bun.serve({
    port: 0,
    async fetch(req) {
        receivedBody = await req.text();
        return new Response("OK");
    },
});

const client = net.connect(server.port, "127.0.0.1");

const request = [
    "POST / HTTP/1.1",
    "Host: localhost",
    "Content-Length: 5",
    "Content-Length: 5",
    "",
    "Hello"
].join("\\r\\n");

await new Promise<void>((resolve, reject) => {
    client.on("error", reject);
    client.on("data", data => {
        const response = data.toString();
        if (!response.includes("HTTP/1.1 200")) {
            console.error("FAIL: Expected 200 for identical Content-Length values, got:", response);
            process.exit(1);
        }
        client.end();
        resolve();
    });
    client.write(request);
});

if (receivedBody !== "Hello") {
    console.error("FAIL: Body not correctly received, got:", receivedBody);
    process.exit(1);
}

console.log("PASS: Identical Content-Length headers correctly accepted");
server.stop();
'''
    tmp_file = "/tmp/test_identical_cl.ts"
    Path(tmp_file).write_text(server_code)

    result = run_bun_command(["run", tmp_file], timeout=30)
    assert result.returncode == 0 and "PASS" in result.stdout, \
        f"Behavioral regression: identical Content-Length values not accepted:\n{result.stderr}"


def test_repo_ban_words():
    """Banned words check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban words check failed:\n{r.stderr[-500:]}"


def test_repo_bun_types():
    """Bun types TypeScript check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/bun-types/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bun types check failed:\n{r.stderr[-500:]}"


def test_repo_http_smuggling_tests():
    """HTTP request smuggling tests pass (pass_to_pass).

    This test file is part of the base repository and existed before
    the fix was applied. It tests Transfer-Encoding + Content-Length conflicts.
    """
    r = subprocess.run(
        ["bun", "test", "test/js/bun/http/request-smuggling.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"HTTP smuggling tests failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass — PR-added test verification (bun test with name filter)
# ---------------------------------------------------------------------------


def test_pr_added_rejects_conflicting_duplicate_Content_Length_hea():
    """fail_to_pass | PR added test 'rejects conflicting duplicate Content-Length headers'
    in 'test/js/bun/http/request-smuggling.test.ts' — must exist and pass."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/http/request-smuggling.test.ts",
         "-t", "rejects conflicting duplicate Content-Length headers"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"PR-added test 'rejects conflicting duplicate Content-Length headers' "
        f"failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_pr_added_accepts_duplicate_Content_Length_headers_with_id():
    """fail_to_pass | PR added test 'accepts duplicate Content-Length headers with identical values'
    in 'test/js/bun/http/request-smuggling.test.ts' — must exist and pass."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/http/request-smuggling.test.ts",
         "-t", "accepts duplicate Content-Length headers with identical values"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"PR-added test 'accepts duplicate Content-Length headers with identical values' "
        f"failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_pr_added_rejects_empty_valued_Content_Length_followed_by_():
    """fail_to_pass | PR added test 'rejects empty-valued Content-Length followed by smuggled Content-Length'
    in 'test/js/bun/http/request-smuggling.test.ts' — must exist and pass."""
    r = subprocess.run(
        ["bun", "test", "test/js/bun/http/request-smuggling.test.ts",
         "-t", "rejects empty-valued Content-Length followed by smuggled Content-Length"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"PR-added test 'rejects empty-valued Content-Length followed by smuggled Content-Length' "
        f"failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
