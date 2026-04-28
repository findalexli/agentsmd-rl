import subprocess
import json
import os
import tempfile
import atexit

REPO = "/workspace/openai-agents-js"

# Node.js test runner — written to temp once, reused across tests
_NODE_RUNNER = r"""// Test runner for milestone assignment behavior
import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = '/workspace/openai-agents-js';
const SCRIPT = join(REPO, '.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs');

const testInput = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const resultPath = process.argv[3];

const tmpDir = mkdtempSync(join(tmpdir(), 'mt-'));
const eventPath = join(tmpDir, 'event.json');
writeFileSync(eventPath, JSON.stringify({
  repository: { owner: { login: 'test' }, name: 'test' },
  pull_request: { number: 1 }
}));

process.env.GITHUB_TOKEN = 'test-token';
process.env.GITHUB_EVENT_PATH = eventPath;

let capturedMilestone = null;
// Suppress console.log from the module under test
globalThis.console = { ...globalThis.console, log: () => {}, warn: () => {} };
globalThis.fetch = async (url, options = {}) => {
  const urlStr = typeof url === 'string' ? url : String(url);
  if (urlStr.includes('/milestones')) {
    return { ok: true, status: 200, json: async () => testInput.milestones };
  }
  if (options && options.method === 'PATCH') {
    capturedMilestone = JSON.parse(options.body);
    return { ok: true, status: 200 };
  }
  return { ok: false, status: 500 };
};

let src = readFileSync(SCRIPT, 'utf8');
src = src.replace(/main\(\);/, '// patched by test harness');
if (!src.includes('export {')) {
  src += '\nexport { assignMilestone, parseMilestoneTitle };\n';
}

const modPath = join(tmpDir, `mod-${Date.now()}-${Math.random().toString(36).slice(2)}.mjs`);
writeFileSync(modPath, src, 'utf8');

try {
  const mod = await import(modPath);
  await mod.assignMilestone(testInput.requiredBump);
} catch (e) {
  writeFileSync(resultPath, JSON.stringify({ error: e.message }));
  process.exit(1);
}

writeFileSync(resultPath, JSON.stringify({
  captured: capturedMilestone,
  milestone: capturedMilestone ? capturedMilestone.milestone : null,
}));
"""

_runner_path = None
def _get_runner_path():
    global _runner_path
    if _runner_path is None:
        fd, _runner_path = tempfile.mkstemp(suffix='.mjs', prefix='milestone_runner_')
        os.write(fd, _NODE_RUNNER.encode())
        os.close(fd)
        atexit.register(lambda: os.unlink(_runner_path) if os.path.exists(_runner_path) else None)
    return _runner_path

