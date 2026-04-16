"""
Benchmark tests for TanStack/router#7030 - CSS asset deduplication in Start manifest

Tests verify that:
1. CSS assets are deduplicated within route entries (shared chunk imports)
2. CSS assets are deduplicated across parent-child route chains
"""

import subprocess
import os

REPO = "/workspace/router"


def test_repo_eslint():
    """Repo's eslint passes on start-plugin-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:eslint", "--skip-nx-cache"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_typecheck():
    """TypeScript type checking passes on start-plugin-core (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:test:types:ts60", "--skip-nx-cache"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"Type check failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_repo_manifestbuilder_unit():
    """Existing manifestBuilder unit tests pass (pass_to_pass)."""
    result = subprocess.run(
        ["pnpm", "vitest", "run", "tests/start-manifest-plugin/manifestBuilder.test.ts", "--reporter=dot"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=os.path.join(REPO, "packages/start-plugin-core"),
        env={**os.environ, "CI": "1"},
    )
    assert result.returncode == 0, f"Unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_typescript_compiles():
    """TypeScript code compiles without errors (pass_to_pass)."""
    # Build the start-plugin-core package
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/start-plugin-core:build"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"},
    )
    assert result.returncode == 0, f"Build failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"


def test_chunk_css_dedupes_shared_imports():
    """CSS from shared imported chunks is deduplicated (fail_to_pass).

    When chunk A imports B and C, and both B and C import shared chunk S,
    the CSS from S should only appear once in A's assets.
    """
    test_code = '''
    import { createChunkCssAssetCollector } from '../src/start-manifest-plugin/manifestBuilder';
    import { describe, test, expect } from 'vitest';

    function makeChunk(opts) {
      return {
        type: 'chunk',
        fileName: opts.fileName,
        imports: opts.imports || [],
        dynamicImports: opts.dynamicImports || [],
        isEntry: opts.isEntry || false,
        moduleIds: opts.moduleIds || [],
        viteMetadata: { importedCss: new Set(opts.importedCss || []) },
      };
    }

    describe('css dedupe f2p', () => {
      test('dedupes css from diamond imports', () => {
        const chunkA = makeChunk({
          fileName: 'a.js',
          imports: ['b.js', 'c.js'],
          importedCss: ['a.css'],
        });
        const chunkB = makeChunk({
          fileName: 'b.js',
          imports: ['shared.js'],
          importedCss: ['b.css'],
        });
        const chunkC = makeChunk({
          fileName: 'c.js',
          imports: ['shared.js'],
          importedCss: ['c.css'],
        });
        const sharedChunk = makeChunk({
          fileName: 'shared.js',
          importedCss: ['shared.css'],
        });
        const chunksByFileName = new Map([
          ['a.js', chunkA],
          ['b.js', chunkB],
          ['c.js', chunkC],
          ['shared.js', sharedChunk],
        ]);

        const { getChunkCssAssets } = createChunkCssAssetCollector({
          chunksByFileName,
          getStylesheetAsset: (cssFile) => ({
            tag: 'link',
            attrs: { rel: 'stylesheet', href: '/' + cssFile, type: 'text/css' },
          }),
        });

        const assets = getChunkCssAssets(chunkA);
        const hrefs = assets.map((a) => a.attrs.href);

        // shared.css should appear exactly once, not twice
        const sharedCount = hrefs.filter(h => h === '/shared.css').length;
        expect(sharedCount).toBe(1);

        // Total should be 4 unique CSS files
        expect(hrefs.length).toBe(4);
        expect(new Set(hrefs).size).toBe(4);
      });
    });
    '''

    test_file = os.path.join(REPO, "packages/start-plugin-core/tests/f2p_chunk_dedupe.test.ts")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["pnpm", "vitest", "run", "tests/f2p_chunk_dedupe.test.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.join(REPO, "packages/start-plugin-core"),
            env={**os.environ, "CI": "1"},
        )
        assert result.returncode == 0, f"Test failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_route_manifest_dedupes_ancestor_css():
    """CSS already in ancestor routes is not repeated in child routes (fail_to_pass).

    When parent route has CSS assets, child routes should not duplicate them.
    """
    test_code = '''
    import { buildStartManifest } from '../src/start-manifest-plugin/manifestBuilder';
    import { describe, test, expect } from 'vitest';

    function makeChunk(opts) {
      return {
        type: 'chunk',
        fileName: opts.fileName,
        imports: opts.imports || [],
        dynamicImports: opts.dynamicImports || [],
        isEntry: opts.isEntry || false,
        moduleIds: opts.moduleIds || [],
        viteMetadata: { importedCss: new Set(opts.importedCss || []) },
      };
    }

    describe('route dedupe f2p', () => {
      test('child route does not repeat parent css', () => {
        const entryChunk = makeChunk({
          fileName: 'entry.js',
          isEntry: true,
          imports: ['shared.js'],
          importedCss: ['entry.css'],
        });
        const sharedChunk = makeChunk({
          fileName: 'shared.js',
          importedCss: ['shared.css'],
        });
        const parentChunk = makeChunk({
          fileName: 'parent.js',
          imports: ['shared.js', 'parent-only.js'],
          moduleIds: ['/routes/parent.tsx?tsr-split=component'],
        });
        const parentOnlyChunk = makeChunk({
          fileName: 'parent-only.js',
          importedCss: ['parent.css'],
        });
        const childChunk = makeChunk({
          fileName: 'child.js',
          imports: ['shared.js', 'parent-only.js', 'child-only.js'],
          moduleIds: ['/routes/child.tsx?tsr-split=component'],
        });
        const childOnlyChunk = makeChunk({
          fileName: 'child-only.js',
          importedCss: ['child.css'],
        });

        const manifest = buildStartManifest({
          clientBundle: {
            'entry.js': entryChunk,
            'shared.js': sharedChunk,
            'parent.js': parentChunk,
            'parent-only.js': parentOnlyChunk,
            'child.js': childChunk,
            'child-only.js': childOnlyChunk,
          },
          routeTreeRoutes: {
            __root__: { children: ['/parent'] },
            '/parent': { filePath: '/routes/parent.tsx', children: ['/child'] },
            '/child': { filePath: '/routes/child.tsx' },
          },
          basePath: '/assets',
        });

        // Child route should only have child.css, not shared.css or parent.css
        const childAssets = manifest.routes['/child']?.assets || [];
        const childHrefs = childAssets.map((a) => a.attrs?.href);

        // shared.css is in root, parent.css is in parent - neither should be in child
        expect(childHrefs).not.toContain('/assets/shared.css');
        expect(childHrefs).not.toContain('/assets/parent.css');

        // child.css should be present
        expect(childHrefs).toContain('/assets/child.css');

        // Only one asset in child
        expect(childAssets.length).toBe(1);
      });
    });
    '''

    test_file = os.path.join(REPO, "packages/start-plugin-core/tests/f2p_route_dedupe.test.ts")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["pnpm", "vitest", "run", "tests/f2p_route_dedupe.test.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.join(REPO, "packages/start-plugin-core"),
            env={**os.environ, "CI": "1"},
        )
        assert result.returncode == 0, f"Test failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_sibling_routes_preserve_shared_css():
    """Sibling routes each get shared CSS that's not in their common ancestor (fail_to_pass).

    CSS assets in cousin routes should not be deduplicated against each other.
    """
    test_code = '''
    import { buildStartManifest } from '../src/start-manifest-plugin/manifestBuilder';
    import { describe, test, expect } from 'vitest';

    function makeChunk(opts) {
      return {
        type: 'chunk',
        fileName: opts.fileName,
        imports: opts.imports || [],
        dynamicImports: opts.dynamicImports || [],
        isEntry: opts.isEntry || false,
        moduleIds: opts.moduleIds || [],
        viteMetadata: { importedCss: new Set(opts.importedCss || []) },
      };
    }

    describe('sibling routes f2p', () => {
      test('cousin routes both get non-ancestor shared css', () => {
        const entryChunk = makeChunk({
          fileName: 'entry.js',
          isEntry: true,
        });
        const deepChunk = makeChunk({
          fileName: 'deep.js',
          importedCss: ['deep.css'],
        });
        const aChunk = makeChunk({
          fileName: 'a.js',
          moduleIds: ['/routes/a.tsx?tsr-split=component'],
        });
        const aChildChunk = makeChunk({
          fileName: 'a-child.js',
          imports: ['deep.js'],
          moduleIds: ['/routes/a-child.tsx?tsr-split=component'],
        });
        const bChunk = makeChunk({
          fileName: 'b.js',
          moduleIds: ['/routes/b.tsx?tsr-split=component'],
        });
        const bChildChunk = makeChunk({
          fileName: 'b-child.js',
          imports: ['deep.js'],
          moduleIds: ['/routes/b-child.tsx?tsr-split=component'],
        });

        const manifest = buildStartManifest({
          clientBundle: {
            'entry.js': entryChunk,
            'deep.js': deepChunk,
            'a.js': aChunk,
            'a-child.js': aChildChunk,
            'b.js': bChunk,
            'b-child.js': bChildChunk,
          },
          routeTreeRoutes: {
            __root__: { children: ['/a', '/b'] },
            '/a': { filePath: '/routes/a.tsx', children: ['/a-child'] },
            '/a-child': { filePath: '/routes/a-child.tsx' },
            '/b': { filePath: '/routes/b.tsx', children: ['/b-child'] },
            '/b-child': { filePath: '/routes/b-child.tsx' },
          },
          basePath: '/assets',
        });

        // Both cousin routes should have deep.css
        const aChildAssets = manifest.routes['/a-child']?.assets || [];
        const bChildAssets = manifest.routes['/b-child']?.assets || [];

        const aChildHrefs = aChildAssets.map((a) => a.attrs?.href);
        const bChildHrefs = bChildAssets.map((a) => a.attrs?.href);

        // deep.css should appear in BOTH cousin routes (not deduplicated against each other)
        expect(aChildHrefs).toContain('/assets/deep.css');
        expect(bChildHrefs).toContain('/assets/deep.css');
      });
    });
    '''

    test_file = os.path.join(REPO, "packages/start-plugin-core/tests/f2p_sibling_dedupe.test.ts")
    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["pnpm", "vitest", "run", "tests/f2p_sibling_dedupe.test.ts"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=os.path.join(REPO, "packages/start-plugin-core"),
            env={**os.environ, "CI": "1"},
        )
        assert result.returncode == 0, f"Test failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


if __name__ == "__main__":
    import sys

    tests = [
        ("test_repo_eslint", test_repo_eslint),
        ("test_repo_typecheck", test_repo_typecheck),
        ("test_repo_manifestbuilder_unit", test_repo_manifestbuilder_unit),
        ("test_typescript_compiles", test_typescript_compiles),
        ("test_chunk_css_dedupes_shared_imports", test_chunk_css_dedupes_shared_imports),
        ("test_route_manifest_dedupes_ancestor_css", test_route_manifest_dedupes_ancestor_css),
        ("test_sibling_routes_preserve_shared_css", test_sibling_routes_preserve_shared_css),
    ]

    failed = []
    for name, test_fn in tests:
        try:
            print(f"Running {name}...", end=" ")
            test_fn()
            print("PASSED")
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append(name)

    if failed:
        print(f"\n{len(failed)} test(s) failed: {failed}")
        sys.exit(1)
    print(f"\nAll {len(tests)} tests passed")
