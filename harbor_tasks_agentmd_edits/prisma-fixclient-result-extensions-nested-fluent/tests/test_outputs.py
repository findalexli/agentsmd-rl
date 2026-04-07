"""
Task: prisma-fixclient-result-extensions-nested-fluent
Repo: prisma/prisma @ 3fd1431decb1013969c9ef061f8c391e715fe973
PR:   29218

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/prisma"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_agents_md_client_architecture_intact():
    """Client architecture section in AGENTS.md is preserved."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "Client architecture (Prisma 7)" in content, \
        "AGENTS.md must retain the Client architecture section"
    assert "ClientEngine" in content, \
        "AGENTS.md must still reference ClientEngine"
    assert "QueryInterpreter" in content, \
        "AGENTS.md must still reference QueryInterpreter"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resolve_context_module_exports_function():
    """New module resolve-result-extension-context.ts must export resolveResultExtensionContext."""
    module_path = (
        Path(REPO) / "packages" / "client" / "src" / "runtime"
        / "core" / "extensions" / "resolve-result-extension-context.ts"
    )
    assert module_path.exists(), \
        f"Module not found: {module_path}"
    content = module_path.read_text()
    assert "export function resolveResultExtensionContext(" in content, \
        "Module must export resolveResultExtensionContext function"
    assert "relationPathFromDataPath" in content, \
        "Module must contain relationPathFromDataPath helper"
    assert "resolveNextArgs" in content, \
        "Module must contain resolveNextArgs helper"


# [pr_diff] fail_to_pass
def test_datapath_parsing_logic():
    """The dataPath parsing logic correctly extracts relation fields from selector/field pairs."""
    script = textwrap.dedent("""\
        const fs = require('fs');
        const src = fs.readFileSync(
            'packages/client/src/runtime/core/extensions/resolve-result-extension-context.ts',
            'utf8'
        );

        // Extract relationPathFromDataPath function
        const fnMatch = src.match(
            /function relationPathFromDataPath\\(dataPath[\\s\\S]*?^\\}/m
        );
        if (!fnMatch) {
            console.error('Could not find relationPathFromDataPath function');
            process.exit(1);
        }

        // Strip TS type annotations to get valid JS
        let fnBody = fnMatch[0]
            .replace(/\\(dataPath: string\\[\\]\\): string\\[\\] \\| undefined/g,
                     '(dataPath)')
            .replace(/: string\\[\\]/g, '')
            .replace(/: string/g, '');

        eval(fnBody);

        // Test 1: single-hop select path
        const r1 = relationPathFromDataPath(['select', 'posts']);
        if (!r1 || r1.length !== 1 || r1[0] !== 'posts') {
            console.error('FAIL: single-hop select', JSON.stringify(r1));
            process.exit(1);
        }

        // Test 2: multi-hop path
        const r2 = relationPathFromDataPath(['select', 'posts', 'include', 'author']);
        if (!r2 || r2.length !== 2 || r2[0] !== 'posts' || r2[1] !== 'author') {
            console.error('FAIL: multi-hop', JSON.stringify(r2));
            process.exit(1);
        }

        // Test 3: invalid first segment returns undefined
        const r3 = relationPathFromDataPath(['where', 'posts']);
        if (r3 !== undefined) {
            console.error('FAIL: invalid selector should return undefined', JSON.stringify(r3));
            process.exit(1);
        }

        // Test 4: empty path returns empty array
        const r4 = relationPathFromDataPath([]);
        if (!r4 || r4.length !== 0) {
            console.error('FAIL: empty path', JSON.stringify(r4));
            process.exit(1);
        }

        // Test 5: relation field named 'select' (edge case from the PR)
        const r5 = relationPathFromDataPath(['select', 'select']);
        if (!r5 || r5.length !== 1 || r5[0] !== 'select') {
            console.error('FAIL: relation named select', JSON.stringify(r5));
            process.exit(1);
        }

        console.log(JSON.stringify({ passed: 5 }));
    """)
    result = subprocess.run(
        ["node", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, \
        f"dataPath parsing tests failed:\\nstdout: {result.stdout}\\nstderr: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data["passed"] == 5, f"Expected 5 tests passed, got {data}"


# [pr_diff] fail_to_pass
def test_getPrismaClient_uses_context_resolution():
    """getPrismaClient.ts must import and use resolveResultExtensionContext."""
    gpc_path = Path(REPO) / "packages" / "client" / "src" / "runtime" / "getPrismaClient.ts"
    content = gpc_path.read_text()
    assert "resolve-result-extension-context" in content, \
        "getPrismaClient.ts must import from resolve-result-extension-context"
    assert "resolveResultExtensionContext" in content, \
        "getPrismaClient.ts must reference resolveResultExtensionContext"
    assert "requestParams.dataPath" in content or "dataPath:" in content, \
        "getPrismaClient.ts must pass dataPath to the context resolver"
    assert "extensionContext.modelName" in content or "context.modelName" in content, \
        "getPrismaClient.ts must use resolved modelName from extension context"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:123 @ 3fd1431decb1013969c9ef061f8c391e715fe973
def test_agents_md_documents_datapath():
    """AGENTS.md must document fluent dataPath and extension context resolution behavior."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    assert "dataPath" in content, \
        "AGENTS.md must document dataPath"
    assert "applyFluent" in content or "fluent" in content.lower(), \
        "AGENTS.md must reference the fluent API path construction"
    content_lower = content.lower()
    assert ("extension context" in content_lower
            or ("selector" in content_lower and "relation field" in content_lower)
            or "selector/field pair" in content_lower), \
        "AGENTS.md must document extension context resolution or selector/field pair interpretation"


# [agent_config] fail_to_pass — AGENTS.md:123 @ 3fd1431decb1013969c9ef061f8c391e715fe973
def test_agents_md_documents_functional_runtime():
    """AGENTS.md must document that functional test .generated clients import runtime directly."""
    agents_md = Path(REPO) / "AGENTS.md"
    content = agents_md.read_text()
    # Must mention the specific runtime bundle path or .generated directory
    has_runtime_client = "runtime/client.js" in content
    has_generated = ".generated" in content
    has_runtime_bundle = "runtime bundle" in content.lower()
    assert has_runtime_client or has_generated or has_runtime_bundle, \
        "AGENTS.md must document runtime/client.js, .generated dirs, or runtime bundle updates"
