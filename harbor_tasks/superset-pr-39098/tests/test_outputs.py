"""
Tests for apache/superset#39098 - fix(security_manager): custom auth_view issue

This PR makes registering SupersetAuthView and SupersetRegisterUserView optional.
Behavioral tests use AST parsing to verify conditional logic structure.
"""

import ast
import subprocess
import os

REPO = "/workspace/superset"


def get_manager_ast():
    manager_path = os.path.join(REPO, "superset/security/manager.py")
    with open(manager_path, "r") as f:
        return ast.parse(f.read(), filename=manager_path)


def find_superset_security_manager(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and node.name == "SupersetSecurityManager":
            return node
    return None


def find_register_views_method(cls_node):
    for item in cls_node.body:
        if isinstance(item, ast.FunctionDef) and item.name == "register_views":
            return item
    return None


def get_assignments_under_conditionals(method_node):
    """
    Return dict: {attr_name: (is_conditional, lineno)}
    For each self.xxx = ... assignment in method, check if it's under an if block.
    """
    result = {}

    class AssignmentVisitor(ast.NodeVisitor):
        def __init__(self):
            self.in_if = False
            self.if_depth = 0

        def visit_If(self, node):
            old_in_if = self.in_if
            old_depth = self.if_depth
            self.in_if = True
            self.if_depth += 1
            self.generic_visit(node)
            self.in_if = old_in_if
            self.if_depth = old_depth

        def visit_Assign(self, node):
            for target in node.targets:
                if isinstance(target, ast.Attribute):
                    if isinstance(target.value, ast.Name) and target.value.id == "self":
                        attr_name = target.attr
                        result[attr_name] = (self.in_if, node.lineno)
            self.generic_visit(node)

    visitor = AssignmentVisitor()
    visitor.visit(method_node)
    return result


def test_register_views_uses_conditionals():
    """
    Verify register_views method uses conditionals for view registration.
    Checks that auth_view and registeruser_view assignments are conditional.
    """
    tree = get_manager_ast()
    cls = find_superset_security_manager(tree)
    assert cls is not None, "SupersetSecurityManager class not found"

    method = find_register_views_method(cls)
    assert method is not None, "register_views method not found"

    assignments = get_assignments_under_conditionals(method)

    auth_conditional = assignments.get("auth_view", (False, None))[0]
    registeruser_conditional = assignments.get("registeruser_view", (False, None))[0]

    assert auth_conditional, (
        "auth_view assignment must be conditional. "
        "This is needed to allow subclasses to disable default auth view registration."
    )
    assert registeruser_conditional, (
        "registeruser_view assignment must be conditional. "
        "This is needed to allow subclasses to disable default register user view registration."
    )


def test_auth_view_assignment_is_conditional():
    tree = get_manager_ast()
    cls = find_superset_security_manager(tree)
    assert cls is not None

    method = find_register_views_method(cls)
    assert method is not None

    assignments = get_assignments_under_conditionals(method)
    auth_conditional = assignments.get("auth_view", (False, None))[0]

    assert auth_conditional, (
        "self.auth_view assignment must be conditional"
    )


def test_registeruser_view_assignment_is_conditional():
    tree = get_manager_ast()
    cls = find_superset_security_manager(tree)
    assert cls is not None

    method = find_register_views_method(cls)
    assert method is not None

    assignments = get_assignments_under_conditionals(method)
    registeruser_conditional = assignments.get("registeruser_view", (False, None))[0]

    assert registeruser_conditional, (
        "self.registeruser_view assignment must be conditional"
    )


def test_both_views_have_conditional_registration():
    tree = get_manager_ast()
    cls = find_superset_security_manager(tree)
    assert cls is not None

    method = find_register_views_method(cls)
    assert method is not None

    assignments = get_assignments_under_conditionals(method)
    auth_conditional = assignments.get("auth_view", (False, None))[0]
    registeruser_conditional = assignments.get("registeruser_view", (False, None))[0]

    assert auth_conditional and registeruser_conditional, (
        "Both auth_view and registeruser_view must have conditional registration"
    )


def test_python_syntax_valid():
    manager_path = os.path.join(REPO, "superset/security/manager.py")
    with open(manager_path, "r") as f:
        compile(f.read(), manager_path, "exec")


def test_repo_ruff_security_manager():
    result = subprocess.run(
        ["ruff", "check", "superset/security/manager.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_ruff_auth_views():
    result = subprocess.run(
        ["ruff", "check", "superset/views/auth.py"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


def test_repo_python_compile_security_module():
    import glob as globmod
    security_dir = os.path.join(REPO, "superset/security")
    py_files = globmod.glob(os.path.join(security_dir, "*.py"))
    for py_file in py_files:
        result = subprocess.run(
            ["python", "-m", "py_compile", py_file],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert result.returncode == 0, f"Compile failed for {py_file}:\n{result.stderr}"
