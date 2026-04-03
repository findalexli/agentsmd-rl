# Chat Customizations: Support Grouping and Badges for External Provider Items

## Problem

When the Chat Customizations editor displays items from an external provider (e.g., Copilot CLI), they are rendered as a flat, ungrouped list. There is no way for providers to organize their items into logical groups (like "Agent Instructions", "Loaded On Demand"), and no way to show inline badges (like `applyTo` glob patterns) next to item names.

Additionally, external provider items have no automatic storage inference — they don't get categorized into Workspace/User/Plugin groups the way native items do, so the grouping UI breaks down.

## Expected Behavior

1. **Interface extensions**: `IExternalCustomizationItem` (in `customizationHarnessService.ts`) should support optional `groupKey`, `badge`, and `badgeTooltip` fields. These fields must propagate through the full API chain — from the proposed extension API type, through the IPC DTO, ExtHost mapping, MainThread mapping, and the internal interface.

2. **Storage inference**: The list widget should infer storage (workspace vs. user) from item URIs by checking workspace folders, active project root, and user data prompts home.

3. **Group-by-groupKey**: When provider items have `groupKey` set, `filterItems` should group them under collapsible headers keyed by `groupKey`. Items without a `groupKey` should fall into a fallback group. When no items have explicit groups, fall through to standard storage-based grouping.

4. **Documentation**: The project's skill file for the chat customizations editor (`.github/skills/chat-customizations-editor/SKILL.md`) should be updated to document the extension API sync chain — listing all layers that must be updated when adding new fields to `IExternalCustomizationItem`.

## Files to Look At

- `src/vs/workbench/contrib/chat/common/customizationHarnessService.ts` — internal `IExternalCustomizationItem` interface
- `src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts` — list widget with `fetchItemsFromProvider()` and `filterItems()`
- `src/vs/workbench/api/browser/mainThreadChatAgents2.ts` — MainThread API bridge
- `src/vs/workbench/api/common/extHost.protocol.ts` — IPC DTO definitions
- `src/vs/workbench/api/common/extHostChatAgents2.ts` — ExtHost mapping
- `src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts` — proposed extension API types
- `.github/skills/chat-customizations-editor/SKILL.md` — agent skill documentation for this editor
