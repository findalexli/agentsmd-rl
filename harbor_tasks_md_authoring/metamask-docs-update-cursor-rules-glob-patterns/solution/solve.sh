#!/usr/bin/env bash
set -euo pipefail

cd /workspace/metamask-docs

# Idempotency guard
if grep -qF "globs: **/*.md,**/*.mdx" ".cursor/rules/content-types.mdc" && grep -qF "- Do not use em dashes (\u2014) to set off extra information. Use commas, parentheses" ".cursor/rules/editorial-voice.mdc" && grep -qF "globs: **/*.md,**/*.mdx" ".cursor/rules/markdown-formatting.mdc" && grep -qF "globs: embedded-wallets/**/*.md,embedded-wallets/**/*.mdx" ".cursor/rules/product-embedded-wallets.mdc" && grep -qF "globs: metamask-connect/**/*.md,metamask-connect/**/*.mdx" ".cursor/rules/product-metamask-connect.mdc" && grep -qF "globs: services/**/*.md,services/**/*.mdx" ".cursor/rules/product-services.mdc" && grep -qF "globs: smart-accounts-kit/**/*.md,smart-accounts-kit/**/*.mdx,src/lib/glossary.j" ".cursor/rules/product-smart-accounts-kit.mdc" && grep -qF "globs: snaps/**/*.md,snaps/**/*.mdx" ".cursor/rules/product-snaps.mdc" && grep -qF "globs: **/*.md,**/*.mdx" ".cursor/rules/terminology.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/content-types.mdc b/.cursor/rules/content-types.mdc
@@ -1,6 +1,6 @@
 ---
 description: Maps folder conventions to Diataxis content types so AI tools produce the right structure for each doc category.
-globs: ["**/*.md", "**/*.mdx"]
+globs: **/*.md,**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/editorial-voice.mdc b/.cursor/rules/editorial-voice.mdc
@@ -1,6 +1,6 @@
 ---
 description: Editorial voice and tone rules aligned with the Microsoft Writing Style Guide and Consensys documentation standards.
-globs: ["**/*.md", "**/*.mdx"]
+globs: **/*.md,**/*.mdx
 alwaysApply: false
 ---
 
@@ -44,12 +44,14 @@ The rules below are the most actionable subset for AI-assisted editing.
 
 ## Punctuation and formatting
 
-- Do not use em dashes or en dashes. Use commas, parentheses, semicolons, or rephrase the sentence.
+- Do not use em dashes (—) to set off extra information. Use commas, parentheses, semicolons, or rephrase the sentence.
 - Use only one space after periods, question marks, and colons.
 - Use sentence case for all headings and titles. Never use title case.
 - Do not end headings, subheadings, or UI titles with periods.
 - Use backticks for inline code, file names, and URLs referenced in prose.
-- Use bold for UI element names (buttons, menu items, field labels).
+- In general, do not use bold to emphasize words in a paragraph. Use bold sparingly:
+  - For UI element names (buttons, menu items, field labels).
+  - For emphasis in exceptional cases such as critical security warnings when an admonition is not enough.
 
 ## Developer content
 
diff --git a/.cursor/rules/markdown-formatting.mdc b/.cursor/rules/markdown-formatting.mdc
@@ -1,6 +1,6 @@
 ---
 description: Markdown formatting conventions for the MetaMask documentation site (Docusaurus).
-globs: ["**/*.md", "**/*.mdx"]
+globs: **/*.md,**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/product-embedded-wallets.mdc b/.cursor/rules/product-embedded-wallets.mdc
@@ -1,6 +1,6 @@
 ---
 description: Product-specific guidance for Embedded Wallets documentation, including naming, content organization, and SDK conventions.
-globs: ["embedded-wallets/**/*.md", "embedded-wallets/**/*.mdx"]
+globs: embedded-wallets/**/*.md,embedded-wallets/**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/product-metamask-connect.mdc b/.cursor/rules/product-metamask-connect.mdc
@@ -1,6 +1,6 @@
 ---
 description: Product-specific guidance for MetaMask Connect documentation, including terminology, CAIP standards, and content organization.
-globs: ["metamask-connect/**/*.md", "metamask-connect/**/*.mdx"]
+globs: metamask-connect/**/*.md,metamask-connect/**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/product-services.mdc b/.cursor/rules/product-services.mdc
@@ -1,6 +1,6 @@
 ---
 description: Product-specific guidance for Services (Infura) documentation, including naming, reference conventions, and partial reuse.
-globs: ["services/**/*.md", "services/**/*.mdx"]
+globs: services/**/*.md,services/**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/product-smart-accounts-kit.mdc b/.cursor/rules/product-smart-accounts-kit.mdc
@@ -1,12 +1,6 @@
 ---
 description: Product-specific guidance for Smart Accounts Kit documentation, including terminology, delegation concepts, glossary/tooltips, and versioning.
-globs:
-  [
-    'smart-accounts-kit/**/*.md',
-    'smart-accounts-kit/**/*.mdx',
-    'src/lib/glossary.json',
-    'scripts/generate-smart-accounts-glossary.js',
-  ]
+globs: smart-accounts-kit/**/*.md,smart-accounts-kit/**/*.mdx,src/lib/glossary.json
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/product-snaps.mdc b/.cursor/rules/product-snaps.mdc
@@ -1,6 +1,6 @@
 ---
 description: Product-specific guidance for Snaps documentation, including naming, content areas, and generated-content constraints.
-globs: ["snaps/**/*.md", "snaps/**/*.mdx"]
+globs: snaps/**/*.md,snaps/**/*.mdx
 alwaysApply: false
 ---
 
diff --git a/.cursor/rules/terminology.mdc b/.cursor/rules/terminology.mdc
@@ -1,6 +1,6 @@
 ---
 description: Required spelling and casing for product names, industry terms, and standards referenced across MetaMask documentation.
-globs: ['**/*.md', '**/*.mdx']
+globs: **/*.md,**/*.mdx
 alwaysApply: false
 ---
 
PATCH

echo "Gold patch applied."
