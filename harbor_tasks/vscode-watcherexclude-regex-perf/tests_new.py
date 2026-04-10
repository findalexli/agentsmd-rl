"""
Task: vscode-watcherexclude-regex-perf
Repo: microsoft/vscode @ 002f2d99e814b4068447558eef47ac8977d1c05a
PR:   306224

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Fix summary:
  - files.contribution.ts: Replace '**/.git/objects/**' glob patterns with
    '.git/objects/**' + '*/.git/objects/**' to avoid pathological RegExp in
    large workspaces. Add explanatory comment.
  - configuration.contribution.ts (sessions): Remove duplicate files.watcherExclude
    block (session override was applying the same pathological patterns).
"""

import subprocess, json
from pathlib import Path

REPO = Path("/workspace/vscode")
FC_FILE = REPO / "src/vs/workbench/contrib/files/browser/files.contribution.ts"
SC_FILE = REPO / "src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node.js in the repo directory."""
    script = REPO / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=str(REPO),
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_optimized_patterns_present():
    """New non-pathological watcherExclude patterns match correct paths.

    Extracts the default patterns from files.contribution.ts via Node.js,
    verifies all six new patterns exist, and validates each one matches
    the intended .git/.hg paths using glob evaluation.
    """
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync(
  'src/vs/workbench/contrib/files/browser/files.contribution.ts', 'utf8'
);

// Extract the default object near watcherExclude
const defaultMatch = content.match(/'default':\\s*\\{([^}]+)\\}/);
if (!defaultMatch) {
  console.error('No default block found');
  process.exit(1);
}

const block = defaultMatch[1];
const patterns = [];
const re = /'([^']+)':\\s*true/g;
let m;
while ((m = re.exec(block)) !== null) {
  patterns.push(m[1]);
}

// Simple glob matcher for the pattern types in this fix:
//   "X/**"   -> path starts with "X/"
//   "*/X/**" -> exactly one segment, then "/X/", then anything
function globMatch(path, pattern) {
  if (!pattern.endsWith('/**')) return path === pattern;
  const base = pattern.slice(0, -3);
  if (base.startsWith('*/')) {
    const target = base.slice(2);
    const slashIdx = path.indexOf('/');
    if (slashIdx === -1) return false;
    const rest = path.slice(slashIdx + 1);
    return rest.startsWith(target + '/') || rest === target;
  }
  return path.startsWith(base + '/') || path === base;
}

// Required new patterns
const required = [
  '.git/objects/**', '.git/subtree-cache/**', '.hg/store/**',
  '*/.git/objects/**', '*/.git/subtree-cache/**', '*/.hg/store/**'
];
const missing = required.filter(p => !patterns.includes(p));
if (missing.length > 0) {
  console.error('Missing patterns: ' + JSON.stringify(missing));
  process.exit(1);
}

// Verify each pattern matches expected paths correctly
const tests = [
  { pattern: '.git/objects/**', path: '.git/objects/pack/abc.pack', expect: true },
  { pattern: '.git/objects/**', path: '.git/objects/ab/cd1234', expect: true },
  { pattern: '.git/subtree-cache/**', path: '.git/subtree-cache/abc', expect: true },
  { pattern: '.hg/store/**', path: '.hg/store/data/xyz.i', expect: true },
  { pattern: '*/.git/objects/**', path: 'project/.git/objects/pack/foo.pack', expect: true },
  { pattern: '*/.git/subtree-cache/**', path: 'subdir/.git/subtree-cache/abc', expect: true },
  { pattern: '*/.hg/store/**', path: 'subproject/.hg/store/data/foo', expect: true },
  // Negative cases: deeper nesting should NOT match */ patterns
  { pattern: '*/.git/objects/**', path: 'vendor/lib/.git/objects/abc', expect: false },
  // Source code should never match exclusion patterns
  { pattern: '.git/objects/**', path: 'src/main.ts', expect: false },
  { pattern: '.hg/store/**', path: 'package.json', expect: false },
];

const failures = [];
for (const t of tests) {
  const result = globMatch(t.path, t.pattern);
  if (result !== t.expect) {
    failures.push(`"${t.pattern}" vs "${t.path}": expected ${t.expect}, got ${result}`);
  }
}
if (failures.length > 0) {
  console.error('Pattern match failures:\\n' + failures.join('\\n'));
  process.exit(1);
}

