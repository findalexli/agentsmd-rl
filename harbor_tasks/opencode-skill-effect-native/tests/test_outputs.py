"""
Task: opencode-skill-effect-native
Repo: anomalyco/opencode @ 21023337fa8011568b2570a3bd49fffed842ce86
PR:   19364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import os
import re
from pathlib import Path

REPO = "/workspace/opencode"
FILE = Path(REPO) / "packages/opencode/src/skill/index.ts"

# ---------------------------------------------------------------------------
# Node.js analysis script — executed once via subprocess, result cached
# ---------------------------------------------------------------------------
_ANALYSIS_JS = r"""
import { readFileSync } from 'node:fs';

const code = readFileSync('packages/opencode/src/skill/index.ts', 'utf8');
// Strip single-line and multi-line comments for reliable matching
const s = code.replace(/\/\/.*$/gm, '').replace(/\/\*[\s\S]*?\*\//g, '');

const result = {
  // Effect generator checks
  add_is_async: /\bconst\s+add\s*=\s*async\b/.test(s),
  add_is_effect_gen: /\bconst\s+add\s*=\s*Effect\.(fnUntraced|fn|gen)\b/.test(s),

  scan_is_async: /\bconst\s+scan\s*=\s*async\b/.test(s),
  scan_is_effect_gen: /\bconst\s+scan\s*=\s*Effect\.(fnUntraced|fn|gen)\b/.test(s),

  loadskills_is_async_fn: /\basync\s+function\s+loadSkills\b/.test(s),
  loadskills_is_async_const: /\bconst\s+loadSkills\s*=\s*async\b/.test(s),
  loadskills_is_effect_gen: /\bloadSkills\s*=\s*Effect\.(fnUntraced|fn|gen)\b/.test(s),

  // Static facade checks
  has_config_get_static: /\bConfig\.get\s*\(/.test(s),
  has_config_directories_static: /\bConfig\.directories\s*\(/.test(s),

  // Promise bridge checks
  has_effect_run_promise: /\bEffect\.runPromise\b/.test(s),
  has_effect_promise_loadskills: /Effect\.promise\s*\([\s\S]{0,80}loadSkills/.test(s),
  has_then_chain: /\.then\s*\(/.test(s),
  has_promise_all: /\bPromise\.all\b/.test(s),

  // Layer dependency checks
  yields_config_service: /yield\*\s*Config\.Service/.test(s),
  layer_type_has_config: /Layer\.Layer<[^>]*Config\.Service/.test(s),
  yields_bus_service: /yield\*\s*Bus\.Service/.test(s),
  layer_type_has_bus: /Layer\.Layer<[^>]*Bus\.Service/.test(s),

  // defaultLayer checks
  provides_config_layer: /Layer\.provide\(\s*Config\.\w+/.test(s),
  provides_bus_layer: /Layer\.provide\(\s*Bus\.\w+/.test(s),
};

console.log(JSON.stringify(result));
"""

_cached_analysis = None


def _get_analysis():
    """Run Node.js analysis of skill/index.ts via subprocess; cache the result."""
    global _cached_analysis
    if _cached_analysis is not None:
        return _cached_analysis
    script = Path(REPO) / "_eval_analysis.mjs"
    script.write_text(_ANALYSIS_JS)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Node analysis failed: {r.stderr}"
        _cached_analysis = json.loads(r.stdout)
    finally:
        script.unlink(missing_ok=True)
    return _cached_analysis


def _read_stripped():
    """Read the file and strip comments for reliable pattern matching."""
    code = FILE.read_text()
    stripped = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    return code, stripped


# ---------------------------------------------------------------------------
# Behavioral module loader — mocks all external deps and executes the module
# ---------------------------------------------------------------------------

_MOCK_LOADER_JS = r"""
const EFFECT_SRC = `
function makeIter(v) { return { [Symbol.iterator]: function*() { yield v; } }; }
globalThis._effectTracker = { fnUntraced: 0, fn: 0, gen: 0 };
export const Effect = {
  fnUntraced: (fn) => { globalThis._effectTracker.fnUntraced++; return Object.assign((...a) => makeIter(undefined), { _tag: "fnUntraced" }); },
  fn: (name) => (fn) => { globalThis._effectTracker.fn++; return Object.assign((...a) => makeIter(undefined), { _tag: "fn", _name: name }); },
  gen: (fn) => { globalThis._effectTracker.gen++; return makeIter(undefined); },
  tryPromise: () => ({ pipe: (...fns) => fns.reduce((v,f) => f ? f(v) : v, makeIter(undefined)) }),
  promise: () => makeIter(undefined),
  catch: (fn) => (v) => v != null ? v : makeIter(undefined),
  forEach: () => makeIter(undefined),
  die: () => makeIter(undefined),
  succeed: (v) => makeIter(v),
  all: (...a) => makeIter(a),
  runPromise: () => Promise.resolve(undefined),
};
export const Layer = {
  effect: (svc, eff) => {
    const l = { _tag: "Layer", _provides: [] };
    l.pipe = (...fns) => fns.reduce((v,f) => f(v), l);
    return l;
  },
  provide: (dep) => (layer) => { if(layer && layer._provides) layer._provides.push(dep); return layer; },
};
export const ServiceMap = { Service: function() { return function(name) { return class { static of(impl) { return impl; } }; }; } };
`;

const GENERIC_SRC = `
export const Bus = { Interface: {}, Service: { [Symbol.iterator]: function*() { yield { publish: () => ({ [Symbol.iterator]: function*() { yield; } }) }; } }, publish: () => {}, layer: { _tag: "BusLayer" } };
export const Config = { Interface: {}, Service: { [Symbol.iterator]: function*() { yield { get: () => ({ [Symbol.iterator]: function*() { yield {}; } }), directories: () => ({ [Symbol.iterator]: function*() { yield []; } }) }; } }, get: async () => ({}), directories: async () => [], defaultLayer: { _tag: "ConfigLayer" } };
export const Discovery = { Interface: {}, Service: { [Symbol.iterator]: function*() { yield { pull: () => ({ [Symbol.iterator]: function*() { yield []; } }) }; } }, defaultLayer: { _tag: "DiscoveryLayer" } };
export const InstanceState = { make: (fn) => ({ [Symbol.iterator]: function*() { yield {}; } }), get: (s) => ({ [Symbol.iterator]: function*() { yield { skills: {}, dirs: new Set() }; } }) };
export const makeRuntime = (svc, layer) => ({ runPromise: (fn) => Promise.resolve(fn({ get: async()=>undefined, all: async()=>[], dirs: async()=>[], available: async()=>[] })) });
export const Flag = { OPENCODE_DISABLE_EXTERNAL_SKILLS: true };
export const Global = { Path: { home: "/tmp" } };
export const Permission = { evaluate: () => ({ action: "allow" }) };
export const Filesystem = { isDir: async () => false, up: async function*() {} };
export const ConfigMarkdown = { parse: async () => ({ data: { name: "test", description: "test" }, content: "" }), FrontmatterError: { isInstance: () => false } };
export const Glob = { scan: async () => [] };
export const Log = { create: () => ({ info: ()=>{}, warn: ()=>{}, error: ()=>{} }) };
export const NamedError = { create: (name, schema) => class E { constructor(d) { this.d = d; } static isInstance() { return false; } }, Unknown: class { constructor(d) { this.d = d; } toObject() { return {}; } } };
export default {};
`;

const ZOD_SRC = `
const handler = { get: (t,p) => {
  if (typeof p === "symbol") return Reflect.get(t,p);
  return function(...a) { return new Proxy({ pick: () => ({ safeParse: () => ({ success: true, data: {} }) }), safeParse: () => ({ success: true, data: {} }) }, handler); };
}};
const z = new Proxy({}, handler);
export default z;
`;

export async function resolve(specifier, context, next) {
  if (specifier.startsWith("node:") || specifier === "os" || specifier === "path" || specifier === "url"
      || specifier.startsWith("file:") || specifier.startsWith("/")) {
    return next(specifier, context);
  }
  if (specifier === "effect") return { url: "mock://effect", shortCircuit: true };
  if (specifier === "zod") return { url: "mock://zod", shortCircuit: true };
  return { url: "mock://generic", shortCircuit: true };
}

export async function load(url, context, next) {
  if (url === "mock://effect") return { format: "module", source: EFFECT_SRC, shortCircuit: true };
  if (url === "mock://zod") return { format: "module", source: ZOD_SRC, shortCircuit: true };
  if (url === "mock://generic") return { format: "module", source: GENERIC_SRC, shortCircuit: true };
  return next(url, context);
}
"""

_BEHAVIORAL_TEST_JS = r"""
try {
  const mod = await import("/workspace/opencode/packages/opencode/src/skill/index.ts");
  const Skill = mod.Skill;
  const tracker = globalThis._effectTracker || { fnUntraced: 0, fn: 0, gen: 0 };
  const results = {
    has_skill: !!Skill,
    has_layer: !!Skill?.layer,
    has_default_layer: !!Skill?.defaultLayer,
    effect_fnUntraced_calls: tracker.fnUntraced,
    effect_fn_calls: tracker.fn,
    effect_gen_calls: tracker.gen,
  };
  if (Skill?.defaultLayer?._provides) {
    const p = Skill.defaultLayer._provides;
    results.provides_count = p.length;
    results.has_discovery_layer = p.some(x => x?._tag === "DiscoveryLayer");
    results.has_config_layer = p.some(x => x?._tag === "ConfigLayer");
    results.has_bus_layer = p.some(x => x?._tag === "BusLayer");
  } else {
    results.provides_count = 0;
    results.has_config_layer = false;
    results.has_bus_layer = false;
  }
  process.stdout.write(JSON.stringify(results) + "\n");
} catch(e) {
  process.stderr.write("ERROR: " + e.message + "\n");
  process.exit(1);
}
"""

_cached_behavioral = None


def _get_behavioral():
    """Execute module with mocked deps via Node.js subprocess; cache the result."""
    global _cached_behavioral
    if _cached_behavioral is not None:
        return _cached_behavioral
    loader = Path(REPO) / "_eval_mock_loader.mjs"
    test_script = Path(REPO) / "_eval_behavioral_test.mjs"
    loader.write_text(_MOCK_LOADER_JS)
    test_script.write_text(_BEHAVIORAL_TEST_JS)
    try:
        r = subprocess.run(
            ["node", "--experimental-transform-types", "--no-warnings",
             "--loader", str(loader), str(test_script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Module execution failed: {r.stderr}"
        _cached_behavioral = json.loads(r.stdout.strip())
    finally:
        loader.unlink(missing_ok=True)
        test_script.unlink(missing_ok=True)
    return _cached_behavioral


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral: module execution with mocked deps
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_behavioral_helpers_are_effect_generators():
    """Execute module: Effect.fnUntraced must be called for add/scan/loadSkills helpers."""
    data = _get_behavioral()
    assert data["has_skill"], "Skill namespace not found in module exports"
    assert data["effect_fnUntraced_calls"] >= 3, \
        f"Expected >= 3 Effect.fnUntraced calls (add, scan, loadSkills), got {data['effect_fnUntraced_calls']}"


# [pr_diff] fail_to_pass
def test_behavioral_default_layer_provides_config_and_bus():
    """Execute module: defaultLayer must provide Config and Bus layers at runtime."""
    data = _get_behavioral()
    assert data["provides_count"] >= 3, \
        f"Expected >= 3 layer provides (Discovery + Config + Bus), got {data['provides_count']}"
    assert data["has_config_layer"], "defaultLayer does not provide Config layer at runtime"
    assert data["has_bus_layer"], "defaultLayer does not provide Bus layer at runtime"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — structural: Effect migration patterns
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loadskills_is_effect_generator():
    """loadSkills must be a native Effect generator, not an async function."""
    a = _get_analysis()
    assert not a["loadskills_is_async_fn"],         "loadSkills is still declared as async function"
    assert not a["loadskills_is_async_const"],         "loadSkills is still an async arrow/expression"
    assert a["loadskills_is_effect_gen"],         "loadSkills must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_add_helper_is_effect_generator():
    """add helper must be a native Effect generator, not async."""
    a = _get_analysis()
    assert not a["add_is_async"], "add helper is still async"
    assert a["add_is_effect_gen"], "add must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_scan_helper_is_effect_generator():
    """scan helper must be a native Effect generator, not async."""
    a = _get_analysis()
    assert not a["scan_is_async"], "scan helper is still async"
    assert a["scan_is_effect_gen"], "scan must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_static_config_facades_removed():
    """Config.get() and Config.directories() static facades must be removed."""
    a = _get_analysis()
    assert not a["has_config_get_static"],         "Static Config.get() facade still present -- yield Config.Service and use the instance"
    assert not a["has_config_directories_static"],         "Static Config.directories() facade still present"


# [pr_diff] fail_to_pass
def test_effect_run_promise_removed():
    """Effect.runPromise bridge must be removed -- discovery.pull() should be yielded natively."""
    a = _get_analysis()
    assert not a["has_effect_run_promise"],         "Effect.runPromise bridge still present -- yield* the Effect directly"


# [pr_diff] fail_to_pass
def test_monolithic_promise_wrapper_removed():
    """The monolithic Effect.promise(() => loadSkills(...)) wrapper must be removed."""
    a = _get_analysis()
    assert not a["has_effect_promise_loadskills"],         "Monolithic Effect.promise(() => loadSkills(...)) wrapper still present"


# [pr_diff] fail_to_pass
def test_layer_declares_config_and_bus_deps():
    """The layer type must declare Config.Service and Bus.Service as dependencies."""
    a = _get_analysis()
    has_config = a["yields_config_service"] or a["layer_type_has_config"]
    has_bus = a["yields_bus_service"] or a["layer_type_has_bus"]
    assert has_config, "Config.Service not yielded or declared in layer dependencies"
    assert has_bus, "Bus.Service not yielded or declared in layer dependencies"


# [pr_diff] fail_to_pass
def test_default_layer_provides_config_and_bus():
    """defaultLayer must provide Config and Bus layers alongside Discovery."""
    a = _get_analysis()
    assert a["provides_config_layer"], "defaultLayer does not provide a Config layer"
    assert a["provides_bus_layer"], "defaultLayer does not provide a Bus layer"


# [pr_diff] fail_to_pass
def test_no_promise_then_chains():
    """Promise .then() chains must be replaced with Effect combinators."""
    a = _get_analysis()
    assert not a["has_then_chain"],         ".then() promise chain still present -- use Effect combinators instead"


# [pr_diff] fail_to_pass
def test_no_promise_all():
    """Promise.all must be replaced with Effect.forEach or Effect.all."""
    a = _get_analysis()
    assert not a["has_promise_all"],         "Promise.all still present -- use Effect.forEach or Effect.all instead"


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_core_patterns_preserved():
    """Core skill discovery patterns must be preserved: SKILL.md, InstanceState, Skill.state."""
    _, stripped = _read_stripped()
    assert "SKILL.md" in stripped, "SKILL.md pattern reference missing"
    assert "InstanceState" in stripped, "InstanceState usage missing"
    assert re.search(r"Skill\.state", stripped), "Skill.state identifier missing"


# [pr_diff] pass_to_pass
def test_error_reporting_preserved():
    """Session.Event.Error reporting must be preserved in the error handling path."""
    _, stripped = _read_stripped()
    assert "Session.Event.Error" in stripped,         "Session.Event.Error reporting missing -- errors must still be published to the bus"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:12 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_try_catch():
    """No try/catch blocks (AGENTS.md: 'Avoid try/catch where possible')."""
    _, stripped = _read_stripped()
    matches = re.findall(r"\btry\s*\{", stripped)
    assert len(matches) == 0,         f"Found {len(matches)} try/catch block(s) -- use Effect.tryPromise or Effect.catch instead"


# [agent_config] pass_to_pass — AGENTS.md:13 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_any_type():
    """No 'any' type annotations (AGENTS.md: 'Avoid using the any type')."""
    _, stripped = _read_stripped()
    any_annotations = re.findall(r":\s*any\b|as\s+any\b|<any[>,]", stripped)
    assert len(any_annotations) == 0,         f"Found {len(any_annotations)} 'any' type annotation(s) -- use specific types instead"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:46 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_raw_fs_imports():
    """No raw 'fs/promises' imports (packages/opencode/AGENTS.md: 'Prefer FileSystem.FileSystem instead of raw fs/promises')."""
    code, _ = _read_stripped()
    assert not re.search(r"""["']fs/promises["']""", code),         "Raw 'fs/promises' import found -- use FileSystem.FileSystem service instead"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:48 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_raw_fetch_calls():
    """No raw fetch() calls (packages/opencode/AGENTS.md: 'Prefer HttpClient.HttpClient instead of raw fetch')."""
    _, stripped = _read_stripped()
    assert not re.search(r"\bfetch\s*\(", stripped),         "Raw fetch() call found -- use HttpClient.HttpClient service instead"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Modified file must retain substantial logic, not be a stub."""
    code = FILE.read_text()
    lines = code.strip().splitlines()
    assert len(lines) >= 100, f"File too short ({len(lines)} lines) -- likely stubbed"
    decls = re.findall(r"\b(function\*?|const|let)\s+\w+", code)
    assert len(decls) >= 5, f"Too few declarations ({len(decls)}) -- likely stubbed"
    assert "export" in code, "No exports found -- file likely gutted"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — CI/CD regression checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_syntax_skill_index():
    """Syntax check skill/index.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/src/skill/index.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_discovery_test():
    """Syntax check test/skill/discovery.test.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/skill/discovery.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_skill_test():
    """Syntax check test/skill/skill.test.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/skill/skill.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_tool_skill_test():
    """Syntax check test/tool/skill.test.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/test/tool/skill.test.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"

# [repo_tests] pass_to_pass
def test_repo_syntax_skill_discovery():
    """Syntax check skill/discovery.ts — dependency of skill/index.ts (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--check", "--experimental-strip-types", "packages/opencode/src/skill/discovery.ts"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"Syntax check failed:\n{r.stderr}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_prepare():
    """pass_to_pass | CI job 'build-electron' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_electron_build():
    """pass_to_pass | CI job 'build-electron' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun run build'], cwd=os.path.join(REPO, 'packages/desktop-electron'),
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")