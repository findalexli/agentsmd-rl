"""
Tests for ant-design Image accessibility enhancement.

This validates that:
1. focus-visible styles are added to the Image component (behavioral)
2. The @rc-component/image dependency is upgraded to support focusTrap
3. TypeScript compiles without errors
"""

import json
import os
import re
import subprocess
import sys
import tempfile

REPO = "/workspace/antd"


class TestFocusVisibleStyles:
    """Tests for focus-visible CSS styles in Image component.

    These tests verify BEHAVIOR by compiling the style file and checking
    that the output contains focus-visible related code, rather than
    just grepping source strings.
    """

    def _get_compiled_style_output(self):
        """Compile the image style file and return compiled content."""
        compile_script = f"""
        const ts = require('typescript');
        const fs = require('fs');
        const path = require('path');

        const filePath = '{REPO}/components/image/style/index.ts';
        const content = fs.readFileSync(filePath, 'utf8');

        const result = ts.transpileModule(content, {{
            compilerOptions: {{
                module: ts.ModuleKind.CommonJS,
                target: ts.ScriptTarget.ES2020,
                esModuleInterop: true,
            }},
            fileName: 'index.ts',
        }});

        console.log(result.outputText);
        """

        result = subprocess.run(
            [sys.executable, "-c", f"""
import subprocess
import sys

script = {repr(compile_script)}
result = subprocess.run(
    ["node", "-e", script],
    cwd="{REPO}",
    capture_output=True,
    text=True,
    timeout=60
)
print(result.stdout, file=sys.stdout)
print(result.stderr, file=sys.stderr)
sys.exit(result.returncode)
"""],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to compile style file: {{result.stderr}}")

        return result.stdout

    def test_style_imports_focus_utilities(self):
        """Style file compiles and uses genFocusOutline and genFocusStyle (fail_to_pass)."""
        output = self._get_compiled_style_output()

        assert "genFocusOutline" in output, \
            "Compiled style file should contain genFocusOutline"
        assert "genFocusStyle" in output, \
            "Compiled style file should contain genFocusStyle"

    def test_image_cover_has_focus_visible_selector(self):
        """Image cover shows on focus-visible, not just hover (fail_to_pass)."""
        output = self._get_compiled_style_output()

        assert "focus-visible" in output.lower(), \
            "Image cover should include focus-visible pseudo-class in compiled styles"

    def test_preview_operation_has_focus_visible_outline(self):
        """Preview operation buttons have focus-visible outline (fail_to_pass)."""
        output = self._get_compiled_style_output()

        assert "genFocusOutline" in output, \
            "Preview operations should use genFocusOutline for focus-visible outline"

    def test_image_component_uses_focus_style(self):
        """Image component spreads genFocusStyle for focus styling (fail_to_pass)."""
        output = self._get_compiled_style_output()

        assert "genFocusStyle" in output, \
            "Image component should use genFocusStyle for focus styling"


class TestDependencyUpgrade:
    """Tests for @rc-component/image dependency upgrade."""

    def test_rc_component_image_version_upgraded(self):
        """@rc-component/image is upgraded to ~1.9.0 for focusTrap support (fail_to_pass)."""
        package_json = os.path.join(REPO, "package.json")
        with open(package_json, "r") as f:
            pkg = json.load(f)

        dependencies = pkg.get("dependencies", {})
        image_version = dependencies.get("@rc-component/image", "")

        assert image_version.startswith("~1.9") or image_version.startswith("^1.9") or \
               image_version.startswith("~2.") or image_version.startswith("^2."), \
            f"@rc-component/image should be ~1.9.0 or higher, got {image_version}"


class TestDocumentation:
    """Tests for API documentation updates."""

    def test_english_docs_have_focustrap_prop(self):
        """English documentation includes focusTrap prop in PreviewType (fail_to_pass)."""
        doc_file = os.path.join(REPO, "components/image/index.en-US.md")
        with open(doc_file, "r") as f:
            content = f.read()

        assert "focusTrap" in content, "English docs should document the focusTrap prop"
        assert "Whether to trap focus within the preview" in content or \
               "trap focus" in content.lower(), \
            "English docs should explain what focusTrap does"

    def test_chinese_docs_have_focustrap_prop(self):
        """Chinese documentation includes focusTrap prop in PreviewType (fail_to_pass)."""
        doc_file = os.path.join(REPO, "components/image/index.zh-CN.md")
        with open(doc_file, "r") as f:
            content = f.read()

        assert "focusTrap" in content, "Chinese docs should document the focusTrap prop"
        assert "捕获焦点" in content or "focus" in content.lower(), \
            "Chinese docs should explain what focusTrap does"


class TestSemanticDemo:
    """Tests for semantic demo update."""

    def test_semantic_demo_disables_focus_trap(self):
        """Semantic demo sets focusTrap: false for inline preview (fail_to_pass)."""
        demo_file = os.path.join(REPO, "components/image/demo/_semantic.tsx")
        with open(demo_file, "r") as f:
            content = f.read()

        assert "focusTrap: false" in content or "focusTrap:false" in content, \
            "Semantic demo should disable focusTrap for inline preview"


class TestTypeScriptCompilation:
    """Tests for TypeScript compilation (pass_to_pass)."""

    def test_typescript_compiles_without_errors(self):
        """TypeScript compilation passes without errors (pass_to_pass)."""
        env = os.environ.copy()
        env["NODE_OPTIONS"] = "--max-old-space-size=4096"
        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=600,
            env=env
        )

        if result.returncode != 0:
            stderr = result.stderr or result.stdout
            image_errors = [line for line in stderr.split("\n")
                          if "components/image" in line.lower()]
            if image_errors:
                assert False, f"TypeScript errors in image component:\n" + "\n".join(image_errors[:10])


