"""
Tests for airflow-breeze-ci-upgrade-order task.

Tests verify that the upgrade command executes CI image build AFTER Dockerfile-updating
commands run, so that update-uv-lock uses an up-to-date image.

These are BEHAVIORAL tests - they execute the upgrade function with mocked run_command
to verify the actual execution order.
"""

import ast
import subprocess
import sys
import os
from pathlib import Path

REPO = Path("/workspace/airflow")

# Script to run in subprocess to test upgrade behavior
BEHAVIORAL_TEST_SCRIPT = '''
import sys
import os
from pathlib import Path
import unittest.mock as mock

# Recorded commands
recorded = []

def mock_run_command(cmd, **kwargs):
    """Mock that records commands."""
    cmd_list = cmd if isinstance(cmd, list) else cmd.split() if isinstance(cmd, str) else []
    recorded.append(cmd_list)
    result = mock.MagicMock()
    result.returncode = 0
    result.stdout = ""
    result.stderr = ""
    return result

# Set up all mocks BEFORE importing anything from breeze
sys.modules['click'] = mock.MagicMock()
sys.modules['click'].option = lambda *a, **kw: lambda f: f
sys.modules['click'].group = lambda *a, **kw: lambda f: f
sys.modules['click'].command = lambda *a, **kw: lambda f: f
sys.modules['click'].pass_context = lambda f: f

# Create all required breeze submodules
for mod_name in [
    'airflow_breeze',
    'airflow_breeze.branch_defaults',
    'airflow_breeze.commands',
    'airflow_breeze.commands.common_options',
    'airflow_breeze.global_constants',
    'airflow_breeze.params',
    'airflow_breeze.params.shell_params',
    'airflow_breeze.utils',
    'airflow_breeze.utils.click_utils',
    'airflow_breeze.utils.console',
    'airflow_breeze.utils.custom_param_types',
    'airflow_breeze.utils.docker_command_utils',
    'airflow_breeze.utils.path_utils',
    'airflow_breeze.utils.run_utils',
    'airflow_breeze.utils.confirm',
    'github',
    'github.Repository',
]:
    sys.modules[mod_name] = mock.MagicMock()

# Set up specific mocks
sys.modules['airflow_breeze.utils.run_utils'].run_command = mock_run_command
sys.modules['airflow_breeze.utils.console'].console_print = mock.MagicMock()
sys.modules['airflow_breeze.utils.console'].get_console = mock.MagicMock()

# Mock confirm
answer_mock = mock.MagicMock()
answer_mock.YES = "yes"
answer_mock.NO = "no"
answer_mock.QUIT = "quit"
sys.modules['airflow_breeze.utils.confirm'].Answer = answer_mock
sys.modules['airflow_breeze.utils.confirm'].user_confirm = lambda x: answer_mock.YES

# Mock branch_defaults
sys.modules['airflow_breeze.branch_defaults'].AIRFLOW_BRANCH = "main"
sys.modules['airflow_breeze.branch_defaults'].DEFAULT_AIRFLOW_CONSTRAINTS_BRANCH = "constraints"

# Add breeze to path
sys.path.insert(0, "/workspace/airflow/dev/breeze/src")

# Clear any cached imports
clear_modules = [k for k in sys.modules.keys() if "airflow_breeze" in k]
for m in clear_modules:
    del sys.modules[m]

try:
    from airflow_breeze.commands.ci_commands import upgrade

    # Call upgrade with all flags enabled
    try:
        upgrade(
            target_branch="main",
            create_pr=False,
            switch_to_base=False,
            airflow_site=Path("/tmp"),
            force_k8s_schema_sync=False,
            autoupdate=True,
            update_chart_dependencies=True,
            upgrade_important_versions=True,
            update_uv_lock=True,
            k8s_schema_sync=False,
            github_token="test_token",
        )
    except SystemExit:
        pass  # Expected

    # Output recorded commands
    import json
    print("CMDS_START")
    print(json.dumps(recorded))
    print("CMDS_END")

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
'''


