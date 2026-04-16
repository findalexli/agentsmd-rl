# Fix broken benchmark imports in napi/parser

The benchmark file `napi/parser/bench.bench.js` has broken import statements that prevent it from running correctly. The "Raw transfer benchmark" was reported as broken.

## Symptoms

When trying to run the benchmarks with `pnpm run bench` (which runs `vitest bench --run ./bench.bench.js`), the benchmark fails to execute due to import errors.

## Files to investigate

- `napi/parser/bench.bench.js` - The main benchmark file with broken imports
- `napi/parser/src-js/index.js` - Check what exports are available
- `napi/parser/src-js/generated/` - Directory with generated files that may need to be imported

## What to look for

1. **Import path issues**: Some imports may be pointing to paths that don't exist. Check if import paths for generated files are correct relative to the benchmark file location.

2. **Named export mismatches**: An import may be trying to import a named export that doesn't exist in the source module. Check what the actual export names are in `src-js/index.js`.

## Verification

After making changes, you can verify the benchmark file is syntactically correct by checking that:
- All import paths resolve to existing files
- All imported names match the actual exports from those modules

The benchmark tests parser performance using various fixtures and raw transfer modes. The imports at the top of the file need to correctly reference the internal modules for constants, deserialization functions, and the AST walker.
