"""
Task: nextjs-layout-segment-optimization
Repo: vercel/next.js @ 883d93c8935afb2b8124ab324a10fa36cbd7a88c
PR:   91701

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/next.js")
APP_PAGE = REPO / "packages/next/src/build/templates/app-page.ts"
LOADER_TREE = REPO / "crates/next-core/src/app_page_loader_tree.rs"
APP_RS = REPO / "crates/next-api/src/app.rs"
CHUNK_GROUP = REPO / "turbopack/crates/turbopack-core/src/module_graph/chunk_group_info.rs"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js validation script in the repo directory."""
    script = REPO / "_eval_tmp.cjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


def _node_result(code: str, timeout: int = 30) -> dict:
    """Run a Node.js script that outputs JSON and parse the result."""
    r = _run_node(code, timeout=timeout)
    assert r.returncode == 0, f"Node.js failed: {r.stderr}"
    return json.loads(r.stdout.strip().split('\n')[-1])


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests using subprocess execution
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_app_page_server_imports_have_transition():
    """Server-side imports in app-page.ts annotated with next-server-utility transition."""
    fp = json.dumps(str(APP_PAGE))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const required = [
  'server/instrumentation/utils', 'server/lib/trace/tracer', 'server/request-meta',
  'server/lib/trace/constants', 'server/app-render/interop-default',
  'server/app-render/strip-flight-headers', 'server/base-http/node',
  'server/lib/experimental/ppr', 'server/request/fallback-params',
  'server/app-render/manifests-singleton', 'server/lib/streaming-metadata',
  'shared/lib/router/utils/app-paths', 'server/lib/server-action-request-meta',
  'client/components/app-router-headers', 'shared/lib/router/utils/is-bot',
  'server/response-cache', 'lib/fallback', 'server/render-result',
  'lib/constants', 'server/stream-utils/encoded-tags',
  'server/stream-utils/node-web-streams-helper', 'server/send-payload',
  'shared/lib/no-fallback-error', 'shared/lib/size-limit',
  'server/lib/postponed-request-body', 'lib/url',
  'client/components/redirect-status-code', 'shared/lib/invariant-error',
  'lib/scheduler', 'shared/lib/router/utils/interception-routes',
  'shared/lib/router/utils/get-segment-param',
];
const importRe = /from\s+['"]([^'"]+)['"](?:\s+with\s*\{([^}]*)\})?/gs;
const specMap = {};
let m;
while ((m = importRe.exec(src)) !== null) {
  const specifier = m[1];
  const withClause = m[2] || '';
  const hasT = withClause.includes('next-server-utility');
  for (const frag of required) {
    if (specifier.includes(frag)) specMap[frag] = hasT;
  }
}
const missing = required.filter(f => !specMap[f]);
console.log(JSON.stringify({missing, missingCount: missing.length, total: required.length}));
"""
    )
    assert data['missingCount'] <= 3, (
        f"{data['missingCount']}/{data['total']} server imports missing "
        f"'next-server-utility' transition:\n  " + '\n  '.join(data['missing'][:8])
    )


# [pr_diff] fail_to_pass
def test_fillmetadata_transition_removed():
    """fillMetadataSegment import no longer has next-server-utility transition."""
    fp = json.dumps(str(LOADER_TREE))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const idx = src.indexOf('fillMetadataSegment');
if (idx === -1) {
  console.log(JSON.stringify({ok: false, error: 'fillMetadataSegment not found'}));
  process.exit(0);
}
const window = src.substring(Math.max(0, idx - 300), idx + 300);
const lines = window.split('\n');
const fillLines = [];
lines.forEach((l, i) => { if (l.includes('fillMetadataSegment')) fillLines.push(i); });
if (fillLines.length === 0) {
  console.log(JSON.stringify({ok: false, error: 'no fillMetadataSegment line'}));
  process.exit(0);
}
const centre = fillLines[0];
const neighbourhood = lines.slice(Math.max(0, centre - 3), centre + 4).join('\n');
const hasTransition = neighbourhood.includes('next-server-utility');
console.log(JSON.stringify({ok: !hasTransition}));
"""
    )
    assert data['ok'], (
        "fillMetadataSegment import still contains next-server-utility transition"
    )


