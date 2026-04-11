"""
Task: vscode-agent-feedback-widget-styles
Repo: microsoft/vscode @ 39a50d8d3f4cb82f8d23f6ed762d8feda0a8032f

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/vscode"
THEME = Path(REPO) / "src/vs/sessions/common/theme.ts"
INPUT_CONTRIB = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts"
WIDGET_CONTRIB = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts"
INPUT_CSS = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css"
WIDGET_CSS = Path(REPO) / "src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorWidget.css"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — required files exist
# ---------------------------------------------------------------------------

def test_required_files_exist():
    """All modified files must be present in the workspace."""
    for p in [THEME, INPUT_CONTRIB, WIDGET_CONTRIB, INPUT_CSS, WIDGET_CSS]:
        assert p.exists(), f"Required file missing: {p}"


def test_copyright_headers_preserved():
    """Microsoft copyright header must remain in all modified TypeScript files."""
    for p in [THEME, INPUT_CONTRIB, WIDGET_CONTRIB]:
        header = p.read_text(encoding="utf-8")[:400]
        assert "Copyright" in header, f"Copyright header missing from {p.name}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral tests via Node.js execution
# ---------------------------------------------------------------------------

def test_theme_border_uses_editor_widget_border():
    """agentFeedbackInputWidgetBorder must use editorWidgetBorder, not transparent(iconForeground)."""
    r = _run_node("""
import { readFileSync } from 'fs';

const src = readFileSync('src/vs/sessions/common/theme.ts', 'utf-8');

