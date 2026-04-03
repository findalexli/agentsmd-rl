"""
Task: playwright-featmcp-filtering-and-optional-headersbody
Repo: microsoft/playwright @ 998f35dccb1de560350765493073dec5ec2c811c
PR:   39672

Enhance browser_network_requests tool with URL filtering (regexp),
optional request headers / request body display, and rename
includeStatic → static. Also create .github/copilot-instructions.md.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/playwright"
NETWORK_TS = Path(REPO) / "packages/playwright-core/src/tools/backend/network.ts"
COMMANDS_TS = Path(REPO) / "packages/playwright-core/src/tools/cli-daemon/commands.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must parse without syntax errors."""
    for fpath in [NETWORK_TS, COMMANDS_TS]:
        assert fpath.exists(), f"{fpath} does not exist"
        content = fpath.read_text()
        # Basic syntax sanity: balanced braces
        assert content.count("{") == content.count("}"), (
            f"Unbalanced braces in {fpath.name}"
        )
        # Must not be empty
        assert len(content) > 100, f"{fpath.name} appears truncated or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — tool schema & behavior
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_schema_has_new_params():
    """browser_network_requests schema must declare filter, requestBody, and requestHeaders params."""
    src = NETWORK_TS.read_text()

    # Find the inputSchema block for the requests tool
    # Look for the three new params as zod field declarations
    assert re.search(r"""filter\s*:\s*z\.\s*string""", src), (
        "inputSchema must include a 'filter' string param"
    )
    assert re.search(r"""requestBody\s*:\s*z\.\s*boolean""", src), (
        "inputSchema must include a 'requestBody' boolean param"
    )
    assert re.search(r"""requestHeaders\s*:\s*z\.\s*boolean""", src), (
        "inputSchema must include a 'requestHeaders' boolean param"
    )


# [pr_diff] fail_to_pass
def test_static_replaces_include_static():
    """The old 'includeStatic' param must be renamed to 'static' in the tool schema."""
    src = NETWORK_TS.read_text()

    # Must NOT have includeStatic as a schema field name
    # (could still appear in variable names elsewhere, so check schema context)
    assert not re.search(r"""includeStatic\s*:\s*z\.""", src), (
        "includeStatic should be renamed to static in the inputSchema"
    )
    # Must have 'static' as a schema field
    assert re.search(r"""static\s*:\s*z\.\s*boolean""", src), (
        "Schema must have a 'static' boolean param (renamed from includeStatic)"
    )


# [pr_diff] fail_to_pass
def test_render_request_handles_headers_and_body():
    """renderRequest must accept and render optional headers and body."""
    src = NETWORK_TS.read_text()

    # The function signature must accept params for body and headers
    # Look for renderRequest with additional params beyond just request
    render_match = re.search(
        r"function\s+renderRequest\s*\([^)]*,[^)]+\)", src
    ) or re.search(
        r"renderRequest\s*=\s*(?:async\s+)?\([^)]*,[^)]+\)", src
    )
    assert render_match, (
        "renderRequest must accept additional parameters for body/headers"
    )

    # Must render headers when requested — check for "Request headers" output
    assert re.search(r"""['\"`].*[Rr]equest\s+headers""", src), (
        "renderRequest must output 'Request headers' label when headers are included"
    )
    # Must render body when requested — check for "Request body" output
    assert re.search(r"""['\"`].*[Rr]equest\s+body""", src), (
        "renderRequest must output 'Request body' label when body is included"
    )


# [pr_diff] fail_to_pass
def test_filter_logic_implemented():
    """The handle function must filter requests by URL using the filter param."""
    src = NETWORK_TS.read_text()

    # Must create a RegExp from the filter param
    assert re.search(r"new\s+RegExp\s*\(", src) or re.search(r"\.match\s*\(", src) or re.search(r"\.test\s*\(", src), (
        "Must use RegExp (or match/test) to filter requests by URL"
    )
    # Must reference params.filter or destructured filter
    assert "filter" in src, "Must reference filter parameter in handle function"

    # Must call .url() to get the request URL for filtering
    assert re.search(r"\.url\(\)", src), (
        "Must access request.url() to filter by URL"
    )


# [pr_diff] fail_to_pass

    # Find the networkRequests command declaration area
    # Check for the new CLI options
    assert re.search(r"""['"]request-body['"]""", src), (
        "CLI must declare 'request-body' option"
    )
    assert re.search(r"""['"]request-headers['"]""", src), (
        "CLI must declare 'request-headers' option"
    )
    assert "filter" in src, (
        "CLI must declare 'filter' option"
    )

    # The toolParams mapping must pass the new params to the MCP tool
    assert "requestBody" in src, (
        "CLI toolParams must map to requestBody"
    )
    assert "requestHeaders" in src, (
        "CLI toolParams must map to requestHeaders"
    )


# ---------------------------------------------------------------------------
# Config edit (config_edit) — copilot-instructions.md
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # Must contain PR review guidance — check key concepts
    assert "review" in content, (
        "copilot-instructions.md must mention PR review"
    )
    assert "comment" in content, (
        "copilot-instructions.md must discuss commenting guidelines"
    )
    # Should focus reviews on meaningful issues
    assert any(w in content for w in ["bug", "logic", "security", "semantic"]), (
        "copilot-instructions.md should focus reviews on substantive issues (bugs, logic, security)"
    )
    # Should discourage style/formatting nitpicks
    assert any(w in content for w in ["style", "formatting", "naming", "whitespace"]), (
        "copilot-instructions.md should mention skipping style/formatting issues"
    )
