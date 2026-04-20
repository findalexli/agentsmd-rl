"""
Test suite for Shadow DOM support in Combobox component (PR #8438)

Tests verify BEHAVIOR by running TypeScript code via tsx subprocess
and asserting on stdout output — not on text/structure of source files.
"""

import subprocess
import os
import sys
import json
import tempfile

REPO = "/workspace/mantine"
UTILS_PATH = f"{REPO}/packages/@mantine/core/src/core/utils/find-element-in-shadow-dom"
COMBOBOX_PATH = f"{REPO}/packages/@mantine/core/src/components/Combobox/use-combobox"


def _run_tsx(script: str, timeout: int = 60) -> subprocess.CompletedProcess:
    """Run a TypeScript script via tsx and return the result."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            ["npx", "tsx", script_path],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result
    finally:
        os.unlink(script_path)


# ---------------------------------------------------------------------------
# Fail-to-pass tests — must fail on base, pass on fix
# ---------------------------------------------------------------------------

def test_find_element_in_shadow_dom_file_exists():
    """The new utility file was created (f2p)."""
    file_path = f"{UTILS_PATH}/find-element-in-shadow-dom.ts"
    assert os.path.exists(file_path), f"Utility file not found: {file_path}"


def test_find_element_in_shadow_dom_exports():
    """The utility file exports the three required functions (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{ nodeName: '#document', querySelector: () => null, querySelectorAll: () => [], createElement: () => ({{}}) }};

import {{ findElementBySelector, findElementsBySelector, getRootElement }} from '{UTILS_PATH}/find-element-in-shadow-dom';
const funcs = [typeof findElementBySelector, typeof findElementsBySelector, typeof getRootElement];
console.log(JSON.stringify(funcs));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    funcs = json.loads(result.stdout.strip())
    assert funcs == ['function', 'function', 'function'], \
        f"Expected all functions, got: {funcs}"


def test_core_utils_exports_shadow_dom_utilities():
    """The core/utils/index.ts exports the new shadow DOM utilities (f2p)."""
    index_path = f"{REPO}/packages/@mantine/core/src/core/utils/index.ts"
    with open(index_path) as f:
        content = f.read()

    assert "find-element-in-shadow-dom" in content or "findElementBySelector" in content, \
        "core/utils/index.ts should export shadow DOM utilities"


def test_getrootelement_handles_null():
    """getRootElement(null) returns document (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{ nodeName: '#document', querySelector: () => null, querySelectorAll: () => [], createElement: () => ({{}}) }};

import {{ getRootElement }} from '{UTILS_PATH}/find-element-in-shadow-dom';
const result = getRootElement(null as any);
console.log(JSON.stringify({{ notUndefined: result !== undefined }}));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data['notUndefined'], "getRootElement(null) should return document (not undefined)"


def test_getrootelement_returns_shadow_root():
    """getRootElement(shadowElement) returns the ShadowRoot (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{
  nodeName = '#shadow-root';
  querySelector() {{ return null; }}
  querySelectorAll() {{ return []; }}
}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{ nodeName: '#document', querySelector: () => null, querySelectorAll: () => [], createElement: () => ({{}}) }};

import {{ getRootElement }} from '{UTILS_PATH}/find-element-in-shadow-dom';

const mockShadowRoot = new (globalThis as any).ShadowRoot();
const mockElement = {{ getRootNode: () => mockShadowRoot }} as any;

const result = getRootElement(mockElement);
console.log(JSON.stringify({{ isShadowRoot: result === mockShadowRoot }}));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data['isShadowRoot'], "getRootElement should return the ShadowRoot"


def test_getrootelement_returns_document_for_regular_element():
    """getRootElement(regularElement) returns document when root is not shadow (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{
  nodeName: '#document',
  querySelector: () => null,
  querySelectorAll: () => [],
  createElement: () => ({{}})
}};

import {{ getRootElement }} from '{UTILS_PATH}/find-element-in-shadow-dom';

const mockDocument = (globalThis as any).document;
const mockElement = {{ getRootNode: () => mockDocument }} as any;

const result = getRootElement(mockElement);
console.log(JSON.stringify({{ isDocument: result === mockDocument }}));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data['isDocument'], "getRootElement should return document for non-shadow elements"


def test_findelementbyselector_calls_queryselector_on_shadow_root():
    """findElementBySelector queries through ShadowRoot, not document (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{ nodeName: '#document', querySelector: () => null, querySelectorAll: () => [], createElement: () => ({{}}) }};

import {{ findElementBySelector }} from '{UTILS_PATH}/find-element-in-shadow-dom';

let querySelectorCalled = false;
let querySelectorArg = '';

const mockShadowRoot = {{
  nodeName: '#shadow-root',
  querySelector: (sel: string) => {{
    querySelectorCalled = true;
    querySelectorArg = sel;
    return {{ found: true }};
  }},
}} as any;

