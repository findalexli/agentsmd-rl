// Copyright 2026, Pulumi Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Test for parallel SignalCancellation behavior. This file is injected
// into sdk/go/common/resource/plugin/ by the harness.

package plugin

import (
	"context"
	"errors"
	"io"
	"sync"
	"testing"
	"time"

	"github.com/hashicorp/hcl/v2"
	"github.com/pulumi/pulumi/sdk/v3/go/common/promise"
	"github.com/pulumi/pulumi/sdk/v3/go/common/testing/diagtest"
	"github.com/pulumi/pulumi/sdk/v3/go/common/tokens"
	"github.com/pulumi/pulumi/sdk/v3/go/common/workspace"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// signalCancelStubAnalyzer is a minimal Analyzer implementation for testing.
type signalCancelStubAnalyzer struct {
	cancelF func(ctx context.Context) error
}

var _ Analyzer = (*signalCancelStubAnalyzer)(nil)

func (a *signalCancelStubAnalyzer) Close() error                  { return nil }
func (a *signalCancelStubAnalyzer) Name() tokens.QName            { return "" }
func (a *signalCancelStubAnalyzer) GetPluginInfo() (PluginInfo, error) {
	return PluginInfo{}, nil
}
func (a *signalCancelStubAnalyzer) GetAnalyzerInfo() (AnalyzerInfo, error) {
	return AnalyzerInfo{}, nil
}
func (a *signalCancelStubAnalyzer) Analyze(AnalyzerResource) (AnalyzeResponse, error) {
	return AnalyzeResponse{}, nil
}
func (a *signalCancelStubAnalyzer) AnalyzeStack([]AnalyzerStackResource) (AnalyzeResponse, error) {
	return AnalyzeResponse{}, nil
}
func (a *signalCancelStubAnalyzer) Remediate(AnalyzerResource) (RemediateResponse, error) {
	return RemediateResponse{}, nil
}
func (a *signalCancelStubAnalyzer) Configure(map[string]AnalyzerPolicyConfig) error {
	return nil
}
func (a *signalCancelStubAnalyzer) Cancel(ctx context.Context) error {
	if a.cancelF != nil {
		return a.cancelF(ctx)
	}
	return nil
}

// signalCancelStubLanguage is a minimal LanguageRuntime implementation for testing.
type signalCancelStubLanguage struct {
	cancelF func() error
}

var _ LanguageRuntime = (*signalCancelStubLanguage)(nil)

func (l *signalCancelStubLanguage) Close() error { return nil }
func (l *signalCancelStubLanguage) GetRequiredPackages(ProgramInfo) ([]workspace.PackageDescriptor, error) {
	return nil, nil
}
func (l *signalCancelStubLanguage) Run(RunInfo) (string, bool, error) { return "", false, nil }
func (l *signalCancelStubLanguage) GetPluginInfo() (PluginInfo, error) {
	return PluginInfo{}, nil
}
func (l *signalCancelStubLanguage) InstallDependencies(InstallDependenciesRequest) (
	io.Reader, io.Reader, <-chan error, error,
) {
	return nil, nil, nil, nil
}
func (l *signalCancelStubLanguage) RuntimeOptionsPrompts(ProgramInfo) ([]RuntimeOptionPrompt, error) {
	return nil, nil
}
func (l *signalCancelStubLanguage) Template(ProgramInfo, tokens.PackageName) error { return nil }
func (l *signalCancelStubLanguage) About(ProgramInfo) (AboutInfo, error)           { return AboutInfo{}, nil }
func (l *signalCancelStubLanguage) GetProgramDependencies(ProgramInfo, bool) ([]DependencyInfo, error) {
	return nil, nil
}
func (l *signalCancelStubLanguage) RunPlugin(context.Context, RunPluginInfo) (
	io.Reader, io.Reader, *promise.Promise[int32], error,
) {
	return nil, nil, nil, nil
}
func (l *signalCancelStubLanguage) GenerateProject(
	string, string, string, bool, string, map[string]string,
) (hcl.Diagnostics, error) {
	return nil, nil
}
func (l *signalCancelStubLanguage) GeneratePackage(
	string, string, map[string][]byte, string, map[string]string, bool,
) (hcl.Diagnostics, error) {
	return nil, nil
}
func (l *signalCancelStubLanguage) GenerateProgram(
	map[string]string, string, bool,
) (map[string][]byte, hcl.Diagnostics, error) {
	return nil, nil, nil
}
func (l *signalCancelStubLanguage) Pack(string, string) (string, error) { return "", nil }
func (l *signalCancelStubLanguage) Link(
	ProgramInfo, []workspace.LinkablePackageDescriptor, string,
) (string, error) {
	return "", nil
}
func (l *signalCancelStubLanguage) Cancel() error {
	if l.cancelF != nil {
		return l.cancelF()
	}
	return nil
}

// TestSignalCancellation_ResourceAndAnalyzerConcurrent verifies that resource
// providers and analyzer plugins receive their cancellation signals
// concurrently within phase 1. A barrier of size 2 forces the two plugins to
// each block on the other entering its cancel callback. With sequential
// execution this deadlocks; with concurrent goroutines it completes.
func TestSignalCancellation_ResourceAndAnalyzerConcurrent(t *testing.T) {
	t.Parallel()

	sink := diagtest.LogSink(t)
	ctx, err := NewContext(t.Context(), sink, sink, nil, nil, "", nil, false, nil, nil)
	require.NoError(t, err)
	host, ok := ctx.Host.(*defaultHost)
	require.True(t, ok)

	var barrier sync.WaitGroup
	barrier.Add(2)
	enter := func() {
		barrier.Done()
		barrier.Wait()
	}

	prov := &MockProvider{
		SignalCancellationF: func(context.Context) error {
			enter()
			return nil
		},
	}
	ana := &signalCancelStubAnalyzer{
		cancelF: func(context.Context) error {
			enter()
			return nil
		},
	}

	host.resourcePlugins = map[Provider]*resourcePlugin{
		prov: {Plugin: prov, Name: "stub-resource"},
	}
	host.analyzerPlugins = map[tokens.QName]*analyzerPlugin{
		tokens.QName("stub-analyzer"): {Plugin: ana, Name: "stub-analyzer"},
	}
	host.languagePlugins = map[string]*languagePlugin{}

	done := make(chan error, 1)
	go func() { done <- host.SignalCancellation() }()

	select {
	case sigErr := <-done:
		assert.NoError(t, sigErr)
	case <-time.After(15 * time.Second):
		t.Fatal("SignalCancellation deadlocked: resource and analyzer plugins are not cancelled concurrently")
	}
}

// TestSignalCancellation_LanguageRuntimesConcurrent verifies that multiple
// language plugins receive their cancellation signals concurrently. A barrier
// of size 2 forces both Cancel callbacks to be active at the same time.
func TestSignalCancellation_LanguageRuntimesConcurrent(t *testing.T) {
	t.Parallel()

	sink := diagtest.LogSink(t)
	ctx, err := NewContext(t.Context(), sink, sink, nil, nil, "", nil, false, nil, nil)
	require.NoError(t, err)
	host, ok := ctx.Host.(*defaultHost)
	require.True(t, ok)

	var barrier sync.WaitGroup
	barrier.Add(2)
	enter := func() error {
		barrier.Done()
		barrier.Wait()
		return nil
	}

	lang1 := &signalCancelStubLanguage{cancelF: enter}
	lang2 := &signalCancelStubLanguage{cancelF: enter}

	host.resourcePlugins = map[Provider]*resourcePlugin{}
	host.analyzerPlugins = map[tokens.QName]*analyzerPlugin{}
	host.languagePlugins = map[string]*languagePlugin{
		"lang-a": {Plugin: lang1, Name: "lang-a"},
		"lang-b": {Plugin: lang2, Name: "lang-b"},
	}

	done := make(chan error, 1)
	go func() { done <- host.SignalCancellation() }()

	select {
	case sigErr := <-done:
		assert.NoError(t, sigErr)
	case <-time.After(15 * time.Second):
		t.Fatal("SignalCancellation deadlocked: language plugins are not cancelled concurrently")
	}
}

// TestSignalCancellation_DeadlineContext verifies that the cancellation
// context passed to resource and analyzer plugins carries a deadline so
// well-behaved plugins that respect it return promptly.
func TestSignalCancellation_DeadlineContext(t *testing.T) {
	t.Parallel()

	sink := diagtest.LogSink(t)
	ctx, err := NewContext(t.Context(), sink, sink, nil, nil, "", nil, false, nil, nil)
	require.NoError(t, err)
	host, ok := ctx.Host.(*defaultHost)
	require.True(t, ok)

	var sawDeadline bool
	var mu sync.Mutex

	prov := &MockProvider{
		SignalCancellationF: func(c context.Context) error {
			_, has := c.Deadline()
			mu.Lock()
			sawDeadline = has
			mu.Unlock()
			if !has {
				return errors.New("provider received cancellation context without a deadline")
			}
			return nil
		},
	}

	host.resourcePlugins = map[Provider]*resourcePlugin{
		prov: {Plugin: prov, Name: "stub-resource"},
	}
	host.analyzerPlugins = map[tokens.QName]*analyzerPlugin{}
	host.languagePlugins = map[string]*languagePlugin{}

	done := make(chan error, 1)
	go func() { done <- host.SignalCancellation() }()

	select {
	case sigErr := <-done:
		require.NoError(t, sigErr,
			"SignalCancellation must pass a context with a deadline to provider plugins")
	case <-time.After(35 * time.Second):
		t.Fatal("SignalCancellation did not return")
	}

	mu.Lock()
	defer mu.Unlock()
	assert.True(t, sawDeadline,
		"provider's SignalCancellation must be called with a deadline-bearing context")
}

