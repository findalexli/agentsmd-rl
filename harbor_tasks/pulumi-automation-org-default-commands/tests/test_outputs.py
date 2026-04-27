"""Tests for Pulumi Automation API `org` commands (PR #22436).

These tests verify that the Go `Workspace`/`LocalWorkspace` and Python
`Workspace`/`LocalWorkspace` types expose `OrgGetDefault`/`OrgSetDefault` (Go)
and `org_get_default`/`org_set_default` (Python), and that those methods
shell out to the Pulumi CLI with the right arguments and correctly process
the result.
"""

import os
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

REPO = Path("/workspace/pulumi")
GO_SDK = REPO / "sdk" / "go"
GO_AUTO = GO_SDK / "auto"
PY_LIB = REPO / "sdk" / "python" / "lib"


# ----------------------------------------------------------------------------
# Python f2p tests (mock-based — no Pulumi CLI required).
# ----------------------------------------------------------------------------

def _import_py_modules():
    if str(PY_LIB) not in sys.path:
        sys.path.insert(0, str(PY_LIB))
    from pulumi.automation._workspace import Workspace
    from pulumi.automation._local_workspace import LocalWorkspace
    from pulumi.automation._cmd import CommandResult
    return Workspace, LocalWorkspace, CommandResult


def test_python_workspace_has_abstract_org_get_default():
    """The Workspace abstract base class must declare `org_get_default`."""
    Workspace, _, _ = _import_py_modules()
    assert hasattr(Workspace, "org_get_default"), (
        "Workspace must expose org_get_default"
    )
    method = Workspace.org_get_default
    assert getattr(method, "__isabstractmethod__", False), (
        "Workspace.org_get_default must be marked with @abstractmethod"
    )


def test_python_workspace_has_abstract_org_set_default():
    """The Workspace abstract base class must declare `org_set_default`."""
    Workspace, _, _ = _import_py_modules()
    assert hasattr(Workspace, "org_set_default"), (
        "Workspace must expose org_set_default"
    )
    method = Workspace.org_set_default
    assert getattr(method, "__isabstractmethod__", False), (
        "Workspace.org_set_default must be marked with @abstractmethod"
    )


def test_python_local_workspace_org_get_default_calls_cli_and_strips():
    """LocalWorkspace.org_get_default invokes `pulumi org get-default` and
    returns the stripped stdout."""
    _, LocalWorkspace, CommandResult = _import_py_modules()

    captured = []

    def fake_run(self, args, on_output=None, on_error=None):
        captured.append(list(args))
        return CommandResult(stdout="  my-default-org \n", stderr="", code=0)

    ws = LocalWorkspace.__new__(LocalWorkspace)
    # Bind the fake to the instance.
    import types
    ws._run_pulumi_cmd_sync = types.MethodType(fake_run, ws)

    result = ws.org_get_default()
    assert result == "my-default-org", f"expected stripped 'my-default-org', got {result!r}"
    assert captured[-1] == ["org", "get-default"], (
        f"expected CLI args ['org', 'get-default'], got {captured[-1]!r}"
    )


def test_python_local_workspace_org_set_default_passes_arg():
    """LocalWorkspace.org_set_default invokes `pulumi org set-default <org>`."""
    _, LocalWorkspace, CommandResult = _import_py_modules()

    captured = []

    def fake_run(self, args, on_output=None, on_error=None):
        captured.append(list(args))
        return CommandResult(stdout="", stderr="", code=0)

    ws = LocalWorkspace.__new__(LocalWorkspace)
    import types
    ws._run_pulumi_cmd_sync = types.MethodType(fake_run, ws)

    rv = ws.org_set_default("my-special-org")
    # Per spec the method returns None.
    assert rv is None, f"expected None, got {rv!r}"
    assert captured[-1] == ["org", "set-default", "my-special-org"], (
        f"expected ['org', 'set-default', 'my-special-org'], got {captured[-1]!r}"
    )


def test_python_local_workspace_org_set_default_varied_names():
    """Vary the org name to ensure it's not hardcoded."""
    _, LocalWorkspace, CommandResult = _import_py_modules()

    captured = []

    def fake_run(self, args, on_output=None, on_error=None):
        captured.append(list(args))
        return CommandResult(stdout="", stderr="", code=0)

    import types
    for name in ["foo", "bar-baz", "with_underscore", "ACME-Corp"]:
        ws = LocalWorkspace.__new__(LocalWorkspace)
        ws._run_pulumi_cmd_sync = types.MethodType(fake_run, ws)
        ws.org_set_default(name)
        assert captured[-1] == ["org", "set-default", name], (
            f"for name={name!r}, expected last 3 args to be set-default name, got {captured[-1]!r}"
        )


# ----------------------------------------------------------------------------
# Go f2p tests — copy a behavioral test file into sdk/go/auto/ then run go test.
# ----------------------------------------------------------------------------

