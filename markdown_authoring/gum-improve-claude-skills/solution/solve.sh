#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gum

# Idempotency guard
if grep -qF "name: gum-property-assignment" ".claude/skills/gum-property-assignment/SKILL.md" && grep -qF "`StartUp()` is called once on load \u2014 subscribe to events here. `ShutDown(PluginS" ".claude/skills/gum-tool-plugins/SKILL.md" && grep -qF "name: gum-tool-save-classes" ".claude/skills/gum-tool-save-classes/SKILL.md" && grep -qF "When a locked instance is selected and the cursor is over one of its polygon ver" ".claude/skills/gum-tool-selection/SKILL.md" && grep -qF "name: gum-tool-undo" ".claude/skills/gum-tool-undo/SKILL.md" && grep -qF "`PropertyGridManager.RefreshDataGrid` tracks the previous display target (elemen" ".claude/skills/gum-tool-variable-grid/SKILL.md" && grep -qF ".claude/skills/variable-grid/SKILL.md" ".claude/skills/variable-grid/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/gum-property-assignment/SKILL.md b/.claude/skills/gum-property-assignment/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: property-assignment
+name: gum-property-assignment
 description: Reference guide for how Gum applies variables and sets properties on renderables. Load this when working on ApplyState, SetProperty, SetVariablesRecursively, CustomSetPropertyOnRenderable, font loading, IsAllLayoutSuspended, or isFontDirty.
 ---
 