# [pr_diff] fail_to_pass
def test_app_module_graphs_option_param():
    """app_module_graphs uses Option<Vc<EvaluatableAssets>> instead of separate params."""
    fp = json.dumps(str(APP_RS))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const fnPat = /fn\s+app_module_graphs\s*\(([\s\S]*?)\)\s*(?:->|\{)/;
const fnMatch = fnPat.exec(src);
if (!fnMatch) {
  console.log(JSON.stringify({ok: false, error: 'function not found'}));
  process.exit(0);
}
const sig = fnMatch[1];
const hasOldParam = sig.includes('has_layout_segments: bool');
const hasOption = sig.includes('Option<');
console.log(JSON.stringify({ok: !hasOldParam && hasOption, hasOldParam, hasOption}));
"""
    )
    assert data['ok'], (
        "app_module_graphs still has has_layout_segments: bool or missing Option parameter"
    )


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group_entry():
    """SharedMultiple variant exists in ChunkGroupEntry enum."""
    fp = json.dumps(str(CHUNK_GROUP))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const enumPat = /pub\s+enum\s+ChunkGroupEntry\s*\{([\s\S]*?)\n\}/;
const enumMatch = enumPat.exec(src);
if (!enumMatch) {
  console.log(JSON.stringify({ok: false, error: 'ChunkGroupEntry enum not found'}));
  process.exit(0);
}
console.log(JSON.stringify({ok: enumMatch[1].includes('SharedMultiple')}));
"""
    )
    assert data['ok'], "SharedMultiple variant missing from ChunkGroupEntry"


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group():
    """SharedMultiple variant exists in ChunkGroup enum."""
    fp = json.dumps(str(CHUNK_GROUP))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const enumPat = /pub\s+enum\s+ChunkGroup\s*\{([\s\S]*?)\n\}/;
const enumMatch = enumPat.exec(src);
if (!enumMatch) {
  console.log(JSON.stringify({ok: false, error: 'ChunkGroup enum not found'}));
  process.exit(0);
}
console.log(JSON.stringify({ok: enumMatch[1].includes('SharedMultiple')}));
"""
    )
    assert data['ok'], "SharedMultiple variant missing from ChunkGroup"


# [pr_diff] fail_to_pass
def test_shared_multiple_in_chunk_group_key():
    """SharedMultiple variant exists in ChunkGroupKey enum."""
    fp = json.dumps(str(CHUNK_GROUP))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const enumPat = /pub\s+enum\s+ChunkGroupKey\s*\{([\s\S]*?)\n\}/;
const enumMatch = enumPat.exec(src);
if (!enumMatch) {
  console.log(JSON.stringify({ok: false, error: 'ChunkGroupKey enum not found'}));
  process.exit(0);
}
console.log(JSON.stringify({ok: enumMatch[1].includes('SharedMultiple')}));
"""
    )
    assert data['ok'], "SharedMultiple variant missing from ChunkGroupKey"


# [pr_diff] fail_to_pass
def test_shared_multiple_pattern_matching():
    """SharedMultiple handled in pattern-match arms (entries, count, debug_str, compute)."""
    fp = json.dumps(str(CHUNK_GROUP))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const refPat = /(?:Self|ChunkGroup|ChunkGroupEntry|ChunkGroupKey)::SharedMultiple/g;
const refs = src.match(refPat) || [];
console.log(JSON.stringify({count: refs.length, ok: refs.length >= 6}));
"""
    )
    assert data['ok'], (
        f"SharedMultiple referenced only {data['count']} times — "
        "expected integration in pattern-match arms (entries, count, debug_str, etc.)"
    )


# [pr_diff] fail_to_pass
def test_route_handlers_no_empty_assets():
    """Route handlers pass None instead of EvaluatableAssets::empty() to app_module_graphs."""
    fp = json.dumps(str(APP_RS))
    data = _node_result(
        "const fs = require('fs');\n"
        f"const src = fs.readFileSync({fp}, 'utf8');\n"
        r"""
