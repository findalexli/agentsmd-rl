"""
Task: posthog-feat-signal-safety-filtering
Repo: PostHog/posthog @ 12335b96f2209c3044a2fd623928284ab81b861d
PR:   51171

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All modified Python files must parse without errors."""
    files = [
        "products/signals/backend/temporal/safety_filter.py",
        "products/signals/backend/temporal/report_safety_judge.py",
        "products/signals/backend/temporal/buffer.py",
        "products/signals/backend/temporal/__init__.py",
        "products/signals/backend/temporal/llm.py",
        "products/signals/backend/temporal/summary.py",
        "products/signals/eval/eval_grouping_e2e.py",
        "products/signals/eval/data_spec.py",
    ]
    for f in files:
        p = Path(REPO) / f
        if p.exists():
            r = subprocess.run(
                ["python3", "-c", f"import ast; ast.parse(open('{p}').read())"],
                capture_output=True, text=True, timeout=30,
            )
            assert r.returncode == 0, f"{f} has syntax errors: {r.stderr}"


# [repo_tests] pass_to_pass
def test_ruff_check_signals():
    """Ruff linter passes on modified signals files (pass_to_pass)."""
    # Install ruff first
    r = subprocess.run(
        ["pip", "install", "ruff", "-q"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install ruff: {r.stderr}"

    # Run ruff check on modified files
    modified_files = [
        "products/signals/backend/temporal/buffer.py",
        "products/signals/backend/temporal/__init__.py",
        "products/signals/backend/temporal/llm.py",
        "products/signals/backend/temporal/summary.py",
        "products/signals/eval/eval_grouping_e2e.py",
        "products/signals/eval/data_spec.py",
    ]

    for f in modified_files:
        p = Path(REPO) / f
        if p.exists():
            r = subprocess.run(
                ["ruff", "check", str(p), "--output-format=concise"],
                capture_output=True, text=True, timeout=60, cwd=REPO,
            )
            assert r.returncode == 0, f"Ruff check failed for {f}:\n{r.stdout}\n{r.stderr}"


# [repo_tests] pass_to_pass
def test_signals_activities_registered():
    """Signals activities are properly registered in temporal module (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
sys.path.insert(0, '/workspace/posthog')

# Verify the imports work at AST level
import ast

# Check __init__.py has proper activity imports
init_path = '/workspace/posthog/products/signals/backend/temporal/__init__.py'
with open(init_path) as f:
    init_src = f.read()
    init_tree = ast.parse(init_src)

# Verify key imports exist (using new names after PR 51171 rename)
imports_found = {
    'report_safety_judge_activity': False,
    'safety_filter_activity': False,
    'summarize_signals_activity': False,
    'actionability_judge_activity': False,
    'BufferSignalsWorkflow': False,
    'SignalReportSummaryWorkflow': False,
}

for node in ast.walk(init_tree):
    if isinstance(node, ast.ImportFrom):
        for alias in node.names:
            if alias.name in imports_found:
                imports_found[alias.name] = True
    elif isinstance(node, ast.Name):
        if node.id in imports_found:
            imports_found[node.id] = True

# Check ACTIVITIES and WORKFLOWS lists exist
has_activities = 'ACTIVITIES' in init_src
has_workflows = 'WORKFLOWS' in init_src

assert has_activities, "ACTIVITIES list not found in __init__.py"
assert has_workflows, "WORKFLOWS list not found in __init__.py"

# Verify all expected imports are present
for name, found in imports_found.items():
    assert found, f"Required import '{name}' not found in __init__.py"

print("All signals activities properly registered")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Signals activities check failed:\n{r.stdout}\n{r.stderr}"
    assert "properly registered" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_safety_filter_module_structure():
    """safety_filter.py must exist with SafetyFilterInput, SafetyFilterOutput,
    SafetyFilterJudgeResponse, safety_filter_activity, and SAFETY_FILTER_PROMPT."""
    r = subprocess.run(
        ["python3", "-c", """
import ast, sys
tree = ast.parse(open('products/signals/backend/temporal/safety_filter.py').read())
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
assigns = []
for n in tree.body:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name):
                assigns.append(t.id)
required_classes = {'SafetyFilterJudgeResponse', 'SafetyFilterInput', 'SafetyFilterOutput'}
required_funcs = {'safety_filter', 'safety_filter_activity'}
missing_cls = required_classes - set(classes)
missing_fn = required_funcs - set(funcs)
assert not missing_cls, f"Missing classes: {missing_cls}"
assert not missing_fn, f"Missing functions: {missing_fn}"
assert 'SAFETY_FILTER_PROMPT' in assigns, f"Missing SAFETY_FILTER_PROMPT constant, found: {assigns}"
print("OK")
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"safety_filter.py structure check failed:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_safety_judge_renamed():
    """safety_judge.py must be renamed to report_safety_judge.py with
    renamed functions and constants."""
    old = Path(REPO) / "products/signals/backend/temporal/safety_judge.py"
    new = Path(REPO) / "products/signals/backend/temporal/report_safety_judge.py"
    assert not old.exists(), "safety_judge.py should have been renamed"
    assert new.exists(), "report_safety_judge.py must exist"

    r = subprocess.run(
        ["python3", "-c", """
import ast
tree = ast.parse(open('products/signals/backend/temporal/report_safety_judge.py').read())
funcs = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
assigns = []
for n in tree.body:
    if isinstance(n, ast.Assign):
        for t in n.targets:
            if isinstance(t, ast.Name):
                assigns.append(t.id)
assert 'report_safety_judge_activity' in funcs, f"Missing report_safety_judge_activity, found: {funcs}"
assert '_build_report_safety_judge_prompt' in funcs, f"Missing _build_report_safety_judge_prompt, found: {funcs}"
assert 'REPORT_SAFETY_JUDGE_SYSTEM_PROMPT' in assigns, f"Missing REPORT_SAFETY_JUDGE_SYSTEM_PROMPT, found: {assigns}"
# Old names must NOT be present
assert 'safety_judge_activity' not in funcs, "Old safety_judge_activity still present"
assert 'SAFETY_JUDGE_SYSTEM_PROMPT' not in assigns, "Old SAFETY_JUDGE_SYSTEM_PROMPT still present"
print("OK")
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"report_safety_judge.py check failed:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_buffer_integrates_safety_filter():
    """buffer.py must import and use safety_filter_activity to filter signals
    before flushing to S3."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
src = open('products/signals/backend/temporal/buffer.py').read()
tree = ast.parse(src)

# Check imports
imports = []
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom):
        if node.module and 'safety_filter' in node.module:
            imports.extend(alias.name for alias in node.names)
assert 'SafetyFilterInput' in imports, f"Missing SafetyFilterInput import, found: {imports}"
assert 'safety_filter_activity' in imports, f"Missing safety_filter_activity import, found: {imports}"

# Check that 'safety_filter_activity' is actually used in the code body
assert 'safety_filter_activity' in src, "safety_filter_activity not used in buffer.py body"
assert 'SafetyFilterInput' in src, "SafetyFilterInput not used in buffer.py body"
print("OK")
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"buffer.py integration check failed:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_init_registers_new_activities():
    """__init__.py must export report_safety_judge_activity and safety_filter_activity."""
    init_path = Path(REPO) / "products/signals/backend/temporal/__init__.py"
    content = init_path.read_text()
    assert "report_safety_judge_activity" in content, \
        "__init__.py must import report_safety_judge_activity"
    assert "safety_filter_activity" in content, \
        "__init__.py must import safety_filter_activity"
    # Old name must not be present
    assert "safety_judge_activity" not in content.replace("report_safety_judge_activity", ""), \
        "__init__.py still references old safety_judge_activity"


# [pr_diff] fail_to_pass
def test_empty_llm_response_error():
    """llm.py must define EmptyLLMResponseError and use it in _extract_text_content."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
src = open('products/signals/backend/temporal/llm.py').read()
tree = ast.parse(src)
classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
assert 'EmptyLLMResponseError' in classes, f"Missing EmptyLLMResponseError class, found: {classes}"

# Verify it's used in _extract_text_content (the raise statement should reference it)
assert 'EmptyLLMResponseError' in src, "EmptyLLMResponseError not used in llm.py"
# It should be raised, not ValueError
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == '_extract_text_content':
        func_src = ast.get_source_segment(src, node)
        assert 'EmptyLLMResponseError' in func_src, "_extract_text_content should raise EmptyLLMResponseError"
        break
else:
    raise AssertionError("_extract_text_content function not found")
print("OK")
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"EmptyLLMResponseError check failed:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout


# [pr_diff] fail_to_pass
def test_summary_uses_renamed_judge():
    """summary.py must import from report_safety_judge, not safety_judge."""
    content = (Path(REPO) / "products/signals/backend/temporal/summary.py").read_text()
    assert "from products.signals.backend.temporal.report_safety_judge import" in content, \
        "summary.py must import from report_safety_judge"
    assert "report_safety_judge_activity" in content, \
        "summary.py must use report_safety_judge_activity"
    # Must not use old module name (except in comments)
    lines = [l for l in content.splitlines() if not l.strip().startswith("#")]
    code_only = "\n".join(lines)
    assert "from products.signals.backend.temporal.safety_judge" not in code_only, \
        "summary.py still imports from old safety_judge module"


# ---------------------------------------------------------------------------
# Config/documentation update tests (fail_to_pass, pr_diff)
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_architecture_documents_safety_filter():
    """ARCHITECTURE.md must document the new safety_filter module including its
    threat taxonomy and buffer workflow integration."""
    arch = (Path(REPO) / "products/signals/ARCHITECTURE.md").read_text()
    # Must mention the new safety_filter function/file
    assert "safety_filter" in arch, \
        "ARCHITECTURE.md must document safety_filter"
    assert "safety_filter.py" in arch or "safety_filter()" in arch, \
        "ARCHITECTURE.md must reference safety_filter.py or safety_filter()"
    # Must describe it as per-signal (not report-level)
    assert "per-signal" in arch.lower() or "per signal" in arch.lower(), \
        "ARCHITECTURE.md must describe safety_filter as per-signal classifier"
    # Must document the threat taxonomy categories
    assert "threat" in arch.lower() and "taxonomy" in arch.lower(), \
        "ARCHITECTURE.md must mention the threat taxonomy"
    # Must distinguish from report-level safety judge
    assert "report_safety_judge" in arch or "report-level" in arch.lower(), \
        "ARCHITECTURE.md must distinguish the report-level safety judge"


# [pr_diff] fail_to_pass
def test_eval_agents_md_has_report_queries():
    """eval/AGENTS.md must have a Reports section with HogQL query templates
    for analyzing eval results."""
    agents = (Path(REPO) / "products/signals/eval/AGENTS.md").read_text()
    # Must have the Reports heading
    assert "# Reports" in agents, \
        "eval/AGENTS.md must have a '# Reports' section"
    # Must have HogQL queries section
    assert "HogQL" in agents, \
        "eval/AGENTS.md must mention HogQL queries"
    # Must include key query templates
    assert "grouping-aggregate" in agents, \
        "eval/AGENTS.md must include the grouping-aggregate query"
    assert "match-quality" in agents, \
        "eval/AGENTS.md must include the match-quality query"
    assert "malicious_leaked_rate" in agents or "malicious" in agents.lower(), \
        "eval/AGENTS.md must reference malicious leak rate metric"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_safety_filter_not_stub():
    """safety_filter.py must have real implementation, not stubs."""
    r = subprocess.run(
        ["python3", "-c", """
import ast
tree = ast.parse(open('products/signals/backend/temporal/safety_filter.py').read())
for node in ast.walk(tree):
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        if node.name in ('safety_filter', 'safety_filter_activity'):
            body = [s for s in node.body
                    if not isinstance(s, (ast.Pass, ast.Expr))
                    or (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            assert len(body) >= 3, f"{node.name} appears to be a stub (only {len(body)} statements)"
print("OK")
"""],
        cwd=REPO, capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Stub check failed:\n{r.stdout}\n{r.stderr}"
    assert "OK" in r.stdout
