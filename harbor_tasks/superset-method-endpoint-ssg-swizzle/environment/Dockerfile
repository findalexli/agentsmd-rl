# syntax=docker/dockerfile:1.4
FROM node:22.11.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --break-system-packages --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-ctrf==0.3.5

WORKDIR /workspace

ARG REPO_URL=https://github.com/apache/superset.git
ARG BASE_COMMIT=61fbfda501ef00d24e5dfeeabaf6b8220b73c4c7

RUN git clone --filter=blob:none --no-checkout "$REPO_URL" superset \
 && cd superset \
 && git sparse-checkout init --cone \
 && git sparse-checkout set docs .github .cursor \
 && git checkout "$BASE_COMMIT"

WORKDIR /workspace/test_harness

RUN npm init -y \
 && npm install --no-audit --no-fund --save-exact \
    react@18.3.1 \
    react-dom@18.3.1 \
    react-redux@9.2.0 \
    esbuild@0.24.2 \
 && npm cache clean --force

# bundle.js: compile a TSX entry to a CJS bundle, mocking @docusaurus/* imports.
RUN cat > /workspace/test_harness/bundle.js <<'JS'
const esbuild = require('esbuild');

const [, , entry, outfile] = process.argv;
if (!entry || !outfile) {
  console.error('usage: node bundle.js <entry.tsx> <outfile.js>');
  process.exit(2);
}

(async () => {
  try {
    await esbuild.build({
      entryPoints: [entry],
      bundle: true,
      platform: 'node',
      format: 'cjs',
      outfile,
      external: ['react', 'react-dom', 'react-redux'],
      jsx: 'automatic',
      loader: { '.tsx': 'tsx', '.ts': 'ts', '.js': 'jsx' },
      logLevel: 'silent',
      plugins: [
        {
          name: 'mock-docusaurus',
          setup(build) {
            build.onResolve({ filter: /^@docusaurus\// }, (args) => ({
              path: args.path,
              namespace: 'doc-mock',
            }));
            build.onLoad({ filter: /.*/, namespace: 'doc-mock' }, () => ({
              contents:
                "const fn = function BrowserOnly(){ return '__BROWSER_ONLY_MARKER__'; };\n" +
                "module.exports = fn;\n" +
                "module.exports.default = fn;\n",
              loader: 'js',
            }));
          },
        },
      ],
    });
  } catch (err) {
    console.error(err && err.message ? err.message : String(err));
    if (err && err.errors) {
      for (const e of err.errors) console.error(JSON.stringify(e));
    }
    process.exit(1);
  }
})();
JS

# render.js: SSR-render a default export from a compiled bundle.
RUN cat > /workspace/test_harness/render.js <<'JS'
const React = require('react');
const { renderToString } = require('react-dom/server');
const modPath = process.argv[2];
const propsArg = process.argv[3] || '{}';
const Mod = require(modPath);
const Comp = (Mod && Mod.default) ? Mod.default : Mod;
const props = JSON.parse(propsArg);
process.stdout.write(renderToString(React.createElement(Comp, props)));
JS

RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
