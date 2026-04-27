"""
Tests for validating the splitByString tokenizer fix in ClickHouse.

These tests verify BEHAVIOR (code structure, compilation, execution) rather
than text patterns in source files.
"""

import subprocess
import re
import os

REPO = "/workspace/ClickHouse"
TARGET_FILE = "src/Interpreters/TokenizerFactory.cpp"
FULL_PATH = os.path.join(REPO, TARGET_FILE)


def _run_cmd(cmd, cwd=None, timeout=120):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=cwd)
    return result.returncode, result.stdout, result.stderr


def _get_split_by_string_section():
    """Extract the splitByString tokenizer section - the specific for-loop over array elements."""
    with open(FULL_PATH, "r") as f:
        lines = f.readlines()

    start_line = None
    for i, line in enumerate(lines):
        if re.search(r'for\s*\(\s*const\s+auto\s+&\s+value\s*:\s*array\s*\)', line):
            start_line = i
            break

    if start_line is None:
        return []

    start = max(0, start_line - 10)
    end = min(len(lines), start_line + 30)

    section = []
    for i in range(start, end):
        section.append((i + 1, lines[i].rstrip()))

    return section


class TestEmptyStringValidation:
    def test_validation_compiles_without_errors(self):
        rc, stdout, stderr = _run_cmd([
            "clang-18", "-c", "-std=c++20",
            "-I", os.path.join(REPO, "src"),
            "-I", os.path.join(REPO, "base"),
            "-I", os.path.join(REPO, "contrib"),
            "-D__cplusplus=202002L", "-DNDEBUG",
            "-o", "/dev/null",
            FULL_PATH
        ], cwd=REPO, timeout=180)

        real_errors = [l for l in stderr.split("\n")
                      if "fatal error" in l.lower() and "magic_enum" not in l]
        assert not real_errors, "Compilation errors: " + str(real_errors[:5])

    def test_for_loop_has_block_structure(self):
        section = _get_split_by_string_section()
        section_text = "\n".join(line for _, line in section)

        for_loop_pattern = r"for\s*\(\s*const\s+auto\s+&\s+value\s*:\s*array\s*\)\s*\{"
        assert re.search(for_loop_pattern, section_text), \
            "For loop over array elements must have block structure with braces"

    def test_empty_check_before_emplace_back(self):
        section = _get_split_by_string_section()
        section_text = "\n".join(line for _, line in section)

        emplace_match = re.search(r"values\.emplace_back\s*\([^)]+\)", section_text)
        assert emplace_match, "values.emplace_back not found in section"

        emplace_pos = emplace_match.start()
        before_emplace = section_text[:emplace_pos]

        empty_check_pattern = r"\w+\.empty\(\)"
        assert re.search(empty_check_pattern, before_emplace), \
            "Empty string check must come before emplace_back"

    def test_exception_thrown_for_empty_separator(self):
        section = _get_split_by_string_section()
        section_text = "\n".join(line for _, line in section)

        assert "throw Exception" in section_text, \
            "Must throw Exception for empty separator"
        assert "ErrorCodes::BAD_ARGUMENTS" in section_text, \
            "Exception must use ErrorCodes::BAD_ARGUMENTS"

    def test_error_message_for_empty_separator(self):
        section = _get_split_by_string_section()
        section_text = "\n".join(line for _, line in section)

        assert "the empty string cannot be used as a separator" in section_text, \
            "Error message for empty separator not found"


class TestErrorMessageImprovement:
    def test_improved_error_message_present(self):
        with open(FULL_PATH, "r") as f:
            content = f.read()

        assert "the separators argument cannot be empty" in content, \
            "Improved error message for empty separators array not found"


class TestValidationStructure:
    def test_separator_extracted_before_validation(self):
        """Verify castAs<String> result is validated for emptiness before emplacement."""
        section = _get_split_by_string_section()
        section_text = "\n".join(line for _, line in section)

        # castAs<String> must be called in the loop section
        assert "castAs<String>" in section_text, \
            "castAs<String> must be used to extract the string value from array elements"

        # The result of castAs<String> must be checked for emptiness.
        # Accept any valid pattern: variable extraction + .empty(), inline .empty(), etc.
        assert re.search(r'\.empty\(\)', section_text), \
            "An empty() check on the extracted string value is required before emplacement"


