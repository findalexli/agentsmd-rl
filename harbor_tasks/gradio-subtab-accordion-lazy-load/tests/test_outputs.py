"""
Task: gradio-subtab-accordion-lazy-load
Repo: gradio-app/gradio @ ccff8b8cacffe36a270fcea9fc8ba29b78c31c8d
PR:   12906

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/gradio"
INIT_TS = f"{REPO}/js/core/src/_init.ts"
SVELTE_TS = f"{REPO}/js/core/src/init.svelte.ts"


def _js(template: str) -> str:
    """Replace path placeholders in a JS template string."""
    return (template
            .replace("%%REPO%%", REPO)
            .replace("%%INIT_TS%%", INIT_TS)
            .replace("%%SVELTE_TS%%", SVELTE_TS))


def _run_node(script: str, timeout: int = 30) -> None:
    """Write JS to temp file, run with node, assert exit 0."""
    tmp = Path(tempfile.mktemp(suffix=".js"))
    try:
        tmp.write_text(script)
        r = subprocess.run(
            ["node", str(tmp)], capture_output=True, text=True, timeout=timeout
        )
        assert r.returncode == 0, (
            f"Node script failed (rc={r.returncode}):\n{r.stdout}\n{r.stderr}"
        )
    finally:
        tmp.unlink(missing_ok=True)


# JS preamble: extract make_visible_if_not_rendered from source, transpile, eval
_FN_PREAMBLE = _js("""
const fs = require('fs');
const ts = require('%%REPO%%/node_modules/typescript');

const src = fs.readFileSync('%%SVELTE_TS%%', 'utf8');
const fnStart = src.indexOf('function make_visible_if_not_rendered');
if (fnStart === -1) { console.error('function not found'); process.exit(1); }

const rest = src.substring(fnStart);
let depth = 0, fnEnd = 0, started = false;
for (let i = 0; i < rest.length; i++) {
  if (rest[i] === '{') { depth++; started = true; }
  if (rest[i] === '}') { depth--; }
  if (started && depth === 0) { fnEnd = i + 1; break; }
}
const fnSource = rest.substring(0, fnEnd);
const jsCode = ts.transpileModule(fnSource, {
  compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.None }
}).outputText;

eval(jsCode);

const mkNode = (id, type, props, children) => ({
  id, type,
  props: { props: props || {}, shared_props: { visible: false } },
  children: children || []
});
""")


# ---------------------------------------------------------------------------
# Gate (pass_to_pass, static) — syntax check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Both modified TypeScript files must parse without syntax errors."""
    _run_node(_js("""
const fs = require('fs');
const ts = require('%%REPO%%/node_modules/typescript');
const files = ['%%INIT_TS%%', '%%SVELTE_TS%%'];
let errors = false;
for (const f of files) {
  const src = fs.readFileSync(f, 'utf8');
  const result = ts.transpileModule(src, {
    compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.ESNext },
    reportDiagnostics: true
  });
  const diags = (result.diagnostics || []).filter(
    d => d.category === ts.DiagnosticCategory.Error
  );
  if (diags.length > 0) {
    console.error('Syntax errors in ' + f);
    errors = true;
  }
}
if (errors) process.exit(1);
"""))


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_tabs_filter_selected_only():
    """make_visible_if_not_rendered only recurses into the selected tab's children."""
    _run_node(_FN_PREAMBLE + """
// Two tab items under a tabs node; tab 10 is selected, tab 20 is not
const child1 = mkNode(100, 'textbox');
const child2 = mkNode(200, 'textbox');
const tab1 = mkNode(10, 'tabitem', { id: 10 }, [child1]);
const tab2 = mkNode(20, 'tabitem', { id: 20 }, [child2]);
const tabsNode = mkNode(1, 'tabs', { selected: 10 }, [tab1, tab2]);

const hidden = new Set([1, 10, 20, 100, 200]);
try { make_visible_if_not_rendered(tabsNode, hidden, false); }
catch(e) { make_visible_if_not_rendered(tabsNode, hidden); }

// Non-selected tab's child must NOT be visible
if (child2.props.shared_props.visible === true) {
  console.error('Non-selected tab child (id:200) was made visible');
  process.exit(1);
}
// Selected tab's child must be visible
if (!child1.props.shared_props.visible) {
  console.error('Selected tab child (id:100) was not made visible');
  process.exit(1);
}
""")


# [pr_diff] fail_to_pass
def test_closed_accordion_children_skipped():
    """make_visible_if_not_rendered skips children of a closed accordion."""
    _run_node(_FN_PREAMBLE + """
const child = mkNode(100, 'textbox');
const accordion = mkNode(1, 'accordion', { open: false }, [child]);
const hidden = new Set([1, 100]);

try { make_visible_if_not_rendered(accordion, hidden, false); }
catch(e) { make_visible_if_not_rendered(accordion, hidden); }

// Closed accordion's child must NOT be made visible
if (child.props.shared_props.visible === true) {
  console.error('Closed accordion child was made visible');
  process.exit(1);
}
// The accordion itself should be visible
if (!accordion.props.shared_props.visible) {
  console.error('Accordion itself should be visible');
  process.exit(1);
}
""")


