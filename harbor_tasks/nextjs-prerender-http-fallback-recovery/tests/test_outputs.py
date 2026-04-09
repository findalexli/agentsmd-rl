"""
Task: nextjs-prerender-http-fallback-recovery
Repo: vercel/next.js @ e464ca398c5992c4ec9fb23192fc60ef7b1b5f94
PR:   92231

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

NOTE: app-render.tsx and create-component-tree.tsx are deep server-rendering
internals that cannot be imported or called outside the full Next.js build
pipeline. All checks use source analysis.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
APP_RENDER = f"{REPO}/packages/next/src/server/app-render/app-render.tsx"
COMPONENT_TREE = f"{REPO}/packages/next/src/server/app-render/create-component-tree.tsx"


def _strip_comments(src: str) -> str:
    """Remove single-line and multi-line comments to prevent gaming via comments."""
    src = re.sub(r"//.*$", "", src, flags=re.MULTILINE)
    src = re.sub(r"/\*[\s\S]*?\*/", "", src)
    return src


def _read_app_render() -> str:
    return _strip_comments(Path(APP_RENDER).read_text())


def _read_component_tree() -> str:
    return _strip_comments(Path(COMPONENT_TREE).read_text())


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified TypeScript files must have balanced braces."""
    for fpath in [APP_RENDER, COMPONENT_TREE]:
        src = Path(fpath).read_text()
        depth = 0
        for ch in src:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
            assert depth >= 0, f"Unbalanced braces in {fpath} (depth went negative)"
        assert depth == 0, f"Unbalanced braces in {fpath} (final depth={depth})"


