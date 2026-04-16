#!/bin/bash
set -e

cd /workspace/containerd

# Idempotency check - verify if fix is already applied
if grep -q "ctrdutil.SanitizeError" internal/cri/instrument/instrumented_service.go; then
    echo "Fix already applied, exiting"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/internal/cri/instrument/instrumented_service.go b/internal/cri/instrument/instrumented_service.go
index c2f5c8de995e..4379f9599743 100644
--- a/internal/cri/instrument/instrumented_service.go
+++ b/internal/cri/instrument/instrumented_service.go
@@ -359,6 +359,10 @@ func (in *instrumentedService) PullImage(ctx context.Context, r *runtime.PullIma
 		span.RecordError(err)
 	}()
 	res, err = in.c.PullImage(ctrdutil.WithNamespace(ctx), r)
+	// Sanitize error to remove sensitive information from both logs and returned gRPC error
+	if err != nil {
+		err = ctrdutil.SanitizeError(err)
+	}
 	return res, errgrpc.ToGRPC(err)
 }

@@ -376,6 +380,10 @@ func (in *instrumentedService) ListImages(ctx context.Context, r *runtime.ListIm
 		}
 	}()
 	res, err = in.c.ListImages(ctrdutil.WithNamespace(ctx), r)
+	// Sanitize error to remove sensitive information from both logs and returned gRPC error
+	if err != nil {
+		err = ctrdutil.SanitizeError(err)
+	}
 	return res, errgrpc.ToGRPC(err)
 }

@@ -393,6 +401,10 @@ func (in *instrumentedService) ImageStatus(ctx context.Context, r *runtime.Image
 		}
 	}()
 	res, err = in.c.ImageStatus(ctrdutil.WithNamespace(ctx), r)
+	// Sanitize error to remove sensitive information from both logs and returned gRPC error
+	if err != nil {
+		err = ctrdutil.SanitizeError(err)
+	}
 	return res, errgrpc.ToGRPC(err)
 }

@@ -411,6 +423,10 @@ func (in *instrumentedService) RemoveImage(ctx context.Context, r *runtime.Remov
 		span.RecordError(err)
 	}()
 	res, err := in.c.RemoveImage(ctrdutil.WithNamespace(ctx), r)
+	// Sanitize error to remove sensitive information from both logs and returned gRPC error
+	if err != nil {
+		err = ctrdutil.SanitizeError(err)
+	}
 	return res, errgrpc.ToGRPC(err)
 }

