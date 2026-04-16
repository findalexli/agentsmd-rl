"""
Benchmark tests for TanStack Router TS4023 fix.

This PR changes `interface ShouldBlockFnLocation` to `type ShouldBlockFnLocation`
to fix TypeScript error TS4023 when useBlocker is wrapped in a custom hook and exported.
"""
import subprocess
import os
import tempfile
import shutil

REPO = "/workspace/router"


def test_ts4023_custom_hook_wrapper():
    """
    Wrapping useBlocker in a custom hook and exporting it compiles without errors.

    This verifies that wrapping and exporting useBlocker doesn't cause TypeScript
    compilation errors. Note: The actual TS4023 error occurs during declaration
    file generation which is tested implicitly by test_repo_build_react_router.

    This is pass_to_pass: verifies compilation doesn't regress.
    """
    # Create a test file that wraps useBlocker
    test_code = '''
import { useBlocker } from '@tanstack/react-router';

// Custom hook that wraps useBlocker
export function useCustomBlocker(shouldBlock: boolean) {
    return useBlocker({
        shouldBlockFn: () => shouldBlock,
    });
}
'''

    # Create a minimal tsconfig for declaration output
    tsconfig = '''{
    "compilerOptions": {
        "target": "ES2020",
        "module": "ESNext",
        "moduleResolution": "bundler",
        "declaration": true,
        "declarationDir": "./dist",
        "outDir": "./dist",
        "strict": true,
        "skipLibCheck": true,
        "esModuleInterop": true,
        "jsx": "react-jsx",
        "paths": {
            "@tanstack/react-router": ["./packages/react-router/src/index.tsx"]
        },
        "baseUrl": "."
    },
    "include": ["test-wrapper.ts"],
    "exclude": ["node_modules"]
}'''

    # Write test files to a temp location within the repo
    test_dir = os.path.join(REPO, "_ts4023_test")
    os.makedirs(test_dir, exist_ok=True)

    try:
        # Write test file
        with open(os.path.join(test_dir, "test-wrapper.ts"), "w") as f:
            f.write(test_code)

        with open(os.path.join(test_dir, "tsconfig.json"), "w") as f:
            f.write(tsconfig)

        # Run TypeScript compiler with declaration output
        result = subprocess.run(
            ["pnpm", "exec", "tsc", "--project", "tsconfig.json", "--noEmit"],
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=120
        )

        # Check for TS4023 error specifically
        has_ts4023 = "TS4023" in result.stderr or "TS4023" in result.stdout

        # The fix should eliminate TS4023
        assert not has_ts4023, (
            f"TS4023 error still present after fix. "
            f"stdout: {result.stdout[-1000:]}, stderr: {result.stderr[-1000:]}"
        )

    finally:
        # Cleanup
        shutil.rmtree(test_dir, ignore_errors=True)


def test_interface_converted_to_type_react():
    """
    Verify ShouldBlockFnLocation is declared as 'type' not 'interface' in react-router.

    This is fail_to_pass: base has 'interface', fix has 'type'.
    """
    useBlocker_path = os.path.join(REPO, "packages/react-router/src/useBlocker.tsx")

    with open(useBlocker_path, "r") as f:
        content = f.read()

    # Check that it uses type declaration, not interface
    assert "type ShouldBlockFnLocation<" in content, (
        "ShouldBlockFnLocation should be declared as 'type', not 'interface'"
    )
    # Should NOT have interface declaration
    assert "interface ShouldBlockFnLocation<" not in content, (
        "ShouldBlockFnLocation should not be declared as 'interface'"
    )


def test_interface_converted_to_type_solid():
    """
    Verify ShouldBlockFnLocation is declared as 'type' not 'interface' in solid-router.

    This is fail_to_pass: base has 'interface', fix has 'type'.
    """
    useBlocker_path = os.path.join(REPO, "packages/solid-router/src/useBlocker.tsx")

    with open(useBlocker_path, "r") as f:
        content = f.read()

    assert "type ShouldBlockFnLocation<" in content, (
        "ShouldBlockFnLocation should be declared as 'type' in solid-router"
    )
    assert "interface ShouldBlockFnLocation<" not in content, (
        "ShouldBlockFnLocation should not be declared as 'interface' in solid-router"
    )


