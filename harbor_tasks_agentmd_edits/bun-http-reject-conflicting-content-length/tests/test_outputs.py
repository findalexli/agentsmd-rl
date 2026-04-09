"""
Task: bun-http-reject-conflicting-content-length
Repo: oven-sh/bun @ 5b3ca83b84f90ccc9c71005db0ab9bd87850bc70
PR:   28838

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
from pathlib import Path

REPO = "/workspace/bun"
HTTP_PARSER = f"{REPO}/packages/bun-uws/src/HttpParser.h"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_http_parser_validates_duplicate_content_length():
    """HttpParser must validate all Content-Length headers, not just the first."""
    src = Path(HTTP_PARSER).read_text()
    # The fix adds a loop that iterates all headers checking for duplicate
    # Content-Length entries and rejecting conflicting values.
    assert 'strncmp(h->key.data(), "content-length", 14)' in src, \
        "HttpParser must iterate headers to find all Content-Length entries"
    assert "strncmp(h->value.data(), contentLengthString.data()" in src, \
        "HttpParser must compare duplicate Content-Length values byte-for-byte"
    assert "HTTP_PARSER_ERROR_INVALID_CONTENT_LENGTH" in src, \
        "HttpParser must return error for conflicting Content-Length values"


def test_http_parser_rejects_empty_content_length():
    """Empty Content-Length values must be rejected to prevent smuggling bypass."""
    src = Path(HTTP_PARSER).read_text()
    # The fix must check for empty Content-Length as the first value
    assert "h->value.length() == 0" in src, \
        "HttpParser must check for empty Content-Length values"
    # The empty check must be within the first-occurrence detection block
    assert "contentLengthString.data() == nullptr" in src, \
        "Empty value check must be within the first-occurrence detection logic"


def test_pr_comments_script_parses():
    """pr-comments.ts must exist and be valid TypeScript that bun can transpile."""
    script = Path(f"{REPO}/scripts/pr-comments.ts")
    assert script.exists(), "scripts/pr-comments.ts must exist"

    os.makedirs("/tmp/_bun_check", exist_ok=True)
    result = subprocess.run(
        ["bun", "build", "--target=bun", "scripts/pr-comments.ts",
         "--outdir", "/tmp/_bun_check"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, \
        f"pr-comments.ts failed to transpile: {result.stderr}"


def test_claude_md_documents_pr_comments():
    """CLAUDE.md must document the pr:comments script with usage examples."""
    claude_md = Path(f"{REPO}/CLAUDE.md").read_text()
    assert "pr:comments" in claude_md, \
        "CLAUDE.md must reference the pr:comments script"
    assert "bun run pr:comments" in claude_md, \
        "CLAUDE.md must show how to run pr:comments"
    assert "gh pr view" in claude_md, \
        "CLAUDE.md must explain why pr:comments is needed vs gh pr view --comments"


def test_package_json_has_pr_comments():
    """package.json must include the pr:comments script entry."""
    package_json = Path(f"{REPO}/package.json").read_text()
    assert "pr:comments" in package_json, \
        "package.json must have pr:comments script entry"
    assert "pr-comments.ts" in package_json, \
        "pr:comments script must point to pr-comments.ts"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_http_parser_content_length_parsing_preserved():
    """Basic Content-Length parsing must still be intact after the fix."""
    src = Path(HTTP_PARSER).read_text()
    assert "contentLengthString" in src, \
        "Content-Length string variable must still exist"
    assert "transfer-encoding" in src.lower(), \
        "Transfer-Encoding handling must be preserved"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD checks from the repo
# ---------------------------------------------------------------------------


def test_repo_lint():
    """Repo's JavaScript linting passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-500:]}"


def test_repo_ban_words():
    """Banned words check passes (pass_to_pass)."""
    r = subprocess.run(
        ["bun", "./test/internal/ban-words.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Ban words check failed:\n{r.stderr[-500:]}"


def test_repo_bun_types():
    """Bun types TypeScript check passes (pass_to_pass)."""
    # Install root deps first (typescript is a devDependency at root)
    r = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"bun install failed: {r.stderr[-500:]}"
    # Run tsc --noEmit from repo root pointing to bun-types tsconfig
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "packages/bun-types/tsconfig.json"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Bun types check failed:\n{r.stderr[-500:]}"
