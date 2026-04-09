#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the fix for user-actions popup menu display
# This removes the conditional check that was hiding the menu for unauthenticated users

patch -p1 << 'PATCH'
diff --git a/frontend/src/components/features/sidebar/user-actions.tsx b/frontend/src/components/features/sidebar/user-actions.tsx
index 2c715e4c2c43..6fc5623fa13b 100644
--- a/frontend/src/components/features/sidebar/user-actions.tsx
+++ b/frontend/src/components/features/sidebar/user-actions.tsx
@@ -2,7 +2,6 @@ import React from "react";
 import ReactDOM from "react-dom";
 import { UserAvatar } from "./user-avatar";
 import { useMe } from "#/hooks/query/use-me";
-import { useShouldShowUserFeatures } from "#/hooks/use-should-show-user-features";
 import { UserContextMenu } from "../user/user-context-menu";
 import { InviteOrganizationMemberModal } from "../org/invite-organization-member-modal";
 import { cn } from "#/utils/utils";
@@ -24,9 +23,6 @@ export function UserActions({ user, isLoading }: UserActionsProps) {
     React.useState(false);
   const hideTimeoutRef = React.useRef<number | null>(null);

-  // Use the shared hook to determine if user actions should be shown
-  const shouldShowUserActions = useShouldShowUserFeatures();
-
   // Clean up timeout on unmount
   React.useEffect(
     () => () => {
@@ -79,21 +75,19 @@ export function UserActions({ user, isLoading }: UserActionsProps) {
       >
         <UserAvatar avatarUrl={user?.avatar_url} isLoading={isLoading} />

-        {shouldShowUserActions && user && (
-          <div
-            className={cn(
-              "opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto",
-              accountContextMenuIsVisible && "opacity-100 pointer-events-auto",
-            )}
-          >
-            <UserContextMenu
-              key={menuResetCount}
-              type={me?.role ?? "member"}
-              onClose={closeAccountMenu}
-              onOpenInviteModal={openInviteMemberModal}
-            />
-          </div>
-        )}
+        <div
+          className={cn(
+            "opacity-0 pointer-events-none group-hover:opacity-100 group-hover:pointer-events-auto",
+            accountContextMenuIsVisible && "opacity-100 pointer-events-auto",
+          )}
+        >
+          <UserContextMenu
+            key={menuResetCount}
+            type={me?.role ?? "member"}
+            onClose={closeAccountMenu}
+            onOpenInviteModal={openInviteMemberModal}
+          />
+        </div>
       </div>

       {inviteMemberModalIsOpen &&
PATCH

# Verify the patch was applied by checking for the distinctive line
grep -q "group-hover:opacity-100 group-hover:pointer-events-auto" frontend/src/components/features/sidebar/user-actions.tsx && \
grep -q "key={menuResetCount}" frontend/src/components/features/sidebar/user-actions.tsx && \
echo "Patch applied successfully"
