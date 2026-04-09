"""Tests for Hugo PR #14631: Use css.Build in theme skeleton.

This verifies that the theme skeleton uses css.Build with proper options
and that CSS components are properly split into separate files.
"""

import os
import subprocess
import tempfile
import pytest

REPO = "/workspace/hugo"

REPO = "/workspace/hugo"
SKELETON_DIR = f"{REPO}/create/skeletons/theme"
CSS_DIR = f"{SKELETON_DIR}/assets/css"
LAYOUTS_DIR = f"{SKELETON_DIR}/layouts"


class TestCSSComponentFiles:
    """Verify CSS is split into component files."""

    def test_header_css_exists(self):
        """Header CSS should exist as a separate component file."""
        header_css = f"{CSS_DIR}/components/header.css"
        assert os.path.exists(header_css), f"Missing {header_css}"

    def test_footer_css_exists(self):
        """Footer CSS should exist as a separate component file."""
        footer_css = f"{CSS_DIR}/components/footer.css"
        assert os.path.exists(footer_css), f"Missing {footer_css}"

    def test_header_css_content(self):
        """Header CSS should contain border-bottom and margin-bottom rules."""
        with open(f"{CSS_DIR}/components/header.css") as f:
            content = f.read()
        assert "border-bottom" in content, "header.css missing border-bottom"
        assert "margin-bottom" in content, "header.css missing margin-bottom"
        assert "1rem" in content, "header.css should use 1rem margin"

    def test_footer_css_content(self):
        """Footer CSS should contain border-top and margin-top rules."""
        with open(f"{CSS_DIR}/components/footer.css") as f:
            content = f.read()
        assert "border-top" in content, "footer.css missing border-top"
        assert "margin-top" in content, "footer.css missing margin-top"
        assert "1rem" in content, "footer.css should use 1rem margin"


class TestMainCSS:
    """Verify main.css properly imports component CSS."""

    def test_main_css_imports_header(self):
        """main.css should @import header.css from components."""
        with open(f"{CSS_DIR}/main.css") as f:
            content = f.read()
        assert '@import "components/header.css"' in content, \
            "main.css should @import components/header.css"

    def test_main_css_imports_footer(self):
        """main.css should @import footer.css from components."""
        with open(f"{CSS_DIR}/main.css") as f:
            content = f.read()
        assert '@import "components/footer.css"' in content, \
            "main.css should @import components/footer.css"

    def test_main_css_no_inline_header_footer(self):
        """main.css should NOT have inline header/footer rules (they're imported)."""
        with open(f"{CSS_DIR}/main.css") as f:
            content = f.read()
        # After fix, these rules should be in component files, not inline
        assert "header {" not in content, \
            "main.css should not have inline header rule (use @import instead)"
        assert "footer {" not in content, \
            "main.css should not have inline footer rule (use @import instead)"

    def test_main_css_keeps_other_rules(self):
        """main.css should still have body and anchor styles."""
        with open(f"{CSS_DIR}/main.css") as f:
            content = f.read()
        assert "body {" in content, "main.css should keep body styles"
        assert "color: #222" in content, "main.css should keep body color"
        assert "a {" in content, "main.css should keep anchor styles"


class TestCSSTemplate:
    """Verify css.html template uses css.Build correctly."""

    def test_css_template_uses_css_build(self):
        """css.html should use css.Build instead of direct minify."""
        css_html = f"{LAYOUTS_DIR}/_partials/head/css.html"
        with open(css_html) as f:
            content = f.read()
        assert "css.Build" in content, "css.html should use css.Build function"

    def test_css_template_has_opts_dict(self):
        """css.html should define $opts dict with minify and sourceMap."""
        css_html = f"{LAYOUTS_DIR}/_partials/head/css.html"
        with open(css_html) as f:
            content = f.read()
        assert "$opts" in content, "css.html should define $opts variable"
        assert '"minify"' in content, "$opts should include minify option"
        assert '"sourceMap"' in content, "$opts should include sourceMap option"

    def test_css_template_conditional_options(self):
        """css.html should use cond for conditional options."""
        css_html = f"{LAYOUTS_DIR}/_partials/head/css.html"
        with open(css_html) as f:
            content = f.read()
        assert "cond hugo.IsDevelopment" in content, \
            "css.html should use cond hugo.IsDevelopment"

    def test_css_template_development_behavior(self):
        """css.html should link directly in development mode."""
        css_html = f"{LAYOUTS_DIR}/_partials/head/css.html"
        with open(css_html) as f:
            content = f.read()
        # Should check hugo.IsDevelopment and link without fingerprint
        assert 'if hugo.IsDevelopment' in content, \
            "Should check hugo.IsDevelopment"
        assert 'fingerprint' in content, \
            "Should fingerprint in production"


class TestJSTemplate:
    """Verify js.html template uses proper js.Build options."""

    def test_js_template_uses_cond_for_minify(self):
        """js.html should use cond for minify option."""
        js_html = f"{LAYOUTS_DIR}/_partials/head/js.html"
        with open(js_html) as f:
            content = f.read()
        assert '"minify" (cond hugo.IsDevelopment false true)' in content, \
            "js.html should use cond for minify (development=false, production=true)"

    def test_js_template_uses_cond_for_sourcemap(self):
        """js.html should use cond for sourceMap option."""
        js_html = f"{LAYOUTS_DIR}/_partials/head/js.html"
        with open(js_html) as f:
            content = f.read()
        assert '"sourceMap" (cond hugo.IsDevelopment "linked" "none")' in content, \
            "js.html should use cond for sourceMap (development=linked, production=none)"

    def test_js_template_no_targetpath(self):
        """js.html should not have targetPath in opts (it was removed)."""
        js_html = f"{LAYOUTS_DIR}/_partials/head/js.html"
        with open(js_html) as f:
            content = f.read()
        assert '"targetPath"' not in content, \
            "js.html should not have targetPath (was removed in PR)"


