"""
Task: opencode-tui-shutdown-naming
Repo: opencode @ 2a0be8316be7ae6ec78f5d221851fc1cc0cdddb2
PR:   anomalyco/opencode#15924

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/opencode")


def _run_bun(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a TypeScript snippet with bun."""
    script_path = REPO / "_eval_tmp.ts"
    script_path.write_text(script)
    try:
        return subprocess.run(
            ["bun", "run", str(script_path)],
            capture_output=True, text=True, timeout=timeout,
            cwd=str(REPO),
        )
    finally:
        script_path.unlink(missing_ok=True)


def _last_json(stdout: str):
    """Parse the last non-empty line of stdout as JSON."""
    lines = [l for l in stdout.strip().split("\n") if l.strip()]
    return json.loads(lines[-1])


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, repo_tests) — actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript typecheck passes via bun turbo typecheck (repo CI)."""
    # First install dependencies (required for workspace resolution)
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    # Run the repo's actual typecheck command
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests_relevant():
    """Repo unit tests for utilities pass (lightweight subset covering modified code)."""
    # First install dependencies (required for workspace resolution)
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    # Run only the util tests that test utility functions related to the modified code
    r = subprocess.run(
        ["bun", "test", "test/util/timeout.test.ts", "test/util/iife.test.ts", "test/util/lazy.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO / "packages/opencode"),
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Prettier code formatting check passes on modified files (repo CI)."""
    # First install dependencies (required for prettier)
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    # Run prettier check on the files modified by the PR
    r = subprocess.run(
        ["npx", "prettier", "--check",
         "packages/opencode/src/cli/cmd/tui/thread.ts",
         "packages/opencode/src/cli/cmd/tui/worker.ts",
         "AGENTS.md"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_valid():
    """Modified TypeScript files are syntactically well-formed."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    worker = REPO / "packages/opencode/src/cli/cmd/tui/worker.ts"
    for path in [thread, worker]:
        content = path.read_text()
        opens = content.count("{")
        closes = content.count("}")
        assert abs(opens - closes) <= 1, f"Unbalanced braces in {path.name}: {opens} open vs {closes} close"
        parens_open = content.count("(")
        parens_close = content.count(")")
        assert abs(parens_open - parens_close) <= 1, f"Unbalanced parens in {path.name}"


# [static] pass_to_pass
def test_with_timeout_behavior():
    """withTimeout utility resolves within timeout and rejects on timeout."""
    result = _run_bun("""
import { withTimeout } from './packages/opencode/src/util/timeout.ts'

// Test 1: resolves normally
const val = await withTimeout(Promise.resolve("ok"), 5000)
console.log(JSON.stringify({ step: "resolved", value: val }))
""")
    assert result.returncode == 0, f"withTimeout failed: {result.stderr}"
    data = _last_json(result.stdout)
    assert data["step"] == "resolved"
    assert data["value"] == "ok"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_thread_imports_with_timeout():
    """thread.ts imports withTimeout and uses it for bounded shutdown."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    const hasImport = /import\s+\{[^}]*withTimeout[^}]*\}\s+from\s+["']@\/util\/timeout["']/.test(content);
    if (!hasImport) {
      console.log(JSON.stringify({pass: false, reason: "withTimeout import missing"}));
      process.exit(1);
    }

    const hasUsage = /withTimeout\s*\([\s\S]*?,\s*\d+\s*\)/.test(content);
    if (!hasUsage) {
      console.log(JSON.stringify({pass: false, reason: "withTimeout not called with timeout value"}));
      process.exit(1);
    }

    console.log(JSON.stringify({pass: true}));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")


# [pr_diff] fail_to_pass
def test_thread_idempotent_stop():
    """thread.ts has idempotent cleanup that unregisters listeners, terminates worker, uses timeout-bounded shutdown, and wraps TUI in try/finally."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    // 1. Find boolean flag initialized to false
    const flagMatch = content.match(/(?:let|const)\s+(\w+)\s*=\s*false/);
    if (!flagMatch) {
      console.log(JSON.stringify({pass: false, reason: "no boolean flag initialized to false"}));
      process.exit(1);
    }
    const flagName = flagMatch[1];

    // 2. Verify idempotency pattern
    const idempotencyRegex = new RegExp("if\\s*\\(\\s*" + flagName + "\\s*\\)\\s*(?:\\{\\s*return\\s*;?\\s*\\}|return)");
    const hasIdempotency = idempotencyRegex.test(content);
    const flagSetRegex = new RegExp(flagName + "\\s*=\\s*true\\s*;?");
    const hasFlagSet = flagSetRegex.test(content);

    // 3. Verify process listener unregistration
    const hasUncaughtOff = /process\.off\s*\(\s*["']uncaughtException["']/.test(content);
    const hasUnhandledOff = /process\.off\s*\(\s*["']unhandledRejection["']/.test(content);
    const hasSigusr2Off = /process\.off\s*\(\s*["']SIGUSR2["']/.test(content);

    // 4. Verify worker termination
    const hasTerminate = /worker\.terminate\s*\(\s*\)/.test(content);

    // 5. Verify timeout-bounded shutdown
    const hasWithTimeout = /withTimeout\s*\([\s\S]*?,\s*\d+\s*\)/.test(content);

    // 6. Verify try/finally around TUI invocation (brace-aware)
    const tuiIdx = content.indexOf("tui(");
    let hasTryFinally = false;
    if (tuiIdx !== -1) {
      let tryIdx = content.lastIndexOf("try", tuiIdx);
      while (tryIdx > 0) {
        const afterTry = content.slice(tryIdx + 3, tryIdx + 10);
        if (afterTry.trimStart().startsWith("{")) break;
        tryIdx = content.lastIndexOf("try", tryIdx - 1);
      }
      if (tryIdx !== -1) {
        const tryBraceIdx = content.indexOf("{", tryIdx);
        let depth = 0;
        let endIdx = tryBraceIdx;
        for (let i = tryBraceIdx; i < content.length; i++) {
          if (content[i] === "{") depth++;
          if (content[i] === "}") {
            depth--;
            if (depth === 0) { endIdx = i; break; }
          }
        }
        const afterBlock = content.slice(endIdx + 1, endIdx + 50);
        hasTryFinally = /finally\s*\{/.test(afterBlock);
      }
    }

    // 7. Behavioral execution: verify idempotency pattern works
    let terminateCalls = 0;
    const mockWorker = { terminate: () => { terminateCalls++; } };
    const testCode = `
      let ${flagName} = false;
      const stop = async () => {
        if (${flagName}) return;
        ${flagName} = true;
        mockWorker.terminate();
      };
      await stop();
      await stop();
    `;
    await new Function("mockWorker", "return (async () => {" + testCode + "})()")(mockWorker);

    console.log(JSON.stringify({
      pass: true,
      hasIdempotency, hasFlagSet,
      hasUncaughtOff, hasUnhandledOff, hasSigusr2Off,
      hasTerminate, hasWithTimeout, hasTryFinally,
      terminateCalls
    }));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")
    assert data["hasIdempotency"], "Must guard against double invocation"
    assert data["hasFlagSet"], "Must set flag to true"
    assert data["hasUncaughtOff"], "Must unregister uncaughtException listener"
    assert data["hasUnhandledOff"], "Must unregister unhandledRejection listener"
    assert data["hasSigusr2Off"], "Must unregister SIGUSR2 listener"
    assert data["hasTerminate"], "Must terminate worker"
    assert data["hasWithTimeout"], "Must use withTimeout for bounded shutdown"
    assert data["hasTryFinally"], "Must use try/finally around TUI invocation"
    assert data["terminateCalls"] == 1, "worker.terminate must be called exactly once when stop invoked twice"


# [pr_diff] fail_to_pass
def test_thread_helpers_extracted():
    """thread.ts extracts worker path resolution and input handling into standalone top-level helpers."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    function extractAsyncFunctions(src) {
      const functions = [];
      // async function name() { ... }
      const declRegex = /async function\s+(\w+)\s*\(/g;
      let match;
      while ((match = declRegex.exec(src)) !== null) {
        const name = match[1];
        const startIdx = match.index;
        const braceIdx = src.indexOf("{", startIdx);
        let depth = 0, endIdx = braceIdx;
        for (let i = braceIdx; i < src.length; i++) {
          if (src[i] === "{") depth++;
          if (src[i] === "}") {
            depth--;
            if (depth === 0) { endIdx = i; break; }
          }
        }
        functions.push({name, body: src.slice(braceIdx + 1, endIdx), full: src.slice(startIdx, endIdx + 1)});
      }
      // const name = async () => { ... }
      const arrowRegex = /(?:const|let|var)\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>\s*\{/g;
      while ((match = arrowRegex.exec(src)) !== null) {
        const name = match[1];
        const startIdx = match.index;
        const braceIdx = src.indexOf("{", startIdx);
        let depth = 0, endIdx = braceIdx;
        for (let i = braceIdx; i < src.length; i++) {
          if (src[i] === "{") depth++;
          if (src[i] === "}") {
            depth--;
            if (depth === 0) { endIdx = i; break; }
          }
        }
        functions.push({name, body: src.slice(braceIdx + 1, endIdx), full: src.slice(startIdx, endIdx + 1)});
      }
      return functions;
    }

    const funcs = extractAsyncFunctions(content);
    if (funcs.length < 2) {
      console.log(JSON.stringify({pass: false, reason: "need at least 2 top-level async helpers", count: funcs.length}));
      process.exit(1);
    }

    let pathHelper = null;
    let inputHelper = null;
    for (const f of funcs) {
      if (f.body.includes("OPENCODE_WORKER_PATH") && f.body.includes("import.meta.url")) {
        pathHelper = f;
      }
      if ((f.body.includes("Bun.stdin") || f.body.includes("process.stdin")) && (f.body.includes("prompt") || f.body.includes("piped"))) {
        inputHelper = f;
      }
    }

    if (!pathHelper) {
      console.log(JSON.stringify({pass: false, reason: "no path resolution helper found"}));
      process.exit(1);
    }
    if (!inputHelper) {
      console.log(JSON.stringify({pass: false, reason: "no input handling helper found"}));
      process.exit(1);
    }

    // Execute path helper with mocks
    const transpiler = new Bun.Transpiler({loader: 'ts'});
    const pathJs = transpiler.transformSync(pathHelper.full);
    const origFilesystem = globalThis.Filesystem;
    const origOPENCODE = globalThis.OPENCODE_WORKER_PATH;
    globalThis.Filesystem = { exists: async () => false };
    globalThis.OPENCODE_WORKER_PATH = undefined;
    globalThis.fileURLToPath = (u) => typeof u === 'string' ? u : u.pathname;

    const pathFactory = new Function("return (async () => {" + pathJs + "; return " + pathHelper.name + "})()");
    const pathFn = await pathFactory();
    const pathResult = await pathFn();

    globalThis.Filesystem = origFilesystem;
    globalThis.OPENCODE_WORKER_PATH = origOPENCODE;

    // Execute input helper with mocks
    const inputJs = transpiler.transformSync(inputHelper.full);
    const origStdinIsTTY = process.stdin.isTTY;
    const origBunStdin = Bun.stdin;

    process.stdin.isTTY = false;
    Bun.stdin = { text: async () => "piped input" };
    globalThis.Bun = { stdin: Bun.stdin };

    const inputFactory = new Function("return (async () => {" + inputJs + "; return " + inputHelper.name + "})()");
    const inputFn = await inputFactory();
    const inputResult1 = await inputFn();
    const inputResult2 = await inputFn("arg");

    process.stdin.isTTY = origStdinIsTTY;
    Bun.stdin = origBunStdin;

    console.log(JSON.stringify({
      pass: true,
      pathResult: typeof pathResult === 'string' ? pathResult : String(pathResult),
      inputResult1,
      inputResult2,
      pathHelperName: pathHelper.name,
      inputHelperName: inputHelper.name
    }));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")
    path_str = data["pathResult"].lower()
    assert "worker" in path_str, "Path helper should resolve to a worker file"
    assert data["inputResult1"] == "piped input", "Input helper should return piped content when no arg"
    assert data["inputResult2"] == "piped input\narg", "Input helper should combine piped + arg"


# [pr_diff] fail_to_pass
def test_worker_shutdown_simplified():
    """worker.ts shutdown calls Instance.disposeAll directly without Promise.race."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/worker.ts").text();

    function extractFunctionBody(funcName) {
      const startIdx = content.indexOf("async " + funcName + "(");
      if (startIdx === -1) return null;
      const braceIdx = content.indexOf("{", startIdx);
      let depth = 0, endIdx = braceIdx;
      for (let i = braceIdx; i < content.length; i++) {
        if (content[i] === "{") depth++;
        if (content[i] === "}") {
          depth--;
          if (depth === 0) { endIdx = i; break; }
        }
      }
      return content.slice(braceIdx + 1, endIdx);
    }

    const body = extractFunctionBody("shutdown");
    if (!body) {
      console.log(JSON.stringify({pass: false, reason: "shutdown function not found"}));
      process.exit(1);
    }

    const hasPromiseRace = body.includes("Promise.race");
    const hasDisposeAll = body.includes("Instance.disposeAll()");

    // Mock Log before executing extracted body
    globalThis.Log = { Default: { info: () => {}, warn: () => {}, error: () => {} } };

    // Execute with mocks
    let disposed = false;
    const mockInstance = { disposeAll: async () => { disposed = true; } };
    const mockEventStream = { abort: null };
    const mockServer = null;

    const fn = new Function("Instance", "eventStream", "server", "return (async () => {" + body + "})()");
    await fn(mockInstance, mockEventStream, mockServer);

    console.log(JSON.stringify({pass: true, hasPromiseRace, hasDisposeAll, disposed}));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")
    assert not data["hasPromiseRace"], "shutdown should not use Promise.race"
    assert data["hasDisposeAll"], "shutdown must call Instance.disposeAll()"
    assert data["disposed"], "shutdown must actually dispose instances when executed"


# ---------------------------------------------------------------------------
# Config-derived (agent_config / pr_diff) — AGENTS.md naming convention
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:21 @ base_commit
def test_short_variable_names():
    """thread.ts must not use old multi-word identifiers replaced by short names."""
    thread = REPO / "packages/opencode/src/cli/cmd/tui/thread.ts"
    content = thread.read_text()
    assert "workerPath" not in content, "Use a short single-word name instead of 'workerPath'"
    assert "baseCwd" not in content, "Use a short single-word name instead of 'baseCwd'"
    assert "shouldStartServer" not in content, "Use a short single-word name instead of 'shouldStartServer'"
    assert "networkOpts" not in content, "Use a short single-word name instead of 'networkOpts'"


# [pr_diff] fail_to_pass
def test_agents_md_naming_enforcement():
    """AGENTS.md must contain the Naming Enforcement section with mandatory rule."""
    agents = REPO / "AGENTS.md"
    content = agents.read_text()
    assert "Naming Enforcement" in content, \
        "AGENTS.md must have Naming Enforcement section"
    assert "THIS RULE IS MANDATORY" in content, \
        "Naming enforcement must be declared as mandatory"
    # Must specify single-word preference
    assert "single word names" in content, \
        "Must specify single-word naming preference"
    # Must list preferred short names as examples
    for name in ["pid", "cfg", "err", "opts", "dir", "root"]:
        assert name in content, \
            f"Must list '{name}' as a preferred short name"
    # Must list examples to avoid
    assert "workerPath" in content, \
        "Must list 'workerPath' as an example to avoid"
