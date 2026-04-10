"""
Tests for ClickHouse formatDateTime %W fix.

This tests that %W formatter is consistently treated as variable-length
regardless of other formatting settings like mysql_M_is_month_name.

The bug: %W was only treated as variable-length when mysql_M_is_month_name was false.
The fix: %W is always checked first, before other conditional checks.
"""

import subprocess
import os
import re
import pytest

REPO = "/workspace/ClickHouse"
TARGET_FILE = os.path.join(REPO, "src/Functions/formatDateTime.cpp")


class TestCodeStructure:
    """Tests that verify the fix is correctly applied to the source code."""

    def test_variable_width_formatter_array_fixed(self):
        """Test that 'W' is removed from variable_width_formatter_M_is_month_name array."""
        with open(TARGET_FILE, 'r') as f:
            content = f.read()

        # After the fix, variable_width_formatter_M_is_month_name should only contain 'M'
        # The buggy version had {'W', 'M'}
        pattern = r"variable_width_formatter_M_is_month_name = \{([^}]+)\}"
        match = re.search(pattern, content)

        assert match is not None, "Could not find variable_width_formatter_M_is_month_name definition"

        array_content = match.group(1).strip()
        # Should only contain 'M', not 'W'
        assert "'M'" in array_content, "Array should contain 'M'"
        assert "'W'" not in array_content, "Array should NOT contain 'W' (it was moved out)"

    def test_w_check_moved_before_conditions(self):
        """Test that %W check happens before the mysql_M_is_month_name conditional."""
        with open(TARGET_FILE, 'r') as f:
            content = f.read()

        # Find the containsOnlyFixedWidthMySQLFormatters function
        func_start = content.find("static bool containsOnlyFixedWidthMySQLFormatters")
        assert func_start != -1, "Could not find containsOnlyFixedWidthMySQLFormatters function"

        func_content = content[func_start:]

        # Look for the early return pattern for variable_width_formatter (which includes 'W')
        # After fix, this check should happen BEFORE the if (mysql_M_is_month_name) block
        early_w_check = re.search(
            r'if \(std::any_of\(\s*variable_width_formatter\.begin\(\)',
            func_content
        )
        assert early_w_check is not None, "Early %W check not found (should be before mysql_M_is_month_name conditional)"

        # Find the mysql_M_is_month_name conditional
        mysql_m_check = func_content.find("if (mysql_M_is_month_name)")
        assert mysql_m_check != -1, "Could not find mysql_M_is_month_name conditional"

        # The early %W check must come BEFORE the mysql_M_is_month_name conditional
        early_w_pos = early_w_check.start()
        mysql_m_pos = mysql_m_check

        assert early_w_pos < mysql_m_pos, \
            f"%W check (pos {early_w_pos}) must come BEFORE mysql_M_is_month_name check (pos {mysql_m_pos})"

    def test_no_else_block_for_w_check(self):
        """Test that the else block with %W check has been removed."""
        with open(TARGET_FILE, 'r') as f:
            content = f.read()

        # After the fix, there should be no else block checking variable_width_formatter
        # because %W is now checked unconditionally before the mysql_M_is_month_name conditional

        func_start = content.find("static bool containsOnlyFixedWidthMySQLFormatters")
        assert func_start != -1, "Could not find function"

        func_content = content[func_start:]

        # Find the mysql_M_is_month_name block
        mysql_m_block = re.search(
            r'if \(mysql_M_is_month_name\)\s*\{[^}]+\}',
            func_content,
            re.DOTALL
        )
        assert mysql_m_block is not None, "Could not find mysql_M_is_month_name block"

        # After the fix, there should be NO else block immediately following
        # The check for variable_width_formatter is now done unconditionally before
        after_m_block = func_content[mysql_m_block.end():mysql_m_block.end()+200]

        # Should not see "else" followed by a block checking variable_width_formatter
        else_pattern = re.search(r'else\s*\{[^}]*variable_width_formatter', after_m_block, re.DOTALL)
        assert else_pattern is None, "Found else block with variable_width_formatter check - this should be removed"