# [pr_diff] fail_to_pass
def test_nested_tabs_selected_path_only():
    """Nested tabs: only the selected path at each level gets rendered."""
    _run_node(_FN_PREAMBLE + """
// Outer tabs (selected: 10), inner tabs (selected: 101)
const inner_child1 = mkNode(1001, 'textbox');
const inner_child2 = mkNode(1002, 'textbox');
const inner_tab1 = mkNode(101, 'tabitem', { id: 101 }, [inner_child1]);
const inner_tab2 = mkNode(102, 'tabitem', { id: 102 }, [inner_child2]);
const innerTabs = mkNode(100, 'tabs', { selected: 101 }, [inner_tab1, inner_tab2]);

const outer_child = mkNode(2001, 'textbox');
const tab_a = mkNode(10, 'tabitem', { id: 10 }, [innerTabs]);
const tab_b = mkNode(20, 'tabitem', { id: 20 }, [outer_child]);
const outerTabs = mkNode(1, 'tabs', { selected: 10 }, [tab_a, tab_b]);

const hidden = new Set([1, 10, 20, 100, 101, 102, 1001, 1002, 2001]);
try { make_visible_if_not_rendered(outerTabs, hidden, false); }
catch(e) { make_visible_if_not_rendered(outerTabs, hidden); }

// Selected path: outer tab 10 → inner tab 101 → inner_child1 should be visible
if (!inner_child1.props.shared_props.visible) {
  console.error('Selected nested child (1001) not visible');
  process.exit(1);
}
// Non-selected inner tab's child must NOT be visible
if (inner_child2.props.shared_props.visible) {
  console.error('Non-selected inner tab child (1002) was made visible');
  process.exit(1);
}
// Non-selected outer tab's child must NOT be visible
if (outer_child.props.shared_props.visible) {
  console.error('Non-selected outer tab child (2001) was made visible');
  process.exit(1);
}
""")


# [pr_diff] fail_to_pass
def test_init_accordion_branch():
    """determine_visible_components in _init.ts handles accordion with open-state check."""
    _run_node(_js("""
const fs = require('fs');
const ts = require('%%REPO%%/node_modules/typescript');

const src = fs.readFileSync('%%INIT_TS%%', 'utf8');
const sourceFile = ts.createSourceFile('_init.ts', src, ts.ScriptTarget.ESNext, true);

let found_accordion_branch = false;
let has_open_check = false;

function visit(node) {
  if (ts.isIfStatement(node)) {
    const cond = node.expression.getText(sourceFile);
    if (cond.includes('accordion') && cond.includes('type')) {
      found_accordion_branch = true;
      const body = node.thenStatement.getText(sourceFile);
      if (body.includes('open')) {
        has_open_check = true;
      }
    }
  }
  ts.forEachChild(node, visit);
}
visit(sourceFile);

if (!found_accordion_branch) {
  console.error('No if-branch testing for accordion type in _init.ts');
  process.exit(1);
}
if (!has_open_check) {
  console.error('Accordion branch does not check open state');
  process.exit(1);
}
"""))


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / static) — regression tests
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_basic_visibility_setting():
    """Basic nodes in hidden_on_startup become visible; others unchanged."""
    _run_node(_FN_PREAMBLE + """
// Column with a textbox child, both in hidden_on_startup
const node = mkNode(1, 'column', {}, [mkNode(2, 'textbox')]);
const hidden = new Set([1, 2]);
try { make_visible_if_not_rendered(node, hidden, false); }
catch(e) { make_visible_if_not_rendered(node, hidden); }

if (!node.props.shared_props.visible) {
  console.error('Node in hidden_on_startup was not made visible');
  process.exit(1);
}
if (!node.children[0].props.shared_props.visible) {
  console.error('Child in hidden_on_startup was not made visible');
  process.exit(1);
}

// Node NOT in hidden_on_startup should keep original visibility
const node2 = mkNode(5, 'column', {}, []);
node2.props.shared_props.visible = false;
try { make_visible_if_not_rendered(node2, new Set(), false); }
catch(e) { make_visible_if_not_rendered(node2, new Set()); }
if (node2.props.shared_props.visible !== false) {
  console.error('Node not in hidden_on_startup had visibility changed');
  process.exit(1);
}
""")


# [pr_diff] pass_to_pass
def test_open_accordion_children_visible():
    """Open accordion's children are still made visible (regression)."""
    _run_node(_FN_PREAMBLE + """
const child = mkNode(100, 'textbox');
// open: true (default open)
const accordion = mkNode(1, 'accordion', { open: true }, [child]);
const hidden = new Set([1, 100]);

try { make_visible_if_not_rendered(accordion, hidden, false); }
catch(e) { make_visible_if_not_rendered(accordion, hidden); }

if (!child.props.shared_props.visible) {
  console.error('Open accordion child should be visible');
  process.exit(1);
}
if (!accordion.props.shared_props.visible) {
  console.error('Open accordion should be visible');
  process.exit(1);
}
""")


# [pr_diff] pass_to_pass
def test_target_accordion_renders_children():
    """When accordion is the direct target, children render even if closed."""
    _run_node(_FN_PREAMBLE + """
const child = mkNode(100, 'textbox');
const accordion = mkNode(1, 'accordion', { open: false }, [child]);
const hidden = new Set([1, 100]);

// is_target_node = true: user navigated to this accordion
try { make_visible_if_not_rendered(accordion, hidden, true); }
catch(e) {
  // Base version takes 2 args; extra arg ignored, recurses into everything → passes
  make_visible_if_not_rendered(accordion, hidden);
}

if (!child.props.shared_props.visible) {
  console.error('Target accordion should render children even when closed');
  process.exit(1);
}
""")
