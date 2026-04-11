"""
Task: prisma-otel-v2-tracing-upgrade
Repo: prisma/prisma @ 423b58507879080bdc1273ca5d30b3de87e5b766
PR:   28268

Upgrade OpenTelemetry SDK from v1 to v2 in tracing test files and update
the @prisma/instrumentation README example code to match the new APIs.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/prisma"

TRACING_TEST_FILES = [
    "packages/client/tests/functional/tracing-disabled/tests.ts",
    "packages/client/tests/functional/tracing-filtered-spans/tests.ts",
    "packages/client/tests/functional/tracing-no-sampling/tests.ts",
    "packages/client/tests/functional/tracing/tests.ts",
]

README_PATH = "packages/instrumentation/README.md"

_otel_dir = None


def _get_otel_dir():
    """Install OTel v2 packages once in a temp dir; return the path."""
    global _otel_dir
    if _otel_dir is not None:
        return _otel_dir
    r = subprocess.run(
        ["bash", "-c", """
set -e
DIR=/tmp/_otel_v2_test
if [ -d "$DIR/node_modules/@opentelemetry/resources" ]; then echo "$DIR"; exit 0; fi
mkdir -p "$DIR" && cd "$DIR"
npm init -y > /dev/null 2>&1
npm install --save \
  @opentelemetry/api@^1.9.0 \
  @opentelemetry/resources@^2.0.0 \
  @opentelemetry/sdk-trace-base@^2.0.0 \
  @opentelemetry/semantic-conventions@^1.30.0 \
  > /dev/null 2>&1