class TestHugoIntegration:
    """Verify Hugo can create and build theme with skeleton."""

    def test_hugo_new_theme_succeeds(self):
        """Hugo should be able to create a new theme using the skeleton."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize a Hugo site
            site_dir = os.path.join(tmpdir, "mysite")
            os.makedirs(site_dir)

            # Create minimal hugo.toml
            with open(os.path.join(site_dir, "hugo.toml"), "w") as f:
                f.write('title = "Test Site"\n')

            # Create a basic content file
            content_dir = os.path.join(site_dir, "content")
            os.makedirs(content_dir)
            with open(os.path.join(content_dir, "_index.md"), "w") as f:
                f.write("---\ntitle: Home\n---\n\nHello World\n")

            # Create new theme
            result = subprocess.run(
                ["hugo", "new", "theme", "mytheme"],
                cwd=site_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result.returncode == 0, f"hugo new theme failed: {result.stderr}"
            assert os.path.exists(os.path.join(site_dir, "themes", "mytheme")), \
                "Theme directory not created"

    def test_theme_files_copied_correctly(self):
        """Theme skeleton files should be copied to new theme."""
        with tempfile.TemporaryDirectory() as tmpdir:
            site_dir = os.path.join(tmpdir, "mysite")
            os.makedirs(site_dir)

            with open(os.path.join(site_dir, "hugo.toml"), "w") as f:
                f.write('title = "Test Site"\n')

            result = subprocess.run(
                ["hugo", "new", "theme", "mytheme"],
                cwd=site_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            assert result.returncode == 0

            theme_dir = os.path.join(site_dir, "themes", "mytheme")

            # Check CSS component files are copied
            assert os.path.exists(os.path.join(theme_dir, "assets", "css", "components", "header.css"))
            assert os.path.exists(os.path.join(theme_dir, "assets", "css", "components", "footer.css"))


# =============================================================================
# Pass-to-Pass Tests (Repo CI/CD checks)
# These verify the repo's existing CI checks pass on both base and fixed code.
# =============================================================================


class TestRepoCI:
    """Repo CI/CD checks that should pass on both base and fixed commits."""

    def test_repo_gofmt(self):
        """Repo's Go code passes gofmt check (pass_to_pass)."""
        r = subprocess.run(
            ["./check_gofmt.sh"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
        )
        assert r.returncode == 0, f"gofmt check failed:\n{r.stdout}\n{r.stderr}"

    def test_repo_go_vet(self):
        """Repo's Go code passes go vet (pass_to_pass)."""
        r = subprocess.run(
            ["go", "vet", "./create/..."],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
            env={**os.environ, "GOTOOLCHAIN": "auto"},
        )
        assert r.returncode == 0, f"go vet failed:\n{r.stderr[-500:]}"

    def test_repo_build(self):
        """Repo compiles successfully (pass_to_pass)."""
        r = subprocess.run(
            ["go", "build", "-o", "/tmp/hugo_test", "."],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=REPO,
            env={**os.environ, "GOTOOLCHAIN": "auto"},
        )
        assert r.returncode == 0, f"go build failed:\n{r.stderr[-500:]}"

    def test_repo_unit_tests_create(self):
        """Repo's create package tests pass (pass_to_pass)."""
        r = subprocess.run(
            ["go", "test", "-timeout=60s", "./create/..."],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=REPO,
            env={**os.environ, "GOTOOLCHAIN": "auto"},
        )
        assert r.returncode == 0, f"create package tests failed:\n{r.stderr[-500:]}"

    def test_repo_go_mod_verify(self):
        """Repo's go.mod and go.sum are valid (pass_to_pass)."""
        r = subprocess.run(
            ["go", "mod", "verify"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO,
            env={**os.environ, "GOTOOLCHAIN": "auto"},
        )
        assert r.returncode == 0, f"go mod verify failed:\n{r.stderr[-500:]}"


class TestThemeSkeletonIntegrity:
    """Verify theme skeleton files exist and are valid (pass_to_pass)."""

    def test_skeleton_css_template_exists(self):
        """Theme skeleton css.html template exists (pass_to_pass)."""
        css_html = f"{SKELETON_DIR}/layouts/_partials/head/css.html"
        assert os.path.exists(css_html), f"Missing {css_html}"

    def test_skeleton_js_template_exists(self):
        """Theme skeleton js.html template exists (pass_to_pass)."""
        js_html = f"{SKELETON_DIR}/layouts/_partials/head/js.html"
        assert os.path.exists(js_html), f"Missing {js_html}"

    def test_skeleton_main_css_exists(self):
        """Theme skeleton main.css exists (pass_to_pass)."""
        main_css = f"{SKELETON_DIR}/assets/css/main.css"
        assert os.path.exists(main_css), f"Missing {main_css}"

    def test_skeleton_main_js_exists(self):
        """Theme skeleton main.js exists (pass_to_pass)."""
        main_js = f"{SKELETON_DIR}/assets/js/main.js"
        assert os.path.exists(main_js), f"Missing {main_js}"

    def test_skeleton_layouts_exist(self):
        """Theme skeleton layout files exist (pass_to_pass)."""
        layouts = ["baseof.html", "home.html", "page.html"]
        for layout in layouts:
            path = f"{SKELETON_DIR}/layouts/{layout}"
            assert os.path.exists(path), f"Missing {path}"