GO_BEHAVIOR_TEST = r'''//go:build !windows

package auto

import (
	"context"
	"testing"

	"github.com/blang/semver"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestOrgGetDefaultBehavior_HarbenchScaffold(t *testing.T) {
	t.Parallel()
	ctx := context.Background()
	m := &mockPulumiCommand{
		version: semver.MustParse("3.0.0"),
		stdout:  "  my-default-org-name  \n",
	}
	ws, err := NewLocalWorkspace(ctx, Pulumi(m))
	require.NoError(t, err)

	result, err := ws.OrgGetDefault(ctx)
	require.NoError(t, err)
	assert.Equal(t, "my-default-org-name", result)
	assert.Equal(t, []string{"org", "get-default"}, m.capturedArgs)
}

func TestOrgSetDefaultBehavior_HarbenchScaffold(t *testing.T) {
	t.Parallel()
	for _, name := range []string{"foo", "bar-baz", "ACME-Corp"} {
		name := name
		t.Run(name, func(t *testing.T) {
			t.Parallel()
			ctx := context.Background()
			m := &mockPulumiCommand{
				version: semver.MustParse("3.0.0"),
			}
			ws, err := NewLocalWorkspace(ctx, Pulumi(m))
			require.NoError(t, err)

			err = ws.OrgSetDefault(ctx, name)
			require.NoError(t, err)
			assert.Equal(t, []string{"org", "set-default", name}, m.capturedArgs)
		})
	}
}
'''


def _write_go_behavior_test():
    target = GO_AUTO / "harbench_org_default_test.go"
    target.write_text(GO_BEHAVIOR_TEST)
    return target


def test_go_org_get_set_default_behavior():
    """Build & run a behavioral Go test that verifies OrgGetDefault and
    OrgSetDefault on the Workspace interface invoke the Pulumi CLI with
    the right args and (for OrgGetDefault) strip the stdout."""
    _write_go_behavior_test()
    env = os.environ.copy()
    env.setdefault("HOME", "/root")
    r = subprocess.run(
        [
            "go", "test",
            "-count=1",
            "-run", "TestOrgGetDefaultBehavior_HarbenchScaffold|TestOrgSetDefaultBehavior_HarbenchScaffold",
            "./auto/",
        ],
        cwd=str(GO_SDK),
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    assert r.returncode == 0, (
        f"Go behavior test failed.\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


def test_go_workspace_interface_compiles_with_new_methods():
    """Compile a small consumer that uses Workspace.OrgGetDefault and
    Workspace.OrgSetDefault — fails on the base commit because those methods
    aren't on the interface yet."""
    consumer_dir = REPO / "_harbench_iface_check"
    if consumer_dir.exists():
        shutil.rmtree(consumer_dir)
    consumer_dir.mkdir()

    # Use go workspace (go.work) or just a small file under sdk/go itself
    # since sdk/go is its own module. Drop the file inside sdk/go/auto where
    # we can refer to types directly.
    target = GO_AUTO / "harbench_iface_compile_test.go"
    target.write_text(textwrap.dedent('''\
        //go:build !windows

        package auto

        import (
        	"context"
        	"testing"
        )

        // _harbenchOrgIfaceUsage statically checks that the Workspace interface
        // has OrgGetDefault and OrgSetDefault. The function is unused at
        // runtime; if either method is missing from the interface this file
        // fails to compile.
        func _harbenchOrgIfaceUsage(w Workspace, ctx context.Context) (string, error) {
        	if err := w.OrgSetDefault(ctx, "x"); err != nil {
        		return "", err
        	}
        	return w.OrgGetDefault(ctx)
        }

        func TestHarbenchOrgIfaceCompile(t *testing.T) {
        	// nothing to do at runtime — the value of this test is that it forces
        	// compilation of _harbenchOrgIfaceUsage.
        	_ = _harbenchOrgIfaceUsage
        }
    '''))

    env = os.environ.copy()
    env.setdefault("HOME", "/root")
    r = subprocess.run(
        ["go", "vet", "./auto/"],
        cwd=str(GO_SDK),
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    assert r.returncode == 0, (
        f"go vet failed.\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


# ----------------------------------------------------------------------------
# pass_to_pass — repo-native checks that hold both before and after the fix.
# ----------------------------------------------------------------------------

def test_p2p_go_sdk_builds():
    """Repo's `go build ./...` for sdk/go succeeds (pass_to_pass)."""
    env = os.environ.copy()
    env.setdefault("HOME", "/root")
    r = subprocess.run(
        ["go", "build", "./..."],
        cwd=str(GO_SDK),
        capture_output=True,
        text=True,
        timeout=600,
        env=env,
    )
    assert r.returncode == 0, (
        f"sdk/go build failed.\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


def test_p2p_python_imports_pulumi_automation():
    """The pulumi.automation module imports cleanly (pass_to_pass)."""
    if str(PY_LIB) not in sys.path:
        sys.path.insert(0, str(PY_LIB))
    import importlib
    mod = importlib.import_module("pulumi.automation")
    assert hasattr(mod, "LocalWorkspace")
    assert hasattr(mod, "Workspace")
