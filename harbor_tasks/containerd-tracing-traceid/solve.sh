#!/bin/bash
set -e

cd /workspace/containerd

# Apply the gold patch for tracing: add option to inject trace ID into logrus fields
cat <<'PATCH' | git apply -
diff --git a/cmd/containerd/command/main.go b/cmd/containerd/command/main.go
index 3d03d38c5284e..27d29e31ce530 100644
--- a/cmd/containerd/command/main.go
+++ b/cmd/containerd/command/main.go
@@ -35,11 +35,13 @@ import (
 	"github.com/containerd/containerd/v2/core/mount"
 	"github.com/containerd/containerd/v2/defaults"
 	"github.com/containerd/containerd/v2/pkg/sys"
+	"github.com/containerd/containerd/v2/pkg/tracing"
 	"github.com/containerd/containerd/v2/version"
 	"github.com/containerd/errdefs"
 	"github.com/containerd/log"
 	"github.com/containerd/plugin"
 	"github.com/containerd/plugin/registry"
+	"github.com/sirupsen/logrus"
 	"github.com/urfave/cli/v2"
 	"google.golang.org/grpc/grpclog"
 )
@@ -205,6 +207,10 @@ can be used and modified as necessary as a custom configuration.`
 			log.G(ctx).WithError(w).Warn("cleanup temp mount")
 		}

+		// Register logging hook for tracing
+		tracingHook := tracing.NewLogrusHook(tracing.WithTraceIDField(config.Debug.LogTraceID))
+		logrus.StandardLogger().AddHook(tracingHook)
+
 		log.G(ctx).WithFields(log.Fields{
 			"version":  version.Version,
 			"revision": version.Revision,
diff --git a/cmd/containerd/server/config/config.go b/cmd/containerd/server/config/config.go
index 76b04dad60350..371e71fb98ee2 100644
--- a/cmd/containerd/server/config/config.go
+++ b/cmd/containerd/server/config/config.go
@@ -233,7 +233,8 @@ type Debug struct {
 	GID     int    `toml:"gid"`
 	Level   string `toml:"level"`
 	// Format represents the logging format. Supported values are 'text' and 'json'.
-	Format string `toml:"format"`
+	Format     string `toml:"format"`
+	LogTraceID bool   `toml:"log_trace_id"`
 }

 // MetricsConfig provides metrics configuration
diff --git a/pkg/tracing/log.go b/pkg/tracing/log.go
index 3af24a294a50e..b1c3a74024242 100644
--- a/pkg/tracing/log.go
+++ b/pkg/tracing/log.go
@@ -35,9 +35,21 @@ var allLevels = []log.Level{
 	log.TraceLevel,
 }

+type HookOpt func(*LogrusHook)
+
 // NewLogrusHook creates a new logrus hook
-func NewLogrusHook() *LogrusHook {
-	return &LogrusHook{}
+func NewLogrusHook(opts ...HookOpt) *LogrusHook {
+	hook := &LogrusHook{}
+	for _, opt := range opts {
+		opt(hook)
+	}
+	return hook
+}
+
+func WithTraceIDField(enabled bool) HookOpt {
+	return func(h *LogrusHook) {
+		h.enableTraceIDField = enabled
+	}
 }

 // LogrusHook is a [logrus.Hook] which adds logrus events to active spans.
@@ -45,7 +57,9 @@ func NewLogrusHook() *LogrusHook {
 // is a no-op.
 //
 // [logrus.Hook]: https://github.com/sirupsen/logrus/blob/v1.9.3/hooks.go#L3-L11
-type LogrusHook struct{}
+type LogrusHook struct {
+	enableTraceIDField bool
+}

 // Levels returns the logrus levels that this hook is interested in.
 func (h *LogrusHook) Levels() []log.Level {
@@ -59,7 +73,15 @@ func (h *LogrusHook) Fire(entry *log.Entry) error {
 		return nil
 	}

-	if !span.IsRecording() || !span.SpanContext().IsValid() {
+	if !span.SpanContext().IsValid() {
+		return nil
+	}
+
+	if h.enableTraceIDField {
+		entry.Data["trace_id"] = span.SpanContext().TraceID().String()
+	}
+
+	if !span.IsRecording() {
 		return nil
 	}

diff --git a/pkg/tracing/log_test.go b/pkg/tracing/log_test.go
new file mode 100644
index 0000000000000..ced6d30a21528
--- /dev/null
+++ b/pkg/tracing/log_test.go
@@ -0,0 +1,91 @@
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
+package tracing
+
+import (
+	"context"
+	"testing"
+
+	"github.com/containerd/log"
+	"github.com/stretchr/testify/assert"
+	"go.opentelemetry.io/otel/trace"
+)
+
+const expectedTraceIDStr = "0102030405060708090a0b0c0d0e0f10"
+
+var (
+	testTraceID = trace.TraceID{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
+	testSpanID  = trace.SpanID{1, 2, 3, 4, 5, 6, 7, 8}
+)
+
+func TestLogrusHookTraceID(t *testing.T) {
+	tests := []struct {
+		name        string
+		enableOpt   bool
+		withSpan    bool
+		expectedTID string
+	}{
+		{
+			name:        "TraceIDInjected",
+			enableOpt:   true,
+			withSpan:    true,
+			expectedTID: expectedTraceIDStr,
+		},
+		{
+			name:      "TraceIDNotInjected_OptionDisabled",
+			enableOpt: false,
+			withSpan:  true,
+		},
+		{
+			name:      "TraceIDNotInjected_NoSpan",
+			enableOpt: true,
+			withSpan:  false,
+		},
+	}
+
+	for _, tc := range tests {
+		t.Run(tc.name, func(t *testing.T) {
+			ctx := context.Background()
+			if tc.withSpan {
+				ctx = trace.ContextWithSpanContext(
+					ctx,
+					trace.NewSpanContext(trace.SpanContextConfig{
+						TraceID: testTraceID,
+						SpanID:  testSpanID,
+					}),
+				)
+			}
+
+			hook := NewLogrusHook(WithTraceIDField(tc.enableOpt))
+			entry := &log.Entry{
+				Context: ctx,
+				Data:    make(log.Fields),
+			}
+
+			err := hook.Fire(entry)
+			assert.NoError(t, err)
+
+			traceID, ok := entry.Data["trace_id"]
+			if tc.expectedTID != "" {
+				assert.True(t, ok)
+				assert.Equal(t, tc.expectedTID, traceID)
+			} else {
+				assert.False(t, ok)
+			}
+		})
+	}
+}
diff --git a/pkg/tracing/plugin/otlp.go b/pkg/tracing/plugin/otlp.go
index 39118329095eb..c7135e03710bc 100644
--- a/pkg/tracing/plugin/otlp.go
+++ b/pkg/tracing/plugin/otlp.go
@@ -25,13 +25,11 @@ import (
 	"time"

 	"github.com/containerd/containerd/v2/pkg/deprecation"
-	"github.com/containerd/containerd/v2/pkg/tracing"
 	"github.com/containerd/containerd/v2/plugins"
 	"github.com/containerd/containerd/v2/plugins/services/warning"
 	"github.com/containerd/errdefs"
 	"github.com/containerd/plugin"
 	"github.com/containerd/plugin/registry"
-	"github.com/sirupsen/logrus"
 	"go.opentelemetry.io/otel"
 	"go.opentelemetry.io/otel/exporters/otlp/otlptrace"
 	"go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
@@ -110,9 +108,6 @@ func init() {
 			return newTracer(ic.Context, procs)
 		},
 	})
-
-	// Register logging hook for tracing
-	logrus.StandardLogger().AddHook(tracing.NewLogrusHook())
 }

 // OTLPConfig holds the configurations for the built-in otlp span processor
PATCH

echo "Patch applied successfully"