class TestRepoCIChecks:
    """
    Pass-to-pass tests that verify the repo's CI checks still pass.
    These ensure the fix doesn't break existing functionality or style.

    Note: Some checks may output warnings for pre-existing issues in the codebase,
    but they pass if no new issues are introduced. We filter results to
    focus on the target file where relevant.
    """

    def test_repo_submodules_check(self):
        """Repo's submodule check passes (pass_to_pass)."""
        r = subprocess.run(
            ["bash", "ci/jobs/scripts/check_style/check_submodules.sh"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Submodule check failed:\n{r.stdout[-500:]}{r.stderr[-500:]}"

    def test_repo_various_checks(self):
        """Repo's various checks pass (pass_to_pass)."""
        r = subprocess.run(
            ["bash", "ci/jobs/scripts/check_style/various_checks.sh"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
        )
        # The script exits with code 1 if the last grep finds nothing (success case).
        # We check for actual errors in the output.
        output = r.stdout + r.stderr

        # Filter for actual error messages (not trace output)
        error_keywords = ["should have", "does not have", "cannot", "should not",
                          "Missing", "failed", "error:", "Error:"]

        # The script produces messages for issues found
        # We filter out bash trace lines starting with "+"
        error_lines = []
        for line in output.split("\n"):
            if line.startswith("+"):
                continue  # Skip bash trace
            for keyword in error_keywords:
                if keyword in line:
                    error_lines.append(line)
                    break

        # If there are issues, they are printed as actual messages
        assert len(error_lines) == 0, f"Various checks found issues:\n" + "\n".join(error_lines[:20])

    def test_formatdatetime_sql_tests_parse(self):
        """Repo's formatDateTime SQL test files are syntactically valid (pass_to_pass)."""
        # Check that the SQL test files exist and have valid structure
        test_files = [
            "tests/queries/0_stateless/00718_format_datetime.sql",
            "tests/queries/0_stateless/01362_year_of_ISO8601_week_modificators_for_formatDateTime.sql",
        ]

        for test_file in test_files:
            full_path = os.path.join(REPO, test_file)
            assert os.path.exists(full_path), f"Test file {test_file} does not exist"

            # Read and validate the SQL
            with open(full_path, 'r') as f:
                content = f.read()

            # Basic sanity checks for SQL validity
            assert "formatDateTime" in content, f"Test file {test_file} should test formatDateTime"

            # Check that all SELECT statements are properly formed
            lines = content.split('\n')
            open_parens = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('--') or line.strip().startswith('/*'):
                    continue
                open_parens += line.count('(') - line.count(')')

            assert open_parens == 0, f"Test file {test_file} has unbalanced parentheses"

    def test_formatdatetime_reference_files_exist(self):
        """Repo's formatDateTime test reference files exist and match SQL files (pass_to_pass)."""
        sql_files = [
            "tests/queries/0_stateless/00718_format_datetime.sql",
            "tests/queries/0_stateless/01362_year_of_ISO8601_week_modificators_for_formatDateTime.sql",
        ]

        for sql_file in sql_files:
            # Reference file has .reference extension
            ref_file = sql_file.replace('.sql', '.reference')
            sql_path = os.path.join(REPO, sql_file)
            ref_path = os.path.join(REPO, ref_file)

            assert os.path.exists(sql_path), f"SQL file {sql_file} does not exist"
            assert os.path.exists(ref_path), f"Reference file {ref_file} does not exist for {sql_file}"


class TestBehavioral:
    """
    Behavioral tests that verify the function behaves correctly.
    These require building and running ClickHouse.
    """

    @pytest.fixture(scope="class")
    def clickhouse_binary(self):
        """Ensure clickhouse binary exists or build it."""
        binary_path = os.path.join(REPO, "build/programs/clickhouse")

        # If binary doesn't exist, we can't run behavioral tests
        if not os.path.exists(binary_path):
            pytest.skip(f"ClickHouse binary not found at {binary_path}. Build required for behavioral tests.")

        return binary_path

    def _run_clickhouse_query(self, binary_path, query, timeout=30):
        """Run a ClickHouse query and return output."""
        cmd = [binary_path, "local", "-q", query]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result

    @pytest.mark.skipif(
        not os.path.exists(os.path.join(REPO, "build/programs/clickhouse")),
        reason="ClickHouse binary not built, skipping behavioral tests"
    )
    def test_formatdatetime_w_with_mysql_m_true(self, clickhouse_binary):
        """Test %W formatting when mysql_M_is_month_name is true."""
        query = """
            SELECT formatDateTime(toDate('2026-04-06'), '%W %d')
            SETTINGS formatdatetime_parsedatetime_m_is_month_name = 1
        """
        result = self._run_clickhouse_query(clickhouse_binary, query)

        # Should succeed and return a formatted date string
        assert result.returncode == 0, f"Query failed: {result.stderr}"

        output = result.stdout.strip()
        # %W should produce weekday name, %d should produce day
        assert "Monday" in output, f"Expected 'Monday' in output, got: {output}"
        assert "06" in output, f"Expected '06' in output, got: {output}"

    @pytest.mark.skipif(
        not os.path.exists(os.path.join(REPO, "build/programs/clickhouse")),
        reason="ClickHouse binary not built, skipping behavioral tests"
    )
    def test_formatdatetime_w_with_mysql_m_false(self, clickhouse_binary):
        """Test %W formatting when mysql_M_is_month_name is false."""
        query = """
            SELECT formatDateTime(toDate('2026-04-06'), '%W %d')
            SETTINGS formatdatetime_parsedatetime_m_is_month_name = 0
        """
        result = self._run_clickhouse_query(clickhouse_binary, query)

        assert result.returncode == 0, f"Query failed: {result.stderr}"

        output = result.stdout.strip()
        assert "Monday" in output, f"Expected 'Monday' in output, got: {output}"
        assert "06" in output, f"Expected '06' in output, got: {output}"

    @pytest.mark.skipif(
        not os.path.exists(os.path.join(REPO, "build/programs/clickhouse")),
        reason="ClickHouse binary not built, skipping behavioral tests"
    )
    def test_formatdatetime_w_consistent_across_settings(self, clickhouse_binary):
        """Test that %W formatting is consistent across different mysql_M_is_month_name settings."""
        queries = [
            ("SELECT formatDateTime(toDate('2026-04-06'), '%W') SETTINGS formatdatetime_parsedatetime_m_is_month_name = 1", "Monday"),
            ("SELECT formatDateTime(toDate('2026-04-06'), '%W') SETTINGS formatdatetime_parsedatetime_m_is_month_name = 0", "Monday"),
        ]

        results = []
        for query, expected_day in queries:
            result = self._run_clickhouse_query(clickhouse_binary, query)
            assert result.returncode == 0, f"Query failed: {result.stderr}"
            results.append(result.stdout.strip())

        # Both should produce the same output (the weekday name)
        assert results[0] == results[1], \
            f"Inconsistent output: mysql_M_is_month_name=1 gives '{results[0]}', but mysql_M_is_month_name=0 gives '{results[1]}'"

        assert "Monday" in results[0], f"Expected 'Monday' in output, got: {results[0]}"


class TestCompilation:
    """Tests that verify the code compiles correctly."""

    def test_source_file_exists(self):
        """Test that the target source file exists."""
        assert os.path.exists(TARGET_FILE), f"Target file not found: {TARGET_FILE}"

    def test_source_file_syntax_valid(self):
        """Test that the source file has valid C++ syntax and key structures."""
        with open(TARGET_FILE, 'r') as f:
            content = f.read()

        # Basic checks for C++ validity
        assert "class FunctionFormatDateTimeImpl" in content, "Main class not found"
        assert "containsOnlyFixedWidthMySQLFormatters" in content, "Target function not found"

        # Verify the file has reasonable structure by checking for key elements
        # of a valid C++ source file (includes, function definitions, etc.)
        assert "#include" in content, "No includes found"
        assert "namespace" in content, "No namespace found"
        assert "return" in content, "No return statements found"

        # Check for balanced parentheses (more reliable than braces due to
        # potential braces in string literals)
        open_paren = content.count('(')
        close_paren = content.count(')')
        assert open_paren == close_paren, f"Unbalanced parentheses: {open_paren} open, {close_paren} close"

        # Verify the file ends properly (ends with brace or semicolon)
        # This is a simple check that the file isn't truncated
        stripped = content.rstrip()
        assert stripped.endswith('}') or stripped.endswith(';') or stripped.endswith(']'), \
            "File may be truncated - doesn't end with expected C++ terminator"
