"""Behavioral tests for the @effect/ai AiError prototype-preservation fix."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

REPO = "/workspace/effect"
AI_PKG = f"{REPO}/packages/ai/ai"
CHECK_TS = "/tests/check_aierror.ts"


def _run_check() -> dict:
    """Run the TS probe inside the @effect/ai package and parse its JSON output."""
    proc = subprocess.run(
        ["pnpm", "exec", "tsx", CHECK_TS],
        cwd=AI_PKG,
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = proc.stdout
    err = proc.stderr
    m = re.search(r"__JSON_BEGIN__\n(.*?)\n__JSON_END__", out, re.S)
    assert m, (
        f"probe did not emit JSON block (rc={proc.returncode})\n"
        f"--- stdout ---\n{out[-1000:]}\n--- stderr ---\n{err[-1000:]}"
    )
    return json.loads(m.group(1))


def test_baseline_input_headers_is_headers():
    """Sanity: the test fixture itself produces a real Headers instance."""
    data = _run_check()
    assert data["input_is_headers"] is True, (
        "Test fixture broken: Headers.fromInput(...) should produce a "
        "Headers instance recognised by Headers.isHeaders. If this fails, "
        "the test environment itself is misconfigured."
    )


def test_request_error_preserves_headers_prototype():
    """fromRequestError must preserve the Headers prototype on request.headers."""
    data = _run_check()
    assert data["req_err_request_headers_is_headers"] is True, (
        "AiError.HttpRequestError.fromRequestError stripped the Headers "
        "prototype from request.headers — Headers.isHeaders(...) returned "
        "false. The constructor's schema validation is normalising the "
        "Headers instance into a plain object."
    )


def test_response_error_preserves_request_headers_prototype():
    """fromResponseError must preserve the Headers prototype on request.headers."""
    data = _run_check()
    assert data["resp_err_request_headers_is_headers"] is True, (
        "AiError.HttpResponseError.fromResponseError stripped the Headers "
        "prototype from request.headers — Headers.isHeaders(...) returned "
        "false."
    )


def test_response_error_preserves_response_headers_prototype():
    """fromResponseError must preserve the Headers prototype on response.headers."""
    data = _run_check()
    assert data["resp_err_response_headers_is_headers"] is True, (
        "AiError.HttpResponseError.fromResponseError stripped the Headers "
        "prototype from response.headers — Headers.isHeaders(...) returned "
        "false."
    )


def test_error_payload_fields_round_trip():
    """The ordinary scalar fields must still be accessible after the fix."""
    data = _run_check()
    assert data["req_err_request_method"] == "POST"
    assert data["req_err_request_url"] == "https://api.example.com/v1/chat"
    assert data["req_err_module"] == "TestModule"
    assert data["req_err_reason"] == "Transport"
    assert data["resp_err_response_status"] == 429
    assert data["resp_err_module"] == "TestModule"
    assert data["resp_err_reason"] == "StatusCode"


def test_changeset_present():
    """AGENTS.md mandates a changeset file accompany every PR."""
    changeset_dir = Path(REPO) / ".changeset"
    assert changeset_dir.is_dir(), f"missing {changeset_dir}"
    matches = []
    for f in changeset_dir.glob("*.md"):
        if f.name in ("README.md",):
            continue
        text = f.read_text()
        if "@effect/ai" in text:
            matches.append((f.name, text))
    assert matches, (
        "no changeset file under .changeset/ mentions '@effect/ai'. "
        "AGENTS.md says: 'All pull requests must include a changeset in the "
        "`.changeset/` directory.'"
    )
    # Each changeset starts with frontmatter declaring affected packages.
    name, body = matches[0]
    assert re.search(r'^---\s*$', body, re.M), (
        f"changeset {name} is missing the YAML frontmatter delimiter '---'"
    )
    assert re.search(r'"@effect/ai":\s*(patch|minor|major)', body), (
        f"changeset {name} must declare a release type for @effect/ai "
        "(patch|minor|major) in its frontmatter."
    )


def test_ai_package_typecheck():
    """AGENTS.md mandates `pnpm check` passes — ensure ai package still type-checks."""
    proc = subprocess.run(
        ["pnpm", "exec", "tsc", "-b", "tsconfig.json"],
        cwd=AI_PKG,
        capture_output=True,
        text=True,
        timeout=600,
    )
    assert proc.returncode == 0, (
        f"`tsc -b tsconfig.json` failed in {AI_PKG}\n"
        f"stdout:\n{proc.stdout[-2000:]}\nstderr:\n{proc.stderr[-2000:]}"
    )