# [static] pass_to_pass
def test_prettier_formatting():
    """Modified TypeScript files must pass Prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", APP_RENDER, COMPONENT_TREE],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\\n{r.stdout[-500:]}{r.stderr[-500:]}"


# [static] pass_to_pass
def test_error_codes_check():
    """Error codes must be valid (pass_to_pass)."""
    r = subprocess.run(
        ["node", "packages/next/check-error-codes.js"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Error codes check failed:\\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_http_error_boundary_status_code_mapping():
    """app-render.tsx must map HTTP status codes to their loader tree boundary slots.

    The fix requires logic that maps:
      404 -> 'not-found' boundary
      403 -> 'forbidden' boundary
      401 -> 'unauthorized' boundary
    This mapping must exist to find the correct fallback for each error type.
    """
    src = _read_app_render()

    # Must map all three status codes to their corresponding boundary slot names
    has_404_notfound = bool(
        re.search(r"404[\s\S]{0,200}not-found|not-found[\s\S]{0,200}404", src)
    )
    has_403_forbidden = bool(
        re.search(r"403[\s\S]{0,200}forbidden|forbidden[\s\S]{0,200}403", src)
    )
    has_401_unauthorized = bool(
        re.search(
            r"401[\s\S]{0,200}unauthorized|unauthorized[\s\S]{0,200}401", src
        )
    )

    assert has_404_notfound, (
        "No mapping from 404 to 'not-found' boundary slot in app-render.tsx"
    )
    assert has_403_forbidden, (
        "No mapping from 403 to 'forbidden' boundary slot in app-render.tsx"
    )
    assert has_401_unauthorized, (
        "No mapping from 401 to 'unauthorized' boundary slot in app-render.tsx"
    )


# [pr_diff] fail_to_pass
def test_deepest_boundary_tree_search():
    """app-render.tsx must find the DEEPEST matching boundary, not just the root.

    The fix recursively walks the loader tree's children slots to find the
    deepest segment that has a matching HTTP fallback boundary. This ensures
    the most specific boundary is used.
    """
    src = _read_app_render()

    # Must traverse children of the loader tree recursively
    # Look for a function or logic that:
    # 1. Accesses children of the loader tree (loaderTree[1].children or similar)
    # 2. Recurses or iterates deeper
    # 3. Prefers deeper matches over shallower ones

    # Pattern: accessing children slot AND recursion/deeper traversal
    has_children_access = bool(
        re.search(r"\w+\[1\]\.children|\w+\[1\]\[.children.\]", src)
        or re.search(r"childrenTree|children[Tt]ree", src)
    )

    # Must prefer deeper boundary (update boundaryTree when deeper match found)
    has_deeper_preference = bool(
        re.search(r"deeper|deepest|deep", src, re.IGNORECASE)
        or re.search(
            r"boundaryTree\s*=\s*\w*[Dd]eep|if\s*\(\s*\w*[Bb]oundary", src
        )
        # Also accept pattern where the function calls itself on children
        or re.search(
            r"find\w*[Bb]oundary\w*\(\s*children|find\w*[Bb]oundary\w*\(\s*child",
            src,
        )
    )

    assert has_children_access, (
        "No recursive traversal of loader tree children found — "
        "the fix must find the deepest matching boundary, not just root level"
    )
    assert has_deeper_preference, (
        "No logic to prefer deeper boundary matches — "
        "must recursively search and prefer the deepest matching boundary"
    )


# [pr_diff] fail_to_pass
def test_prerender_http_error_state_type_exported():
    """create-component-tree.tsx must export a type for prerender HTTP error state.

    The type must contain:
    - A reference to the boundary tree (LoaderTree)
    - The triggered HTTP status code (404/403/401)
    """
    src = _read_component_tree()

    # Must export a type with boundary tree and status code fields
    has_export = bool(
        re.search(
            r"export\s+type\s+\w*[Pp]rerender\w*[Hh][Tt][Tt][Pp]\w*[Ee]rror\w*State",
            src,
        )
        or re.search(
            r"export\s+type\s+\w*[Hh][Tt][Tt][Pp]\w*[Ee]rror\w*[Ss]tate", src
        )
        or re.search(
            r"export\s+(?:type|interface)\s+\w*[Pp]rerender\w*[Ff]allback\w*",
            src,
        )
    )

    has_boundary = bool(
        re.search(r"boundaryTree\s*:\s*LoaderTree|boundary\w*\s*:\s*LoaderTree", src)
    )
    has_status = bool(
        re.search(
            r"triggeredStatus\s*:|statusCode\s*:|status\s*:\s*\w*[Hh][Tt][Tt][Pp]",
            src,
        )
        or re.search(r"(?:404|403|401)\s*\|", src)
    )

    assert has_export, (
        "No exported type for prerender HTTP error state in create-component-tree.tsx"
    )
    assert has_boundary, (
        "Exported type must include a LoaderTree field for the boundary"
    )
    assert has_status, (
        "Exported type must include a status code field (404/403/401)"
    )


# [pr_diff] fail_to_pass
def test_recovery_branches_on_cache_components_http_error():
    """Prerender recovery must branch based on cacheComponents + HTTP access error.

    On the base commit, ALL prerender recovery errors go through
    getErrorRSCPayload. The fix must add a branch that, when cacheComponents
    is enabled and the error is an HTTP access fallback with a matching
    boundary, uses getRSCPayload with the scoped fallback info instead.
    """
    src = _read_app_render()

    # The recovery path must check for cacheComponents AND HTTP access error
    # and conditionally use getRSCPayload instead of getErrorRSCPayload
    has_cache_components_check = bool(
        re.search(r"cacheComponents\s*&&\s*\w*[Hh][Tt][Tt][Pp]", src)
        or re.search(r"cacheComponents[\s\S]{0,100}isHTTPAccessFallback", src)
        or re.search(r"cacheComponents[\s\S]{0,100}[Aa]ccess[Ff]allback", src)
    )

    # Must conditionally call getRSCPayload (not getErrorRSCPayload) when
    # a matching boundary exists
    has_conditional_rsc_payload = bool(
        re.search(
            r"prerenderHTTPError[\s\S]{0,300}getRSCPayload"
            r"|[Hh][Tt][Tt][Pp]\w*[Ee]rror[\s\S]{0,300}getRSCPayload",
            src,
        )
        or re.search(
            r"boundaryTree[\s\S]{0,500}getRSCPayload", src
        )
    )

    assert has_cache_components_check, (
        "Recovery path does not check for cacheComponents + HTTP access error — "
        "all errors still go through the generic error handling path"
    )
    assert has_conditional_rsc_payload, (
        "Recovery path does not conditionally use getRSCPayload with "
        "scoped fallback — must use getRSCPayload when boundary exists"
    )


# [pr_diff] fail_to_pass
def test_flight_stream_teed_for_prerender():
    """When using HTTP fallback recovery, the Flight stream must be teed.

    Both Fizz (for rendering the HTML) and the prerender buffer (for Flight
    data / segment data collection) need their own copy of the Flight stream.
    The fix must tee the stream so each consumer gets its own copy.
    """
    src = _read_app_render()

    # Must tee the stream — look for teeStream usage or manual ReadableStream tee
    has_tee = bool(
        re.search(r"teeStream\s*\(", src)
        or re.search(r"\.tee\s*\(", src)
    )

    # The tee must be connected to the error/HTTP fallback recovery path
    # (not just any tee anywhere in the file)
    has_tee_in_recovery = bool(
        re.search(
            r"prerenderHTTPError[\s\S]{0,1500}teeStream"
            r"|prerenderHTTPError[\s\S]{0,1500}\.tee\(",
            src,
        )
        or re.search(
            r"teeStream[\s\S]{0,1500}prerenderHTTPError", src
        )
        or re.search(
            r"errorServer\w*[\s\S]{0,500}teeStream"
            r"|errorServer\w*[\s\S]{0,500}\.tee\(",
            src,
        )
    )

    assert has_tee, (
        "No stream teeing found — both Fizz and prerender buffer need "
        "their own copy of the Flight stream"
    )
    assert has_tee_in_recovery, (
        "Stream teeing not connected to the HTTP fallback recovery path"
    )


# [pr_diff] fail_to_pass
def test_component_tree_renders_scoped_fallback():
    """create-component-tree.tsx must render the scoped fallback at the boundary.

    When the prerender HTTP error state indicates a boundary match at the
    current tree node and the children route key, the code must render the
    appropriate fallback element (notFoundElement for 404, forbiddenElement
    for 403, unauthorizedElement for 401) instead of descending into the
    throwing subtree.
    """
    src = _read_component_tree()

    # Must check boundary match AND children route key
    has_boundary_match = bool(
        re.search(
            r"boundaryTree\s*===?\s*tree|tree\s*===?\s*\w*boundaryTree", src
        )
        or re.search(r"prerenderHTTPError\S*boundaryTree\s*===", src)
        or re.search(r"shouldRender\w*[Ff]allback|shouldRender\w*[Hh][Tt][Tt][Pp]", src)
    )

    # Must render fallback elements based on status code
    has_fallback_elements = bool(
        re.search(r"notFoundElement", src)
        and re.search(r"forbiddenElement", src)
        and re.search(r"unauthorizedElement", src)
    )

    # These fallback elements must be selected based on the triggered status
    # code (404/403/401) in a switch or conditional
    has_status_switch = bool(
        re.search(
            r"(?:case\s+404|===\s*404|triggeredStatus[\s\S]{0,100}404)[\s\S]{0,200}notFoundElement",
            src,
        )
        or re.search(
            r"(?:case\s+403|===\s*403|triggeredStatus[\s\S]{0,100}403)[\s\S]{0,200}forbiddenElement",
            src,
        )
        or re.search(
            r"(?:case\s+401|===\s*401|triggeredStatus[\s\S]{0,100}401)[\s\S]{0,200}unauthorizedElement",
            src,
        )
    )

    # Must call createSeedData with the fallback element
    has_seed_data = bool(
        re.search(r"createSeedData\s*\([\s\S]{0,200}fallback", src)
        or re.search(r"createSeedData\s*\(\s*ctx\s*,\s*fallback", src)
        or re.search(
            r"createSeedData\s*\([\s\S]{0,200}(?:notFoundElement|forbiddenElement|unauthorizedElement)",
            src,
        )
    )

    assert has_boundary_match, (
        "No boundary match check in create-component-tree.tsx — "
        "must check if current tree matches the prerender HTTP error boundary"
    )
    assert has_fallback_elements, (
        "Fallback elements (notFoundElement, forbiddenElement, unauthorizedElement) "
        "must all be used in the new rendering logic"
    )
    assert has_status_switch, (
        "No status-code-based selection of fallback element — "
        "must pick the right fallback for 404/403/401"
    )
    assert has_seed_data, (
        "Must create seed data from the fallback element via createSeedData"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_generic_error_path_preserved():
    """getErrorRSCPayload must still exist for non-HTTP-access errors.

    The fix only adds a BRANCH — the existing error recovery path via
    getErrorRSCPayload must remain for errors without a matching boundary.
    """
    src = _read_app_render()
    assert re.search(r"getErrorRSCPayload", src), (
        "getErrorRSCPayload removed — the generic error path must be preserved "
        "for errors that don't have a matching HTTP fallback boundary"
    )


# [static] pass_to_pass
def test_app_render_not_truncated():
    """app-render.tsx must not be truncated (>200KB file)."""
    src = Path(APP_RENDER).read_text()
    size = len(src.encode())
    assert size >= 200_000, (
        f"app-render.tsx is only {size} bytes — appears truncated/gutted "
        f"(expected >200KB for this file)"
    )


# [static] pass_to_pass
def test_create_component_tree_not_truncated():
    """create-component-tree.tsx must not be truncated (>15KB file)."""
    src = Path(COMPONENT_TREE).read_text()
    size = len(src.encode())
    assert size >= 15_000, (
        f"create-component-tree.tsx is only {size} bytes — appears truncated/gutted "
        f"(expected >15KB for this file)"
    )
