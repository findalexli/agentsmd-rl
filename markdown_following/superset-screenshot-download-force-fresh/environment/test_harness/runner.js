/*
 * Synthetic harness that exercises useDownloadScreenshot without a real
 * React renderer. Captures the URL that the hook posts to
 * SupersetClient.post and prints it as the last line of stdout for the
 * Python test to parse.
 *
 * Usage: node runner.js <path-to-useDownloadScreenshot.ts>
 */
const path = require('path');
const fs = require('fs');
const Module = require('module');

const esbuild = require('esbuild');

const HOOK_PATH = process.argv[2];
if (!HOOK_PATH || !fs.existsSync(HOOK_PATH)) {
  console.error('runner.js: missing hook source path');
  process.exit(2);
}

const HARNESS = __dirname;
const MOCKS = path.join(HARNESS, 'mocks');

// Bundle the hook with every external import redirected to a stub.
// Relative imports (e.g. ../components/menu/DownloadMenuItems/types) are
// resolved against the real file tree at the base commit.
const result = esbuild.buildSync({
  entryPoints: [HOOK_PATH],
  bundle: true,
  platform: 'node',
  format: 'cjs',
  target: 'node20',
  write: false,
  logLevel: 'silent',
  alias: {
    react: path.join(MOCKS, 'react.js'),
    'react-redux': path.join(MOCKS, 'react-redux.js'),
    lodash: path.join(MOCKS, 'lodash.js'),
    'content-disposition': path.join(MOCKS, 'empty.js'),
    rison: path.join(HARNESS, 'node_modules', 'rison', 'js', 'rison.js'),
    '@superset-ui/core': path.join(MOCKS, 'superset-ui-core.js'),
    '@apache-superset/core/translation': path.join(MOCKS, 'translation.js'),
    '@apache-superset/core/utils': path.join(MOCKS, 'utils.js'),
    'src/components/MessageToasts/withToasts': path.join(MOCKS, 'empty.js'),
    'src/logger/LogUtils': path.join(MOCKS, 'logutils.js'),
    'src/utils/urlUtils': path.join(MOCKS, 'empty.js'),
    'src/dashboard/types': path.join(MOCKS, 'empty.js'),
  },
});

const code = result.outputFiles[0].text;

// Evaluate the bundle in a fresh CommonJS module so we can `require` its exports.
const bundleModule = new Module(path.join(HARNESS, '__bundle__.js'));
bundleModule.filename = path.join(HARNESS, '__bundle__.js');
bundleModule.paths = Module._nodeModulePaths(HARNESS);
bundleModule._compile(code, bundleModule.filename);

const { useDownloadScreenshot } = bundleModule.exports;
if (typeof useDownloadScreenshot !== 'function') {
  console.error('runner.js: useDownloadScreenshot was not exported from bundle');
  process.exit(3);
}

// Call the hook (synchronous in our stubbed React).
const dashboardId = 1234;
const downloadScreenshot = useDownloadScreenshot(dashboardId);

// PNG = 'png' per DownloadScreenshotFormat enum.
downloadScreenshot('png');

// Read shared capture state from globalThis (the bundled mock and this
// process share the same array).
setImmediate(() => {
  const calls = (globalThis.__supersetMock && globalThis.__supersetMock.postCalls) || [];
  if (calls.length === 0) {
    console.error('runner.js: SupersetClient.post was never called');
    process.exit(4);
  }
  const endpoint = calls[0].endpoint || '';
  // Last line of stdout is the parsed signal the Python test reads.
  console.log('ENDPOINT:' + endpoint);
  // Hook started timers (toast + retry intervals) that would keep Node
  // alive indefinitely; force-exit once we have the captured URL.
  process.exit(0);
});
