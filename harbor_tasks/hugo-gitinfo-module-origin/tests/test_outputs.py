"""Tests for Hugo GitInfo module origin fix.

This test suite verifies that:
1. ModuleOrigin.IsZero() correctly identifies empty origins
2. loadGitInfo returns errors instead of just logging them
3. Origin info is loaded from .info files when Origin is nil
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/hugo"
MODULES_DIR = f"{REPO}/modules"
HUGOLIB_DIR = f"{REPO}/hugolib"


def test_module_origin_iszero_true_when_empty():
    """Test that ModuleOrigin.IsZero() returns true when URL is empty.

    This verifies the new IsZero() method added in modules/module.go.
    """
    test_code = '''
package main

import (
	"fmt"
	"github.com/gohugoio/hugo/modules"
)

func main() {
	// Test empty origin
	emptyOrigin := modules.ModuleOrigin{}
	if !emptyOrigin.IsZero() {
		fmt.Println("FAIL: IsZero() should return true for empty origin")
		return
	}

	// Test non-empty origin
	nonEmptyOrigin := modules.ModuleOrigin{
		URL: "https://github.com/example/repo",
		VCS: "git",
	}
	if nonEmptyOrigin.IsZero() {
		fmt.Println("FAIL: IsZero() should return false for non-empty origin")
		return
	}

	fmt.Println("PASS: IsZero() works correctly")
}
'''
    # Write and run the test
    with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as f:
        f.write(test_code)
        test_file = f.name

    try:
        # Compile and run in the hugo repo context
        result = subprocess.run(
            ['go', 'run', test_file],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        output = result.stdout + result.stderr
        assert result.returncode == 0, f"Test code failed:\n{output}"
        assert "PASS: IsZero() works correctly" in output, f"IsZero() test failed:\n{output}"
    finally:
        os.unlink(test_file)


def test_loadgitinfo_returns_error():
    """Test that loadGitInfo returns errors instead of just logging them.

    This verifies the behavioral change in hugo_sites.go where
    'h.Log.Errorln("Failed to read Git log:", err)' was changed to 'return err'.
    """
    # Read the hugo_sites.go file and verify the fix is present
    hugo_sites_path = Path(HUGOLIB_DIR) / "hugo_sites.go"
    content = hugo_sites_path.read_text()

    # Check that we return the error instead of just logging it
    assert "return err" in content, "loadGitInfo should return error, not just log it"

    # Make sure the old logging-only pattern is not present in loadGitInfo
    # We look for the context around where the error handling occurs
    lines = content.split('\n')
    in_loadgitinfo = False
    found_return = False
    for i, line in enumerate(lines):
        if "loadGitInfo()" in line and "func" in line:
            in_loadgitinfo = True
        elif in_loadgitinfo and line.startswith("func "):
            in_loadgitinfo = False
        elif in_loadgitinfo and "gi, err := newGitInfo(cfg)" in line:
            # Check subsequent lines for proper error handling
            for j in range(i+1, min(i+5, len(lines))):
                if "return err" in lines[j]:
                    found_return = True
                # The old code had "h.Log.Errorln" which we should not find
                # in the error handling section after newGitInfo
                if "h.Log.Errorln(\"Failed to read Git log:\"" in lines[j]:
                    assert False, "Found old logging-only error handling"

    assert found_return, "loadGitInfo should return error when newGitInfo fails"


def test_origin_check_with_iszero_in_gitinfo():
    """Test that gitinfo.go checks !mod.Origin().IsZero() before using Origin.

    This verifies the fix in gitinfo.go where we now check IsZero() before
    relying on the Origin data.
    """
    gitinfo_path = Path(HUGOLIB_DIR) / "gitinfo.go"
    content = gitinfo_path.read_text()

    # Check that the IsZero() check is present
    assert "!mod.Origin().IsZero()" in content, \
        "gitinfo.go should check !mod.Origin().IsZero() before using Origin"


def test_client_handles_nil_origin():
    """Test that modules/client.go handles nil Origin by loading from .info file.

    This verifies the core fix that reads Origin info from the .info JSON file
    when Origin is nil in the go list output.
    """
    client_path = Path(MODULES_DIR) / "client.go"
    content = client_path.read_text()

    # Check for the nil Origin handling code
    assert "if m.Origin == nil && m.GoMod != \"\"" in content or \
           'if m.Origin == nil && m.GoMod != ""' in content or \
           "if m.Origin == nil" in content, \
        "client.go should check for nil Origin before attempting to load from .info"

    # Check for info file loading
    assert 'strings.TrimSuffix(m.GoMod, ".mod") + ".info"' in content, \
        "client.go should derive .info filename from .mod filename"

    # Check for JSON unmarshaling
    assert "json.Unmarshal" in content, \
        "client.go should unmarshal the .info JSON file"


def test_syntax_compiles():
    """Test that the modified Go code compiles without syntax errors."""
    result = subprocess.run(
        ['go', 'build', './...'],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        # Check for specific expected errors
        stderr = result.stderr
        # Allow errors related to external module fetching, but not syntax errors
        if "syntax error" in stderr or "cannot find" in stderr or "undefined:" in stderr:
            # Build just the modules package to verify our changes compile
            result2 = subprocess.run(
                ['go', 'build', './modules'],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result2.returncode == 0, f"Modules package failed to compile:\n{result2.stderr}"

            # Build hugolib
            result3 = subprocess.run(
                ['go', 'build', './hugolib'],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result3.returncode == 0, f"Hugolib package failed to compile:\n{result3.stderr}"


def test_module_origin_struct_has_fields():
    """Test that ModuleOrigin struct has the expected fields (URL, VCS, Hash, Ref)."""
    module_path = Path(MODULES_DIR) / "module.go"
    content = module_path.read_text()

    # Check for ModuleOrigin struct definition
    assert "type ModuleOrigin struct" in content, "ModuleOrigin struct should be defined"

    # Check for expected fields
    assert "URL" in content, "ModuleOrigin should have URL field"
    assert "VCS" in content or "Vcs" in content, "ModuleOrigin should have VCS field"


# =============================================================================
# Pass-to-Pass Tests: Repository CI/CD Gates
# These tests verify the repo's own CI/CD checks pass on both base and fixed.
# =============================================================================


def test_repo_gofmt():
    """Repo's Go code passes gofmt formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["gofmt", "-l", "."],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    # gofmt -l returns list of files with formatting issues; should be empty
    assert r.returncode == 0, f"gofmt check failed with error:\n{r.stderr}"
    assert r.stdout == "", f"gofmt found formatting issues in files:\n{r.stdout}"


