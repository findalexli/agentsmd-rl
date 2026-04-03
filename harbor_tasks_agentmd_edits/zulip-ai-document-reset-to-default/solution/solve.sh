#!/usr/bin/env bash
set -euo pipefail

cd /workspace/zulip

# Idempotent: skip if already applied
if grep -q 'title: Reset settings for users' starlight_help/src/content/docs/reset-settings-for-users.mdx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
index e33c8ce1cb802..5b3794ca660e1 100644
--- a/.claude/CLAUDE.md
+++ b/.claude/CLAUDE.md
@@ -143,6 +143,8 @@ coherent idea."** This is non-negotiable.
 - Mix multiple separable changes in a single commit.
 - Create a commit that "fixes" a mistake from an earlier commit in the same PR;
   always edit Git to fix the original commit.
+- Add content in one commit only to remove or move it in the next;
+  plan upfront what belongs where and do it right the first time.
 - Include debugging code, commented-out code, or temporary TODOs.

 ### Commit Message Format
@@ -201,12 +203,17 @@ Since `git rebase -i` requires an interactive editor, use
    Note: `--autosquash` alone without `-i` does **not** reorder or
    squash anything.

-3. **Rewording commit messages:** In the todo script, use `exec` lines:
-   ```
-   pick <hash> Original message
-   exec GIT_EDITOR=/path/to/new-msg-script.sh git commit --amend
+3. **Rewording commit messages:** Use `git format-patch` to export
+   commits as patch files, edit the message headers in the patch
+   files, then reapply:
+
+   ```bash
+   git format-patch <base> -o /tmp/patches/
+   # Edit the commit message in each /tmp/patches/000N-*.patch file
+   # (the message is between the Subject: line and the --- line)
+   git reset --hard <base>
+   git am /tmp/patches/*.patch
    ```
-   where the message script writes the new commit message to `$1`.

 ## Testing Requirements

@@ -487,14 +494,19 @@ a sidebar entry in `starlight_help/astro.config.mjs`.
 See `docs/documentation/helpcenter.md` for the full writing guide. Key points:

 - **Bold** UI element names (e.g., **Settings** page, **Save changes** button).
-- Do not specify default values or list out options in instructions — the user
-  can see them in the UI.
+- Do not specify default values or list out options — the user can see
+  them in the UI. For dropdowns, refer to the setting by its label name
+  rather than enumerating the choices.
 - Do not use "we" to refer to Zulip; use "you" for the reader.
 - Fewer words is better; many users have English as a second language.
 - Use `<kbd>Enter</kbd>` for keyboard keys (non-Mac; auto-translated for Mac).
+- Use `FlattenedList` to merge adjacent bullet lists (inline markdown
+  and/or include components) into a single visual list. Use
+  `FlattenedSteps` for the same purpose with ordered (numbered) lists.
 - Common components and their imports:
   ```
   import {Steps, TabItem, Tabs} from "@astrojs/starlight/components";
+  import FlattenedList from "../../components/FlattenedList.astro";
   import FlattenedSteps from "../../components/FlattenedSteps.astro";
   import NavigationSteps from "../../components/NavigationSteps.astro";
   import ZulipTip from "../../components/ZulipTip.astro";
diff --git a/starlight_help/astro.config.mjs b/starlight_help/astro.config.mjs
index cb033b7203ada..90989432ae320 100644
--- a/starlight_help/astro.config.mjs
+++ b/starlight_help/astro.config.mjs
@@ -556,6 +556,7 @@ export default defineConfig({
                         "change-a-users-name",
                         "manage-user-channel-subscriptions",
                         "manage-user-group-membership",
+                        "reset-settings-for-users",
                     ],
                 },
                 {
diff --git a/starlight_help/src/content/docs/configure-default-new-user-settings.mdx b/starlight_help/src/content/docs/configure-default-new-user-settings.mdx
index 008f673dd42e6..e13cff852c7ef 100644
--- a/starlight_help/src/content/docs/configure-default-new-user-settings.mdx
+++ b/starlight_help/src/content/docs/configure-default-new-user-settings.mdx
@@ -2,47 +2,36 @@
 title: Configure default settings for new users
 ---

+import FlattenedList from "../../components/FlattenedList.astro";
 import FlattenedSteps from "../../components/FlattenedSteps.astro";
 import NavigationSteps from "../../components/NavigationSteps.astro";
 import AdminOnly from "../include/_AdminOnly.mdx";
+import DefaultUserSettingsList from "../include/_DefaultUserSettingsList.mdx";
 import SaveChanges from "../include/_SaveChanges.mdx";

 <AdminOnly />

-Organization administrators can configure the default values of
-personal preference settings for new users joining the
-organization. This can help seamlessly customize the Zulip experience
-to match how the organization in question is using Zulip.
-
-Existing users' preferences cannot be modified by administrators, and
-users will be able to customize their own settings once they
-join. Administrators can customize defaults for all personal
-preference settings, including the following:
-
-* Privacy settings:
-  * Displaying [availability](/help/status-and-availability) to other users
-  * Allowing others to see when the user has [read
-    messages](/help/read-receipts)
-  * Allowing others to see when the user is [typing a
-    message](/help/typing-notifications)
-* Preferences:
-  * [Language](/help/change-your-language)
-  * [Time format](/help/change-the-time-format)
-  * [Light theme vs. dark theme](/help/dark-theme)
-  * [Font size](/help/font-size)
-  * [Line spacing](/help/line-spacing)
-  * [Emoji theme](/help/emoji-and-emoticons#change-your-emoji-set)
-  * [Home view](/help/configure-home-view)
-    ([**Inbox**](/help/inbox) vs.
-    [**Recent conversations**](/help/recent-conversations) vs.
-    [**Combined feed**](/help/reading-strategies#combined-feed))
-* Notification settings:
-  * What types of messages [trigger notifications][default-notifications]
-  * Which topics users will [automatically follow](/help/follow-a-topic). This
-    minimizes the need to [mention](/help/mention-a-user-or-group) other users
-    to get their attention.
-
-[default-notifications]: /help/channel-notifications#configure-default-notifications-for-all-channels
+You can configure the default values of personal preference settings for new
+users joining your organization. This lets you customize the Zulip experience to
+match how your organization is using Zulip.
+
+Users will be able to customize their own settings once they join.
+If needed, administrators can [reset settings for
+users](/help/reset-settings-for-users) to the organization default.
+
+Administrators can customize defaults for all personal preference
+settings, including the following:
+
+<FlattenedList>
+  * Privacy settings:
+    * Displaying [availability](/help/status-and-availability) to other users
+    * Allowing others to see when the user has [read
+      messages](/help/read-receipts)
+    * Allowing others to see when the user is [typing a
+      message](/help/typing-notifications)
+
+  <DefaultUserSettingsList />
+</FlattenedList>

 ## Configure default settings for new users

@@ -74,6 +63,7 @@ API](/api/create-user).

 ## Related articles

+* [Reset settings for users](/help/reset-settings-for-users)
 * [Moving to Zulip](/help/moving-to-zulip)
 * [Customize settings for new users](/help/customize-settings-for-new-users)
 * [Set default channels for new users](/help/set-default-channels-for-new-users)
diff --git a/starlight_help/src/content/docs/configure-home-view.mdx b/starlight_help/src/content/docs/configure-home-view.mdx
index ce0c79b39e5d5..e0d1868ee63d0 100644
--- a/starlight_help/src/content/docs/configure-home-view.mdx
+++ b/starlight_help/src/content/docs/configure-home-view.mdx
@@ -84,3 +84,4 @@ and will not affect the behavior of the
 * [Recent conversations](/help/recent-conversations)
 * [Combined feed](/help/combined-feed)
 * [Keyboard shortcuts](/help/keyboard-shortcuts)
+* [Reset settings for users](/help/reset-settings-for-users)
diff --git a/starlight_help/src/content/docs/customize-settings-for-new-users.mdx b/starlight_help/src/content/docs/customize-settings-for-new-users.mdx
index 069a5ad1da22e..1038d81388294 100644
--- a/starlight_help/src/content/docs/customize-settings-for-new-users.mdx
+++ b/starlight_help/src/content/docs/customize-settings-for-new-users.mdx
@@ -11,3 +11,4 @@ import CustomizeSettingsForNewUsers from "../include/_CustomizeSettingsForNewUse
 * [Moving to Zulip](/help/moving-to-zulip)
 * [Invite users to join](/help/invite-users-to-join)
 * [Getting started with Zulip](/help/getting-started-with-zulip)
+* [Reset settings for users](/help/reset-settings-for-users)
diff --git a/starlight_help/src/content/docs/manage-a-user.mdx b/starlight_help/src/content/docs/manage-a-user.mdx
index 1355dc6599a27..33ed0c885190a 100644
--- a/starlight_help/src/content/docs/manage-a-user.mdx
+++ b/starlight_help/src/content/docs/manage-a-user.mdx
@@ -39,3 +39,4 @@ import UserCogIcon from "~icons/zulip-icon/user-cog";
 * [Deactivate or reactivate a user](/help/deactivate-or-reactivate-a-user)
 * [Change a user's role](/help/user-roles#change-a-users-role)
 * [Change a user's name](/help/change-a-users-name)
+* [Reset settings for users](/help/reset-settings-for-users)
diff --git a/starlight_help/src/content/docs/manage-user-channel-subscriptions.mdx b/starlight_help/src/content/docs/manage-user-channel-subscriptions.mdx
index 6c61ca9a0eac3..ae704af135cb0 100644
--- a/starlight_help/src/content/docs/manage-user-channel-subscriptions.mdx
+++ b/starlight_help/src/content/docs/manage-user-channel-subscriptions.mdx
@@ -37,3 +37,4 @@ import UnsubscribeUserFromChannel from "../include/_UnsubscribeUserFromChannel.m
 * [Unsubscribe users from a channel](/help/unsubscribe-users-from-a-channel)
 * [Unsubscribe from a channel](/help/unsubscribe-from-a-channel)
 * [View channel subscribers](/help/view-channel-subscribers)
+* [Reset settings for users](/help/reset-settings-for-users)
diff --git a/starlight_help/src/content/docs/reset-settings-for-users.mdx b/starlight_help/src/content/docs/reset-settings-for-users.mdx
new file mode 100644
index 0000000000000..8df90ab705788
--- /dev/null
+++ b/starlight_help/src/content/docs/reset-settings-for-users.mdx
@@ -0,0 +1,46 @@
+---
+title: Reset settings for users
+---
+
+import FlattenedSteps from "../../components/FlattenedSteps.astro";
+import NavigationSteps from "../../components/NavigationSteps.astro";
+import AdminOnly from "../include/_AdminOnly.mdx";
+import DefaultUserSettingsList from "../include/_DefaultUserSettingsList.mdx";
+
+import ResetIcon from "~icons/zulip-icon/reset";
+
+<AdminOnly />
+
+Organization administrators can reset preference and notification
+settings for users to the [organization
+default](/help/configure-default-new-user-settings). You can choose
+to reset settings for all users, or only those who have not
+personally configured the setting.
+
+Settings administrators can reset include:
+
+<DefaultUserSettingsList />
+
+Privacy settings can be [configured for new
+users](/help/configure-default-new-user-settings), but cannot be
+reset for existing users.
+
+## Reset settings for users
+
+<FlattenedSteps>
+  <NavigationSteps target="settings/default-user-settings" />
+
+  1. Next to the setting you want to reset, click the **Reset users
+     to default** (<ResetIcon />) icon.
+
+  1. Select the desired option for **Users whose configuration should
+     be changed**.
+
+  1. Click **Confirm**.
+</FlattenedSteps>
+
+## Related articles
+
+* [Configure default settings for new users](/help/configure-default-new-user-settings)
+* [Customize settings for new users](/help/customize-settings-for-new-users)
+* [Manage a user](/help/manage-a-user)
diff --git a/starlight_help/src/content/include/_DefaultUserSettingsList.mdx b/starlight_help/src/content/include/_DefaultUserSettingsList.mdx
new file mode 100644
index 0000000000000..b8c2451c10e20
--- /dev/null
+++ b/starlight_help/src/content/include/_DefaultUserSettingsList.mdx
@@ -0,0 +1,21 @@
+* Preferences:
+  * [Language](/help/change-your-language)
+  * [Time format](/help/change-the-time-format)
+  * [Light theme vs. dark theme](/help/dark-theme)
+  * [Font size](/help/font-size)
+  * [Line spacing](/help/line-spacing)
+  * [Emoji theme](/help/emoji-and-emoticons#change-your-emoji-set)
+  * [Home view](/help/configure-home-view)
+    ([**Inbox**](/help/inbox) vs.
+    [**Recent conversations**](/help/recent-conversations) vs.
+    [**Combined feed**](/help/reading-strategies#combined-feed))
+* Notification settings:
+  * What types of messages [trigger notifications][default-notifications]
+  * Which topics users will [automatically follow](/help/follow-a-topic). This
+    minimizes the need to [mention](/help/mention-a-user-or-group) other users
+    to get their attention.
+  * [Desktop](/help/desktop-notifications),
+    [mobile](/help/mobile-notifications), and
+    [email](/help/email-notifications) notification settings
+
+[default-notifications]: /help/channel-notifications#configure-default-notifications-for-all-channels

PATCH

echo "Patch applied successfully."
