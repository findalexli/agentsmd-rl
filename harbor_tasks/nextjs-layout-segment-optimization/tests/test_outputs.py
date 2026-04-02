"""
Task: nextjs-layout-segment-optimization
Repo: vercel/next.js @ 883d93c8935afb2b8124ab324a10fa36cbd7a88c
PR:   91701

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = Path("/workspace/next.js")

APP_PAGE = REPO / "packages/next/src/build/templates/app-page.ts"
LOADER_TREE = REPO / "crates/next-core/src/app_page_loader_tree.rs"
APP_RS = REPO / "crates/next-api/src/app.rs"
CHUNK_GROUP = REPO / "turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_app_page_server_imports_have_transition():
    """Server-side imports in app-page.ts must have next-server-utility transition."""
    src = APP_PAGE.read_text()

    # Import paths that the PR annotates with the transition.
    # Each is a substring of the from-specifier that uniquely identifies the import.
    required_paths = [
        "server/instrumentation/utils",
        "server/lib/trace/tracer",
        "server/request-meta",
        "server/lib/trace/constants",
        "server/app-render/interop-default",
        "server/app-render/strip-flight-headers",
        "server/base-http/node",
        "server/lib/experimental/ppr",
        "server/request/fallback-params",
        "server/app-render/manifests-singleton",
        "server/lib/streaming-metadata",
        "shared/lib/router/utils/app-paths",
        "server/lib/server-action-request-meta",
        "client/components/app-router-headers",
        "shared/lib/router/utils/is-bot",
        "server/response-cache",
        "lib/fallback",
        "server/render-result",
        "lib/constants",
        "server/stream-utils/encoded-tags",
        "server/stream-utils/node-web-streams-helper",
        "server/send-payload",
        "shared/lib/no-fallback-error",
        "shared/lib/size-limit",
        "server/lib/postponed-request-body",
        "lib/url",
        "client/components/redirect-status-code",
        "shared/lib/invariant-error",
        "lib/scheduler",
        "shared/lib/router/utils/interception-routes",
        "shared/lib/router/utils/get-segment-param",
    ]

    # Split the source into logical import statements.  An import may span
    # multiple lines (e.g. when destructured), so we join continuation lines.
    # Strategy: find every `from '...'` (or `from "..."`) and the optional
    # `with { ... }` that follows it on the same or next line.
    #
    # We match: from '<specifier>' [with { <attrs> }]
    from_pattern = re.compile(
        r"""from\s+['"]([^'"]+)['"]"""           # group 1 = specifier
        r"""(?:\s+with\s*\{([^}]*)\})?""",        # group 2 = with-clause (optional)
        re.DOTALL,
    )

    # Build a map: normalised specifier fragment -> has transition?
    spec_has_transition: dict[str, bool] = {}
    for m in from_pattern.finditer(src):
        specifier = m.group(1)
        with_clause = m.group(2) or ""
        has_t = "next-server-utility" in with_clause
        for frag in required_paths:
            if frag in specifier:
                # Keep the *last* match (handles re-exports after imports)
                spec_has_transition[frag] = has_t

    missing = [p for p in required_paths if not spec_has_transition.get(p, False)]
    # Allow up to 3 misses (some imports may have been refactored)
    assert len(missing) <= 3, (
        f"{len(missing)}/{ len(required_paths)} server imports missing "
        f"'next-server-utility' transition:\n  " + "\n  ".join(missing[:8])
    )


# [pr_diff] fail_to_pass
def test_fillmetadata_transition_removed():
    """fillMetadataSegment import string must NOT have next-server-utility transition."""
    src = LOADER_TREE.read_text()
    assert "fillMetadataSegment" in src, "fillMetadataSegment not found in file"

    # The import lives in a Rust string literal (rcstr! macro).
    # Find every string literal that mentions fillMetadataSegment.
    # Pattern: quoted strings (possibly multi-line via Rust raw strings or \ continuations).
    # We look for content between balanced quotes near fillMetadataSegment.
    idx = src.index("fillMetadataSegment")
    # Grab a generous window around it (the string spans ~2 lines)
    window = src[max(0, idx - 300) : idx + 300]

    # Within this window, the buggy version has `next-server-utility` as part of
    # the same string literal.  The fix removes it entirely from this context.
    # Check that the keyword does NOT appear near fillMetadataSegment.
    lines = window.splitlines()
    fill_lines = [
        i for i, l in enumerate(lines) if "fillMetadataSegment" in l
    ]
    assert fill_lines, "Could not locate fillMetadataSegment line"

    # Check a ±3-line neighbourhood around fillMetadataSegment
    centre = fill_lines[0]
    neighbourhood = "\n".join(lines[max(0, centre - 3) : centre + 4])
    assert "next-server-utility" not in neighbourhood, (
        "fillMetadataSegment import still contains next-server-utility transition"
    )


# [pr_diff] fail_to_pass
def test_app_module_graphs_option_param():
    """app_module_graphs must use Option<Vc<EvaluatableAssets>> instead of two params."""
    src = APP_RS.read_text()

    # Find the function signature (may be multi-line)
    fn_pat = re.compile(
        r"fn\s+app_module_graphs\s*\((.*?)\)\s*(?:->|\{)",
        re.DOTALL,
    )
    fn_match = fn_pat.search(src)
    assert fn_match, "app_module_graphs function not found"

    sig = fn_match.group(1)

    # Old pattern MUST be gone: a standalone `has_layout_segments: bool` param
    assert "has_layout_segments: bool" not in sig, (
        "app_module_graphs still has has_layout_segments: bool parameter"
    )

    # New pattern: Option wrapping the client_shared_entries
    assert "Option<" in sig, (
        "app_module_graphs signature does not use an Option parameter"
    )


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group_entry():
    """SharedMultiple variant must exist in ChunkGroupEntry enum."""
    src = CHUNK_GROUP.read_text()
    enum_match = re.search(
        r"pub\s+enum\s+ChunkGroupEntry\s*\{(.*?)\n\}",
        src, re.DOTALL,
    )
    assert enum_match, "ChunkGroupEntry enum not found"
    assert "SharedMultiple" in enum_match.group(1), (
        "SharedMultiple variant missing from ChunkGroupEntry"
    )


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group():
    """SharedMultiple variant must exist in ChunkGroup enum."""
    src = CHUNK_GROUP.read_text()
    enum_match = re.search(
        r"pub\s+enum\s+ChunkGroup\s*\{(.*?)\n\}",
        src, re.DOTALL,
    )
    assert enum_match, "ChunkGroup enum not found"
    assert "SharedMultiple" in enum_match.group(1), (
        "SharedMultiple variant missing from ChunkGroup"
    )


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group_key():
    """SharedMultiple variant must exist in ChunkGroupKey enum."""
    src = CHUNK_GROUP.read_text()
    enum_match = re.search(
        r"pub\s+enum\s+ChunkGroupKey\s*\{(.*?)\n\}",
        src, re.DOTALL,
    )
    assert enum_match, "ChunkGroupKey enum not found"
    assert "SharedMultiple" in enum_match.group(1), (
        "SharedMultiple variant missing from ChunkGroupKey"
    )


# [pr_diff] fail_to_pass
def test_shared_multiple_pattern_matching():
    """SharedMultiple must be handled in match arms, not just declared in enums."""
    src = CHUNK_GROUP.read_text()

    # Count references like Self::SharedMultiple, ChunkGroup::SharedMultiple, etc.
    # Enum definitions contribute ~3 hits; match arms contribute more.
    refs = re.findall(
        r"(?:Self|ChunkGroup|ChunkGroupEntry|ChunkGroupKey)::SharedMultiple",
        src,
    )
    # Gold patch has ~11 references (3 enum defs + 8 match uses).
    # Require at least 6 to ensure it is integrated in pattern matches.
    assert len(refs) >= 6, (
        f"SharedMultiple referenced only {len(refs)} times — "
        "expected integration in pattern-match arms (entries, count, debug_str, etc.)"
    )


# [pr_diff] fail_to_pass
def test_route_handlers_no_empty_assets():
    """Route handlers must not pass EvaluatableAssets::empty() to app_module_graphs."""
    src = APP_RS.read_text()

    # Find all call-sites of app_module_graphs
    call_sites = list(re.finditer(r"app_module_graphs\s*\(", src))
    assert call_sites, "No calls to app_module_graphs found"

    for call in call_sites:
        # Grab the argument list (up to closing paren or 600 chars)
        start = call.end()
        region = src[start : start + 600]
        assert "EvaluatableAssets::empty()" not in region, (
            "app_module_graphs call still passes EvaluatableAssets::empty() — "
            "route handlers should pass None instead"
        )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — guard rails from repo config files
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:407, .agents/skills/dce-edge/SKILL.md:54
def test_no_relative_require_in_app_page():
    """app-page.ts must not use require() with relative paths (use entry-base.ts exports)."""
    src = APP_PAGE.read_text()

    # Match require('./...' or require('../...'
    relative_requires = re.findall(r"""\brequire\s*\(\s*['"]\.\.?/""", src)
    assert len(relative_requires) == 0, (
        f"app-page.ts has {len(relative_requires)} relative require() call(s) — "
        "internal modules must be exported from entry-base.ts and accessed via entryBase.*"
    )


# [agent_config] pass_to_pass — AGENTS.md:398, .agents/skills/react-vendoring/SKILL.md:25
def test_no_react_server_dom_webpack_in_app_page():
    """app-page.ts must not directly import from react-server-dom-webpack/*."""
    src = APP_PAGE.read_text()

    # All react-server-dom-webpack imports must go through entry-base.ts
    direct_imports = re.findall(
        r"""(?:import|from)\s+['"]react-server-dom-webpack/""", src
    )
    assert len(direct_imports) == 0, (
        f"app-page.ts has {len(direct_imports)} direct react-server-dom-webpack import(s) — "
        "these must stay in entry-base.ts; consume via component module exports"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub / regression
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_modified_files_exist():
    """All four modified files must exist with substantial content."""
    checks = [
        (APP_PAGE, 80),
        (LOADER_TREE, 100),
        (APP_RS, 400),
        (CHUNK_GROUP, 150),
    ]
    for path, min_lines in checks:
        assert path.exists(), f"{path} does not exist"
        n = len(path.read_text().splitlines())
        assert n >= min_lines, f"{path.name} has {n} lines, expected >= {min_lines}"


# [static] pass_to_pass
def test_existing_transitions_preserved():
    """Pre-existing transition annotations (RouteKind, entry-base) must survive."""
    src = APP_PAGE.read_text()
    # RouteKind import already had the transition before this PR
    assert re.search(
        r"from\s+['\"].*route-kind['\"].*with\s*\{[^}]*next-server-utility",
        src, re.DOTALL,
    ), "RouteKind import lost its next-server-utility transition"
    # entry-base re-export
    assert re.search(
        r"(?:import|export)\s+.*entry-base.*with\s*\{[^}]*next-server-utility",
        src, re.DOTALL,
    ), "entry-base import/export lost its next-server-utility transition"
