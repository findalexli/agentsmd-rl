"""Behavioral and regression tests for docker/compose#13674.

The fix is in pkg/compose/publish.go: when the user declines the bind-mount
or sensitive-data confirmation prompt during `compose publish`, the function
must return `api.ErrCanceled` instead of `nil`, so callers can distinguish
"user cancelled" from "succeeded".

Tests inject a Go test file into the package under test (the agent does NOT
see this file at solve time — `tests/` is mounted read-only at evaluation),
then run `go test`. The injected tests call publish() directly with mocks
for the prompt and event bus.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path("/workspace/compose")
PKG_DIR = REPO / "pkg" / "compose"
INJECTED_TEST = PKG_DIR / "harbor_f2p_test.go"

INJECTED_GO_SRC = r'''/*
   Copyright 2020 Docker Compose CLI authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
*/

package compose

import (
	"errors"
	"os"
	"testing"

	"github.com/compose-spec/compose-go/v2/types"
	"gotest.tools/v3/assert"

	"github.com/docker/compose/v5/pkg/api"
)

func Test_HarborPublishBindMountDeclineReturnsErrCanceled(t *testing.T) {
	project := &types.Project{
		Services: types.Services{
			"web": {
				Name:  "web",
				Image: "nginx",
				Volumes: []types.ServiceVolumeConfig{
					{
						Type:   types.VolumeTypeBind,
						Source: "/host/path",
						Target: "/container/path",
					},
				},
			},
		},
	}

	declined := func(message string, defaultValue bool) (bool, error) {
		return false, nil
	}
	svc := &composeService{
		prompt: declined,
		events: &ignore{},
	}

	err := svc.publish(t.Context(), project, "docker.io/myorg/myapp:latest", api.PublishOptions{})
	assert.Assert(t, errors.Is(err, api.ErrCanceled),
		"expected api.ErrCanceled when user declines bind mount prompt, got: %v", err)
}

func Test_HarborPublishSensitiveDataDeclineReturnsErrCanceled(t *testing.T) {
	dir := t.TempDir()
	envPath := dir + "/secrets.env"
	secretData := `AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"`
	err := os.WriteFile(envPath, []byte(secretData), 0o600)
	assert.NilError(t, err)

	project := &types.Project{
		Services: types.Services{
			"web": {
				Name:  "web",
				Image: "nginx",
				EnvFiles: []types.EnvFile{
					{Path: envPath, Required: true},
				},
			},
		},
	}

	declined := func(message string, defaultValue bool) (bool, error) {
		return false, nil
	}
	svc := &composeService{
		prompt: declined,
		events: &ignore{},
	}

	err = svc.publish(t.Context(), project, "docker.io/myorg/myapp:latest", api.PublishOptions{WithEnvironment: true})
	assert.Assert(t, errors.Is(err, api.ErrCanceled),
		"expected api.ErrCanceled when user declines sensitive data prompt, got: %v", err)
}

func Test_HarborPublishAcceptDoesNotReturnErrCanceled(t *testing.T) {
	project := &types.Project{
		Services: types.Services{
			"web": {
				Name:  "web",
				Image: "nginx",
			},
		},
	}

	accepted := func(message string, defaultValue bool) (bool, error) {
		return true, nil
	}
	svc := &composeService{
		prompt: accepted,
		events: &ignore{},
		dryRun: true,
	}

	err := svc.publish(t.Context(), project, "docker.io/myorg/myapp:latest", api.PublishOptions{})
	assert.Assert(t, !errors.Is(err, api.ErrCanceled),
		"publish() must not return api.ErrCanceled when user accepts; got: %v", err)
}
'''


def _ensure_test_injected() -> None:
    """Drop the harbor f2p Go test into the compose package, idempotently."""
    current = INJECTED_TEST.read_text(encoding="utf-8") if INJECTED_TEST.exists() else ""
    if current != INJECTED_GO_SRC:
        INJECTED_TEST.write_text(INJECTED_GO_SRC, encoding="utf-8")


def _run_go_test(run_pattern: str, timeout: int = 300) -> subprocess.CompletedProcess:
    _ensure_test_injected()
    return subprocess.run(
        ["go", "test", "-count=1", "-run", run_pattern, "-v", "./pkg/compose/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def test_publish_bind_mount_decline_returns_err_canceled():
    """fail-to-pass: declining the bind-mount prompt must yield api.ErrCanceled."""
    r = _run_go_test("Test_HarborPublishBindMountDeclineReturnsErrCanceled")
    assert r.returncode == 0, (
        "publish() did not return api.ErrCanceled when user declined the "
        f"bind-mount confirmation prompt.\nSTDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )
    assert "--- PASS: Test_HarborPublishBindMountDeclineReturnsErrCanceled" in r.stdout, (
        f"expected explicit PASS line; got:\n{r.stdout[-2000:]}"
    )


def test_publish_sensitive_data_decline_returns_err_canceled():
    """fail-to-pass: declining the sensitive-data prompt must yield api.ErrCanceled."""
    r = _run_go_test("Test_HarborPublishSensitiveDataDeclineReturnsErrCanceled")
    assert r.returncode == 0, (
        "publish() did not return api.ErrCanceled when user declined the "
        f"sensitive-data confirmation prompt.\nSTDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )
    assert "--- PASS: Test_HarborPublishSensitiveDataDeclineReturnsErrCanceled" in r.stdout, (
        f"expected explicit PASS line; got:\n{r.stdout[-2000:]}"
    )


def test_publish_accept_does_not_return_err_canceled():
    """pass-to-pass control: accepting the prompt must NOT return ErrCanceled."""
    r = _run_go_test("Test_HarborPublishAcceptDoesNotReturnErrCanceled")
    assert r.returncode == 0, (
        "publish() returned api.ErrCanceled even when the user accepted "
        f"the prompt — the fix must be conditional on decline.\n"
        f"STDOUT:\n{r.stdout[-2000:]}\nSTDERR:\n{r.stderr[-1000:]}"
    )


def test_existing_create_layers_test_still_passes():
    """pass-to-pass: pre-existing Test_createLayers must still pass."""
    r = subprocess.run(
        ["go", "test", "-count=1", "-run", "Test_createLayers", "-v", "./pkg/compose/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"existing Test_createLayers regressed:\nSTDOUT:\n{r.stdout[-2000:]}\n"
        f"STDERR:\n{r.stderr[-1000:]}"
    )


def test_compose_package_compiles():
    """pass-to-pass: pkg/compose must compile."""
    r = subprocess.run(
        ["go", "build", "./pkg/compose/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"pkg/compose failed to build:\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_repo_go_vet_passes():
    """pass-to-pass: `go vet` on pkg/compose must pass.

    Maps to CLAUDE.md's 'After modifying any Go code, ALWAYS run the
    linter and fix all reported issues' — go vet is a strict subset of
    golangci-lint's govet linter, so passing it is necessary.
    """
    r = subprocess.run(
        ["go", "vet", "./pkg/compose/..."],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert r.returncode == 0, (
        f"`go vet ./pkg/compose/...` failed:\nSTDERR:\n{r.stderr[-2000:]}"
    )


def test_publish_go_imports_api_package():
    """The api package must remain imported in publish.go.

    The fix references api.ErrCanceled. Without the api import, the file
    cannot compile (caught above) — and downstream callers of errors.Is
    rely on the same sentinel package.
    """
    src = (REPO / "pkg" / "compose" / "publish.go").read_text(encoding="utf-8")
    assert "github.com/docker/compose/v5/pkg/api" in src, (
        "publish.go must continue to import the api package "
        "(provider of api.ErrCanceled)."
    )
