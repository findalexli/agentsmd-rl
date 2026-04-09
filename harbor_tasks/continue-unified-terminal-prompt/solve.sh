#!/bin/bash
set -e

cd /workspace/continue

# Check if patch already applied (idempotency)
if grep -q '<div className="text-terminal pb-2">{command}</div>' gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the patch
patch -p1 <<'PATCH'
diff --git a/gui/src/components/UnifiedTerminal/UnifiedTerminal.test.tsx b/gui/src/components/UnifiedTerminal/UnifiedTerminal.test.tsx
index 55420628fc9..e27773401d3 100644
--- a/gui/src/components/UnifiedTerminal/UnifiedTerminal.test.tsx
+++ b/gui/src/components/UnifiedTerminal/UnifiedTerminal.test.tsx
@@ -48,7 +48,7 @@ describe("UnifiedTerminalCommand", () => {
     );

     // Should show the command
-    expect(screen.getByText(`$ ${MOCK_COMMAND}`)).toBeInTheDocument();
+    expect(screen.getByText(MOCK_COMMAND)).toBeInTheDocument();

     // Should show terminal header
     expect(screen.getByText("Terminal")).toBeInTheDocument();
@@ -68,7 +68,7 @@ describe("UnifiedTerminalCommand", () => {
     );

     // Should show the command and output
-    expect(screen.getByText(`$ ${MOCK_COMMAND}`)).toBeInTheDocument();
+    expect(screen.getByText(MOCK_COMMAND)).toBeInTheDocument();

     // Check that the output content exists in the container
     expect(container.textContent).toMatch(/Test 1 passed/);
@@ -303,7 +303,7 @@ describe("UnifiedTerminalCommand", () => {
     );

     // Should show command but no output section
-    expect(screen.getByText(`$ ${MOCK_COMMAND}`)).toBeInTheDocument();
+    expect(screen.getByText(MOCK_COMMAND)).toBeInTheDocument();

     // Should not show any output content
     const outputElements = container.querySelectorAll(
diff --git a/gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx b/gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx
index f048af8fb36..e564d385515 100644
--- a/gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx
+++ b/gui/src/components/UnifiedTerminal/UnifiedTerminal.tsx
@@ -410,7 +410,7 @@ export function UnifiedTerminalCommand({

   // Create combined content for copying (command + output)
   const copyContent = useMemo(() => {
-    let content = `$ ${command}`;
+    let content = command;
     if (hasOutput) {
       content += `\n\n${output}`;
     }
@@ -459,7 +459,7 @@ export function UnifiedTerminalCommand({
             <pre className="bg-editor">
               <code>
                 {/* Command is always visible */}
-                <div className="text-terminal pb-2">$ {command}</div>
+                <div className="text-terminal pb-2">{command}</div>

                 {/* Running state with cursor */}
                 {isRunning && !hasOutput && (
PATCH

echo "Patch applied successfully!"
