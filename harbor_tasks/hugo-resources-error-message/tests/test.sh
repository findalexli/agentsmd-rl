#!/bin/bash

cd /workspace/hugo

# Create a Go test file that tests getImageOps behavior
# This test creates a resource that doesn't implement ImageResourceOps
# and verifies the panic message contains helpful information
cat > /workspace/hugo/resources/getimageops_panic_test.go << 'GOEOF'
package resources

import (
	"reflect"
	"testing"
)

func TestGetImageOpsPanic(t *testing.T) {
	// Create a minimal spec for testing
	spec := &Spec{}

	// Create a resource that does NOT implement images.ImageResourceOps
	// We use a simple resource that only implements the basic interface
	nonImageResource := &testNonImageResource{
		name_:      "test.svg",
		mediaType_: "image/svg+xml",
	}

	adapter := newResourceAdapter(spec, false, nonImageResource)

	// Call getImageOps and expect a panic
	defer func() {
		r := recover()
		if r == nil {
			t.Fatal("expected panic but got none")
		}

		msg, ok := r.(string)
		if !ok {
			t.Fatalf("expected panic message to be string, got %T", r)
		}

		// Verify the message contains helpful information
		// The fixed version should include:
		// - Resource name
		// - Media type
		// - Hints about reflection methods

		// Check for resource name presence (the exact format may vary)
		if !contains(msg, "test.svg") {
			t.Errorf("panic message should mention resource name 'test.svg', got: %s", msg)
		}

		// Check for media type presence
		if !contains(msg, "image/svg+xml") {
			t.Errorf("panic message should mention media type 'image/svg+xml', got: %s", msg)
		}

		// Check for reflection method hints
		if !contains(msg, "reflect.IsImageResource") {
			t.Errorf("panic message should mention reflect.IsImageResource, got: %s", msg)
		}
		if !contains(msg, "reflect.IsImageResourceProcessable") {
			t.Errorf("panic message should mention reflect.IsImageResourceProcessable, got: %s", msg)
		}
		if !contains(msg, "reflect.IsImageResourceWithMeta") {
			t.Errorf("panic message should mention reflect.IsImageResourceWithMeta, got: %s", msg)
		}
	}()

	// This should panic
	_ = adapter.getImageOps()
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsHelper(s, substr))
}

func containsHelper(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}

// testNonImageResource is a minimal resource that doesn't implement ImageResourceOps
type testNonImageResource struct {
	name_      string
	mediaType_ string
}

func (r *testNonImageResource) Name() string {
	return r.name_
}

func (r *testNonImageResource) MediaType() media.Type {
	return media.Type{Type: r.mediaType_}
}

func (r *testNonImageResource) Content(_ any) (any, error) {
	return nil, nil
}

func (r *testNonImageResource) Key() string {
	return r.name_
}

func (r *testNonImageResource) StaleVersion() uint32 {
	return 0
}
GOEOF

# Install pytest if not already installed
pip3 install pytest --break-system-packages 2>/dev/null || true

# Run the verifier tests and capture result
python3 -m pytest /tests/test_outputs.py -v --tb=short 2>&1 | tee /logs/verifier/test_output.log
TEST_EXIT=${PIPESTATUS[0]}

# Clean up the temporary Go test file
rm -f /workspace/hugo/resources/getimageops_panic_test.go

# Write binary reward file (1 if all tests pass, 0 otherwise)
if [ $TEST_EXIT -eq 0 ]; then
    echo "1" > /logs/verifier/reward.txt
else
    echo "0" > /logs/verifier/reward.txt
fi