console.log(JSON.stringify({ patterns, verified: tests.length }));
""")
    assert r.returncode == 0, f"Pattern verification failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    required = [
        '.git/objects/**', '.git/subtree-cache/**', '.hg/store/**',
        '*/.git/objects/**', '*/.git/subtree-cache/**', '*/.hg/store/**'
    ]
    for p in required:
        assert p in data['patterns'], f"Missing pattern: {p}"
    assert data['verified'] == 10, f"Expected 10 verified glob tests, got {data['verified']}"


# [pr_diff] fail_to_pass
def test_pathological_patterns_removed():
    """Old '**/' prefix patterns removed — they generate catastrophically complex RegExp.

    Parses the default block via Node.js and confirms no '**/...' patterns
    remain (the old patterns caused exponential backtracking in the watcher).
    """
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync(
  'src/vs/workbench/contrib/files/browser/files.contribution.ts', 'utf8'
);

const defaultMatch = content.match(/'default':\\s*\\{([^}]+)\\}/);
if (!defaultMatch) {
  console.error('No default block found');
  process.exit(1);
}

const block = defaultMatch[1];
const patterns = [];
const re = /'([^']+)':\\s*true/g;
let m;
while ((m = re.exec(block)) !== null) {
  patterns.push(m[1]);
}

// Any pattern starting with **/ is the old pathological form
const pathological = patterns.filter(p => p.startsWith('**/'));
if (pathological.length > 0) {
  console.error('Pathological patterns still present: ' + JSON.stringify(pathological));
  process.exit(1);
}

console.log(JSON.stringify({ clean: true, patternCount: patterns.length }));
""")
    assert r.returncode == 0, f"Old pathological patterns still present: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data['clean'] is True


# [pr_diff] fail_to_pass
def test_performance_comment_present():
    """Explanatory comment documenting why '**' prefix patterns are avoided."""
    content = FC_FILE.read_text()

    assert "Avoiding a" in content and "**" in content, \
        "Missing comment about avoiding '**' patterns"
    assert "slow things down" in content or "complex" in content, \
        "Missing performance explanation in comment"


# [pr_diff] fail_to_pass
def test_session_config_duplicate_removed():
    """Duplicate files.watcherExclude removed from sessions configuration.

    Parses the session config via Node.js and verifies no watcherExclude
    override remains (the sessions contrib was re-applying the same
    pathological patterns, defeating the workbench-level fix).
    """
    r = _run_node("""
import fs from 'fs';
const content = fs.readFileSync(
  'src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts', 'utf8'
);

if (content.includes("'files.watcherExclude'")) {
  console.error('Duplicate files.watcherExclude still present in sessions config');
  process.exit(1);
}

// Verify the file still has its core registration (not accidentally deleted)
if (!content.includes('registerDefaultConfigurations')) {
  console.error('Session config corrupted: registerDefaultConfigurations missing');
  process.exit(1);
}

console.log(JSON.stringify({ duplicateRemoved: true }));
""")
    assert r.returncode == 0, f"Session config check failed: {r.stderr}"
    data = json.loads(r.stdout.strip())
    assert data['duplicateRemoved'] is True


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression tests
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_watcher_exclude_still_in_workbench():
    """watcherExclude configuration is still defined in the workbench files config.

    The fix replaces the default value; it must NOT remove the setting entirely.
    """
    content = FC_FILE.read_text()

    assert "watcherExclude" in content, \
        "watcherExclude key missing — configuration was removed instead of patched"
    assert "'default':" in content, \
        "'default' section missing from watcherExclude configuration"


# [static] pass_to_pass
def test_config_files_still_register():
    """Both TypeScript files still call their respective registration APIs."""
    fc_content = FC_FILE.read_text()
    sc_content = SC_FILE.read_text()

    assert "registerConfiguration" in fc_content, \
        "files.contribution.ts no longer calls registerConfiguration"
    assert "registerDefaultConfigurations" in sc_content, \
        "configuration.contribution.ts no longer calls registerDefaultConfigurations"


# [repo_tests] pass_to_pass
def test_repo_eslint_files_contrib():
    """ESLint passes on files contribution module (pass_to_pass)."""
    r = subprocess.run(
        ["node", "build/eslint.ts", "src/vs/workbench/contrib/files/browser/files.contribution.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on files.contribution.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_eslint_session_config():
    """ESLint passes on sessions configuration contribution (pass_to_pass)."""
    r = subprocess.run(
        ["node", "build/eslint.ts", "src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed on configuration.contribution.ts:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_hygiene_check():
    """Repository hygiene checks pass (pass_to_pass).

    Runs the precommit hygiene check (experimental-strip-types) which
    validates code formatting and basic structure.
    """
    r = subprocess.run(
        ["npm", "run", "precommit"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Hygiene check failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Config-derived (agent_config) — rules from .github/copilot-instructions.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — .github/copilot-instructions.md:112 @ 002f2d99e814b4068447558eef47ac8977d1c05a
def test_tab_indentation_in_files_contribution():
    """files.contribution.ts uses tabs (not spaces) for indentation per VS Code style guide."""
    content = FC_FILE.read_text()
    lines = content.splitlines()

    tab_indented = sum(1 for line in lines if line.startswith("\t"))
    space_indented = sum(1 for line in lines if line.startswith("    ") and not line.startswith("\t"))

    assert tab_indented > 10, \
        f"Expected tab-indented lines, found only {tab_indented} — file may use spaces"
    assert space_indented < 5, \
        f"Found {space_indented} space-indented lines; file must use tabs per copilot-instructions.md:112"
