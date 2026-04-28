"""
Task: posthog-stickiness-axis-labels
Repo: posthog @ 314b93aa807030d5ef1c9bb17d44cb3609f10cb3
PR:   #53655

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
import subprocess
from pathlib import Path

REPO = "/workspace/posthog"
DATES_TS = f"{REPO}/frontend/src/lib/charts/utils/dates.ts"
LINEGRAPH_TSX = f"{REPO}/frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx"


def _call_tick_callback(allDays, interval="day", numericTickPrefix=None, test_values=None):
    """
    Transpile dates.ts via the TypeScript compiler API, stub out imports
    (the numeric-allDays early-return path does not touch dayjs), then call
    createXAxisTickCallback and return results as {value_index: output}.
    """
    opts = {"interval": interval, "allDays": allDays, "timezone": "UTC"}
    if numericTickPrefix is not None:
        opts["numericTickPrefix"] = numericTickPrefix

    if test_values is None:
        test_values = [[v, i] for i, v in enumerate(allDays)]

    script = (
        "const ts = require('typescript');\n"
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('__DATES__', 'utf8');\n"
        "const js = ts.transpileModule(src, {\n"
        "  compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },\n"
        "}).outputText;\n"
        "const m = { exports: {} };\n"
        "new Function('module', 'exports', 'require', js)(m, m.exports, () => ({}));\n"
        "const fn = m.exports.createXAxisTickCallback;\n"
        "if (!fn) { console.error('createXAxisTickCallback not exported'); process.exit(1); }\n"
        "const cb = fn(__OPTS__);\n"
        "const results = {};\n"
        "const inputs = __INPUTS__;\n"
        "for (const [val, idx] of inputs) {\n"
        "  results[String(val) + '_' + String(idx)] = cb(val, idx);\n"
        "}\n"
        "console.log(JSON.stringify(results));\n"
    )
    script = script.replace("__DATES__", DATES_TS)
    script = script.replace("__OPTS__", json.dumps(opts))
    script = script.replace("__INPUTS__", json.dumps(test_values))

    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=30, text=True,
    )
    assert r.returncode == 0, (
        f"Node script failed (exit {r.returncode}):\n{r.stderr}\n{r.stdout}"
    )
    return json.loads(r.stdout.strip())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_prefix_day_ticks():
    """createXAxisTickCallback returns 'Day N' when numericTickPrefix='Day' with numeric allDays."""
    results = _call_tick_callback(
        allDays=[1, 2, 3, 4, 5],
        interval="day",
        numericTickPrefix="Day",
        test_values=[[1, 0], [3, 2], [5, 4]],
    )
    assert results["1_0"] == "Day 1", f"Expected 'Day 1', got {results['1_0']!r}"
    assert results["3_2"] == "Day 3", f"Expected 'Day 3', got {results['3_2']!r}"
    assert results["5_4"] == "Day 5", f"Expected 'Day 5', got {results['5_4']!r}"


# [pr_diff] fail_to_pass
def test_prefix_week_and_month_ticks():
    """numericTickPrefix works for 'Week' and 'Month' prefixes, not just 'Day'."""
    week = _call_tick_callback(
        allDays=[1, 2, 3],
        interval="week",
        numericTickPrefix="Week",
        test_values=[[1, 0], [2, 1], [3, 2]],
    )
    assert week["1_0"] == "Week 1", f"Expected 'Week 1', got {week['1_0']!r}"
    assert week["2_1"] == "Week 2", f"Expected 'Week 2', got {week['2_1']!r}"
    assert week["3_2"] == "Week 3", f"Expected 'Week 3', got {week['3_2']!r}"

    month = _call_tick_callback(
        allDays=[1, 2, 3],
        interval="month",
        numericTickPrefix="Month",
        test_values=[[1, 0], [3, 2]],
    )
    assert month["1_0"] == "Month 1", f"Expected 'Month 1', got {month['1_0']!r}"
    assert month["3_2"] == "Month 3", f"Expected 'Month 3', got {month['3_2']!r}"


# [pr_diff] fail_to_pass
def test_linegraph_stickiness_wiring():
    """LineGraph.tsx passes numericTickPrefix to createXAxisTickCallback when isStickiness."""
    script = (
        "const ts = require('typescript');\n"
        "const fs = require('fs');\n"
        "const src = fs.readFileSync('__FILE__', 'utf8');\n"
        "const sf = ts.createSourceFile('LineGraph.tsx', src, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);\n"
        "let hasNumericTickPrefix = false;\n"
        "let hasIsStickiness = false;\n"
        "function visit(node) {\n"
        "  if (ts.isPropertyAssignment(node) && node.name.getText(sf) === 'numericTickPrefix') {\n"
        "    hasNumericTickPrefix = true;\n"
        "  }\n"
        "  if (ts.isIdentifier(node) && node.text === 'isStickiness') {\n"
        "    hasIsStickiness = true;\n"
        "  }\n"
        "  ts.forEachChild(node, visit);\n"
        "}\n"
        "visit(sf);\n"
        "console.log(JSON.stringify({ hasNumericTickPrefix, hasIsStickiness }));\n"
    ).replace("__FILE__", LINEGRAPH_TSX)

    r = subprocess.run(
        ["node", "-e", script],
        capture_output=True, timeout=30, text=True,
    )
    assert r.returncode == 0, f"Node script failed:\n{r.stderr}"
    result = json.loads(r.stdout.strip())
    assert result["hasNumericTickPrefix"], (
        "LineGraph.tsx must pass numericTickPrefix to createXAxisTickCallback"
    )
    assert result["hasIsStickiness"], (
        "LineGraph.tsx must reference isStickiness to determine when to add prefix"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass — regression + config guards
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_no_prefix_returns_plain_numbers():
    """Without numericTickPrefix, numeric allDays still return plain number strings."""
    results = _call_tick_callback(
        allDays=[1, 2, 3, 4, 5],
        interval="day",
        test_values=[[1, 0], [3, 2], [5, 4]],
    )
    assert results["1_0"] == "1", f"Expected '1', got {results['1_0']!r}"
    assert results["3_2"] == "3", f"Expected '3', got {results['3_2']!r}"
    assert results["5_4"] == "5", f"Expected '5', got {results['5_4']!r}"


# [agent_config] pass_to_pass — AGENTS.md:95
def test_dayjs_import_convention():
    """dates.ts must import dayjs from 'lib/dayjs', not directly from 'dayjs' package (AGENTS.md:95)."""
    src = Path(DATES_TS).read_text()
    direct_import = re.search(r"from\s+['\"]dayjs['\"]", src) or re.search(
        r"from\s+['\"]dayjs/", src
    )
    assert direct_import is None, (
        "dates.ts must use 'lib/dayjs', not import directly from 'dayjs' package"
    )
    lib_import = re.search(r"from\s+['\"]lib/dayjs['\"]", src)
    assert lib_import is not None, "dates.ts must import from 'lib/dayjs'"


# ---------------------------------------------------------------------------
# Pass-to-pass — repo CI/CD tests (pass on base commit and after fix)
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_lint_js():
    """Repo's JavaScript/TypeScript linting passes (pass_to_pass)."""
    setup = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && corepack enable && corepack prepare pnpm@10.29.3 --activate && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert setup.returncode == 0, f"Setup for oxlint failed:\n{setup.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && pnpm exec oxlint --quiet"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"JavaScript linting (oxlint) failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_jest_dates():
    """Repo's Jest tests for dates.ts module pass (pass_to_pass)."""
    setup = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && corepack enable && corepack prepare pnpm@10.29.3 --activate && pnpm install --frozen-lockfile >/dev/null 2>&1 && pnpm --filter=@posthog/frontend build:products >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert setup.returncode == 0, f"Setup for Jest failed:\n{setup.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog/frontend && pnpm exec jest --testPathPattern='dates.test.ts' --forceExit"],
        capture_output=True, text=True, timeout=180, cwd=REPO,
    )
    assert r.returncode == 0, f"Jest tests for dates.ts failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_lint_css():
    """Repo's CSS/SCSS linting passes (pass_to_pass)."""
    setup = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && corepack enable && corepack prepare pnpm@10.29.3 --activate && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert setup.returncode == 0, f"Setup for CSS linting failed:\n{setup.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && pnpm run lint:css"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"CSS linting (stylelint) failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_markdown_lint():
    """Repo's markdown linting passes (pass_to_pass)."""
    setup = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && corepack enable && corepack prepare pnpm@10.29.3 --activate && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert setup.returncode == 0, f"Setup for markdown linting failed:\n{setup.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && pnpm exec markdownlint-cli2 --config .config/.markdownlint-cli2.jsonc '**/*.{md,mdx}'"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Markdown linting failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_build_products():
    """Repo's frontend product build passes (pass_to_pass)."""
    setup = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && corepack enable && corepack prepare pnpm@10.29.3 --activate && pnpm install --frozen-lockfile >/dev/null 2>&1"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert setup.returncode == 0, f"Setup for product build failed:\n{setup.stderr[-500:]}"

    r = subprocess.run(
        ["bash", "-c", "cd /workspace/posthog && pnpm --filter=@posthog/frontend build:products"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Product build failed:\n{r.stderr[-500:]}{r.stdout[-500:]}"

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_returns_raw_value_when_days_are_numbers_and_no_p():
    """fail_to_pass | PR added test 'returns raw value when days are numbers and no prefix is provided' in 'frontend/src/lib/charts/utils/dates.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "frontend/src/lib/charts/utils/dates.test.ts" -t "returns raw value when days are numbers and no prefix is provided" 2>&1 || npx vitest run "frontend/src/lib/charts/utils/dates.test.ts" -t "returns raw value when days are numbers and no prefix is provided" 2>&1 || pnpm jest "frontend/src/lib/charts/utils/dates.test.ts" -t "returns raw value when days are numbers and no prefix is provided" 2>&1 || npx jest "frontend/src/lib/charts/utils/dates.test.ts" -t "returns raw value when days are numbers and no prefix is provided" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'returns raw value when days are numbers and no prefix is provided' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_formats_numbers_with_a_prefix_when_provided():
    """fail_to_pass | PR added test 'formats numbers with a prefix when provided' in 'frontend/src/lib/charts/utils/dates.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "frontend/src/lib/charts/utils/dates.test.ts" -t "formats numbers with a prefix when provided" 2>&1 || npx vitest run "frontend/src/lib/charts/utils/dates.test.ts" -t "formats numbers with a prefix when provided" 2>&1 || pnpm jest "frontend/src/lib/charts/utils/dates.test.ts" -t "formats numbers with a prefix when provided" 2>&1 || npx jest "frontend/src/lib/charts/utils/dates.test.ts" -t "formats numbers with a prefix when provided" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'formats numbers with a prefix when provided' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_dagster_tests_run_migrations():
    """pass_to_pass | CI job 'Dagster tests' → step 'Run migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py migrate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_dagster_tests_run_clickhouse_migrations():
    """pass_to_pass | CI job 'Dagster tests' → step 'Run clickhouse migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py migrate_clickhouse'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run clickhouse migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_dagster_tests_run_dagster_tests():
    """pass_to_pass | CI job 'Dagster tests' → step 'Run Dagster tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest posthog/dags --junitxml=junit-dagster.xml'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run Dagster tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_dagster_tests_run_products_dagster_tests():
    """pass_to_pass | CI job 'Dagster tests' → step 'Run products Dagster tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pytest products/**/dags --junitxml=junit-products.xml'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run products Dagster tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_lint_proto_definitions_lint_protos():
    """pass_to_pass | CI job 'Lint proto definitions' → step 'Lint protos'"""
    r = subprocess.run(
        ["bash", "-lc", 'buf lint proto/'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint protos' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_python_proto_stubs_are_u_check_for_diff():
    """pass_to_pass | CI job 'Check Python proto stubs are up to date' → step 'Check for diff'"""
    r = subprocess.run(
        ["bash", "-lc", 'if ! git diff --exit-code posthog/personhog_client/proto/generated/; then\n  echo ""\n  echo "ERROR: Generated Python proto stubs are out of date."\n  echo "Run \'bash bin/generate_personhog_proto.sh\' and commit the result."\n  exit 1\nfi\necho "Generated Python proto stubs are up to date."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for diff' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_for_breaking_changes_check_for_breaking_changes():
    """pass_to_pass | CI job 'Check for breaking changes' → step 'Check for breaking changes'"""
    r = subprocess.run(
        ["bash", "-lc", "buf breaking proto/ --against 'https://github.com/PostHog/posthog.git#branch=master,subdir=proto'"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check for breaking changes' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_llm_gateway_tests_run_tests():
    """pass_to_pass | CI job 'LLM Gateway Tests' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'uv run pytest tests/ -v --tb=short --junitxml=junit.xml'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_migrations_and_openap_check_migrations():
    """pass_to_pass | CI job 'Validate migrations and OpenAPI types' → step 'Check migrations'"""
    r = subprocess.run(
        ["bash", "-lc", 'python manage.py makemigrations --check --dry-run'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_migrations_and_openap_check_ch_migrations():
    """pass_to_pass | CI job 'Validate migrations and OpenAPI types' → step 'Check CH migrations'"""
    r = subprocess.run(
        ["bash", "-lc", '# Same as above, except now for CH looking at files that were added in posthog/clickhouse/migrations/\ngit diff --name-status origin/master..HEAD | grep "A\\sposthog/clickhouse/migrations/" | grep -v README | awk \'{print $2}\' | python manage.py test_ch_migrations_are_safe'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check CH migrations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_validate_migrations_and_openap_check_and_update_openapi_types():
    """pass_to_pass | CI job 'Validate migrations and OpenAPI types' → step 'Check and update OpenAPI types'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter=@posthog/mcp run scaffold-yaml -- --sync-all'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check and update OpenAPI types' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_discover_product_tests_discover_products_to_test():
    """pass_to_pass | CI job 'Discover product tests' → step 'Discover products to test'"""
    r = subprocess.run(
        ["bash", "-lc", '# turbo-discover.js diffs backend:test vs backend:contract-check\n# to detect isolated products. Non-isolated product changes trigger\n# the full suite (all products + Django).\nRESULT=$(node .github/scripts/turbo-discover.js)\necho "Result: $RESULT"\necho "matrix=$(echo "$RESULT" | jq -c \'.matrix\')" >> $GITHUB_OUTPUT\necho "run_legacy=$(echo "$RESULT" | jq -r \'.run_legacy\')" >> $GITHUB_OUTPUT\n\n# Keep contract-check remote cache warm for future runs\n./node_modules/.bin/turbo run backend:contract-check --output-logs=errors-only 2>/dev/null || true'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Discover products to test' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")