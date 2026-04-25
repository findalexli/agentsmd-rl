"""Test outputs for hugo cascade-to-self bug fix."""

import subprocess
import tempfile
import os

REPO = "/workspace/hugo"


def test_cascade_frontmatter_on_regular_page():
    """Test that regular pages (leaf bundles) can have cascade frontmatter that affects themselves.

    This is a fail-to-pass test: before the fix, cascade frontmatter was only processed
    for branch nodes (sections), not regular pages. After the fix, regular pages can
    also set cascade frontmatter that applies to themselves.
    """
    # Create a test case using Hugo's integration test framework
    test_code = '''
package hugolib

import "testing"

// TestRegularPageCascadeToSelf verifies that regular pages can cascade to themselves.
// This tests the fix for issue #14627.
func TestRegularPageCascadeToSelf(t *testing.T) {
	t.Parallel()

	files := `
-- hugo.toml --
disableKinds = ['home','rss','sitemap','taxonomy','term']
environment = 'pubweb'
-- content/s1/_index.md --
---
title: s1
cascade:
  target:
    environment: pubweb
  build:
    list: never
    render: never
    publishResources: false
---
-- content/s1/p1.md --
---
title: p1
---
-- content/s2/_index.md --
---
title: s2
---
-- content/s2/p2.md --
---
title: p2
cascade:
  target:
    environment: pubweb
  build:
    list: never
    render: never
    publishResources: false
---
-- content/s2/p3/index.md --
---
title: p3
cascade:
  target:
    environment: pubweb
  build:
    list: never
    render: never
    publishResources: false
---
-- layouts/all.html --
{{ .Title }}|
`

	b := Test(t, files)

	// Section with cascade: should NOT render (cascade applies to self)
	b.AssertFileExists("public/s1/index.html", false)
	// Regular page in section with cascade: should NOT render (cascade inherited)
	b.AssertFileExists("public/s1/p1/index.html", false)

	// Section without cascade: should render normally
	b.AssertFileExists("public/s2/index.html", true)
	// Regular page with cascade in frontmatter: should NOT render (cascade applies to self)
	b.AssertFileExists("public/s2/p2/index.html", false)
	// Leaf bundle with cascade in frontmatter: should NOT render (cascade applies to self)
	b.AssertFileExists("public/s2/p3/index.html", false)
}
'''

    # Write the test file
    test_file = os.path.join(REPO, "hugolib/cascade_to_self_test.go")
    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        # Run the specific test
        result = subprocess.run(
            ["go", "test", "-v", "-run", "TestRegularPageCascadeToSelf", "./hugolib/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Clean up the test file first
        os.remove(test_file)

        # The test should pass (returncode 0) after the fix
        assert result.returncode == 0, f"TestRegularPageCascadeToSelf failed:\n{result.stdout}\n{result.stderr}"
    except Exception:
        # Ensure cleanup on any error
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_cascade_to_self_multiple_environments():
    """Test cascade targeting with multiple environment values.

    Verifies that cascade target.environment matching works correctly
    for regular pages with various environment configurations.
    """
    test_code = '''
package hugolib

import "testing"

// Test that cascade with target.environment works for regular pages with different env values
func TestRegularPageCascadeToSelfMultiEnv(t *testing.T) {
	t.Parallel()

	// Test with different environment values
	envs := []string{"prod", "staging", "dev", "testing"}

	for _, env := range envs {
		env := env // capture range variable
		t.Run(env, func(t *testing.T) {
			t.Parallel()

			files := `
-- hugo.toml --
disableKinds = ['home','rss','sitemap','taxonomy','term']
environment = '` + env + `'
-- content/page1.md --
---
title: page1
cascade:
  target:
    environment: ` + env + `
  build:
    render: never
---
-- content/page2.md --
---
title: page2
---
-- layouts/all.html --
{{ .Title }}|
`

			b := Test(t, files)

			// page1 has cascade targeting this environment - should not render
			b.AssertFileExists("public/page1/index.html", false)
			// page2 has no cascade - should render
			b.AssertFileExists("public/page2/index.html", true)
		})
	}
}
'''

    test_file = os.path.join(REPO, "hugolib/cascade_multi_env_test.go")
    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "-v", "-run", "TestRegularPageCascadeToSelfMultiEnv", "./hugolib/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180
        )

        os.remove(test_file)

        assert result.returncode == 0, f"MultiEnv test failed:\n{result.stdout}\n{result.stderr}"
    except Exception:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_cascade_frontmatter_on_regular_page_via_api():
    """Verify cascade frontmatter processing via Hugo API directly.

    This is a behavioral fail-to-pass test that exercises the page cascade
    processing through Hugo's integration test framework (similar to how
    the original bug was reported and fixed). Unlike text-matching tests,
    this executes Hugo code and verifies observable behavior: regular pages
    with cascade frontmatter targeting the current environment should have
    their build options (like render:never) respected.
    """
    test_code = '''
package hugolib

import "testing"

// TestRegularPageCascadeViaAPI verifies cascade frontmatter processing for regular pages.
// This exercises the same code path as the original bug fix without checking text patterns.
func TestRegularPageCascadeViaAPI(t *testing.T) {
	t.Parallel()

	files := `
-- hugo.toml --
disableKinds = ['home','rss','sitemap','taxonomy','term']
environment = 'testenv'
-- content/apitest/_index.md --
---
title: apitest section
---
-- content/apitest/page1.md --
---
title: page1 with cascade
cascade:
  target:
    environment: testenv
  build:
    render: never
---
-- content/apitest/page2.md --
---
title: page2 no cascade
---
-- layouts/all.html --
{{ .Title }}|
`

	b := Test(t, files)

	// page1 has cascade targeting testenv - should NOT render (build.render=never)
	b.AssertFileExists("public/apitest/page1/index.html", false)
	// page2 has no cascade - should render normally
	b.AssertFileExists("public/apitest/page2/index.html", true)
}
'''

    test_file = os.path.join(REPO, "hugolib/cascade_api_test.go")
    with open(test_file, 'w') as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["go", "test", "-v", "-run", "TestRegularPageCascadeViaAPI", "./hugolib/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        os.remove(test_file)

        assert result.returncode == 0, f"TestRegularPageCascadeViaAPI failed:\n{result.stdout}\n{result.stderr}"
    except Exception:
        if os.path.exists(test_file):
            os.remove(test_file)
        raise


def test_repo_go_test_hugolib():
    """Repo's own hugolib tests pass (pass_to_pass).

    Verifies the repository's test suite still passes after the fix.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "-run", "TestCascade", "./hugolib/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Repo cascade tests failed:\n{result.stderr[-500:]}"


def test_repo_go_build():
    """Repo builds successfully (pass_to_pass).

    Verifies the Go code compiles without errors.
    """
    result = subprocess.run(
        ["go", "build", "./..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Go build failed:\n{result.stderr}"


def test_repo_gofmt():
    """Repo code is properly formatted (pass_to_pass).

    Verifies Go code follows standard formatting conventions.
    """
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    # gofmt returns 0 even when it finds issues, check for empty output
    assert result.stdout.strip() == "", f"gofmt found formatting issues in:\n{result.stdout}"


def test_repo_go_vet():
    """Repo passes go vet static analysis (pass_to_pass).

    Verifies Go code passes static analysis checks.
    """
    result = subprocess.run(
        ["go", "vet", "./hugolib/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_repo_hugolib_unit_tests():
    """Repo's hugolib package unit tests pass (pass_to_pass).

    Verifies core hugolib functionality tests pass.
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "./hugolib/", "-timeout=120s"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"hugolib unit tests failed:\n{result.stderr[-500:]}"


def test_repo_page_tests():
    """Repo's page package tests pass (pass_to_pass).

    Verifies page-related functionality tests pass (relevant to cascade changes).
    """
    result = subprocess.run(
        ["go", "test", "-count=1", "./resources/page/...", "-timeout=120s"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"page tests failed:\n{result.stderr[-500:]}"


def test_repo_cascade_integration_tests():
    """Repo's cascade integration tests pass (pass_to_pass).

    Verifies cascade functionality works correctly across different scenarios.
    """
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "-run", "TestCascade", "./hugolib/", "-timeout=120s"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Cascade integration tests failed:\n{result.stderr[-500:]}"
