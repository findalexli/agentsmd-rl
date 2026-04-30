#!/bin/bash
set -e

cd /workspace/electron

# Check if already patched
if grep -q "requesting_frame->GetLastCommittedOrigin().GetURL()" shell/browser/web_contents_permission_helper.cc; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/shell/browser/api/electron_api_web_contents.cc b/shell/browser/api/electron_api_web_contents.cc
index 378ab0a4a8283..6ff7f1a2cf769 100644
--- a/shell/browser/api/electron_api_web_contents.cc
+++ b/shell/browser/api/electron_api_web_contents.cc
@@ -1739,7 +1739,8 @@ bool WebContents::CheckMediaAccessPermission(
       content::WebContents::FromRenderFrameHost(render_frame_host);
   auto* permission_helper =
       WebContentsPermissionHelper::FromWebContents(web_contents);
-  return permission_helper->CheckMediaAccessPermission(security_origin, type);
+  return permission_helper->CheckMediaAccessPermission(render_frame_host,
+                                                       security_origin, type);
 }

 void WebContents::RequestMediaAccessPermission(
diff --git a/shell/browser/serial/electron_serial_delegate.cc b/shell/browser/serial/electron_serial_delegate.cc
index fb169485156a9..df8f68f0a0ed4 100644
--- a/shell/browser/serial/electron_serial_delegate.cc
+++ b/shell/browser/serial/electron_serial_delegate.cc
@@ -51,8 +51,7 @@ bool ElectronSerialDelegate::CanRequestPortPermission(
   auto* web_contents = content::WebContents::FromRenderFrameHost(frame);
   auto* permission_helper =
       WebContentsPermissionHelper::FromWebContents(web_contents);
-  return permission_helper->CheckSerialAccessPermission(
-      frame->GetLastCommittedOrigin());
+  return permission_helper->CheckSerialAccessPermission(frame);
 }

 bool ElectronSerialDelegate::HasPortPermission(
diff --git a/shell/browser/web_contents_permission_helper.cc b/shell/browser/web_contents_permission_helper.cc
index 23332fe5554e7..ea4a4f74f2913 100644
--- a/shell/browser/web_contents_permission_helper.cc
+++ b/shell/browser/web_contents_permission_helper.cc
@@ -228,14 +228,14 @@ void WebContentsPermissionHelper::RequestPermission(
 }

 bool WebContentsPermissionHelper::CheckPermission(
+    content::RenderFrameHost* requesting_frame,
     blink::PermissionType permission,
     base::DictValue details) const {
-  auto* rfh = web_contents_->GetPrimaryMainFrame();
   auto* permission_manager = static_cast<ElectronPermissionManager*>(
       web_contents_->GetBrowserContext()->GetPermissionControllerDelegate());
-  auto origin = web_contents_->GetLastCommittedURL();
-  return permission_manager->CheckPermissionWithDetails(permission, rfh, origin,
-                                                        std::move(details));
+  auto origin = requesting_frame->GetLastCommittedOrigin().GetURL();
+  return permission_manager->CheckPermissionWithDetails(
+      permission, requesting_frame, origin, std::move(details));
 }

 void WebContentsPermissionHelper::RequestFullscreenPermission(
@@ -313,6 +313,7 @@ void WebContentsPermissionHelper::RequestOpenExternalPermission(
 }

 bool WebContentsPermissionHelper::CheckMediaAccessPermission(
+    content::RenderFrameHost* requesting_frame,
     const url::Origin& security_origin,
     blink::mojom::MediaStreamType type) const {
   base::DictValue details;
@@ -321,14 +322,16 @@ bool WebContentsPermissionHelper::CheckMediaAccessPermission(
   auto blink_type = type == blink::mojom::MediaStreamType::DEVICE_AUDIO_CAPTURE
                         ? blink::PermissionType::AUDIO_CAPTURE
                         : blink::PermissionType::VIDEO_CAPTURE;
-  return CheckPermission(blink_type, std::move(details));
+  return CheckPermission(requesting_frame, blink_type, std::move(details));
 }

 bool WebContentsPermissionHelper::CheckSerialAccessPermission(
-    const url::Origin& embedding_origin) const {
+    content::RenderFrameHost* requesting_frame) const {
   base::DictValue details;
-  details.Set("securityOrigin", embedding_origin.GetURL().spec());
-  return CheckPermission(blink::PermissionType::SERIAL, std::move(details));
+  details.Set("securityOrigin",
+              requesting_frame->GetLastCommittedOrigin().GetURL().spec());
+  return CheckPermission(requesting_frame, blink::PermissionType::SERIAL,
+                         std::move(details));
 }

 WEB_CONTENTS_USER_DATA_KEY_IMPL(WebContentsPermissionHelper);
diff --git a/shell/browser/web_contents_permission_helper.h b/shell/browser/web_contents_permission_helper.h
index e98189bf8fb63..bde8c4a665256 100644
--- a/shell/browser/web_contents_permission_helper.h
+++ b/shell/browser/web_contents_permission_helper.h
@@ -47,9 +47,11 @@ class WebContentsPermissionHelper
                                      const GURL& url);

   // Synchronous Checks
-  bool CheckMediaAccessPermission(const url::Origin& security_origin,
+  bool CheckMediaAccessPermission(content::RenderFrameHost* requesting_frame,
+                                  const url::Origin& security_origin,
                                   blink::mojom::MediaStreamType type) const;
-  bool CheckSerialAccessPermission(const url::Origin& embedding_origin) const;
+  bool CheckSerialAccessPermission(
+      content::RenderFrameHost* requesting_frame) const;

  private:
   explicit WebContentsPermissionHelper(content::WebContents* web_contents);
@@ -61,7 +63,8 @@ class WebContentsPermissionHelper
                          bool user_gesture = false,
                          base::DictValue details = {});

-  bool CheckPermission(blink::PermissionType permission,
+  bool CheckPermission(content::RenderFrameHost* requesting_frame,
+                       blink::PermissionType permission,
                        base::DictValue details) const;

   // TODO(clavin): refactor to use the WebContents provided by the
PATCH

echo "Patch applied successfully"