const callPat = /app_module_graphs\s*\(/g;
let match;
let found = false;
let hasEmpty = false;
while ((match = callPat.exec(src)) !== null) {
  found = true;
  const region = src.substring(match.index, match.index + 600);
  if (region.includes('EvaluatableAssets::empty()')) hasEmpty = true;
}
console.log(JSON.stringify({ok: found && !hasEmpty, found, hasEmpty}));
"""
    )
    assert data['ok'], (
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
    relative_requires = re.findall(r"""\brequire\s*\(\s*['"]\.\.?/""", src)
    assert len(relative_requires) == 0, (
        f"app-page.ts has {len(relative_requires)} relative require() call(s) — "
        "internal modules must be exported from entry-base.ts and accessed via entryBase.*"
    )


# [agent_config] pass_to_pass — AGENTS.md:398, .agents/skills/react-vendoring/SKILL.md:25
def test_no_react_server_dom_webpack_in_app_page():
    """app-page.ts must not directly import from react-server-dom-webpack/*."""
    src = APP_PAGE.read_text()
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
    assert re.search(
        r"from\s+['\"].*route-kind['\"].*with\s*\{[^}]*next-server-utility",
        src, re.DOTALL,
    ), "RouteKind import lost its next-server-utility transition"
    assert re.search(
        r"(?:import|export)\s+.*entry-base.*with\s*\{[^}]*next-server-utility",
        src, re.DOTALL,
    ), "entry-base import/export lost its next-server-utility transition"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD gates from the repo's actual test suite
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_git_status():
    """Repo is a valid git repository with expected commit checked out (pass_to_pass).

    Validates the git repository structure and that we're at the expected commit.
    """
    # Check git status works
    r = subprocess.run(
        ["git", "status", "--short"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"git status failed: {r.stderr}"

    # Check we're at the expected commit
    r2 = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r2.returncode == 0, f"git rev-parse failed: {r2.stderr}"
    commit = r2.stdout.strip()
    expected_commit = "883d93c8935afb2b8124ab324a10fa36cbd7a88c"
    assert commit == expected_commit, f"Expected commit {expected_commit}, got {commit}"


# [repo_tests] pass_to_pass
def test_repo_file_structure():
    """Repo has expected file structure for the PR changes (pass_to_pass)."""
    # Key directories must exist
    assert (REPO / "packages/next/src/build/templates").is_dir(), (
        "templates directory missing"
    )
    assert (REPO / "crates/next-core/src").is_dir(), (
        "next-core/src directory missing"
    )
    assert (REPO / "crates/next-api/src").is_dir(), (
        "next-api/src directory missing"
    )
    assert (REPO / "turbopack/crates/turbopack-core/src/module_graph").is_dir(), (
        "turbopack module_graph directory missing"
    )


# [repo_tests] pass_to_pass
def test_repo_app_page_syntax():
    """Modified app-page.ts has valid JavaScript/TypeScript syntax (pass_to_pass).

    Runs Node.js syntax check to ensure the file is syntactically valid.
    This validates the TypeScript import with syntax introduced in the PR.
    """
    r = subprocess.run(
        ["node", "--check", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"app-page.ts has syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_chunk_group_info_structure():
    """Chunk group info Rust file has expected enum structure (pass_to_pass).

    Validates the file contains the expected enum definitions and patterns
    that the PR will modify.
    """
    r = subprocess.run(
        ["grep", "-c", "pub enum ChunkGroupEntry", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "ChunkGroupEntry enum not found in chunk_group_info.rs"
    )

    r = subprocess.run(
        ["grep", "-c", "pub enum ChunkGroup", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "ChunkGroup enum not found in chunk_group_info.rs"
    )


# [repo_tests] pass_to_pass
def test_repo_next_api_structure():
    """Next API Rust file has expected app_module_graphs function (pass_to_pass).

    Validates the file contains the app_module_graphs function that the PR modifies.
    """
    r = subprocess.run(
        ["grep", "-c", "fn app_module_graphs", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "app_module_graphs function not found in app.rs"
    )

# [repo_tests] pass_to_pass
def test_repo_loader_tree_structure():
    """App page loader tree has expected metadata import pattern (pass_to_pass).

    Validates the file contains fillMetadataSegment import that the PR modifies.
    """
    r = subprocess.run(
        ["grep", "-c", "fillMetadataSegment", str(LOADER_TREE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "fillMetadataSegment not found in app_page_loader_tree.rs"
    )


# [repo_tests] pass_to_pass
def test_repo_app_page_syntax_check():
    """Repo CI: app-page.ts TypeScript syntax is valid (pass_to_pass).

    Runs Node.js syntax check to validate the template file compiles.
    This is a CI-style check similar to what the repo runs.
    """
    r = subprocess.run(
        ["node", "--check", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"app-page.ts has syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass
def test_repo_turbopack_chunk_group_structure():
    """Repo CI: Turbopack chunk_group_info.rs has expected enum structure (pass_to_pass).

    Validates the file contains expected ChunkGroupEntry, ChunkGroup, and ChunkGroupKey enums.
    This is a CI-style structural check.
    """
    # Check for ChunkGroupEntry enum
    r = subprocess.run(
        ["grep", "-c", "pub enum ChunkGroupEntry", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "ChunkGroupEntry enum not found"
    )

    # Check for ChunkGroup enum
    r = subprocess.run(
        ["grep", "-c", "pub enum ChunkGroup", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "ChunkGroup enum not found"
    )

    # Check for ChunkGroupKey enum
    r = subprocess.run(
        ["grep", "-c", "pub enum ChunkGroupKey", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "ChunkGroupKey enum not found"
    )



# [repo_tests] pass_to_pass
def test_repo_turbopack_chunk_group_file_size():
    """Repo CI: chunk_group_info.rs has substantial content (pass_to_pass).

    Validates the chunk_group_info.rs file has expected size and structure.
    This is a CI-style check for file content validation.
    """
    r = subprocess.run(
        ["wc", "-l", str(CHUNK_GROUP)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, f"wc command failed: {r.stderr}"
    line_count = int(r.stdout.strip().split()[0])
    assert line_count >= 150, (
        f"chunk_group_info.rs has {line_count} lines, expected >= 150"
    )


# [repo_tests] pass_to_pass
def test_repo_app_rs_structure():
    """Repo CI: next-api/src/app.rs has expected function structure (pass_to_pass).

    Validates the file contains app_module_graphs function with expected signature.
    """
    # Check for app_module_graphs function
    r = subprocess.run(
        ["grep", "-c", "fn app_module_graphs", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "app_module_graphs function not found in app.rs"
    )

    # Check for has_layout_segments parameter (should exist in base commit)
    r = subprocess.run(
        ["grep", "-c", "has_layout_segments", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "has_layout_segments not found in app.rs (expected in base commit)"
    )


# [repo_tests] pass_to_pass
def test_repo_next_api_client_runtime_entries():
    """Repo CI: next-api/src/app.rs has client_runtime_entries usage (pass_to_pass).

    Validates the file contains client_runtime_entries which is used by the PR changes.
    """
    r = subprocess.run(
        ["grep", "-c", "client_runtime_entries", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "client_runtime_entries not found in app.rs"
    )


# [repo_tests] pass_to_pass
def test_repo_app_page_imports_structure():
    """Repo CI: app-page.ts has expected import structure with transitions (pass_to_pass).

    Validates the template file has the expected import pattern structure.
    This is a CI-style structural check for the modified TypeScript template.
    """
    # Check for turbopack-transition annotations
    r = subprocess.run(
        ["grep", "-c", "turbopack-transition", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "turbopack-transition annotations not found in app-page.ts"
    )

    # Check for next-server-utility transition
    r = subprocess.run(
        ["grep", "-c", "next-server-utility", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "next-server-utility transition not found in app-page.ts"
    )

    # Check for entry-base import
    r = subprocess.run(
        ["grep", "-c", "entry-base", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "entry-base import not found in app-page.ts"
    )


# [repo_tests] pass_to_pass — CI: TypeScript template syntax validation
def test_repo_app_page_template_syntax():
    """Repo CI: app-page.ts has valid TypeScript syntax (pass_to_pass).

    Runs Node.js --check to validate the template file syntax.
    This matches the repo's CI approach for validating build templates.
    """
    r = subprocess.run(
        ["node", "--check", str(APP_PAGE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0, (
        f"app-page.ts template has syntax errors:\n{r.stderr[-500:]}"
    )


# [repo_tests] pass_to_pass — CI: Build template syntax validation
def test_repo_build_templates_syntax():
    """Repo CI: All build templates have valid syntax (pass_to_pass).

    Validates TypeScript syntax for all template files in the build directory.
    """
    templates = [
        REPO / "packages/next/src/build/templates/app-page.ts",
        REPO / "packages/next/src/build/templates/app-route.ts",
        REPO / "packages/next/src/build/templates/edge-app-route.ts",
        REPO / "packages/next/src/build/templates/edge-ssr-app.ts",
        REPO / "packages/next/src/build/templates/edge-ssr.ts",
        REPO / "packages/next/src/build/templates/helpers.ts",
    ]
    for template in templates:
        if template.exists():
            r = subprocess.run(
                ["node", "--check", str(template)],
                capture_output=True, text=True, timeout=30, cwd=str(REPO),
            )
            assert r.returncode == 0, (
                f"{template.name} has syntax errors:\n{r.stderr[-200:]}"
            )


# [repo_tests] pass_to_pass — CI: chunk_group_info.rs structure validation
def test_repo_chunk_group_info_compiles():
    """Repo CI: chunk_group_info.rs has valid Rust structure (pass_to_pass).

    Validates the Rust file contains syntactically correct enum definitions.
    Uses grep to verify the expected enum structure exists.
    """
    # Check for all three enum definitions
    for enum_name in ["ChunkGroupEntry", "ChunkGroup", "ChunkGroupKey"]:
        r = subprocess.run(
            ["grep", "-c", f"pub enum {enum_name}", str(CHUNK_GROUP)],
            capture_output=True, text=True, timeout=30, cwd=str(REPO),
        )
        assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
            f"{enum_name} enum not found in chunk_group_info.rs"
        )


# [repo_tests] pass_to_pass — CI: app.rs function signature validation
def test_repo_app_rs_function_signatures():
    """Repo CI: app.rs has expected function signatures (pass_to_pass).

    Validates the Rust file contains expected function signatures.
    """
    # Check for app_module_graphs function
    r = subprocess.run(
        ["grep", "-c", "fn app_module_graphs", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "app_module_graphs function not found in app.rs"
    )

    # Check for client_runtime_entries function
    r = subprocess.run(
        ["grep", "-c", "fn client_runtime_entries", str(APP_RS)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "client_runtime_entries function not found in app.rs"
    )


# [repo_tests] pass_to_pass — CI: app_page_loader_tree.rs structure
def test_repo_app_page_loader_tree_structure():
    """Repo CI: app_page_loader_tree.rs has expected structure (pass_to_pass).

    Validates the Rust file contains expected imports and patterns.
    """
    # Check for fillMetadataSegment
    r = subprocess.run(
        ["grep", "-c", "fillMetadataSegment", str(LOADER_TREE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "fillMetadataSegment not found in app_page_loader_tree.rs"
    )

    # Check for AppPageLoaderTreeBuilder
    r = subprocess.run(
        ["grep", "-c", "AppPageLoaderTreeBuilder", str(LOADER_TREE)],
        capture_output=True, text=True, timeout=30, cwd=str(REPO),
    )
    assert r.returncode == 0 and int(r.stdout.strip()) > 0, (
        "AppPageLoaderTreeBuilder not found in app_page_loader_tree.rs"
    )
