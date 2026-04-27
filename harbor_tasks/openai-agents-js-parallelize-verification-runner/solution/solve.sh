#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openai-agents-js

# Idempotency guard: bail out if patch already applied.
if grep -q "createDefaultPlan" .agents/skills/code-change-verification/scripts/run.sh 2>/dev/null \
   || [ -f .agents/skills/code-change-verification/scripts/run.mjs ] && grep -q "export function createDefaultPlan" .agents/skills/code-change-verification/scripts/run.mjs 2>/dev/null; then
    if [ -f .agents/skills/code-change-verification/scripts/run.mjs ]; then
        echo "Patch already applied; nothing to do."
        exit 0
    fi
fi

cat > /tmp/gold.patch <<'PATCH'
diff --git a/.agents/skills/code-change-verification/SKILL.md b/.agents/skills/code-change-verification/SKILL.md
index 67dc31754..9b291f304 100644
--- a/.agents/skills/code-change-verification/SKILL.md
+++ b/.agents/skills/code-change-verification/SKILL.md
@@ -19,16 +19,18 @@ Ensure work is only marked complete after installing dependencies, building, lin
 
 ## Manual workflow
 
-- Run from the repository root in this order: `pnpm i`, `pnpm build`, `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, `pnpm test`.
-- Do not skip steps; stop and fix issues immediately when a command fails.
-- Re-run the full stack after applying fixes so the commands execute in the required order.
+- Run from the repository root in these phases: `pnpm i`, `pnpm build`, then `pnpm -r build-check`, `pnpm -r -F "@openai/*" dist:check`, `pnpm lint`, and `pnpm test`.
+- The skill may execute the final validation phase in parallel, but every step above must still pass.
+- Do not skip steps; stop and fix issues immediately when any step fails.
+- Re-run the full stack after applying fixes so the commands execute with the same barriers and coverage.
 
 ## Resources
 
 ### scripts/run.sh
 
 - Executes the full verification sequence (including declaration checks) with fail-fast semantics.
-- Prefer this entry point to ensure the commands always run in the correct order from the repo root.
+- Keeps `pnpm i` and `pnpm build` as barriers, then runs independent validation steps in parallel.
+- Prefer this entry point to ensure the commands always run from the repo root with the expected fail-fast behavior.
 
 ### scripts/run.ps1
 
diff --git a/.agents/skills/code-change-verification/scripts/run.mjs b/.agents/skills/code-change-verification/scripts/run.mjs
new file mode 100644
index 000000000..6aaeb0590
--- /dev/null
+++ b/.agents/skills/code-change-verification/scripts/run.mjs
@@ -0,0 +1,329 @@
+#!/usr/bin/env node
+
+import { execFileSync, spawn } from 'node:child_process';
+import path from 'node:path';
+import { fileURLToPath } from 'node:url';
+
+const { console, process, setTimeout } = globalThis;
+
+const SIGNAL_EXIT_CODES = {
+  SIGINT: 2,
+  SIGKILL: 9,
+  SIGTERM: 15,
+};
+
+const TERMINATION_GRACE_PERIOD_MS = 5_000;
+const scriptPath = fileURLToPath(import.meta.url);
+const scriptDir = path.dirname(scriptPath);
+
+function printUsage() {
+  console.log(`code-change-verification
+
+Usage:
+  node .agents/skills/code-change-verification/scripts/run.mjs
+`);
+}
+
+function getRepoRoot() {
+  try {
+    return execFileSync(
+      'git',
+      ['-C', scriptDir, 'rev-parse', '--show-toplevel'],
+      {
+        encoding: 'utf8',
+        stdio: ['ignore', 'pipe', 'ignore'],
+      },
+    ).trim();
+  } catch {
+    return path.resolve(scriptDir, '../../../..');
+  }
+}
+
+function getPnpmCommand() {
+  return process.platform === 'win32' ? 'pnpm.cmd' : 'pnpm';
+}
+
+function createPnpmStep(label, args) {
+  return {
+    label,
+    command: getPnpmCommand(),
+    args,
+    commandText: `pnpm ${args.join(' ')}`,
+  };
+}
+
+export function createDefaultPlan() {
+  return {
+    sequentialSteps: [
+      createPnpmStep('install', ['i']),
+      createPnpmStep('build', ['build']),
+    ],
+    parallelSteps: [
+      createPnpmStep('build-check', ['-r', 'build-check']),
+      createPnpmStep('dist-check', ['-r', '-F', '@openai/*', 'dist:check']),
+      createPnpmStep('lint', ['lint']),
+      createPnpmStep('test', ['test']),
+    ],
+  };
+}
+
+function splitBufferedLines(buffer) {
+  return buffer.split(/\r\n|[\n\r]/);
+}
+
+function forwardPrefixedOutput(stream, target, label) {
+  return new Promise((resolve, reject) => {
+    let buffer = '';
+
+    stream.setEncoding('utf8');
+    stream.on('data', (chunk) => {
+      buffer += chunk;
+      const lines = splitBufferedLines(buffer);
+      buffer = lines.pop() ?? '';
+      for (const line of lines) {
+        target.write(`[${label}] ${line}\n`);
+      }
+    });
+    stream.on('error', reject);
+    stream.on('end', () => {
+      if (buffer) {
+        target.write(`[${label}] ${buffer}\n`);
+      }
+      resolve();
+    });
+  });
+}
+
+function normalizeExitCode(code, signal) {
+  if (typeof code === 'number') {
+    return code;
+  }
+  if (signal && SIGNAL_EXIT_CODES[signal]) {
+    return 128 + SIGNAL_EXIT_CODES[signal];
+  }
+  return 1;
+}
+
+function startStep(step, repoRoot) {
+  console.log(`Running ${step.commandText}...`);
+
+  const child = spawn(step.command, step.args, {
+    cwd: repoRoot,
+    detached: process.platform !== 'win32',
+    env: process.env,
+    stdio: ['ignore', 'pipe', 'pipe'],
+  });
+  const stdoutDone = forwardPrefixedOutput(
+    child.stdout,
+    process.stdout,
+    step.label,
+  );
+  const stderrDone = forwardPrefixedOutput(
+    child.stderr,
+    process.stderr,
+    step.label,
+  );
+
+  const result = new Promise((resolve) => {
+    let settled = false;
+    const finish = (payload) => {
+      if (settled) {
+        return;
+      }
+      settled = true;
+      resolve(payload);
+    };
+
+    child.on('error', (error) => {
+      finish({ code: 1, error, signal: null, step });
+    });
+    child.on('exit', (code, signal) => {
+      finish({ code, error: null, signal, step });
+    });
+  }).then(async (payload) => {
+    await Promise.allSettled([stdoutDone, stderrDone]);
+    return {
+      ...payload,
+      exitCode: normalizeExitCode(payload.code, payload.signal),
+    };
+  });
+
+  return { child, result, step };
+}
+
+async function killWindowsProcessTree(pid) {
+  await new Promise((resolve) => {
+    const killer = spawn('taskkill', ['/PID', String(pid), '/T', '/F'], {
+      stdio: 'ignore',
+    });
+    killer.on('error', () => resolve());
+    killer.on('exit', () => resolve());
+  });
+}
+
+async function terminateRun(run, force = false) {
+  const { child } = run;
+
+  if (!child.pid) {
+    return;
+  }
+
+  if (process.platform === 'win32') {
+    await killWindowsProcessTree(child.pid);
+    return;
+  }
+
+  const signal = force ? 'SIGKILL' : 'SIGTERM';
+  try {
+    process.kill(-child.pid, signal);
+  } catch {
+    try {
+      child.kill(signal);
+    } catch {
+      // Ignore termination races.
+    }
+  }
+}
+
+async function stopRemainingRuns(runs, failedLabel) {
+  const survivors = runs.filter((run) => run.step.label !== failedLabel);
+  await Promise.allSettled(survivors.map((run) => terminateRun(run)));
+  await Promise.race([
+    Promise.allSettled(survivors.map((run) => run.result)),
+    new Promise((resolve) => setTimeout(resolve, TERMINATION_GRACE_PERIOD_MS)),
+  ]);
+  await Promise.allSettled(survivors.map((run) => terminateRun(run, true)));
+}
+
+async function runStep(step, repoRoot, activeRuns) {
+  const run = startStep(step, repoRoot);
+  activeRuns.add(run);
+  const result = await run.result;
+  activeRuns.delete(run);
+  return result;
+}
+
+async function runParallelSteps(steps, repoRoot, activeRuns) {
+  const runs = steps.map((step) => startStep(step, repoRoot));
+  for (const run of runs) {
+    activeRuns.add(run);
+  }
+
+  const allDone = Promise.all(runs.map((run) => run.result));
+  const firstFailure = new Promise((resolve) => {
+    for (const run of runs) {
+      run.result.then((result) => {
+        if (result.exitCode !== 0) {
+          resolve(result);
+        }
+      });
+    }
+  });
+
+  const outcome = await Promise.race([
+    allDone.then((results) => ({ results, type: 'done' })),
+    firstFailure.then((result) => ({ result, type: 'failed' })),
+  ]);
+
+  if (outcome.type === 'done') {
+    const failedResult = outcome.results.find(
+      (result) => result.exitCode !== 0,
+    );
+    for (const run of runs) {
+      activeRuns.delete(run);
+    }
+    if (failedResult) {
+      return {
+        exitCode: failedResult.exitCode,
+        failedStep: failedResult.step,
+        results: outcome.results,
+      };
+    }
+    return { exitCode: 0, failedStep: null, results: outcome.results };
+  }
+
+  console.error(
+    `code-change-verification: ${outcome.result.step.commandText} failed with exit code ${outcome.result.exitCode}. Stopping remaining verification steps.`,
+  );
+  await stopRemainingRuns(runs, outcome.result.step.label);
+  const results = await allDone;
+  for (const run of runs) {
+    activeRuns.delete(run);
+  }
+  return {
+    exitCode: outcome.result.exitCode,
+    failedStep: outcome.result.step,
+    results,
+  };
+}
+
+export async function runVerification(options = {}) {
+  const defaultPlan = createDefaultPlan();
+  const repoRoot = options.repoRoot ?? getRepoRoot();
+  const sequentialSteps =
+    options.sequentialSteps ?? defaultPlan.sequentialSteps;
+  const parallelSteps = options.parallelSteps ?? defaultPlan.parallelSteps;
+  const activeRuns = new Set();
+  let interrupted = false;
+
+  const handleSignal = async (signal) => {
+    if (interrupted) {
+      return;
+    }
+    interrupted = true;
+    console.error(
+      `code-change-verification: received ${signal}. Stopping running steps.`,
+    );
+    await Promise.allSettled(
+      [...activeRuns].map((run) =>
+        terminateRun(run, process.platform === 'win32'),
+      ),
+    );
+    process.exit(128 + (SIGNAL_EXIT_CODES[signal] ?? 1));
+  };
+
+  process.once('SIGINT', handleSignal);
+  process.once('SIGTERM', handleSignal);
+
+  try {
+    // Keep install and build as barriers before validations that can run independently.
+    for (const step of sequentialSteps) {
+      const result = await runStep(step, repoRoot, activeRuns);
+      if (result.exitCode !== 0) {
+        console.error(
+          `code-change-verification: ${step.commandText} failed with exit code ${result.exitCode}.`,
+        );
+        return result.exitCode;
+      }
+    }
+
+    const parallelResult = await runParallelSteps(
+      parallelSteps,
+      repoRoot,
+      activeRuns,
+    );
+    if (parallelResult.exitCode !== 0) {
+      return parallelResult.exitCode;
+    }
+
+    console.log('code-change-verification: all commands passed.');
+    return 0;
+  } finally {
+    process.removeListener('SIGINT', handleSignal);
+    process.removeListener('SIGTERM', handleSignal);
+  }
+}
+
+function isDirectRun() {
+  return path.resolve(process.argv[1] || '') === scriptPath;
+}
+
+if (isDirectRun()) {
+  if (process.argv.includes('--help')) {
+    printUsage();
+    process.exit(0);
+  }
+
+  const exitCode = await runVerification();
+  process.exit(exitCode);
+}
diff --git a/.agents/skills/code-change-verification/scripts/run.ps1 b/.agents/skills/code-change-verification/scripts/run.ps1
index fd9460a48..178fff479 100644
--- a/.agents/skills/code-change-verification/scripts/run.ps1
+++ b/.agents/skills/code-change-verification/scripts/run.ps1
@@ -2,40 +2,5 @@ Set-StrictMode -Version Latest
 $ErrorActionPreference = "Stop"
 
 $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
-$repoRoot = $null
-
-try {
-    $repoRoot = (& git -C $scriptDir rev-parse --show-toplevel 2>$null)
-} catch {
-    $repoRoot = $null
-}
-
-if (-not $repoRoot) {
-    $repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..\..")
-}
-
-Set-Location $repoRoot
-
-function Invoke-PnpmStep {
-    param(
-        [Parameter(Mandatory = $true)][string[]]$Args
-    )
-
-    $commandText = "pnpm " + ($Args -join " ")
-    Write-Host "Running $commandText..."
-    & pnpm @Args
-
-    if ($LASTEXITCODE -ne 0) {
-        Write-Error "code-change-verification: $commandText failed with exit code $LASTEXITCODE."
-        exit $LASTEXITCODE
-    }
-}
-
-Invoke-PnpmStep -Args @("i")
-Invoke-PnpmStep -Args @("build")
-Invoke-PnpmStep -Args @("-r", "build-check")
-Invoke-PnpmStep -Args @("-r", "-F", "@openai/*", "dist:check")
-Invoke-PnpmStep -Args @("lint")
-Invoke-PnpmStep -Args @("test")
-
-Write-Host "code-change-verification: all commands passed."
+& node (Join-Path $scriptDir "run.mjs") @args
+exit $LASTEXITCODE
diff --git a/.agents/skills/code-change-verification/scripts/run.sh b/.agents/skills/code-change-verification/scripts/run.sh
index 5e06be947..8935387a5 100755
--- a/.agents/skills/code-change-verification/scripts/run.sh
+++ b/.agents/skills/code-change-verification/scripts/run.sh
@@ -2,29 +2,4 @@
 set -euo pipefail
 
 SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
-if command -v git >/dev/null 2>&1; then
-  REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null || true)"
-fi
-REPO_ROOT="${REPO_ROOT:-$(cd "${SCRIPT_DIR}/../../../.." && pwd)}"
-
-cd "${REPO_ROOT}"
-
-echo "Running pnpm i..."
-pnpm i
-
-echo "Running pnpm build..."
-pnpm build
-
-echo "Running pnpm -r build-check..."
-pnpm -r build-check
-
-echo "Running pnpm -r -F \"@openai/*\" dist:check..."
-pnpm -r -F "@openai/*" dist:check
-
-echo "Running pnpm lint..."
-pnpm lint
-
-echo "Running pnpm test..."
-pnpm test
-
-echo "code-change-verification: all commands passed."
+exec node "${SCRIPT_DIR}/run.mjs" "$@"
diff --git a/AGENTS.md b/AGENTS.md
index fcef784bf..3ae188b40 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -107,7 +107,7 @@ The OpenAI Agents JS repository is a pnpm-managed monorepo that provides:
     ```
 3.  Make changes and add/update unit tests in `packages/<pkg>/test` unless doing so is truly infeasible.
 4.  Run `pnpm -r build-check` early to catch TypeScript errors across packages, tests, and examples.
