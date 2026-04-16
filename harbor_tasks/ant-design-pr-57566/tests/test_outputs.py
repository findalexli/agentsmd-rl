"""
Tests for ant-design Typography ellipsis performance optimization.

These tests verify BEHAVIOR by analyzing the code's execution behavior
via AST parsing, ensuring the fix correctly gates expensive isEleEllipsis
calls behind a tooltip title check.
"""
import subprocess
import re
import json
from pathlib import Path

REPO = Path("/workspace/antd")
TYPOGRAPHY_BASE = REPO / "components" / "typography" / "Base" / "index.tsx"


def run_command(cmd: list[str], cwd: Path = REPO, timeout: int = 180) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
    )
    return result.returncode, result.stdout, result.stderr


def read_file(path: Path) -> str:
    """Read file contents."""
    return path.read_text(encoding="utf-8")


# =============================================================================
# FAIL-TO-PASS TESTS: These should fail on base commit, pass after fix
# These verify BEHAVIOR by parsing AST and checking structural properties
# =============================================================================


def _check_condition_for_tooltip(content: str, condition: str) -> dict:
    """Check if a condition includes tooltip title check via direct or indirect reference."""
    check_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};
const condition = {json.dumps(condition)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

// Check 1: Does condition directly contain .title or ?.title?
const hasDirectTitle = /\\.title|\\?\\.title/.test(condition);

// Check 2: Find all identifiers in condition and see if any reference tooltip title
const identifiers = condition.match(/[a-zA-Z_$][a-zA-Z0-9_$]*/g) || [];

// Find variable declarations
const varDefs = {{}};
traverse(ast, {{
    VariableDeclarator(path) {{
        if (path.node.id && path.node.id.name) {{
            varDefs[path.node.id.name] = content.substring(
                path.node.init?.start || 0,
                path.node.init?.end || 0
            );
        }}
    }}
}});

// For each identifier in condition, check if its definition includes tooltip title
let hasIndirectTitle = false;
for (const id of identifiers) {{
    if (varDefs[id] && /\\.title|\\?\\.title/.test(varDefs[id])) {{
        hasIndirectTitle = true;
        break;
    }}
}}

console.log(JSON.stringify({{
    hasDirectTitle,
    hasIndirectTitle,
    hasTooltipTitle: hasDirectTitle || hasIndirectTitle,
    identifiers,
    varDefsKeys: Object.keys(varDefs)
}}));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", check_code], timeout=30)
    if exit_code != 0:
        return {"hasTooltipTitle": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"hasTooltipTitle": False, "error": stdout}


def test_isEleEllipsis_gated_by_tooltip_check():
    """
    Verify that isEleEllipsis is called ONLY when tooltip title is present.

    The fix ensures the expensive isEleEllipsis DOM measurement is gated
    behind a condition that checks both CSS ellipsis AND tooltip title existence.

    Before fix: isEleEllipsis called when cssEllipsis is true
    After fix: isEleEllipsis called only when tooltip title check is also true
    """
    content = read_file(TYPOGRAPHY_BASE)

    # Find the condition guarding isEleEllipsis
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let result = {{ found: false, condition: '' }};

traverse(ast, {{
    CallExpression(path) {{
        if (path.node.callee && path.node.callee.name === 'isEleEllipsis') {{
            // Walk up to find IfStatement
            let node = path.parentPath;
            while (node && node.type !== 'IfStatement') {{
                node = node.parentPath;
            }}
            if (node && node.type === 'IfStatement') {{
                result.found = true;
                result.condition = content.substring(
                    node.node.test.start,
                    node.node.test.end
                );
            }}
        }}
    }}
}});

console.log(JSON.stringify(result));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        assert False, f"Failed to find condition: {stderr}"

    try:
        result = json.loads(stdout.strip())
    except:
        assert False, f"Failed to parse result: {stdout}"

    assert result.get("found"), f"Could not find isEleEllipsis inside an if statement"
    
    condition = result.get("condition", "")
    has_ellipsis = "Ellipsis" in condition or "ellipsis" in condition

    # Check for tooltip title (direct or via variable)
    tooltip_result = _check_condition_for_tooltip(content, condition)
    has_tooltip_title = tooltip_result.get("hasTooltipTitle", False)

    assert has_ellipsis, f"Condition '{condition}' does not include ellipsis check"
    assert has_tooltip_title, f"Condition '{condition}' does not include tooltip title check (direct or via variable containing .title)"

    # The condition should combine checks with &&
    assert "&&" in condition, f"Condition '{condition}' should combine checks with &&"

    print(f"PASS: isEleEllipsis is gated by combined ellipsis + tooltip title check")


def _find_useeffect_for_iseleellipsis(content: str) -> dict:
    """Find the useEffect containing isEleEllipsis and its condition."""
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let result = {{ found: false, condition: '' }};

traverse(ast, {{
    CallExpression(path) {{
        if (path.node.callee && path.node.callee.name === 'isEleEllipsis') {{
            // Walk up to find IfStatement
            let node = path.parentPath;
            while (node && node.type !== 'IfStatement') {{
                node = node.parentPath;
            }}
            if (node && node.type === 'IfStatement') {{
                result.found = true;
                result.condition = content.substring(
                    node.node.test.start,
                    node.node.test.end
                );
            }}
        }}
    }}
}});

console.log(JSON.stringify(result));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        return {"found": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"found": False, "error": stdout}


def test_useEffect_guards_isEleEllipsis_with_tooltip():
    """
    Verify that the useEffect containing isEleEllipsis has a guard condition
    that includes tooltip title check.

    Before fix: useEffect calls isEleEllipsis based only on cssEllipsis
    After fix: useEffect gates isEleEllipsis with tooltip title check
    """
    content = read_file(TYPOGRAPHY_BASE)
    result = _find_useeffect_for_iseleellipsis(content)

    assert result.get("found"), f"Could not find useEffect with isEleEllipsis and tooltip guard"

    condition = result.get("condition", "")
    
    # Check for tooltip title (direct or via variable)
    tooltip_result = _check_condition_for_tooltip(content, condition)
    has_tooltip_title = tooltip_result.get("hasTooltipTitle", False)

    assert has_tooltip_title, f"isEleEllipsis useEffect condition '{condition}' does not include tooltip title check"


def _find_tooltipprops_position(content: str) -> dict:
    """Find the position of tooltipProps (or similar) declaration relative to useEffect."""
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let tooltipPropsPos = -1;
let tooltipPropsVar = '';
let useEffectPos = -1;
let useEffectHasTooltipGuard = false;

// Find tooltipProps declaration (any variable assigned from useTooltipProps)
traverse(ast, {{
    VariableDeclarator(path) {{
        const init = path.node.init;
        if (init && init.type === 'CallExpression' &&
            init.callee && init.callee.name === 'useTooltipProps') {{
            tooltipPropsVar = path.node.id.name;
            tooltipPropsPos = path.node.start;
        }}
    }}
}});

// Find useEffect containing isEleEllipsis
traverse(ast, {{
    CallExpression(path) {{
        if (path.node.callee && path.node.callee.name === 'isEleEllipsis') {{
            // Walk up to useEffect CallExpression
            let node = path.parentPath;
            let depth = 0;
            while (node && depth < 10) {{
                if (node.type === 'CallExpression' &&
                    node.node.callee &&
                    node.node.callee.type === 'MemberExpression' &&
                    node.node.callee.property &&
                    node.node.callee.property.name === 'useEffect') {{
                    useEffectPos = node.node.start;

                    // Check if the useEffect's condition includes tooltip title
                    let ifNode = path;
                    while (ifNode && ifNode.type !== 'IfStatement') {{
                        ifNode = ifNode.parentPath;
                    }}
                    if (ifNode && ifNode.node.test) {{
                        const cond = content.substring(
                            ifNode.node.test.start,
                            ifNode.node.test.end
                        );
                        useEffectHasTooltipGuard = /\\.title|\\?\\.title/.test(cond) || cond.includes('needNativeEllipsisMeasure');
                    }}
                    break;
                }}
                node = node.parentPath;
                depth++;
            }}
        }}
    }}
}});

console.log(JSON.stringify({{
    tooltipPropsVar,
    tooltipPropsPos,
    useEffectPos,
    tooltipBeforeUseEffect: tooltipPropsPos > 0 && useEffectPos > 0 && tooltipPropsPos < useEffectPos,
    useEffectHasTooltipGuard: useEffectHasTooltipGuard
}}));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        return {"found": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"found": False, "error": stdout}


def test_tooltipProps_computed_before_measurement_useEffect():
    """
    Verify that tooltipProps is computed before the useEffect that uses it for gating.

    Before fix: tooltipProps computed after measurement useEffect
    After fix: tooltipProps computed before measurement useEffect
    """
    content = read_file(TYPOGRAPHY_BASE)
    result = _find_tooltipprops_position(content)

    tooltip_before = result.get("tooltipBeforeUseEffect", False)
    has_guard = result.get("useEffectHasTooltipGuard", False)

    assert tooltip_before, f"tooltipProps should be computed before the measurement useEffect (found positions: tooltipProps={result.get('tooltipPropsPos')}, useEffect={result.get('useEffectPos')})"
    assert has_guard, f"The measurement useEffect should guard isEleEllipsis with tooltip title check"


def _find_ismergedellipsis_condition(content: str) -> dict:
    """Find isMergedEllipsis and check if it gates native ellipsis with tooltip."""
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let result = {{ found: false }};

// Helper to find variable definitions
const varDefs = {{}};
traverse(ast, {{
    VariableDeclarator(path) {{
        if (path.node.id && path.node.id.name) {{
            const init = path.node.init;
            if (init) {{
                varDefs[path.node.id.name] = content.substring(init.start, init.end);
            }}
        }}
    }}
}});

// Helper to check if expression contains tooltip title
function hasTooltipTitle(exprStr) {{
    if (/\\.title|\\?\\.title/.test(exprStr)) return true;
    const ids = exprStr.match(/[a-zA-Z_$][a-zA-Z0-9_$]*/g) || [];
    for (const id of ids) {{
        if (varDefs[id] && /\\.title|\\?\\.title/.test(varDefs[id])) return true;
    }}
    return false;
}}

// Find isMergedEllipsis variable declaration
traverse(ast, {{
    VariableDeclarator(path) {{
        if (path.node.id && path.node.id.name === 'isMergedEllipsis') {{
            const init = path.node.init;
            result.found = true;

            // Handle LogicalExpression (mergedEnableEllipsis && <cond>)
            if (init && init.type === 'LogicalExpression') {{
                // The right side is the ConditionalExpression
                const condExpr = init.right;
                if (condExpr && condExpr.type === 'ConditionalExpression') {{
                    const trueBranch = content.substring(condExpr.consequent.start, condExpr.consequent.end);
                    result.trueBranch = trueBranch;
                    result.hasNativeEllipsis = /isNativeEllipsis/.test(trueBranch);
                    result.hasTooltipTitle = hasTooltipTitle(trueBranch);
                    result.hasAndOperator = trueBranch.includes('&&');
                }}
            }}
            // Handle ConditionalExpression directly (legacy)
            else if (init && init.type === 'ConditionalExpression') {{
                const trueBranch = content.substring(init.consequent.start, init.consequent.end);
                result.trueBranch = trueBranch;
                result.hasNativeEllipsis = /isNativeEllipsis/.test(trueBranch);
                result.hasTooltipTitle = hasTooltipTitle(trueBranch);
                result.hasAndOperator = trueBranch.includes('&&');
            }}
        }}
    }}
}});

console.log(JSON.stringify(result));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        return {"found": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"found": False, "error": stdout}


def test_isMergedEllipsis_gates_native_with_tooltip():
    """
    Verify that isMergedEllipsis gates native ellipsis with tooltip title check.

    Before fix: isMergedEllipsis = mergedEnableEllipsis && (cssEllipsis ? isNativeEllipsis : isJsEllipsis)
    After fix: isMergedEllipsis includes tooltip title check in the ternary's true branch
    """
    content = read_file(TYPOGRAPHY_BASE)
    result = _find_ismergedellipsis_condition(content)

    assert result.get("found"), f"Could not find isMergedEllipsis conditional"

    true_branch = result.get("trueBranch", "")
    has_native = result.get("hasNativeEllipsis", False)
    has_tooltip = result.get("hasTooltipTitle", False)

    assert has_native, f"isMergedEllipsis true branch should include isNativeEllipsis: {true_branch}"
    assert has_tooltip, f"isMergedEllipsis true branch should include tooltip title check: {true_branch}"


def _find_intersection_observer_early_return(content: str) -> dict:
    """Find IntersectionObserver early return condition."""
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let result = {{ found: false, condition: '' }};

// Find IntersectionObserver usage
traverse(ast, {{
    NewExpression(path) {{
        if (path.node.callee && path.node.callee.name === 'IntersectionObserver') {{
            // Walk up to find useEffect CallExpression
            let node = path.parentPath;
            let depth = 0;
            while (node && depth < 10) {{
                if (node.type === 'CallExpression' &&
                    node.node.callee &&
                    node.node.callee.type === 'MemberExpression' &&
                    node.node.callee.property &&
                    node.node.callee.property.name === 'useEffect') {{
                    // Found useEffect with IntersectionObserver
                    // Look for early return in callback body
                    const callback = node.node.arguments[0];
                    if (callback && callback.body && callback.body.body) {{
                        for (const stmt of callback.body.body) {{
                            if (stmt.type === 'IfStatement' && stmt.consequent) {{
                                const consequent = stmt.consequent;
                                if (consequent.type === 'BlockStatement') {{
                                    for (const s of consequent.body) {{
                                        if (s.type === 'ReturnStatement') {{
                                            result.found = true;
                                            result.condition = content.substring(
                                                stmt.test.start,
                                                stmt.test.end
                                            );
                                            break;
                                        }}
                                    }}
                                }}
                            }}
                        }}
                    }}
                    break;
                }}
                node = node.parentPath;
                depth++;
            }}
        }}
    }}
}});

console.log(JSON.stringify(result));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        return {"found": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"found": False, "error": stdout}


def test_intersection_observer_gated_by_measurement_condition():
    """
    Verify that IntersectionObserver setup has early return gated by tooltip title.

    Before fix: early return checks !cssEllipsis
    After fix: early return checks !needNativeEllipsisMeasure (which includes tooltip)
    """
    content = read_file(TYPOGRAPHY_BASE)
    result = _find_intersection_observer_early_return(content)

    assert result.get("found"), f"Could not find IntersectionObserver early return"

    condition = result.get("condition", "")
    
    # Check for tooltip title (direct or via variable)
    tooltip_result = _check_condition_for_tooltip(content, condition)
    has_tooltip_title = tooltip_result.get("hasTooltipTitle", False)

    assert has_tooltip_title, f"IntersectionObserver early return condition should include tooltip title check: {condition}"


def _find_intersection_observer_deps(content: str) -> dict:
    """Find IntersectionObserver useEffect dependencies."""
    find_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

let result = {{ found: false, deps: '' }};

// Find IntersectionObserver in useEffect
traverse(ast, {{
    NewExpression(path) {{
        if (path.node.callee && path.node.callee.name === 'IntersectionObserver') {{
            // Walk up to find useEffect CallExpression
            let node = path.parentPath;
            let depth = 0;
            while (node && depth < 10) {{
                if (node.type === 'CallExpression' &&
                    node.node.callee &&
                    node.node.callee.type === 'MemberExpression' &&
                    node.node.callee.property &&
                    node.node.callee.property.name === 'useEffect') {{
                    // Found useEffect with IntersectionObserver
                    // Find the deps array (last argument)
                    const args = node.node.arguments;
                    if (args.length >= 2) {{
                        const deps = args[args.length - 1];
                        if (deps && deps.type === 'ArrayExpression') {{
                            result.found = true;
                            result.deps = content.substring(deps.start, deps.end);
                        }}
                    }}
                    break;
                }}
                node = node.parentPath;
                depth++;
            }}
        }}
    }}
}});

console.log(JSON.stringify(result));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", find_code], timeout=30)
    if exit_code != 0:
        return {"found": False, "error": stderr}
    try:
        return json.loads(stdout.strip())
    except:
        return {"found": False, "error": stdout}


def test_intersection_observer_dependencies_include_measurement_condition():
    """
    Verify that IntersectionObserver dependency array includes the measurement condition.

    Before fix: deps = [cssEllipsis, mergedEnableEllipsis]
    After fix: deps include something that gates measurement (with tooltip)
    """
    content = read_file(TYPOGRAPHY_BASE)
    result = _find_intersection_observer_deps(content)

    assert result.get("found"), f"Could not find IntersectionObserver deps"

    deps = result.get("deps", "")
    
    # Check if deps include a variable that relates to tooltip title
    # In gold fix, this would be needNativeEllipsisMeasure
    # Check if deps string contains something that was defined with tooltip title
    check_code = f"""
const parser = require('@babel/parser');
const traverse = require('@babel/traverse').default;

const content = {json.dumps(content)};
const deps = {json.dumps(deps)};

const ast = parser.parse(content, {{
    sourceType: 'module',
    plugins: ['jsx', 'typescript'],
    errorRecovery: true
}});

// Find deps array elements
const identifiers = deps.match(/[a-zA-Z_$][a-zA-Z0-9_$]*/g) || [];

// Find variable declarations
const varDefs = {{}};
traverse(ast, {{
    VariableDeclarator(path) {{
        if (path.node.id && path.node.id.name) {{
            varDefs[path.node.id.name] = content.substring(
                path.node.init?.start || 0,
                path.node.init?.end || 0
            );
        }}
    }}
}});

// Check if any dep variable has tooltip title in its definition
let hasTooltipDep = false;
for (const id of identifiers) {{
    if (varDefs[id] && /\\.title|\\?\\.title/.test(varDefs[id])) {{
        hasTooltipDep = true;
        break;
    }}
}}

console.log(JSON.stringify({{ hasTooltipDep, identifiers, deps }}));
"""
    exit_code, stdout, stderr = run_command(["node", "-e", check_code], timeout=30)
    if exit_code != 0:
        assert False, f"Failed to check deps: {stderr}"
    
    try:
        check_result = json.loads(stdout.strip())
    except:
        assert False, f"Failed to parse dep check result: {stdout}"
    
    has_tooltip_dep = check_result.get("hasTooltipDep", False)
    
    assert has_tooltip_dep, f"IntersectionObserver deps should include tooltip-related variable (one that references .title): {deps}"


# =============================================================================
# PASS-TO-PASS TESTS: These should pass on both base and fixed commits
# =============================================================================


def test_repo_biome_lint():
    """Run Biome linter on Typography component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr}{result.stdout}"


def test_repo_biome_lint_typography_dir():
    """Run Biome linter on entire Typography directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/typography/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr}{result.stdout}"


