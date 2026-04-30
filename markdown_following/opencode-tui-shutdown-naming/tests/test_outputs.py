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
# Gates (pass_to_pass, repo_tests) -- actual CI commands
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_repo_typecheck():
    """TypeScript typecheck passes via bun turbo typecheck (repo CI)."""
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    r = subprocess.run(
        ["bun", "turbo", "typecheck"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-1000:]}\n{r.stdout[-1000:]}"


# [repo_tests] pass_to_pass
def test_repo_unit_tests_relevant():
    """Repo unit tests for utilities pass (lightweight subset covering modified code)."""
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    r = subprocess.run(
        ["bun", "test", "test/util/timeout.test.ts", "test/util/iife.test.ts", "test/util/lazy.test.ts"],
        capture_output=True, text=True, timeout=120, cwd=str(REPO / "packages/opencode"),
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_prettier():
    """Prettier code formatting check passes on modified files (repo CI)."""
    install = subprocess.run(
        ["bun", "install"],
        capture_output=True, text=True, timeout=300, cwd=str(REPO),
    )
    assert install.returncode == 0, f"bun install failed: {install.stderr[-500:]}"
    r = subprocess.run(
        ["npx", "prettier", "--check",
         "packages/opencode/src/cli/cmd/tui/thread.ts",
         "packages/opencode/src/cli/cmd/tui/worker.ts",
         "AGENTS.md"],
        capture_output=True, text=True, timeout=60, cwd=str(REPO),
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}\n{r.stdout[-500:]}"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) -- syntax / compilation checks
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
# Fail-to-pass (pr_diff) -- core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_thread_imports_with_timeout():
    """thread.ts uses the withTimeout utility and wraps TUI invocation in try/finally."""
    r = _run_bun(r"""
    const src = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    // 1. Verify thread.ts transpiles correctly (compilation check)
    const transpiler = new Bun.Transpiler({ loader: "ts" });
    try { transpiler.transformSync(src); }
    catch (e) {
        console.log(JSON.stringify({ pass: false, reason: "Transpile error: " + e.message }));
        process.exit(1);
    }

    // 2. Import and run the withTimeout utility (behavioral verification)
    const { withTimeout } = await import("./packages/opencode/src/util/timeout.ts");
    const val = await withTimeout(Promise.resolve(42), 5000);
    if (val !== 42) {
        console.log(JSON.stringify({ pass: false, reason: "withTimeout returned wrong value" }));
        process.exit(1);
    }

    // 3. Verify thread.ts references the timeout utility
    if (!/withTimeout/.test(src)) {
        console.log(JSON.stringify({ pass: false, reason: "thread.ts does not reference withTimeout" }));
        process.exit(1);
    }

    // 4. Verify try/finally wraps the tui() invocation
    const tuiIdx = src.indexOf("tui(");
    if (tuiIdx === -1) {
        console.log(JSON.stringify({ pass: false, reason: "tui() call not found in thread.ts" }));
        process.exit(1);
    }

    let hasTryFinally = false;
    let searchPos = tuiIdx;
    while (searchPos > 0) {
        const ti = src.lastIndexOf("try", searchPos);
        if (ti === -1) break;
        const firstChar = src.slice(ti + 3, ti + 15).trimStart()[0];
        if (firstChar !== "{") { searchPos = ti - 1; continue; }

        const ob = src.indexOf("{", ti + 3);
        let d = 0, cb = ob;
        for (let i = ob; i < src.length; i++) {
            if (src[i] === "{") d++;
            if (src[i] === "}") { d--; if (!d) { cb = i; break; } }
        }
        if (tuiIdx > ob && tuiIdx < cb) {
            const after = src.slice(cb + 1, cb + 50).trimStart();
            if (/^finally\s*\{/.test(after)) { hasTryFinally = true; break; }
        }
        searchPos = ti - 1;
    }

    if (!hasTryFinally) {
        console.log(JSON.stringify({ pass: false, reason: "No try/finally block wrapping tui()" }));
        process.exit(1);
    }

    console.log(JSON.stringify({ pass: true }));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")


# [pr_diff] fail_to_pass
def test_thread_idempotent_stop():
    """thread.ts cleanup is idempotent: extracts and executes the actual cleanup function with mocks to verify it unregisters listeners, terminates worker once, and uses timeout."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    // --- Step 1: Find the async cleanup function (the one calling .terminate()) ---
    function findCleanup(src) {
        const patterns = [
            /(?:const|let|var)\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*(?::[^=]*?)?\s*=>\s*\{/g,
            /async\s+function\s+(\w+)\s*\([^)]*\)\s*\{/g,
        ];
        for (const re of patterns) {
            let m;
            while ((m = re.exec(src)) !== null) {
                const ob = src.indexOf("{", m.index + m[0].length - 1);
                let d = 0, cb = ob;
                for (let i = ob; i < src.length; i++) {
                    if (src[i] === "{") d++;
                    if (src[i] === "}") { d--; if (!d) { cb = i; break; } }
                }
                const body = src.slice(ob + 1, cb);
                if (/\w+\.\s*terminate\s*\(\s*\)/.test(body)) {
                    return { name: m[1], body, pos: m.index };
                }
            }
        }
        return null;
    }

    const fn = findCleanup(content);
    if (!fn) {
        console.log(JSON.stringify({ pass: false, reason: "No async cleanup function with worker .terminate() found" }));
        process.exit(1);
    }

    // --- Step 2: Find the idempotency guard (let/var X = false before the function) ---
    const before = content.slice(Math.max(0, fn.pos - 500), fn.pos);
    const gm = before.match(/(?:let|var)\s+(\w+)\s*=\s*false\b/);
    if (!gm) {
        console.log(JSON.stringify({ pass: false, reason: "No idempotency guard (boolean = false) found before cleanup function" }));
        process.exit(1);
    }
    const guard = gm[1];

    // --- Step 3: Detect variable names referenced in the function body ---
    const body = fn.body;
    const wVar = (body.match(/(\w+)\.\s*terminate\s*\(/) || [])[1] || "worker";
    const cVar = (body.match(/(\w+)\.\s*call\s*\(\s*["']shutdown["']/) || [])[1] || "client";

    // Detect handler references from process.off / process.removeListener calls
    const handlers = new Set();
    for (const m of body.matchAll(/process\.(?:off|removeListener)\s*\(\s*["'][^"']+["']\s*,\s*(\w+)\s*\)/g)) {
        handlers.add(m[1]);
    }

    // --- Step 4: Transpile body to JS (strip any TS type annotations) ---
    const transpiler = new Bun.Transpiler({ loader: "ts" });
    let jsBody;
    try {
        const wrapped = "async function __w(){" + body + "}";
        const out = transpiler.transformSync(wrapped);
        jsBody = out.slice(out.indexOf("{") + 1, out.lastIndexOf("}"));
    } catch { jsBody = body; }

    // --- Step 5: Build mock environment and execute the function twice ---
    const state = { terminate: 0, off: [], shutdown: 0, timeout: false };

    const mocks = {};
    mocks[wVar] = { terminate() { state.terminate++; } };
    mocks[cVar] = { call: async (method) => { if (method === "shutdown") state.shutdown++; } };
    mocks["withTimeout"] = async (p) => { state.timeout = true; return p; };
    mocks["Log"] = { Default: { info(){}, warn(){}, error(){} } };
    mocks["process"] = {
        off(e) { state.off.push(e); },
        removeListener(e) { state.off.push(e); },
        removeAllListeners(e) { if (e) state.off.push(e); },
    };
    for (const h of handlers) { if (!(h in mocks)) mocks[h] = () => {}; }

    const pn = Object.keys(mocks);
    const pv = Object.values(mocks);

    const code = "let " + guard + " = false;\n" +
                 "const __fn = async () => {\n" + jsBody + "\n};\n" +
                 "await __fn();\nawait __fn();";

    const runner = new Function("state", ...pn, "return (async () => {" + code + "})()");
    await runner(state, ...pv);

    console.log(JSON.stringify({
        pass: true,
        terminate: state.terminate,
        off: state.off,
        shutdown: state.shutdown,
        timeout: state.timeout,
    }));
    """)
    assert r.returncode == 0, f"Bun script failed: {r.stderr}"
    data = _last_json(r.stdout)
    assert data["pass"], data.get("reason", "")
    assert data["terminate"] == 1, \
        f"Worker must be terminated exactly once when cleanup is called twice (got {data['terminate']})"
    assert data["shutdown"] <= 1, \
        f"Shutdown RPC must be called at most once (got {data['shutdown']})"
    assert len(data["off"]) >= 2, \
        f"Must unregister at least 2 process event listeners via process.off (got {len(data['off'])})"
    assert data["timeout"], "Must use withTimeout for timeout-bounded shutdown"


# [pr_diff] fail_to_pass
def test_thread_helpers_extracted():
    """thread.ts extracts worker path resolution and input handling into standalone top-level helpers."""
    r = _run_bun(r"""
    const content = await Bun.file("./packages/opencode/src/cli/cmd/tui/thread.ts").text();

    function extractAsyncFunctions(src) {
      const functions = [];
      const declRegex = /async function\s+(\w+)\s*\(/g;
      let match;
      while ((match = declRegex.exec(src)) !== null) {
        const name = match[1];
        const startIdx = match.index;
        const braceIdx = src.indexOf("{", startIdx);
        let depth = 0, endIdx = braceIdx;
        for (let i = braceIdx; i < src.length; i++) {
          if (src[i] === "{") depth++;
          if (src[i] === "}") { depth--; if (depth === 0) { endIdx = i; break; } }
        }
        functions.push({name, body: src.slice(braceIdx + 1, endIdx), full: src.slice(startIdx, endIdx + 1)});
      }
      const arrowRegex = /(?:const|let|var)\s+(\w+)\s*=\s*async\s*\([^)]*\)\s*=>\s*\{/g;
      while ((match = arrowRegex.exec(src)) !== null) {
        const name = match[1];
        const startIdx = match.index;
        const braceIdx = src.indexOf("{", startIdx);
        let depth = 0, endIdx = braceIdx;
        for (let i = braceIdx; i < src.length; i++) {
          if (src[i] === "{") depth++;
          if (src[i] === "}") { depth--; if (depth === 0) { endIdx = i; break; } }
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

    // Find helpers by content (not by name)
    let pathHelper = null;
    let inputHelper = null;
    for (const f of funcs) {
      if (f.body.includes("OPENCODE_WORKER_PATH") && f.body.includes("import.meta.url")) {
        pathHelper = f;
      }
      if (f.body.includes("Bun.stdin") || f.body.includes("process.stdin") ||
          (f.body.includes("stdin") && f.body.includes("isTTY"))) {
        inputHelper = f;
      }
    }

    if (!pathHelper) {
      console.log(JSON.stringify({pass: false, reason: "no path resolution helper found (must use OPENCODE_WORKER_PATH and import.meta.url)"}));
      process.exit(1);
    }
    if (!inputHelper) {
      console.log(JSON.stringify({pass: false, reason: "no input handling helper found (must read from stdin)"}));
      process.exit(1);
    }

    // Execute path helper with mocks via new Function (replace non-Function-safe refs)
    const transpiler = new Bun.Transpiler({loader: 'ts'});
    const mockMetaUrl = "file:///workspace/opencode/packages/opencode/src/cli/cmd/tui/thread.ts";

    let pathJs = transpiler.transformSync(pathHelper.full);
    pathJs = pathJs.replace(/import\.meta\.url/g, JSON.stringify(mockMetaUrl));

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

    // Execute input helper with mocks (replace Bun.stdin and process.stdin.isTTY via text substitution)
    let inputJs = transpiler.transformSync(inputHelper.full);
    inputJs = inputJs.replace(/import\.meta\.url/g, JSON.stringify(mockMetaUrl));
    inputJs = inputJs.replace(/process\.stdin\.isTTY/g, 'false');
    inputJs = inputJs.replace(/Bun\.stdin/g, '__mockBunStdin');

    const inputFactory = new Function("__mockBunStdin",
        "return (async () => {" + inputJs + "; return " + inputHelper.name + "})()");
    const inputFn = await inputFactory({ text: async () => "piped input" });
    const inputResult1 = await inputFn();
    const inputResult2 = await inputFn("arg");

    console.log(JSON.stringify({
      pass: true,
      pathResult: typeof pathResult === 'string' ? pathResult : String(pathResult),
      inputResult1,
      inputResult2,
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
        if (content[i] === "}") { depth--; if (depth === 0) { endIdx = i; break; } }
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

    globalThis.Log = { Default: { info: () => {}, warn: () => {}, error: () => {} } };

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
# Config-derived (agent_config / pr_diff) -- AGENTS.md naming convention
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass
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
    assert "single word names" in content, \
        "Must specify single-word naming preference"
    for name in ["pid", "cfg", "err", "opts", "dir", "root"]:
        assert name in content, \
            f"Must list '{name}' as a preferred short name"
    assert "workerPath" in content, \
        "Must list 'workerPath' as an example to avoid"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_unit_run_unit_tests():
    """pass_to_pass | CI job 'unit' → step 'Run unit tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun turbo test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run unit tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_e2e_run_app_e2e_tests():
    """pass_to_pass | CI job 'e2e' → step 'Run app e2e tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun --cwd packages/app test:e2e:local'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run app e2e tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_cli_build():
    """pass_to_pass | CI job 'build-cli' → step 'Build'"""
    r = subprocess.run(
        ["bash", "-lc", './packages/opencode/script/build.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_verify_certificate():
    """pass_to_pass | CI job 'build-tauri' → step 'Verify Certificate'"""
    r = subprocess.run(
        ["bash", "-lc", 'CERT_INFO=$(security find-identity -v -p codesigning build.keychain | grep "Developer ID Application")\nCERT_ID=$(echo "$CERT_INFO" | awk -F\'"\' \'{print $2}\')\necho "CERT_ID=$CERT_ID" >> $GITHUB_ENV\necho "Certificate imported."'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Verify Certificate' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_prepare():
    """pass_to_pass | CI job 'build-tauri' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun ./scripts/prepare.ts'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_tauri_show_tauri_cli_version():
    """pass_to_pass | CI job 'build-tauri' → step 'Show tauri-cli version'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo tauri --version'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Show tauri-cli version' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_typecheck_run_typecheck():
    """pass_to_pass | CI job 'typecheck' → step 'Run typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'bun typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")