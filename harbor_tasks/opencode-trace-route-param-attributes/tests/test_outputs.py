"""Behavioral tests for opencode#23189 — auto-tag route spans with route params.

The PR introduces a `requestAttributes(c)` helper in
packages/opencode/src/server/routes/instance/trace.ts that builds a flat
Record<string, string> of span attributes for an HTTP request: http.method,
http.path (pathname only — query stripped), and every matched route param
prefixed with `opencode.`. The same helper is used by `runRequest`.

We exercise the helper through bun by invoking a small TS driver that imports
from the modified source file and prints the helper's output as JSON. Python
parses the JSON and asserts the expected attribute map.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO = Path("/workspace/opencode")
PKG = REPO / "packages/opencode"
TRACE_TS = "/workspace/opencode/packages/opencode/src/server/routes/instance/trace.ts"


def _call_request_attributes(
    method: str, url: str, params: dict[str, str]
) -> dict[str, str]:
    """Drive `requestAttributes(c)` from `trace.ts` and return its result.

    Fails the calling test (via assertion on bun's exit code or a parse error)
    when the helper is missing, throws, or returns something that isn't a
    plain object of strings.
    """
    # Use a named import — this fails at module-load time (not just at call
    # time) if `requestAttributes` is not a named export, mirroring how the
    # gold test file imports it.
    driver = f"""
import {{ requestAttributes }} from {json.dumps(TRACE_TS)}
if (typeof requestAttributes !== "function") {{
  console.error("HELPER_NOT_A_FUNCTION")
  process.exit(2)
}}
const ctx = {{
  req: {{
    method: {json.dumps(method)},
    url: {json.dumps(url)},
    param: () => ({json.dumps(params)}),
  }},
}}
const out = requestAttributes(ctx as any)
process.stdout.write(JSON.stringify(out))
"""
    r = subprocess.run(
        ["bun", "run", "-"],
        input=driver,
        capture_output=True,
        text=True,
        cwd=str(PKG),
        timeout=60,
    )
    assert r.returncode == 0, (
        f"bun driver failed (rc={r.returncode}).\n"
        f"stderr:\n{r.stderr}\nstdout:\n{r.stdout}"
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:  # pragma: no cover — surfaced as test failure
        raise AssertionError(
            f"helper did not print valid JSON: {e}\nstdout was:\n{r.stdout!r}"
        )


# ───────────────────────── fail_to_pass: behavior ────────────────────────────


def test_method_and_path_basic():
    """http.method and http.path are populated for a simple GET."""
    attrs = _call_request_attributes("GET", "http://localhost/session", {})
    assert attrs["http.method"] == "GET"
    assert attrs["http.path"] == "/session"


def test_path_strips_query_string():
    """http.path is the URL pathname only — query string is dropped."""
    attrs = _call_request_attributes(
        "GET",
        "http://localhost/file/search?query=foo&limit=10",
        {},
    )
    assert attrs["http.path"] == "/file/search"
    # And the query keys must NOT leak into the attributes map.
    assert "query" not in attrs
    assert "opencode.query" not in attrs


def test_route_params_get_opencode_prefix():
    """Each route param k=v becomes attribute opencode.k=v."""
    attrs = _call_request_attributes(
        "POST",
        "http://localhost/session/ses_xyz/prompt_async",
        {"sessionID": "ses_xyz"},
    )
    assert attrs["opencode.sessionID"] == "ses_xyz"
    # The unprefixed key must NOT be present — prefixing is the whole point.
    assert "sessionID" not in attrs


def test_multiple_nested_route_params():
    """Nested IDs (sessionID + messageID + partID) all show up prefixed."""
    attrs = _call_request_attributes(
        "GET",
        "http://localhost/session/ses_a/message/msg_b/part/prt_c",
        {"sessionID": "ses_a", "messageID": "msg_b", "partID": "prt_c"},
    )
    assert attrs["opencode.sessionID"] == "ses_a"
    assert attrs["opencode.messageID"] == "msg_b"
    assert attrs["opencode.partID"] == "prt_c"


def test_no_params_no_opencode_attrs():
    """When the route has no matched params, no opencode.* keys appear."""
    attrs = _call_request_attributes(
        "POST", "http://localhost/config", {}
    )
    opencode_keys = [k for k in attrs if k.startswith("opencode.")]
    assert opencode_keys == []
    # http.method/path still present
    assert attrs["http.method"] == "POST"
    assert attrs["http.path"] == "/config"


def test_non_id_param_name_is_preserved():
    """A non-ID param like :name (used by mcp routes) is still tagged verbatim."""
    attrs = _call_request_attributes(
        "POST", "http://localhost/mcp/exa/connect", {"name": "exa"}
    )
    assert attrs["opencode.name"] == "exa"


def test_method_value_is_request_method_not_constant():
    """http.method is taken from the request, not hardcoded."""
    for method in ("GET", "POST", "PATCH", "DELETE"):
        attrs = _call_request_attributes(method, "http://localhost/x", {})
        assert attrs["http.method"] == method


def test_runRequest_delegates_to_requestAttributes():
    """`runRequest` must delegate to `requestAttributes(c)` rather than
    constructing the attribute map inline. This is the second half of the
    refactor — without it, the route-param tags are NOT emitted on actual
    request spans, only when `requestAttributes` is called directly.

    We can't easily invoke `runRequest` end-to-end here without standing up
    the full Effect runtime, so we verify two things in the source:
      1. `requestAttributes` is called as a function (not just mentioned).
      2. `runRequest` no longer hardcodes `"http.method": c.req.method` as
         an inline attributes object — that responsibility now belongs to
         the helper.
    """
    src = Path(TRACE_TS).read_text()

    # 1. There must be at least one *call* of requestAttributes in the file
    #    in addition to its definition. A call looks like `requestAttributes(`
    #    where the preceding token is not `function` / `const`.
    import re
    call_sites = [
        m for m in re.finditer(r"requestAttributes\s*\(", src)
        if not re.search(
            r"(?:function|const|export\s+function|export\s+const)\s+$",
            src[: m.start()],
        )
    ]
    assert len(call_sites) >= 1, (
        "Expected `runRequest` (or another caller) to invoke "
        "`requestAttributes(...)`. Did not find any call site outside the "
        "function's own definition.\n\nFile:\n" + src
    )

    # 2. The old inline attribute object inside runRequest should be gone.
    #    Specifically, the literal `"http.method": c.req.method` next to
    #    `"http.path"` should no longer appear inside `runRequest` — the
    #    helper builds that map now.
    runrequest_match = re.search(
        r"export function runRequest[\s\S]*?\n\}\n", src
    )
    assert runrequest_match is not None, (
        "Could not locate `runRequest` definition in trace.ts:\n" + src
    )
    runrequest_body = runrequest_match.group(0)
    assert '"http.method": c.req.method' not in runrequest_body, (
        "`runRequest` still builds the attributes object inline — it should "
        "delegate to `requestAttributes(c)` so route params are tagged on "
        "real request spans.\n\nrunRequest body was:\n" + runrequest_body
    )


# ─────────────────────── pass_to_pass: existing repo test ────────────────────


def test_existing_cli_error_test_still_passes():
    """An unrelated existing unit test in the repo continues to pass.
    Guards against the agent's edit accidentally breaking something else."""
    r = subprocess.run(
        ["bun", "test", "test/cli/error.test.ts"],
        cwd=str(PKG),
        capture_output=True,
        text=True,
        timeout=180,
    )
    assert r.returncode == 0, (
        f"existing test/cli/error.test.ts failed (rc={r.returncode}).\n"
        f"stdout:\n{r.stdout}\nstderr:\n{r.stderr[-500:]}"
    )