diff --git a/.claude/skills/gum-tool-plugins/SKILL.md b/.claude/skills/gum-tool-plugins/SKILL.md
@@ -0,0 +1,75 @@
+---
+name: gum-tool-plugins
+description: Reference guide for the Gum tool's plugin system. Load this when working on plugin registration, PluginBase, InternalPlugin, PluginManager, plugin events, or finding which internal plugin owns a feature.
+---
+
+# Gum Tool Plugin System Reference
+
+## Architecture
+
+The plugin system uses MEF (Managed Extensibility Framework) for discovery. All plugins are marked with `[Export(typeof(PluginBase))]` and auto-discovered at startup.
+
+### Class Hierarchy
+
+- `IPlugin` — minimal interface: `StartUp()`, `ShutDown(PluginShutDownReason)`, `FriendlyName`, `UniqueId`, `Version`
+- `PluginBase` — concrete base with all event declarations and pre-injected helper services (`_guiCommands`, `_fileCommands`, `_tabManager`, `_menuStripManager`, `_dialogService`)
+- `InternalPlugin` — base for internal plugins; provides default `ShutDown()` returning `false` and auto-generates `FriendlyName`
+
+### Internal vs. External
+
+**Internal plugins** live in `Gum/Plugins/InternalPlugins/`, inherit from `InternalPlugin`, and are compiled into Gum.exe.
+
+**External plugins** are separate .dlls loaded from `[GumExecutableDirectory]\Plugins\` at runtime. They inherit from `PluginBase` directly.
+
+The type check `is InternalPlugin` is used at runtime — internal plugins receive events before external ones.
+
+## Key Files
+
+| File | Purpose |
+|------|---------|
+| `Gum/Plugins/BaseClasses/PluginBase.cs` | All event declarations + helper services |
+| `Gum/Plugins/BaseClasses/InternalPlugin.cs` | Base for internal plugins |
+| `Gum/Plugins/PluginManager.cs` | Loads plugins via MEF, routes all events via `Call*` methods |
+| `Gum/Plugins/PluginContainer.cs` | Wraps each plugin; tracks enabled state and failure info |
+| `Gum/Plugins/InternalPlugins/` | All built-in plugin subfolders |
+
+## Plugin Lifecycle
+
+`StartUp()` is called once on load — subscribe to events here. `ShutDown(PluginShutDownReason)` is called on unload. Service dependencies are injected via `Locator.GetRequiredService<T>()` (typically called in the constructor, not `StartUp`). If any plugin handler throws, `PluginContainer` disables that plugin for the rest of the session.
+
+## Internal Plugin Map
+
+Each internal plugin lives in `Gum/Plugins/InternalPlugins/[FeatureName]/` with a `Main[FeatureName]Plugin.cs` entry point.
+
+| Feature | Plugin Folder |
+|---------|--------------|
+| Element tree view | `TreeView/` |
+| Variables/Properties tab | `VariableGrid/` |
+| State panel | `StatePlugin/` |
+| Behaviors panel | `Behaviors/` |
+| Output panel | `Output/` |
+| Alignment controls | `AlignmentButtons/` |
+| Menu strip | `MenuStripPlugin/` |
+| Undo/History | `Undos/` |
+| Delete dialog | `Delete/` |
+
+## Common Events
+
+All events are defined on `PluginBase` — subscribe in `StartUp()`. The full list is in `PluginBase.cs`. Most-used categories:
+
+- **Selection**: `ElementSelected`, `InstanceSelected`, `ReactToStateSaveSelected`, `BehaviorSelected`, `TreeNodeSelected`
+- **Variable changes**: `VariableSet`, `VariableSetLate`
+- **Element lifecycle**: `ElementAdd`, `ElementDelete`, `ElementRename`, `ElementDuplicate`, `ElementReloaded`
+- **Instance lifecycle**: `InstanceAdd`, `InstanceDelete`, `InstanceRename`, `InstanceReordered`
+- **Project**: `ProjectLoad`, `BeforeProjectSave`, `AfterProjectSave`
+- **Wireframe**: `WireframeRefreshed`, `BeforeRender`, `AfterRender`, `CameraChanged`
+
+**Query events** (plugins return values to intercept behavior): `TryHandleDelete`, `GetSelectedIpsos`, `VariableExcluded`, `GetDeleteStateResponse`, `CreateGraphicalUiElement`
+
+## Non-Obvious Behaviors
+
+**Event ordering**: `PluginManager` sorts with `OrderBy(!(item is InternalPlugin))`, so internal plugins always handle events before external ones.
+
+**VariableSet vs. VariableSetLate**: Two events for the same change. Use `VariableSet` to respond to a change; use `VariableSetLate` for cleanup/refresh that should run after all other plugins have responded.
+
+**Finding which plugin owns a feature**: Search `StartUp()` methods for the event subscription. E.g., to find what handles `VariableSet`, grep for `VariableSet +=` in `InternalPlugins/`. The subscribing plugin is the owner.
diff --git a/.claude/skills/gum-tool-save-classes/SKILL.md b/.claude/skills/gum-tool-save-classes/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: gum-save-classes
+name: gum-tool-save-classes
 description: Reference guide for Gum's save/load data model. Load this when working with GumProjectSave, ScreenSave, ComponentSave, StandardElementSave, ElementSave, StateSave, VariableSave, InstanceSave, BehaviorSave, or any serialization/deserialization of Gum project files.
 ---
 
diff --git a/.claude/skills/gum-tool-selection/SKILL.md b/.claude/skills/gum-tool-selection/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: selection-system
+name: gum-tool-selection
 description: Reference guide for Gum's editor selection system. Load this when working on click/drag selection, the rectangle/marquee selector, input handlers (move, resize, rotate, polygon points), the IsActive flag, locked instance behavior, or SelectionManager coordination.
 ---
 
@@ -30,57 +30,25 @@ Mouse drag  → OnDrag()          → only meaningful when IsActive; applies tra
 Mouse up    → OnRelease()       → cleans up; resets IsActive to false
 ```
 
-`HandlePush` returns `bool`:
-- `true` — this handler claims the gesture; `IsActive` becomes `true`
-- `false` — this handler passes; another handler or the rectangle selector may act
+`HandlePush` returns `bool`: `true` means this handler claims the gesture and sets `IsActive = true`; `false` passes to the next handler or the rectangle selector.
 
 ### `IsActive` Flag
 
