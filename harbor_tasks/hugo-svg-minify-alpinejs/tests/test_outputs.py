"""
Tests for Hugo SVG minification fix.

This verifies that Alpine.js directives (x-bind and : shorthand) are preserved
when minifying SVG content.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"
MINIFIERS_DIR = os.path.join(REPO, "minifiers")

def run_go_test(test_pattern=None, timeout=120):
    """Run Go tests and return result."""
    cmd = ["go", "test", "-v", "-count=1"]
    if test_pattern:
        cmd.extend(["-run", test_pattern])
    cmd.append("./minifiers/...")

    result = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout
    )
    return result


def test_svg_minifier_preserves_alpine_x_bind():
    """Fail-to-pass: SVG minifier must preserve x-bind:href directives."""
    # Run the specific test for issue #14669
    result = run_go_test("TestBugs")

    if result.returncode != 0:
        # Check if our specific test case is failing
        if "x-bind:href" in result.stdout or "x-bind:href" in result.stderr:
            assert False, f"x-bind:href directive was stripped from SVG: {result.stdout}\n{result.stderr}"
        # If test doesn't exist yet or other failure, we need to test manually

    # Direct test: run the minifier on SVG with x-bind:href
    test_code = '''
package main

import (
    "bytes"
    "fmt"
    "os"

    "github.com/gohugoio/hugo/minifiers"
    "github.com/gohugoio/hugo/media"
    "github.com/gohugoio/hugo/output"
    "github.com/gohugoio/hugo/config/testconfig"
    "github.com/spf13/afero"
)

func main() {
    m, err := minifiers.New(media.DefaultTypes, output.DefaultFormats, testconfig.GetTestConfig(afero.NewMemMapFs(), nil))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error creating minifier: %v\\n", err)
        os.Exit(1)
    }

    input := `<use x-bind:href="myicon">`
    var b bytes.Buffer
    err = m.Minify(media.Builtin.SVGType, &b, bytes.NewBufferString(input))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error minifying: %v\\n", err)
        os.Exit(1)
    }

    output := b.String()
    if output != input {
        fmt.Fprintf(os.Stderr, "FAIL: x-bind:href was modified\\nInput:  %s\\nOutput: %s\\n", input, output)
        os.Exit(1)
    }
    fmt.Println("PASS: x-bind:href preserved")
}
'''

    # Write test file
    test_file = os.path.join(REPO, "test_alpine.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "run", "test_alpine.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            assert False, f"x-bind:href directive not preserved: {result.stderr}"
    finally:
        os.remove(test_file)


def test_svg_minifier_preserves_alpine_shorthand():
    """Fail-to-pass: SVG minifier must preserve :href shorthand (blank namespace) directives."""
    test_code = '''
package main

import (
    "bytes"
    "fmt"
    "os"

    "github.com/gohugoio/hugo/minifiers"
    "github.com/gohugoio/hugo/media"
    "github.com/gohugoio/hugo/output"
    "github.com/gohugoio/hugo/config/testconfig"
    "github.com/spf13/afero"
)

func main() {
    m, err := minifiers.New(media.DefaultTypes, output.DefaultFormats, testconfig.GetTestConfig(afero.NewMemMapFs(), nil))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error creating minifier: %v\\n", err)
        os.Exit(1)
    }

    input := `<use :href="myicon">`
    var b bytes.Buffer
    err = m.Minify(media.Builtin.SVGType, &b, bytes.NewBufferString(input))
    if err != nil {
        fmt.Fprintf(os.Stderr, "Error minifying: %v\\n", err)
        os.Exit(1)
    }

    output := b.String()
    if output != input {
        fmt.Fprintf(os.Stderr, "FAIL: :href shorthand was modified\\nInput:  %s\\nOutput: %s\\n", input, output)
        os.Exit(1)
    }
    fmt.Println("PASS: :href shorthand preserved")
}
'''

    test_file = os.path.join(REPO, "test_alpine2.go")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "run", "test_alpine2.go"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            assert False, f":href shorthand not preserved: {result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_minifiers_config_has_keep_namespaces():
    """Pass-to-pass: Verify minifiers/config.go has KeepNamespaces configured for SVG."""
    config_file = os.path.join(MINIFIERS_DIR, "config.go")
    with open(config_file, "r") as f:
        content = f.read()

    assert 'KeepNamespaces' in content, "KeepNamespaces not found in config.go"
    assert '""' in content, "Empty namespace not configured"
    assert '"x-bind"' in content, "x-bind namespace not configured"


def test_upstream_minify_version():
    """Pass-to-pass: Verify tdewolff/minify is updated to v2.24.11 or later."""
    go_mod_path = os.path.join(REPO, "go.mod")
    with open(go_mod_path, "r") as f:
        content = f.read()

    # Check for updated minify version
    assert "github.com/tdewolff/minify/v2 v2.24.11" in content, \
        "tdewolff/minify not updated to v2.24.11"


def test_alpine_variations_preserved():
    """Fail-to-pass: Test various Alpine.js directive patterns in SVG."""
    variations = [
        ('<use x-bind:href="icon">', 'x-bind:href'),
        ('<use :href="icon">', ':href shorthand'),
        ('<circle x-bind:r="radius">', 'x-bind:r'),
        ('<circle :cx="x">', ':cx shorthand'),
    ]

    for input_svg, desc in variations:
        test_code = f'''
package main

import (
    "bytes"
    "fmt"
    "os"

    "github.com/gohugoio/hugo/minifiers"
    "github.com/gohugoio/hugo/media"
    "github.com/gohugoio/hugo/output"
    "github.com/gohugoio/hugo/config/testconfig"
    "github.com/spf13/afero"
)

func main() {{
    m, err := minifiers.New(media.DefaultTypes, output.DefaultFormats, testconfig.GetTestConfig(afero.NewMemMapFs(), nil))
    if err != nil {{
        fmt.Fprintf(os.Stderr, "Error creating minifier: %v\\n", err)
        os.Exit(1)
    }}

    input := `{input_svg}`
    var b bytes.Buffer
    err = m.Minify(media.Builtin.SVGType, &b, bytes.NewBufferString(input))
    if err != nil {{
        fmt.Fprintf(os.Stderr, "Error minifying: %v\\n", err)
        os.Exit(1)
    }}

    output := b.String()
    if output != input {{
        fmt.Fprintf(os.Stderr, "FAIL: %s was modified\\nInput:  %s\\nOutput: %s\\n", "{desc}", input, output)
        os.Exit(1)
    }}
    fmt.Println("PASS: {desc} preserved")
}}
'''
        test_file = os.path.join(REPO, "test_var.go")
        with open(test_file, "w") as f:
            f.write(test_code)

        try:
            result = subprocess.run(
                ["go", "run", "test_var.go"],
                cwd=REPO,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                assert False, f"Variation failed for {desc}: {result.stderr}"
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


def test_compilation_passes():
    """Pass-to-pass: Hugo must compile after the fix."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Compilation failed: {result.stderr}"


def test_repo_gofmt():
    """Repo's Go code passes gofmt check (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # gofmt returns 0 even if it finds issues, but outputs file names
    # The check_gofmt.sh script expects empty output
    assert result.returncode == 0, f"gofmt command failed: {result.stderr}"
    assert result.stdout.strip() == "", f"gofmt found issues in files:\n{result.stdout}"


def test_repo_vet_minifiers():
    """Repo's minifiers package passes go vet (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./minifiers/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_repo_tests_minifiers():
    """Repo's minifiers package tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-count=1", "./minifiers/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"minifiers tests failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_build():
    """Repo builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Build failed:\n{result.stderr[-500:]}"


def test_repo_module_check():
    """Repo's Go modules are valid (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, f"go mod verify failed:\n{result.stderr}"