echo "$DIR"
"""],
        capture_output=True, text=True, timeout=90,
    )
    assert r.returncode == 0, f"Failed to install OTel v2 packages: {r.stderr}"
    _otel_dir = r.stdout.strip()
    return _otel_dir


def _run_node_file(code: str, timeout: int = 30):
    """Write a Node.js script to a temp file and execute with v2 OTel on NODE_PATH."""
    otel_dir = _get_otel_dir()
    script = Path("/tmp/_eval_test.js")
    script.write_text(code)
    try:
        env = {**os.environ, "NODE_PATH": f"{otel_dir}/node_modules"}
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout,
            cwd=REPO, env=env,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """All modified TypeScript files exist and are non-empty."""
    for rel in TRACING_TEST_FILES + [README_PATH]:
        p = Path(REPO) / rel
        assert p.exists(), f"Missing file: {rel}"
        content = p.read_text()
        assert len(content) > 100, f"File too small (likely empty/corrupt): {rel}"


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

def test_repo_prettier_readme():
    """README.md passes prettier formatting check (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", f"{REPO}/{README_PATH}"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr}"


def test_repo_ts_syntax_tracing():
    """All tracing test files have valid TypeScript syntax (pass_to_pass)."""
    # Install babel parser in temp dir
    r = subprocess.run(
        ["bash", "-c", """
set -e
mkdir -p /tmp/babel-check && cd /tmp/babel-check
if [ ! -d node_modules/@babel/parser ]; then
  npm init -y > /dev/null 2>&1
  npm install @babel/parser > /dev/null 2>&1
fi
"""],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Failed to install babel parser: {r.stderr}"

    # Check each test file
    for rel in TRACING_TEST_FILES:
        test_file = Path(REPO) / rel
        code = """
const fs = require('fs');
const parser = require('/tmp/babel-check/node_modules/@babel/parser');
const code = fs.readFileSync('FILE_PATH', 'utf8');
parser.parse(code, { sourceType: 'module', plugins: ['typescript'] });
console.log('OK');
""".replace("FILE_PATH", str(test_file))

        r = subprocess.run(
            ["node", "-e", code],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, f"Syntax check failed for {rel}:\n{r.stderr}"


def test_repo_otel_v2_imports_resolve():
    """OTel v2 package imports resolve correctly at runtime (pass_to_pass)."""
    code = """
// Verify all v2 APIs can be imported and used
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } = require('@opentelemetry/semantic-conventions');
const { BasicTracerProvider, InMemorySpanExporter, SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { trace } = require('@opentelemetry/api');

// Verify imports are functions/constants
if (typeof resourceFromAttributes !== 'function') throw new Error('resourceFromAttributes not a function');
if (typeof ATTR_SERVICE_NAME !== 'string') throw new Error('ATTR_SERVICE_NAME not a string');
if (typeof ATTR_SERVICE_VERSION !== 'string') throw new Error('ATTR_SERVICE_VERSION not a string');
if (typeof BasicTracerProvider !== 'function') throw new Error('BasicTracerProvider not a function');
if (typeof InMemorySpanExporter !== 'function') throw new Error('InMemorySpanExporter not a function');
if (typeof SimpleSpanProcessor !== 'function') throw new Error('SimpleSpanProcessor not a function');
if (typeof trace.setGlobalTracerProvider !== 'function') throw new Error('trace.setGlobalTracerProvider not a function');

// Test creating a provider with v2 patterns
const exporter = new InMemorySpanExporter();
const provider = new BasicTracerProvider({
    resource: resourceFromAttributes({
        [ATTR_SERVICE_NAME]: 'test',
        [ATTR_SERVICE_VERSION]: '1.0.0',
    }),
    spanProcessors: [new SimpleSpanProcessor(exporter)],
});
trace.setGlobalTracerProvider(provider);

console.log('V2_IMPORTS_OK');
"""
    r = _run_node_file(code)
    assert r.returncode == 0, f"OTel v2 imports check failed:\n{r.stderr}"
    assert "V2_IMPORTS_OK" in r.stdout


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — behavioral code-execution tests
# ---------------------------------------------------------------------------

def test_v2_otel_provider_pattern():
    """OTel v2 provider initialization works at runtime and all tracing test
    files use v2 patterns (resourceFromAttributes, spanProcessors in
    constructor, trace.setGlobalTracerProvider)."""
    files_json = json.dumps([str(Path(REPO) / f) for f in TRACING_TEST_FILES])
    code = """
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { BasicTracerProvider, InMemorySpanExporter, SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } = require('@opentelemetry/semantic-conventions');
const { trace } = require('@opentelemetry/api');
const fs = require('fs');

// Exercise the full v2 initialization pattern to prove it works at runtime
const exporter = new InMemorySpanExporter();
const provider = new BasicTracerProvider({
    resource: resourceFromAttributes({
        [ATTR_SERVICE_NAME]: 'test',
        [ATTR_SERVICE_VERSION]: '1.0.0',
    }),
    spanProcessors: [new SimpleSpanProcessor(exporter)],
});
trace.setGlobalTracerProvider(provider);

// Verify each test file uses v2 patterns, not v1
const files = FILES_PLACEHOLDER;
const errors = [];
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const name = f.split('/').pop();
    if (!content.includes('resourceFromAttributes'))
        errors.push(name + ': missing resourceFromAttributes (v2)');
    if (content.includes('new Resource('))
        errors.push(name + ': uses deprecated new Resource() (v1)');
    if (!content.includes('spanProcessors'))
        errors.push(name + ': missing spanProcessors in constructor (v2)');
    if (content.includes('addSpanProcessor'))
        errors.push(name + ': uses deprecated addSpanProcessor() (v1)');
    if (!content.includes('setGlobalTracerProvider'))
        errors.push(name + ': missing trace.setGlobalTracerProvider() (v2)');
    if (/\\.register\\(\\)/.test(content))
        errors.push(name + ': uses deprecated .register() (v1)');
}

if (errors.length > 0) {
    console.error(JSON.stringify(errors, null, 2));
    process.exit(1);
}
console.log('V2_PROVIDER_OK');
""".replace("FILES_PLACEHOLDER", files_json)
    r = _run_node_file(code)
    assert r.returncode == 0, f"V2 provider pattern check failed:\n{r.stderr}"
    assert "V2_PROVIDER_OK" in r.stdout


def test_v2_semantic_conventions():
    """OTel v2 semantic convention constants resolve correctly at runtime and
    test files that previously used SEMRESATTRS_* now use ATTR_SERVICE_NAME/VERSION."""
    files_json = json.dumps([
        str(Path(REPO) / "packages/client/tests/functional/tracing-disabled/tests.ts"),
        str(Path(REPO) / "packages/client/tests/functional/tracing-no-sampling/tests.ts"),
    ])
    code = """
const { ATTR_SERVICE_NAME, ATTR_SERVICE_VERSION } = require('@opentelemetry/semantic-conventions');
const fs = require('fs');

// Verify v2 constants resolve to real string values at runtime
if (typeof ATTR_SERVICE_NAME !== 'string' || ATTR_SERVICE_NAME === '')
    throw new Error('ATTR_SERVICE_NAME did not resolve to a valid string');
if (typeof ATTR_SERVICE_VERSION !== 'string' || ATTR_SERVICE_VERSION === '')
    throw new Error('ATTR_SERVICE_VERSION did not resolve to a valid string');

// Verify the two files that previously used SEMRESATTRS_* now use ATTR_*
const files = FILES_PLACEHOLDER;
const errors = [];
for (const f of files) {
    const content = fs.readFileSync(f, 'utf8');
    const name = f.split('/').pop();
    if (!content.includes('ATTR_SERVICE_NAME'))
        errors.push(name + ': missing ATTR_SERVICE_NAME (v2)');
    if (!content.includes('ATTR_SERVICE_VERSION'))
        errors.push(name + ': missing ATTR_SERVICE_VERSION (v2)');
    if (content.includes('SEMRESATTRS_'))
        errors.push(name + ': uses deprecated SEMRESATTRS_ constants (v1)');
}

if (errors.length > 0) {
    console.error(JSON.stringify(errors, null, 2));
    process.exit(1);
}
console.log('V2_CONVENTIONS_OK');
""".replace("FILES_PLACEHOLDER", files_json)
    r = _run_node_file(code)
    assert r.returncode == 0, f"V2 semantic conventions check failed:\n{r.stderr}"
    assert "V2_CONVENTIONS_OK" in r.stdout


def test_parent_span_context_property():
    """tracing/tests.ts uses parentSpanContext?.spanId (v2) instead of
    parentSpanId (v1) for root span filtering and tree building."""
    test_file = str(Path(REPO) / "packages/client/tests/functional/tracing/tests.ts")
    code = """
const { BasicTracerProvider, InMemorySpanExporter, SimpleSpanProcessor } = require('@opentelemetry/sdk-trace-base');
const fs = require('fs');

// Exercise v2 SDK: create a span and verify ReadableSpan API shape
const exporter = new InMemorySpanExporter();
const provider = new BasicTracerProvider({
    spanProcessors: [new SimpleSpanProcessor(exporter)],
});
const tracer = provider.getTracer('test');

const span = tracer.startSpan('test-span');
span.end();

const spans = exporter.getFinishedSpans();
if (spans.length === 0) throw new Error('No spans exported from v2 SDK');

// v2 ReadableSpan exposes parentSpanContext (not parentSpanId)
const s = spans[0];
if ('parentSpanId' in s && !('parentSpanContext' in s))
    throw new Error('v2 SDK ReadableSpan should have parentSpanContext, not parentSpanId');

// Verify the test file uses parentSpanContext, not bare parentSpanId
const content = fs.readFileSync('TEST_FILE', 'utf8');
if (!content.includes('parentSpanContext'))
    throw new Error('tracing/tests.ts must use parentSpanContext?.spanId (v2)');

const lines = content.split('\\n');
for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed.includes('parentSpanId') && !trimmed.includes('parentSpanContext'))
        throw new Error('tracing/tests.ts uses deprecated parentSpanId: ' + trimmed);
}

console.log('PARENT_SPAN_CONTEXT_OK');
""".replace("TEST_FILE", test_file)
    r = _run_node_file(code)
    assert r.returncode == 0, f"parentSpanContext check failed:\n{r.stderr}"
    assert "PARENT_SPAN_CONTEXT_OK" in r.stdout


def test_readme_v2_example():
    """README.md Jaeger example uses v2 OTel APIs (resourceFromAttributes,
    ATTR_SERVICE_NAME/VERSION, spanProcessors, trace.setGlobalTracerProvider)."""
    readme_file = str(Path(REPO) / README_PATH)
    code = """
const { resourceFromAttributes } = require('@opentelemetry/resources');
const { ATTR_SERVICE_NAME } = require('@opentelemetry/semantic-conventions');
const fs = require('fs');

// Verify v2 APIs are real (sanity)
if (typeof resourceFromAttributes !== 'function')
    throw new Error('resourceFromAttributes is not a function in v2 package');

const content = fs.readFileSync('README_FILE', 'utf8');

// Find the TypeScript code block that contains the tracing setup
const codeBlocks = [...content.matchAll(/```ts\\n([\\s\\S]*?)```/g)].map(m => m[1]);
const tracingBlock = codeBlocks.find(b => b.includes('BasicTracerProvider'));
if (!tracingBlock)
    throw new Error('No TypeScript code block with BasicTracerProvider found in README');

const errors = [];
if (!tracingBlock.includes('resourceFromAttributes'))
    errors.push('missing resourceFromAttributes (v2)');
if (tracingBlock.includes('new Resource('))
    errors.push('uses deprecated new Resource() (v1)');
if (!tracingBlock.includes('ATTR_SERVICE_NAME'))
    errors.push('missing ATTR_SERVICE_NAME (v2)');
if (tracingBlock.includes('SEMRESATTRS_'))
    errors.push('uses deprecated SEMRESATTRS_ constants (v1)');
if (!tracingBlock.includes('spanProcessors'))
    errors.push('missing spanProcessors in constructor (v2)');
if (tracingBlock.includes('addSpanProcessor'))
    errors.push('uses deprecated addSpanProcessor() (v1)');
if (!tracingBlock.includes('setGlobalTracerProvider'))
    errors.push('missing trace.setGlobalTracerProvider() (v2)');
if (/\\.register\\(\\)/.test(tracingBlock))
    errors.push('uses deprecated .register() (v1)');

if (errors.length > 0) {
    console.error('README example: ' + JSON.stringify(errors, null, 2));
    process.exit(1);
}
console.log('README_V2_OK');
""".replace("README_FILE", readme_file)
    r = _run_node_file(code)
    assert r.returncode == 0, f"README v2 example check failed:\n{r.stderr}"
    assert "README_V2_OK" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static)
# ---------------------------------------------------------------------------

def test_not_stub():
    """Test files retain their full test logic (not stubbed out)."""
    content = (Path(REPO) / "packages/client/tests/functional/tracing/tests.ts").read_text()
    assert "BasicTracerProvider" in content, "tracing/tests.ts must create a BasicTracerProvider"
    assert "InMemorySpanExporter" in content, "tracing/tests.ts must use InMemorySpanExporter"
    assert "buildTree" in content, "tracing/tests.ts must have buildTree function"
    assert "getFinishedSpans" in content, "tracing/tests.ts must call getFinishedSpans"
    assert len(content.split("\n")) > 100, "tracing/tests.ts appears truncated"
