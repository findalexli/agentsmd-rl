"""
Task: next.js-fixpagesrouter-restore-contentlength-and-etag
Repo: vercel/next.js @ fb85660ab1f70e294465af0074dc7c941e3540ca
PR:   90304

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
HANDLER = Path(REPO) / "packages/next/src/server/route-modules/pages/pages-handler.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """pages-handler.ts has balanced braces (basic TS syntax sanity)."""
    src = HANDLER.read_text()
    assert src.count("{") == src.count("}"), "Unbalanced curly braces in pages-handler.ts"
    assert src.count("(") == src.count(")"), "Unbalanced parentheses in pages-handler.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_data_response_no_buffer_wrap():
    """/_next/data/ JSON response must pass string to RenderResult, not Buffer.

    Buffer.from() causes RenderResult.isDynamic to return true (response is not
    a string), which makes sendRenderResult skip Content-Length and ETag headers.
    """
    src = HANDLER.read_text()
    assert "Buffer.from(JSON.stringify(result.value.pageData))" not in src, \
        "Data response wraps JSON.stringify with Buffer.from() — breaks Content-Length/ETag"
    # The JSON.stringify call itself must still be present
    assert "JSON.stringify(result.value.pageData)" in src, \
        "Data response must still use JSON.stringify for pageData serialization"


# [pr_diff] fail_to_pass

    Same root cause: Buffer.from(previousCacheEntry.value.html) produces a
    non-string, making the response appear dynamic.
    """
    src = HANDLER.read_text()
    assert "Buffer.from(previousCacheEntry.value.html)" not in src, \
        "ISR fallback wraps html with Buffer.from() — breaks Content-Length/ETag"
    assert "previousCacheEntry.value.html" in src, \
        "ISR fallback must still reference previousCacheEntry.value.html"


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — AGENTS.md documentation fixes
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass — AGENTS.md:151-157 @ 962e5b166cea3fdb6589837a8fd3ea62031be17d

    The -- is required to forward args through pnpm to the underlying script.
    Without it, pnpm swallows the --args flag.
    """
    content = (Path(REPO) / "AGENTS.md").read_text()
    assert "pnpm new-test -- --args" in content, \
        "AGENTS.md should use 'pnpm new-test -- --args' to forward args correctly"


# [config_edit] fail_to_pass — AGENTS.md:148-157,403 @ 962e5b166cea3fdb6589837a8fd3ea62031be17d

    Base commit has 3 occurrences of 'pnpm new-test --args' (missing --).
    All must be fixed to 'pnpm new-test -- --args'.
    """
    content = (Path(REPO) / "AGENTS.md").read_text()
    # Match 'pnpm new-test' followed directly by '--args' (no '--' separator)
    broken = re.findall(r"pnpm new-test\s+--args", content)
    assert len(broken) == 0, \
        f"Found {len(broken)} 'pnpm new-test --args' without -- separator"
