"""
Test outputs for hugo-dedent-markers task.

Tests the DedentMarkers function and the RenderShortcodes integration
to ensure Hugo context markers don't leak when indented.
"""

import subprocess
import sys
import os

REPO = "/workspace/hugo"
HUGOCONTEXT_DIR = f"{REPO}/markup/goldmark/hugocontext"


def test_dedent_markers_function_exists():
    """Verify DedentMarkers function exists and is exported."""
    code = r"""
package main

import (
    "fmt"
    "github.com/gohugoio/hugo/markup/goldmark/hugocontext"
)

func main() {
    input := []byte("  {{__hugo_ctx pid=123}}")
    result := hugocontext.DedentMarkers(input)
    fmt.Printf("%s", result)
}
"""
    test_file = "/tmp/test_dedent_import.go"
    with open(test_file, "w") as f2:
        f2.write(code)

    result = subprocess.run(
        ["go", "run", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.remove(test_file)

    assert result.returncode == 0, f"Failed to import DedentMarkers: {result.stderr}"
    assert "{{__hugo_ctx" in result.stdout


def test_dedent_markers_strips_leading_spaces():
    """Test DedentMarkers strips leading spaces from context markers."""
    code = r"""
package main

import (
    "bytes"
    "fmt"
    "os"
    "github.com/gohugoio/hugo/markup/goldmark/hugocontext"
)

func main() {
    testCases := []struct {
        input    []byte
        expected []byte
    }{
        {[]byte("    {{__hugo_ctx pid=123}}"), []byte("{{__hugo_ctx pid=123}}")},
        {[]byte("  {{__hugo_ctx}}"), []byte("{{__hugo_ctx}}")},
    }

    for i, tc := range testCases {
        result := hugocontext.DedentMarkers(tc.input)
        if !bytes.Equal(result, tc.expected) {
            fmt.Printf("FAIL: case %d: got %q, want %q\n", i, result, tc.expected)
            os.Exit(1)
        }
    }
    fmt.Println("PASS")
}
"""
    test_file = "/tmp/test_dedent_spaces.go"
    with open(test_file, "w") as f2:
        f2.write(code)

    result = subprocess.run(
        ["go", "run", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.remove(test_file)

    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_dedent_markers_strips_leading_tabs():
    """Test DedentMarkers strips leading tabs from context markers."""
    code = r"""
package main

import (
    "bytes"
    "fmt"
    "os"
    "github.com/gohugoio/hugo/markup/goldmark/hugocontext"
)

func main() {
    input := []byte("\t\t{{__hugo_ctx end}}")
    expected := []byte("{{__hugo_ctx end}}")
    result := hugocontext.DedentMarkers(input)
    if !bytes.Equal(result, expected) {
        fmt.Printf("FAIL: got %q, want %q\n", result, expected)
        os.Exit(1)
    }
    fmt.Println("PASS")
}
"""
    test_file = "/tmp/test_dedent_tabs.go"
    with open(test_file, "w") as f2:
        f2.write(code)

    result = subprocess.run(
        ["go", "run", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.remove(test_file)

    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_dedent_markers_preserves_non_markers():
    """Test DedentMarkers preserves content without context markers."""
    code = r"""
package main

import (
    "bytes"
    "fmt"
    "os"
    "github.com/gohugoio/hugo/markup/goldmark/hugocontext"
)

func main() {
    inputs := [][]byte{
        []byte("regular text without markers"),
        []byte("    indented code block"),
    }

    for i, input := range inputs {
        result := hugocontext.DedentMarkers(input)
        if !bytes.Equal(result, input) {
            fmt.Printf("FAIL case %d: expected unchanged %q, got %q\n", i, input, result)
            os.Exit(1)
        }
    }
    fmt.Println("PASS")
}
"""
    test_file = "/tmp/test_dedent_preserve.go"
    with open(test_file, "w") as f2:
        f2.write(code)

    result = subprocess.run(
        ["go", "run", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.remove(test_file)

    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_dedent_markers_handles_multiple_markers():
    """Test DedentMarkers handles multiple markers in same content."""
    code = r"""
package main

import (
    "bytes"
    "fmt"
    "os"
    "github.com/gohugoio/hugo/markup/goldmark/hugocontext"
)

func main() {
    input := []byte("some text\n    {{__hugo_ctx pid=1}}\nmore text\n        {{__hugo_ctx /}}\nend")

    expected := []byte("some text\n{{__hugo_ctx pid=1}}\nmore text\n{{__hugo_ctx /}}\nend")

    result := hugocontext.DedentMarkers(input)
    if !bytes.Equal(result, expected) {
        fmt.Printf("FAIL: got:\n%q\nwant:\n%q\n", result, expected)
        os.Exit(1)
    }
    fmt.Println("PASS")
}
"""
    test_file = "/tmp/test_dedent_multiple.go"
    with open(test_file, "w") as f2:
        f2.write(code)

    result = subprocess.run(
        ["go", "run", test_file],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    os.remove(test_file)

    assert result.returncode == 0
    assert "PASS" in result.stdout


def test_hugolib_rendershortcodes_test():
    """Run the upstream TestRenderShortcodesCodeBlock test."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRenderShortcodesCodeBlock", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_assert_no_render_shortcodes_artifacts_exists():
    """Verify AssertNoRenderShortcodesArtifacts method exists."""
    result = subprocess.run(
        ["grep", "-r", "AssertNoRenderShortcodesArtifacts", "--include=*.go", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert "AssertNoRenderShortcodesArtifacts" in result.stdout


def test_dedent_called_in_content_toC():
    """Verify DedentMarkers is called in contentToC function."""
    result = subprocess.run(
        ["grep", "DedentMarkers", "hugolib/page__content.go"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0


# Pass-to-pass tests - verify repo's own CI checks pass on base commit


def test_repo_hugocontext_package():
    """Hugo's hugocontext package tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "./markup/goldmark/hugocontext/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_repo_hugolib_rendershortcodes():
    """Hugo's RenderShortcodes related tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestRenderShortcodes", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_repo_go_build():
    """Hugo repo builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_repo_go_vet():
    """Hugo repo passes go vet (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./markup/goldmark/hugocontext/...", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


# Additional pass-to-pass tests for CI/CD coverage


def test_repo_go_fmt():
    """Hugo's hugocontext package passes gofmt check (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=f"{REPO}/markup/goldmark/hugocontext",
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0
    assert result.stdout.strip() == "", f"Unformatted files: {result.stdout}"


def test_repo_goldmark_package():
    """Hugo's goldmark package tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["go", "test", "-v", "./markup/goldmark/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_repo_hugolib_package_build():
    """Hugo's hugolib package builds successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0


def test_repo_go_mod_verify():
    """Hugo's go.mod dependencies are consistent (pass_to_pass)."""
    result = subprocess.run(
        ["go", "mod", "verify"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0