diff --git a/internal/cri/util/sanitize.go b/internal/cri/util/sanitize.go
new file mode 100644
index 000000000000..d50a15ebf669
--- /dev/null
+++ b/internal/cri/util/sanitize.go
@@ -0,0 +1,93 @@
+/*
+   Copyright The containerd Authors.
+
+   Licensed under the Apache License, Version 2.0 (the "License");
+   you may not use this file except in compliance with the License.
+   You may obtain a copy of the License at
+
+       http://www.apache.org/licenses/LICENSE-2.0
+
+   Unless required by applicable law or agreed to in writing, software
+   distributed under the License is distributed on an "AS IS" BASIS,
+   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+   See the License for the specific language governing permissions and
+   limitations under the License.
+*/
+
+package util
+
+import (
+	"errors"
+	"net/url"
+	"strings"
+)
+
+// SanitizeError sanitizes an error by redacting sensitive information in URLs.
+// If the error contains a *url.Error, it parses and sanitizes the URL.
+// Otherwise, it returns the error unchanged.
+func SanitizeError(err error) error {
+	if err == nil {
+		return nil
+	}
+
+	// Check if the error is or contains a *url.Error
+	var urlErr *url.Error
+	if errors.As(err, &urlErr) {
+		// Parse and sanitize the URL
+		sanitizedURL := sanitizeURL(urlErr.URL)
+		if sanitizedURL != urlErr.URL {
+			// Wrap with sanitized url.Error
+			return &sanitizedError{
+				original:     err,
+				sanitizedURL: sanitizedURL,
+				urlError:     urlErr,
+			}
+		}
+		return err
+	}
+
+	// No sanitization needed for non-URL errors
+	return err
+}
+
+// sanitizeURL properly parses a URL and redacts all query parameters.
+func sanitizeURL(rawURL string) string {
+	parsed, err := url.Parse(rawURL)
+	if err != nil {
+		// If URL parsing fails, return original (malformed URLs shouldn't leak tokens)
+		return rawURL
+	}
+
+	// Check if URL has query parameters
+	query := parsed.Query()
+	if len(query) == 0 {
+		return rawURL
+	}
+
+	// Redact all query parameters
+	for param := range query {
+		query.Set(param, "[REDACTED]")
+	}
+
+	// Reconstruct URL with sanitized query
+	parsed.RawQuery = query.Encode()
+	return parsed.String()
+}
+
+// sanitizedError wraps an error containing a *url.Error with a sanitized URL.
+type sanitizedError struct {
+	original     error
+	sanitizedURL string
+	urlError     *url.Error
+}
+
+// Error returns the error message with the sanitized URL.
+func (e *sanitizedError) Error() string {
+	// Replace all occurrences of the original URL with the sanitized version
+	return strings.ReplaceAll(e.original.Error(), e.urlError.URL, e.sanitizedURL)
+}
+
+// Unwrap returns the original error for error chain traversal.
+func (e *sanitizedError) Unwrap() error {
+	return e.original
+}
diff --git a/internal/cri/util/sanitize_test.go b/internal/cri/util/sanitize_test.go
new file mode 100644
index 000000000000..03e4fb269406
--- /dev/null
+++ b/internal/cri/util/sanitize_test.go
@@ -0,0 +1,128 @@
+/*
+   Copyright The containerd Authors.
+
+   Licensed under the Apache License, Version 2.0 (the "License");
+   you may not use this file except in compliance with the License.
+   You may obtain a copy of the License at
+
+       http://www.apache.org/licenses/LICENSE-2.0
+
+   Unless required by applicable law or agreed to in writing, software
+   distributed under the License is distributed on an "AS IS" BASIS,
+   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+   See the License for the specific language governing permissions and
+   limitations under the License.
+*/
+
+package util
+
+import (
+	"errors"
+	"fmt"
+	"net/url"
+	"testing"
+
+	"github.com/stretchr/testify/assert"
+	"github.com/stretchr/testify/require"
+)
+
+func TestSanitizeError_SimpleURLError(t *testing.T) {
+	// Create a url.Error with sensitive info
+	originalURL := "https://storage.blob.core.windows.net/container/blob?sig=SECRET&sv=2020"
+	urlErr := &url.Error{
+		Op:  "Get",
+		URL: originalURL,
+		Err: fmt.Errorf("connection timeout"),
+	}
+
+	// Sanitize
+	sanitized := SanitizeError(urlErr)
+	require.NotNil(t, sanitized)
+
+	// Check it's a sanitizedError with correct properties
+	sanitizedErr, ok := sanitized.(*sanitizedError)
+	require.True(t, ok, "Should return *sanitizedError type")
+	assert.Equal(t, urlErr, sanitizedErr.original)
+	assert.Equal(t, urlErr, sanitizedErr.urlError)
+	assert.Equal(t, "https://storage.blob.core.windows.net/container/blob?sig=%5BREDACTED%5D&sv=%5BREDACTED%5D", sanitizedErr.sanitizedURL)
+
+	// Test Error() method - verifies ReplaceAll functionality
+	expected := "Get \"https://storage.blob.core.windows.net/container/blob?sig=%5BREDACTED%5D&sv=%5BREDACTED%5D\": connection timeout"
+	assert.Equal(t, expected, sanitized.Error())
+}
+
+func TestSanitizeError_WrappedError(t *testing.T) {
+	originalURL := "https://storage.blob.core.windows.net/blob?sig=SECRET&sv=2020"
+	urlErr := &url.Error{
+		Op:  "Get",
+		URL: originalURL,
+		Err: fmt.Errorf("timeout"),
+	}
+
+	wrappedErr := fmt.Errorf("image pull failed: %w", urlErr)
+
+	// Sanitize
+	sanitized := SanitizeError(wrappedErr)
+
+	// Test Error() method with wrapped error - verifies ReplaceAll works in wrapped context
+	sanitizedMsg := sanitized.Error()
+	assert.NotContains(t, sanitizedMsg, "SECRET", "Secret should be sanitized")
+	assert.Contains(t, sanitizedMsg, "image pull failed", "Wrapper message should be preserved")
+	assert.Contains(t, sanitizedMsg, "%5BREDACTED%5D", "Should contain sanitized marker")
+
+	// Should still be able to unwrap to url.Error
+	var targetURLErr *url.Error
+	assert.True(t, errors.As(sanitized, &targetURLErr),
+		"Should be able to find *url.Error in sanitized error chain")
+
+	// Verify url.Error properties are preserved
+	assert.Equal(t, "Get", targetURLErr.Op)
+	assert.Contains(t, targetURLErr.Err.Error(), "timeout")
+}
+
+func TestSanitizeError_NonURLError(t *testing.T) {
+	// Regular error without url.Error
+	regularErr := fmt.Errorf("some error occurred")
+
+	sanitized := SanitizeError(regularErr)
+
+	// Should return the exact same error object
+	assert.Equal(t, regularErr, sanitized,
+		"Non-URL errors should pass through unchanged")
+}
+
+func TestSanitizeError_NilError(t *testing.T) {
+	sanitized := SanitizeError(nil)
+	assert.Nil(t, sanitized, "nil error should return nil")
+}
+
+func TestSanitizeError_NoQueryParams(t *testing.T) {
+	// URL without any query parameters
+	urlErr := &url.Error{
+		Op:  "Get",
+		URL: "https://registry.example.com/v2/image/manifests/latest",
+		Err: fmt.Errorf("not found"),
+	}
+
+	sanitized := SanitizeError(urlErr)
+
+	// Should return the same error object (no sanitization needed)
+	assert.Equal(t, urlErr, sanitized,
+		"Errors without query params should pass through unchanged")
+}
+
+func TestSanitizedError_Unwrap(t *testing.T) {
+	originalURL := "https://storage.blob.core.windows.net/blob?sig=SECRET"
+	urlErr := &url.Error{
+		Op:  "Get",
+		URL: originalURL,
+		Err: fmt.Errorf("timeout"),
+	}
+
+	sanitized := SanitizeError(urlErr)
+
+	// Should be able to unwrap
+	unwrapped := errors.Unwrap(sanitized)
+	assert.NotNil(t, unwrapped, "Should be able to unwrap sanitized error")
+	assert.Equal(t, urlErr, unwrapped, "Unwrapped should be the original error")
+}
PATCH

echo "Patch applied successfully"
