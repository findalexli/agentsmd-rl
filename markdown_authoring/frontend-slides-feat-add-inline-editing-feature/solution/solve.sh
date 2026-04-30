#!/usr/bin/env bash
set -euo pipefail

cd /workspace/frontend-slides

# Idempotency guard
if grep -qF "The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `point" "SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/SKILL.md b/SKILL.md
@@ -305,6 +305,15 @@ Before designing, understand the content. Ask via AskUserQuestion:
 
 The user can select **"Other"** to type or paste any custom folder path (e.g. `~/Desktop/screenshots`). This way the image folder path is collected in the same form — no extra round-trip.
 
+**Question 5: Inline Editing**
+- Header: "Editing"
+- Question: "Do you need to edit text directly in the browser after generation?"
+- Options:
+  - "Yes (Recommended)" — Can edit text in-browser, auto-save to localStorage, export file
+  - "No" — Presentation only, keeps file smaller
+
+**Remember the user's choice — it determines whether edit-related HTML/CSS/JS is included in Phase 3.**
+
 If user has content, ask them to share it (text, bullet points, images, etc.).
 
 ### Step 1.2: Image Evaluation
@@ -866,6 +875,95 @@ Every presentation should include:
    - 3D tilt on hover
    - Magnetic buttons
    - Counter animations
+   - **Inline editing** (only if user opted in during content discovery):
+     - Edit toggle button (hidden by default, revealed via hover hotzone or `E` key)
+     - Auto-save to localStorage
+     - Export/save file functionality
+     - See "Edit Button Implementation" section below for required code patterns
+
+### Edit Button Implementation (When User Opts In)
+
+**If the user chose "No" for inline editing in Phase 1, skip this entirely — do not generate any edit-related HTML, CSS, or JS.**
+
+**⚠️ Critical: Do NOT use CSS `~` sibling selector for hover-based show/hide.**
+
+The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` on the toggle button causes the hover chain to break: user hovers hotzone → button becomes visible → mouse moves toward button → leaves hotzone → button disappears before click reaches it.
+
+**Required approach: JS-based hover with delay timeout.**
+
+HTML structure:
+```html
+<div class="edit-hotzone"></div>
+<button class="edit-toggle" id="editToggle" title="编辑模式 (E)">✏️</button>
+```
+
+CSS (visibility controlled by JS classes only):
+```css
+/* ⚠️ Do NOT use CSS ~ sibling selector for this!
+   pointer-events: none breaks the hover chain.
+   Must use JS with delay timeout. */
+.edit-hotzone {
+    position: fixed; top: 0; left: 0;
+    width: 80px; height: 80px;
+    z-index: 10000;
+    cursor: pointer;
+}
+.edit-toggle {
+    opacity: 0;
+    pointer-events: none;
+    transition: opacity 0.3s ease;
+    z-index: 10001;
+}
+/* Only JS-added classes control visibility */
+.edit-toggle.show,
+.edit-toggle.active {
+    opacity: 1;
+    pointer-events: auto;
+}
+```
+
+JS (all three interaction methods):
+```javascript
+// 1. Click handler on the toggle button
+document.getElementById('editToggle').addEventListener('click', () => {
+    editor.toggleEditMode();
+});
+
+// 2. Hotzone hover with 400ms grace period
+const hotzone = document.querySelector('.edit-hotzone');
+const editToggle = document.getElementById('editToggle');
+let hideTimeout = null;
+
+hotzone.addEventListener('mouseenter', () => {
+    clearTimeout(hideTimeout);
+    editToggle.classList.add('show');
+});
+hotzone.addEventListener('mouseleave', () => {
+    hideTimeout = setTimeout(() => {
+        if (!editor.isActive) editToggle.classList.remove('show');
+    }, 400);
+});
+editToggle.addEventListener('mouseenter', () => {
+    clearTimeout(hideTimeout);
+});
+editToggle.addEventListener('mouseleave', () => {
+    hideTimeout = setTimeout(() => {
+        if (!editor.isActive) editToggle.classList.remove('show');
+    }, 400);
+});
+
+// 3. Hotzone direct click
+hotzone.addEventListener('click', () => {
+    editor.toggleEditMode();
+});
+
+// 4. Keyboard shortcut (E key, skip when editing text)
+document.addEventListener('keydown', (e) => {
+    if ((e.key === 'e' || e.key === 'E') && !e.target.getAttribute('contenteditable')) {
+        editor.toggleEditMode();
+    }
+});
+```
 
 ### Code Quality Requirements
 
@@ -1064,6 +1162,14 @@ Your presentation is ready!
 Would you like me to make any adjustments?
 ```
 
+If the user opted in to inline editing, also include:
+```
+**Editing:**
+- Hover over top-left corner or press E to enter edit mode
+- Click any text to edit directly
+- Ctrl+S or click "Save file" to save changes
+```
+
 ---
 
 ## Style Reference: Effect → Feeling Mapping
PATCH

echo "Gold patch applied."
