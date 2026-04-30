"""
Task: workers-sdk-ai-search-type-generation
Repo: workers-sdk @ 4dc94fd5209d17663fac32ac99f7f20d17f1f07f
PR:   13151

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess

REPO = "/workspace/workers-sdk"
TYPE_GEN = "packages/wrangler/src/type-generation/index.ts"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_typescript_syntax():
    """Type generation file must be valid and contain expected function signatures."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');
if (!src.includes('function collectCoreBindings(')) {{
    console.error('Missing collectCoreBindings');
    process.exit(1);
}}
if (!src.includes('function collectCoreBindingsPerEnvironment(')) {{
    console.error('Missing collectCoreBindingsPerEnvironment');
    process.exit(1);
}}
console.log('Syntax OK: file readable, key functions present');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr.decode()}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_core_bindings_ai_search_namespace():
    """collectCoreBindings must generate AiSearchNamespace type for ai_search_namespaces."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');

// Isolate collectCoreBindings (ends where collectCoreBindingsPerEnvironment begins)
const coreStart = src.indexOf('function collectCoreBindings(');
const perEnvStart = src.indexOf('function collectCoreBindingsPerEnvironment(');
if (coreStart === -1 || perEnvStart === -1) {{
    console.error('Could not find function boundaries');
    process.exit(1);
}}
const coreFunc = src.substring(coreStart, perEnvStart);

// Find ai_search_namespaces handling with AiSearchNamespace type and addBinding call
const nsIdx = coreFunc.indexOf('ai_search_namespaces');
if (nsIdx === -1) {{
    console.error('collectCoreBindings does not handle ai_search_namespaces');
    process.exit(1);
}}
const nsBlock = coreFunc.substring(nsIdx, nsIdx + 600);
if (!nsBlock.includes('"AiSearchNamespace"') && !nsBlock.includes("'AiSearchNamespace'")) {{
    console.error('ai_search_namespaces not mapped to AiSearchNamespace type');
    process.exit(1);
}}
if (!nsBlock.includes('addBinding')) {{
    console.error('ai_search_namespaces block missing addBinding call');
    process.exit(1);
}}
console.log('PASS');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"collectCoreBindings missing ai_search_namespaces->AiSearchNamespace:\n"
        f"{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_core_bindings_ai_search_instance():
    """collectCoreBindings must generate AiSearchInstance type for ai_search."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');

const coreStart = src.indexOf('function collectCoreBindings(');
const perEnvStart = src.indexOf('function collectCoreBindingsPerEnvironment(');
if (coreStart === -1 || perEnvStart === -1) {{
    console.error('Could not find function boundaries');
    process.exit(1);
}}
const coreFunc = src.substring(coreStart, perEnvStart);

