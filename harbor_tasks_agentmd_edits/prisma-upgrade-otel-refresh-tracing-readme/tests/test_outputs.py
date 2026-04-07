"""
Task: prisma-upgrade-otel-refresh-tracing-readme
Repo: prisma/prisma @ 423b58507879080bdc1273ca5d30b3de87e5b766
PR:   28268

Upgrade OpenTelemetry deps to v2 and refresh tracing setup in client tests
and @prisma/instrumentation README examples.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / validation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_json_syntax_check():
    """package.json files modified by this PR must be valid JSON."""
    pkg_files = [
        "packages/client/package.json",
        "packages/query-plan-executor/package.json",
    ]
    for pkg_file in pkg_files:
        r = subprocess.run(
            ["node", "-e", f"JSON.parse(require('fs').readFileSync('{pkg_file}', 'utf8'))"],
            cwd=REPO, capture_output=True, text=True, timeout=10,
        )
        assert r.returncode == 0, f"{pkg_file} is not valid JSON: {r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_client_otel_versions_upgraded():
    """packages/client/package.json has updated OpenTelemetry dependency versions."""
    r = subprocess.run(
        ["node", "-e", """
const pkg = JSON.parse(require('fs').readFileSync('packages/client/package.json', 'utf8'));
const deps = Object.assign({}, pkg.dependencies || {}, pkg.devDependencies || {});
const checks = {
    '@opentelemetry/resources': v => v.startsWith('2.'),
    '@opentelemetry/sdk-trace-base': v => v.startsWith('2.'),
    '@opentelemetry/semantic-conventions': v => {
        const minor = parseInt(v.split('.')[1], 10);
        return minor >= 37;
    },
};
let ok = true;
for (const [name, test] of Object.entries(checks)) {
    const ver = deps[name];
    if (!ver || !test(ver)) {
        console.error(name + ' = ' + (ver || 'MISSING') + ' — expected upgrade');
        ok = false;
    }
}
if (!ok) process.exit(1);
console.log('All OTel versions OK');
"""],
        cwd=REPO, capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, f"OTel versions not upgraded:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_tracing_tests_use_resource_from_attributes():
    """All tracing test files must use resourceFromAttributes (not new Resource)."""
    for ts_file in TRACING_TEST_FILES:
        content = (Path(REPO) / ts_file).read_text()
        assert "resourceFromAttributes" in content, \
            f"{ts_file}: must use resourceFromAttributes instead of new Resource"
        assert "new Resource(" not in content, \
            f"{ts_file}: still contains deprecated 'new Resource(' constructor"


# [pr_diff] fail_to_pass
def test_tracing_tests_use_set_global_tracer():
    """All tracing test files must use trace.setGlobalTracerProvider (not .register())."""
    for ts_file in TRACING_TEST_FILES:
        content = (Path(REPO) / ts_file).read_text()
        assert "setGlobalTracerProvider" in content, \
            f"{ts_file}: must use trace.setGlobalTracerProvider()"
        assert ".register()" not in content, \
            f"{ts_file}: still contains deprecated .register() call"


# [pr_diff] fail_to_pass
def test_tracing_uses_parent_span_context():
    """tracing/tests.ts must use parentSpanContext?.spanId (not parentSpanId)."""
    content = (Path(REPO) / "packages/client/tests/functional/tracing/tests.ts").read_text()
    assert "parentSpanContext?.spanId" in content, \
        "tracing/tests.ts: must use parentSpanContext?.spanId (v2 API)"
    assert "span.parentSpanId" not in content, \
        "tracing/tests.ts: still contains deprecated span.parentSpanId"


# [pr_diff] fail_to_pass
def test_tracing_tests_use_span_processors_option():
    """Tracing test files must pass spanProcessors in the constructor (not addSpanProcessor)."""
    for ts_file in TRACING_TEST_FILES:
        content = (Path(REPO) / ts_file).read_text()
        assert "spanProcessors" in content, \
            f"{ts_file}: must use spanProcessors option in BasicTracerProvider constructor"
        assert "addSpanProcessor" not in content, \
            f"{ts_file}: still contains deprecated addSpanProcessor() call"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_uses_resource_from_attributes():
    """README.md Jaeger example must use resourceFromAttributes (not new Resource)."""
    content = (Path(REPO) / README_PATH).read_text()
    assert "resourceFromAttributes" in content, \
        "README.md: Jaeger example must use resourceFromAttributes"
    assert "new Resource(" not in content, \
        "README.md: still contains deprecated 'new Resource(' constructor"


# [pr_diff] fail_to_pass
def test_readme_uses_new_semantic_conventions():
    """README.md must use ATTR_SERVICE_NAME/VERSION (not deprecated SEMRESATTRS_)."""
    content = (Path(REPO) / README_PATH).read_text()
    assert "ATTR_SERVICE_NAME" in content, \
        "README.md: must use ATTR_SERVICE_NAME"
    assert "ATTR_SERVICE_VERSION" in content, \
        "README.md: must use ATTR_SERVICE_VERSION"
    assert "SEMRESATTRS_" not in content, \
        "README.md: still contains deprecated SEMRESATTRS_ constants"


# [pr_diff] fail_to_pass
def test_readme_uses_set_global_tracer():
    """README.md Jaeger example must use trace.setGlobalTracerProvider (not .register())."""
    content = (Path(REPO) / README_PATH).read_text()
    assert "setGlobalTracerProvider" in content, \
        "README.md: must use trace.setGlobalTracerProvider()"
    assert "provider.register()" not in content, \
        "README.md: still contains deprecated provider.register() call"