-5.  When `$code-change-verification` applies (see Mandatory Skill Usage), run it to execute the full verification stack in order before considering the work complete.
+5.  When `$code-change-verification` applies (see Mandatory Skill Usage), run it to execute the full verification stack with the skill-defined phase barriers before considering the work complete.
 6.  Commit using Conventional Commits.
 7.  Push and open a pull request.
 8.  When reporting code changes as complete (after substantial code work), invoke `$pr-draft-summary` as the final handoff step unless the task falls under the documented skip cases.
@@ -177,7 +177,7 @@ See [this README](integration-tests/README.md) for details.
 
 #### Mandatory Local Run Order
 
-When `$code-change-verification` applies (see Mandatory Skill Usage), run the full validation sequence locally via the `$code-change-verification` skill; do not skip any step or change the order.
+When `$code-change-verification` applies (see Mandatory Skill Usage), run the full validation sequence locally via the `$code-change-verification` skill; do not skip any step, and preserve the skill-defined barriers (`pnpm i`, `pnpm build`, then the remaining validation steps).
 
 Before opening a pull request, always run `$changeset-validation` to ensure all changed packages are covered by a changeset and the validation passes; if no packages were touched and a changeset is unnecessary, you can skip creating one.
 
PATCH

git apply --whitespace=nowarn /tmp/gold.patch
echo "Gold patch applied."
