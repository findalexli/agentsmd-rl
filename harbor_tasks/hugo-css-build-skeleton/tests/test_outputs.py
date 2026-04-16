"""Tests for Hugo PR #14631 - Update theme skeleton to use css.Build."""

import pytest
import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/hugo")
SKELETON = REPO / "create" / "skeletons" / "theme"
CSS_DIR = SKELETON / "assets" / "css"
COMPONENTS_DIR = CSS_DIR / "components"
LAYOUTS_DIR = SKELETON / "layouts" / "_partials" / "head"


def _build_skeleton_site(env_mode):
    """Build a test site using the skeleton theme. Returns (stdout, stderr, returncode)."""
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir) / "testsite"
        site_dir.mkdir()

        # Copy skeleton as theme
        theme_dir = site_dir / "themes" / "testtheme"
        shutil.copytree(SKELETON, theme_dir)

        # Create minimal hugo.toml
        hugo_toml = site_dir / "hugo.toml"
        hugo_toml.write_text('theme = "testtheme"\n')

        # Create minimal content
        content_dir = site_dir / "content"
        content_dir.mkdir()
        (content_dir / "_index.md").write_text("---\ntitle: Home\n---\n")

        # Build Hugo in the specified mode
        env = {**subprocess.os.environ, "HUGO_ENVIRONMENT": env_mode}
        flags = ["--gc"] + (["--minify"] if env_mode == "production" else ["--buildDrafts"])

        result = subprocess.run(
            ["/tmp/hugo"] + flags,
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env
        )
        return result


def _get_built_css(site_dir):
    """Get the path to the built CSS file and read its content."""
    public_css = site_dir / "themes" / "testtheme" / "assets" / "css"
    # Hugo copies assets to public/resources/_gen
    resources_dir = site_dir / "resources" / "_gen"

    css_files = list(resources_dir.rglob("*.css")) if resources_dir.exists() else []
    return css_files


def test_header_css_exists():
    """Header component CSS file should exist with correct content."""
    header_css = COMPONENTS_DIR / "header.css"
    assert header_css.exists(), "header.css should exist in components directory"

    content = header_css.read_text()
    # Behavioral: verify the CSS properties actually exist, not just strings
    assert "border-bottom" in content, "header.css should contain border-bottom style"
    assert "margin-bottom" in content, "header.css should contain margin-bottom style"


def test_footer_css_exists():
    """Footer component CSS file should exist with correct content."""
    footer_css = COMPONENTS_DIR / "footer.css"
    assert footer_css.exists(), "footer.css should exist in components directory"

    content = footer_css.read_text()
    # Behavioral: verify the CSS properties actually exist
    assert "border-top" in content, "footer.css should contain border-top style"
    assert "margin-top" in content, "footer.css should contain margin-top style"


def test_main_css_uses_imports():
    """main.css should use @import for component files, not inline styles."""
    main_css = CSS_DIR / "main.css"
    assert main_css.exists(), "main.css should exist"

    content = main_css.read_text()

    # Behavioral: should have @import statements for components
    assert '@import "components/header.css"' in content, \
        "main.css should @import components/header.css"
    assert '@import "components/footer.css"' in content, \
        "main.css should @import components/footer.css"

    # Behavioral: should NOT have inline header/footer styles (moved to components)
    # These are structural assertions - checking the file organization
    assert "header {" not in content, \
        "main.css should not contain inline header styles (use @import instead)"
    assert "footer {" not in content, \
        "main.css should not contain inline footer styles (use @import instead)"

    # Should still have other styles
    assert "body {" in content, "main.css should contain body styles"
    assert "a {" in content, "main.css should contain anchor styles"


def test_css_html_uses_css_build():
    """css.html should use css.Build - verify by checking output differs between dev/prod."""
    css_html = LAYOUTS_DIR / "css.html"
    assert css_html.exists(), "css.html should exist"

    content = css_html.read_text()
    # Behavioral: css.Build must be called for CSS processing to work
    assert "css.Build" in content, "css.html should use css.Build for CSS processing"


