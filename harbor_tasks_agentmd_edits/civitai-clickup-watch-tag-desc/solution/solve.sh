#!/usr/bin/env bash
set -euo pipefail

cd /workspace/civitai

# Idempotent: skip if already applied
if grep -q 'addWatcher' .claude/skills/clickup/api/tasks.mjs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.claude/skills/clickup/SKILL.md b/.claude/skills/clickup/SKILL.md
index fd6662202..c94c1becb 100644
--- a/.claude/skills/clickup/SKILL.md
+++ b/.claude/skills/clickup/SKILL.md
@@ -56,6 +56,9 @@ node .claude/skills/clickup/query.mjs <command> [options]
 | `link <task> <url> ["desc"]` | Add external link reference (as comment) |
 | `checklist <task> "item"` | Add checklist item to task |
 | `delete-comment <comment_id>` | Delete a comment |
+| `watch <task> <user>` | Notify user via @mention comment (watchers not supported in API) |
+| `tag <task> "tag_name"` | Add a tag to task |
+| `description <task> "text"` | Update task description (markdown supported) |

 ### Options

@@ -213,6 +216,37 @@ node .claude/skills/clickup/query.mjs me
 node .claude/skills/clickup/query.mjs delete-comment 90110200841741
 ```

+### Notify Users (Watch)
+
+```bash
+# Notify user via @mention comment (ClickUp API doesn't support adding watchers directly)
+node .claude/skills/clickup/query.mjs watch 86a1b2c3d koen
+
+# Notify by email
+node .claude/skills/clickup/query.mjs watch 86a1b2c3d jane@example.com
+```
+
+### Add Tags
+
+```bash
+# Add a tag to a task
+node .claude/skills/clickup/query.mjs tag 86a1b2c3d "DevOps"
+node .claude/skills/clickup/query.mjs tag 86a1b2c3d "bug"
+```
+
+### Update Description
+
+```bash
+# Update task description with markdown
+node .claude/skills/clickup/query.mjs description 86a1b2c3d "## Summary
+This is a **bold** statement.
+
+- Item 1
+- Item 2
+
+See [documentation](https://example.com) for more info."
+```
+
 ## Task/List URL Formats

 The skill recognizes these ClickUp URL formats:
@@ -270,7 +304,8 @@ Total: 2 task(s)
 - **Daily standups**: Use `my-tasks` to see your assignments
 - **Status updates**: Post progress comments as you work
 - **Task management**: Assign, prioritize, and set due dates
-- **Collaboration**: View recent comments for context
+- **Collaboration**: View recent comments for context, add watchers
+- **Task organization**: Add tags to categorize tasks
 - **Task linking**: Reference task IDs in commit messages

 ## Tips
diff --git a/.claude/skills/clickup/api/tasks.mjs b/.claude/skills/clickup/api/tasks.mjs
index 5991b71af..322b4814f 100644
--- a/.claude/skills/clickup/api/tasks.mjs
+++ b/.claude/skills/clickup/api/tasks.mjs
@@ -255,3 +255,33 @@ export async function moveTask(taskId, targetListId) {
   });
   return response;
 }
+
+// Add a watcher/follower to a task
+// NOTE: ClickUp API v2 does not have a documented public endpoint for adding watchers.
+// Returns null to indicate watchers cannot be added programmatically via API.
+// Callers should use @mentions in comments as an alternative notification mechanism.
+export async function addWatcher(taskId, userId) {
+  throw new Error(
+    'ClickUp API v2 does not support adding watchers programmatically. ' +
+    'Use "@username" in a comment to notify someone instead.'
+  );
+}
+
+// Add a tag to a task
+export async function addTag(taskId, tagName) {
+  // Tag names in URL must be URL-encoded
+  const encodedTag = encodeURIComponent(tagName);
+  const response = await apiRequest(`/task/${taskId}/tag/${encodedTag}`, {
+    method: 'POST',
+  });
+  return response;
+}
+
+// Remove a tag from a task
+export async function removeTag(taskId, tagName) {
+  const encodedTag = encodeURIComponent(tagName);
+  const response = await apiRequest(`/task/${taskId}/tag/${encodedTag}`, {
+    method: 'DELETE',
+  });
+  return response;
+}
diff --git a/.claude/skills/clickup/query.mjs b/.claude/skills/clickup/query.mjs
index f494f5b14..747ac755c 100644
--- a/.claude/skills/clickup/query.mjs
+++ b/.claude/skills/clickup/query.mjs
@@ -21,6 +21,9 @@
  *   link <task> <url> ["desc"]    Add external link reference
  *   checklist <task> "item"       Add checklist item
  *   delete-comment <comment_id>   Delete a comment
+ *   watch <task> <user>           Add a watcher to task
+ *   tag <task> "tag_name"         Add a tag to task
+ *   description <task> "text"     Update task description (markdown supported)
  *
  * Options:
  *   --json       Output raw JSON
@@ -36,6 +39,7 @@ import {
   getTasksInList,
   getAvailableStatuses,
   updateTaskStatus,
+  updateTask,
   createTask,
   createSubtask,
   searchTasks,
@@ -45,6 +49,8 @@ import {
   setPriority,
   moveTask,
   parseDateInput,
+  addWatcher,
+  addTag,
 } from './api/tasks.mjs';
 import { getComments, postComment, deleteComment } from './api/comments.mjs';
 import { addChecklistItemToTask, getChecklists } from './api/checklists.mjs';
@@ -117,6 +123,9 @@ Commands:
   link <task> <url> ["desc"]    Add external link reference
   checklist <task> "item"       Add checklist item
   delete-comment <comment_id>   Delete a comment
+  watch <task> <user>           Add a watcher to task
+  tag <task> "tag_name"         Add a tag to task
+  description <task> "text"     Update task description (markdown supported)

 Options:
   --json       Output raw JSON
@@ -139,7 +148,10 @@ Examples:
   node query.mjs move 86a1b2c3d 901111220964
   node query.mjs link 86a1b2c3d "https://github.com/..." "PR #123"
   node query.mjs checklist 86a1b2c3d "Review code"
-  node query.mjs delete-comment 90110200841741`);
+  node query.mjs delete-comment 90110200841741
+  node query.mjs watch 86a1b2c3d koen
+  node query.mjs tag 86a1b2c3d "DevOps"
+  node query.mjs description 86a1b2c3d "## Summary\\nThis is **bold** text"`);
   process.exit(1);
 }

@@ -349,20 +361,30 @@ async function main() {
         // Build options from flags
         const options = {};
         if (descriptionArg) {
-          options.description = descriptionArg;
+          // Use markdown_description for proper markdown rendering in ClickUp
+          // Note: Task descriptions use markdown_description (ClickUp parses),
+          // while comments use JSON array format (we parse via markdownToClickUp)
+          options.markdown_description = descriptionArg;
         }
         if (dueArg) {
           const dueDate = parseDateInput(dueArg);
           options.due_date = dueDate.getTime();
         }
         if (assigneeArg) {
-          const teamId = await getTeamId();
-          const user = await findUser(teamId, assigneeArg);
-          if (!user) {
-            console.error(`Error: User "${assigneeArg}" not found in team`);
-            process.exit(1);
+          let assigneeId;
+          if (assigneeArg.toLowerCase() === 'me') {
+            // Special case: "me" means the current authenticated user
+            assigneeId = await getUserId();
+          } else {
+            const teamId = await getTeamId();
+            const user = await findUser(teamId, assigneeArg);
+            if (!user) {
+              console.error(`Error: User "${assigneeArg}" not found in team`);
+              process.exit(1);
+            }
+            assigneeId = user.id;
           }
-          options.assignees = [user.id];
+          options.assignees = [assigneeId];
         }

         const task = await createTask(listId, title, options);
@@ -551,6 +573,81 @@ async function main() {
         break;
       }

+      case 'watch': {
+        const taskId = parseTaskId(targetInput);
+        if (!taskId) {
+          console.error('Error: Could not parse task ID from input');
+          process.exit(1);
+        }
+        if (!arg2) {
+          console.error('Error: User required');
+          console.error('Usage: node query.mjs watch <task> <user>');
+          process.exit(1);
+        }
+        const teamId = await getTeamId();
+        const user = await findUser(teamId, arg2);
+        if (!user) {
+          console.error(`Error: User "${arg2}" not found in team`);
+          process.exit(1);
+        }
+        // ClickUp API v2 doesn't support adding watchers programmatically.
+        // Post a comment with @mention as an alternative to notify the user.
+        const mentionComment = `@${user.username} has been added as a watcher on this task.`;
+        const result = await postComment(taskId, mentionComment);
+        if (jsonOutput) {
+          console.log(JSON.stringify({ notified: true, user: user.username, comment_id: result.id }, null, 2));
+        } else {
+          console.log(`Notified ${user.username || user.email} via @mention comment`);
+          console.log(`(Note: ClickUp API does not support adding watchers directly)`);
+        }
+        break;
+      }
+
+      case 'tag': {
+        const taskId = parseTaskId(targetInput);
+        if (!taskId) {
+          console.error('Error: Could not parse task ID from input');
+          process.exit(1);
+        }
+        if (!arg2) {
+          console.error('Error: Tag name required');
+          console.error('Usage: node query.mjs tag <task> "tag_name"');
+          process.exit(1);
+        }
+        await addTag(taskId, arg2);
+        if (jsonOutput) {
+          console.log(JSON.stringify({ tagged: true, taskId, tag: arg2 }, null, 2));
+        } else {
+          console.log(`Tag "${arg2}" added to task`);
+        }
+        break;
+      }
+
+      case 'description': {
+        const taskId = parseTaskId(targetInput);
+        if (!taskId) {
+          console.error('Error: Could not parse task ID from input');
+          process.exit(1);
+        }
+        if (!arg2) {
+          console.error('Error: Description text required');
+          console.error('Usage: node query.mjs description <task> "description text"');
+          console.error('Markdown formatting is supported.');
+          process.exit(1);
+        }
+        // Use markdown_description for proper markdown rendering in ClickUp
+        // Note: Unlike comments (which use JSON array format via markdownToClickUp),
+        // task descriptions use ClickUp's native markdown_description field
+        const task = await updateTask(taskId, { markdown_description: arg2 });
+        if (jsonOutput) {
+          console.log(JSON.stringify(task, null, 2));
+        } else {
+          console.log('Task description updated');
+          console.log(`URL: ${task.url}`);
+        }
+        break;
+      }
+
       default:
         console.error(`Unknown command: ${command}`);
         showUsage();

PATCH

echo "Patch applied successfully."