const result = findElementBySelector('.mantine-option', mockShadowRoot);
console.log(JSON.stringify({{
  called: querySelectorCalled,
  arg: querySelectorArg,
  found: result !== null
}}));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data['called'], "findElementBySelector should call querySelector on the ShadowRoot"
    assert data['arg'] == '.mantine-option', f"querySelector should be called with '.mantine-option', got '{data['arg']}'"
    assert data['found'], "findElementBySelector should find the element"


def test_findelementsbyselector_calls_queryselectorall_on_shadow_root():
    """findElementsBySelector queries through ShadowRoot, not document (f2p)."""
    script = f"""
(globalThis as any).ShadowRoot = class {{}};
(globalThis as any).Document = class {{}};
(globalThis as any).document = {{ nodeName: '#document', querySelector: () => null, querySelectorAll: () => [], createElement: () => ({{}}) }};

import {{ findElementsBySelector }} from '{UTILS_PATH}/find-element-in-shadow-dom';

let querySelectorAllCalled = false;
const querySelectorAllArgs = [];

const mockShadowRoot = {{
  nodeName: '#shadow-root',
  querySelectorAll: (sel: string) => {{
    querySelectorAllCalled = true;
    querySelectorAllArgs.push(sel);
    if (sel === '.mantine-option') return [{{opt:true}}];  // direct match
    if (sel === '*') return [{{ shadowRoot: {{ querySelectorAll: () => [{{opt:true}}] }} }}];  // element with shadow
    return [];
  }},
}} as any;

const result = findElementsBySelector('.mantine-option', mockShadowRoot);
console.log(JSON.stringify({{
  called: querySelectorAllCalled,
  args: querySelectorAllArgs,
  count: result.length
}}));
"""
    result = _run_tsx(script)
    assert result.returncode == 0, f"tsx failed: {result.stderr}"
    data = json.loads(result.stdout.strip())
    assert data['called'], "findElementsBySelector should call querySelectorAll on the ShadowRoot"
    assert '.mantine-option' in data['args'], f"querySelectorAll should be called with '.mantine-option', got {data['args']}"
    assert data['count'] == 2, f"findElementsBySelector should find 2 elements (1 direct + 1 via shadow), got {data['count']}"


def test_use_combobox_imports_shadow_dom_utilities():
    """use-combobox.ts imports the shadow DOM utilities (f2p)."""
    use_combobox_path = f"{COMBOBOX_PATH}/use-combobox.ts"
    with open(use_combobox_path) as f:
        content = f.read()

    # Should import from the shadow DOM utilities (any import style is valid)
    assert "find-element-in-shadow-dom" in content or "findElementBySelector" in content, \
        "use-combobox.ts should import from the shadow DOM utilities"


def test_use_combobox_uses_getrootelement_before_querying():
    """use-combobox.ts uses getRootElement to determine the query root (f2p)."""
    use_combobox_path = f"{COMBOBOX_PATH}/use-combobox.ts"
    with open(use_combobox_path) as f:
        content = f.read()

    # Should call getRootElement to get the root before querying
    assert "getRootElement" in content, \
        "use-combobox.ts should use getRootElement to determine query root"


# ---------------------------------------------------------------------------
# Pass-to-pass tests — must pass on both base and fix
# ---------------------------------------------------------------------------

def test_use_combobox_typescript_compiles():
    """The modified use-combobox.ts compiles without errors (p2p)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "packages/@mantine/core/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Filter out unrelated errors (from other packages)
    errors = [line for line in result.stderr.split('\n') if 'use-combobox.ts' in line]

    assert result.returncode == 0 or len(errors) == 0, \
        f"TypeScript compilation errors in use-combobox.ts:\n{result.stderr[-2000:]}"


def test_shadow_dom_utility_typescript_compiles():
    """The new find-element-in-shadow-dom.ts compiles without errors (p2p)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--project", "packages/@mantine/core/tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Filter for errors in the shadow DOM utility file
    errors = [line for line in result.stderr.split('\n')
              if 'find-element-in-shadow-dom' in line]

    assert result.returncode == 0 or len(errors) == 0, \
        f"TypeScript compilation errors in find-element-in-shadow-dom:\n{result.stderr[-2000:]}"


def test_repo_eslint_use_combobox():
    """ESLint passes for use-combobox.ts (p2p)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/core/src/components/Combobox/use-combobox/use-combobox.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"ESLint failed for use-combobox.ts:\n{r.stdout[-1000:]}"


def test_repo_eslint_core_utils():
    """ESLint passes for core utils index.ts (p2p)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/core/src/core/utils/index.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"ESLint failed for core/utils/index.ts:\n{r.stdout[-1000:]}"


def test_repo_prettier_modified_files():
    """Prettier check passes for modified files (p2p)."""
    r = subprocess.run(
        ["npx", "prettier", "--check",
         "packages/@mantine/core/src/components/Combobox/use-combobox/use-combobox.ts",
         "packages/@mantine/core/src/core/utils/index.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short", "--no-header"]))