// Extract the registerColor call for agentFeedbackInputWidget.border
const match = src.match(/registerColor\\(\\s*['\\u0060"]agentFeedbackInputWidget\\.border['\\u0060"][\\s\\S]*?\\)/);
if (!match) {
    console.error('Could not find registerColor call for agentFeedbackInputWidget.border');
    process.exit(1);
}

const colorDef = match[0];

// Must use editorWidgetBorder for dark/light themes
if (!colorDef.includes('editorWidgetBorder')) {
    console.error('Border color definition does not use editorWidgetBorder');
    process.exit(1);
}

// Must NOT use transparent(iconForeground, ...) anymore
if (colorDef.includes('iconForeground')) {
    console.error('Border color definition still uses iconForeground');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_icon_foreground_removed_from_theme():
    """iconForeground import must be removed from theme.ts after border fix."""
    r = _run_node("""
import { readFileSync } from 'fs';

const src = readFileSync('src/vs/sessions/common/theme.ts', 'utf-8');

// Extract all import statements
const imports = src.split('\\n').filter(l => /^import\\s/.test(l));

// iconForeground must not appear in any import
const bad = imports.filter(l => l.includes('iconForeground'));
if (bad.length > 0) {
    console.error('iconForeground is still imported: ' + bad[0].trim());
    process.exit(1);
}

// Double-check: no usage anywhere in the file
if (src.includes('iconForeground')) {
    console.error('iconForeground is still referenced somewhere in theme.ts');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_apply_font_info_removed():
    """applyFontInfo calls must be removed from agentFeedbackEditorInputContribution.ts."""
    r = _run_node("""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorInputContribution.ts',
    'utf-8'
);

// Find method calls to applyFontInfo (e.g., this._editor.applyFontInfo(...))
const calls = src.match(/\\.applyFontInfo\\s*\\(/g);
if (calls && calls.length > 0) {
    console.error('Found ' + calls.length + ' applyFontInfo call(s) — should be removed');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_animation_keyframes_added():
    """agentFeedbackEditorInput.css must include agentFeedbackInputAppear keyframe animation."""
    r = _run_node("""
import { readFileSync } from 'fs';

const css = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css',
    'utf-8'
);

// 1. @keyframes block must exist
const kfMatch = css.match(/@keyframes\\s+agentFeedbackInputAppear\\s*\\{([\\s\\S]*?)\\n\\}/);
if (!kfMatch) {
    console.error('Missing @keyframes agentFeedbackInputAppear');
    process.exit(1);
}

const kfBody = kfMatch[1];

// 2. Must animate opacity (from 0 to 1)
if (!kfBody.includes('opacity')) {
    console.error('Keyframe must animate opacity');
    process.exit(1);
}

// 3. Must animate transform via translateY
if (!kfBody.includes('translateY')) {
    console.error('Keyframe must use translateY transform');
    process.exit(1);
}

// 4. Widget rule must reference this animation
const widgetRule = css.match(/\\.agent-feedback-input-widget\\s*\\{([^}]+)\\}/);
if (!widgetRule || !widgetRule[1].includes('agentFeedbackInputAppear')) {
    console.error('.agent-feedback-input-widget must use agentFeedbackInputAppear animation');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_reduced_motion_accessibility():
    """agentFeedbackEditorInput.css must include prefers-reduced-motion media query."""
    r = _run_node("""
import { readFileSync } from 'fs';

const css = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css',
    'utf-8'
);

// Find prefers-reduced-motion media query
const mqMatch = css.match(/@media\\s*\\(prefers-reduced-motion:\\s*reduce\\)\\s*\\{([\\s\\S]*?)\\n\\}/);
if (!mqMatch) {
    console.error('Missing @media (prefers-reduced-motion: reduce) query');
    process.exit(1);
}

const mqBody = mqMatch[1];

// Must disable animation inside the media query
if (!/animation\\s*:\\s*none/.test(mqBody)) {
    console.error('prefers-reduced-motion block must set animation: none');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_font_inherit_in_input_css():
    """textarea and measure elements in agentFeedbackEditorInput.css must use font: inherit."""
    r = _run_node("""
import { readFileSync } from 'fs';

const css = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/media/agentFeedbackEditorInput.css',
    'utf-8'
);

// Count font: inherit declarations
const matches = css.match(/font\\s*:\\s*inherit/g) || [];
if (matches.length < 2) {
    console.error(
        'Expected at least 2 font: inherit declarations (textarea + measure), found ' + matches.length
    );
    process.exit(1);
}

// Verify they're in the right context (textarea rule and measure rule)
const textareaRule = css.match(/textarea\\s*\\{([^}]+)\\}/);
const measureRule = css.match(/measure[^{]*\\{([^}]+)\\}/);

if (!textareaRule || !/font\\s*:\\s*inherit/.test(textareaRule[1])) {
    console.error('textarea rule must have font: inherit');
    process.exit(1);
}
if (!measureRule || !/font\\s*:\\s*inherit/.test(measureRule[1])) {
    console.error('measure element rule must have font: inherit');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_comment_icon_in_header():
    """Widget header must include a decorative comment icon with aria-hidden."""
    r = _run_node("""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts',
    'utf-8'
);

// Must use renderIcon(Codicon.comment)
if (!src.includes('Codicon.comment')) {
    console.error('Widget must use Codicon.comment icon');
    process.exit(1);
}

const hasRenderIcon = /renderIcon\\s*\\(\\s*Codicon\\.comment\\s*\\)/.test(src);
if (!hasRenderIcon) {
    console.error('Must call renderIcon(Codicon.comment)');
    process.exit(1);
}

// Must set aria-hidden for accessibility (decorative icon)
if (!src.includes('aria-hidden')) {
    console.error('Comment icon must have aria-hidden attribute');
    process.exit(1);
}

// Must append to header node
if (!src.includes('_headerNode.appendChild')) {
    console.error('Comment icon must be appended to _headerNode');
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


def test_single_comment_shows_text_not_label():
    """When there is exactly one comment, title must show comment text, not '1 comment' label."""
    r = _run_node("""
import { readFileSync } from 'fs';

const src = readFileSync(
    'src/vs/sessions/contrib/agentFeedback/browser/agentFeedbackEditorWidgetContribution.ts',
    'utf-8'
);

// Extract the _updateTitle method body
const methodMatch = src.match(/_updateTitle\\s*\\(\\s*\\)\\s*(?::\\s*void\\s*)?\\{([\\s\\S]*?)^\\t\\}/m);
if (!methodMatch) {
    // Fallback: find count === 1 block
    const blockMatch = src.match(/count\\s*===\\s*1[\\s\\S]*?\\}/);
    if (!blockMatch) {
        console.error('Could not find _updateTitle method or count === 1 block');
        process.exit(1);
    }
    const block = blockMatch[0];
    if (!block.includes('_commentItems[0].text')) {
        console.error('count === 1 block must use _commentItems[0].text');
        process.exit(1);
    }
    if (block.includes("localize('oneComment'") || block.includes('localize("oneComment"')) {
        console.error("Old localize('oneComment') string must be removed");
        process.exit(1);
    }
    console.log('PASS');
    process.exit(0);
}

const methodBody = methodMatch[1];

// Must use _commentItems[0].text for single comment preview
if (!methodBody.includes('_commentItems[0].text')) {
    console.error('_updateTitle must use _commentItems[0].text when count === 1');
    process.exit(1);
}

// Must NOT use the old localized "1 comment" string
if (methodBody.includes("localize('oneComment'") || methodBody.includes('localize("oneComment"')) {
    console.error("Old localize('oneComment') string must be removed");
    process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"Failed: {r.stderr or r.stdout}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands from the repo
# ---------------------------------------------------------------------------

def test_repo_eslint():
    """Repo's ESLint passes on all source files (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "eslint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_stylelint():
    """Repo's Stylelint passes on all CSS files (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "stylelint"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"


def test_repo_unit_tests():
    """Repo's Node.js unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "test-node"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-500:] if r.stderr else r.stdout[-500:]}"
