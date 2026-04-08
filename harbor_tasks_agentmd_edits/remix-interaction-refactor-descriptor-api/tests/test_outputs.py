"""
Task: remix-interaction-refactor-descriptor-api
Repo: remix-run/remix @ 90016e313b24a05c5862a853a3b518290d9017ba
PR:   10823

Refactor Interaction API:
- Interactions use `this` context (this.on, this.target, this.signal, this.raise)
- Descriptors extend AddEventListenerOptions directly (no capture()/listenWith())
- createContainer accepts ContainerOptions { signal?, onError? }
- InteractionHandle class implements Interaction interface

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import re
from pathlib import Path

REPO = "/workspace/remix"
PKG = f"{REPO}/packages/interaction"
INTERACTION = f"{PKG}/src/lib/interaction.ts"
INDEX = f"{PKG}/src/index.ts"
README = f"{PKG}/README.md"
CHANGELOG = f"{PKG}/CHANGELOG.md"

_tsx_installed = False


def _ensure_tsx():
    """Install tsx globally (idempotent)."""
    global _tsx_installed
    if _tsx_installed:
        return
    subprocess.run(
        ["npm", "install", "-g", "tsx"],
        capture_output=True, text=True, timeout=60,
    )
    _tsx_installed = True


def _run_ts(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run TypeScript code using tsx in the interaction src/lib directory."""
    _ensure_tsx()
    script = Path(PKG) / "src" / "lib" / "_eval_tmp.ts"
    script.write_text(code)
    try:
        return subprocess.run(
            ["tsx", str(script)],
            capture_output=True, text=True, timeout=timeout,
            cwd=f"{PKG}/src/lib",
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass — structural gates
# ---------------------------------------------------------------------------

def test_core_files_exist():
    """Core interaction source files exist with substantial content."""
    files = [
        INTERACTION,
        INDEX,
        f"{PKG}/src/lib/interactions/form.ts",
        f"{PKG}/src/lib/interactions/keys.ts",
        f"{PKG}/src/lib/interactions/popover.ts",
        f"{PKG}/src/lib/interactions/press.ts",
    ]
    for f in files:
        p = Path(f)
        assert p.exists(), f"{p.name} must exist"
        assert len(p.read_text()) > 50, f"{p.name} must have content"


def test_core_exports_preserved():
    """Core API functions are still exported: on, createContainer, defineInteraction."""
    content = Path(INDEX).read_text()
    for name in ["on", "createContainer", "defineInteraction"]:
        assert name in content, f"{name} must be exported from index.ts"


# ---------------------------------------------------------------------------
# fail_to_pass — behavioral (subprocess via tsx)
# ---------------------------------------------------------------------------

def test_create_container_on_error():
    """createContainer accepts { onError } option and calls it when a listener throws."""
    r = _run_ts("""\
import { createContainer } from './interaction.ts'

let target = new EventTarget()
let errorCaught = false
let expectedError = new Error('sync-throw')

let container = createContainer(target, {
  onError(error: unknown) {
    if (error === expectedError) errorCaught = true
  },
})
container.set({
  test: () => { throw expectedError },
})
target.dispatchEvent(new Event('test'))

if (!errorCaught) {
  process.stderr.write('onError was not called with the expected error\\n')
  process.exit(1)
}
process.stdout.write('PASS\\n')
""")
    assert r.returncode == 0, f"Failed (rc={r.returncode}): {r.stderr}"
    assert "PASS" in r.stdout


def test_descriptor_object_syntax():
    """Descriptor objects with { once: true, listener } work as inline descriptors."""
    r = _run_ts("""\
import { createContainer } from './interaction.ts'

let target = new EventTarget()
let callCount = 0

createContainer(target).set({
  test: { once: true, listener: () => { callCount++ } },
})
target.dispatchEvent(new Event('test'))
target.dispatchEvent(new Event('test'))

if (callCount !== 1) {
  process.stderr.write('Expected 1 call, got ' + callCount + '\\n')
  process.exit(1)
}
process.stdout.write('PASS\\n')
""")
    assert r.returncode == 0, f"Failed (rc={r.returncode}): {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass — structural (file content)
# ---------------------------------------------------------------------------

def test_old_helpers_removed():
    """capture() and listenWith() are no longer exported from index.ts."""
    content = Path(INDEX).read_text()
    export_match = re.search(r'export\s*\{([^}]+)\}', content)
    assert export_match, "index.ts must have an export block"
    exports = export_match.group(1)
    # Strip type-prefixed names to check only value exports
    value_exports = re.sub(r'\btype\s+\w+', '', exports)
    assert "capture" not in value_exports, "capture must not be a value export"
    assert "listenWith" not in value_exports, "listenWith must not be exported"


def test_new_types_exported():
    """Interaction and ContainerOptions types are exported from index.ts."""
    content = Path(INDEX).read_text()
    export_match = re.search(r'export\s*\{([^}]+)\}', content)
    assert export_match, "Must have export block"
    exports = export_match.group(1)
    assert "Interaction" in exports, "Interaction must be in export block"
    assert "ContainerOptions" in exports, "ContainerOptions must be in export block"


def test_interaction_context_pattern():
    """InteractionSetup uses this: Interaction context instead of positional args."""
    content = Path(INTERACTION).read_text()
    assert re.search(r'interface\s+Interaction\b', content), \
        "Interaction interface must be defined"
    assert re.search(r'InteractionSetup.*=.*\(this:\s*Interaction\)', content), \
        "InteractionSetup must use this: Interaction"
    assert "target: EventTarget, signal: AbortSignal) => void" not in content, \
        "Old InteractionSetup signature must be removed"


def test_readme_descriptor_syntax():
    """README shows new descriptor object syntax, not old capture()/listenWith() calls."""
    content = Path(README).read_text()
    assert re.search(r'capture:\s*true', content), \
        "README should show capture: true descriptor syntax"
    assert not re.search(r'\bcapture\s*\(', content), \
        "README should not show capture() function call"
    assert not re.search(r'\blistenWith\s*\(', content), \
        "README should not show listenWith() function call"


def test_changelog_unreleased_heading():
    """CHANGELOG.md uses ## Unreleased heading per AGENTS.md convention."""
    content = Path(CHANGELOG).read_text()
    assert "## Unreleased" in content, \
        "CHANGELOG must have ## Unreleased heading"
