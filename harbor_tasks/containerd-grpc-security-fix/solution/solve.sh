#!/bin/bash
set -e

cd /workspace/containerd

# Check if already patched (idempotency)
if grep -q "DisableStrictPathChecking" vendor/google.golang.org/grpc/internal/envconfig/envconfig.go 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/go.mod b/go.mod
index 4cc721940ffe3..a01a76bc41eaa 100644
--- a/go.mod
+++ b/go.mod
@@ -80,7 +80,7 @@ require (
 	golang.org/x/sys v0.42.0
 	golang.org/x/time v0.15.0
 	google.golang.org/genproto/googleapis/rpc v0.0.0-20260209200024-4cfbd4190f57
-	google.golang.org/grpc v1.79.2
+	google.golang.org/grpc v1.79.3
 	google.golang.org/protobuf v1.36.11
 	gopkg.in/inf.v0 v0.9.1
 	k8s.io/apimachinery v0.35.2
diff --git a/go.sum b/go.sum
index b61498a8a8671..4babe8f9eb83b 100644
--- a/go.sum
+++ b/go.sum
@@ -532,8 +532,8 @@ google.golang.org/grpc v1.23.0/go.mod h1:Y5yQAOtifL1yxbo5wqy6BxZv8vAUGQwXBOALyac
 google.golang.org/grpc v1.25.1/go.mod h1:c3i+UQWmh7LiEpx4sFZnkU36qjEYZ0imhYfXVyQciAY=
 google.golang.org/grpc v1.27.0/go.mod h1:qbnxyOmOxrQa7FizSgH+ReBfzJrCY1pSN7KXBS8abTk=
 google.golang.org/grpc v1.33.2/go.mod h1:JMHMWHQWaTccqQQlmk3MJZS+GWXOdAesneDmEnv2fbc=
-google.golang.org/grpc v1.79.2 h1:fRMD94s2tITpyJGtBBn7MkMseNpOZU8ZxgC3MMBaXRU=
-google.golang.org/grpc v1.79.2/go.mod h1:KmT0Kjez+0dde/v2j9vzwoAScgEPx/Bw1CYChhHLrHQ=
+google.golang.org/grpc v1.79.3 h1:sybAEdRIEtvcD68Gx7dmnwjZKlyfuc61Dyo9pGXXkKE=
+google.golang.org/grpc v1.79.3/go.mod h1:KmT0Kjez+0dde/v2j9vzwoAScgEPx/Bw1CYChhHLrHQ=
 google.golang.org/protobuf v0.0.0-20200109180630-ec00e32a8dfd/go.mod h1:DFci5gLYBciE7Vtevhsrf46CRTquxDuWsQurQQe4oz8=
 google.golang.org/protobuf v0.0.0-20200221191635-4d8936d0db64/go.mod h1:kwYJMbMJ01Woi6D6+Kah6886xMZcty6N08ah7+eCXa0=
 google.golang.org/protobuf v0.0.0-20200228230310-ab0ca4ff8a60/go.mod h1:cfTl7dwQJ+fmap5saPgwCLgHXTUD7jkjRqWcaiX5VyM=
diff --git a/vendor/google.golang.org/grpc/internal/envconfig/envconfig.go b/vendor/google.golang.org/grpc/internal/envconfig/envconfig.go
index e8dc791299eae..7ad6fb44ca859 100644
--- a/vendor/google.golang.org/grpc/internal/envconfig/envconfig.go
+++ b/vendor/google.golang.org/grpc/internal/envconfig/envconfig.go
@@ -88,6 +88,22 @@ var (
 	// feature can be disabled by setting the environment variable
 	// GRPC_EXPERIMENTAL_PF_WEIGHTED_SHUFFLING to "false".
 	PickFirstWeightedShuffling = boolFromEnv("GRPC_EXPERIMENTAL_PF_WEIGHTED_SHUFFLING", true)
+
+	// DisableStrictPathChecking indicates whether strict path checking is
+	// disabled. This feature can be disabled by setting the environment
+	// variable GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING to "true".
+	//
+	// When strict path checking is enabled, gRPC will reject requests with
+	// paths that do not conform to the gRPC over HTTP/2 specification found at
+	// https://github.com/grpc/grpc/blob/master/doc/PROTOCOL-HTTP2.md.
+	//
+	// When disabled, gRPC will allow paths that do not contain a leading slash.
+	// Enabling strict path checking is recommended for security reasons, as it
+	// prevents potential path traversal vulnerabilities.
+	//
+	// A future release will remove this environment variable, enabling strict
+	// path checking behavior unconditionally.
+	DisableStrictPathChecking = boolFromEnv("GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING", false)
 )

 func boolFromEnv(envVar string, def bool) bool {
diff --git a/vendor/google.golang.org/grpc/server.go b/vendor/google.golang.org/grpc/server.go
index 1b5cefe817150..8efb29a7b95cc 100644
--- a/vendor/google.golang.org/grpc/server.go
+++ b/vendor/google.golang.org/grpc/server.go
@@ -42,6 +42,7 @@ import (
 	"google.golang.org/grpc/internal"
 	"google.golang.org/grpc/internal/binarylog"
 	"google.golang.org/grpc/internal/channelz"
+	"google.golang.org/grpc/internal/envconfig"
 	"google.golang.org/grpc/internal/grpcsync"
 	"google.golang.org/grpc/internal/grpcutil"
 	istats "google.golang.org/grpc/internal/stats"
@@ -149,6 +150,8 @@ type Server struct {

 	serverWorkerChannel      chan func()
 	serverWorkerChannelClose func()
+
+	strictPathCheckingLogEmitted atomic.Bool
 }

 type serverOptions struct {
@@ -1762,6 +1765,24 @@ func (s *Server) processStreamingRPC(ctx context.Context, stream *transport.Serv
 	return ss.s.WriteStatus(statusOK)
 }

+func (s *Server) handleMalformedMethodName(stream *transport.ServerStream, ti *traceInfo) {
+	if ti != nil {
+		ti.tr.LazyLog(&fmtStringer{"Malformed method name %q", []any{stream.Method()}}, true)
+		ti.tr.SetError()
+	}
+	errDesc := fmt.Sprintf("malformed method name: %q", stream.Method())
+	if err := stream.WriteStatus(status.New(codes.Unimplemented, errDesc)); err != nil {
+		if ti != nil {
+			ti.tr.LazyLog(&fmtStringer{"%v", []any{err}}, true)
+			ti.tr.SetError()
+		}
+		channelz.Warningf(logger, s.channelz, "grpc: Server.handleStream failed to write status: %v", err)
+	}
+	if ti != nil {
+		ti.tr.Finish()
+	}
+}
+
 func (s *Server) handleStream(t transport.ServerTransport, stream *transport.ServerStream) {
 	ctx := stream.Context()
 	ctx = contextWithServer(ctx, s)
@@ -1782,26 +1803,30 @@ func (s *Server) handleStream(t transport.ServerTransport, stream *transport.Ser
 	}

 	sm := stream.Method()
-	if sm != "" && sm[0] == '/' {
+	if sm == "" {
+		s.handleMalformedMethodName(stream, ti)
+		return
+	}
+	if sm[0] != '/' {
+		// TODO(easwars): Add a link to the CVE in the below log messages once
+		// published.
+		if envconfig.DisableStrictPathChecking {
+			if old := s.strictPathCheckingLogEmitted.Swap(true); !old {
+				channelz.Warningf(logger, s.channelz, "grpc: Server.handleStream received malformed method name %q. Allowing it because the environment variable GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING is set to true, but this option will be removed in a future release.", sm)
+			}
+		} else {
+			if old := s.strictPathCheckingLogEmitted.Swap(true); !old {
+				channelz.Warningf(logger, s.channelz, "grpc: Server.handleStream rejected malformed method name %q. To temporarily allow such requests, set the environment variable GRPC_GO_EXPERIMENTAL_DISABLE_STRICT_PATH_CHECKING to true. Note that this is not recommended as it may allow requests to bypass security policies.", sm)
+			}
+			s.handleMalformedMethodName(stream, ti)
+			return
+		}
+	} else {
 		sm = sm[1:]
 	}
 	pos := strings.LastIndex(sm, "/")
 	if pos == -1 {
-		if ti != nil {
-			ti.tr.LazyLog(&fmtStringer{"Malformed method name %q", []any{sm}}, true)
-			ti.tr.SetError()
-		}
-		errDesc := fmt.Sprintf("malformed method name: %q", stream.Method())
-		if err := stream.WriteStatus(status.New(codes.Unimplemented, errDesc)); err != nil {
-			if ti != nil {
-				ti.tr.LazyLog(&fmtStringer{"%v", []any{err}}, true)
-				ti.tr.SetError()
-			}
-			channelz.Warningf(logger, s.channelz, "grpc: Server.handleStream failed to write status: %v", err)
-		}
-		if ti != nil {
-			ti.tr.Finish()
-		}
+		s.handleMalformedMethodName(stream, ti)
 		return
 	}
 	service := sm[:pos]
diff --git a/vendor/google.golang.org/grpc/version.go b/vendor/google.golang.org/grpc/version.go
index f9da6c6cae36c..76c2eed773a2c 100644
--- a/vendor/google.golang.org/grpc/version.go
+++ b/vendor/google.golang.org/grpc/version.go
@@ -19,4 +19,4 @@
 package grpc

 // Version is the current grpc version.
-const Version = "1.79.2"
+const Version = "1.79.3"
diff --git a/vendor/modules.txt b/vendor/modules.txt
index eb799969b184f..5e9eeae8c5150 100644
--- a/vendor/modules.txt
+++ b/vendor/modules.txt
@@ -741,7 +741,7 @@ google.golang.org/genproto/googleapis/api/httpbody
 google.golang.org/genproto/googleapis/rpc/code
 google.golang.org/genproto/googleapis/rpc/errdetails
 google.golang.org/genproto/googleapis/rpc/status
-# google.golang.org/grpc v1.79.2
+# google.golang.org/grpc v1.79.3
 ## explicit; go 1.24.0
 google.golang.org/grpc
 google.golang.org/grpc/attributes
PATCH

echo "Patch applied successfully!"
