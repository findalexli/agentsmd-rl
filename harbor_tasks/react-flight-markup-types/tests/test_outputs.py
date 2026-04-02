"""
Task: react-flight-markup-types
Repo: facebook/react @ 10680271fab565e0edf948d3a6dc9d30e83df94c
PR:   35634

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/react"
MARKUP_CONFIG = f"{REPO}/packages/react-client/src/forks/ReactFlightClientConfig.markup.js"
ACTION_SERVER = f"{REPO}/packages/react-server/src/ReactFlightActionServer.js"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_reference_id_not_opaque():
    """ServerReferenceId type must not use the 'opaque' modifier."""
    # AST-only because: Flow type annotations in JS files cannot be executed
    src = Path(MARKUP_CONFIG).read_text()
    assert "export opaque type ServerReferenceId" not in src, (
        "ServerReferenceId must not be an opaque type — "
        "opaque types hide the underlying representation from external consumers, "
        "but ServerReferenceId is a plain string that must be passable across module boundaries"
    )
    assert "export type ServerReferenceId = string" in src, (
        "ServerReferenceId must be exported as a plain type alias for string"
    )


# [pr_diff] fail_to_pass
def test_resolve_server_reference_parameter_type():
    """resolveServerReference id parameter must use ServerReferenceId, not mixed."""
    # AST-only because: Flow type annotations in JS files cannot be executed
    src = Path(MARKUP_CONFIG).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "resolveServerReference" in line and "export function" in line:
            # Check the next 6 lines for the id parameter declaration
            context = "\n".join(lines[i : i + 6])
            assert "id: mixed" not in context, (
                "resolveServerReference must not use 'id: mixed' — "
                "the parameter should reference the declared ServerReferenceId type"
            )
            assert "id: ServerReferenceId" in context, (
                "resolveServerReference must use 'id: ServerReferenceId' as the parameter type"
            )
            return
    assert False, "resolveServerReference function not found in markup config file"


# [pr_diff] fail_to_pass
def test_load_server_reference_metadata_id_type():
    """loadServerReference metaData.id must use ServerReferenceId, not string."""
    # AST-only because: Flow type annotations in JS files cannot be executed
    src = Path(ACTION_SERVER).read_text()
    lines = src.splitlines()
    for i, line in enumerate(lines):
        if "function loadServerReference" in line:
            # Find the metaData object type block in the next ~15 lines
            context = "\n".join(lines[i : i + 15])
            # Locate just the metaData block
            start = context.find("metaData:")
            if start == -1:
                continue
            end = context.find("}", start)
            metadata_block = context[start : end + 1] if end != -1 else context[start:]
            assert "id: string" not in metadata_block, (
                "loadServerReference metaData.id must not be typed as bare 'string' — "
                "it should use the specific ServerReferenceId type alias"
            )
            assert "id: ServerReferenceId" in metadata_block, (
                "loadServerReference metaData.id must be typed as 'ServerReferenceId'"
            )
            return
    assert False, "loadServerReference function not found in ReactFlightActionServer.js"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_server_manifest_remains_opaque():
    """ServerManifest must stay opaque — only ServerReferenceId type was changed."""
    # AST-only because: Flow type annotations in JS files cannot be executed
    src = Path(MARKUP_CONFIG).read_text()
    assert "export opaque type ServerManifest = null" in src, (
        "ServerManifest must remain an opaque type (not changed by this fix)"
    )


# [static] pass_to_pass
def test_resolve_server_reference_throws_error():
    """resolveServerReference must still throw its error (body not stubbed out)."""
    # AST-only because: Flow type annotations in JS files cannot be executed
    src = Path(MARKUP_CONFIG).read_text()
    assert "renderToHTML should not have emitted Server References" in src, (
        "resolveServerReference must still contain its throw statement — "
        "the fix is only a type annotation change, not a logic change"
    )