class TestCodeQuality:
    """Tests for code quality and linting (pass_to_pass)."""

    def test_eslint_passes_on_image_styles(self):
        """ESLint passes on the image style file (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "eslint", "components/image/style/index.ts", "--max-warnings=0"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode != 0:
            stderr = result.stderr or result.stdout
            if "error" in stderr.lower():
                assert False, f"ESLint errors in image style:\n{stderr[-500:]}"

    def test_eslint_passes_on_image_dir(self):
        """ESLint passes on the entire image component directory (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "eslint", "components/image/", "--max-warnings=0"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180
        )

        assert result.returncode == 0, f"ESLint errors in image component:\n{(result.stderr or result.stdout)[-500:]}"

    def test_biome_lint_on_image(self):
        """Biome lint passes on image component (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "biome", "lint", "components/image/"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"Biome lint errors:\n{(result.stderr or result.stdout)[-500:]}"

    def test_remark_lint_on_image_docs(self):
        """Markdown lint passes on image documentation (pass_to_pass)."""
        result = subprocess.run(
            ["npx", "remark", "components/image/index.en-US.md", "components/image/index.zh-CN.md", "-f", "-q"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )

        assert result.returncode == 0, f"Remark lint errors:\n{(result.stderr or result.stdout)[-500:]}"


class TestRepoTests:
    """Tests that run the repo's actual test suite (pass_to_pass)."""

    def test_image_a11y_tests(self):
        """Image accessibility tests pass (pass_to_pass)."""
        result = subprocess.run(
            ["npm", "run", "test", "--", "--testPathPatterns=components/image/__tests__/a11y", "--no-cache"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, f"Image a11y tests failed:\n{(result.stderr or result.stdout)[-1000:]}"

    def test_image_unit_tests(self):
        """Image unit tests pass (pass_to_pass)."""
        result = subprocess.run(
            ["npm", "run", "test", "--", "--testPathPatterns=components/image/__tests__/index", "--no-cache"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, f"Image unit tests failed:\n{(result.stderr or result.stdout)[-1000:]}"

    def test_image_demo_tests(self):
        """Image demo snapshot tests pass (pass_to_pass)."""
        result = subprocess.run(
            ["npm", "run", "test", "--", "--testPathPatterns=components/image/__tests__/demo.test.ts", "--no-cache"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300
        )

        assert result.returncode == 0, f"Image demo tests failed:\n{(result.stderr or result.stdout)[-1000:]}"
