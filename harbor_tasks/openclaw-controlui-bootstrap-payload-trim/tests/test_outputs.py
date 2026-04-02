"""
Task: openclaw-controlui-bootstrap-payload-trim
Repo: openclaw/openclaw @ 847912f3e2cfefad5b383603ec53525ae599b48c
PR:   57727

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

import pytest

REPO = "/workspace/openclaw"

CHANGED_FILES = [
    "src/gateway/control-ui-contract.ts",
    "src/gateway/control-ui.ts",
    "ui/src/ui/controllers/control-ui-bootstrap.ts",
    "ui/vite.config.ts",
]


@pytest.fixture(scope="module", autouse=True)
def npm_install():
    """Install npm dependencies for root and ui packages."""
    subprocess.run(
        ["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund", "--loglevel=error"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    subprocess.run(
        ["npm", "install", "--ignore-scripts", "--no-audit", "--no-fund", "--loglevel=error"],
        cwd=f"{REPO}/ui", capture_output=True, timeout=120,
    )


def _patch_gateway_test():
    """Patch gateway HTTP test to assert NEW behavior (no extra fields in payload)."""
    gw = Path(f"{REPO}/src/gateway/control-ui.http.test.ts")
    src = gw.read_text()
    # Remove assistantAgentId from the parsed type alias
    src = re.sub(r"\n\s*assistantAgentId:\s*string;\n", "\n", src)
    # Replace positive assertion with negative ones
    src = src.replace(
        'expect(parsed.assistantAgentId).toBe("main")',
        'expect(parsed).not.toHaveProperty("assistantAgentId");\n        expect(parsed).not.toHaveProperty("serverVersion")',
    )
    gw.write_text(src)


def _patch_ui_test():
    """Patch UI bootstrap test to assert NEW behavior (removed fields are null)."""
    ui = Path(f"{REPO}/ui/src/ui/controllers/control-ui-bootstrap.test.ts")
    src = ui.read_text()
    # Remove extra fields from mock response
    src = re.sub(r'\n\s*assistantAgentId:\s*"main",\n', "\n", src)
    src = re.sub(r'\n\s*serverVersion:\s*"2026\.3\.7",\n', "\n", src)
    # Replace positive assertions with null checks
    src = src.replace(
        'expect(state.assistantAgentId).toBe("main")',
        "expect(state.assistantAgentId).toBeNull()",
    )
    src = src.replace(
        'expect(state.serverVersion).toBe("2026.3.7")',
        "expect(state.serverVersion).toBeNull()",
    )
    # Add null assertions after "Assistant" name checks in blocks that lack them
    lines = src.split("\n")
    new_lines = []
    for i, line in enumerate(lines):
        new_lines.append(line)
        if 'expect(state.assistantName).toBe("Assistant")' in line:
            indent = line[: len(line) - len(line.lstrip())]
            j = i + 1
            while j < len(lines) and lines[j].strip() == "":
                j += 1
            if j < len(lines) and "assistantAgentId" not in lines[j]:
                new_lines.append(f"{indent}expect(state.assistantAgentId).toBeNull();")
                new_lines.append(f"{indent}expect(state.serverVersion).toBeNull();")
    ui.write_text("\n".join(new_lines))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_gateway_handler_bootstrap_payload():
    """Gateway handler test: bootstrap payload has no assistantAgentId or serverVersion."""
    _patch_gateway_test()
    r = subprocess.run(
        ["npx", "vitest", "run", "src/gateway/control-ui.http.test.ts",
         "--reporter=verbose", "--no-color"],
        cwd=REPO, capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"Gateway handler vitest failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_ui_bootstrap_controller():
    """UI bootstrap controller test: removed fields default to null."""
    _patch_ui_test()
    r = subprocess.run(
        ["npx", "vitest", "run", "src/ui/controllers/control-ui-bootstrap.test.ts",
         "--reporter=verbose", "--no-color"],
        cwd=f"{REPO}/ui", capture_output=True, timeout=120,
    )
    assert r.returncode == 0, (
        f"UI bootstrap vitest failed:\n{r.stdout.decode()[-2000:]}\n{r.stderr.decode()[-1000:]}"
    )


# [pr_diff] fail_to_pass
def test_contract_type_no_extra_fields():
    """ControlUiBootstrapConfig type has only display fields, no internal identifiers."""
    src = Path(f"{REPO}/src/gateway/control-ui-contract.ts").read_text()
    # Core fields must be present
    assert re.search(r"basePath\s*[:\?]", src), "Missing basePath in contract type"
    assert re.search(r"assistantName\s*[:\?]", src), "Missing assistantName in contract type"
    assert re.search(r"assistantAvatar\s*[:\?]", src), "Missing assistantAvatar in contract type"
    # Removed fields must be absent
    assert not re.search(r"assistantAgentId\s*[:\?]", src), "assistantAgentId still in contract type"
    assert not re.search(r"serverVersion\s*[:\?]", src), "serverVersion still in contract type"


# [pr_diff] fail_to_pass
def test_vite_stub_no_agent_id():
    """Vite dev server mock bootstrap response does not include assistantAgentId."""
    src = Path(f"{REPO}/ui/vite.config.ts").read_text()
    assert "assistantAgentId" not in src, "Vite dev stub still includes assistantAgentId"


# [pr_diff] fail_to_pass
def test_handler_no_version_import():
    """Gateway handler must not import resolveRuntimeServiceVersion (removed field source)."""
    src = Path(f"{REPO}/src/gateway/control-ui.ts").read_text()
    assert "resolveRuntimeServiceVersion" not in src, (
        "Handler still imports resolveRuntimeServiceVersion — serverVersion field not fully removed"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_handler_core_fields_preserved():
    """Gateway handler still populates basePath, assistantName, assistantAvatar."""
    src = Path(f"{REPO}/src/gateway/control-ui.ts").read_text()
    # Check the satisfies block still has the three required fields
    for field in ["basePath", "assistantName", "assistantAvatar"]:
        assert field in src, f"Handler missing core display field: {field}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:144 @ 847912f3e2cfefad5b383603ec53525ae599b48c
def test_no_any_types():
    """No 'any' type annotations in changed files (CLAUDE.md:144)."""
    for relpath in CHANGED_FILES:
        fpath = Path(f"{REPO}/{relpath}")
        if not fpath.exists():
            continue
        for i, line in enumerate(fpath.read_text().splitlines(), 1):
            # Match `: any`, `<any>`, `as any` patterns but not inside comments/strings
            stripped = line.lstrip()
            if stripped.startswith("//") or stripped.startswith("*"):
                continue
            assert not re.search(r":\s*any\b", line), (
                f"'any' type annotation at {relpath}:{i}: {line.strip()}"
            )
            assert not re.search(r"\bas\s+any\b", line), (
                f"'as any' cast at {relpath}:{i}: {line.strip()}"
            )


# [agent_config] pass_to_pass — CLAUDE.md:146 @ 847912f3e2cfefad5b383603ec53525ae599b48c
def test_no_ts_nocheck_or_lint_suppression():
    """No @ts-nocheck or inline lint suppressions in changed files (CLAUDE.md:146)."""
    suppression_patterns = [
        (r"@ts-nocheck", "@ts-nocheck"),
        (r"@ts-ignore", "@ts-ignore"),
        (r"eslint-disable", "eslint-disable"),
        (r"oxlint-disable", "oxlint-disable"),
    ]
    for relpath in CHANGED_FILES:
        fpath = Path(f"{REPO}/{relpath}")
        if not fpath.exists():
            continue
        content = fpath.read_text()
        for pattern, label in suppression_patterns:
            assert not re.search(pattern, content), (
                f"Lint suppression '{label}' found in {relpath}"
            )