// Must handle ai_search (not ai_search_namespaces) with AiSearchInstance
// Look for a second occurrence or a distinct pattern like env.ai_search
const patterns = [
    /\\.ai_search\\b(?!_namespaces)/,
    /bindingType.*ai_search[^_]/,
    /["']ai_search["'](?!_namespaces)/
];
let found = false;
for (const pat of patterns) {{
    if (pat.test(coreFunc)) {{
        found = true;
        break;
    }}
}}
if (!found) {{
    console.error('collectCoreBindings does not handle ai_search bindings');
    process.exit(1);
}}
if (!coreFunc.includes('"AiSearchInstance"') && !coreFunc.includes("'AiSearchInstance'")) {{
    console.error('ai_search not mapped to AiSearchInstance type');
    process.exit(1);
}}
console.log('PASS');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"collectCoreBindings missing ai_search->AiSearchInstance:\n"
        f"{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_per_env_ai_search_namespace():
    """collectCoreBindingsPerEnvironment must generate AiSearchNamespace for ai_search_namespaces."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');

const perEnvStart = src.indexOf('function collectCoreBindingsPerEnvironment(');
if (perEnvStart === -1) {{
    console.error('Could not find collectCoreBindingsPerEnvironment');
    process.exit(1);
}}
const perEnvFunc = src.substring(perEnvStart);

// Check for ai_search_namespaces handling with AiSearchNamespace type and bindings.push
const nsIdx = perEnvFunc.indexOf('ai_search_namespaces');
if (nsIdx === -1) {{
    console.error('collectCoreBindingsPerEnvironment does not handle ai_search_namespaces');
    process.exit(1);
}}
const nsBlock = perEnvFunc.substring(nsIdx, nsIdx + 600);
if (!nsBlock.includes('"AiSearchNamespace"') && !nsBlock.includes("'AiSearchNamespace'")) {{
    console.error('ai_search_namespaces not mapped to AiSearchNamespace type');
    process.exit(1);
}}
if (!nsBlock.includes('bindings.push') && !nsBlock.includes('bindings.push(')) {{
    // Also accept addBinding pattern in case implementation differs
    if (!nsBlock.includes('addBinding')) {{
        console.error('ai_search_namespaces block missing bindings.push or addBinding call');
        process.exit(1);
    }}
}}
console.log('PASS');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"collectCoreBindingsPerEnvironment missing ai_search_namespaces->AiSearchNamespace:\n"
        f"{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_per_env_ai_search_instance():
    """collectCoreBindingsPerEnvironment must generate AiSearchInstance for ai_search."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');

const perEnvStart = src.indexOf('function collectCoreBindingsPerEnvironment(');
if (perEnvStart === -1) {{
    console.error('Could not find collectCoreBindingsPerEnvironment');
    process.exit(1);
}}
const perEnvFunc = src.substring(perEnvStart);

// Must handle ai_search (not ai_search_namespaces) with AiSearchInstance
const patterns = [
    /\\.ai_search\\b(?!_namespaces)/,
    /bindingType.*ai_search[^_]/,
    /["']ai_search["'](?!_namespaces)/
];
let found = false;
for (const pat of patterns) {{
    if (pat.test(perEnvFunc)) {{
        found = true;
        break;
    }}
}}
if (!found) {{
    console.error('collectCoreBindingsPerEnvironment does not handle ai_search');
    process.exit(1);
}}
if (!perEnvFunc.includes('"AiSearchInstance"') && !perEnvFunc.includes("'AiSearchInstance'")) {{
    console.error('ai_search not mapped to AiSearchInstance type');
    process.exit(1);
}}
console.log('PASS');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"collectCoreBindingsPerEnvironment missing ai_search->AiSearchInstance:\n"
        f"{r.stderr.decode()}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_bindings_preserved():
    """Existing binding type mappings (vpc_services -> Fetcher) must remain intact."""
    r = subprocess.run(
        ["node", "-e", f"""
const fs = require('fs');
const src = fs.readFileSync('{TYPE_GEN}', 'utf8');

// Verify existing vpc_services -> Fetcher binding in collectCoreBindings
const coreStart = src.indexOf('function collectCoreBindings(');
const perEnvStart = src.indexOf('function collectCoreBindingsPerEnvironment(');
const coreFunc = src.substring(coreStart, perEnvStart);

if (!coreFunc.includes('vpc_services') || !coreFunc.includes('"Fetcher"')) {{
    console.error('collectCoreBindings lost vpc_services -> Fetcher binding');
    process.exit(1);
}}

// Also check per-env function
const perEnvFunc = src.substring(perEnvStart);
if (!perEnvFunc.includes('vpc_services') || !perEnvFunc.includes('"Fetcher"')) {{
    console.error('collectCoreBindingsPerEnvironment lost vpc_services -> Fetcher binding');
    process.exit(1);
}}

// Verify other existing bindings still present
const requiredTypes = ['"Ai"', '"Fetcher"', '"RateLimit"'];
for (const t of requiredTypes) {{
    if (!src.includes(t)) {{
        console.error('Missing existing binding type: ' + t);
        process.exit(1);
    }}
}}
console.log('PASS: existing bindings preserved');
"""],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"Existing bindings broken:\n{r.stderr.decode()}"
    )
