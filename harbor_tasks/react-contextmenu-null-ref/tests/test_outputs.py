"""
Task: react-contextmenu-null-ref
Repo: facebook/react @ 93882bd40ee48dc6d072dfc0b6cc7801fac1be31
PR:   35923

Tests for fixing ContextMenu null ref crash in React DevTools.
All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/react"
MENU_FILE = "packages/react-devtools-shared/src/devtools/ContextMenu/ContextMenu.js"
CONTEXT_MENU = Path(REPO) / MENU_FILE


def _run_node(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute a Node.js script in the repo working directory."""
    tmp = Path(REPO) / "_eval_test.cjs"
    tmp.write_text(script)
    try:
        return subprocess.run(
            ["node", str(tmp)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        tmp.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# pass_to_pass (static)
# ---------------------------------------------------------------------------

def test_file_structure():
    """ContextMenu.js must exist with ContextMenu function, useLayoutEffect, and createPortal."""
    assert CONTEXT_MENU.exists(), f"File not found: {CONTEXT_MENU}"
    src = CONTEXT_MENU.read_text()
    assert len(src) > 200, "File appears empty"
    assert "function ContextMenu" in src, "ContextMenu function not found"
    assert "useLayoutEffect" in src, "useLayoutEffect hook removed"
    assert "createPortal" in src, "createPortal removed"


# ---------------------------------------------------------------------------
# pass_to_pass (repo_tests) - Real CI commands from the React repo
# ---------------------------------------------------------------------------

def test_repo_lint():
    """Repo's ESLint passes on the codebase (pass_to_pass).

    Runs: yarn lint
    This is the same command CI runs to check code style.
    """
    r = subprocess.run(
        ["yarn", "lint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


def test_repo_flow():
    """Repo's Flow type checking passes for dom-node renderer (pass_to_pass).

    Runs: yarn flow dom-node
    This checks Flow types for the DOM renderer configuration.
    """
    r = subprocess.run(
        ["yarn", "flow", "dom-node"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Flow check failed:\n{r.stderr[-1000:] if r.stderr else r.stdout[-1000:]}"


# ---------------------------------------------------------------------------
# fail_to_pass (pr_diff) — behavioral tests via Node.js subprocess
# ---------------------------------------------------------------------------

def test_createref_not_used_as_default():
    """createRef() must not be imported or used as default ref prop (root cause of crash).

    Runs Node.js to parse the source and verify createRef is removed from
    both the import and the function signature default parameter.
    """
    script = (
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('" + MENU_FILE + "', 'utf-8');\n"
        "\n"
        "// createRef must not be imported from react\n"
        "const importLines = src.split('\\n').filter(l => /^import\\s/.test(l) && l.includes(\"'react'\"));\n"
        "if (importLines.some(l => l.includes('createRef'))) {\n"
        "  process.stderr.write('FAIL: createRef is still imported from react\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// createRef() must not appear as default param in ContextMenu function signature\n"
        "const sigMatch = src.match(/function\\s+ContextMenu\\s*\\(\\{[\\s\\S]*?\\}[\\s\\S]*?\\)\\s*(?::\\s*\\S+\\s*)?\\{/);\n"
        "if (!sigMatch) {\n"
        "  process.stderr.write('FAIL: ContextMenu function signature not found\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "if (sigMatch[0].includes('createRef')) {\n"
        "  process.stderr.write('FAIL: createRef() still used as default param\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "process.stdout.write('PASS\\n');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_hidemenu_variable_and_early_return_in_effect():
    """hideMenu variable must guard useLayoutEffect against null ref access.

    Runs Node.js to verify hideMenu is declared before the effect and
    checked inside the effect body as an early-return guard.
    """
    script = (
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('" + MENU_FILE + "', 'utf-8');\n"
        "\n"
        "// hideMenu must be declared as a variable\n"
        "if (!src.match(/(?:const|let|var)\\s+hideMenu\\b/)) {\n"
        "  process.stderr.write('FAIL: hideMenu is not declared as a variable\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// hideMenu must be defined BEFORE useLayoutEffect\n"
        "const defIdx = src.search(/(?:const|let|var)\\s+hideMenu\\b/);\n"
        "const effectIdx = src.indexOf('useLayoutEffect(');\n"
        "if (effectIdx === -1) {\n"
        "  process.stderr.write('FAIL: useLayoutEffect not found\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "if (defIdx > effectIdx) {\n"
        "  process.stderr.write('FAIL: hideMenu defined after useLayoutEffect\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// Effect body must contain if (hideMenu) guard\n"
        "const effectSrc = src.slice(effectIdx);\n"
        "const bodyMatch = effectSrc.match(/useLayoutEffect\\(\\s*\\(\\)\\s*=>\\s*\\{([\\s\\S]*?)\\n\\s*\\},\\s*\\[/);\n"
        "if (!bodyMatch) {\n"
        "  process.stderr.write('FAIL: Cannot extract useLayoutEffect body\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "if (!bodyMatch[1].match(/if\\s*\\(\\s*hideMenu\\s*\\)/)) {\n"
        "  process.stderr.write('FAIL: useLayoutEffect body does not check hideMenu\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "process.stdout.write('PASS\\n');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_null_check_before_using_ref():
    """menuRef.current must be null-checked in useLayoutEffect before use as HTMLElement.

    Runs Node.js to verify the effect body references menuRef.current and
    includes an explicit === null guard before casting to HTMLElement.
    """
    script = (
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('" + MENU_FILE + "', 'utf-8');\n"
        "\n"
        "// Extract useLayoutEffect body\n"
        "const effectSrc = src.slice(src.indexOf('useLayoutEffect('));\n"
        "const bodyMatch = effectSrc.match(/useLayoutEffect\\(\\s*\\(\\)\\s*=>\\s*\\{([\\s\\S]*?)\\n\\s*\\},\\s*\\[/);\n"
        "if (!bodyMatch) {\n"
        "  process.stderr.write('FAIL: Cannot extract useLayoutEffect body\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "const body = bodyMatch[1];\n"
        "\n"
        "// Must reference menuRef.current and have a null check (=== null)\n"
        "if (!body.includes('menuRef.current')) {\n"
        "  process.stderr.write('FAIL: menuRef.current not referenced in effect\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "if (!body.includes('=== null')) {\n"
        "  process.stderr.write('FAIL: No === null check in effect body\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "process.stdout.write('PASS\\n');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_hidemenu_in_dependency_array():
    """useLayoutEffect dependency array must be [hideMenu], not empty [].

    Runs Node.js to verify the effect's dependency array changed from the
    buggy empty [] to [hideMenu] so the effect re-runs on visibility change.
    """
    script = (
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('" + MENU_FILE + "', 'utf-8');\n"
        "\n"
        "// Must NOT have empty dependency array (the buggy pattern)\n"
        "if (src.match(/useLayoutEffect\\([\\s\\S]*?\\},\\s*\\[\\s*\\]\\s*\\)/)) {\n"
        "  process.stderr.write('FAIL: useLayoutEffect still has empty dep array []\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// Must have [hideMenu] as dependency array\n"
        "if (!src.match(/\\},\\s*\\[hideMenu\\]\\s*\\)/)) {\n"
        "  process.stderr.write('FAIL: useLayoutEffect deps should be [hideMenu]\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "process.stdout.write('PASS\\n');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_internal_ref_replaces_prop_ref():
    """Component must use internal useRef (menuRef) attached to div, not external ref prop.

    Runs Node.js to verify menuRef is introduced and wired to the JSX element,
    replacing the old ref prop that used createRef() as a default.
    """
    script = (
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('" + MENU_FILE + "', 'utf-8');\n"
        "\n"
        "// menuRef must exist (internal ref via React.useRef)\n"
        "if (!src.includes('menuRef')) {\n"
        "  process.stderr.write('FAIL: menuRef not found — internal ref not introduced\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// JSX must attach menuRef to the div element\n"
        "if (!src.match(/ref=\\{menuRef\\}/)) {\n"
        "  process.stderr.write('FAIL: menuRef not attached to ContextMenu div\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "// Old prop ref default must be gone\n"
        "if (src.includes('ref = createRef()')) {\n"
        "  process.stderr.write('FAIL: Old ref = createRef() default still present\\n');\n"
        "  process.exit(1);\n"
        "}\n"
        "\n"
        "process.stdout.write('PASS\\n');\n"
    )
    r = _run_node(script)
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout
