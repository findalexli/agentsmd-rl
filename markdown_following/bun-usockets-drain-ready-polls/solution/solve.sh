#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'us_internal_drain_ready_polls' packages/bun-usockets/src/eventing/epoll_kqueue.c 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/packages/bun-usockets/src/eventing/epoll_kqueue.c b/packages/bun-usockets/src/eventing/epoll_kqueue.c
index 6c2bdc4967b..462203a98af 100644
--- a/packages/bun-usockets/src/eventing/epoll_kqueue.c
+++ b/packages/bun-usockets/src/eventing/epoll_kqueue.c
@@ -285,6 +285,30 @@ static void us_internal_dispatch_ready_polls(struct us_loop_t *loop) {
 #endif
 }

+/* If the kernel filled our entire buffer, more events are likely already queued.
+ * Re-poll non-blocking and dispatch again before running pre/post callbacks, so a
+ * single tick covers all pending I/O instead of one 1024-event slice per roundtrip.
+ * Conditioned on saturation and capped at 48 iterations — matches libuv's uv__io_poll
+ * (vendor/libuv/src/unix/linux.c:1387,1590 and kqueue.c:253,451). */
+static void us_internal_drain_ready_polls(struct us_loop_t *loop) {
+    int drain_count = 48;
+    while (UNLIKELY(loop->num_ready_polls == LIBUS_MAX_READY_POLLS) && --drain_count != 0 && loop->num_polls > 0) {
+#ifdef LIBUS_USE_EPOLL
+        static const struct timespec zero = {0, 0};
+        loop->num_ready_polls = bun_epoll_pwait2(loop->fd, loop->ready_polls, LIBUS_MAX_READY_POLLS, &zero);
+#else
+        do {
+            loop->num_ready_polls = kevent64(loop->fd, NULL, 0, loop->ready_polls, LIBUS_MAX_READY_POLLS, KEVENT_FLAG_IMMEDIATE, NULL);
+        } while (IS_EINTR(loop->num_ready_polls));
+#endif
+        if (loop->num_ready_polls <= 0) {
+            loop->num_ready_polls = 0;
+            break;
+        }
+        us_internal_dispatch_ready_polls(loop);
+    }
+}
+
 void us_loop_run(struct us_loop_t *loop) {
     us_loop_integrate(loop);

@@ -295,14 +319,15 @@ void us_loop_run(struct us_loop_t *loop) {

         /* Fetch ready polls */
 #ifdef LIBUS_USE_EPOLL
-        loop->num_ready_polls = bun_epoll_pwait2(loop->fd, loop->ready_polls, 1024, NULL);
+        loop->num_ready_polls = bun_epoll_pwait2(loop->fd, loop->ready_polls, LIBUS_MAX_READY_POLLS, NULL);
 #else
         do {
-            loop->num_ready_polls = kevent64(loop->fd, NULL, 0, loop->ready_polls, 1024, 0, NULL);
+            loop->num_ready_polls = kevent64(loop->fd, NULL, 0, loop->ready_polls, LIBUS_MAX_READY_POLLS, 0, NULL);
         } while (IS_EINTR(loop->num_ready_polls));
 #endif

         us_internal_dispatch_ready_polls(loop);
+        us_internal_drain_ready_polls(loop);

         /* Emit post callback */
         us_internal_loop_post(loop);
@@ -336,10 +361,10 @@ void us_loop_run_bun_tick(struct us_loop_t *loop, const struct timespec* timeout
     /* A zero timespec already has a fast path in ep_poll (fs/eventpoll.c):
      * it sets timed_out=1 (line 1952) and returns before any scheduler
      * interaction (line 1975). No equivalent of KEVENT_FLAG_IMMEDIATE needed. */
-    loop->num_ready_polls = bun_epoll_pwait2(loop->fd, loop->ready_polls, 1024, timeout);
+    loop->num_ready_polls = bun_epoll_pwait2(loop->fd, loop->ready_polls, LIBUS_MAX_READY_POLLS, timeout);
 #else
     do {
-        loop->num_ready_polls = kevent64(loop->fd, NULL, 0, loop->ready_polls, 1024,
+        loop->num_ready_polls = kevent64(loop->fd, NULL, 0, loop->ready_polls, LIBUS_MAX_READY_POLLS,
             /* When we won't idle (pending wakeups or zero timeout), use KEVENT_FLAG_IMMEDIATE.
              * In XNU's kqueue_scan (bsd/kern/kern_event.c):
              *  - KEVENT_FLAG_IMMEDIATE: returns immediately after kqueue_process() (line 8031)
@@ -351,8 +376,8 @@ void us_loop_run_bun_tick(struct us_loop_t *loop, const struct timespec* timeout
     } while (IS_EINTR(loop->num_ready_polls));
 #endif

-
     us_internal_dispatch_ready_polls(loop);
+    us_internal_drain_ready_polls(loop);

     /* Emit post callback */
     us_internal_loop_post(loop);

PATCH

echo "Patch applied successfully."