class TestCommandOrderingBehavioral:
    """
    Behavioral tests that verify execution order by calling the upgrade function.
    """

    def _run_behavioral_test(self):
        """
        Execute the upgrade function in a subprocess with mocked dependencies.

        Returns list of recorded commands or None if behavioral test couldn't run.
        """
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(BEHAVIORAL_TEST_SCRIPT)
            script_path = f.name

        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(REPO),
            )

            output = result.stdout + result.stderr

            # Parse the output to extract recorded commands
            lines = output.splitlines()
            recording = False
            json_data = []
            for line in lines:
                if line == "CMDS_START":
                    recording = True
                    continue
                if line == "CMDS_END":
                    recording = False
                    break
                if recording:
                    json_data.append(line)

            if json_data:
                import json
                return json.loads("".join(json_data))

            # Check if there was an error
            if "ERROR:" in output:
                return None

            return []

        except Exception as e:
            return None

        finally:
            Path(script_path).unlink(missing_ok=True)

    def _extract_sequence(self, commands):
        """Extract command type sequence from recorded commands."""
        sequence = []
        for cmd in commands:
            if not cmd:
                continue
            cmd_str = " ".join(cmd)
            if "breeze" in cmd_str and "ci-image" in cmd_str and "build" in cmd_str:
                sequence.append("build")
            elif "autoupdate" in cmd_str and "prek" in cmd_str:
                sequence.append("autoupdate")
            elif "update-chart-dependencies" in cmd_str:
                sequence.append("chart-deps")
            elif "upgrade-important-versions" in cmd_str:
                sequence.append("upgrade-versions")
            elif "update-uv-lock" in cmd_str:
                sequence.append("uv-lock")
        return sequence

    def test_dockerfile_commands_run_before_image_build(self):
        """
        Verify Dockerfile commands (autoupdate, chart-deps, upgrade-versions) run BEFORE build.

        (fail_to_pass - original code had build first)
        """
        recorded = self._run_behavioral_test()

        if recorded is None:
            # Fallback to AST
            self._test_ast_dockerfile_before_build()
            return

        sequence = self._extract_sequence(recorded)

        build_pos = None
        for i, cmd in enumerate(sequence):
            if cmd == "build":
                build_pos = i
                break

        assert build_pos is not None, "Expected 'breeze ci-image build' command"

        # Check Dockerfile commands are before build
        dockerfile_cmds = ["autoupdate", "chart-deps", "upgrade-versions"]
        for cmd_name in dockerfile_cmds:
            positions = [i for i, c in enumerate(sequence) if c == cmd_name]
            for pos in positions:
                assert pos < build_pos, (
                    f"'{cmd_name}' (pos {pos}) must run BEFORE build (pos {build_pos})"
                )

    def test_update_uv_lock_runs_after_image_build(self):
        """
        Verify update-uv-lock runs AFTER the CI image build.

        (fail_to_pass - original code had uv-lock before build)
        """
        recorded = self._run_behavioral_test()

        if recorded is None:
            self._test_ast_uv_lock_after_build()
            return

        sequence = self._extract_sequence(recorded)

        build_pos = None
        uv_lock_pos = None

        for i, cmd in enumerate(sequence):
            if cmd == "build":
                build_pos = i
            if cmd == "uv-lock":
                uv_lock_pos = i

        assert build_pos is not None, "Expected 'breeze ci-image build'"
        assert uv_lock_pos is not None, "Expected 'update-uv-lock'"
        assert build_pos < uv_lock_pos, (
            f"uv-lock (pos {uv_lock_pos}) must run AFTER build (pos {build_pos})"
        )

    def test_correct_execution_order_all_commands(self):
        """
        Verify complete order: Dockerfile commands -> build -> uv-lock.

        (fail_to_pass - verifies complete sequence)
        """
        recorded = self._run_behavioral_test()

        if recorded is None:
            self._test_ast_complete_order()
            return

        sequence = self._extract_sequence(recorded)

        dockerfile_positions = []
        build_pos = None
        uv_lock_positions = []

        for i, cmd in enumerate(sequence):
            if cmd == "build":
                build_pos = i
            elif cmd == "uv-lock":
                uv_lock_positions.append(i)
            elif cmd in ["autoupdate", "chart-deps", "upgrade-versions"]:
                dockerfile_positions.append(i)

        assert build_pos is not None, "CI image build must be called"
        assert uv_lock_positions, "update-uv-lock must be called"
        assert dockerfile_positions, "Dockerfile commands must be called"

        for pos in dockerfile_positions:
            assert pos < build_pos, f"Dockerfile cmd at {pos} should be before build at {build_pos}"
        for pos in uv_lock_positions:
            assert build_pos < pos, f"uv-lock at {pos} should be after build at {build_pos}"

    def test_all_required_commands_are_called(self):
        """
        Verify all required commands are present.

        Required: autoupdate, chart-deps, upgrade-versions, ci-image build, uv-lock.

        (fail_to_pass - verifies command set)
        """
        recorded = self._run_behavioral_test()

        if recorded is None:
            self._test_ast_all_commands()
            return

        sequence = self._extract_sequence(recorded)

        required = ["autoupdate", "chart-deps", "upgrade-versions", "build", "uv-lock"]
        for cmd in required:
            assert cmd in sequence, f"Expected '{cmd}' in sequence, got: {sequence}"

    def test_commands_run_via_run_command(self):
        """
        Verify commands are executed via run_command.

        (fail_to_pass - verifies execution method)
        """
        recorded = self._run_behavioral_test()

        if recorded is None:
            self._test_ast_run_command()
            return

        sequence = self._extract_sequence(recorded)
        assert len(sequence) >= 5, f"Expected at least 5 commands, found {len(sequence)}"

    # AST Fallback implementations
    def _get_ast_info(self):
        """Extract AST info from upgrade function."""
        content = (REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py").read_text()
        tree = ast.parse(content)

        func_node = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
                func_node = node
                break

        if func_node is None:
            return None

        # Analyze the AST structure
        info = {
            "has_pre_image_commands": False,
            "has_post_image_commands": False,
            "has_upgrade_commands": False,
            "pre_loop_before_build": False,
            "post_loop_after_build": False,
            "commands_in_lists": [],
        }

        # Look at the function body to find assignment statements and loops
        for node in func_node.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "pre_image_commands":
                            info["has_pre_image_commands"] = True
                            # Extract commands from the list
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                                        if isinstance(elt.elts[0], ast.Constant):
                                            info["commands_in_lists"].append(elt.elts[0].value)
                        elif target.id == "post_image_commands":
                            info["has_post_image_commands"] = True
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                                        if isinstance(elt.elts[0], ast.Constant):
                                            info["commands_in_lists"].append(elt.elts[0].value)
                        elif target.id == "upgrade_commands":
                            info["has_upgrade_commands"] = True
                            if isinstance(node.value, ast.List):
                                for elt in node.value.elts:
                                    if isinstance(elt, ast.Tuple) and len(elt.elts) >= 2:
                                        if isinstance(elt.elts[0], ast.Constant):
                                            info["commands_in_lists"].append(elt.elts[0].value)

        # Look for run_command calls with the list build
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                # Check if it's run_command(["breeze", "ci-image", "build"...])
                if isinstance(node.func, ast.Name) and node.func.id == "run_command":
                    if node.args and isinstance(node.args[0], ast.List):
                        elements = []
                        for elt in node.args[0].elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                elements.append(elt.value)
                        if elements == ["breeze", "ci-image", "build", "--python", "3.10"]:
                            info["has_build_list_call"] = True

        # Check structure: look for the order of for loops and build call
        # Get source to check relative positions of loops
        lines = content.splitlines()
        func_start = func_node.lineno - 1
        func_end = func_node.end_lineno
        func_lines = lines[func_start:func_end]

        # Find line numbers of key constructs
        pre_loop_line = None
        post_loop_line = None
        build_line = None

        for i, line in enumerate(func_lines):
            if "for step_name, command in pre_image_commands" in line:
                pre_loop_line = i
            if "for step_name, command in post_image_commands" in line:
                post_loop_line = i
            if '["breeze", "ci-image", "build"' in line:
                build_line = i

        if pre_loop_line is not None and build_line is not None:
            info["pre_loop_before_build"] = pre_loop_line < build_line

        if post_loop_line is not None and build_line is not None:
            info["post_loop_after_build"] = post_loop_line > build_line

        return info

    def _test_ast_dockerfile_before_build(self):
        """AST-based test for Dockerfile commands before build."""
        info = self._get_ast_info()
        assert info is not None, "Could not find upgrade function"

        # Fixed version: has pre_image_commands and the loop runs before build
        if info["has_pre_image_commands"]:
            assert info["pre_loop_before_build"], (
                "pre_image_commands loop should execute before 'breeze ci-image build'"
            )
        elif info["has_upgrade_commands"]:
            # Broken version: only has upgrade_commands, build comes before the loop
            # This is what fails for the base code
            raise AssertionError(
                "Base code uses 'upgrade_commands' without pre/post split - "
                "commands run after build. This is the bug."
            )

    def _test_ast_uv_lock_after_build(self):
        """AST-based test for uv-lock after build."""
        info = self._get_ast_info()
        assert info is not None

        # Fixed version has post_image_commands with the loop after build
        if info["has_post_image_commands"]:
            assert info["post_loop_after_build"], (
                "post_image_commands loop should execute after 'breeze ci-image build'"
            )
            assert "update-uv-lock" in info["commands_in_lists"], (
                "update-uv-lock should be in post_image_commands"
            )
        else:
            # Broken version - no post_image_commands, so uv-lock runs with others
            raise AssertionError(
                "Base code has no post_image_commands - update-uv-lock runs before build. "
                "This is the bug."
            )

    def _test_ast_complete_order(self):
        """AST-based test for complete order."""
        info = self._get_ast_info()
        assert info is not None

        # Fixed version has both pre and post loops with correct order
        if info["has_pre_image_commands"] and info["has_post_image_commands"]:
            assert info["pre_loop_before_build"] and info["post_loop_after_build"], (
                "Expected: pre loop -> build -> post loop"
            )
        else:
            raise AssertionError(
                "Base code doesn't have proper pre/post command split - this is the bug."
            )

    def _test_ast_all_commands(self):
        """AST-based test that all required commands are present."""
        info = self._get_ast_info()
        assert info is not None

        required = ["autoupdate", "update-chart-dependencies", "upgrade-important-versions", "update-uv-lock"]
        for cmd in required:
            assert cmd in info["commands_in_lists"], f"Expected '{cmd}' in command lists"

    def _test_ast_run_command(self):
        """AST-based test for run_command usage."""
        info = self._get_ast_info()
        assert info is not None

        # Just verify commands are in the lists that get executed via run_command
        assert len(info["commands_in_lists"]) >= 4, (
            f"Expected at least 4 commands in lists, found {len(info['commands_in_lists'])}"
        )


class TestFileStructure:
    """Tests for basic file structure (pass_to_pass tests)."""

    def test_file_syntax_valid(self):
        """ci_commands.py has valid Python syntax."""
        content = (REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py").read_text()
        try:
            ast.parse(content)
        except SyntaxError as e:
            raise AssertionError(f"ci_commands.py has invalid Python syntax: {e}")

    def test_upgrade_function_exists(self):
        """The upgrade function exists."""
        content = (REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py").read_text()
        tree = ast.parse(content)

        upgrade_found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "upgrade":
                upgrade_found = True
                break

        assert upgrade_found, "Expected 'upgrade' function to exist"


class TestCodeQuality:
    """Tests for code quality (pass_to_pass tests)."""

    def test_ruff_lint_passes(self):
        """ci_commands.py passes ruff lint checks."""
        result = subprocess.run(
            ["ruff", "check", str(REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py")],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"ruff lint failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_format_passes(self):
        """ci_commands.py passes ruff format checks."""
        result = subprocess.run(
            ["ruff", "format", "--check", str(REPO / "dev/breeze/src/airflow_breeze/commands/ci_commands.py")],
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, f"ruff format check failed:\n{result.stdout}\n{result.stderr}"

    def test_breeze_commands_dir_lint(self):
        """All files in breeze commands directory pass ruff lint."""
        commands_dir = REPO / "dev/breeze/src/airflow_breeze/commands"
        result = subprocess.run(
            ["ruff", "check", str(commands_dir)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"ruff lint on commands dir failed:\n{result.stdout}\n{result.stderr}"
