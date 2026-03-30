#!/usr/bin/env bash
set -euo pipefail
cd /workspace/zeroclaw

# Apply the gold patch
git apply --whitespace=fix - << 'PATCH'
diff --git a/src/multimodal.rs b/src/multimodal.rs
index ee4e6dd734..4d7cdbefda 100644
--- a/src/multimodal.rs
+++ b/src/multimodal.rs
@@ -121,27 +121,30 @@ pub async fn prepare_messages_for_provider(
     let (max_images, max_image_size_mb) = config.effective_limits();
     let max_bytes = max_image_size_mb.saturating_mul(1024 * 1024);

-    let found_images = count_image_markers(messages);
-    if found_images > max_images {
-        return Err(MultimodalError::TooManyImages {
-            max_images,
-            found: found_images,
-        }
-        .into());
-    }
+    let total_images = count_image_markers(messages);

-    if found_images == 0 {
+    if total_images == 0 {
         return Ok(PreparedMessages {
             messages: messages.to_vec(),
             contains_images: false,
         });
     }

+    // When image count exceeds the limit, strip markers from oldest messages
+    // first so that the most recent (most relevant) images survive. This
+    // prevents conversations from becoming permanently stuck once the
+    // cumulative image count crosses the threshold.
+    let trimmed = if total_images > max_images {
+        trim_old_images(messages, max_images)
+    } else {
+        messages.to_vec()
+    };
+
     let remote_client = build_runtime_proxy_client_with_timeouts("provider.ollama", 30, 10);

-    let mut normalized_messages = Vec::with_capacity(messages.len());
+    let mut normalized_messages = Vec::with_capacity(trimmed.len());
     let mut has_successful_images = false;
-    for message in messages {
+    for message in &trimmed {
         if message.role != "user" {
             normalized_messages.push(message.clone());
             continue;
@@ -200,6 +203,60 @@ pub async fn prepare_messages_for_provider(
     })
 }

+/// Strip image markers from older messages (oldest first) until total image
+/// count is within `max_images`. Keeps the text content of each message.
+fn trim_old_images(messages: &[ChatMessage], max_images: usize) -> Vec<ChatMessage> {
+    // Find which messages (by index) contain images, oldest first.
+    let image_positions: Vec<(usize, usize)> = messages
+        .iter()
+        .enumerate()
+        .filter(|(_, m)| m.role == "user")
+        .filter_map(|(i, m)| {
+            let count = parse_image_markers(&m.content).1.len();
+            if count > 0 {
+                Some((i, count))
+            } else {
+                None
+            }
+        })
+        .collect();
+
+    // Determine how many images to drop (from the oldest messages).
+    let total: usize = image_positions.iter().map(|(_, c)| c).sum();
+    let mut to_drop = total.saturating_sub(max_images);
+
+    // Collect indices of messages whose images should be stripped.
+    let mut strip_indices = std::collections::HashSet::new();
+    for &(idx, count) in &image_positions {
+        if to_drop == 0 {
+            break;
+        }
+        strip_indices.insert(idx);
+        to_drop = to_drop.saturating_sub(count);
+    }
+
+    messages
+        .iter()
+        .enumerate()
+        .map(|(i, m)| {
+            if strip_indices.contains(&i) {
+                let (cleaned, _) = parse_image_markers(&m.content);
+                let text = if cleaned.trim().is_empty() {
+                    "[image removed from history]".to_string()
+                } else {
+                    cleaned
+                };
+                ChatMessage {
+                    role: m.role.clone(),
+                    content: text,
+                }
+            } else {
+                m.clone()
+            }
+        })
+        .collect()
+}
+
 fn compose_multimodal_message(text: &str, data_uris: &[String]) -> String {
     let mut content = String::new();
     let trimmed = text.trim();
PATCH
