"""
Task: pytorch-graphpickler-ignorerawnode-tests
Repo: pytorch/pytorch @ e931ab4802816cec55aa5a25b51f27cb941c924e
PR:   176954

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import json
import subprocess
from pathlib import Path

REPO = "/workspace/pytorch"
TARGET = f"{REPO}/test/fx/test_graph_pickler.py"


def _run_py(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute Python code via subprocess."""
    return subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=timeout,
    )


def _source():
    return Path(TARGET).read_text()


def _tree():
    return ast.parse(_source())


def _find_agent_test_methods():
    """Return test methods in classes that reference ignore_raw_node."""
    result = []
    for node in ast.walk(_tree()):
        if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                    result.append(item)
    for node in ast.iter_child_nodes(_tree()):
        if (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
                and "ignore_raw_node" in ast.dump(node)):
            result.append(node)
    return result


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Target test file must compile without syntax errors."""
    r = _run_py(f"compile(open('{TARGET}').read(), '{TARGET}', 'exec')")
    assert r.returncode == 0, f"Syntax error: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI/CD validation
def test_p2p_repo_ast_valid():
    """Repo test file must have valid AST (pass_to_pass)."""
    r = _run_py(f'''
import ast
try:
    with open("{TARGET}") as f:
        ast.parse(f.read())
    print("OK")
except SyntaxError as e:
    print(f"SyntaxError: {{e}}")
''')
    assert r.returncode == 0 and "OK" in r.stdout, f"AST validation failed: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI/CD validation
def test_p2p_repo_imports_parse():
    """Repo test file imports must be syntactically valid (pass_to_pass)."""
    r = _run_py(f'''
import ast
with open("{TARGET}") as f:
    tree = ast.parse(f.read())

imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
print(f"Found {{len(imports)}} import statements")
print("OK")
''')
    assert r.returncode == 0 and "OK" in r.stdout, f"Import parsing failed: {r.stderr}"


# [repo_tests] pass_to_pass - repo CI py_compile
def test_p2p_repo_py_compile():
    """Repo test file must compile via py_compile (CI/CD build gate)."""
    r = subprocess.run(
        ["python3", "-m", "py_compile", TARGET],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"py_compile failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - repo CI lint: Owner label check
def test_p2p_repo_owner_label():
    """Repo test file must have valid # Owner(s): label (CI linting gate)."""
    r = subprocess.run(
        ["python3", "-c",
         f"import re; import sys; content=open('{TARGET}').read(); match=re.search(r'#\\s*Owner\\(s\\):\\s*\\[([^\\]]+)\\]', content); sys.exit(0 if (match and 'module: unknown' not in match.group(1)) else 1)"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Owner label check failed: file must have '# Owner(s): [module: fx]' or similar"


# [repo_tests] pass_to_pass - repo CI lint: run_tests pattern check
def test_p2p_repo_has_main_run_tests():
    """Repo test file must have 'if __name__ == __main__: run_tests()' (CI linting gate)."""
    code = f'''
import ast
import sys
tree = ast.parse(open("{TARGET}").read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.If):
        test = node.test
        if (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name)
                and test.left.id == "__name__"
                and len(test.ops) == 1
                and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"):
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Call)
                        and isinstance(stmt.func, ast.Name)
                        and stmt.func.id == "run_tests"):
                    found = True
                    break
sys.exit(0 if found else 1)
'''
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"run_tests pattern check failed: file must end with 'if __name__ == \"__main__\": run_tests()'"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) - core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_has_ignore_raw_node_tests():
    """Agent must add at least one test method that exercises ignore_raw_node."""
    r = _run_py(f'''
import ast, json
tree = ast.parse(open("{TARGET}").read())
methods = []
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                methods.append(item.name)
for node in ast.iter_child_nodes(tree):
    if (isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
            and "ignore_raw_node" in ast.dump(node)):
        methods.append(node.name)
print(json.dumps(methods))
''')
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    methods = json.loads(r.stdout.strip())
    assert len(methods) >= 1, (
        "No test methods found that reference ignore_raw_node - "
        "add tests for GraphPickler.Options(ignore_raw_node=...)"
    )


# [pr_diff] fail_to_pass
def test_default_raises_covered():
    """A test must verify GraphPickler.dumps raises by default on raw Node metadata."""
    r = _run_py(f'''
import ast, json
tree = ast.parse(open("{TARGET}").read())
found = False
for node in ast.walk(tree):
    if isinstance(node, ast.ClassDef) and "ignore_raw_node" in ast.dump(node):
        for item in node.body:
            if isinstance(item, ast.FunctionDef) and item.name.startswith("test_"):
                dump = ast.dump(item)
                if ("assertRaises" in dump or "assertRaisesRegex" in dump) and "dumps" in dump:
                    found = True
print(json.dumps(found))
''')
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    found = json.loads(r.stdout.strip())
    assert found, (
        "No test method covers the default-raises behavior: "
        "expected assertRaises/assertRaisesRegex + GraphPickler.dumps call"
    )


# [pr_diff] fail_to_pass
def test_ignore_true_round_trip():
    """A test must verify the ignore_raw_node=True round-trip (dumps then loads)."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, "No test methods found"
    for m in methods:
        dump = ast.dump(m)
        if "ignore_raw_node" in dump and "loads" in dump:
            return
    assert False, (
        "No test method tests the ignore_raw_node=True round-trip: "
        "expected a test that passes Options(ignore_raw_node=True) and calls loads()"
    )


# [pr_diff] fail_to_pass
def test_raw_node_in_meta():
    """Tests must inject a raw Node into node.meta to trigger the code path."""
    r = _run_py(f'''
import ast, json
tree = ast.parse(open("{TARGET}").read())
found = False
for cls in ast.walk(tree):
    if not isinstance(cls, ast.ClassDef):
        continue
    if "ignore_raw_node" not in ast.dump(cls):
        continue
    for child in ast.walk(cls):
        if (isinstance(child, ast.Assign)
                and child.targets
                and isinstance(child.targets[0], ast.Subscript)
                and isinstance(child.targets[0].value, ast.Attribute)
                and child.targets[0].value.attr == "meta"):
            found = True
print(json.dumps(found))
''')
    assert r.returncode == 0, f"Analysis failed: {r.stderr}"
    found = json.loads(r.stdout.strip())
    assert found, (
        "No assignment into node.meta found in agent's test code - "
        "tests must inject a raw Node (e.g. call_node.meta['key'] = call_node) "
        "to exercise the ignore_raw_node code path"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) - anti-stub + structural
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_not_stub():
    """Agent must have >=2 test methods with real assertions and at least one pickler call."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 2, f"Found {len(methods)} test method(s), need >= 2"

    for m in methods:
        has_assert = any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and "assert" in child.func.attr.lower()
            for child in ast.walk(m)
        ) or any(isinstance(child, ast.Assert) for child in ast.walk(m))
        assert has_assert, f"{m.name} has no assertions (stub)"

        stmt_count = sum(
            1 for child in ast.walk(m)
            if isinstance(child, (ast.Assign, ast.Expr, ast.Assert, ast.With, ast.If))
        )
        assert stmt_count >= 3, f"{m.name} has only {stmt_count} statements (trivial)"

    any_pickler = any(
        "dumps" in ast.dump(m) or "loads" in ast.dump(m) for m in methods
    )
    assert any_pickler, "No test method calls dumps or loads - not testing pickling"


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass - CLAUDE.md:17-27 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_pytorch_test_class():
    """Tests must use PyTorch's TestCase (not unittest.TestCase) - CLAUDE.md:17-27."""
    agent_classes = [
        n for n in ast.walk(_tree())
        if isinstance(n, ast.ClassDef) and "ignore_raw_node" in ast.dump(n)
    ]
    assert len(agent_classes) > 0, "No test class found for ignore_raw_node feature"

    for cls in agent_classes:
        for base in cls.bases:
            if (isinstance(base, ast.Attribute) and base.attr == "TestCase"
                    and isinstance(base.value, ast.Name)
                    and base.value.id == "unittest"):
                assert False, (
                    f"{cls.name} uses unittest.TestCase; "
                    "use TestCase from torch.testing._internal.common_utils - CLAUDE.md:17-27"
                )
        good = any(isinstance(b, ast.Name) and b.id == "TestCase" for b in cls.bases)
        assert good, (
            f"{cls.name} must inherit from TestCase "
            "(from torch.testing._internal.common_utils) - CLAUDE.md:17-27"
        )


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:57 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_has_owner_label():
    """Test file must have a valid # Owner(s): label, not 'module: unknown'."""
    import re
    src = _source()
    match = re.search(r"#\s*Owner\(s\):\s*\[([^\]]*)\]", src)
    assert match, (
        "Test file is missing a '# Owner(s): [...]' label - "
        "see review-checklist.md:57"
    )
    owners = match.group(1)
    assert "module: unknown" not in owners, (
        "# Owner(s) label must not be 'module: unknown' - "
        "see review-checklist.md:57"
    )


