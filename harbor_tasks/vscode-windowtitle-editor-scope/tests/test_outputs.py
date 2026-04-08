"""
Task: vscode-windowtitle-editor-scope
Repo: microsoft/vscode @ c2016b08f5d48a676858f04907c2b1c10ab03a44

Fix: Scope the editor service in BrowserTitlebarPart to its own editor
groups container, preventing the main window title from showing editors
that were moved to auxiliary windows.

All checks must pass for reward = 1. Any failure = reward 0.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    return subprocess.run(
        ["node", "-e", code],
        capture_output=True, text=True, timeout=timeout, cwd=REPO,
    )


# --- fail_to_pass ---


def test_scoped_editor_service_created():
    """editorService.createScoped called with editorGroupsContainer and stored."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/workbench/browser/parts/titlebar/titlebarPart.ts', 'utf8');
if (!src.includes('editorService.createScoped(editorGroupsContainer'))) {
  console.error('FAIL: editorService.createScoped(editorGroupsContainer, ...) not found');
  process.exit(1);
}
if (!src.includes('scopedEditorService')) {
  console.error('FAIL: scopedEditorService variable not assigned');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Scoped editor service not created: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_child_instantiation_service_with_override():
    """Child instantiation service with IEditorService override in ServiceCollection."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/workbench/browser/parts/titlebar/titlebarPart.ts', 'utf8');
if (!src.includes('instantiationService.createChild(new ServiceCollection')) {
  console.error('FAIL: createChild(new ServiceCollection(...)) not found');
  process.exit(1);
}
if (!src.includes('IEditorService, scopedEditorService')) {
  console.error('FAIL: IEditorService -> scopedEditorService override not found');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Child instantiation service wrong: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_window_title_uses_scoped_service():
    """WindowTitle instantiated via the scoped this.instantiationService."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/workbench/browser/parts/titlebar/titlebarPart.ts', 'utf8');
if (!src.includes('this.instantiationService.createInstance(WindowTitle'))) {
  console.error('FAIL: must use this.instantiationService.createInstance(WindowTitle, ...)');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"WindowTitle not using scoped service: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_active_editor_from_container():
    """Active editor read from editorGroupsContainer, not global editorService."""
    r = _run_node("""
const fs = require('fs');
const src = fs.readFileSync('src/vs/workbench/browser/parts/titlebar/titlebarPart.ts', 'utf8');
if (!src.includes('this.editorGroupsContainer.activeGroup.activeEditor')) {
  console.error('FAIL: should use editorGroupsContainer.activeGroup.activeEditor');
  process.exit(1);
}
if (src.includes('this.editorService.activeEditor')) {
  console.error('FAIL: old pattern this.editorService.activeEditor still present');
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"Active editor source wrong: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# --- pass_to_pass ---


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_file_transpiles():
    """Modified TypeScript file transpiles without syntax errors."""
    r = _run_node("""
const ts = require('typescript');
const fs = require('fs');
const src = fs.readFileSync('src/vs/workbench/browser/parts/titlebar/titlebarPart.ts', 'utf8');
const result = ts.transpileModule(src, {
  compilerOptions: {
    module: ts.ModuleKind.ESNext,
    target: ts.ScriptTarget.ESNext,
    experimentalDecorators: true,
    emitDecoratorMetadata: true,
  },
  reportDiagnostics: true,
});
if (result.diagnostics && result.diagnostics.length > 0) {
  result.diagnostics.forEach(d => {
    const msg = typeof d.messageText === 'string'
      ? d.messageText
      : d.messageText.messageText || JSON.stringify(d.messageText);
    console.error('Transpile error: ' + msg);
  });
  process.exit(1);
}
console.log('PASS');
""")
    assert r.returncode == 0, f"TypeScript transpile failed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout
