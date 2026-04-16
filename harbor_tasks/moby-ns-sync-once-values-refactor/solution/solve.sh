#!/bin/bash
set -e

cd /workspace/moby

# Check if already applied
if grep -q "sync.OnceValues" daemon/libnetwork/ns/init_linux.go; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/daemon/libnetwork/ns/init_linux.go b/daemon/libnetwork/ns/init_linux.go
index a59812ec07c8a..266875a738d3c 100644
--- a/daemon/libnetwork/ns/init_linux.go
+++ b/daemon/libnetwork/ns/init_linux.go
@@ -14,65 +14,67 @@ import (
 	"github.com/vishvananda/netns"
 )

-var (
-	initNs   = netns.None()
-	initNl   nlwrap.Handle
-	initOnce sync.Once
-	// NetlinkSocketsTimeout represents the default timeout duration for the sockets
-	NetlinkSocketsTimeout = 3 * time.Second
-)
+// NetlinkSocketsTimeout represents the default timeout duration for the sockets.
+const NetlinkSocketsTimeout = 3 * time.Second
+
+// initNamespace initializes a new network namespace.
+var initNamespace = sync.OnceValues(initHandles)

 // initHandles initializes a new network namespace
-func initHandles() {
-	var err error
-	initNs, err = netns.Get()
+func initHandles() (netns.NsHandle, nlwrap.Handle) {
+	initNs, err := netns.Get()
 	if err != nil {
-		log.G(context.TODO()).Errorf("could not get initial namespace: %v", err)
+		log.G(context.Background()).WithError(err).Error("could not get initial namespace: falling back to using netns.None")
+		initNs = netns.None()
 	}
-	initNl, err = nlwrap.NewHandle(getSupportedNlFamilies()...)
+	initNl, err := nlwrap.NewHandle(getSupportedNlFamilies()...)
 	if err != nil {
 		// Fail fast to keep the invariant: NlHandle must be a valid handle
 		panic(fmt.Errorf("could not create netlink handle on initial (host) namespace: %w", err))
 	}
 	err = initNl.SetSocketTimeout(NetlinkSocketsTimeout)
 	if err != nil {
-		log.G(context.TODO()).Warnf("Failed to set the timeout on the default netlink handle sockets: %v", err)
+		log.G(context.Background()).WithError(err).Warn("failed to set the timeout on the default netlink handle sockets")
 	}
+
+	return initNs, initNl
 }

 // ResetHandles resets the initial namespace and netlink handles.
 // This is useful for testing to ensure a clean state. It will
 // panic if called outside a test.
+//
+// Note: This function is not safe for concurrent use with callers
+// that are using handles obtained from this package. It may close
+// handles while they are still in use.
 func ResetHandles() {
 	if !testing.Testing() {
 		panic("ResetHandles should only be called from tests")
 	}
+	initNs, initNl := initNamespace()
+	// Reset the initNamespace sync.OnceValues. This may race with
+	// concurrent callers still calling the old initNamespace (and
+	// values), but adding a [sync.RWMutex] only for the test-case
+	// is probably too much (unless things are racy).
+	initNamespace = sync.OnceValues(initHandles)
 	if initNs.IsOpen() {
-		initNs.Close()
-		initNs = netns.None()
+		_ = initNs.Close()
 	}
 	if initNl.Handle != nil {
 		initNl.Close()
-		initNl = nlwrap.Handle{}
 	}
-	initOnce = sync.Once{}
-}
-
-// ParseHandlerInt transforms the namespace handler into an integer
-func ParseHandlerInt() int {
-	return int(getHandler())
 }

-// GetHandler returns the namespace handler
-func getHandler() netns.NsHandle {
-	initOnce.Do(initHandles)
-	return initNs
+// NsHandle returns the network namespace handle for the initial (host) namespace.
+func NsHandle() netns.NsHandle {
+	ns, _ := initNamespace()
+	return ns
 }

-// NlHandle returns the netlink handler
+// NlHandle returns the netlink handle.
 func NlHandle() nlwrap.Handle {
-	initOnce.Do(initHandles)
-	return initNl
+	_, nl := initNamespace()
+	return nl
 }

 func getSupportedNlFamilies() []int {
@@ -99,7 +101,7 @@ func checkXfrmSocket() error {
 	if err != nil {
 		return err
 	}
-	syscall.Close(fd)
+	_ = syscall.Close(fd)
 	return nil
 }

@@ -109,6 +111,6 @@ func checkNfSocket() error {
 	if err != nil {
 		return err
 	}
-	syscall.Close(fd)
+	_ = syscall.Close(fd)
 	return nil
 }
diff --git a/daemon/libnetwork/ns/init_windows.go b/daemon/libnetwork/ns/init_windows.go
deleted file mode 100644
index f5838f81dd160..0000000000000
--- a/daemon/libnetwork/ns/init_windows.go
+++ /dev/null
@@ -1,3 +0,0 @@
-package ns
-
-// File is present so that go build ./... is closer to working on Windows from repo root.
diff --git a/daemon/libnetwork/osl/interface_linux.go b/daemon/libnetwork/osl/interface_linux.go
index 62062b5951bba..3e17f3908e489 100644
--- a/daemon/libnetwork/osl/interface_linux.go
+++ b/daemon/libnetwork/osl/interface_linux.go
@@ -262,7 +262,7 @@ func (n *Namespace) AddInterface(ctx context.Context, srcName, dstPrefix, dstNam
 		if nerr := n.nlHandle.LinkSetName(iface, i.SrcName()); nerr != nil {
 			log.G(ctx).Errorf("renaming interface (%s->%s) failed, %v after config error %v", i.DstName(), i.SrcName(), nerr, err)
 		}
-		if nerr := n.nlHandle.LinkSetNsFd(iface, ns.ParseHandlerInt()); nerr != nil {
+		if nerr := n.nlHandle.LinkSetNsFd(iface, int(ns.NsHandle())); nerr != nil {
 			log.G(ctx).Errorf("moving interface %s to host ns failed, %v, after config error %v", i.SrcName(), nerr, err)
 		}
 		return err
@@ -845,8 +845,9 @@ func (n *Namespace) RemoveInterface(i *Interface) error {
 		}
 	} else if !n.isDefault {
 		// Move the network interface to caller namespace.
+		//
 		// TODO(aker): What's this really doing? There are no calls to LinkDel in this package: is this code really used? (Interface.Remove() has 3 callers); see https://github.com/moby/moby/pull/46315/commits/108595c2fe852a5264b78e96f9e63cda284990a6#r1331265335
-		if err := n.nlHandle.LinkSetNsFd(iface, ns.ParseHandlerInt()); err != nil {
+		if err := n.nlHandle.LinkSetNsFd(iface, int(ns.NsHandle())); err != nil {
 			log.G(context.TODO()).Debugf("LinkSetNsFd failed for interface %s: %v", i.SrcName(), err)
 			return err
 		}
PATCH

echo "Patch applied successfully"