def _run_milestone_test(required_bump, milestones):
    """Run the milestone assignment test with given parameters."""
    runner = _get_runner_path()
    test_data = {"requiredBump": required_bump, "milestones": milestones}
    fd, result_path = tempfile.mkstemp(suffix='.json', prefix='milestone_result_')
    os.close(fd)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        test_path = f.name
    try:
        r = subprocess.run(
            ["node", runner, test_path, result_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert r.returncode == 0, f"Runner error (exit={r.returncode}):\nstdout={r.stdout}\nstderr={r.stderr}"
        with open(result_path) as rf:
            return json.load(rf)
    finally:
        os.unlink(test_path)
        if os.path.exists(result_path):
            os.unlink(result_path)


def test_patch_selects_lowest_milestone():
    """When requiredBump is 'patch', the lowest (oldest) open milestone is selected."""
    milestones = [
        {"title": "0.5.x", "number": 5},
        {"title": "0.4.x", "number": 4},
        {"title": "0.3.x", "number": 3},
    ]
    result = _run_milestone_test("patch", milestones)
    assert result["milestone"] == 3, f"Expected milestone 3 (oldest 0.3.x), got {result['milestone']}"


def test_patch_selects_lowest_two_milestones():
    """Patch bump selects oldest even with only two open milestones."""
    milestones = [
        {"title": "2.1.x", "number": 21},
        {"title": "1.0.x", "number": 10},
    ]
    result = _run_milestone_test("patch", milestones)
    assert result["milestone"] == 10, f"Expected milestone 10 (oldest 1.0.x), got {result['milestone']}"


def test_minor_selects_second_newest():
    """Minor bump selects the second-newest milestone."""
    milestones = [
        {"title": "0.5.x", "number": 5},
        {"title": "0.4.x", "number": 4},
        {"title": "0.3.x", "number": 3},
    ]
    result = _run_milestone_test("minor", milestones)
    assert result["milestone"] == 4, f"Expected milestone 4 (0.4.x), got {result['milestone']}"


def test_minor_falls_back_to_only_milestone():
    """Minor bump falls back to the only open milestone when only one exists."""
    milestones = [
        {"title": "0.5.x", "number": 5},
    ]
    result = _run_milestone_test("minor", milestones)
    assert result["milestone"] == 5, f"Expected milestone 5 (only option), got {result['milestone']}"


def test_none_skips_assignment():
    """When requiredBump is 'none', no milestone is assigned."""
    milestones = [
        {"title": "0.5.x", "number": 5},
    ]
    result = _run_milestone_test("none", milestones)
    assert result["milestone"] is None, f"Expected no milestone assignment, got {result['milestone']}"


def test_parse_milestone_title():
    """parseMilestoneTitle correctly parses X.Y.x milestone titles."""
    runner = _get_runner_path()

    parse_test = r"""import { readFileSync, writeFileSync, mkdtempSync } from 'node:fs';
import { join } from 'node:path';
import { tmpdir } from 'node:os';

const REPO = '/workspace/openai-agents-js';
const SCRIPT = join(REPO, '.codex/skills/changeset-validation/scripts/changeset-assign-milestone.mjs');

let src = readFileSync(SCRIPT, 'utf8');
src = src.replace(/main\(\);/, '// patched');
src += '\nexport { parseMilestoneTitle };\n';

const tmpDir = mkdtempSync(join(tmpdir(), 'mt-parse-'));
const modPath = join(tmpDir, `mod-${Date.now()}.mjs`);
writeFileSync(modPath, src, 'utf8');

const { parseMilestoneTitle } = await import(modPath);

const cases = [
  ['0.5.x', { major: 0, minor: 5, title: '0.5.x' }],
  ['12.34.x', { major: 12, minor: 34, title: '12.34.x' }],
  ['not-a-milestone', null],
  ['v1.0', null],
  ['1.0.0', null],
  ['', null],
];

let failed = 0;
for (const [input, expected] of cases) {
  const got = parseMilestoneTitle(input);
  const ok = JSON.stringify(got) === JSON.stringify(expected);
  if (!ok) {
    console.error(`FAIL: parseMilestoneTitle(${JSON.stringify(input)}) = ${JSON.stringify(got)}, expected ${JSON.stringify(expected)}`);
    failed++;
  }
}

if (failed > 0) {
  console.error(`${failed} parse tests failed`);
  process.exit(1);
}
console.log('All parse tests passed');
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.mjs', delete=False) as f:
        f.write(parse_test)
        parse_test_path = f.name
    try:
        r = subprocess.run(
            ["node", parse_test_path],
            capture_output=True, text=True, timeout=30, cwd=REPO
        )
        assert r.returncode == 0, f"Parse test failed:\n{r.stderr}"
    finally:
        os.unlink(parse_test_path)


def test_repo_lint():
    """Repo linting passes."""
    r = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True, text=True, timeout=120, cwd=REPO
    )
    assert r.returncode == 0, f"Lint failed:\n{r.stderr[-1000:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_run_build():
    """pass_to_pass | CI job 'build' → step 'Run build'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_check_generated_declarations():
    """pass_to_pass | CI job 'test' → step 'Check generated declarations'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r -F "@openai/*" dist:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check generated declarations' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_linter():
    """pass_to_pass | CI job 'test' → step 'Run linter'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run linter' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_type_check_docs_scripts():
    """pass_to_pass | CI job 'test' → step 'Type-check docs scripts'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm docs:scripts:check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Type-check docs scripts' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_compile_examples():
    """pass_to_pass | CI job 'test' → step 'Compile examples'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm -r build-check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Compile examples' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")