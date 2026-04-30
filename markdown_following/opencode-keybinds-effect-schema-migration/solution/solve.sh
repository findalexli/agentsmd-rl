#!/bin/bash
# Apply the gold patch from PR #23227 to the cloned opencode repo.
# Idempotent: if the distinctive marker is already present, skip.
set -euo pipefail

cd /workspace/opencode

DISTINCTIVE='const KeybindsSchema = Schema.Struct({'

if grep -qF "$DISTINCTIVE" packages/opencode/src/config/keybinds.ts 2>/dev/null; then
  echo "solve.sh: gold already applied; skipping"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/opencode/src/config/keybinds.ts b/packages/opencode/src/config/keybinds.ts
index 8a22289d2a7f..a84fc0b37d58 100644
--- a/packages/opencode/src/config/keybinds.ts
+++ b/packages/opencode/src/config/keybinds.ts
@@ -1,166 +1,127 @@
 export * as ConfigKeybinds from "./keybinds"

-import z from "zod"
+import { Effect, Schema } from "effect"
+import type z from "zod"
+import { zod } from "@/util/effect-zod"

-export const Keybinds = z
-  .object({
-    leader: z.string().optional().default("ctrl+x").describe("Leader key for keybind combinations"),
-    app_exit: z.string().optional().default("ctrl+c,ctrl+d,<leader>q").describe("Exit the application"),
-    editor_open: z.string().optional().default("<leader>e").describe("Open external editor"),
-    theme_list: z.string().optional().default("<leader>t").describe("List available themes"),
-    sidebar_toggle: z.string().optional().default("<leader>b").describe("Toggle sidebar"),
-    scrollbar_toggle: z.string().optional().default("none").describe("Toggle session scrollbar"),
-    username_toggle: z.string().optional().default("none").describe("Toggle username visibility"),
-    status_view: z.string().optional().default("<leader>s").describe("View status"),
-    session_export: z.string().optional().default("<leader>x").describe("Export session to editor"),
-    session_new: z.string().optional().default("<leader>n").describe("Create a new session"),
-    session_list: z.string().optional().default("<leader>l").describe("List all sessions"),
-    session_timeline: z.string().optional().default("<leader>g").describe("Show session timeline"),
-    session_fork: z.string().optional().default("none").describe("Fork session from message"),
-    session_rename: z.string().optional().default("ctrl+r").describe("Rename session"),
-    session_delete: z.string().optional().default("ctrl+d").describe("Delete session"),
-    stash_delete: z.string().optional().default("ctrl+d").describe("Delete stash entry"),
-    model_provider_list: z.string().optional().default("ctrl+a").describe("Open provider list from model dialog"),
-    model_favorite_toggle: z.string().optional().default("ctrl+f").describe("Toggle model favorite status"),
-    session_share: z.string().optional().default("none").describe("Share current session"),
-    session_unshare: z.string().optional().default("none").describe("Unshare current session"),
-    session_interrupt: z.string().optional().default("escape").describe("Interrupt current session"),
-    session_compact: z.string().optional().default("<leader>c").describe("Compact the session"),
-    messages_page_up: z.string().optional().default("pageup,ctrl+alt+b").describe("Scroll messages up by one page"),
-    messages_page_down: z
-      .string()
-      .optional()
-      .default("pagedown,ctrl+alt+f")
-      .describe("Scroll messages down by one page"),
-    messages_line_up: z.string().optional().default("ctrl+alt+y").describe("Scroll messages up by one line"),
-    messages_line_down: z.string().optional().default("ctrl+alt+e").describe("Scroll messages down by one line"),
-    messages_half_page_up: z.string().optional().default("ctrl+alt+u").describe("Scroll messages up by half page"),
-    messages_half_page_down: z.string().optional().default("ctrl+alt+d").describe("Scroll messages down by half page"),
-    messages_first: z.string().optional().default("ctrl+g,home").describe("Navigate to first message"),
-    messages_last: z.string().optional().default("ctrl+alt+g,end").describe("Navigate to last message"),
-    messages_next: z.string().optional().default("none").describe("Navigate to next message"),
-    messages_previous: z.string().optional().default("none").describe("Navigate to previous message"),
-    messages_last_user: z.string().optional().default("none").describe("Navigate to last user message"),
-    messages_copy: z.string().optional().default("<leader>y").describe("Copy message"),
-    messages_undo: z.string().optional().default("<leader>u").describe("Undo message"),
-    messages_redo: z.string().optional().default("<leader>r").describe("Redo message"),
-    messages_toggle_conceal: z
-      .string()
-      .optional()
-      .default("<leader>h")
-      .describe("Toggle code block concealment in messages"),
-    tool_details: z.string().optional().default("none").describe("Toggle tool details visibility"),
-    model_list: z.string().optional().default("<leader>m").describe("List available models"),
-    model_cycle_recent: z.string().optional().default("f2").describe("Next recently used model"),
-    model_cycle_recent_reverse: z.string().optional().default("shift+f2").describe("Previous recently used model"),
-    model_cycle_favorite: z.string().optional().default("none").describe("Next favorite model"),
-    model_cycle_favorite_reverse: z.string().optional().default("none").describe("Previous favorite model"),
-    command_list: z.string().optional().default("ctrl+p").describe("List available commands"),
-    agent_list: z.string().optional().default("<leader>a").describe("List agents"),
-    agent_cycle: z.string().optional().default("tab").describe("Next agent"),
-    agent_cycle_reverse: z.string().optional().default("shift+tab").describe("Previous agent"),
-    variant_cycle: z.string().optional().default("ctrl+t").describe("Cycle model variants"),
-    variant_list: z.string().optional().default("none").describe("List model variants"),
-    input_clear: z.string().optional().default("ctrl+c").describe("Clear input field"),
-    input_paste: z.string().optional().default("ctrl+v").describe("Paste from clipboard"),
-    input_submit: z.string().optional().default("return").describe("Submit input"),
-    input_newline: z
-      .string()
-      .optional()
-      .default("shift+return,ctrl+return,alt+return,ctrl+j")
-      .describe("Insert newline in input"),
-    input_move_left: z.string().optional().default("left,ctrl+b").describe("Move cursor left in input"),
-    input_move_right: z.string().optional().default("right,ctrl+f").describe("Move cursor right in input"),
-    input_move_up: z.string().optional().default("up").describe("Move cursor up in input"),
-    input_move_down: z.string().optional().default("down").describe("Move cursor down in input"),
-    input_select_left: z.string().optional().default("shift+left").describe("Select left in input"),
-    input_select_right: z.string().optional().default("shift+right").describe("Select right in input"),
-    input_select_up: z.string().optional().default("shift+up").describe("Select up in input"),
-    input_select_down: z.string().optional().default("shift+down").describe("Select down in input"),
-    input_line_home: z.string().optional().default("ctrl+a").describe("Move to start of line in input"),
-    input_line_end: z.string().optional().default("ctrl+e").describe("Move to end of line in input"),
-    input_select_line_home: z.string().optional().default("ctrl+shift+a").describe("Select to start of line in input"),
-    input_select_line_end: z.string().optional().default("ctrl+shift+e").describe("Select to end of line in input"),
-    input_visual_line_home: z.string().optional().default("alt+a").describe("Move to start of visual line in input"),
-    input_visual_line_end: z.string().optional().default("alt+e").describe("Move to end of visual line in input"),
-    input_select_visual_line_home: z
-      .string()
-      .optional()
-      .default("alt+shift+a")
-      .describe("Select to start of visual line in input"),
-    input_select_visual_line_end: z
-      .string()
-      .optional()
-      .default("alt+shift+e")
-      .describe("Select to end of visual line in input"),
-    input_buffer_home: z.string().optional().default("home").describe("Move to start of buffer in input"),
-    input_buffer_end: z.string().optional().default("end").describe("Move to end of buffer in input"),
-    input_select_buffer_home: z
-      .string()
-      .optional()
-      .default("shift+home")
-      .describe("Select to start of buffer in input"),
-    input_select_buffer_end: z.string().optional().default("shift+end").describe("Select to end of buffer in input"),
-    input_delete_line: z.string().optional().default("ctrl+shift+d").describe("Delete line in input"),
-    input_delete_to_line_end: z.string().optional().default("ctrl+k").describe("Delete to end of line in input"),
-    input_delete_to_line_start: z.string().optional().default("ctrl+u").describe("Delete to start of line in input"),
-    input_backspace: z.string().optional().default("backspace,shift+backspace").describe("Backspace in input"),
-    input_delete: z.string().optional().default("ctrl+d,delete,shift+delete").describe("Delete character in input"),
-    input_undo: z
-      .string()
-      .optional()
-      // On Windows prepend ctrl+z since terminal_suspend releases the binding.
-      .default(process.platform === "win32" ? "ctrl+z,ctrl+-,super+z" : "ctrl+-,super+z")
-      .describe("Undo in input"),
-    input_redo: z.string().optional().default("ctrl+.,super+shift+z").describe("Redo in input"),
-    input_word_forward: z
-      .string()
-      .optional()
-      .default("alt+f,alt+right,ctrl+right")
-      .describe("Move word forward in input"),
-    input_word_backward: z
-      .string()
-      .optional()
-      .default("alt+b,alt+left,ctrl+left")
-      .describe("Move word backward in input"),
-    input_select_word_forward: z
-      .string()
-      .optional()
-      .default("alt+shift+f,alt+shift+right")
-      .describe("Select word forward in input"),
-    input_select_word_backward: z
-      .string()
-      .optional()
-      .default("alt+shift+b,alt+shift+left")
-      .describe("Select word backward in input"),
-    input_delete_word_forward: z
-      .string()
-      .optional()
-      .default("alt+d,alt+delete,ctrl+delete")
-      .describe("Delete word forward in input"),
-    input_delete_word_backward: z
-      .string()
-      .optional()
-      .default("ctrl+w,ctrl+backspace,alt+backspace")
-      .describe("Delete word backward in input"),
-    history_previous: z.string().optional().default("up").describe("Previous history item"),
-    history_next: z.string().optional().default("down").describe("Next history item"),
-    session_child_first: z.string().optional().default("<leader>down").describe("Go to first child session"),
-    session_child_cycle: z.string().optional().default("right").describe("Go to next child session"),
-    session_child_cycle_reverse: z.string().optional().default("left").describe("Go to previous child session"),
-    session_parent: z.string().optional().default("up").describe("Go to parent session"),
-    terminal_suspend: z
-      .string()
-      .optional()
-      .default("ctrl+z")
-      .transform((v) => (process.platform === "win32" ? "none" : v))
-      .describe("Suspend terminal"),
-    terminal_title_toggle: z.string().optional().default("none").describe("Toggle terminal title"),
-    tips_toggle: z.string().optional().default("<leader>h").describe("Toggle tips on home screen"),
-    plugin_manager: z.string().optional().default("none").describe("Open plugin manager dialog"),
-    display_thinking: z.string().optional().default("none").describe("Toggle thinking blocks visibility"),
-  })
-  .strict()
-  .meta({
-    ref: "KeybindsConfig",
-  })
+// Every keybind field has the same shape: an optional string with a default
+// binding and a human description.  `keybind()` keeps the declaration list
+// below dense and readable.
+const keybind = (value: string, description: string) =>
+  Schema.String.pipe(Schema.optional, Schema.withDecodingDefault(Effect.succeed(value))).annotate({ description })
+
+// Windows prepends ctrl+z to the undo binding because `terminal_suspend`
+// cannot consume ctrl+z on native Windows terminals (no POSIX suspend).
+const inputUndoDefault = process.platform === "win32" ? "ctrl+z,ctrl+-,super+z" : "ctrl+-,super+z"
+
+const KeybindsSchema = Schema.Struct({
+  leader: keybind("ctrl+x", "Leader key for keybind combinations"),
+  app_exit: keybind("ctrl+c,ctrl+d,<leader>q", "Exit the application"),
+  editor_open: keybind("<leader>e", "Open external editor"),
+  theme_list: keybind("<leader>t", "List available themes"),
+  sidebar_toggle: keybind("<leader>b", "Toggle sidebar"),
+  scrollbar_toggle: keybind("none", "Toggle session scrollbar"),
+  username_toggle: keybind("none", "Toggle username visibility"),
+  status_view: keybind("<leader>s", "View status"),
+  session_export: keybind("<leader>x", "Export session to editor"),
+  session_new: keybind("<leader>n", "Create a new session"),
+  session_list: keybind("<leader>l", "List all sessions"),
+  session_timeline: keybind("<leader>g", "Show session timeline"),
+  session_fork: keybind("none", "Fork session from message"),
+  session_rename: keybind("ctrl+r", "Rename session"),
+  session_delete: keybind("ctrl+d", "Delete session"),
+  stash_delete: keybind("ctrl+d", "Delete stash entry"),
+  model_provider_list: keybind("ctrl+a", "Open provider list from model dialog"),
+  model_favorite_toggle: keybind("ctrl+f", "Toggle model favorite status"),
+  session_share: keybind("none", "Share current session"),
+  session_unshare: keybind("none", "Unshare current session"),
+  session_interrupt: keybind("escape", "Interrupt current session"),
+  session_compact: keybind("<leader>c", "Compact the session"),
+  messages_page_up: keybind("pageup,ctrl+alt+b", "Scroll messages up by one page"),
+  messages_page_down: keybind("pagedown,ctrl+alt+f", "Scroll messages down by one page"),
+  messages_line_up: keybind("ctrl+alt+y", "Scroll messages up by one line"),
+  messages_line_down: keybind("ctrl+alt+e", "Scroll messages down by one line"),
+  messages_half_page_up: keybind("ctrl+alt+u", "Scroll messages up by half page"),
+  messages_half_page_down: keybind("ctrl+alt+d", "Scroll messages down by half page"),
+  messages_first: keybind("ctrl+g,home", "Navigate to first message"),
+  messages_last: keybind("ctrl+alt+g,end", "Navigate to last message"),
+  messages_next: keybind("none", "Navigate to next message"),
+  messages_previous: keybind("none", "Navigate to previous message"),
+  messages_last_user: keybind("none", "Navigate to last user message"),
+  messages_copy: keybind("<leader>y", "Copy message"),
+  messages_undo: keybind("<leader>u", "Undo message"),
+  messages_redo: keybind("<leader>r", "Redo message"),
+  messages_toggle_conceal: keybind("<leader>h", "Toggle code block concealment in messages"),
+  tool_details: keybind("none", "Toggle tool details visibility"),
+  model_list: keybind("<leader>m", "List available models"),
+  model_cycle_recent: keybind("f2", "Next recently used model"),
+  model_cycle_recent_reverse: keybind("shift+f2", "Previous recently used model"),
+  model_cycle_favorite: keybind("none", "Next favorite model"),
+  model_cycle_favorite_reverse: keybind("none", "Previous favorite model"),
+  command_list: keybind("ctrl+p", "List available commands"),
+  agent_list: keybind("<leader>a", "List agents"),
+  agent_cycle: keybind("tab", "Next agent"),
+  agent_cycle_reverse: keybind("shift+tab", "Previous agent"),
+  variant_cycle: keybind("ctrl+t", "Cycle model variants"),
+  variant_list: keybind("none", "List model variants"),
+  input_clear: keybind("ctrl+c", "Clear input field"),
+  input_paste: keybind("ctrl+v", "Paste from clipboard"),
+  input_submit: keybind("return", "Submit input"),
+  input_newline: keybind("shift+return,ctrl+return,alt+return,ctrl+j", "Insert newline in input"),
+  input_move_left: keybind("left,ctrl+b", "Move cursor left in input"),
+  input_move_right: keybind("right,ctrl+f", "Move cursor right in input"),
+  input_move_up: keybind("up", "Move cursor up in input"),
+  input_move_down: keybind("down", "Move cursor down in input"),
+  input_select_left: keybind("shift+left", "Select left in input"),
+  input_select_right: keybind("shift+right", "Select right in input"),
+  input_select_up: keybind("shift+up", "Select up in input"),
+  input_select_down: keybind("shift+down", "Select down in input"),
+  input_line_home: keybind("ctrl+a", "Move to start of line in input"),
+  input_line_end: keybind("ctrl+e", "Move to end of line in input"),
+  input_select_line_home: keybind("ctrl+shift+a", "Select to start of line in input"),
+  input_select_line_end: keybind("ctrl+shift+e", "Select to end of line in input"),
+  input_visual_line_home: keybind("alt+a", "Move to start of visual line in input"),
+  input_visual_line_end: keybind("alt+e", "Move to end of visual line in input"),
+  input_select_visual_line_home: keybind("alt+shift+a", "Select to start of visual line in input"),
+  input_select_visual_line_end: keybind("alt+shift+e", "Select to end of visual line in input"),
+  input_buffer_home: keybind("home", "Move to start of buffer in input"),
+  input_buffer_end: keybind("end", "Move to end of buffer in input"),
+  input_select_buffer_home: keybind("shift+home", "Select to start of buffer in input"),
+  input_select_buffer_end: keybind("shift+end", "Select to end of buffer in input"),
+  input_delete_line: keybind("ctrl+shift+d", "Delete line in input"),
+  input_delete_to_line_end: keybind("ctrl+k", "Delete to end of line in input"),
+  input_delete_to_line_start: keybind("ctrl+u", "Delete to start of line in input"),
+  input_backspace: keybind("backspace,shift+backspace", "Backspace in input"),
+  input_delete: keybind("ctrl+d,delete,shift+delete", "Delete character in input"),
+  input_undo: keybind(inputUndoDefault, "Undo in input"),
+  input_redo: keybind("ctrl+.,super+shift+z", "Redo in input"),
+  input_word_forward: keybind("alt+f,alt+right,ctrl+right", "Move word forward in input"),
+  input_word_backward: keybind("alt+b,alt+left,ctrl+left", "Move word backward in input"),
+  input_select_word_forward: keybind("alt+shift+f,alt+shift+right", "Select word forward in input"),
+  input_select_word_backward: keybind("alt+shift+b,alt+shift+left", "Select word backward in input"),
+  input_delete_word_forward: keybind("alt+d,alt+delete,ctrl+delete", "Delete word forward in input"),
+  input_delete_word_backward: keybind("ctrl+w,ctrl+backspace,alt+backspace", "Delete word backward in input"),
+  history_previous: keybind("up", "Previous history item"),
+  history_next: keybind("down", "Next history item"),
+  session_child_first: keybind("<leader>down", "Go to first child session"),
+  session_child_cycle: keybind("right", "Go to next child session"),
+  session_child_cycle_reverse: keybind("left", "Go to previous child session"),
+  session_parent: keybind("up", "Go to parent session"),
+  // `terminal_suspend` was formerly `.default("ctrl+z").transform((v) => win32 ? "none" : v)`,
+  // but `tui.ts` already forces the binding to "none" on win32 before calling
+  // `Keybinds.parse(...)`, so the schema-level transform was redundant.
+  terminal_suspend: keybind("ctrl+z", "Suspend terminal"),
+  terminal_title_toggle: keybind("none", "Toggle terminal title"),
+  tips_toggle: keybind("<leader>h", "Toggle tips on home screen"),
+  plugin_manager: keybind("none", "Open plugin manager dialog"),
+  display_thinking: keybind("none", "Toggle thinking blocks visibility"),
+}).annotate({ identifier: "KeybindsConfig" })
+
+export type Keybinds = Schema.Schema.Type<typeof KeybindsSchema>
+
+// Consumers access `Keybinds.shape` and `Keybinds.shape.X.parse(undefined)`,
+// which requires the runtime type to be a ZodObject, not just ZodType.  Every
+// field is `string().optional().default(...)` at runtime, so widen to that.
+export const Keybinds = zod(KeybindsSchema) as unknown as z.ZodObject<
+  Record<keyof Keybinds, z.ZodDefault<z.ZodOptional<z.ZodString>>>
+>
PATCH

echo "solve.sh: gold patch applied"