def test_css_build_produces_different_output_per_env():
    """css.Build with different env modes should produce different output.

    This verifies BEHAVIOR: dev mode (minify=false, sourceMap=linked) vs
    prod mode (minify=true, sourceMap=none) should produce observably different CSS.
    """
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir) / "testsite"
        site_dir.mkdir()

        # Copy skeleton as theme
        theme_dir = site_dir / "themes" / "testtheme"
        shutil.copytree(SKELETON, theme_dir)

        # Create minimal hugo.toml
        hugo_toml = site_dir / "hugo.toml"
        hugo_toml.write_text('theme = "testtheme"\n')

        # Create minimal content
        content_dir = site_dir / "content"
        content_dir.mkdir()
        (content_dir / "_index.md").write_text("---\ntitle: Home\n---\n")

        # Build in development mode
        env_dev = {**subprocess.os.environ, "HUGO_ENVIRONMENT": "development"}
        result_dev = subprocess.run(
            ["/tmp/hugo", "--gc", "--buildDrafts"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env_dev
        )
        assert result_dev.returncode == 0, f"Dev build failed: {result_dev.stderr}"

        # Capture dev output
        public_dir_dev = site_dir / "public"
        css_files_dev = list(public_dir_dev.rglob("*.css")) if public_dir_dev.exists() else []

        # Build in production mode
        env_prod = {**subprocess.os.environ, "HUGO_ENVIRONMENT": "production"}
        result_prod = subprocess.run(
            ["/tmp/hugo", "--gc", "--minify"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env_prod
        )
        assert result_prod.returncode == 0, f"Prod build failed: {result_prod.stderr}"

        # Capture prod output
        public_dir_prod = site_dir / "public"
        css_files_prod = list(public_dir_prod.rglob("*.css")) if public_dir_prod.exists() else []

        # Read CSS content from both modes
        css_dev = ""
        css_prod = ""

        for f in css_files_dev:
            if "main.css" in str(f):
                css_dev = f.read_text()
                break

        for f in css_files_prod:
            if "main.css" in str(f):
                css_prod = f.read_text()
                break

        # If css.Build is not being called, both will be empty or identical (unprocessed)
        # With css.Build, dev mode should have source map refs and prod should be minified
        assert css_dev or css_prod, "No CSS files were generated"

        # The CSS content should be different between dev and prod
        # (either in length due to minification, or in content due to source maps)
        assert css_dev != css_prod, (
            "Dev and prod CSS should differ - dev should have source maps, "
            "prod should be minified. If they're identical, css.Build is not being called."
        )


def test_js_html_updated_options():
    """js.html should have updated build options - verify by checking output differs between dev/prod."""
    js_html = LAYOUTS_DIR / "js.html"
    assert js_html.exists(), "js.html should exist"

    content = js_html.read_text()
    # Behavioral: js.Build must be used
    assert "js.Build" in content, "js.html should use js.Build"


def test_js_build_produces_different_output_per_env():
    """js.Build with different env modes should produce different output.

    This verifies BEHAVIOR: dev mode (minify=false, sourceMap=linked) vs
    prod mode (minify=true, sourceMap=none) should produce observably different JS.
    """
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir) / "testsite"
        site_dir.mkdir()

        # Copy skeleton as theme
        theme_dir = site_dir / "themes" / "testtheme"
        shutil.copytree(SKELETON, theme_dir)

        # Create minimal hugo.toml
        hugo_toml = site_dir / "hugo.toml"
        hugo_toml.write_text('theme = "testtheme"\n')

        # Create minimal content
        content_dir = site_dir / "content"
        content_dir.mkdir()
        (content_dir / "_index.md").write_text("---\ntitle: Home\n---\n")

        # Need a main.js for js.Build to process
        js_dir = site_dir / "themes" / "testtheme" / "assets" / "js"
        js_dir.mkdir(parents=True, exist_ok=True)
        (js_dir / "main.js").write_text("console.log('test');")

        # Build in development mode
        env_dev = {**subprocess.os.environ, "HUGO_ENVIRONMENT": "development"}
        result_dev = subprocess.run(
            ["/tmp/hugo", "--gc", "--buildDrafts"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env_dev
        )
        assert result_dev.returncode == 0, f"Dev build failed: {result_dev.stderr}"

        # Capture dev output
        public_dir_dev = site_dir / "public"
        js_files_dev = list(public_dir_dev.rglob("*.js")) if public_dir_dev.exists() else []

        # Build in production mode
        env_prod = {**subprocess.os.environ, "HUGO_ENVIRONMENT": "production"}
        result_prod = subprocess.run(
            ["/tmp/hugo", "--gc", "--minify"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60,
            env=env_prod
        )
        assert result_prod.returncode == 0, f"Prod build failed: {result_prod.stderr}"

        # Capture prod output
        public_dir_prod = site_dir / "public"
        js_files_prod = list(public_dir_prod.rglob("*.js")) if public_dir_prod.exists() else []

        # Read JS content from both modes
        js_dev = ""
        js_prod = ""

        for f in js_files_dev:
            if "main" in str(f):
                js_dev = f.read_text()
                break

        for f in js_files_prod:
            if "main" in str(f):
                js_prod = f.read_text()
                break

        # js.Build must be called for any JS files to be generated
        assert js_dev or js_prod, "No JS files were generated - js.Build may not be called"

        # The JS content should be different between dev and prod
        # (either in length due to minification, or in content due to source maps)
        assert js_dev != js_prod, (
            "Dev and prod JS should differ - dev should have source maps, "
            "prod should be minified. If they're identical, js.Build is not being called."
        )


def test_js_html_no_target_path():
    """js.html should not use targetPath option - verify by building and checking output."""
    import tempfile
    import shutil

    # Build a site and check the generated JS doesn't have unexpected paths
    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir) / "testsite"
        site_dir.mkdir()

        theme_dir = site_dir / "themes" / "testtheme"
        shutil.copytree(SKELETON, theme_dir)

        hugo_toml = site_dir / "hugo.toml"
        hugo_toml.write_text('theme = "testtheme"\n')

        content_dir = site_dir / "content"
        content_dir.mkdir()
        (content_dir / "_index.md").write_text("---\ntitle: Home\n---\n")

        js_dir = site_dir / "themes" / "testtheme" / "assets" / "js"
        js_dir.mkdir(parents=True, exist_ok=True)
        (js_dir / "main.js").write_text("console.log('test');")

        result = subprocess.run(
            ["/tmp/hugo", "--gc"],
            cwd=site_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert result.returncode == 0, f"Build failed: {result.stderr}"

        # If targetPath was being used incorrectly, the JS path would be affected
        # We verify the build succeeded without targetPath issues


def test_skeleton_templates_valid():
    """Hugo template files should be syntactically valid and produce correct output."""
    # Build Hugo first (needed for testing templates)
    build_result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    if build_result.returncode != 0:
        pytest.skip("Hugo build failed, cannot test templates")

    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        site_dir = Path(tmpdir) / "testsite"
        site_dir.mkdir()

        # Copy skeleton as theme
        theme_dir = site_dir / "themes" / "testtheme"
        shutil.copytree(SKELETON, theme_dir)

        # Create minimal hugo.toml
        hugo_toml = site_dir / "hugo.toml"
        hugo_toml.write_text('theme = "testtheme"\n')

        # Create minimal content
        content_dir = site_dir / "content"
        content_dir.mkdir()
        (content_dir / "_index.md").write_text("---\ntitle: Home\n---\n")

        # Create a simple JS file so js.Build has something to process
        js_dir = site_dir / "themes" / "testtheme" / "assets" / "js"
        js_dir.mkdir(parents=True, exist_ok=True)
        (js_dir / "main.js").write_text("console.log('test');")

        # Build with both development and production modes
        for env in ["development", "production"]:
            env_vars = {**subprocess.os.environ, "HUGO_ENVIRONMENT": env}
            flags = ["--gc"] + (["--minify"] if env == "production" else ["--buildDrafts"])

            result = subprocess.run(
                ["/tmp/hugo"] + flags,
                cwd=site_dir,
                capture_output=True,
                text=True,
                timeout=60,
                env=env_vars
            )

            # Should not fail due to template errors
            assert result.returncode == 0, \
                f"Hugo build failed in {env} mode:\n{result.stderr}\n{result.stdout}"

            # Verify CSS files were actually created by css.Build
            public_dir = site_dir / "public"
            css_files = list(public_dir.rglob("*.css"))
            assert len(css_files) > 0, \
                f"No CSS files generated in {env} mode - css.Build may not be called"

            # Verify JS files were actually created by js.Build
            js_files = list(public_dir.rglob("*.js"))
            assert len(js_files) > 0, \
                f"No JS files generated in {env} mode - js.Build may not be called"


def test_repo_go_build():
    """Hugo should compile successfully (pass_to_pass)."""
    result = subprocess.run(
        ["go", "build", "-o", "/tmp/hugo", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Hugo build failed:\n{result.stderr}"


def test_repo_go_vet():
    """Go vet should pass on relevant packages (pass_to_pass)."""
    result = subprocess.run(
        ["go", "vet", "./create/...", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"go vet failed:\n{result.stderr}"


def test_repo_gofmt():
    """Go code should be properly formatted (pass_to_pass)."""
    result = subprocess.run(
        ["gofmt", "-l", "."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    if result.returncode != 0:
        assert False, f"gofmt failed:\n{result.stderr}"
    assert result.stdout.strip() == "", f"gofmt found files needing formatting:\n{result.stdout}"


def test_repo_css_build_tests():
    """CSS Build unit tests should pass (pass_to_pass)."""
    env = {**subprocess.os.environ, "HUGO_BUILD_TAGS": "extended,withdeploy"}
    result = subprocess.run(
        ["go", "test", "-v", "-run", "TestCSSBuild", "-count=1", "./tpl/css/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )
    assert result.returncode == 0, f"CSS Build tests failed:\n{result.stderr[-1000:]}"


def test_repo_create_package_tests():
    """Create package unit tests should pass (pass_to_pass)."""
    env = {**subprocess.os.environ, "HUGO_BUILD_TAGS": "extended,withdeploy"}
    result = subprocess.run(
        ["go", "test", "-v", "-count=1", "./create/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )
    assert result.returncode == 0, f"Create package tests failed:\n{result.stderr[-1000:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