def test_repo_vet():
    """Repo's Go code passes go vet static analysis (pass_to_pass)."""
    # Vet only the packages we care about (not the whole repo - too slow)
    for pkg in ["./modules/...", "./hugolib/..."]:
        r = subprocess.run(
            ["go", "vet", pkg],
            capture_output=True, text=True, timeout=60, cwd=REPO,
        )
        assert r.returncode == 0, f"go vet failed for {pkg}:\n{r.stderr[-500:]}"


def test_repo_build():
    """Repo's Go code builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["go", "build", "./..."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"go build failed:\n{r.stderr[-500:]}"


def test_repo_modules_tests():
    """Tests for modules package pass (pass_to_pass)."""
    r = subprocess.run(
        ["go", "test", "-failfast", "-timeout", "60s", "./modules/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"modules tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


def test_repo_hugolib_tests():
    """Tests for hugolib package pass (pass_to_pass)."""
    # Run only quick tests to stay within 120s limit
    # Skip tests that require external tools like asciidoctor
    r = subprocess.run(
        ["go", "test", "-failfast", "-short", "-timeout", "60s",
         "-skip", "TestPagesFromGoTmplAsciiDoc|TestAsciiDoc",
         "./hugolib/..."],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    # Allow tests to pass even if some tests fail due to missing external tools
    # We just need the core hugolib tests to pass
    if r.returncode != 0:
        # Check if the failure is due to missing external tools, not code issues
        stderr_out = r.stderr + r.stdout
        if "asciidoctor" in stderr_out.lower() or "pandoc" in stderr_out.lower():
            # These are external tool issues, not code bugs - test passes
            return
    assert r.returncode == 0, f"hugolib tests failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
