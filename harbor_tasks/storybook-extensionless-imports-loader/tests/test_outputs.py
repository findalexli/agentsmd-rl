"""Behavioral tests for the storybook ts loader extension-resolution feature."""

import os
import subprocess
from pathlib import Path

REPO = Path("/workspace/repo")
LOADER_SRC = REPO / "code/core/src/bin/loader.ts"
LOADER_TEST_DEST = REPO / "code/core/src/bin/loader.test.ts"

# Vitest test file content (gold from PR #32641 — kept inline so /tests/ holds
# only test.sh + test_outputs.py per scaffold conventions).
_LOADER_TEST_TS = r"""import { existsSync } from 'node:fs';
import * as path from 'node:path';

import { beforeEach, describe, expect, it, vi } from 'vitest';

import { deprecate } from 'storybook/internal/node-logger';

import { addExtensionsToRelativeImports, resolveWithExtension } from './loader';

// Mock dependencies
vi.mock('node:fs');
vi.mock('storybook/internal/node-logger');

describe('loader', () => {
  describe('resolveWithExtension', () => {
    it('should return the path as-is if it already has an extension', () => {
      const result = resolveWithExtension('./test.js', '/project/src/file.ts');

      expect(result).toBe('./test.js');
      expect(deprecate).not.toHaveBeenCalled();
    });

    it('should resolve extensionless import to .ts extension when file exists', () => {
      const currentFile = '/project/src/file.ts';
      const expectedPath = path.resolve(path.dirname(currentFile), './utils.ts');

      vi.mocked(existsSync).mockImplementation((filePath) => {
        return filePath === expectedPath;
      });

      const result = resolveWithExtension('./utils', currentFile);

      expect(result).toBe('./utils.ts');
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('One or more extensionless imports detected: "./utils"')
      );
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining(
          'For maximum compatibility, you should add an explicit file extension'
        )
      );
    });

    it('should resolve extensionless import to .js extension when file exists', () => {
      const currentFile = '/project/src/file.ts';
      const expectedPath = path.resolve(path.dirname(currentFile), './utils.js');

      vi.mocked(existsSync).mockImplementation((filePath) => {
        return filePath === expectedPath;
      });

      const result = resolveWithExtension('./utils', currentFile);

      expect(result).toBe('./utils.js');
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('One or more extensionless imports detected: "./utils"')
      );
    });

    it('should show deprecation message when encountering an extensionless import', () => {
      vi.mocked(existsSync).mockReturnValue(true);

      resolveWithExtension('./utils', '/project/src/file.ts');

      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('One or more extensionless imports detected: "./utils"')
      );
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('in file "/project/src/file.ts"')
      );
    });

    it('should return original path when file cannot be resolved', () => {
      vi.mocked(existsSync).mockReturnValue(false);

      const result = resolveWithExtension('./missing', '/project/src/file.ts');

      expect(result).toBe('./missing');
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('One or more extensionless imports detected: "./missing"')
      );
    });

    it('should resolve relative to parent directory', () => {
      const currentFile = '/project/src/file.ts';
      const expectedPath = path.resolve(path.dirname(currentFile), '../utils.ts');

      vi.mocked(existsSync).mockImplementation((filePath) => {
        return filePath === expectedPath;
      });

      const result = resolveWithExtension('../utils', currentFile);

      expect(result).toBe('../utils.ts');
      expect(deprecate).toHaveBeenCalledWith(
        expect.stringContaining('One or more extensionless imports detected: "../utils"')
      );
    });
  });

  describe('addExtensionsToRelativeImports', () => {
    beforeEach(() => {
      // Default: all files exist with .ts extension
      vi.mocked(existsSync).mockImplementation((filePath) => {
        return (filePath as string).endsWith('.ts');
      });
    });

    it('should not modify imports that already have extensions', () => {
      const testCases = [
        { input: `import foo from './test.js';`, expected: `import foo from './test.js';` },
        { input: `import foo from './test.ts';`, expected: `import foo from './test.ts';` },
        { input: `import foo from '../utils.mjs';`, expected: `import foo from '../utils.mjs';` },
        {
          input: `export { bar } from './module.tsx';`,
          expected: `export { bar } from './module.tsx';`,
        },
      ];

      testCases.forEach(({ input, expected }) => {
        const result = addExtensionsToRelativeImports(input, '/project/src/file.ts');
        expect(result).toBe(expected);
        expect(deprecate).not.toHaveBeenCalled();
      });
    });

    it('should add extension to static import statements', () => {
      const source = `import { foo } from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import { foo } from './utils.ts';`);
    });

    it('should add extension to static export statements', () => {
      const source = `export { foo } from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`export { foo } from './utils.ts';`);
    });

    it('should add extension to dynamic import statements', () => {
      const source = `const module = await import('./utils');`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`const module = await import('./utils.ts');`);
    });

    it('should handle default imports', () => {
      const source = `import foo from './module';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import foo from './module.ts';`);
    });

    it('should handle named imports', () => {
      const source = `import { foo, bar } from './module';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import { foo, bar } from './module.ts';`);
    });

    it('should handle namespace imports', () => {
      const source = `import * as utils from './module';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import * as utils from './module.ts';`);
    });

    it('should handle side-effect imports', () => {
      const source = `import './styles';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import './styles.ts';`);
    });

    it('should handle export all statements', () => {
      const source = `export * from './module';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`export * from './module.ts';`);
    });

    it('should not modify absolute imports', () => {
      const testCases = [
        `import foo from 'react';`,
        `import bar from '@storybook/react';`,
        `import baz from 'node:fs';`,
      ];

      testCases.forEach((source) => {
        const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');
        expect(result).toBe(source);
      });
    });

    it('should not modify imports that match the pattern but are not relative paths', () => {
      // Edge case: a path that starts with a dot but not ./ or ../
      // This tests the condition that returns 'match' unchanged
      const source = `import foo from '.config';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      // Should not be modified since it doesn't start with ./ or ../
      expect(result).toBe(source);
      expect(deprecate).not.toHaveBeenCalled();
    });

    it('should handle single quotes', () => {
      const source = `import foo from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import foo from './utils.ts';`);
    });

    it('should handle double quotes', () => {
      const source = `import foo from "./utils";`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import foo from "./utils.ts";`);
    });

    it('should handle paths starting with ./', () => {
      const source = `import foo from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import foo from './utils.ts';`);
    });

    it('should handle paths starting with ../', () => {
      const source = `import foo from '../utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import foo from '../utils.ts';`);
    });

    it('should handle multiple imports in the same file', () => {
      const source = `import foo from './foo';\nimport bar from './bar';\nexport { baz } from '../baz';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(
        `import foo from './foo.ts';\nimport bar from './bar.ts';\nexport { baz } from '../baz.ts';`
      );
    });

    it('should preserve the import structure after adding extensions', () => {
      const source = `import { foo, bar } from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toContain('{ foo, bar }');
      expect(result).toBe(`import { foo, bar } from './utils.ts';`);
    });

    it('should handle imports with comments', () => {
      const source = `// This is a comment\nimport foo from './utils'; // inline comment`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`// This is a comment\nimport foo from './utils.ts'; // inline comment`);
    });

    it('should handle multi-line imports with named exports on separate lines', () => {
      const source = `import {
  foo,
  bar,
  baz
} from './utils';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`import {
  foo,
  bar,
  baz
} from './utils.ts';`);
    });

    it('should handle multi-line exports with named exports on separate lines', () => {
      const source = `export {
  foo,
  bar
} from '../module';`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`export {
  foo,
  bar
} from '../module.ts';`);
    });

    it('should handle multi-line dynamic imports', () => {
      const source = `const module = await import(
  './utils'
);`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`const module = await import(
  './utils.ts'
);`);
    });

    it('should handle dynamic imports with backticks', () => {
      const source = 'import(`./foo`);';
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe('import(`./foo.ts`);');
    });

    it('should not modify dynamic imports with template literal interpolation', () => {
      const source = 'import(`${foo}/bar`);';
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      // Cannot be supported: template interpolation ${foo} is a runtime value
      // The regex stops at $ to avoid matching interpolated expressions
      expect(result).toBe('import(`${foo}/bar`);');
    });

    it('should not modify dynamic imports with template literal interpolation and relative path', () => {
      const source = 'import(`./${foo}/bar`);';
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      // Cannot be supported: template interpolation ${foo} is a runtime value
      // The regex stops at $ to avoid matching interpolated expressions
      expect(result).toBe('import(`./${foo}/bar`);');
    });

    it('should handle array of dynamic imports', () => {
      const source = `const [] = [
  import('./foo'),
  import('./bar'),
];`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(`const [] = [
  import('./foo.ts'),
  import('./bar.ts'),
];`);
    });

    it('should handle multi-line backtick dynamic imports', () => {
      const source = 'const module = await import(\n  `./utils`\n);';
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe('const module = await import(\n  `./utils.ts`\n);');
    });

    it('should handle mixed quote types in same file', () => {
      const source = `import foo from './foo';\nimport bar from "./bar";\nimport(\`./baz\`);`;
      const result = addExtensionsToRelativeImports(source, '/project/src/file.ts');

      expect(result).toBe(
        `import foo from './foo.ts';\nimport bar from "./bar.ts";\nimport(\`./baz.ts\`);`
      );
    });
  });
});
"""


