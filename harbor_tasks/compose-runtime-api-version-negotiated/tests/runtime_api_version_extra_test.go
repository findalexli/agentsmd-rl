/*
   Copyright 2026 Docker Compose CLI authors

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0
*/

package compose

import (
	"context"
	"testing"

	"github.com/moby/moby/client"
	"go.uber.org/mock/gomock"
	"gotest.tools/v3/assert"

	"github.com/docker/compose/v5/pkg/mocks"
)

// TestExtraRuntimeAPIVersionUsesNegotiation verifies that RuntimeAPIVersion
// triggers a negotiated Ping (NOT ServerVersion) and returns the negotiated
// ClientVersion (NOT the server's raw APIVersion).
func TestExtraRuntimeAPIVersionUsesNegotiation(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()

	apiClient := mocks.NewMockAPIClient(mockCtrl)
	cli := mocks.NewMockCli(mockCtrl)
	tested := &composeService{dockerCli: cli}

	cli.EXPECT().Client().Return(apiClient).AnyTimes()

	// Server reports 1.99 (raw max API), but client negotiated down to 1.43.
	// The method MUST return the negotiated value, not the server max.
	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.99"}, nil).Times(1)
	apiClient.EXPECT().ClientVersion().Return("1.43").Times(1)

	version, err := tested.RuntimeAPIVersion(context.Background())
	assert.NilError(t, err)
	assert.Equal(t, version, "1.43")
}

// TestExtraRuntimeAPIVersionCachesSuccess verifies that after one successful
// negotiation, subsequent calls return the cached value without re-pinging.
func TestExtraRuntimeAPIVersionCachesSuccess(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()

	apiClient := mocks.NewMockAPIClient(mockCtrl)
	cli := mocks.NewMockCli(mockCtrl)
	tested := &composeService{dockerCli: cli}

	cli.EXPECT().Client().Return(apiClient).AnyTimes()

	// Strict Times(1): a second Ping/ClientVersion call would FAIL the test.
	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.50"}, nil).Times(1)
	apiClient.EXPECT().ClientVersion().Return("1.50").Times(1)

	for i := 0; i < 3; i++ {
		v, err := tested.RuntimeAPIVersion(context.Background())
		assert.NilError(t, err)
		assert.Equal(t, v, "1.50")
	}
}

// TestExtraRuntimeAPIVersionDoesNotCacheError verifies that a failed Ping does
// NOT poison the cache; a subsequent call must retry and succeed.
func TestExtraRuntimeAPIVersionDoesNotCacheError(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()

	apiClient := mocks.NewMockAPIClient(mockCtrl)
	cli := mocks.NewMockCli(mockCtrl)
	tested := &composeService{dockerCli: cli}

	cli.EXPECT().Client().Return(apiClient).AnyTimes()

	first := apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{}, context.DeadlineExceeded).Times(1)
	apiClient.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.44"}, nil).Times(1).After(first)
	apiClient.EXPECT().ClientVersion().Return("1.44").Times(1)

	_, err := tested.RuntimeAPIVersion(context.Background())
	assert.ErrorIs(t, err, context.DeadlineExceeded)

	v, err := tested.RuntimeAPIVersion(context.Background())
	assert.NilError(t, err)
	assert.Equal(t, v, "1.44")
}

// TestExtraRuntimeAPIVersionPerInstanceCache verifies that the cache is
// per-service (i.e., a struct field) and not shared via a package-level var.
// Two different composeService instances must independently negotiate.
func TestExtraRuntimeAPIVersionPerInstanceCache(t *testing.T) {
	mockCtrl := gomock.NewController(t)
	defer mockCtrl.Finish()

	apiClientA := mocks.NewMockAPIClient(mockCtrl)
	cliA := mocks.NewMockCli(mockCtrl)
	svcA := &composeService{dockerCli: cliA}
	cliA.EXPECT().Client().Return(apiClientA).AnyTimes()
	apiClientA.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.40"}, nil).Times(1)
	apiClientA.EXPECT().ClientVersion().Return("1.40").Times(1)

	apiClientB := mocks.NewMockAPIClient(mockCtrl)
	cliB := mocks.NewMockCli(mockCtrl)
	svcB := &composeService{dockerCli: cliB}
	cliB.EXPECT().Client().Return(apiClientB).AnyTimes()
	apiClientB.EXPECT().Ping(gomock.Any(), client.PingOptions{NegotiateAPIVersion: true}).
		Return(client.PingResult{APIVersion: "1.50"}, nil).Times(1)
	apiClientB.EXPECT().ClientVersion().Return("1.50").Times(1)

	vA, errA := svcA.RuntimeAPIVersion(context.Background())
	assert.NilError(t, errA)
	assert.Equal(t, vA, "1.40")

	vB, errB := svcB.RuntimeAPIVersion(context.Background())
	assert.NilError(t, errB)
	assert.Equal(t, vB, "1.50")
}
