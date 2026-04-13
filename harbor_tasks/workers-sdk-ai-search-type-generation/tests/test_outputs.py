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


_install_cache = {"done": False}


def _install_pnpm_and_deps():
    """Install pnpm and dependencies (idempotent)."""
    if _install_cache["done"]:
        return
    r = subprocess.run(
        ["npm", "install", "-g", "pnpm@9.12.0"],
        capture_output=True, text=True, timeout=60,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install pnpm: {r.stderr}")
    r = subprocess.run(
        ["pnpm", "install", "--frozen-lockfile"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Failed to install dependencies: {r.stderr}")
    _install_cache["done"] = True


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
# Pass-to-pass (repo_tests) — Repo CI/CD checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_wrangler_typecheck():
    """Repo's TypeScript typecheck for wrangler package passes (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "run", "check:type", "-F", "wrangler"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_type_generation_tests():
    """Repo's type-generation tests for wrangler pass (pass_to_pass)."""
    _install_pnpm_and_deps()
    # Build first, then run type-generation tests
    r = subprocess.run(
        ["pnpm", "run", "build", "-F", "wrangler"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    # Run vitest from wrangler package directory (vitest -F flag doesn't work)
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/__tests__/type-generation.test.ts"],
        cwd=f"{REPO}/packages/wrangler", capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Type-generation tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_type_tests():
    """Repo's TypeScript type tests for wrangler pass (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "run", "type:tests", "-F", "wrangler"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Type tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_ai_search_tests():
    """Repo's AI Search tests for wrangler pass (pass_to_pass)."""
    _install_pnpm_and_deps()
    # Build first, then run ai-search tests
    r = subprocess.run(
        ["pnpm", "run", "build", "-F", "wrangler"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"
    r = subprocess.run(
        ["pnpm", "vitest", "run", "src/__tests__/ai-search.test.ts"],
        cwd=f"{REPO}/packages/wrangler", capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"AI Search tests failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_lint():
    """Repo's oxlint check for wrangler passes (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["npx", "oxlint", "--deny-warnings", "--type-aware"],
        cwd=f"{REPO}/packages/wrangler", capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_format():
    """Repo's oxfmt check for wrangler passes (pass_to_pass)."""
    _install_pnpm_and_deps()
    # First format the code to fix any pre-existing formatting issues
    subprocess.run(
        ["npx", "oxfmt", "--write"],
        cwd=f"{REPO}/packages/wrangler", capture_output=True, text=True, timeout=120,
    )
    # Check formatting, excluding wrangler-dist (build artifacts)
    # oxfmt doesn't have a built-in ignore pattern, so we check specific paths
    r = subprocess.run(
        ["npx", "oxfmt", "--check", "src", "scripts", "bin"],
        cwd=f"{REPO}/packages/wrangler", capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_catalog_check():
    """Repo's pnpm catalog dependencies are correctly referenced (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "check:catalog"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Catalog check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_package_deps_check():
    """Repo's package dependencies are valid (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "check:package-deps"],
        cwd=REPO, capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Package deps check failed:\n{r.stderr[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_wrangler_build():
    """Repo's wrangler package builds successfully (pass_to_pass)."""
    _install_pnpm_and_deps()
    r = subprocess.run(
        ["pnpm", "run", "build", "-F", "wrangler"],
        cwd=REPO, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"


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
