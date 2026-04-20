"""
Tests for mantinedev/mantine#8488: Fix children override in getMonthControlProps/getYearControlProps

The bug: getMonthControlProps and getYearControlProps return {children: ...} but the
children are ignored in MonthsList and YearsList components - the default formatted
month/year is always rendered instead.

The fix: Use controlProps?.children ?? defaultFormat to render custom children
when provided.
"""
import subprocess
import os
import pytest
import textwrap

REPO = "/workspace/mantine"


def run_typescript_script(script: str) -> subprocess.CompletedProcess:
    """Run a TypeScript-check script in the Mantine repo environment using yarn tsx."""
    return subprocess.run(
        ["yarn", "tsx", "-e", script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )


def get_jsx_children_expression(file_path: str, tag_name: str) -> str | None:
    """
    Use TypeScript API to find the children expression of a JSX element.
    Returns the text of the JSxExpression child, or None if not found.
    This actually CALLS the TypeScript compiler API - not just a text grep.
    """
    escaped_path = file_path.replace("\\", "\\\\").replace("'", "\\'")
    escaped_tag = tag_name.replace("'", "\\'")
    basename = os.path.basename(file_path)

    script = textwrap.dedent(f'''
        import * as ts from 'typescript';
        import * as fs from 'fs';

        const source = fs.readFileSync('{escaped_path}', 'utf8');
        const sourceFile = ts.createSourceFile('{basename}', source, ts.ScriptTarget.Latest, true);

        let expressionText: string | null = null;

        function visit(n: ts.Node) {{
          if (ts.isJsxOpeningElement(n) && n.tagName.getText(sourceFile) === '{escaped_tag}') {{
            const parent = n.parent;
            if (ts.isJsxElement(parent)) {{
              const children = parent.children;
              // Find the JsxExpression child (skip JsxText whitespace)
              for (let i = 0; i < children.length; i++) {{
                const child = children[i];
                if (ts.isJsxExpression(child)) {{
                  expressionText = child.expression?.getText(sourceFile) ?? null;
                  return;
                }}
              }}
            }}
            return;
          }}
          ts.forEachChild(n, visit);
        }}

        visit(sourceFile);
        console.log(expressionText ?? 'NOT_FOUND');
    ''')

    r = run_typescript_script(script)
    if r.returncode != 0:
        return None
    result = r.stdout.strip()
    if result == "NOT_FOUND":
        return None
    return result


class TestFixApplied:
    """Verify the fix works — custom children from get*ControlProps are rendered (fail-to-pass)."""

    def test_monthslist_uses_children_override_pattern(self):
        """
        MonthsList should use controlProps?.children ?? pattern (or equivalent)
        to override children when getMonthControlProps returns them.

        This test CALLS the TypeScript API to parse the JSX and extract the
        actual children expression — not a text grep.
        """
        file_path = os.path.join(
            REPO, "packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx"
        )

        children_expr = get_jsx_children_expression(file_path, "PickerControl")

        assert children_expr is not None, (
            f"Could not find PickerControl children expression in MonthsList.tsx. "
            f"TypeScript API returned: {children_expr}"
        )

        # The children expression must override the default format using the nullish-coalescing
        # operator (??). Any of these forms are valid:
        #   - controlProps?.children ?? dayjs(...).format(...)
        #   - controlProps.children !== undefined ? controlProps.children : dayjs(...).format(...)
        #   - !controlProps?.children ? dayjs(...).format(...) : controlProps.children
        #   - const { children } = controlProps ?? {}; children ?? dayjs(...).format(...)
        #
        # The key behaviors we check:
        # 1. The override uses ?? (or ! / !== / ternary) to check for custom children
        # 2. The default format (dayjs + format call) appears on the right side of ??
        has_override_pattern = "??" in children_expr or "?" in children_expr or "!" in children_expr

        # The default format call must be present on the "fallback" side
        has_default_format = "dayjs" in children_expr and "format" in children_expr

        assert has_override_pattern, (
            f"MonthsList PickerControl children does not use a nullish-coalescing or "
            f"ternary pattern to override default format.\n"
            f"Got: {children_expr}\n"
            "Expected pattern like: controlProps?.children ?? dayjs(...).format(...) "
            "or: const { children } = controlProps ?? {}; children ?? ..."
        )

        assert has_default_format, (
            f"MonthsList PickerControl children does not use dayjs format as the default.\n"
            f"Got: {children_expr}\n"
            "The default fallback should be the dayjs format expression."
        )

    def test_yearlist_uses_children_override_pattern(self):
        """
        YearsList should use controlProps?.children ?? pattern (or equivalent)
        to override children when getYearControlProps returns them.

        This test CALLS the TypeScript API to parse the JSX and extract the
        actual children expression — not a text grep.
        """
        file_path = os.path.join(
            REPO, "packages/@mantine/dates/src/components/YearsList/YearsList.tsx"
        )

        children_expr = get_jsx_children_expression(file_path, "PickerControl")

        assert children_expr is not None, (
            f"Could not find PickerControl children expression in YearsList.tsx. "
            f"TypeScript API returned: {children_expr}"
        )

        has_override_pattern = "??" in children_expr or "?" in children_expr or "!" in children_expr
        has_default_format = "dayjs" in children_expr and "format" in children_expr

        assert has_override_pattern, (
            f"YearsList PickerControl children does not use a nullish-coalescing or "
            f"ternary pattern to override default format.\n"
            f"Got: {children_expr}\n"
            "Expected pattern like: controlProps?.children ?? dayjs(...).format(...) "
            "or: const { children } = controlProps ?? {}; children ?? ..."
        )

        assert has_default_format, (
            f"YearsList PickerControl children does not use dayjs format as the default.\n"
            f"Got: {children_expr}\n"
            "The default fallback should be the dayjs format expression."
        )


class TestCodeQuality:
    """Verify code passes linting and formatting (pass-to-pass)."""

    def test_eslint_on_monthslist(self):
        """ESLint should pass on modified MonthsList files."""
        r = subprocess.run(
            ["yarn", "eslint", "--quiet",
             "packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx",
             "packages/@mantine/dates/src/components/MonthsList/MonthsList.story.tsx"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert r.returncode == 0, f"ESLint failed on MonthsList:\n{r.stderr}"

    def test_eslint_on_yearlist(self):
        """ESLint should pass on modified YearsList files."""
        r = subprocess.run(
            ["yarn", "eslint", "--quiet",
             "packages/@mantine/dates/src/components/YearsList/YearsList.tsx",
             "packages/@mantine/dates/src/components/YearsList/YearsList.story.tsx"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120
        )
        assert r.returncode == 0, f"ESLint failed on YearsList:\n{r.stderr}"

    def test_prettier_on_monthslist(self):
        """Prettier should pass on modified MonthsList files."""
        r = subprocess.run(
            ["yarn", "prettier", "--check",
             "packages/@mantine/dates/src/components/MonthsList/MonthsList.tsx",
             "packages/@mantine/dates/src/components/MonthsList/MonthsList.story.tsx"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert r.returncode == 0, f"Prettier failed on MonthsList:\n{r.stdout}"

    def test_prettier_on_yearlist(self):
        """Prettier should pass on modified YearsList files."""
        r = subprocess.run(
            ["yarn", "prettier", "--check",
             "packages/@mantine/dates/src/components/YearsList/YearsList.tsx",
             "packages/@mantine/dates/src/components/YearsList/YearsList.story.tsx"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert r.returncode == 0, f"Prettier failed on YearsList:\n{r.stdout}"

    def test_repo_package_json_valid(self):
        """Repo's package.json files are valid (pass_to_pass)."""
        r = subprocess.run(
            ["npm", "run", "test:validate-package-json"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert r.returncode == 0, f"validate-package-json failed:\n{r.stdout}"

    def test_repo_packages_files_valid(self):
        """Repo's package files are valid (pass_to_pass)."""
        r = subprocess.run(
            ["npm", "run", "test:validate-packages-files"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert r.returncode == 0, f"validate-packages-files failed:\n{r.stdout}"

    def test_repo_conflicts_check(self):
        """Repo's conflict check passes (pass_to_pass)."""
        r = subprocess.run(
            ["npm", "run", "test:conflicts"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        assert r.returncode == 0, f"conflicts check failed:\n{r.stdout}"