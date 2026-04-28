"""Behavioral tests for the swizzled MethodEndpoint component.

The PR adds docs/src/theme/ApiExplorer/MethodEndpoint/index.tsx — a local
override of docusaurus-theme-openapi-docs's MethodEndpoint component. The
upstream version calls a Redux hook at the top level which crashes during
Docusaurus static site generation (no Redux Provider exists during SSG).

The fix gates the Redux access behind `<BrowserOnly>`, so SSG can render
without touching the store.

These tests compile the swizzled file with esbuild (mocking BrowserOnly to
the SSG behavior of returning null) and SSR-render the component with
`renderToString`. A correct fix renders without throwing; the buggy version
or a missing file fails.
"""
import json
import os
import shutil
import subprocess
import tempfile

import pytest

REPO = "/workspace/superset"
HARNESS = "/workspace/test_harness"
TARGET = os.path.join(
    REPO, "docs/src/theme/ApiExplorer/MethodEndpoint/index.tsx"
)


def _bundle(entry: str) -> str:
    """Compile a TSX file via esbuild; return path to the CJS bundle.
    Raises on failure.

    The bundle is written under HARNESS so external `require('react')` calls
    in the bundled output resolve against the harness's node_modules.
    """
    out_dir = tempfile.mkdtemp(prefix="bundle_", dir=HARNESS)
    out_file = os.path.join(out_dir, "bundle.js")
    r = subprocess.run(
        ["node", "bundle.js", entry, out_file],
        cwd=HARNESS,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if r.returncode != 0:
        shutil.rmtree(out_dir, ignore_errors=True)
        raise RuntimeError(
            f"esbuild failed for {entry}:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"
        )
    return out_file


def _ssr(props: dict) -> str:
    """Compile TARGET and SSR-render with given props. Returns rendered HTML.
    Raises on compile or render failure."""
    bundle = _bundle(TARGET)
    try:
        r = subprocess.run(
            ["node", "render.js", bundle, json.dumps(props)],
            cwd=HARNESS,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode != 0:
            raise RuntimeError(
                f"SSR render failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"
            )
        return r.stdout
    finally:
        shutil.rmtree(os.path.dirname(bundle), ignore_errors=True)


# ----------------------- fail_to_pass tests -----------------------

def test_swizzle_file_exists():
    """The swizzle file must exist at the expected swizzle path."""
    assert os.path.isfile(TARGET), (
        f"Expected swizzle file at {TARGET}; Docusaurus only picks up "
        f"theme overrides at this exact path."
    )


def test_ssr_does_not_crash_without_redux_provider():
    """Core regression: SSR must not throw when no Redux Provider is mounted.

    This simulates Docusaurus SSG, which is the failure mode the PR fixes.
    The upstream component calls useSelector at the top level of
    MethodEndpoint, which throws "could not find react-redux context value"
    during SSG. A correct swizzle gates the Redux access behind BrowserOnly
    so it is never invoked on the server.
    """
    html = _ssr({"method": "get", "path": "/users"})
    assert isinstance(html, str) and len(html) > 0, (
        "Expected non-empty SSR output"
    )


def test_path_variable_substitution_id():
    """Path variables in braces must be converted to colon-prefixed form."""
    html = _ssr({"method": "get", "path": "/users/{id}"})
    assert ":id" in html, (
        f"Expected ':id' in rendered output for path '/users/{{id}}', got: {html!r}"
    )
    assert "{id}" not in html, (
        f"Brace form should be replaced; got: {html!r}"
    )


def test_path_variable_substitution_multiple():
    """Multiple path variables are all substituted."""
    html = _ssr({"method": "get", "path": "/users/{user_id}/posts/{post_id}"})
    assert ":user_id" in html
    assert ":post_id" in html
    assert "{user_id}" not in html
    assert "{post_id}" not in html


def test_method_uppercased_in_badge_get():
    html = _ssr({"method": "get", "path": "/x"})
    assert ">GET<" in html or "GET" in html
    # The original lowercase form must not be the rendered text
    # (it's still in the className `badge--primary`, but the visible text is uppercase)
    # check for absence of plain ">get<"
    assert ">get<" not in html


def test_method_uppercased_post():
    html = _ssr({"method": "post", "path": "/x"})
    assert "POST" in html


def test_method_event_renders_as_webhook():
    """The 'event' method must render as 'Webhook' (not 'EVENT')."""
    html = _ssr({"method": "event", "path": "/hook"})
    assert "Webhook" in html, f"Expected 'Webhook' in output, got: {html!r}"
    assert "EVENT" not in html, (
        f"'event' method should render as 'Webhook', not 'EVENT'; got: {html!r}"
    )


def test_method_color_class_get_primary():
    """GET method gets the 'primary' badge color."""
    html = _ssr({"method": "get", "path": "/x"})
    assert "badge--primary" in html, (
        f"Expected 'badge--primary' class for GET; got: {html!r}"
    )


def test_method_color_class_post_success():
    html = _ssr({"method": "post", "path": "/x"})
    assert "badge--success" in html


def test_method_color_class_delete_danger():
    html = _ssr({"method": "delete", "path": "/x"})
    assert "badge--danger" in html


def test_method_color_class_put_info():
    html = _ssr({"method": "put", "path": "/x"})
    assert "badge--info" in html


def test_method_color_class_patch_warning():
    html = _ssr({"method": "patch", "path": "/x"})
    assert "badge--warning" in html


def test_method_color_class_head_secondary():
    html = _ssr({"method": "head", "path": "/x"})
    assert "badge--secondary" in html


def test_event_method_omits_path():
    """When method is 'event', the path heading is not rendered."""
    html = _ssr({"method": "event", "path": "/hook"})
    # No <h2> path heading for event
    assert "openapi__method-endpoint-path" not in html, (
        f"event method should not render the path heading; got: {html!r}"
    )


def test_endpoint_renders_path_heading():
    """Non-event methods render a path heading element."""
    html = _ssr({"method": "get", "path": "/x"})
    assert "openapi__method-endpoint-path" in html


def test_pre_wrapper_class_present():
    """The output is wrapped in a <pre> with the openapi__method-endpoint class."""
    html = _ssr({"method": "get", "path": "/x"})
    assert "openapi__method-endpoint" in html
    assert "<pre" in html


def test_divider_rendered():
    """A divider div is rendered after the pre block."""
    html = _ssr({"method": "get", "path": "/x"})
    assert "openapi__divider" in html


def test_redux_useselector_not_invoked_at_top_level():
    """During SSR, useSelector must not be called from MethodEndpoint's body.

    We render with a fresh require so any top-level Redux access would throw
    'could not find react-redux context value'. If the swizzle correctly
    gates Redux behind BrowserOnly (which we mock to return null on the
    server), the hook is never reached.
    """
    # Render twice to also exercise the React re-render path.
    h1 = _ssr({"method": "get", "path": "/a/{id}"})
    h2 = _ssr({"method": "post", "path": "/b/{x}/{y}"})
    assert ":id" in h1
    assert ":x" in h2 and ":y" in h2


def test_callback_context_omits_server_url():
    """When context='callback', no server URL is rendered (only the path)."""
    html = _ssr({"method": "get", "path": "/cb/{id}", "context": "callback"})
    # Should still render the heading and the substituted path
    assert "openapi__method-endpoint-path" in html
    assert ":id" in html
    assert "__BROWSER_ONLY_MARKER__" not in html, (
        "BrowserOnly/server URL wrapper must not appear for callback context"
    )


# ----------------------- agent_config rules -----------------------

def test_agent_config_asf_license_header():
    """New code files require an ASF license header (CLAUDE.md rule)."""
    with open(TARGET, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Licensed to the Apache Software Foundation" in content, (
        "New code files must include the standard Apache Software "
        "Foundation license header (CLAUDE.md / AGENTS.md / "
        ".cursor/rules/dev-standard.mdc)"
    )
    assert "Apache License, Version 2.0" in content


def test_agent_config_no_any_type():
    """TypeScript code must not use the `any` type (CLAUDE.md frontend rule)."""
    with open(TARGET, "r", encoding="utf-8") as f:
        content = f.read()
    # Strip line/block comments before scanning so commentary about `any`
    # (e.g., explanatory prose) isn't penalized. Only assertions about real
    # TypeScript type annotations using `any` should fail.
    import re
    # Remove block comments
    no_block = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)
    # Remove line comments
    no_comments = re.sub(r"//[^\n]*", "", no_block)
    # Look for type-position `any` usage:
    #   ': any' or '<any>' or 'as any' or 'any[]' or '| any' or 'Record<string, any>'
    bad_patterns = [
        r":\s*any\b",
        r"\bas\s+any\b",
        r"<\s*any\s*[,>]",
        r"\bany\s*\[\s*\]",
        r"\|\s*any\b",
    ]
    for pat in bad_patterns:
        m = re.search(pat, no_comments)
        assert m is None, (
            f"Disallowed `any` type usage found (pattern {pat!r} matched "
            f"{m.group()!r}). Use specific types instead — see CLAUDE.md "
            f"'Frontend Modernization > NO `any` types'."
        )


# ----------------------- pass_to_pass sanity -----------------------

def test_p2p_docs_package_json_valid():
    """Repo's docs/package.json is valid JSON (sanity p2p)."""
    with open(os.path.join(REPO, "docs/package.json"), "r") as f:
        data = json.load(f)
    assert "dependencies" in data
    assert "docusaurus-theme-openapi-docs" in data["dependencies"], (
        "Expected docusaurus-theme-openapi-docs dependency at base; the "
        "swizzle target depends on it being declared."
    )


def test_p2p_existing_theme_file_compiles():
    """An unrelated existing theme file compiles with esbuild — sanity p2p
    matching the repo's `yarn typecheck`/`yarn build` CI step."""
    existing = os.path.join(REPO, "docs/src/theme/Root.js")
    assert os.path.isfile(existing), (
        f"Expected pre-existing file {existing} at base"
    )
    out = tempfile.mkdtemp(prefix="p2p_", dir=HARNESS)
    try:
        r = subprocess.run(
            ["node", "bundle.js", existing, os.path.join(out, "out.js")],
            cwd=HARNESS,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, (
            f"Existing theme file should compile cleanly: {r.stderr}"
        )
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_p2p_ci_typecheck_mimic():
    """Mimic the docs CI pipeline typecheck/compile step.

    The CI workflow (.github/workflows/superset-docs-verify.yml) runs
    'yarn typecheck' then 'yarn build' scoped to the docs/ directory.
    Both would catch TypeScript/compilation errors in theme files.
    This test validates that an existing theme file compiles via the
    same esbuild bundler the CI pipeline invokes.
    """
    existing = os.path.join(REPO, "docs/src/theme/Root.js")
    assert os.path.isfile(existing)
    out = tempfile.mkdtemp(prefix="ci_mimic_", dir=HARNESS)
    try:
        r = subprocess.run(
            ["bash", "-lc",
             f"cd /workspace/test_harness && node bundle.js {existing} {os.path.join(out, 'out.js')}"],
            capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, (
            f"CI typecheck equivalent should pass: {r.stderr}"
        )
    finally:
        shutil.rmtree(out, ignore_errors=True)


def test_p2p_node_runtime_works():
    """Node + react-dom/server are installed in the harness."""
    r = subprocess.run(
        ["node", "-e", "require('react-dom/server'); console.log('ok')"],
        cwd=HARNESS,
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert r.returncode == 0
    assert "ok" in r.stdout