-`IsActive = true` signals that a handler owns the current drag gesture. It is the critical signal used to suppress the rectangle selector (see below). It must be set to `true` in `HandlePush` when claiming a gesture, and reset to `false` in `OnRelease`.
+`IsActive = true` signals that a handler owns the current drag gesture. It suppresses the rectangle selector — `SelectionManager` passes `isHandlerActive = true` to `RectangleSelector.HandleDrag`, which returns immediately. Must be set in `HandlePush` when claiming a gesture and reset in `OnRelease`.
 
 The base class `HandlePush` automatically checks `Context.IsSelectionLocked()` and returns `false` if locked. Handlers that **override** `HandlePush` must replicate or explicitly call this check.
 
 ## Rectangle Selector (Marquee Selection)
 
 **File:** `Tool/EditorTabPlugin_XNA/RectangleSelector.cs`
 
-The rectangle selector activates on drag when **no handler is active** and the cursor is **not over the element body** (or Shift is held for additive selection).
+The rectangle selector activates on drag when no handler is active and the cursor is not over the element body (or Shift is held for additive selection), after a minimum drag distance is exceeded. `SelectionManager` passes `isHandlerActive` based on whether any handler's `IsActive` is `true`.
 
-### Activation Condition (in `HandleDrag`)
-
-```csharp
-public void HandleDrag(bool isHandlerActive = false)
-{
-    if (isHandlerActive) return;  // suppressed when any handler owns the gesture
-
-    bool shouldActivate = multiSelectKeyHeld || !_selectionManager.IsOverBody;
-    if (!shouldActivate) return;
-
-    // ... activates after MinimumDragDistance is exceeded
-}
-```
-
-`isHandlerActive` is passed by `SelectionManager` based on whether any handler's `IsActive` is `true`. The rectangle selector also receives this flag in `Update()` to control visual visibility.
-
-### What It Selects
-
-`GetElementsInRectangle()` finds all visible elements whose bounds intersect the drag rectangle. It skips:
-- `ScreenSave` elements (screens can't be rectangle-selected)
-- `InstanceSave` elements where `Locked == true`
-
-On release, it either replaces the selection or toggles elements additively (Shift held).
+`GetElementsInRectangle()` finds visible elements whose bounds intersect the drag rectangle, skipping `ScreenSave` elements and instances where `Locked == true`. On release, it either replaces the selection or toggles additively (Shift held).
 
 ## Locking (`InstanceSave.Locked`)
 
-### Key Property and Helper
-
-```csharp
-// GumDataTypes/InstanceSave.cs
-public bool Locked { get; set; }
-
-// Tool/EditorTabPlugin_XNA/Editors/EditorContext.cs
-public bool IsSelectionLocked() => SelectedState.SelectedInstance?.Locked == true;
-```
+`InstanceSave.Locked` is defined in `GumDataTypes/InstanceSave.cs`. The helper `EditorContext.IsSelectionLocked()` (in `Tool/EditorTabPlugin_XNA/Editors/EditorContext.cs`) returns `true` when the selected instance is locked.
 
 ### Where Locking Is Enforced
 
@@ -101,36 +69,19 @@ public bool IsSelectionLocked() => SelectedState.SelectedInstance?.Locked == tru
 
 ### Locked + IsActive Interaction (Critical)
 
-When a locked instance is selected and the cursor is over one of its **polygon verts**, the following must happen in `HandlePush`:
-
-1. Detect cursor is over a vert (`GetIndexOver` returns non-null)
-2. Set `IsActive = true` — this suppresses the rectangle selector
-3. Do **not** set `_grabbedIndex` — this ensures `OnDrag` is a no-op
-4. Return `true` — consume the push
-
-Without step 2, the rectangle selector activates on drag because `isHandlerActive` is `false` and the cursor over a vert is typically not "over body".
+When a locked instance is selected and the cursor is over one of its polygon verts, `PolygonPointInputHandler.HandlePush` must: detect the vert, set `IsActive = true` (to suppress the rectangle selector), but not set `_grabbedIndex` (so `OnDrag` is a no-op), and return `true` to consume the push. Without setting `IsActive`, the rectangle selector activates on drag because the cursor over a vert is typically not "over body".
 
 ### Locked Selection Display
 
-When a locked instance is selected in the standard (non-polygon) editor, `LockedSelectionVisual` draws a dashed bounding rectangle using the same line color as resize handles. This replaces the resize handles that would normally appear. The outline is shown **regardless of the instance's `Visible` property**, so the user can always locate a locked object selected from the tree view.
-
-`LockedSelectionVisual` is registered in `StandardWireframeEditor` and integrates with the standard `IEditorVisual` lifecycle (`UpdateToSelection` / `Update` / `Destroy`). It is not used in `PolygonWireframeEditor` because polygon point nodes already provide a visual for locked polygon selections.
+`LockedSelectionVisual` draws a dashed bounding rectangle for a locked selected instance, replacing the resize handles that would normally appear. It shows regardless of the instance's `Visible` property. Registered in `StandardWireframeEditor`; not used in `PolygonWireframeEditor`.
 
 ### Locked Instances Are Still Tree-Selectable
 
-Locked instances cannot be selected by clicking on the canvas or by the rectangle selector, but **can always be selected via the tree view**. This is intentional — tree view selection is the only way for users to select a locked instance so they can unlock it.
-
-Multi-selection (via tree view) of mixed locked/unlocked instances is supported. Transforms (move/resize) apply only to the unlocked members of the selection; locked members stay put.
+Locked instances cannot be canvas-clicked or rectangle-selected, but **can always be selected via the tree view** — the only way to select a locked instance to unlock it. Multi-selection of mixed locked/unlocked is supported; transforms apply only to unlocked members.
 
 ## `_lastPushWasOnLockedBody`
 
-Tracked in `SelectionManager.ProcessInputForSelection()`:
-
-```csharp
-_lastPushWasOnLockedBody = _selectedState.SelectedInstance?.Locked == true && IsOverBody;
-```
-
-Used in `ProcessRectangleSelection()` to prevent deselection when the user releases the mouse over a locked instance body without dragging. Without this, clicking on a locked body would deselect it.
+Tracked in `SelectionManager.ProcessInputForSelection()` — set to `true` when the selected instance is locked and the cursor is over the body. Used in `ProcessRectangleSelection()` to prevent deselection when the user releases the mouse over a locked body without dragging.
 
 ## Key Files Summary
 
diff --git a/.claude/skills/gum-tool-undo/SKILL.md b/.claude/skills/gum-tool-undo/SKILL.md
@@ -1,5 +1,5 @@
 ---
-name: undo-system
+name: gum-tool-undo
 description: Reference guide for Gum's undo/redo system. Load this when working on undo/redo behavior, the History tab, UndoManager, UndoPlugin, UndoSnapshot, or stale reference issues after undo.
 ---
 
diff --git a/.claude/skills/gum-tool-variable-grid/SKILL.md b/.claude/skills/gum-tool-variable-grid/SKILL.md
@@ -0,0 +1,100 @@
+---
+name: gum-tool-variable-grid
+description: Reference guide for Gum's Variables tab and DataUiGrid system. Load this when working on the Variables tab, DataUiGrid control, MemberCategory, InstanceMember, category population, property grid refresh, or category expansion state persistence.
+---
+
+# Gum Variables Tab & DataUiGrid Reference
+
+## Overview
+
+The **Variables tab** displays and edits properties of the selected element, instance, state, or behavior. Built on `DataUiGrid` (a WPF `ItemsControl` subclass) from the `WpfDataUi` library. Categories render as collapsible `Expander` sections.
+
+---
+
+## Architecture Layers
+
+```
+[User selects object]
+        ↓
+[MainVariableGridPlugin] (event subscription)
+        ↓
+[PropertyGridManager.RefreshDataGrid()]
+        ↓
+[ElementSaveDisplayer.GetCategories()]
+        ↓ (produces List<MemberCategory>)
+[DataUiGrid.SetCategories()]
+        ↓
+[WPF Expander per MemberCategory, rows per InstanceMember]
+```
+
+---
+
+## Key Files
+
+| Purpose | File Path |
+|---------|-----------|
+| DataUiGrid control | `WpfDataUi/DataUiGrid.cs` |
+| DataUiGrid XAML template | `WpfDataUi/Themes/Generic.xaml` |
+| MemberCategory / InstanceMember models | `WpfDataUi/DataTypes/` |
+| Gum-specific member subclass | `Gum/Plugins/InternalPlugins/VariableGrid/StateReferencingInstanceMember.cs` |
+| Plugin wiring selection events | `Gum/Plugins/InternalPlugins/VariableGrid/MainVariableGridPlugin.cs` |
+| Category population manager | `Gum/Plugins/InternalPlugins/VariableGrid/PropertyGridManager.cs` |
+| Category factory | `Gum/Plugins/InternalPlugins/VariableGrid/ElementSaveDisplayer.cs` |
+| Behavior categories | `Gum/Plugins/InternalPlugins/VariableGrid/BehaviorShowingLogic.cs` |
+| Host UserControl | `Gum/Plugins/InternalPlugins/VariableGrid/MainPropertyGrid.xaml(.cs)` |
+
+---
+
+## Non-Obvious Behaviors
+
+### SetCategories Expansion Preservation
+
+`DataUiGrid.SetCategories()` captures `{name → IsExpanded}` from existing categories, replaces the list, then re-applies the saved values by name. Category collapse state persists across selection changes within a session. `IsExpanded` is `Mode=TwoWay` in the XAML template so user gestures write back to the model immediately.
+
+### Structural Rebuild vs. Partial Refresh
+
+`PropertyGridManager.RefreshDataGrid` tracks the previous display target (element, state, instances, behavior). If unchanged and `force=false`, it calls `Refresh()` to update values without recreating categories. If the target changed, it calls `SetCategories` with a fresh list from `ElementSaveDisplayer`. Pass `force: true` to always rebuild.
+
+### Multi-Select Path
+
+When multiple instances are selected, `SetMultipleCategoryLists` is used instead of `SetCategories`. `MultiSelectInstanceMember` wrappers coordinate synchronized edits across all selected instances and record a single undo after all values are set.
+
+### StateReferencingInstanceMember
+
+All members in the Variables tab use `StateReferencingInstanceMember` (subclass of `InstanceMember`), not the generic reflection path. Its `IsReadOnly` returns `true` when `InstanceSave?.Locked == true`. Its `IsDefault` returns `true` when the value is absent from the selected state (not inherited from defaults).
+
+---
+
+## Refresh Trigger Flow
+
+```
+Selection changed
+  → MainVariableGridPlugin.Handle*Selected()
+  → PropertyGridManager.RefreshEntireGrid(force: true)
+  → RefreshDataGrid(...)
+     ├─ Target changed?
+     │   yes → ElementSaveDisplayer.GetCategories()
+     │          → DataUiGrid.SetCategories()     ← preserves IsExpanded by name
+     └─ Target same?
+             → DataUiGrid.Refresh()              ← only updates member values
+```
+
+Variable set by UI:
+```
+InstanceMember.AfterSetByUi
+  → StateReferencingInstanceMember.NotifyVariableLogic()
+  → PropertyGridManager.RefreshEntireGrid(force: false)
+  → DataUiGrid.Refresh()   (no structural rebuild needed)
+```
+
+---
+
+## Common Patterns
+
+### Making a category collapsed by default
+
+Set `IsExpanded = false` on the `MemberCategory` before passing to `SetCategories`. The first time the category appears it uses the incoming value; subsequent appearances restore the user's last state.
+
+### Forcing a full grid rebuild
+
+Call `PropertyGridManager.RefreshEntireGrid(force: true)`. The `force` flag bypasses the same-target optimization and always recreates categories.
diff --git a/.claude/skills/variable-grid/SKILL.md b/.claude/skills/variable-grid/SKILL.md
@@ -1,254 +0,0 @@
----
-name: variable-grid
-description: Reference guide for Gum's Variables tab and DataUiGrid system. Load this when working on the Variables tab, DataUiGrid control, MemberCategory, InstanceMember, category population, property grid refresh, or category expansion state persistence.
----
-
-# Gum Variables Tab & DataUiGrid Reference
-
-## Overview
-
-The **Variables tab** in the Gum editor displays and edits the properties of the currently selected element, instance, state, or behavior. It is built on top of the `DataUiGrid` WPF control from the `WpfDataUi` library. Categories of properties are represented as collapsible `Expander` sections.
-
----
-
-## Architecture Layers
-
-```
-[User selects object]
-        ↓
-[MainVariableGridPlugin] (event subscription)
-        ↓
-[PropertyGridManager.RefreshDataGrid()]
-        ↓
-[ElementSaveDisplayer.GetCategories()]
-        ↓ (produces List<MemberCategory>)
-[DataUiGrid.SetCategories()]
-        ↓
-[WPF Expander per MemberCategory, rows per InstanceMember]
-```
-
----
-
-## Key Files
-
-| Purpose | File Path |
-|---------|-----------|
-| DataUiGrid control | `WpfDataUi/DataUiGrid.cs` |
-| DataUiGrid XAML template | `WpfDataUi/Themes/Generic.xaml` |
-| MemberCategory model | `WpfDataUi/DataTypes/MemberCategory.cs` |
-| InstanceMember model | `WpfDataUi/DataTypes/InstanceMember.cs` |
-| Gum-specific member subclass | `Gum/Plugins/InternalPlugins/VariableGrid/StateReferencingInstanceMember.cs` |
-| Plugin wiring selection events | `Gum/Plugins/InternalPlugins/VariableGrid/MainVariableGridPlugin.cs` |
-| Category population manager | `Gum/Plugins/InternalPlugins/VariableGrid/PropertyGridManager.cs` |
-| Category factory | `Gum/Plugins/InternalPlugins/VariableGrid/ElementSaveDisplayer.cs` |
-| Behavior categories | `Gum/Plugins/InternalPlugins/VariableGrid/BehaviorShowingLogic.cs` |
-| Host UserControl | `Gum/Plugins/InternalPlugins/VariableGrid/MainPropertyGrid.xaml(.cs)` |
-
----
-
-## DataUiGrid Control (`WpfDataUi/DataUiGrid.cs`)
-
-`DataUiGrid` is an `ItemsControl` subclass. Its items are `MemberCategory` objects.
-
-### Key Properties
-
-| Property | Type | Purpose |
-|----------|------|---------|
-| `Instance` | `object` (DependencyProperty) | Object being displayed; setting triggers `PopulateCategories()` |
-| `Categories` | `BulkObservableCollection<MemberCategory>` | The displayed categories (bound to ItemsSource) |
-| `TypesToIgnore` | collection | Types excluded from reflection-based population |
-| `MembersToIgnore` | collection | Member names excluded |
-
-### Key Methods
-
-| Method | Description |
-|--------|-------------|
-| `SetCategories(IList<MemberCategory>)` | Batch-replaces all categories, fires a single Reset notification, and **preserves `IsExpanded` state** by matching category names |
-| `SetMultipleCategoryLists(...)` | Multi-select editing path: merges multiple lists into `MultiSelectInstanceMember` wrappers |
-| `PopulateCategories()` | Reflection-based auto-population when `Instance` is set directly |
-| `RefreshDelegateBasedElementVisibility()` | Toggles member visibility based on conditional delegates |
-| `Refresh()` | Re-reads values without rebuilding the full structure |
-| `Apply(TypeMemberDisplayProperties)` | Applies display overrides (displayer type, read-only, etc.) to already-populated members |
-
-### `SetCategories` Expansion Preservation
-
-When `SetCategories` is called, it:
-1. Captures `{name → IsExpanded}` from the old categories.
-2. Replaces the category list.
-3. Re-applies the captured `IsExpanded` values to matching new categories by name.
-
-This ensures that collapsing a category persists across instance changes within a session.
-
-### XAML Template (`WpfDataUi/Themes/Generic.xaml`)
-
-```xml
-<DataTemplate x:Key="DataUi.MemberCategoryTemplate" DataType="{x:Type dataTypes:MemberCategory}">
-    <Expander Header="{Binding Name}" IsExpanded="{Binding IsExpanded, Mode=TwoWay}">
-        <ItemsControl AlternationCount="2" ItemsSource="{Binding Members}" />
-    </Expander>
-</DataTemplate>
-```
-
-`IsExpanded` uses `Mode=TwoWay` so user gestures (clicking the expander header) write back to the model, and programmatic resets (via `SetCategories`) are reflected in the UI.
-
----
-
-## MemberCategory (`WpfDataUi/DataTypes/MemberCategory.cs`)
-
-Groups related `InstanceMember` objects under a named header.
-
-### Key Properties
-
-| Property | Type | Default | Notes |
-|----------|------|---------|-------|
-| `Name` | `string` | — | Category display name |
-| `Members` | `ObservableCollection<InstanceMember>` | — | Members in this category |
-| `IsExpanded` | `bool` | `true` | Raises `PropertyChanged`; bound to Expander |
-| `HeaderColor` | `Brush?` | `null` | Optional header tint |
-| `HideHeader` | `bool` | `false` | Hides the category header entirely |
-| `Visibility` | computed | — | Collapsed when `Members.Count == 0` |
-
-### Events
-
-| Event | Fired When |
-|-------|-----------|
-| `PropertyChanged` | `IsExpanded`, `CategoryBorderThickness`, `Width`, `Visibility` change |
-| `MemberValueChangedByUi` | Any member in this category is edited by the user |
-
----
-
-## InstanceMember (`WpfDataUi/DataTypes/InstanceMember.cs`)
-
-Represents one editable row in the grid.
-
-### Key Properties
-
-| Property | Purpose |
-|----------|---------|
-| `Name` | Property/field name (used for lookup) |
-| `DisplayName` | Label shown in the UI |
-| `Value` | Gets/sets value via reflection or custom delegates |
-| `PropertyType` | The CLR type of the value |
-| `PreferredDisplayer` | Which control type to use (TextBox, ComboBox, etc.) |
-| `CustomOptions` | Options for ComboBox-style displayers |
-| `IsReadOnly` | Whether the field is editable |
-| `IsDefault` | Whether the value is the type default |
-| `IsIndeterminate` | For multi-select when values differ |
-| `Category` | Parent `MemberCategory` (set automatically on `Members.Add`) |
-
-### Custom Get/Set Delegates
-
-Instead of reflection, callers can assign:
-- `CustomGetEvent` — `Func<object, object>` to read value
-- `CustomSetEvent` — `Action<object, object>` to write value
-- `CustomGetTypeEvent` — `Func<object, Type>` to get property type
-- `CustomSetPropertyEvent` — for named property set with change-tracking
-
-### Key Events
-
-| Event | Purpose |
-|-------|---------|
-| `BeforeSetByUi` | Fired before user edits are committed |
-| `AfterSetByUi` | Fired after user edits; triggers refresh/undo |
-| `PropertyChanged` | Standard INotifyPropertyChanged |
-
----
-
-## StateReferencingInstanceMember (`VariableGrid/StateReferencingInstanceMember.cs`)
-
-Subclass of `InstanceMember` used for all members in the Variables tab (not the generic reflection path).
-
-### Additional Properties
-
-| Property | Purpose |
-|----------|---------|
-| `StateSave` | The state being edited |
-| `StateSaveCategory` | Category within state |
-| `InstanceSave` | The instance (null if editing the element itself) |
-| `ElementSave` | The parent element |
-| `RootVariableName` | Extracted from `Name`; handles nested paths like `"Child.Width"` |
-
-### Overrides
-
-- **`IsReadOnly`**: Returns `true` when `InstanceSave?.Locked == true` (and the variable is not `"Locked"` itself), preventing edits to locked instances.
-- **`IsDefault`**: Returns `true` when the value is strictly absent from the selected state (not inherited from defaults).
-
----
-
-## PropertyGridManager (`VariableGrid/PropertyGridManager.cs`)
-
-Central coordinator between selection state and the DataUiGrid.
-
-### Key Methods
-
-| Method | Description |
-|--------|-------------|
-| `RefreshEntireGrid(force)` | Entry point from plugin events; delegates to `RefreshDataGrid` |
-| `RefreshDataGrid(element, state, instances, behavior, category, force)` | Determines if a structural rebuild or partial refresh is needed, then calls `SetCategories` or `Refresh` |
-
-### Structural Rebuild vs. Partial Refresh
-
-`RefreshDataGrid` tracks the previous display target (element, state, instances, behavior). If unchanged and `force=false`, it only calls `mVariablesDataGrid.Refresh()` to update member values without recreating categories. If the target changed, it calls `SetCategories` with freshly created categories.
-
-### Multi-Select Path
-
-When multiple instances are selected, `SetMultipleCategoryLists` is used instead of `SetCategories`. `MultiSelectInstanceMember` wrappers coordinate synchronized edits across all instances and record a single undo after all values are set.
-
----
-
-## ElementSaveDisplayer (`VariableGrid/ElementSaveDisplayer.cs`)
-
-Factory that produces `List<MemberCategory>` for a given element/state/instance.
-
-### Key Methods
-
-| Method | Description |
-|--------|-------------|
-| `GetCategories(element, state, instance, ...)` | Main entry point; returns populated category list |
-| `GetProperties(...)` | Assembles `PropertyData` list (handles variable inheritance, exposed variables, etc.) |
-| `CreateSrimFromPropertyData(...)` | Creates a `StateReferencingInstanceMember` and wires up its delegates |
-
-Categories are created anew on each call. The expansion state is preserved by `DataUiGrid.SetCategories`, not here.
-
----
-
-## Refresh Trigger Flow
-
-```
-Selection changed
-  → MainVariableGridPlugin.Handle*Selected()
-  → PropertyGridManager.RefreshEntireGrid(force: true)
-  → RefreshDataGrid(...)
-     ├─ Target changed?
-     │   yes → ElementSaveDisplayer.GetCategories()
-     │          → DataUiGrid.SetCategories()     ← preserves IsExpanded by name
-     └─ Target same?
-             → DataUiGrid.Refresh()              ← only updates member values
-```
-
-Variable set by UI:
-```
-InstanceMember.AfterSetByUi
-  → StateReferencingInstanceMember.NotifyVariableLogic()
-  → PropertyGridManager.RefreshEntireGrid(force: false)
-  → DataUiGrid.Refresh()   (no structural rebuild needed)
-```
-
----
-
-## Common Patterns
-
-### Adding a new variable to the Variables tab
-
-Variables shown in the tab come from `ElementSave.DefaultState` variables. To add a new one:
-1. Create a `VariableSave` and add it to the element's state in the data model.
-2. `ElementSaveDisplayer.GetProperties()` will pick it up automatically on the next refresh.
-3. To customize the displayer or category, handle the `GetDisplayer` plugin event.
-
-### Making a category collapsed by default
-
-Set `IsExpanded = false` on the `MemberCategory` object after creating it, before passing to `SetCategories`. Because `SetCategories` only restores expansion state for categories **already seen** by the user, the first time a category appears it will use whatever `IsExpanded` is set on the incoming category object.
-
-### Forcing a full grid rebuild
-
-Call `PropertyGridManager.RefreshEntireGrid(force: true)`. The `force` flag bypasses the same-target optimization and always recreates categories.
PATCH

echo "Gold patch applied."
