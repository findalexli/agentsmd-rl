"""
Task: opencode-file-watcher-effectify
Repo: anomalyco/opencode @ d4694d058cc590b0f05261a04460034d2fa8541d
PR:   #17827

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/opencode"

WATCHER = Path(REPO) / "packages/opencode/src/file/watcher.ts"
INSTANCES = Path(REPO) / "packages/opencode/src/effect/instances.ts"
FLAG = Path(REPO) / "packages/opencode/src/flag/flag.ts"
BOOTSTRAP = Path(REPO) / "packages/opencode/src/project/bootstrap.ts"
INSTANCE = Path(REPO) / "packages/opencode/src/project/instance.ts"
PTY = Path(REPO) / "packages/opencode/src/pty/index.ts"
AGENTS_MD = Path(REPO) / "packages/opencode/AGENTS.md"


# ---------------------------------------------------------------------------
# Node.js analysis helper — validates code structure via subprocess
# ---------------------------------------------------------------------------

_analysis_cache = None

ANALYSIS_SCRIPT = r"""
const fs = require('fs');
const results = {};

// --- watcher.ts ---
const watcher = fs.readFileSync('packages/opencode/src/file/watcher.ts', 'utf8');
const stripped = watcher.replace(/\/\*[\s\S]*?\*\//g, '').replace(/(?<![:\/"'\\])\/\/[^\n]*/g, '');

// FileWatcherService is a class extending ServiceMap.Service
results.hasServiceClass = /class\s+FileWatcherService\s+extends\s+ServiceMap\.Service/.test(stripped);
results.hasStaticLayer = /static\s+readonly\s+layer\s*=/.test(stripped);
results.hasServiceTag = /@opencode\/FileWatcher/.test(stripped);
results.usesServiceOf = /FileWatcherService\.of\s*\(/.test(stripped);
results.usesEffectGen = /Effect\.gen\s*\(\s*function\s*\*/.test(stripped);
results.usesEffectAddFinalizer = /Effect\.addFinalizer/.test(stripped);
results.usesInstanceBind = /Instance\.bind\s*\(/.test(stripped);
results.usesInstanceContext = /yield\s*\*\s*InstanceContext/.test(stripped);
results.importsEffect = /import\s*\{[^}]*\bEffect\b[^}]*\}\s*from\s*["']effect["']/.test(stripped);
results.importsServiceMap = /import\s*\{[^}]*\bServiceMap\b[^}]*\}\s*from\s*["']effect["']/.test(stripped);

// FileWatcher.Event still exported (public API preserved)
results.fileWatcherEventExported = /export\s+const\s+Event\s*=/.test(stripped);
results.fileWatcherNamespaceExists = /export\s+namespace\s+FileWatcher\b/.test(stripped);

// Old imperative init() pattern gone
results.hasOldInit = /export\s+function\s+init\s*\(\s*\)/.test(stripped);
results.usesInstanceState = /Instance\.state\s*\(/.test(stripped);

// --- flag.ts ---
const flag = fs.readFileSync('packages/opencode/src/flag/flag.ts', 'utf8');

// Extract lines around OPENCODE_EXPERIMENTAL_FILEWATCHER
const fwMatch = flag.match(/OPENCODE_EXPERIMENTAL_FILEWATCHER[\s\S]{0,300}/);
results.flagFwUsesConfigBoolean = fwMatch ? /Config\.boolean\s*\(\s*["']OPENCODE_EXPERIMENTAL_FILEWATCHER["']/.test(fwMatch[0]) : false;
results.flagFwUsesTruthy = fwMatch ? /truthy\s*\(\s*["']OPENCODE_EXPERIMENTAL_FILEWATCHER["']/.test(fwMatch[0]) : false;

const dfwMatch = flag.match(/OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER[\s\S]{0,300}/);
results.flagDfwUsesConfigBoolean = dfwMatch ? /Config\.boolean\s*\(\s*["']OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER["']/.test(dfwMatch[0]) : false;
results.flagDfwUsesTruthy = dfwMatch ? /truthy\s*\(\s*["']OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER["']/.test(dfwMatch[0]) : false;

results.flagImportsConfig = /import\s*\{[^}]*\bConfig\b[^}]*\}\s*from\s*["']effect["']/.test(flag);

// --- instance.ts ---
const instance = fs.readFileSync('packages/opencode/src/project/instance.ts', 'utf8');
results.instanceHasBind = /bind\s*[<(]/.test(instance) && /context\.use\s*\(\s*\)/.test(instance) && /context\.provide/.test(instance);

// --- pty/index.ts ---
const pty = fs.readFileSync('packages/opencode/src/pty/index.ts', 'utf8');
results.ptyUsesInstanceBind = /Instance\.bind\s*\(/.test(pty);
// Count how many Instance.bind calls (should be at least 2: onData + onExit)
results.ptyInstanceBindCount = (pty.match(/Instance\.bind\s*\(/g) || []).length;

// --- bootstrap.ts ---
const bootstrap = fs.readFileSync('packages/opencode/src/project/bootstrap.ts', 'utf8');
results.bootstrapImportsService = /FileWatcherService/.test(bootstrap);
results.bootstrapUsesRunPromise = /runPromiseInstance/.test(bootstrap);
results.bootstrapOldInit = /FileWatcher\.init\s*\(\s*\)/.test(bootstrap);

// --- instances.ts ---
const instances = fs.readFileSync('packages/opencode/src/effect/instances.ts', 'utf8');
results.instancesHasFileWatcher = /FileWatcherService/.test(instances);
results.instancesInUnion = /InstanceServices\s*=[\s\S]*?FileWatcherService/.test(instances);
results.instancesInLayer = /Layer\.fresh\s*\(\s*FileWatcherService\.layer\s*\)/.test(instances);

console.log(JSON.stringify(results));
"""


def _get_analysis():
    """Run Node.js analysis script and cache result."""
    global _analysis_cache
    if _analysis_cache is not None:
        return _analysis_cache
    script = Path(REPO) / "_eval_analysis.cjs"
    script.write_text(ANALYSIS_SCRIPT)
    try:
        r = subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Analysis script failed: {r.stderr}"
        _analysis_cache = json.loads(r.stdout.strip())
        return _analysis_cache
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavior tests via Node.js subprocess
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_watcher_is_effect_service():
    """FileWatcherService must be a class extending ServiceMap.Service with static layer."""
    a = _get_analysis()
    assert a["hasServiceClass"], (
        "FileWatcherService class extending ServiceMap.Service not found in watcher.ts"
    )
    assert a["hasStaticLayer"], (
        "FileWatcherService missing 'static readonly layer'"
    )
    assert a["hasServiceTag"], (
        "FileWatcherService missing '@opencode/FileWatcher' service tag"
    )
    assert a["importsServiceMap"], (
        "ServiceMap not imported from 'effect'"
    )


# [pr_diff] fail_to_pass
def test_instance_bind_exists():
    """Instance must have a bind() method that captures and restores ALS context."""
    a = _get_analysis()
    assert a["instanceHasBind"], (
        "Instance.bind not found or doesn't use context.use() + context.provide()"
    )


# [pr_diff] fail_to_pass
def test_flags_config_boolean():
    """Watcher flags must use Config.boolean() from effect, not truthy()."""
    a = _get_analysis()
    assert a["flagImportsConfig"], "Config not imported from 'effect' in flag.ts"
    assert a["flagFwUsesConfigBoolean"], (
        "OPENCODE_EXPERIMENTAL_FILEWATCHER doesn't use Config.boolean()"
    )
    assert not a["flagFwUsesTruthy"], (
        "OPENCODE_EXPERIMENTAL_FILEWATCHER still uses truthy()"
    )
    assert a["flagDfwUsesConfigBoolean"], (
        "OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER doesn't use Config.boolean()"
    )
    assert not a["flagDfwUsesTruthy"], (
        "OPENCODE_EXPERIMENTAL_DISABLE_FILEWATCHER still uses truthy()"
    )


# [pr_diff] fail_to_pass
def test_pty_uses_instance_bind():
    """Pty onData and onExit callbacks must be wrapped with Instance.bind()."""
    a = _get_analysis()
    assert a["ptyUsesInstanceBind"], "Instance.bind() not used in pty/index.ts"
    assert a["ptyInstanceBindCount"] >= 2, (
        f"Expected at least 2 Instance.bind() calls in pty (onData + onExit), "
        f"found {a['ptyInstanceBindCount']}"
    )


# [pr_diff] fail_to_pass
def test_bootstrap_uses_service():
    """Bootstrap must import FileWatcherService and use runPromiseInstance, not FileWatcher.init()."""
    a = _get_analysis()
    assert a["bootstrapImportsService"], (
        "bootstrap.ts doesn't import FileWatcherService"
    )
    assert a["bootstrapUsesRunPromise"], (
        "bootstrap.ts doesn't use runPromiseInstance()"
    )
    assert not a["bootstrapOldInit"], (
        "bootstrap.ts still calls FileWatcher.init()"
    )


# [pr_diff] fail_to_pass
def test_instances_registers_service():
    """FileWatcherService must be added to InstanceServices union and Layer.mergeAll."""
    a = _get_analysis()
    assert a["instancesHasFileWatcher"], (
        "FileWatcherService not found in instances.ts"
    )
    assert a["instancesInUnion"], (
        "FileWatcherService not in InstanceServices type union"
    )
    assert a["instancesInLayer"], (
        "Layer.fresh(FileWatcherService.layer) not in Layer.mergeAll"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_agents_md_effect_callback():
    """AGENTS.md must document the Effect.callback pattern (renamed from Effect.async)."""
    content = AGENTS_MD.read_text()
    assert "Effect.callback" in content, (
        "AGENTS.md doesn't mention Effect.callback"
    )
    assert "Effect.async" in content, (
        "AGENTS.md should mention the old Effect.async name for context"
    )


# [pr_diff] fail_to_pass
def test_agents_md_instance_scoped_services():
    """AGENTS.md must document the instance-scoped Effect services pattern."""
    content = AGENTS_MD.read_text().lower()
    assert "instance" in content and "service" in content, (
        "AGENTS.md doesn't mention instance-scoped services"
    )
    # Must describe the ServiceMap.Service + static layer pattern
    raw = AGENTS_MD.read_text()
    assert "ServiceMap.Service" in raw or "static readonly layer" in raw, (
        "AGENTS.md should reference ServiceMap.Service or static readonly layer pattern"
    )
    assert "InstanceContext" in raw or "InstanceServices" in raw, (
        "AGENTS.md should reference InstanceContext or InstanceServices"
    )


# [pr_diff] fail_to_pass
def test_agents_md_instance_bind():
    """AGENTS.md must document Instance.bind for native callback ALS context."""
    content = AGENTS_MD.read_text()
    assert "Instance.bind" in content, (
        "AGENTS.md doesn't mention Instance.bind"
    )
    # Should explain it's for native addon callbacks
    lower = content.lower()
    assert "native" in lower or "callback" in lower or "als" in lower, (
        "AGENTS.md should explain that Instance.bind is for native/callback/ALS context"
    )


# [pr_diff] fail_to_pass
def test_agents_md_flag_config_migration():
    """AGENTS.md must document the Flag -> Effect.Config migration pattern."""
    content = AGENTS_MD.read_text()
    assert "Config.boolean" in content or "Config<boolean>" in content, (
        "AGENTS.md doesn't document Config.boolean flag migration"
    )
    assert "flag" in content.lower(), (
        "AGENTS.md should mention flag migration"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — compliance with existing AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/opencode/AGENTS.md:24 @ d4694d0
def test_layer_uses_service_of():
    """Layer must return FileWatcherService.of({...}), not a plain object (AGENTS.md line 24)."""
    a = _get_analysis()
    assert a["usesServiceOf"], (
        "FileWatcherService.of() not found — Layer must use ServiceName.of() per AGENTS.md"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression: public API preserved
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_file_watcher_event_preserved():
    """FileWatcher.Event namespace must still be exported (public API)."""
    a = _get_analysis()
    assert a["fileWatcherNamespaceExists"], (
        "FileWatcher namespace no longer exists in watcher.ts"
    )
    assert a["fileWatcherEventExported"], (
        "FileWatcher.Event no longer exported"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — compliance with existing AGENTS.md rules
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:23 @ d4694d0
def test_service_follows_naming_convention():
    """FileWatcherService must follow ServiceMap.Service<Name, Name.Service>()('@opencode/...') pattern."""
    a = _get_analysis()
    assert a["hasServiceClass"], (
        "FileWatcherService not defined as ServiceMap.Service class"
    )
    assert a["hasServiceTag"], (
        "Service tag should follow '@opencode/...' pattern per AGENTS.md"
    )


# [agent_config] pass_to_pass — packages/opencode/AGENTS.md:34 @ d4694d0
def test_layer_uses_effect_gen():
    """Layer implementation must use Effect.gen(function* () {...}) for composition."""
    a = _get_analysis()
    assert a["usesEffectGen"], (
        "Effect.gen(function* ...) not used in watcher layer — AGENTS.md requires it for composition"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """watcher.ts must not be gutted — must retain substantial logic."""
    content = WATCHER.read_text()
    lines = content.strip().splitlines()
    assert len(lines) >= 80, f"Only {len(lines)} lines — file appears gutted"
    for req in ["FileWatcherService", "FileWatcher", "subscribe", "Bus.publish"]:
        assert req in content, f"Missing required identifier: {req}"
