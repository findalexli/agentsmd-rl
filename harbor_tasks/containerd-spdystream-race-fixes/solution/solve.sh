#!/bin/bash
set -e

cd /workspace/containerd

# Apply the gold patch to update moby/spdystream from v0.2.0 to v0.5.0
cat <<'PATCH' | patch -p1
diff --git a/go.mod b/go.mod
index febc834935c14..6d090b5154739 100644
--- a/go.mod
+++ b/go.mod
@@ -119,7 +119,7 @@ require (
 	github.com/matttproud/golang_protobuf_extensions v1.0.4 // indirect
 	github.com/miekg/pkcs11 v1.1.1 // indirect
 	github.com/mistifyio/go-zfs/v3 v3.0.1 // indirect
-	github.com/moby/spdystream v0.2.0 // indirect
+	github.com/moby/spdystream v0.5.0 // indirect
 	github.com/modern-go/concurrent v0.0.0-20180306012644-bacd9c7ef1dd // indirect
 	github.com/modern-go/reflect2 v1.0.2 // indirect
 	github.com/pkg/errors v0.9.1 // indirect

diff --git a/go.sum b/go.sum
index c09121fd06b25..0359bc7357cef 100644
--- a/go.sum
+++ b/go.sum
@@ -509,8 +509,8 @@ github.com/mitchellh/mapstructure v1.1.2/go.mod h1:FVVH3fgwuzCH5S8UJGiWEs2h04kUh
 github.com/mndrix/tap-go v0.0.0-20171203230836-629fa407e90b/go.mod h1:pzzDgJWZ34fGzaAZGFW22KVZDfyrYW+QABMrWnJBnSs=
 github.com/moby/locker v1.0.1 h1:fOXqR41zeveg4fFODix+1Ch4mj/gT0NE1XJbp/epuBg=
 github.com/moby/locker v1.0.1/go.mod h1:S7SDdo5zpBK84bzzVlKr2V0hz+7x9hWbYC/kq7oQppc=
-github.com/moby/spdystream v0.2.0 h1:cjW1zVyyoiM0T7b6UoySUFqzXMoqRckQtXwGPiBhOM8=
-github.com/moby/spdystream v0.2.0/go.mod h1:f7i0iNDQJ059oMTcWxx8MA/zKFIuD/lY+0GqbN2Wy8c=
+github.com/moby/spdystream v0.5.0 h1:7r0J1Si3QO/kjRitvSLVVFUjxMEb/YLj6S9FF62JBCU=
+github.com/moby/spdystream v0.5.0/go.mod h1:xBAYlnt/ay+11ShkdFKNAG7LsyK/tmNBVvVOwrfMgdI=
 github.com/moby/sys/mountinfo v0.4.0/go.mod h1:rEr8tzG/lsIZHBtN/JjGG+LMYx9eXgW2JI+6q0qou+A=
 github.com/moby/sys/mountinfo v0.6.2 h1:BzJjoreD5BMFNmD9Rus6gdd1pLuecOFPt8wC+Vygl78=
 github.com/moby/sys/mountinfo v0.6.2/go.mod h1:IJb6JQeOklcdMU9F5xQ8ZALD+CUr5VlGpwtX+VE0rpI=

diff --git a/integration/client/go.sum b/integration/client/go.sum
index 9c719f0f03197..6fb91e6fbc809 100644
--- a/integration/client/go.sum
+++ b/integration/client/go.sum
@@ -1837,6 +1837,7 @@ github.com/mndrix/tap-go v0.0.0-20171203230836-629fa407e90b/go.mod h1:pzzDgJWZ34
 github.com/moby/locker v1.0.1 h1:fOXqR41zeveg4fFODix+1Ch4mj/gT0NE1XJbp/epuBg=
 github.com/moby/locker v1.0.1/go.mod h1:S7SDdo5zpBK84bzzVlKr2V0hz+7x9hWbYC/kq7oQppc=
 github.com/moby/spdystream v0.2.0/go.mod h1:f7i0iNDQJ059oMTcWxx8MA/zKFIuD/lY+0GqbN2Wy8c=
+github.com/moby/spdystream v0.5.0/go.mod h1:xBAYlnt/ay+11ShkdFKNAG7LsyK/tmNBVvVOwrfMgdI=
 github.com/moby/sys/mountinfo v0.4.1/go.mod h1:rEr8tzG/lsIZHBtN/JjGG+LMYx9eXgW2JI+6q0qou+A=
 github.com/moby/sys/mountinfo v0.5.0/go.mod h1:3bMD3Rg+zkqx8MRYPi7Pyb0Ie97QEBmdxbhnCLlSvSU=
 github.com/moby/sys/mountinfo v0.6.2 h1:BzJjoreD5BMFNmD9Rus6gdd1pLuecOFPt8wC+Vygl78=

diff --git a/vendor/github.com/moby/spdystream/connection.go b/vendor/github.com/moby/spdystream/connection.go
index d906bb05ceda3..1394d0ad4c22c 100644
--- a/vendor/github.com/moby/spdystream/connection.go
+++ b/vendor/github.com/moby/spdystream/connection.go
@@ -208,9 +208,10 @@ type Connection struct {
 	nextStreamId     spdy.StreamId
 	receivedStreamId spdy.StreamId

-	pingIdLock sync.Mutex
-	pingId     uint32
-	pingChans  map[uint32]chan error
+	// pingLock protects pingChans and pingId
+	pingLock  sync.Mutex
+	pingId    uint32
+	pingChans map[uint32]chan error

 	shutdownLock sync.Mutex
 	shutdownChan chan error
@@ -274,16 +275,20 @@ func NewConnection(conn net.Conn, server bool) (*Connection, error) {
 // returns the response time
 func (s *Connection) Ping() (time.Duration, error) {
 	pid := s.pingId
-	s.pingIdLock.Lock()
+	s.pingLock.Lock()
 	if s.pingId > 0x7ffffffe {
 		s.pingId = s.pingId - 0x7ffffffe
 	} else {
 		s.pingId = s.pingId + 2
 	}
-	s.pingIdLock.Unlock()
 	pingChan := make(chan error)
 	s.pingChans[pid] = pingChan
-	defer delete(s.pingChans, pid)
+	s.pingLock.Unlock()
+	defer func() {
+		s.pingLock.Lock()
+		delete(s.pingChans, pid)
+		s.pingLock.Unlock()
+	}()

 	frame := &spdy.PingFrame{Id: pid}
 	startTime := time.Now()
@@ -612,10 +617,14 @@ func (s *Connection) handleDataFrame(frame *spdy.DataFrame) error {
 }

 func (s *Connection) handlePingFrame(frame *spdy.PingFrame) error {
-	if s.pingId&0x01 != frame.Id&0x01 {
+	s.pingLock.Lock()
+	pingId := s.pingId
+	pingChan, pingOk := s.pingChans[frame.Id]
+	s.pingLock.Unlock()
+
+	if pingId&0x01 != frame.Id&0x01 {
 		return s.framer.WriteFrame(frame)
 	}
-	pingChan, pingOk := s.pingChans[frame.Id]
 	if pingOk {
 		close(pingChan)
 	}
@@ -703,7 +712,9 @@ func (s *Connection) shutdown(closeTimeout time.Duration) {

 	var timeout <-chan time.Time
 	if closeTimeout > time.Duration(0) {
-		timeout = time.After(closeTimeout)
+		timer := time.NewTimer(closeTimeout)
+		defer timer.Stop()
+		timeout = timer.C
 	}
 	streamsClosed := make(chan bool)

@@ -730,17 +741,23 @@ func (s *Connection) shutdown(closeTimeout time.Duration) {
 	}

 	if err != nil {
-		duration := 10 * time.Minute
-		time.AfterFunc(duration, func() {
-			select {
-			case err, ok := <-s.shutdownChan:
-				if ok {
-					debugMessage("Unhandled close error after %s: %s", duration, err)
-				}
-			default:
-			}
-		})
-		s.shutdownChan <- err
+		// default to 1 second
+		duration := time.Second
+		// if a closeTimeout was given, use that, clipped to 1s-10m
+		if closeTimeout > time.Second {
+			duration = closeTimeout
+		}
+		if duration > 10*time.Minute {
+			duration = 10 * time.Minute
+		}
+		timer := time.NewTimer(duration)
+		defer timer.Stop()
+		select {
+		case s.shutdownChan <- err:
+			// error was handled
+		case <-timer.C:
+			debugMessage("Unhandled close error after %s: %s", duration, err)
+		}
 	}
 	close(s.shutdownChan)
 }
@@ -799,7 +816,9 @@ func (s *Connection) CloseWait() error {
 func (s *Connection) Wait(waitTimeout time.Duration) error {
 	var timeout <-chan time.Time
 	if waitTimeout > time.Duration(0) {
-		timeout = time.After(waitTimeout)
+		timer := time.NewTimer(waitTimeout)
+		defer timer.Stop()
+		timeout = timer.C
 	}

 	select {

diff --git a/vendor/github.com/moby/spdystream/stream.go b/vendor/github.com/moby/spdystream/stream.go
index 404e3c02dfac3..171c1e9e33114 100644
--- a/vendor/github.com/moby/spdystream/stream.go
+++ b/vendor/github.com/moby/spdystream/stream.go
@@ -305,6 +305,8 @@ func (s *Stream) Identifier() uint32 {
 // IsFinished returns whether the stream has finished
 // sending data
 func (s *Stream) IsFinished() bool {
+	s.finishLock.Lock()
+	defer s.finishLock.Unlock()
 	return s.finished
 }

diff --git a/vendor/modules.txt b/vendor/modules.txt
index dc8783e8847e6..7d5b5a65185e2 100644
--- a/vendor/modules.txt
+++ b/vendor/modules.txt
@@ -354,7 +354,7 @@ github.com/mistifyio/go-zfs/v3
 # github.com/moby/locker v1.0.1
 ## explicit; go 1.13
 github.com/moby/locker
-# github.com/moby/spdystream v0.2.0
+# github.com/moby/spdystream v0.5.0
 ## explicit; go 1.13
 github.com/moby/spdystream
 github.com/moby/spdystream/spdy
PATCH

# Verify the patch was applied
grep -q "github.com/moby/spdystream v0.5.0" go.mod && echo "Patch applied successfully"

# Update vendor directory
go mod vendor
