import subprocess
import tempfile
import os

REPO = "/workspace/openai-agents-js"
SRC = "/workspace/openai-agents-js/packages/agents-core/src/errors.ts"


def test_error_subclass_names():
    """All AgentsError subclasses report correct .name (fail_to_pass)."""
    test_script = f"""
import {{ MaxTurnsExceededError }} from '{SRC}';
import {{ ModelBehaviorError }} from '{SRC}';
import {{ UserError }} from '{SRC}';
import {{ InputGuardrailTripwireTriggered }} from '{SRC}';
import {{ OutputGuardrailTripwireTriggered }} from '{SRC}';
import {{ GuardrailExecutionError }} from '{SRC}';
import {{ ToolCallError }} from '{SRC}';

const checks = [
    [MaxTurnsExceededError, 'MaxTurnsExceededError', ['Test error', {{}}]],
    [ModelBehaviorError, 'ModelBehaviorError', ['Test error', {{}}]],
    [UserError, 'UserError', ['Test error', {{}}]],
    [InputGuardrailTripwireTriggered, 'InputGuardrailTripwireTriggered', ['Test error', {{}}, {{}}]],
    [OutputGuardrailTripwireTriggered, 'OutputGuardrailTripwireTriggered', ['Test error', {{}}, {{}}]],
    [GuardrailExecutionError, 'GuardrailExecutionError', ['Test error', new Error('cause'), {{}}]],
    [ToolCallError, 'ToolCallError', ['Test error', new Error('cause'), {{}}]],
];

let failed = false;
for (const [Cls, expectedName, args] of checks) {{
    const instance = new Cls(...args);
    if (instance.name !== expectedName) {{
        console.error('FAIL: ' + Cls.name + '.name is "' + instance.name + '", expected "' + expectedName + '"');
        failed = true;
    }}
}}
if (failed) process.exit(1);
console.log('OK');
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
        f.write(test_script)
        tmpfile = f.name

    try:
        r = subprocess.run(
            ["npx", "tsx", tmpfile],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"Error name test failed:\nSTDERR: {r.stderr}\nSTDOUT: {r.stdout}"
    finally:
        os.unlink(tmpfile)


def test_error_to_string_includes_subclass_name():
    """Error.toString() includes the specific subclass name (fail_to_pass)."""
    test_script = f"""
import {{ InvalidToolInputError }} from '{SRC}';

const err = new InvalidToolInputError('Invalid JSON input for tool', {{}}, undefined, undefined);
const str = err.toString();
if (!str.startsWith('InvalidToolInputError:')) {{
    console.error('FAIL: toString() is "' + str + '", expected it to start with "InvalidToolInputError:"');
    process.exit(1);
}}
console.log('OK');
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".ts", delete=False) as f:
        f.write(test_script)
        tmpfile = f.name

    try:
        r = subprocess.run(
            ["npx", "tsx", tmpfile],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=REPO,
        )
        assert r.returncode == 0, f"toString test failed:\nSTDERR: {r.stderr}\nSTDOUT: {r.stdout}"
    finally:
        os.unlink(tmpfile)


def test_agents_core_build():
    """The agents-core package builds successfully (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "-F", "agents-core", "build"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-500:]}"


def test_agents_core_build_check():
    """Type checking with test files passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "-F", "agents-core", "build-check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Type check failed:\n{r.stderr[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_build_all_packages():
    """pass_to_pass | CI job 'test' → step 'Build all packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build all packages' failed (returncode={r.returncode}):\n"
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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_should_set_error_names():
    """fail_to_pass | PR added test 'should set error names' in 'packages/agents-core/test/errors.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || npx vitest run "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || pnpm jest "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1 || npx jest "packages/agents-core/test/errors.test.ts" -t "should set error names" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'should set error names' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