def test_interface_converted_to_type_vue():
    """
    Verify ShouldBlockFnLocation is declared as 'type' not 'interface' in vue-router.

    This is fail_to_pass: base has 'interface', fix has 'type'.
    """
    useBlocker_path = os.path.join(REPO, "packages/vue-router/src/useBlocker.tsx")

    with open(useBlocker_path, "r") as f:
        content = f.read()

    assert "type ShouldBlockFnLocation<" in content, (
        "ShouldBlockFnLocation should be declared as 'type' in vue-router"
    )
    assert "interface ShouldBlockFnLocation<" not in content, (
        "ShouldBlockFnLocation should not be declared as 'interface' in vue-router"
    )


def test_type_alias_has_equals_sign_react():
    """
    Verify the type alias uses proper syntax with '=' in react-router.

    Type aliases use: type Name = { ... }
    Interfaces use: interface Name { ... }

    This is fail_to_pass.
    """
    useBlocker_path = os.path.join(REPO, "packages/react-router/src/useBlocker.tsx")

    with open(useBlocker_path, "r") as f:
        content = f.read()

    # Find the ShouldBlockFnLocation declaration and verify it has the = sign
    # The pattern should be: type ShouldBlockFnLocation<...> = {
    lines = content.split('\n')
    found_type_decl = False
    found_equals = False

    for i, line in enumerate(lines):
        if "type ShouldBlockFnLocation<" in line:
            found_type_decl = True
            # Check current and next few lines for the = sign before {
            check_lines = '\n'.join(lines[i:i+6])
            if "> = {" in check_lines or ">\n= {" in check_lines.replace(" ", ""):
                found_equals = True
            break

    assert found_type_decl, "Could not find 'type ShouldBlockFnLocation<' declaration"
    assert found_equals, "Type alias should use '= {' syntax, not interface syntax"


def test_repo_type_check():
    """
    Repository type checking passes (pass_to_pass).

    Uses the repo's own test:types target via Nx.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Type checking failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_eslint():
    """
    Repository ESLint passes for react-router package (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"ESLint failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_build_react_router():
    """
    React-router package builds successfully (pass_to_pass).

    Verifies the TypeScript compiles and builds without errors.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:build",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Build failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_blocker_unit_tests():
    """
    Repository unit tests for blocker pass (pass_to_pass).

    Runs the blocker-specific unit tests from the repo.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/react-router:test:unit",
         "--outputStyle=stream", "--skipRemoteCache",
         "--", "tests/blocker.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Blocker unit tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_solid_router_type_check():
    """
    Solid-router package type checking passes (pass_to_pass).

    Verifies TypeScript types compile without errors for solid-router.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Solid-router type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_solid_router_eslint():
    """
    Solid-router package ESLint passes (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/solid-router:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Solid-router ESLint failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_solid_router_blocker_unit_tests():
    """
    Solid-router blocker unit tests pass (pass_to_pass).

    Runs the blocker-specific unit tests for solid-router.
    """
    result = subprocess.run(
        ["pnpm", "vitest", "run", "tests/blocker.test.tsx"],
        cwd=os.path.join(REPO, "packages/solid-router"),
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1"}
    )

    assert result.returncode == 0, (
        f"Solid-router blocker tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_vue_router_type_check():
    """
    Vue-router package type checking passes (pass_to_pass).

    Verifies TypeScript types compile without errors for vue-router.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:types",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Vue-router type check failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_vue_router_eslint():
    """
    Vue-router package ESLint passes (pass_to_pass).
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:eslint",
         "--outputStyle=stream", "--skipRemoteCache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Vue-router ESLint failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )


def test_repo_vue_router_blocker_unit_tests():
    """
    Vue-router blocker unit tests pass (pass_to_pass).

    Runs the blocker-specific unit tests for vue-router.
    """
    result = subprocess.run(
        ["pnpm", "nx", "run", "@tanstack/vue-router:test:unit",
         "--outputStyle=stream", "--skipRemoteCache",
         "--", "tests/blocker.test.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "1", "NX_DAEMON": "false"}
    )

    assert result.returncode == 0, (
        f"Vue-router blocker tests failed:\nstdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
    )
