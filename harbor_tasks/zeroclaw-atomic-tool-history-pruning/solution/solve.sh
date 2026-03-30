#!/usr/bin/env bash
set -euo pipefail
cd /workspace/zeroclaw

# Apply the gold patch
git apply --whitespace=fix - << 'PATCH'
diff --git a/src/agent/history.rs b/src/agent/history.rs
index 95800e3eab..22932a409e 100644
--- a/src/agent/history.rs
+++ b/src/agent/history.rs
@@ -76,6 +76,8 @@ pub(crate) fn fast_trim_tool_results(
 }

 /// Emergency: drop oldest non-system, non-recent messages from history.
+/// Tool groups (assistant + consecutive tool messages) are dropped
+/// atomically to preserve tool_use/tool_result pairing. See #4810.
 /// Returns number of messages dropped.
 pub(crate) fn emergency_history_trim(
     history: &mut Vec<crate::providers::ChatMessage>,
@@ -87,6 +89,18 @@ pub(crate) fn emergency_history_trim(
     while dropped < target_drop && i < history.len().saturating_sub(keep_recent) {
         if history[i].role == "system" {
             i += 1;
+        } else if history[i].role == "assistant" {
+            // Count following tool messages — drop as atomic group
+            let mut tool_count = 0;
+            while i + 1 + tool_count < history.len().saturating_sub(keep_recent)
+                && history[i + 1 + tool_count].role == "tool"
+            {
+                tool_count += 1;
+            }
+            for _ in 0..=tool_count {
+                history.remove(i);
+                dropped += 1;
+            }
         } else {
             history.remove(i);
             dropped += 1;
diff --git a/src/agent/history_pruner.rs b/src/agent/history_pruner.rs
index 0791373dcb..0e8f643942 100644
--- a/src/agent/history_pruner.rs
+++ b/src/agent/history_pruner.rs
@@ -101,44 +101,79 @@ pub fn prune_history(messages: &mut Vec<ChatMessage>, config: &HistoryPrunerConf

     let mut collapsed_pairs: usize = 0;

-    // Phase 1 – collapse assistant+tool pairs
+    // Phase 1 – collapse assistant+tool groups atomically.
+    // An assistant message followed by one or more consecutive tool messages
+    // forms an atomic group (tool_use + tool_result pairing). Collapsing only
+    // part of the group would orphan tool_use blocks, causing API 400 errors
+    // from providers that enforce pairing (e.g., Anthropic). See #4810.
     if config.collapse_tool_results {
         let mut i = 0;
-        while i + 1 < messages.len() {
+        while i < messages.len() {
             let protected = protected_indices(messages, config.keep_recent);
-            if messages[i].role == "assistant"
-                && messages[i + 1].role == "tool"
-                && !protected[i]
-                && !protected[i + 1]
-            {
-                let tool_content = &messages[i + 1].content;
-                let truncated: String = tool_content.chars().take(100).collect();
-                let summary = format!("[Tool result: {truncated}...]");
-                messages[i] = ChatMessage {
-                    role: "assistant".to_string(),
-                    content: summary,
-                };
-                messages.remove(i + 1);
-                collapsed_pairs += 1;
-            } else {
-                i += 1;
+            if messages[i].role == "assistant" && !protected[i] {
+                // Count consecutive tool messages following this assistant
+                let mut tool_count = 0;
+                while i + 1 + tool_count < messages.len()
+                    && messages[i + 1 + tool_count].role == "tool"
+                    && !protected[i + 1 + tool_count]
+                {
+                    tool_count += 1;
+                }
+                if tool_count > 0 {
+                    let summary =
+                        format!("[Tool exchange: {tool_count} tool call(s) — results collapsed]");
+                    messages[i] = ChatMessage {
+                        role: "assistant".to_string(),
+                        content: summary,
+                    };
+                    for _ in 0..tool_count {
+                        messages.remove(i + 1);
+                    }
+                    collapsed_pairs += tool_count;
+                    continue;
+                }
             }
+            i += 1;
         }
     }

-    // Phase 2 – budget enforcement
+    // Phase 2 – budget enforcement: drop messages to fit token budget.
+    // Tool groups (assistant + consecutive tool messages) are dropped
+    // atomically to preserve tool_use/tool_result pairing. See #4810.
     let mut dropped_messages: usize = 0;
     while estimate_tokens(messages) > config.max_tokens {
         let protected = protected_indices(messages, config.keep_recent);
-        if let Some(idx) = protected
-            .iter()
-            .enumerate()
-            .find(|&(_, &p)| !p)
-            .map(|(i, _)| i)
-        {
-            messages.remove(idx);
+        let mut dropped_any = false;
+        let mut i = 0;
+        while i < messages.len() {
+            if protected[i] {
+                i += 1;
+                continue;
+            }
+            if messages[i].role == "assistant" {
+                // Count following tool messages — drop as atomic group
+                let mut tool_count = 0;
+                while i + 1 + tool_count < messages.len()
+                    && messages[i + 1 + tool_count].role == "tool"
+                {
+                    tool_count += 1;
+                }
+                if tool_count > 0 {
+                    for _ in 0..=tool_count {
+                        messages.remove(i);
+                    }
+                    dropped_messages += 1 + tool_count;
+                    dropped_any = true;
+                    break;
+                }
+            }
+            // Non-tool-group message — safe to drop individually
+            messages.remove(i);
             dropped_messages += 1;
-        } else {
+            dropped_any = true;
+            break;
+        }
+        if !dropped_any {
             break;
         }
     }
PATCH