def _ensure_test_file_in_place():
    """Materialize the gold loader.test.ts alongside loader.ts so vitest can
    import it via `./loader`."""
    LOADER_TEST_DEST.parent.mkdir(parents=True, exist_ok=True)
    LOADER_TEST_DEST.write_text(_LOADER_TEST_TS)


def _run_vitest(name_pattern: str | None = None, timeout: int = 180) -> subprocess.CompletedProcess:
    _ensure_test_file_in_place()
    cmd = ["npx", "--no-install", "vitest", "run", "--reporter=default"]
    if name_pattern is not None:
        cmd.extend(["-t", name_pattern])
    return subprocess.run(
        cmd,
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true", "FORCE_COLOR": "0"},
    )


def _diagnostic(r: subprocess.CompletedProcess) -> str:
    return (
        f"\n--- exit={r.returncode} ---\n"
        f"--- stdout (last 4000) ---\n{r.stdout[-4000:]}\n"
        f"--- stderr (last 2000) ---\n{r.stderr[-2000:]}\n"
    )


def _build_real_module(tag: str) -> Path:
    """Bundle loader.ts via esbuild (inlining relative imports like the
    constants module) and write a self-contained .mjs alongside loader.ts
    so its bare specifiers (`esbuild`, `ts-dedent`, `storybook/internal/...`)
    resolve via the repo's node_modules. Returns the path of the .mjs."""
    out = REPO / "code/core/src/bin" / f"_real_loader_{tag}.mjs"
    helper = REPO / "scripts_build_real.mjs"
    helper.write_text(
        f"""
import {{build}} from 'esbuild';
await build({{
  entryPoints: ['./code/core/src/bin/loader.ts'],
  outfile: {str(out)!r},
  bundle: true,
  format: 'esm',
  platform: 'node',
  target: 'node20.19',
  external: ['storybook/*', 'esbuild', 'ts-dedent', 'node:*'],
}});
console.log('OK');
"""
    )
    try:
        r = subprocess.run(
            ["node", str(helper)],
            cwd=str(REPO), capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"esbuild prep failed: {r.stderr}"
    finally:
        try:
            helper.unlink()
        except FileNotFoundError:
            pass
    return out


# ---------------------------------------------------------------------------
# Fail-to-pass (f2p): require the implementation to exist and behave correctly
# ---------------------------------------------------------------------------

def test_resolve_with_extension_suite():
    """The 'resolveWithExtension' describe block in loader.test.ts must pass."""
    r = _run_vitest("resolveWithExtension")
    assert r.returncode == 0, "resolveWithExtension tests failed:" + _diagnostic(r)


def test_add_extensions_to_relative_imports_suite():
    """The 'addExtensionsToRelativeImports' describe block must pass."""
    r = _run_vitest("addExtensionsToRelativeImports")
    assert r.returncode == 0, "addExtensionsToRelativeImports tests failed:" + _diagnostic(r)


def test_full_loader_vitest_suite():
    """All tests in loader.test.ts must pass under vitest."""
    r = _run_vitest()
    assert r.returncode == 0, "Full vitest suite failed:" + _diagnostic(r)


def test_resolve_with_extension_real_module():
    """End-to-end behavior on the real (unmocked) implementation:
    paths that already have an extension are returned unchanged."""
    out = _build_real_module("unchanged")
    driver = REPO / "code/core/src/bin/_run_unchanged.mjs"
    driver.write_text(
        f"""
const mod = await import({str(out)!r});
const r1 = mod.resolveWithExtension('./test.js', '/p/src/file.ts');
const r2 = mod.resolveWithExtension('../utils.tsx', '/p/src/file.ts');
if (r1 !== './test.js') {{ console.error('FAIL r1', r1); process.exit(2); }}
if (r2 !== '../utils.tsx') {{ console.error('FAIL r2', r2); process.exit(3); }}
console.log('OK');
"""
    )
    try:
        r = subprocess.run(
            ["node", str(driver)],
            cwd=str(REPO), capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"driver failed: {_diagnostic(r)}"
        assert "OK" in r.stdout
    finally:
        for p in (driver, out):
            try:
                p.unlink()
            except FileNotFoundError:
                pass


def test_add_extensions_real_module():
    """End-to-end on the real implementation: a sibling .ts file is found and
    appended; bare specifiers and template-interpolated paths are untouched."""
    out = _build_real_module("addext")
    helper = REPO / "code/core/src/bin/__sibling_helper.ts"
    helper.write_text("export const x = 1;\n")
    driver = REPO / "code/core/src/bin/_run_addext.mjs"
    driver.write_text(
        f"""
import {{resolve}} from 'node:path';
const mod = await import({str(out)!r});
const filePath = resolve(process.cwd(), 'code/core/src/bin/loader.ts');

const rewritten = mod.addExtensionsToRelativeImports(
  `import {{ x }} from './__sibling_helper';\\nconst dyn = await import('./__sibling_helper');`,
  filePath
);
if (!rewritten.includes(`'./__sibling_helper.ts'`)) {{
  console.error('Static import NOT rewritten. Got:', rewritten);
  process.exit(2);
}}
const dynRewrites = (rewritten.match(/\\.\\/__sibling_helper\\.ts/g) || []).length;
if (dynRewrites < 2) {{
  console.error('Dynamic import NOT rewritten. Got:', rewritten);
  process.exit(3);
}}
const passthrough = mod.addExtensionsToRelativeImports(
  `import x from 'react';`,
  filePath
);
if (passthrough !== `import x from 'react';`) {{
  console.error('Bare specifier was modified:', passthrough);
  process.exit(4);
}}
const tplGuard = mod.addExtensionsToRelativeImports(
  'import(`./${{foo}}/bar`);',
  filePath
);
if (tplGuard !== 'import(`./${{foo}}/bar`);') {{
  console.error('Template-interpolated path was rewritten:', tplGuard);
  process.exit(5);
}}
console.log('OK');
"""
    )
    try:
        r = subprocess.run(
            ["node", str(driver)],
            cwd=str(REPO), capture_output=True, text=True, timeout=60,
        )
        assert r.returncode == 0, f"driver failed: {_diagnostic(r)}"
        assert "OK" in r.stdout
    finally:
        for p in (driver, out, helper):
            try:
                p.unlink()
            except FileNotFoundError:
                pass


# ---------------------------------------------------------------------------
# Pass-to-pass (p2p): repository-level checks that pass at base AND at gold
# ---------------------------------------------------------------------------

def test_loader_typescript_compiles():
    """loader.ts must remain syntactically valid under `tsc --strict`.

    Pass-to-pass: the base file already type-checks; a correct fix must not
    break it. Reflects `.github/copilot-instructions.md` "TypeScript strict
    mode is enabled".
    """
    r = subprocess.run(
        ["npx", "--no-install", "tsc", "--noEmit"],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"tsc failed:\nstdout={r.stdout[-2000:]}\nstderr={r.stderr[-1000:]}"
    )


def test_loader_esbuild_parses():
    """loader.ts must be parseable by esbuild's TS loader (pass-to-pass).

    Mirrors the runtime transformation the loader performs.
    """
    r = subprocess.run(
        [
            "node", "-e",
            "import('esbuild').then(({transform}) => transform("
            "require('node:fs').readFileSync('code/core/src/bin/loader.ts','utf-8'),"
            "{loader:'ts',format:'esm',platform:'neutral'})"
            ".then(()=>console.log('OK')).catch(e=>{console.error(e);process.exit(2)}));",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, (
        f"esbuild parse failed:\nstdout={r.stdout!r}\nstderr={r.stderr!r}"
    )
    assert "OK" in r.stdout

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_core_unit_tests__windows_lates_compile():
    """pass_to_pass | CI job 'Core Unit Tests, windows-latest' → step 'compile'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn task --task compile --start-from=compile'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'compile' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_core_unit_tests__windows_lates_test():
    """pass_to_pass | CI job 'Core Unit Tests, windows-latest' → step 'test'"""
    r = subprocess.run(
        ["bash", "-lc", 'yarn test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")