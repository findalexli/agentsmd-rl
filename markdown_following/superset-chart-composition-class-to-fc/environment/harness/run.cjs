/* eslint-disable */
// Compiles + loads the three chart-composition components from the agent's
// working tree, then prints a JSON object describing each component to stdout.

const path = require('path');
const fs = require('fs');
const Module = require('module');
const { JSDOM } = require('jsdom');
const esbuild = require('esbuild');

const REPO_SRC = '/workspace/superset/superset-frontend/packages/superset-ui-core/src';
const TARGETS = {
  ChartFrame: path.join(REPO_SRC, 'chart-composition/ChartFrame.tsx'),
  WithLegend: path.join(REPO_SRC, 'chart-composition/legend/WithLegend.tsx'),
  TooltipFrame: path.join(REPO_SRC, 'chart-composition/tooltip/TooltipFrame.tsx'),
};

const dom = new JSDOM('<!doctype html><html><body></body></html>', { url: 'http://localhost/' });
global.window = dom.window;
global.document = dom.window.document;
global.navigator = dom.window.navigator;
global.HTMLElement = dom.window.HTMLElement;
global.Element = dom.window.Element;
global.Node = dom.window.Node;

const HARNESS_NM = '/test_harness/node_modules';

// esbuild plugin: redirect '../utils' (any depth) and other repo-internal
// barrel imports to a minimal stub providing only `isDefined`.
const stubsPlugin = {
  name: 'stubs',
  setup(build) {
    const stubUtilsPath = '/test_harness/stub_utils.js';
    if (!fs.existsSync(stubUtilsPath)) {
      fs.writeFileSync(
        stubUtilsPath,
        "exports.isDefined = function isDefined(x){return x!==null && x!==undefined;};\n",
      );
    }
    build.onResolve({ filter: /(^|\/)\.\.\/utils$/ }, () => ({ path: stubUtilsPath }));
    build.onResolve({ filter: /(^|\/)\.\.\/\.\.\/utils$/ }, () => ({ path: stubUtilsPath }));
    // Also catch any direct ../utils relative to source files
    build.onResolve({ filter: /\.\.\/utils$/ }, () => ({ path: stubUtilsPath }));
  },
};

async function loadCompiled(srcPath) {
  const result = await esbuild.build({
    entryPoints: [srcPath],
    bundle: true,
    platform: 'node',
    format: 'cjs',
    target: 'node22',
    write: false,
    jsx: 'automatic',
    jsxImportSource: 'react',
    loader: { '.ts': 'ts', '.tsx': 'tsx' },
    sourcemap: false,
    logLevel: 'silent',
    nodePaths: [HARNESS_NM],
    resolveExtensions: ['.tsx', '.ts', '.jsx', '.js'],
    external: ['react', 'react/*', 'react-dom', 'react-dom/*', '@visx/responsive', '@visx/*'],
    plugins: [stubsPlugin],
    tsconfigRaw: '{}',
  });
  const code = result.outputFiles[0].text;
  const m = new Module(srcPath);
  m.filename = srcPath;
  m.paths = [HARNESS_NM, ...Module._nodeModulePaths(path.dirname(srcPath))];
  m._compile(code, srcPath);
  return m.exports;
}

const React = require(path.join(HARNESS_NM, 'react'));
const ReactDOMServer = require(path.join(HARNESS_NM, 'react-dom/server'));
global.React = React;

const REACT_MEMO = Symbol.for('react.memo');
const REACT_FORWARD_REF = Symbol.for('react.forward_ref');

function describe(comp) {
  const out = { typeof_str: typeof comp };
  if (comp == null) {
    out.is_null = true;
    return out;
  }
  out.is_memo = comp.$$typeof === REACT_MEMO;
  out.is_forward_ref = comp.$$typeof === REACT_FORWARD_REF;
  let inner = comp;
  if (out.is_memo) inner = comp.type;
  out.inner_typeof = typeof inner;
  out.inner_is_class = !!(inner && inner.prototype && inner.prototype.isReactComponent);
  out.inner_is_pure_class = !!(inner && inner.prototype && inner.prototype.isPureReactComponent);
  out.has_static_default_props = !!(inner && inner.defaultProps);
  out.fn_name = inner && inner.name ? inner.name : null;
  return out;
}

function renderToString(element) {
  try {
    return { ok: true, html: ReactDOMServer.renderToStaticMarkup(element) };
  } catch (e) {
    return { ok: false, error: String(e && e.message || e) };
  }
}

const result = { components: {}, renders: {} };

(async () => {
for (const [name, p] of Object.entries(TARGETS)) {
  try {
    const mod = await loadCompiled(p);
    const exp = mod.default;
    result.components[name] = describe(exp);
    const src = fs.readFileSync(p, 'utf8');
    result.components[name].source_uses_purecomponent = /\bPureComponent\b/.test(src);
    result.components[name].source_uses_class_keyword =
      new RegExp(`\\bclass\\s+${name}\\b`).test(src);
  } catch (e) {
    result.components[name] = { error: String(e && e.message || e) };
  }
}

try {
  const ChartFrame = (await loadCompiled(TARGETS.ChartFrame)).default;

  result.renders.ChartFrame_default_render = renderToString(
    React.createElement(ChartFrame, { width: 100, height: 100 })
  );

  result.renders.ChartFrame_fits = renderToString(
    React.createElement(ChartFrame, {
      width: 200,
      height: 200,
      renderContent: ({ width, height }) =>
        React.createElement('span', { 'data-testid': 'rc' }, `${width}x${height}`),
    })
  );

  result.renders.ChartFrame_overflowX = renderToString(
    React.createElement(ChartFrame, {
      width: 100,
      height: 100,
      contentWidth: 300,
      renderContent: ({ width, height }) =>
        React.createElement('span', null, `${width}x${height}`),
    })
  );

  const TooltipFrame = (await loadCompiled(TARGETS.TooltipFrame)).default;
  result.renders.TooltipFrame_default = renderToString(
    React.createElement(TooltipFrame, null,
      React.createElement('span', null, 'inner'))
  );
  result.renders.TooltipFrame_with_class = renderToString(
    React.createElement(TooltipFrame, { className: 'tt' },
      React.createElement('span', null, 'inner'))
  );

  const WithLegend = (await loadCompiled(TARGETS.WithLegend)).default;
  result.renders.WithLegend_smoke = renderToString(
    React.createElement(WithLegend, {
      renderChart: ({ width, height }) =>
        React.createElement('span', null, `chart-${width}-${height}`),
    })
  );
  result.renders.WithLegend_with_legend = renderToString(
    React.createElement(WithLegend, {
      position: 'left',
      renderChart: () => React.createElement('span', null, 'c'),
      renderLegend: ({ direction }) =>
        React.createElement('em', null, `legend-${direction}`),
    })
  );
} catch (e) {
  result.renders.fatal = String(e && e.stack || e);
}

process.stdout.write(JSON.stringify(result, null, 2));
})();
