#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opentrons

# Idempotency guard
if grep -qF "- CSS file names should be `snake_case` and match the component name, followed b" ".cursor/rules/css-modules.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/css-modules.mdc b/.cursor/rules/css-modules.mdc
@@ -7,10 +7,16 @@ globs: '**/*.module.css'
 
 ### File Naming Convention
 
-- CSS file name should be component name (all lowercase) followed by `.module.css`
-- Example: `navbar.module.css`, `button.module.css`, `modal.module.css`
+- CSS file names should be `snake_case` and match the component name, followed by `.module.css`.
+- Example: `navbar.module.css`, `primary_button.module.css`, `modal_shell.module.css`
 
-### CSS Variables Usage
+### Class Naming Convention
+
+- Use `snake_case` for class names with a clear `component_element` structure.
+- Use descriptive names that reflect the element's purpose within the component.
+- Example: `.navbar_link`, `.modal_header`, `.primary_button_label`
+
+### CSS Variables (Design Tokens)
 
 - **MUST USE** CSS variables from `components/src/styles/global.css` for:
 
@@ -25,17 +31,37 @@ globs: '**/*.module.css'
 - **DO NOT USE** CSS variables for:
   - `width` and `height` - use explicit values (e.g., `2rem`, `100vh`, `5.625rem`)
 
-### CSS Class Naming
+### Dynamic Classes with `clsx`
+
+- This repo uses `clsx` (https://github.com/lukeed/clsx) for conditionally applying classes.
+
+- **Example:**
+
+  ```tsx
+  import clsx from 'clsx'
+  import styles from './my_component.module.css'
+
+  interface MyComponentProps {
+    isDisabled: boolean
+    children: React.ReactNode
+  }
+
+  export const MyComponent = ({ isDisabled, children }: MyComponentProps) => {
+    const className = clsx(styles.base_style, {
+      [styles.disabled_style]: isDisabled,
+    })
 
-- Use snake_case for class names (e.g., `.navbar_link`, `.nav_container`, `.bottom_container`)
-- Use descriptive names that reflect the component's purpose
+    return <div className={className}>{children}</div>
+  }
+  ```
 
 ### Global Selectors
 
-- When targeting React Router or other global classes, use `:global()` syntax
-- Example: `.navbar_link:global(.active)` for React Router's active class
+- When targeting React Router or other global classes, use the `:global()` syntax.
+- Example: `.navbar_link:global(.active)` for React Router's active class.
 
-### Linting
+### Linting and Formatting
 
-- Always check CSS Modules files follow stylelint by running `make lint-css`
-- Ensure all styles pass linting before committing
+- Always check that CSS Modules files follow stylelint by running `make lint-css`.
+- If linting fails, you can often fix issues by running `make format-css`.
+- Ensure all styles pass linting before committing.
\ No newline at end of file
PATCH

echo "Gold patch applied."
