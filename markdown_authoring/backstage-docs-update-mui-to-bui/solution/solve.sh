#!/usr/bin/env bash
set -euo pipefail

cd /workspace/backstage

# Idempotency guard
if grep -qF "- `Button` - Action buttons (`variant=\"primary\"`, `variant=\"secondary\"`, `varian" "docs/.well-known/skills/mui-to-bui-migration/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/docs/.well-known/skills/mui-to-bui-migration/SKILL.md b/docs/.well-known/skills/mui-to-bui-migration/SKILL.md
@@ -29,44 +29,51 @@ Before starting migration:
 
 - `Box` - Basic layout container with CSS properties
 - `Container` - Centered content container with max-width
+- `Flex` - Flex layout component
+- `FullPage` - Full-page layout wrapper
 - `Grid` - CSS Grid-based layout (`Grid.Root`, `Grid.Item`)
-- `Flex` - `Flexbox` layout component
 
 ### UI Components
 
-- `Accordion` - Collapsible content panels
+- `Accordion` - Collapsible content panels (`Accordion`, `AccordionTrigger`, `AccordionPanel`, `AccordionGroup`)
+- `Alert` - Alert/notification banners (`status`, `title`, `description`)
 - `Avatar` - User/entity avatars
-- `Button` - Primary action buttons (`variant="primary"`, `variant="secondary"`, `isDisabled`)
+- `Button` - Action buttons (`variant="primary"`, `variant="secondary"`, `variant="tertiary"`, `isDisabled`, `destructive`, `loading`)
 - `ButtonIcon` - Icon-only buttons (`icon`, `onPress`, `variant`)
 - `ButtonLink` - Link styled as button
 - `Card` - Content cards (`Card`, `CardHeader`, `CardBody`, `CardFooter`)
 - `Checkbox` - Checkbox input
 - `Dialog` - Modal dialogs (`DialogTrigger`, `Dialog`, `DialogHeader`, `DialogBody`, `DialogFooter`)
-- `Header` - Page headers
-- `Header` - Full page header component
+- `FieldLabel` - Form field label with description and secondary label
+- `Header` - Page headers with breadcrumbs and tabs
 - `Link` - Navigation links
-- `Menu` - Dropdown menus (`MenuTrigger`, `Menu`, `MenuItem`)
+- `List` - List component (`List`, `ListRow`)
+- `Menu` - Dropdown menus (`MenuTrigger`, `Menu`, `MenuItem`, `MenuSection`, `MenuSeparator`, `SubmenuTrigger`)
 - `PasswordField` - Password input field
+- `PluginHeader` - Plugin-level header with icon, title, tabs, and actions
 - `Popover` - Popover overlays
-- `RadioGroup` - Radio button groups
+- `RadioGroup` - Radio button groups (`RadioGroup`, `Radio`)
+- `SearchAutocomplete` - Search input with autocomplete popover (`SearchAutocomplete`, `SearchAutocompleteItem`)
 - `SearchField` - Search input
-- `Select` - Dropdown select
+- `Select` - Dropdown select (single and multiple selection modes)
 - `Skeleton` - Loading skeleton
 - `Switch` - Toggle switch
-- `Table` - Data tables
+- `Table` - Data tables (with `useTable` hook for data management)
+- `TablePagination` - Standalone pagination component
 - `Tabs` - Tab navigation (`Tabs`, `TabList`, `Tab`, `TabPanel`)
 - `Tag` - Tag/chip component (replaces MUI Chip)
 - `TagGroup` - Tag/chip groups
-- `Text` - Typography component (`variant`, `color`)
+- `Text` - Typography component (`variant`, `color`, `weight`, `truncate`)
 - `TextField` - Text input (`isRequired`, `onChange` receives string directly)
 - `ToggleButton` - Toggle buttons
 - `ToggleButtonGroup` - Grouped toggle buttons
-- `Tooltip` - Tooltip overlays (used with TooltipTrigger from react-aria-components)
+- `Tooltip` - Tooltip overlays (`TooltipTrigger`, `Tooltip` — both from `@backstage/ui`)
 - `VisuallyHidden` - Accessibility helper
 
 ### Hooks
 
 - `useBreakpoint` - Responsive breakpoint hook
+- `useTable` - Table data management hook (supports `complete`, `offset`, and `cursor` pagination modes)
 
 ## Migration Patterns
 