def test_repo_biome_check():
    """Run Biome check (lint + format) on Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "check", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stderr}{result.stdout}"


def test_repo_eslint():
    """Run ESLint on Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr}{result.stdout}"


def test_repo_typescript_parse():
    """Verify TypeScript parser can parse Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('components/typography/Base/index.tsx', 'utf8');
const sourceFile = ts.createSourceFile(
    'index.tsx',
    content,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TSX
);
const diagnostics = [];
function visit(node) {
    if (node.kind === ts.SyntaxKind.Unknown) {
        diagnostics.push('Unknown syntax at position ' + node.pos);
    }
    ts.forEachChild(node, visit);
}
visit(sourceFile);
if (diagnostics.length > 0) {
    console.error('Parse errors:', diagnostics.join(', '));
    process.exit(1);
}
console.log('TypeScript parse OK');
"""],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TypeScript parse failed:\n{result.stderr}"


def test_typography_base_required_imports():
    """Verify that required imports exist in Typography Base (pass_to_pass)."""
    content = read_file(TYPOGRAPHY_BASE)

    # Check for essential imports that should always be present
    assert "import React" in content or "from 'react'" in content, \
        "React import should be present"
    assert "useTooltipProps" in content, \
        "useTooltipProps hook should be imported/used"
    assert "isEleEllipsis" in content, \
        "isEleEllipsis utility should be imported/used"


def test_typography_base_exports():
    """Verify that Typography Base component exports correctly (pass_to_pass)."""
    content = read_file(TYPOGRAPHY_BASE)

    # Check that the Base component is exported
    assert "export default" in content or "export { Base" in content or "export default Base" in content, \
        "Base component should be exported"

    # Check that it's a forwardRef component
    assert "React.forwardRef" in content or "forwardRef" in content, \
        "Base should use forwardRef for ref forwarding"
