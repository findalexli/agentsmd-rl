"""
Task: prisma-fixclient-apply-result-extensions-for
Repo: prisma @ 3fd1431decb1013969c9ef061f8c391e715fe973
PR:   prisma/prisma#29218

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"
RESOLVE_MODULE = "packages/client/src/runtime/core/extensions/resolve-result-extension-context.ts"
GET_PRISMA = "packages/client/src/runtime/getPrismaClient.ts"


def _transpile_resolve_module():
    """Transpile the resolve module TS -> CJS via esbuild, stubbing type-only imports."""
    src = Path(REPO) / RESOLVE_MODULE
    if not src.exists():
        return None
    r = subprocess.run(
        ["esbuild", str(src), "--format=cjs", "--platform=node",
         "--outfile=/tmp/resolve-ctx.cjs"],
        capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return None
    # Stub out type-only requires (RuntimeDataModel, JsArgs are not used at runtime)
    content = Path("/tmp/resolve-ctx.cjs").read_text()
    content = re.sub(r'require\([^)]+\)', '({})', content)
    Path("/tmp/resolve-ctx.cjs").write_text(content)
    return "/tmp/resolve-ctx.cjs"


def _run_node(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["node", "-e", script],
        capture_output=True, text=True, timeout=15,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must be valid syntax (esbuild can parse them)."""
    src = Path(REPO) / RESOLVE_MODULE
    assert src.exists(), f"{RESOLVE_MODULE} must exist"
    r = subprocess.run(
        ["esbuild", str(src), "--format=cjs", "--platform=node",
         "--outfile=/tmp/syntax-check.cjs"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"TypeScript syntax error:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_resolve_empty_datapath_returns_root():
    """Empty dataPath must return the root model context unchanged."""
    mod = _transpile_resolve_module()
    assert mod, "Could not transpile resolve module"
    r = _run_node(
        f"const {{ resolveResultExtensionContext }} = require('{mod}');\n"
        "const ctx = resolveResultExtensionContext({\n"
        "  dataPath: [],\n"
        "  modelName: 'User',\n"
        "  args: { where: { id: '1' } },\n"
        "  runtimeDataModel: { models: {}, types: {} },\n"
        "});\n"
        "if (ctx.modelName !== 'User') throw new Error('Expected User, got ' + ctx.modelName);\n"
        "if (ctx.args.where.id !== '1') throw new Error('Args mismatch');\n"
        "console.log('PASS');\n"
    )
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"Empty dataPath test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_resolve_one_hop_select():
    """One-hop ['select', 'posts'] dataPath must resolve to the related Post model."""
    mod = _transpile_resolve_module()
    assert mod, "Could not transpile resolve module"
    r = _run_node(
        f"const {{ resolveResultExtensionContext }} = require('{mod}');\n"
        "const datamodel = {\n"
        "  models: {\n"
        "    User: { fields: [\n"
        "      { kind: 'object', name: 'posts', type: 'Post', relationName: 'R1', isList: true },\n"
        "    ] },\n"
        "    Post: { fields: [] },\n"
        "  },\n"
        "  types: {},\n"
        "};\n"
        "const ctx = resolveResultExtensionContext({\n"
        "  dataPath: ['select', 'posts'],\n"
        "  modelName: 'User',\n"
        "  args: { select: { posts: { select: { id: true } } } },\n"
        "  runtimeDataModel: datamodel,\n"
        "});\n"
        "if (ctx.modelName !== 'Post') throw new Error('Expected Post, got ' + ctx.modelName);\n"
        "if (!ctx.args || !ctx.args.select || !ctx.args.select.id) throw new Error('Args not resolved');\n"
        "console.log('PASS');\n"
    )
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"One-hop test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_resolve_multi_hop():
    """Multi-hop dataPath must traverse through multiple relation fields."""
    mod = _transpile_resolve_module()
    assert mod, "Could not transpile resolve module"
    r = _run_node(
        f"const {{ resolveResultExtensionContext }} = require('{mod}');\n"
        "const datamodel = {\n"
        "  models: {\n"
        "    User: { fields: [\n"
        "      { kind: 'object', name: 'posts', type: 'Post', relationName: 'R1' },\n"
        "    ] },\n"
        "    Post: { fields: [\n"
        "      { kind: 'object', name: 'author', type: 'User', relationName: 'R2' },\n"
        "    ] },\n"
        "  },\n"
        "  types: {},\n"
        "};\n"
        "const ctx = resolveResultExtensionContext({\n"
        "  dataPath: ['select', 'posts', 'select', 'author'],\n"
        "  modelName: 'User',\n"
        "  args: { select: { posts: { select: { author: { select: { id: true } } } } } },\n"
        "  runtimeDataModel: datamodel,\n"
        "});\n"
        "if (ctx.modelName !== 'User') throw new Error('Expected User at end, got ' + ctx.modelName);\n"
        "if (!ctx.args.select || !ctx.args.select.id) throw new Error('Args not resolved to leaf');\n"
        "console.log('PASS');\n"
    )
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"Multi-hop test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_resolve_keyword_named_relation():
    """Relation fields named 'select' or 'include' must not be confused with selectors."""
    mod = _transpile_resolve_module()
    assert mod, "Could not transpile resolve module"
    r = _run_node(
        f"const {{ resolveResultExtensionContext }} = require('{mod}');\n"
        "const datamodel = {\n"
        "  models: {\n"
        "    Source: { fields: [\n"
        "      { kind: 'object', name: 'select', type: 'Target', relationName: 'R1', isList: true },\n"
        "    ] },\n"
        "    Target: { fields: [] },\n"
        "  },\n"
        "  types: {},\n"
        "};\n"
        "const ctx = resolveResultExtensionContext({\n"
        "  dataPath: ['select', 'select'],\n"
        "  modelName: 'Source',\n"
        "  args: { select: { select: true } },\n"
        "  runtimeDataModel: datamodel,\n"
        "});\n"
        "if (ctx.modelName !== 'Target') throw new Error('Expected Target, got ' + ctx.modelName);\n"
        "console.log('PASS');\n"
    )
    assert r.returncode == 0 and "PASS" in r.stdout, (
        f"Keyword relation test failed:\nstdout: {r.stdout}\nstderr: {r.stderr}"
    )


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config edit (config_edit) — AGENTS.md documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
