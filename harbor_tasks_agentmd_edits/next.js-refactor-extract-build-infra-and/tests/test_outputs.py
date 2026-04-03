"""
Task: next.js-refactor-extract-build-infra-and
Repo: vercel/next.js @ f922882fac7026198e1d95d936047aad72350358
PR:   90422

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/next.js"

SERVER_ALIAS = (
    Path(REPO)
    / "packages/next/src/build/webpack/alias/react-dom-server.js"
)
EXPERIMENTAL_ALIAS = (
    Path(REPO)
    / "packages/next/src/build/webpack/alias/react-dom-server-experimental.js"
)
SKILL_PATH = Path(REPO) / ".agents/skills/v8-jit/SKILL.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified JS alias files must parse without syntax errors."""
    for path in [SERVER_ALIAS, EXPERIMENTAL_ALIAS]:
        r = subprocess.run(
            ["node", "--check", str(path)],
            capture_output=True,
            timeout=15,
        )
        assert r.returncode == 0, (
            f"Syntax error in {path.name}: {r.stderr.decode()}"
        )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_server_exports_pipeable_stream():
    """react-dom-server.js must re-export renderToPipeableStream and resumeToPipeableStream."""
    content = SERVER_ALIAS.read_text()
    assert "exports.renderToPipeableStream" in content, (
        "react-dom-server.js must export renderToPipeableStream"
    )
    assert "exports.resumeToPipeableStream" in content, (
        "react-dom-server.js must export resumeToPipeableStream"
    )


# [pr_diff] fail_to_pass
def test_experimental_exports_pipeable_stream():
    """react-dom-server-experimental.js must re-export renderToPipeableStream and resumeToPipeableStream."""
    content = EXPERIMENTAL_ALIAS.read_text()
    assert "exports.renderToPipeableStream" in content, (
        "react-dom-server-experimental.js must export renderToPipeableStream"
    )
    assert "exports.resumeToPipeableStream" in content, (
        "react-dom-server-experimental.js must export resumeToPipeableStream"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — agent skill file tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass

    # Must cover hidden classes / shapes (core V8 concept)
    assert "hidden class" in content or "shape" in content, (
        "SKILL.md must cover V8 hidden classes/shapes"
    )

    # Must cover monomorphic vs polymorphic (IC optimization)
    assert "monomorphic" in content or "monomorphism" in content, (
        "SKILL.md must cover monomorphic call sites"
    )

    # Must cover V8 compilation tiers
    assert "turbofan" in content or "tiered compilation" in content or "optimizing compiler" in content, (
        "SKILL.md must cover V8's optimizing compiler (Turbofan) or tiered compilation"
    )

    # Must cover deoptimization
    assert "deopt" in content, (
        "SKILL.md must cover deoptimization"
    )


# [config_edit] fail_to_pass

    # Must have code blocks (practical examples)
    code_blocks = re.findall(r"```", content)
    assert len(code_blocks) >= 4, (
        f"SKILL.md should include multiple code examples (found {len(code_blocks) // 2} blocks, expected >= 2)"
    )

    # Must reference Next.js server internals (this is specific to the repo)
    content_lower = content.lower()
    assert "next.js" in content_lower or "next js" in content_lower or "server internal" in content_lower or "rendering" in content_lower, (
        "SKILL.md must reference Next.js server internals or rendering context"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_server_exports_preserved():
    """Existing exports (renderToReadableStream, resume, etc.) must still be present."""
    for path in [SERVER_ALIAS, EXPERIMENTAL_ALIAS]:
        content = path.read_text()
        for export_name in ["renderToReadableStream", "renderToString", "renderToStaticMarkup", "resume"]:
            assert f"exports.{export_name}" in content, (
                f"{path.name} must still export {export_name}"
            )
