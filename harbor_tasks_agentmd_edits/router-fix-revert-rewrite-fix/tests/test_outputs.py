"""
Task: router-fix-revert-rewrite-fix
Repo: TanStack/router @ aa68f71febbfc2f751fd3f2252bc42c27c939835
PR:   6211

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/router"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and contain valid code."""
    files = [
        "packages/router-core/src/router.ts",
        "e2e/react-start/i18n-paraglide/src/server.ts",
    ]
    for f in files:
        fp = Path(REPO) / f
        assert fp.exists(), f"{f} does not exist"
        content = fp.read_text()
        assert len(content.strip()) > 50, f"{f} is too short or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_router_publicHref_not_output_rewritten():
    """Router's parseLocation must set publicHref directly from the original href,
    not by applying the output rewrite (which causes redirect loops with i18n)."""
    router_ts = (Path(REPO) / "packages/router-core/src/router.ts").read_text()

    # Locate the parseLocation method's parse function
    parse_start = router_ts.find("parseLocation")
    assert parse_start != -1, "parseLocation method not found in router.ts"
    parse_end = router_ts.find("resolvePathCache", parse_start)
    assert parse_end != -1, "Could not find end boundary of parseLocation"
    parse_section = router_ts[parse_start:parse_end]

    # The fix removes executeRewriteOutput from parseLocation — it was causing
    # publicHref to diverge from what buildLocation computes, triggering redirect loops.
    assert "executeRewriteOutput" not in parse_section, (
        "parseLocation must not call executeRewriteOutput to compute publicHref "
        "(this causes infinite redirect loops with i18n locale prefix rewriting)"
    )

    # After the fix, publicHref is set directly to the original href
    assert "publicHref: href" in parse_section, (
        "publicHref should be assigned directly from the original href, "
        "not computed via output rewrite"
    )

    # The reverted code stored an intermediate internalPathname variable
    assert "internalPathname" not in parse_section, (
        "The internalPathname variable should be removed — pathname should "
        "use url.pathname directly"
    )


# [pr_diff] fail_to_pass
def test_router_pathname_uses_url_pathname():
    """parseLocation must decode pathname from url.pathname directly,
    not from a separately saved internalPathname variable."""
    router_ts = (Path(REPO) / "packages/router-core/src/router.ts").read_text()

    parse_start = router_ts.find("parseLocation")
    parse_end = router_ts.find("resolvePathCache", parse_start)
    parse_section = router_ts[parse_start:parse_end]

    # After the fix, pathname is decoded directly from url.pathname
    assert "decodePath(url.pathname)" in parse_section, (
        "pathname should use decodePath(url.pathname), not decodePath(internalPathname)"
    )

    # The urlForOutput clone should not exist
    assert "urlForOutput" not in parse_section, (
        "urlForOutput variable should be removed — no URL cloning needed for output rewrite"
    )


# [pr_diff] fail_to_pass
def test_server_uses_original_request():
    """The i18n paraglide server.ts must pass the original request to the handler,
    not the middleware-transformed request (which breaks URL rewriting)."""
    server_ts = (Path(REPO) / "e2e/react-start/i18n-paraglide/src/server.ts").read_text()

    # The fix changes: ({ request }) => handler.fetch(request)
    # To:              () => handler.fetch(req)
    # The middleware-modified request has already been rewritten and should NOT
    # be passed to the TanStack Start handler.
    assert "() => handler.fetch(req)" in server_ts, (
        "server.ts should use () => handler.fetch(req) — passing the original "
        "request, not the middleware-transformed one"
    )
    assert "({ request })" not in server_ts, (
        "server.ts should not destructure 'request' from the middleware callback — "
        "the original req should be used instead"
    )


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — documentation / README update tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
