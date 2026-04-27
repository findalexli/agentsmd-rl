// Copyright 2026, Pulumi Corporation.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package diy

import (
	"context"
	"fmt"
	"path/filepath"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"

	"github.com/pulumi/pulumi/pkg/v3/backend"
	"github.com/pulumi/pulumi/sdk/v3/go/common/testing/diagtest"
)

// runRefreshSafely calls b.Refresh, recovering from any panic that may occur
// because we pass a deliberately minimal UpdateOperation. The point of the
// test is to verify whether the call hits the lock-acquisition code path,
// not to drive a full refresh.
func runRefreshSafely(
	ctx context.Context,
	b *diyBackend,
	stack backend.Stack,
	op backend.UpdateOperation,
) (err error) {
	defer func() {
		if r := recover(); r != nil {
			err = fmt.Errorf("panic: %v", r)
		}
	}()
	_, err = b.Refresh(ctx, stack, op)
	return err
}

// TestRefreshPreviewOnlySkipsLockHarbor verifies that calling Refresh with
// PreviewOnly=true does NOT acquire the state lock for the diy backend.
//
// Setup: two diy backend instances point at the same on-disk store.
// A second backend (with a different lockID) acquires the stack lock.
// We then call Refresh with PreviewOnly=true on the first backend.
//
// Before the fix: Refresh calls b.Lock unconditionally, which calls
// checkForLock, sees the foreign lock, and returns an error containing
// "the stack is currently locked".
//
// After the fix: Refresh skips locking for the PreviewOnly path. The call
// may still fail or panic for unrelated reasons (the engine inputs are
// minimal), but the resulting error must not mention the state lock.
func TestRefreshPreviewOnlySkipsLockHarbor(t *testing.T) {
	t.Parallel()

	tmpDir := t.TempDir()
	ctx := t.Context()

	b1, err := New(ctx, diagtest.LogSink(t), "file://"+filepath.ToSlash(tmpDir), nil)
	require.NoError(t, err)
	db1, ok := b1.(*diyBackend)
	require.True(t, ok)

	b2, err := New(ctx, diagtest.LogSink(t), "file://"+filepath.ToSlash(tmpDir), nil)
	require.NoError(t, err)
	db2, ok := b2.(*diyBackend)
	require.True(t, ok)

	stackRef, err := b1.ParseStackReference("organization/project/a")
	require.NoError(t, err)

	aStack, err := b1.CreateStack(ctx, stackRef, "", nil, nil)
	require.NoError(t, err)
	require.NotNil(t, aStack)

	// Acquire a lock from the other backend (different lockID).
	require.NoError(t, db2.Lock(ctx, stackRef))
	defer db2.Unlock(ctx, stackRef)

	// Sanity: the foreign lock should be visible to the first backend.
	checkErr := db1.checkForLock(ctx, stackRef)
	require.Error(t, checkErr)
	require.Contains(t, checkErr.Error(), "the stack is currently locked")

	op := backend.UpdateOperation{
		Opts: backend.UpdateOptions{PreviewOnly: true},
	}

	refreshErr := runRefreshSafely(ctx, db1, aStack, op)

	if refreshErr == nil {
		// The function returned no error; that is fine — it certainly did
		// not bail out on the lock check.
		return
	}
	assert.NotContains(
		t,
		strings.ToLower(refreshErr.Error()),
		"currently locked",
		"Refresh with PreviewOnly=true must not perform the state-lock check; "+
			"got error: %v",
		refreshErr,
	)
}

// TestRefreshNonPreviewStillLocksHarbor verifies the inverse: when
// PreviewOnly is false, Refresh continues to acquire the state lock as
// before. This is a pass_to_pass guard: it should hold both before and
// after the fix.
func TestRefreshNonPreviewStillLocksHarbor(t *testing.T) {
	t.Parallel()

	tmpDir := t.TempDir()
	ctx := t.Context()

	b1, err := New(ctx, diagtest.LogSink(t), "file://"+filepath.ToSlash(tmpDir), nil)
	require.NoError(t, err)
	db1, ok := b1.(*diyBackend)
	require.True(t, ok)

	b2, err := New(ctx, diagtest.LogSink(t), "file://"+filepath.ToSlash(tmpDir), nil)
	require.NoError(t, err)
	db2, ok := b2.(*diyBackend)
	require.True(t, ok)

	stackRef, err := b1.ParseStackReference("organization/project/b")
	require.NoError(t, err)
	aStack, err := b1.CreateStack(ctx, stackRef, "", nil, nil)
	require.NoError(t, err)
	require.NotNil(t, aStack)

	require.NoError(t, db2.Lock(ctx, stackRef))
	defer db2.Unlock(ctx, stackRef)

	op := backend.UpdateOperation{
		Opts: backend.UpdateOptions{PreviewOnly: false},
	}

	refreshErr := runRefreshSafely(ctx, db1, aStack, op)

	require.Error(t, refreshErr,
		"Refresh without PreviewOnly must still attempt to acquire the lock and fail")
	assert.Contains(
		t,
		strings.ToLower(refreshErr.Error()),
		"currently locked",
		"Refresh without PreviewOnly should fail on the lock check; "+
			"got error: %v",
		refreshErr,
	)
}