# [agent_config] pass_to_pass - .claude/skills/pr-review/review-checklist.md:60 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_has_run_tests():
    """Test file must end with 'if __name__ == \"__main__\": run_tests()'."""
    tree = _tree()
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        test = node.test
        if (isinstance(test, ast.Compare)
                and isinstance(test.left, ast.Name) and test.left.id == "__name__"
                and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq)
                and len(test.comparators) == 1
                and isinstance(test.comparators[0], ast.Constant)
                and test.comparators[0].value == "__main__"):
            for stmt in ast.walk(node):
                if (isinstance(stmt, ast.Call)
                        and isinstance(stmt.func, ast.Name)
                        and stmt.func.id == "run_tests"):
                    return
    assert False, (
        "Test file must end with 'if __name__ == \"__main__\": run_tests()' - "
        "see review-checklist.md:60"
    )


# [agent_config] fail_to_pass - .claude/skills/pr-review/review-checklist.md:68 @ e931ab4802816cec55aa5a25b51f27cb941c924e
def test_uses_assert_raises_for_errors():
    """Error tests must use assertRaises/assertRaisesRegex, not bare try/except - review-checklist.md:68."""
    methods = _find_agent_test_methods()
    assert len(methods) >= 1, "No test methods found"

    found = any(
        "assertRaises" in ast.dump(m) or "assertRaisesRegex" in ast.dump(m)
        for m in methods
    )
    assert found, (
        "No test method uses assertRaises/assertRaisesRegex for the error path - "
        "see review-checklist.md:68"
    )
