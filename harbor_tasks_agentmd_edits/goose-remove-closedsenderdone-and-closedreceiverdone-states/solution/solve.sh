#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied
if grep -q 'SndWait.*OfferState' model/channel/channel.go 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the channel state refactor patch
git apply - <<'PATCH'
diff --git a/model/channel/channel.go b/model/channel/channel.go
index 69bf2184..fdc55a47 100644
--- a/model/channel/channel.go
+++ b/model/channel/channel.go
@@ -9,12 +9,13 @@ import (
 type OfferState uint64

 const (
-	// Only idle and closed used for buffered channels.
-	idle OfferState = 0
-	// v = nil means receiver is making offer, v non-nil means sender is making offer
-	offer    OfferState = 1
-	accepted OfferState = 2
-	closed   OfferState = 3
+	Buffered OfferState = 0
+	Idle     OfferState = 1
+	SndWait  OfferState = 2
+	RcvWait  OfferState = 3
+	SndDone  OfferState = 4
+	RcvDone  OfferState = 5
+	Closed   OfferState = 6
 )

 type Channel[T any] struct {
@@ -25,16 +26,20 @@ type Channel[T any] struct {
 	cap    uint64

 	// Value only used for unbuffered channels
-	v *T
+	v T
 }

 // buffer_size = 0 is an unbuffered channel
 func NewChannelRef[T any](buffer_size uint64) *Channel[T] {
+	local_state := Idle
+	if buffer_size > 0 {
+		local_state = Buffered
+	}
 	return &Channel[T]{
 		buffer: make([]T, 0),
 		lock:   new(sync.Mutex),
 		cap:    buffer_size,
-		state:  idle,
+		state:  local_state,
 	}
 }

@@ -43,20 +48,14 @@ func NewChannelRef[T any](buffer_size uint64) *Channel[T] {
 // is equivalent to:
 //
 // c <- val
-func (c *Channel[T]) Send(val T) {
+func (c *Channel[T]) Send(v T) {
 	if c == nil {
 		// Block forever
 		for {
 		}
 	}
-
-	// Create a send case for this channel
-	sendCase := NewSendCase(c, val)
-
-	// Run a blocking select with just this one case
-	// This will block until the send succeeds
-	Select1(sendCase, true)
-	return
+	for !c.TrySend(v, true) {
+	}
 }

 // Equivalent to:
@@ -64,21 +63,19 @@ func (c *Channel[T]) Send(val T) {
 // Notably, this requires the user to consume the ok bool which is not actually required with Go
 // channels. This should be able to be solved by adding an overload wrapper that discards the ok
 // bool.
+
 func (c *Channel[T]) Receive() (T, bool) {
 	if c == nil {
 		// Block forever
 		for {
 		}
 	}
-
-	// Create a receive case for this channel
-	recvCase := NewRecvCase(c)
-
-	// Run a blocking select with just this one case
-	// This will block until the receive succeeds
-	Select1(recvCase, true)
-
-	return recvCase.Value, recvCase.Ok
+	for {
+		success, v, ok := c.TryReceive(true)
+		if success {
+			return v, ok
+		}
+	}
 }

 // This is a non-blocking attempt at closing. The only reason close blocks ever is because there
@@ -86,18 +83,19 @@ func (c *Channel[T]) Receive() (T, bool) {
 // the closer must still obtain the channel's lock
 func (c *Channel[T]) TryClose() bool {
 	c.lock.Lock()
-	if c.state == closed {
+	switch c.state {
+	case Closed:
 		panic("close of closed channel")
-	}
+	case Idle, Buffered:
+		c.state = Closed
+		c.lock.Unlock()
+		return true
 	// For unbuffered channels, if there is an exchange in progress, let the exchange complete.
 	// In the runtime channel code the lock is held while this happens.
-	if c.state == idle {
-		c.state = closed
+	default:
 		c.lock.Unlock()
-		return true
+		return false
 	}
-	c.lock.Unlock()
-	return false
 }

 // c.Close()
@@ -109,9 +107,7 @@ func (c *Channel[T]) Close() {
 	if c == nil {
 		panic("close of nil channel")
 	}
-	var done bool = false
-	for !done {
-		done = c.TryClose()
+	for !c.TryClose() {
 	}
 }

@@ -127,162 +123,128 @@ func (c *Channel[T]) ReceiveDiscardOk() T {
 	return return_val
 }

-// If there is a value available in the buffer, consume it, otherwise, don't select.
-func (c *Channel[T]) BufferedTryReceive() (bool, T, bool) {
-	c.lock.Lock()
-	var v T
-	if len(c.buffer) > 0 {
-		val_copy := c.buffer[0]
-		c.buffer = c.buffer[1:]
-		c.lock.Unlock()
-		return true, val_copy, true
-	}
-	if c.state == closed {
-		c.lock.Unlock()
-		return true, v, false
-	}
-	c.lock.Unlock()
-	return false, v, true
-}
-
-func (c *Channel[T]) UnbufferedTryReceive(blocking bool) (bool, T, bool) {
+// Non-blocking receive function used for select statements.
+// The blocking parameter here is used to determine whether or not we will make an offer to a
+// waiting sender. If true, we will make an offer since blocking receive is modeled as a for loop
+// around nonblocking TryReceive. If false, we don't make an offer since we don't need to match
+// with another non-blocking send.
+func (c *Channel[T]) TryReceive(blocking bool) (bool, T, bool) {
 	var local_val T
 	// First critical section: determine state and get value if sender is ready
 	c.lock.Lock()
-	if c.state == closed {
-		c.lock.Unlock()
-		return true, local_val, false
-	}
-	// Sender is making an offer, complete it
-	if c.state == offer && c.v != nil {
-		local_val = *c.v
-		c.state = accepted
-		c.lock.Unlock()
-		return true, local_val, true
-	}
-
-	// Channel idle, we can make an offer
-	if c.state == idle && blocking {
-		c.state = offer
-		c.lock.Unlock()
-		c.lock.Lock()
-		if c.state == closed {
+	switch c.state {
+	case Buffered:
+		var v T
+		if len(c.buffer) > 0 {
+			val_copy := c.buffer[0]
+			c.buffer = c.buffer[1:]
 			c.lock.Unlock()
-			return true, local_val, false
+			return true, val_copy, true
 		}
-		// Offer wasn't accepted in time, rescind it.
-		if c.state == offer {
-			c.state = idle
+		c.lock.Unlock()
+		return false, v, true
+	case Closed:
+		// For a buffered channel, we drain the buffer before returning ok=false.
+		if len(c.buffer) > 0 {
+			val_copy := c.buffer[0]
+			c.buffer = c.buffer[1:]
 			c.lock.Unlock()
-			return false, local_val, true
+			return true, val_copy, true
 		}
-		// Offer was accepted, complete the exchange.
-		if c.state == accepted {
-			c.state = idle
-			local_val = *c.v
-			c.v = nil
+		c.lock.Unlock()
+		return true, local_val, false
+	// Sender is making an offer, accept it
+	case SndWait:
+		local_val = c.v
+		c.state = RcvDone
+		c.lock.Unlock()
+		return true, local_val, true
+	case Idle:
+		if blocking {
+			c.state = RcvWait
 			c.lock.Unlock()
-			return true, local_val, true
+			c.lock.Lock()
+			switch c.state {
+			// Offer wasn't accepted in time, rescind it.
+			case RcvWait:
+				c.state = Idle
+				c.lock.Unlock()
+				return false, local_val, true
+			// Offer was accepted, reset channel.
+			case SndDone:
+				c.state = Idle
+				local_val = c.v
+				c.lock.Unlock()
+				return true, local_val, true
+			default:
+				// The protocol does not allow interference when an offer is outgoing.
+				panic("not supposed to be here!")
+			}
 		}
-		// Cases should be exhaustive which is non-obvious here, since close can rescind the offer
-		// for us but other receivers cannot.
-		panic("not supposed to be here!")
-	}
-	// If another exchange is in progress we'll try again unless we are nonblocking.
-	if c.state == accepted || c.state == offer || !blocking {
+		// For nonblocking, we can't make offers, only can complete them.
 		c.lock.Unlock()
 		return false, local_val, true
-	}
-	// We should be exhaustively handling these cases but Go wants a return everywhere
-	panic("not supposed to be here!")
-}
-
-// Non-blocking receive function used for select statements. Blocking receive is modeled as
-// a single blocking select statement which amounts to a for loop until selected.
-// The blocking parameter here is used to determine whether or not we will make an offer to a
-// waiting sender. If true, we will make an offer since blocking receive is modeled as a for loop
-// around nonblocking TryReceive. If false, we don't make an item we don't need to match
-// with another non-blocking send.
-func (c *Channel[T]) TryReceive(blocking bool) (bool, T, bool) {
-	if c.cap > 0 {
-		return c.BufferedTryReceive()
-	} else {
-		return c.UnbufferedTryReceive(blocking)
+	// An exchange is in progress that we can't participate in.
+	default:
+		c.lock.Unlock()
+		return false, local_val, true
 	}
 }

-func (c *Channel[T]) UnbufferedTrySend(val T, blocking bool) bool {
+// Non-Blocking send operation for select statements. Blocking send and blocking select
+// statements simply call this in a for loop until it returns true.
+func (c *Channel[T]) TrySend(val T, blocking bool) bool {
 	c.lock.Lock()
-	if c.state == closed {
+	switch c.state {
+	case Closed:
 		panic("send on closed channel")
-	}
-	// Receiver waiting, complete exchange.
-	if c.state == offer && c.v == nil {
-		c.v = new(T)
-		c.state = accepted
-		*c.v = val
+	case Buffered:
+		// If we have room, buffer our value
+		if len(c.buffer) < int(c.cap) {
+			c.buffer = append(c.buffer, val)
+			c.lock.Unlock()
+			return true
+		}
 		c.lock.Unlock()
-		return true
-	}
-	// No exchange in progress, make an offer.
-	// Make an offer only if blocking.
-	if c.state == idle && blocking {
-		c.v = new(T)
-		c.state = offer
-		// Save the value in case the receiver completes the exchange.
-		*c.v = val
+		return false
+	case RcvWait:
+		// Receiver offers, accept offer.
+		c.state = SndDone
+		c.v = val
 		c.lock.Unlock()
-		c.lock.Lock()
-		// Receiver accepts, reset the channel.
-		if c.state == accepted {
-			c.state = idle
-			c.v = nil
+		return true
+	case Idle:
+		// Make an offer only if blocking.
+		if blocking {
+			c.state = SndWait
+			// Save the value in case the receiver completes the exchange.
+			c.v = val
 			c.lock.Unlock()
-			return true
-		}
-		// Offer still stands, rescind it.
-		if c.state == offer {
-			c.state = idle
-			c.v = nil
-			c.lock.Unlock()
-			return false
+			c.lock.Lock()
+			switch c.state {
+			// Receiver accepts, reset the channel.
+			case RcvDone:
+				c.state = Idle
+				c.lock.Unlock()
+				return true
+			// Offer still stands, rescind it.
+			case SndWait:
+				c.state = Idle
+				c.lock.Unlock()
+				return false
+			// This protocol doesn't work if other parties can cancel the exchange.
+			default:
+				panic("Invalid state transition with open receive offer")
+			}
 		}
-		// This protocol doesn't work if other parties can cancel the exchange.
-		panic("Invalid state transition with open receive offer")
-	}
-	c.lock.Unlock()
-	return false
-}
-
-// If the buffer has free space, push our value.
-func (c *Channel[T]) BufferedTrySend(val T) bool {
-	c.lock.Lock()
-	if c.state == closed {
-		panic("send on closed channel")
-	}
-
-	// If we have room, buffer our value
-	if len(c.buffer) < int(c.cap) {
-		c.buffer = append(c.buffer, val)
+		// Nonblocking sends can't make offers, only can accept them.
 		c.lock.Unlock()
-		return true
+		return false
+	// An exchange is in progress that we can't participate in.
+	default:
+		c.lock.Unlock()
+		return false
 	}
-	c.lock.Unlock()
-	return false
-}
-
-// Non-Blocking send operation for select statements. Blocking send and blocking select
-// statements simply call this in a for loop until it returns true.
-func (c *Channel[T]) TrySend(val T, blocking bool) bool {
-
-	sendResult := false
-	// Buffered channel:
-	if c.cap != 0 {
-		sendResult = c.BufferedTrySend(val)
-	} else {
-		sendResult = c.UnbufferedTrySend(val, blocking)
-	}
-	return sendResult
 }

 // c.Len()
PATCH

echo "Patch applied successfully."
