// Helper used by test_outputs.py to inspect the registry-router worker.
//
// Strategy: read src/index.ts as text, append `export { ORIGINS, sortedByDistance };`
// so the symbols become module exports, transpile to ESM JS with the bundled
// TypeScript compiler, then dynamic-import and dump the data we need as JSON
// on stdout.
//
// Usage: node extract_origins.cjs <path-to-index.ts>

"use strict";

const fs = require("fs");
const path = require("path");
const os = require("os");

const indexPath = path.resolve(process.argv[2]);
const repoRoot = path.resolve(indexPath, "..", "..", "..", "..");
const ts = require(path.join(repoRoot, "infra", "registry-router", "node_modules", "typescript"));

let source = fs.readFileSync(indexPath, "utf8");

// The worker file declares ORIGINS and sortedByDistance as module-private
// const/function. Append explicit named exports so the transpiled JS lets us
// inspect them.
source += "\nexport { ORIGINS, sortedByDistance };\n";

const out = ts.transpileModule(source, {
  compilerOptions: {
    module: ts.ModuleKind.ESNext,
    target: ts.ScriptTarget.ES2022,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
  },
});

const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "rr-extract-"));
const outFile = path.join(tmpDir, "index.mjs");
fs.writeFileSync(outFile, out.outputText);

(async () => {
  const mod = await import(outFile);
  const origins = mod.ORIGINS;

  const probes = [
    { label: "sydney",     lat: -33.87, lon:  151.21 },
    { label: "melbourne",  lat: -37.81, lon:  144.96 },
    { label: "brisbane",   lat: -27.47, lon:  153.03 },
    { label: "frankfurt",  lat:  50.11, lon:    8.68 },
    { label: "ashburn",    lat:  39.04, lon:  -77.49 },
    { label: "portland",   lat:  45.59, lon: -122.60 },
    { label: "santiago",   lat: -33.45, lon:  -70.67 },
    { label: "singapore",  lat:   1.35, lon:  103.82 },
  ];

  const sortedProbes = {};
  for (const p of probes) {
    const sorted = mod.sortedByDistance(p.lat, p.lon);
    sortedProbes[p.label] = sorted.map((o) => o.host);
  }

  console.log(JSON.stringify({ origins, sortedProbes }));
})().catch((err) => {
  console.error(err && err.stack ? err.stack : String(err));
  process.exit(1);
});