@@ -145,7 +152,7 @@ function MyComponent() {
 @layer components {
   .container {
     padding: var(--bui-space-4);
-    background-color: var(--bui-bg-surface-1);
+    background-color: var(--bui-bg-neutral-1);
     border-radius: var(--bui-radius-2);
   }
 
@@ -324,19 +331,14 @@ me < /span>
 **After (BUI TooltipTrigger pattern):**
 
 ```typescript
-import {Tooltip, Text} from '@backstage/ui';
-import {TooltipTrigger} from 'react-aria-components';
+import { Tooltip, TooltipTrigger, Text } from '@backstage/ui';
 
 <TooltipTrigger>
-  <Text>Hover
-me < /Text>
-< Tooltip > Tooltip
-content < /Tooltip>
-< /TooltipTrigger>;
+  <Text>Hover me</Text>
+  <Tooltip>Tooltip content</Tooltip>
+</TooltipTrigger>;
 ```
 
-Note: Add `react-aria-components` to your dependencies.
-
 ### 7. Dialog Pattern
 
 **Before (MUI Dialog):**
@@ -549,75 +551,38 @@ variant = "secondary" / >
   < /MenuTrigger>;
 ```
 
-### 12. List to HTML with CSS Modules
+### 12. List to BUI List
 
 **Before (MUI List):**
 
 ```typescript
-import {List, ListItem, ListItemIcon, ListItemText} from '@material-ui/core';
+import { List, ListItem, ListItemIcon, ListItemText } from '@material-ui/core';
 
 <List>
   <ListItem>
     <ListItemIcon>
-      <SomeIcon / >
-</ListItemIcon>
-< ListItemText
-primary = "Title"
-secondary = "Description" / >
+      <SomeIcon />
+    </ListItemIcon>
+    <ListItemText primary="Title" secondary="Description" />
   </ListItem>
-  < /List>;
+</List>;
 ```
 
-**After (HTML list with BUI and CSS Modules):**
-
-```css
-/* MyList.module.css */
-@layer components {
-  .list {
-    list-style: none;
-    padding: 0;
-    margin: 0;
-  }
-
-  .listItem {
-    display: flex;
-    align-items: flex-start;
-    padding: var(--bui-space-2) 0;
-  }
-
-  .listItemIcon {
-    min-width: 36px;
-    display: flex;
-    align-items: center;
-    color: var(--bui-fg-primary);
-  }
-}
-```
+**After (BUI List):**
 
 ```typescript
-import {Flex, Text} from '@backstage/ui';
-import {RiSomeIcon} from '@remixicon/react';
-import styles from './MyList.module.css';
+import { List, ListRow } from '@backstage/ui';
+import { RiSomeIcon } from '@remixicon/react';
 
-<ul className = {styles.list} >
-<li className = {styles.listItem} >
-<div className = {styles.listItemIcon} >
-<RiSomeIcon size = {20}
-/>
-< /div>
-< Flex
-direction = "column" >
-  <Text>Title < /Text>
-  < Text
-variant = "body-small"
-color = "secondary" >
-  Description
-  < /Text>
-  < /Flex>
-  < /li>
-  < /ul>;
+<List>
+  <ListRow icon={<RiSomeIcon size={20} />} description="Description">
+    Title
+  </ListRow>
+</List>;
 ```
 
+Note: `ListRow` supports `icon`, `description`, `menuItems`, and `customActions` props.
+
 ### 13. Chip to Tag
 
 **Before (MUI Chip):**
@@ -636,7 +601,39 @@ import {Tag} from '@backstage/ui';
 <Tag size = "small" > Category < /Tag>;
 ```
 
-### 14. Icons: MUI Icons to Remix Icons
+### 14. Alert Pattern
+
+**Before (MUI Alert):**
+
+```typescript
+import { Alert, AlertTitle } from '@material-ui/lab';
+
+<Alert severity="error">
+  <AlertTitle>Error</AlertTitle>
+  Something went wrong.
+</Alert>;
+```
+
+**After (BUI Alert):**
+
+```typescript
+import { Alert } from '@backstage/ui';
+
+<Alert
+  status="danger"
+  icon
+  title="Error"
+  description="Something went wrong."
+/>;
+```
+
+Status mapping: `severity="error"` → `status="danger"`, `severity="warning"` → `status="warning"`,
+`severity="info"` → `status="info"`, `severity="success"` → `status="success"`.
+
+Set `icon` to `true` for automatic status icons, or pass a custom `ReactElement`.
+Use `loading` for a loading spinner, and `customActions` for action buttons.
+
+### 15. Icons: MUI Icons to Remix Icons
 
 **Before (MUI Icons):**
 
@@ -705,12 +702,12 @@ Find more icons at: https://remixicon.com/
 | -------------------- | ------------------------------------------ |
 | `text.primary`       | `var(--bui-fg-primary)`                    |
 | `text.secondary`     | `var(--bui-fg-secondary)`                  |
-| `background.paper`   | `var(--bui-bg-surface-1)`                  |
-| `background.default` | `var(--bui-bg-surface-0)`                  |
+| `background.paper`   | `var(--bui-bg-neutral-1)`                  |
+| `background.default` | `var(--bui-bg-app)`                        |
 | `primary.main`       | `var(--bui-bg-solid)` or `var(--bui-ring)` |
 | `error.main`         | `var(--bui-fg-danger)`                     |
-| `action.hover`       | `var(--bui-bg-hover)`                      |
-| `divider`            | `var(--bui-border)`                        |
+| `action.hover`       | `var(--bui-bg-neutral-1-hover)`            |
+| `divider`            | `var(--bui-border-1)`                      |
 
 ### Typography
 
@@ -730,7 +727,7 @@ Find more icons at: https://remixicon.com/
 | Border radius small  | `var(--bui-radius-2)`    |
 | Border radius medium | `var(--bui-radius-3)`    |
 | Border radius full   | `var(--bui-radius-full)` |
-| Link color           | `var(--bui-fg-link)`     |
+| Link color           | `var(--bui-fg-info)`     |
 
 ## Known Limitations
 
@@ -739,8 +736,6 @@ Some Backstage APIs still require MUI-compatible icon types:
 - **NavItemBlueprint** (`@backstage/frontend-plugin-api`): The `icon` prop expects MUI `IconComponent` type. Remix icons
   are not type-compatible.
 - **Timeline** (`@material-ui/lab`): No BUI equivalent exists.
-- **Pagination** (`@material-ui/lab`): No BUI equivalent exists.
-- **Alert** (`@material-ui/lab`): No BUI equivalent exists.
 
 For these cases, keep using MUI components.
 
@@ -750,29 +745,31 @@ When migrating a plugin:
 
 1. [ ] Add `@backstage/ui` dependency
 2. [ ] Add `@remixicon/react` dependency (if using icons)
-3. [ ] Add `react-aria-components` dependency (if using Tooltip)
-4. [ ] Add CSS import to root file
-5. [ ] Remove `@material-ui/core` imports (except components with no BUI equivalent)
-6. [ ] Remove `@material-ui/icons` imports
+3. [ ] Add CSS import to root file
+4. [ ] Remove `@material-ui/core` imports (except components with no BUI equivalent)
+5. [ ] Remove `@material-ui/icons` imports
+6. [ ] Remove `@material-ui/lab` imports (Alert, Pagination now in BUI)
 7. [ ] Remove `makeStyles` and related imports
 8. [ ] Create `.module.css` files for component styles
 9. [ ] Replace `Typography` with `Text`
 10. [ ] Replace `Box display="flex"` with `Flex`
 11. [ ] Replace `Grid container/item` with `Grid.Root/Grid.Item`
 12. [ ] Replace `Paper` with `Card`
 13. [ ] Replace MUI `Dialog` with BUI `DialogTrigger` pattern
-14. [ ] Replace MUI `Tooltip` with BUI `TooltipTrigger` pattern
+14. [ ] Replace MUI `Tooltip` with BUI `TooltipTrigger` pattern (both from `@backstage/ui`)
 15. [ ] Replace MUI `Tabs` with BUI `Tabs`
 16. [ ] Replace MUI `Menu` with BUI `MenuTrigger` pattern
 17. [ ] Replace `Chip` with `Tag`
 18. [ ] Replace `IconButton` with `ButtonIcon`
-19. [ ] Update `Button` props (`disabled` → `isDisabled`, `variant="contained"` → `variant="primary"`)
-20. [ ] Update `TextField` props (`required` → `isRequired`, `onChange` signature)
-21. [ ] Replace MUI icons with Remix icons
-22. [ ] Run `yarn tsc` to check for type errors
-23. [ ] Run `yarn build` to verify build
-24. [ ] Run `yarn lint` to check for missing dependencies
-25. [ ] Test component rendering and functionality
+19. [ ] Replace MUI `Alert` with BUI `Alert`
+20. [ ] Replace MUI `List` with BUI `List` and `ListRow`
+21. [ ] Update `Button` props (`disabled` → `isDisabled`, `variant="contained"` → `variant="primary"`)
+22. [ ] Update `TextField` props (`required` → `isRequired`, `onChange` signature)
+23. [ ] Replace MUI icons with Remix icons
+24. [ ] Run `yarn tsc` to check for type errors
+25. [ ] Run `yarn build` to verify build
+26. [ ] Run `yarn lint` to check for missing dependencies
+27. [ ] Test component rendering and functionality
 
 ## Reference
 
PATCH

echo "Gold patch applied."
