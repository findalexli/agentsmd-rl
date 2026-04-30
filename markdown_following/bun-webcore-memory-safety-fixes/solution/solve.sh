#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotency check: if ThreadSafeWeakPtr is already in BroadcastChannel.cpp, patch was applied
if grep -q 'ThreadSafeWeakPtr<BroadcastChannel>' src/bun.js/bindings/webcore/BroadcastChannel.cpp 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/webcore/BroadcastChannel.cpp b/src/bun.js/bindings/webcore/BroadcastChannel.cpp
index 9302f6554d6..6312fbae1c6 100644
--- a/src/bun.js/bindings/webcore/BroadcastChannel.cpp
+++ b/src/bun.js/bindings/webcore/BroadcastChannel.cpp
@@ -54,9 +54,9 @@ namespace WebCore {
 WTF_MAKE_TZONE_ALLOCATED_IMPL(BroadcastChannel);

 static Lock allBroadcastChannelsLock;
-static UncheckedKeyHashMap<BroadcastChannelIdentifier, BroadcastChannel*>& allBroadcastChannels() WTF_REQUIRES_LOCK(allBroadcastChannelsLock)
+static UncheckedKeyHashMap<BroadcastChannelIdentifier, ThreadSafeWeakPtr<BroadcastChannel>>& allBroadcastChannels() WTF_REQUIRES_LOCK(allBroadcastChannelsLock)
 {
-    static NeverDestroyed<UncheckedKeyHashMap<BroadcastChannelIdentifier, BroadcastChannel*>> map;
+    static NeverDestroyed<UncheckedKeyHashMap<BroadcastChannelIdentifier, ThreadSafeWeakPtr<BroadcastChannel>>> map;
     return map;
 }

@@ -165,7 +165,7 @@ BroadcastChannel::BroadcastChannel(ScriptExecutionContext& context, const String
 {
     {
         Locker locker { allBroadcastChannelsLock };
-        allBroadcastChannels().add(m_mainThreadBridge->identifier(), this);
+        allBroadcastChannels().add(m_mainThreadBridge->identifier(), *this);
     }
     m_mainThreadBridge->registerChannel(context);
     jsRef(context.jsGlobalObject());
@@ -241,7 +241,7 @@ void BroadcastChannel::dispatchMessageTo(BroadcastChannelIdentifier channelIdent
         RefPtr<BroadcastChannel> channel;
         {
             Locker locker { allBroadcastChannelsLock };
-            channel = allBroadcastChannels().get(channelIdentifier);
+            channel = allBroadcastChannels().get(channelIdentifier).get();
         }
         if (channel)
             channel->dispatchMessage(WTF::move(message));
diff --git a/src/bun.js/bindings/webcore/EventListenerMap.cpp b/src/bun.js/bindings/webcore/EventListenerMap.cpp
index 468b4e00ba0..3636f605ea5 100644
--- a/src/bun.js/bindings/webcore/EventListenerMap.cpp
+++ b/src/bun.js/bindings/webcore/EventListenerMap.cpp
@@ -73,6 +73,7 @@ bool EventListenerMap::containsActive(const AtomString& eventType) const

 void EventListenerMap::clear()
 {
+    releaseAssertOrSetThreadUID();
     Locker locker { m_lock };

     for (auto& entry : m_entries) {
@@ -102,6 +103,7 @@ static inline size_t findListener(const EventListenerVector& listeners, EventLis

 void EventListenerMap::replace(const AtomString& eventType, EventListener& oldListener, Ref<EventListener>&& newListener, const RegisteredEventListener::Options& options)
 {
+    releaseAssertOrSetThreadUID();
     Locker locker { m_lock };

     auto* listeners = find(eventType);
@@ -115,6 +117,7 @@ void EventListenerMap::replace(const AtomString& eventType, EventListener& oldLi

 bool EventListenerMap::add(const AtomString& eventType, Ref<EventListener>&& listener, const RegisteredEventListener::Options& options)
 {
+    releaseAssertOrSetThreadUID();
     Locker locker { m_lock };

     if (auto* listeners = find(eventType)) {
@@ -141,6 +144,7 @@ static bool removeListenerFromVector(EventListenerVector& listeners, EventListen

 bool EventListenerMap::remove(const AtomString& eventType, EventListener& listener, bool useCapture)
 {
+    releaseAssertOrSetThreadUID();
     Locker locker { m_lock };

     for (unsigned i = 0; i < m_entries.size(); ++i) {
@@ -179,6 +183,7 @@ static void removeFirstListenerCreatedFromMarkup(EventListenerVector& listenerVe

 void EventListenerMap::removeFirstEventListenerCreatedFromMarkup(const AtomString& eventType)
 {
+    releaseAssertOrSetThreadUID();
     Locker locker { m_lock };

     for (unsigned i = 0; i < m_entries.size(); ++i) {
diff --git a/src/bun.js/bindings/webcore/EventListenerMap.h b/src/bun.js/bindings/webcore/EventListenerMap.h
index 690afd133cc..b255ca81dd6 100644
--- a/src/bun.js/bindings/webcore/EventListenerMap.h
+++ b/src/bun.js/bindings/webcore/EventListenerMap.h
@@ -35,8 +35,10 @@
 #include "RegisteredEventListener.h"
 #include <atomic>
 #include <memory>
+#include <wtf/Assertions.h>
 #include <wtf/Forward.h>
 #include <wtf/Lock.h>
+#include <wtf/Threading.h>
 #include <wtf/text/AtomString.h>

 namespace WebCore {
@@ -70,8 +72,21 @@ class EventListenerMap {
     Lock& lock() { return m_lock; }

 private:
+    void releaseAssertOrSetThreadUID()
+    {
+        if (!m_threadUID) {
+            ASSERT(!Thread::mayBeGCThread());
+            m_threadUID = Thread::currentSingleton().uid();
+            return;
+        }
+        if (m_threadUID == Thread::currentSingleton().uid()) [[likely]]
+            return;
+        RELEASE_ASSERT(Thread::mayBeGCThread());
+    }
+
     Vector<std::pair<AtomString, EventListenerVector>, 0, CrashOnOverflow, 4> m_entries;
     Lock m_lock;
+    uint32_t m_threadUID { 0 };
 };

 template<typename Visitor>
diff --git a/src/bun.js/bindings/webcore/JSAbortController.cpp b/src/bun.js/bindings/webcore/JSAbortController.cpp
index b488219e976..35bd2867f17 100644
--- a/src/bun.js/bindings/webcore/JSAbortController.cpp
+++ b/src/bun.js/bindings/webcore/JSAbortController.cpp
@@ -242,6 +242,7 @@ void JSAbortController::visitChildrenImpl(JSCell* cell, Visitor& visitor)
     ASSERT_GC_OBJECT_INHERITS(thisObject, info());
     Base::visitChildren(thisObject, visitor);
     addWebCoreOpaqueRoot(visitor, thisObject->wrapped().opaqueRoot());
+    thisObject->wrapped().signal().reason().visit(visitor);
 }

 DEFINE_VISIT_CHILDREN(JSAbortController);
diff --git a/src/bun.js/bindings/webcore/MessagePortChannel.cpp b/src/bun.js/bindings/webcore/MessagePortChannel.cpp
index ba984626f45..a6e6680f5ed 100644
--- a/src/bun.js/bindings/webcore/MessagePortChannel.cpp
+++ b/src/bun.js/bindings/webcore/MessagePortChannel.cpp
@@ -121,6 +121,9 @@ bool MessagePortChannel::postMessageToRemote(MessageWithMessagePorts&& message,
     ASSERT(remoteTarget == m_ports[0] || remoteTarget == m_ports[1]);
     size_t i = remoteTarget == m_ports[0] ? 0 : 1;

+    if (m_isClosed[i])
+        return false;
+
     m_pendingMessages[i].append(WTF::move(message));
     // LOG(MessagePorts, "MessagePortChannel %s (%p) now has %zu messages pending on port %s", logString().utf8().data(), this, m_pendingMessages[i].size(), remoteTarget.logString().utf8().data());

PATCH
echo "- WebCore fixes applied: MessagePortChannel memory leak, JSAbortController signal reason, BroadcastChannel use-after-free, EventListenerMap thread affinity." >> CLAUDE.md