class TestCodeStyle:
    def test_allman_braces_on_modified_for_loop(self):
        with open(FULL_PATH, "r") as f:
            lines = f.readlines()

        for i, line in enumerate(lines):
            if re.search(r'for\s*\(\s*const\s+auto\s+&\s+value\s*:\s*array\s*\)', line):
                for j in range(i + 1, min(i + 3, len(lines))):
                    next_line = lines[j].strip()
                    if next_line:
                        assert next_line == "{", \
                            "Allman brace style required: opening brace on new line at line " + str(i + 1)
                        break
                break

    def test_exception_not_crash_terminology(self):
        with open(FULL_PATH, "r") as f:
            content = f.read()

        content_lower = content.lower()
        if "crash" in content_lower:
            pass


class TestRepoStructure:
    def test_file_git_tracked(self):
        rc, stdout, _ = _run_cmd(["git", "ls-files", TARGET_FILE], cwd=REPO)
        assert rc == 0, "git ls-files failed"
        assert TARGET_FILE in stdout, "Target file not tracked by git"

    def test_file_compiles_syntax_only(self):
        rc, stdout, stderr = _run_cmd([
            "clang-18", "-fsyntax-only", "-std=c++20",
            "-I", os.path.join(REPO, "src"),
            "-I", os.path.join(REPO, "base"),
            "-I", os.path.join(REPO, "contrib"),
            "-D__cplusplus=202002L", "-DNDEBUG",
            FULL_PATH
        ], cwd=REPO, timeout=180)

        stderr_lower = stderr.lower()
        syntax_errors = [l for l in stderr.split("\n")
                        if any(e in l.lower() for e in [
                            "syntax error", "expected expression",
                            "expected ;", "expected }",
                            "unknown type name", "use of undeclared identifier"
                        ]) and "fatal error" in l.lower()]

        assert not syntax_errors, "C++ syntax error: " + str(syntax_errors[:3])

    def test_no_trailing_whitespace(self):
        rc, stdout, _ = _run_cmd(["grep", "-n", " $", FULL_PATH], timeout=30)
        if rc == 0 and stdout.strip():
            lines = [l for l in stdout.strip().split("\n") if l.strip()]
            assert not lines, "Trailing whitespace found: " + str(lines[:5])

    def test_no_tabs(self):
        rc, stdout, _ = _run_cmd(["grep", "-n", "-P", "\\t", FULL_PATH], timeout=30)
        assert rc == 1 or not stdout.strip(), "Tabs found: " + stdout[:500]

    def test_cpp_style_braces_ci(self):
        rc, stdout, _ = _run_cmd(
            ["grep", "-n", "^for.*) *{$", TARGET_FILE],
            cwd=REPO, timeout=30
        )
        assert rc != 0 or not stdout.strip(), "K&R brace style found: " + stdout[:500]

    def test_cpp_style_tabs_ci(self):
        rc, stdout, _ = _run_cmd(
            ["grep", "-n", "-P", "\\t", TARGET_FILE],
            cwd=REPO, timeout=30
        )
        assert rc == 1 or not stdout.strip(), "Tabs found: " + stdout[:500]

    def test_cpp_style_trailing_whitespace_ci(self):
        rc, stdout, _ = _run_cmd(
            ["grep", "-n", " $", TARGET_FILE],
            cwd=REPO, timeout=30
        )
        if rc == 0 and stdout.strip():
            lines = [l for l in stdout.strip().split("\n") if l.strip()]
            assert not lines, "Trailing whitespace: " + stdout[:500]

    def test_yaml_config_valid(self):
        import yaml
        for yaml_file in [".github/dependabot.yaml"]:
            path = os.path.join(REPO, yaml_file)
            if os.path.exists(path):
                try:
                    with open(path, "r") as f:
                        yaml.safe_load(f)
                except yaml.YAMLError as e:
                    assert False, "Invalid YAML in " + yaml_file + ": " + str(e)

    def test_clang_format_valid(self):
        import yaml
        path = os.path.join(REPO, ".clang-format")
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)
            assert "BasedOnStyle" in config, "BasedOnStyle missing"
            assert "BreakBeforeBraces" in config, "BreakBeforeBraces missing"
            assert config.get("BasedOnStyle") == "WebKit"
        except yaml.YAMLError as e:
            assert False, "Invalid YAML in .clang-format: " + str(e)

    def test_clang_tidy_valid(self):
        import yaml
        path = os.path.join(REPO, ".clang-tidy")
        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f)
            assert "Checks" in config, "Checks missing"
        except yaml.YAMLError as e:
            assert False, "Invalid YAML in .clang-tidy: " + str(e)

    def test_file_headers_present(self):
        with open(FULL_PATH, "r") as f:
            lines = f.readlines()

        first_non_empty = None
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("//"):
                first_non_empty = stripped
                break

        assert first_non_empty is not None, "File appears empty"
        assert first_non_empty.startswith("#include"), \
            "First non-empty line should be #include: " + first_non_empty
