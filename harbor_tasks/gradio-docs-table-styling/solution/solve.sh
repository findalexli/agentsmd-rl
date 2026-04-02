#!/usr/bin/env bash
set -euo pipefail

STYLE_FILE="js/_website/src/lib/assets/style.css"

# Idempotency: check if general table styling already exists
if grep -q '^table {' "$STYLE_FILE" 2>/dev/null; then
    echo "Table styling already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/js/_website/src/lib/assets/style.css b/js/_website/src/lib/assets/style.css
index 7b0f3dbfbe..faad0d01cd 100644
--- a/js/_website/src/lib/assets/style.css
+++ b/js/_website/src/lib/assets/style.css
@@ -479,3 +479,44 @@ summary::after {
 .dark .obj .max-h-96.overflow-y-scroll table tbody td {
 	color: #e5e5e5 !important;
 }
+
+table {
+	width: 100%;
+	border-collapse: collapse;
+	margin-top: 1.5rem;
+	margin-bottom: 1.5rem;
+	font-size: 1rem;
+}
+
+table thead th {
+	background-color: #f3f4f6;
+	color: #111827;
+	font-weight: 600;
+	text-align: left;
+	padding-left: 1rem;
+	padding-right: 1rem;
+	padding-top: 0.5rem;
+	padding-bottom: 0.5rem;
+	border: 1px solid #e5e7eb;
+}
+
+.dark table thead th {
+	background-color: #374151;
+	color: #f3f4f6;
+	border: 1px solid #52525b;
+}
+
+table tbody td {
+	padding-left: 1rem;
+	padding-right: 1rem;
+	padding-top: 0.5rem;
+	padding-bottom: 0.5rem;
+	border: 1px solid #e5e7eb;
+	color: #374151;
+	vertical-align: top;
+}
+
+.dark table tbody td {
+	border: 1px solid #52525b;
+	color: #d1d5db;
+}

PATCH

echo "Table styling applied."
