"""
Task: opencode-skill-effect-native
Repo: anomalyco/opencode @ 21023337fa8011568b2570a3bd49fffed842ce86
PR:   19364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
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
# Fail-to-pass (pr_diff) — core behavioral: Effect migration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loadskills_is_effect_generator():
    """loadSkills must be a native Effect generator, not an async function."""
    a = _get_analysis()
    assert not a["loadskills_is_async_fn"], \
        "loadSkills is still declared as async function"
    assert not a["loadskills_is_async_const"], \
        "loadSkills is still an async arrow/expression"
    assert a["loadskills_is_effect_gen"], \
        "loadSkills must be assigned to Effect.fnUntraced/fn/gen"


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
    assert not a["has_config_get_static"], \
        "Static Config.get() facade still present -- yield Config.Service and use the instance"
    assert not a["has_config_directories_static"], \
        "Static Config.directories() facade still present"


# [pr_diff] fail_to_pass
def test_effect_run_promise_removed():
    """Effect.runPromise bridge must be removed -- discovery.pull() should be yielded natively."""
    a = _get_analysis()
    assert not a["has_effect_run_promise"], \
        "Effect.runPromise bridge still present -- yield* the Effect directly"


# [pr_diff] fail_to_pass
def test_monolithic_promise_wrapper_removed():
    """The monolithic Effect.promise(() => loadSkills(...)) wrapper must be removed."""
    a = _get_analysis()
    assert not a["has_effect_promise_loadskills"], \
        "Monolithic Effect.promise(() => loadSkills(...)) wrapper still present"


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
    assert not a["has_then_chain"], \
        ".then() promise chain still present -- use Effect combinators instead"


# [pr_diff] fail_to_pass
def test_no_promise_all():
    """Promise.all must be replaced with Effect.forEach or Effect.all."""
    a = _get_analysis()
    assert not a["has_promise_all"], \
        "Promise.all still present -- use Effect.forEach or Effect.all instead"


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
    assert "Session.Event.Error" in stripped, \
        "Session.Event.Error reporting missing -- errors must still be published to the bus"


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:12 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_try_catch():
    """No try/catch blocks (AGENTS.md: 'Avoid try/catch where possible')."""
    _, stripped = _read_stripped()
    matches = re.findall(r"\btry\s*\{", stripped)
    assert len(matches) == 0, \
        f"Found {len(matches)} try/catch block(s) -- use Effect.tryPromise or Effect.catch instead"


# [agent_config] pass_to_pass — AGENTS.md:13 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_any_type():
    """No 'any' type annotations (AGENTS.md: 'Avoid using the any type')."""
    _, stripped = _read_stripped()
    any_annotations = re.findall(r":\s*any\b|as\s+any\b|<any[>,]", stripped)
    assert len(any_annotations) == 0, \
        f"Found {len(any_annotations)} 'any' type annotation(s) -- use specific types instead"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:46 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_raw_fs_imports():
    """No raw 'fs/promises' imports (packages/opencode/AGENTS.md: 'Prefer FileSystem.FileSystem instead of raw fs/promises')."""
    code, _ = _read_stripped()
    assert not re.search(r"""["']fs/promises["']""", code), \
        "Raw 'fs/promises' import found -- use FileSystem.FileSystem service instead"


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:48 @ 21023337fa8011568b2570a3bd49fffed842ce86
def test_no_raw_fetch_calls():
    """No raw fetch() calls (packages/opencode/AGENTS.md: 'Prefer HttpClient.HttpClient instead of raw fetch')."""
    _, stripped = _read_stripped()
    assert not re.search(r"\bfetch\s*\(", stripped), \
        "Raw fetch() call found -- use HttpClient.HttpClient service instead"


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
