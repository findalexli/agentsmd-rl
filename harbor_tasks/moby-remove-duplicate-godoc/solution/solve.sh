#!/bin/bash
set -e

cd /workspace/moby

# Apply the gold patch for PR #52260:
# - Remove duplicate package doc from local_unix.go and local_windows.go
# - Enable godoclint linter in .golangci.yml

patch -p1 <<'PATCH'
diff --git a/.golangci.yml b/.golangci.yml
index 4d576e508452b..63857de0f8427 100644
--- a/.golangci.yml
+++ b/.golangci.yml
@@ -27,7 +27,8 @@ linters:
     - fatcontext                # Detects nested contexts in loops and function literals.
     - forbidigo
     - gocheckcompilerdirectives # Detects invalid go compiler directive comments (//go:).
-    - gocritic                  # Detects for bugs, performance and style issues.
+    - gocritic                  # Detects bugs, performance and style issues.
+    - godoclint                 # Detects issues in godoc.
     - gosec                     # Detects security problems.
     - govet
     - iface                     # Detects incorrect use of interfaces. Currently only used for "identical" interfaces in the same package.
diff --git a/daemon/volume/local/local_unix.go b/daemon/volume/local/local_unix.go
index dff9a03d5f0e3..48de6a54837aa 100644
--- a/daemon/volume/local/local_unix.go
+++ b/daemon/volume/local/local_unix.go
@@ -1,8 +1,5 @@
 //go:build linux || freebsd

-// Package local provides the default implementation for volumes. It
-// is used to mount data volume containers and directories local to
-// the host server.
 package local

 import (
diff --git a/daemon/volume/local/local_windows.go b/daemon/volume/local/local_windows.go
index 0fd26bb008791..ad5c595170fd8 100644
--- a/daemon/volume/local/local_windows.go
+++ b/daemon/volume/local/local_windows.go
@@ -1,6 +1,3 @@
-// Package local provides the default implementation for volumes. It
-// is used to mount data volume containers and directories local to
-// the host server.
 package local

 import (
PATCH

# Idempotency check: verify godoclint is enabled
if ! grep -q "godoclint" .golangci.yml; then
    echo "ERROR: Failed to apply patch - godoclint not found in .golangci.yml"
    exit 1
fi

echo "Patch applied successfully"
