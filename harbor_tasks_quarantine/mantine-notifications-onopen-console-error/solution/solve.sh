#!/bin/bash
set -e

cd /workspace/mantine

# Check if already patched (idempotency)
if grep -q "onOpen: _onOpen," packages/@mantine/notifications/src/NotificationContainer.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/packages/@mantine/notifications/src/NotificationContainer.tsx b/packages/@mantine/notifications/src/NotificationContainer.tsx
index 081b7ef708..2d4960acfd 100644
--- a/packages/@mantine/notifications/src/NotificationContainer.tsx
+++ b/packages/@mantine/notifications/src/NotificationContainer.tsx
@@ -21,7 +21,7 @@ export function NotificationContainer({
   onHoverEnd,
   ...others
 }: NotificationContainerProps) {
-  const { autoClose: _autoClose, message, ...notificationProps } = data;
+  const { autoClose: _autoClose, message, onOpen: _onOpen, ...notificationProps } = data;
   const autoCloseDuration = getAutoClose(autoClose, data.autoClose);
   const autoCloseTimeout = useRef<number>(-1);
   const [hovered, setHovered] = useState(false);
PATCH

echo "Patch applied successfully"
