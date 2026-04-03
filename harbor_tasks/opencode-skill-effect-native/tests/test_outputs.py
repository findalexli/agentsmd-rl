"""
Task: opencode-skill-effect-native
Repo: anomalyco/opencode @ 21023337fa8011568b2570a3bd49fffed842ce86
PR:   19364

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/opencode"
FILE = Path(REPO) / "packages/opencode/src/skill/index.ts"


def _read_stripped():
    """Read the file and strip comments for reliable pattern matching."""
    code = FILE.read_text()
    # Strip single-line comments
    stripped = re.sub(r"//.*$", "", code, flags=re.MULTILINE)
    # Strip multi-line comments
    stripped = re.sub(r"/\*[\s\S]*?\*/", "", stripped)
    return code, stripped


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral: Effect migration
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_loadskills_is_effect_generator():
    """loadSkills must be a native Effect generator, not an async function."""
    _, stripped = _read_stripped()
    assert not re.search(r"\basync\s+function\s+loadSkills\b", stripped), \
        "loadSkills is still declared as async function"
    assert not re.search(r"\bconst\s+loadSkills\s*=\s*async\b", stripped), \
        "loadSkills is still an async arrow/expression"
    assert re.search(r"\bloadSkills\s*=\s*Effect\.(fnUntraced|fn|gen)\b", stripped), \
        "loadSkills must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_add_helper_is_effect_generator():
    """add helper must be a native Effect generator, not async."""
    _, stripped = _read_stripped()
    assert not re.search(r"\bconst\s+add\s*=\s*async\b", stripped), \
        "add helper is still async"
    assert re.search(r"\bconst\s+add\s*=\s*Effect\.(fnUntraced|fn|gen)\b", stripped), \
        "add must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_scan_helper_is_effect_generator():
    """scan helper must be a native Effect generator, not async."""
    _, stripped = _read_stripped()
    assert not re.search(r"\bconst\s+scan\s*=\s*async\b", stripped), \
        "scan helper is still async"
    assert re.search(r"\bconst\s+scan\s*=\s*Effect\.(fnUntraced|fn|gen)\b", stripped), \
        "scan must be assigned to Effect.fnUntraced/fn/gen"


# [pr_diff] fail_to_pass
def test_static_config_facades_removed():
    """Config.get() and Config.directories() static facades must be removed.

    The fix yields Config.Service and calls methods on the instance instead.
    Tests capitalized static calls; lowercase instance calls (config.get()) are fine.
    """
    _, stripped = _read_stripped()
    assert not re.search(r"\bConfig\.get\s*\(", stripped), \
        "Static Config.get() facade still present -- yield Config.Service and use the instance"
    assert not re.search(r"\bConfig\.directories\s*\(", stripped), \
        "Static Config.directories() facade still present"


# [pr_diff] fail_to_pass
def test_effect_run_promise_removed():
    """Effect.runPromise bridge must be removed -- discovery.pull() should be yielded natively."""
    _, stripped = _read_stripped()
    assert not re.search(r"\bEffect\.runPromise\b", stripped), \
        "Effect.runPromise bridge still present -- yield* the Effect directly"


# [pr_diff] fail_to_pass
def test_monolithic_promise_wrapper_removed():
    """The monolithic Effect.promise(() => loadSkills(...)) wrapper must be removed.

    The InstanceState.make closure should call loadSkills natively via yield*.
    """
    _, stripped = _read_stripped()
    assert not re.search(r"Effect\.promise\s*\([\s\S]{0,80}loadSkills", stripped), \
        "Monolithic Effect.promise(() => loadSkills(...)) wrapper still present"


# [pr_diff] fail_to_pass
def test_layer_declares_config_and_bus_deps():
    """The layer type must declare Config.Service and Bus.Service as dependencies.

    Either via the Layer.Layer<...> type annotation or by yielding them in the body.
    """
    _, stripped = _read_stripped()
    has_config = (
        re.search(r"yield\*\s*Config\.Service", stripped)
        or re.search(r"Layer\.Layer<[^>]*Config\.Service", stripped)
    )
    has_bus = (
        re.search(r"yield\*\s*Bus\.Service", stripped)
        or re.search(r"Layer\.Layer<[^>]*Bus\.Service", stripped)
    )
    assert has_config, "Config.Service not yielded or declared in layer dependencies"
    assert has_bus, "Bus.Service not yielded or declared in layer dependencies"


# [pr_diff] fail_to_pass
def test_default_layer_provides_config_and_bus():
    """defaultLayer must provide Config and Bus layers alongside Discovery."""
    _, stripped = _read_stripped()
    # Look for Layer.provide with Config and Bus layer references near defaultLayer
    assert re.search(r"Layer\.provide\(\s*Config\.\w+", stripped), \
        "defaultLayer does not provide a Config layer"
    assert re.search(r"Layer\.provide\(\s*Bus\.\w+", stripped), \
        "defaultLayer does not provide a Bus layer"


# [pr_diff] fail_to_pass
def test_no_promise_then_chains():
    """Promise .then() chains must be replaced with Effect combinators.

    The base code uses .then((matches) => Promise.all(...)) which should become
    Effect.forEach with concurrency.
    """
    _, stripped = _read_stripped()
    assert not re.search(r"\.then\s*\(", stripped), \
        ".then() promise chain still present -- use Effect combinators instead"


# [pr_diff] fail_to_pass
def test_no_promise_all():
    """Promise.all must be replaced with Effect.forEach or Effect.all.

    The base code uses Promise.all(matches.map(...)) which should become
    Effect.forEach(matches, ..., { concurrency: \"unbounded\" }).
    """
    _, stripped = _read_stripped()
    assert not re.search(r"\bPromise\.all\b", stripped), \
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
    # Match type annotation patterns: `: any`, `as any`, `<any>`
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
