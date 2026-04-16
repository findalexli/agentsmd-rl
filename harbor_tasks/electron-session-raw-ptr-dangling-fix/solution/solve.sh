#!/bin/bash
set -e

cd /workspace/electron

# Apply the gold patch to fix dangling raw_ptr
git apply <<'PATCH'
diff --git a/shell/browser/api/electron_api_session.cc b/shell/browser/api/electron_api_session.cc
index c0a92b913d2cd..79306dd35b4a2 100644
--- a/shell/browser/api/electron_api_session.cc
+++ b/shell/browser/api/electron_api_session.cc
@@ -550,8 +550,7 @@ gin::WrapperInfo Session::kWrapperInfo = {{gin::kEmbedderNativeGin},
 Session::Session(v8::Isolate* isolate, ElectronBrowserContext* browser_context)
     : isolate_(isolate),
       network_emulation_token_(base::UnguessableToken::Create()),
-      browser_context_{
-          raw_ref<ElectronBrowserContext>::from_ptr(browser_context)} {
+      browser_context_{browser_context} {
   gin::PerIsolateData* data = gin::PerIsolateData::From(isolate);
   data->AddDisposeObserver(this);
   // Observe DownloadManager to get download notifications.
@@ -584,16 +583,21 @@ Session::~Session() {
 }

 void Session::Dispose() {
-  if (keep_alive_) {
-    browser_context()->GetDownloadManager()->RemoveObserver(this);
+  if (!keep_alive_)
+    return;
+
+  ElectronBrowserContext* const browser_context = this->browser_context();
+  if (!browser_context)
+    return;
+
+  browser_context->GetDownloadManager()->RemoveObserver(this);

 #if BUILDFLAG(ENABLE_BUILTIN_SPELLCHECKER)
-    if (auto* service =
-            SpellcheckServiceFactory::GetForContext(browser_context())) {
-      service->SetHunspellObserver(nullptr);
-    }
-#endif
+  if (auto* service =
+          SpellcheckServiceFactory::GetForContext(browser_context)) {
+    service->SetHunspellObserver(nullptr);
   }
+#endif
 }

 void Session::OnDownloadCreated(content::DownloadManager* manager,
@@ -1875,6 +1879,7 @@ void Session::OnBeforeMicrotasksRunnerDispose(v8::Isolate* isolate) {
   data->RemoveDisposeObserver(this);
   Dispose();
   weak_factory_.Invalidate();
+  browser_context_ = nullptr;
   keep_alive_.Clear();
 }

diff --git a/shell/browser/api/electron_api_session.h b/shell/browser/api/electron_api_session.h
index f7e672d4add1b..48c209d26c1bf 100644
--- a/shell/browser/api/electron_api_session.h
+++ b/shell/browser/api/electron_api_session.h
@@ -10,7 +10,6 @@
 #include <vector>

 #include "base/memory/raw_ptr.h"
-#include "base/memory/raw_ref.h"
 #include "base/memory/weak_ptr.h"
 #include "base/values.h"
 #include "content/public/browser/download_manager.h"
@@ -103,8 +102,8 @@ class Session final : public gin::Wrappable<Session>,
   Session(v8::Isolate* isolate, ElectronBrowserContext* browser_context);
   ~Session() override;

-  ElectronBrowserContext* browser_context() const {
-    return &browser_context_.get();
+  [[nodiscard]] ElectronBrowserContext* browser_context() const {
+    return browser_context_;
   }

   // gin::Wrappable
@@ -225,7 +224,7 @@ class Session final : public gin::Wrappable<Session>,
   // The client id to enable the network throttler.
   base::UnguessableToken network_emulation_token_;

-  const raw_ref<ElectronBrowserContext> browser_context_;
+  raw_ptr<ElectronBrowserContext> browser_context_;

   gin::WeakCellFactory<Session> weak_factory_{this};

diff --git a/shell/browser/api/electron_api_web_contents.cc b/shell/browser/api/electron_api_web_contents.cc
index 0e66f025321de..6b31a8246d2e9 100644
--- a/shell/browser/api/electron_api_web_contents.cc
+++ b/shell/browser/api/electron_api_web_contents.cc
@@ -910,14 +910,15 @@ WebContents::WebContents(v8::Isolate* isolate,
     session = Session::FromPartition(isolate, "");
   }
   session_ = session;
+  ElectronBrowserContext* const browser_context = session->browser_context();
+  DCHECK(browser_context != nullptr);

   std::unique_ptr<content::WebContents> web_contents;
   if (is_guest()) {
     scoped_refptr<content::SiteInstance> site_instance =
-        content::SiteInstance::CreateForURL(session->browser_context(),
+        content::SiteInstance::CreateForURL(browser_context,
                                             GURL("chrome-guest://fake-host"));
-    content::WebContents::CreateParams params(session->browser_context(),
-                                              site_instance);
+    content::WebContents::CreateParams params{browser_context, site_instance};
     guest_delegate_ =
         std::make_unique<WebViewGuestDelegate>(embedder_->web_contents(), this);
     params.guest_delegate = guest_delegate_.get();
@@ -945,7 +946,7 @@ WebContents::WebContents(v8::Isolate* isolate,
     SkColor bc = ParseCSSColor(background_color_str).value_or(SK_ColorWHITE);
     bool transparent = bc == SK_ColorTRANSPARENT;

-    content::WebContents::CreateParams params(session->browser_context());
+    content::WebContents::CreateParams params{browser_context};
     auto* view = new OffScreenWebContentsView(
         transparent, offscreen_use_shared_texture_,
         offscreen_shared_texture_pixel_format_, offscreen_device_scale_factor_,
@@ -956,13 +957,13 @@ WebContents::WebContents(v8::Isolate* isolate,
     web_contents = content::WebContents::Create(params);
     view->SetWebContents(web_contents.get());
   } else {
-    content::WebContents::CreateParams params(session->browser_context());
+    content::WebContents::CreateParams params{browser_context};
     params.initially_hidden = !initially_shown;
     web_contents = content::WebContents::Create(params);
   }

-  InitWithSessionAndOptions(isolate, std::move(web_contents),
-                            session->browser_context(), options);
+  InitWithSessionAndOptions(isolate, std::move(web_contents), browser_context,
+                            options);
 }

 void WebContents::InitZoomController(content::WebContents* web_contents,
diff --git a/shell/browser/electron_browser_main_parts.cc b/shell/browser/electron_browser_main_parts.cc
index 7819d4cc9c413..745aa6929b95f 100644
--- a/shell/browser/electron_browser_main_parts.cc
+++ b/shell/browser/electron_browser_main_parts.cc
@@ -626,6 +626,9 @@ void ElectronBrowserMainParts::PostMainMessageLoopRun() {
 #if BUILDFLAG(IS_LINUX)
   ui::OzonePlatform::GetInstance()->PostMainMessageLoopRun();
 #endif
+
+  browser_.reset();
+  js_env_.reset();
 }

 #if !BUILDFLAG(IS_MAC)
diff --git a/shell/common/api/electron_api_url_loader.cc b/shell/common/api/electron_api_url_loader.cc
index 56ba8f50a95be..a5f591989c8d3 100644
--- a/shell/common/api/electron_api_url_loader.cc
+++ b/shell/common/api/electron_api_url_loader.cc
@@ -705,8 +705,10 @@ gin_helper::Handle<SimpleURLLoaderWrapper> SimpleURLLoaderWrapper::Create(
       else  // default session
         session = Session::FromPartition(args->isolate(), "");
     }
-    if (session)
+    if (session) {
       browser_context = session->browser_context();
+      DCHECK(browser_context != nullptr);
+    }
   }

   auto ret = gin_helper::CreateHandle(
diff --git a/spec/cpp-heap-spec.ts b/spec/cpp-heap-spec.ts
index bc36fd828369a..c57b53104b90a 100644
--- a/spec/cpp-heap-spec.ts
+++ b/spec/cpp-heap-spec.ts
@@ -1,5 +1,6 @@
 import { expect } from 'chai';

+import { once } from 'node:events';
 import * as path from 'node:path';

 import { startRemoteControlApp } from './lib/spec-helpers';
@@ -39,6 +40,33 @@ describe('cpp heap', () => {
   });

   describe('session module', () => {
+    it('does not crash on exit with live session wrappers', async () => {
+      const rc = await startRemoteControlApp();
+      await rc.remotely(async () => {
+        const { app, session } = require('electron');
+
+        const sessions = [
+          session.defaultSession,
+          session.fromPartition('cppheap-exit'),
+          session.fromPartition('persist:cppheap-exit-persist')
+        ];
+
+        // We want to test GC on shutdown, so add a global reference
+        // to these sessions to prevent pre-shutdown GC.
+        (globalThis as any).sessionRefs = sessions;
+
+        // We want to test CppGC-traced references during shutdown.
+        // The CppGC-managed cookies will do that; but since they're
+        // lazy-created, access them here to ensure they're live.
+        sessions.forEach(ses => ses.cookies);
+
+        setTimeout(() => app.quit());
+      });
+
+      const [code] = await once(rc.process, 'exit');
+      expect(code).to.equal(0);
+    });
+
     it('should record as node in heap snapshot', async () => {
       const { remotely } = await startRemoteControlApp(['--expose-internals']);
       const result = await remotely(async (heap: string, snapshotHelper: string) => {
PATCH

echo "Patch applied successfully"
