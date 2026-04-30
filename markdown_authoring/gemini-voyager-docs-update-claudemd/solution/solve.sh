#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gemini-voyager

# Idempotency guard
if grep -qF "| `src/features/backup/` | Auto-backup with File System API/JSZip fallback | Cha" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -1,7 +1,7 @@
 # CLAUDE.md - AI Assistant Guide for Gemini Voyager
 
-> **Last Updated**: 2025-11-13
-> **Version**: 0.9.2
+> **Last Updated**: 2025-11-18
+> **Version**: 0.9.5
 > **Purpose**: Comprehensive guide for AI assistants working with the Gemini Voyager codebase
 
 ---
@@ -31,7 +31,8 @@ Gemini Voyager is a cross-browser extension that enhances the Google Gemini AI c
 - **Prompt Library**: Tag-based prompt management with import/export
 - **Chat Export**: Export conversations to JSON, Markdown, or PDF with asset packaging
 - **Formula Copy**: One-click LaTeX/KaTeX formula source copying
-- **UI Customization**: Adjustable chat width, dark mode, multi-language support (EN/ZH)
+- **UI Customization**: Adjustable chat width, sidebar width, dark mode, multi-language support (EN/ZH)
+- **Auto-Backup**: Automatic timestamped backups with File System Access API or JSZip fallback
 
 ### Tech Stack
 
@@ -69,6 +70,7 @@ gemini-voyager/
 │   │   │   ├── folder/           # Folder organization
 │   │   │   ├── prompt/           # Prompt library
 │   │   │   ├── chatWidth/        # Chat width adjuster
+│   │   │   ├── sidebarWidth/     # Sidebar width adjuster
 │   │   │   ├── editInputWidth/   # Edit input width adjuster
 │   │   │   └── formulaCopy/      # LaTeX formula copying
 │   │   ├── popup/                # Extension popup UI
@@ -83,7 +85,8 @@ gemini-voyager/
 │   ├── features/                 # Shared feature modules
 │   │   ├── export/               # Chat export (JSON, MD, PDF)
 │   │   ├── folder/               # Folder system logic
-│   │   └── formulaCopy/          # Formula copy logic
+│   │   ├── formulaCopy/          # Formula copy logic
+│   │   └── backup/               # Auto-backup with File System API
 │   ├── components/               # React UI components
 │   │   └── ui/                   # Reusable primitives (Button, Card, etc.)
 │   ├── hooks/                    # Custom React hooks
@@ -114,6 +117,7 @@ gemini-voyager/
 | `src/core/services/` | Business logic services (storage, logging, DOM) | Changing storage strategy, logging behavior |
 | `src/core/types/` | TypeScript type definitions | Adding new data structures |
 | `src/features/export/` | Multi-format export functionality | Changing export formats or behavior |
+| `src/features/backup/` | Auto-backup with File System API/JSZip fallback | Changing backup strategy, adding backup targets |
 | `src/components/ui/` | Reusable UI components | Adding new UI primitives |
 | `src/hooks/` | Custom React hooks | Adding reusable stateful logic |
 | `src/locales/` | Translation files | Adding new languages or updating text |
@@ -207,9 +211,12 @@ const storage = await createStorageService(); // Auto-selects implementation
 - `geminiTimelineDraggable` - Timeline draggable state
 - `geminiTimelinePosition` - Timeline position coordinates
 - `geminiChatWidth` - Chat container width
+- `geminiSidebarWidth` - Sidebar width setting
 - `language` - UI language preference
 
-**Note**: Some features (e.g., Prompt Manager) use local storage keys (`gvPromptItems`, `gvPromptPanelLocked`) not in the central `StorageKeys` object
+**Note**: Some features use storage keys not in the central `StorageKeys` object:
+- Prompt Manager: `gvPromptItems`, `gvPromptPanelLocked`
+- Backup Service: `gvBackupConfig` (defined in `src/features/backup/types/backup.ts`)
 
 **Concurrency**: Uses `AsyncLock` to prevent race conditions during import/export operations
 
@@ -690,6 +697,45 @@ async setYourFeatureData(data: YourData): Promise<void> {
 }
 ```
 
+### Working with Backup Service
+
+The backup service (`src/features/backup/`) provides automatic timestamped backups with File System Access API:
+
+**Key Features**:
+- Automatic backups at configurable intervals
+- Manual backup triggering
+- Backs up prompts and folder data
+- JSZip fallback for browsers without File System Access API support
+
+**Example Usage**:
+```typescript
+import { BackupService, backupService } from '@/features/backup/services/BackupService';
+
+// Request directory access
+const dirHandle = await BackupService.requestDirectoryAccess();
+if (!dirHandle) {
+  console.log('User cancelled directory selection');
+  return;
+}
+
+// Create backup
+const config = {
+  enabled: true,
+  intervalHours: 24,
+  includePrompts: true,
+  includeFolders: true,
+};
+
+const result = await backupService.createBackup(dirHandle, config);
+if (result.success) {
+  console.log(`Backup created: ${result.data.promptCount} prompts, ${result.data.folderCount} folders`);
+}
+```
+
+**Backup Structure**:
+- Each backup creates a timestamped folder: `backup-YYYYMMDD-HHMMSS/`
+- Contains: `prompts.json`, `folders.json`, `metadata.json`
+
 ### Handling Browser-Specific Code
 
 Use feature detection instead of browser detection:
@@ -740,6 +786,8 @@ For manifest differences, use separate configs:
 | `src/core/types/common.ts` | Shared type definitions | Brand types, utility types |
 | `src/core/errors/index.ts` | Error classes | `AppError`, `StorageError`, etc. |
 | `src/features/export/ConversationExportService.ts` | Chat export logic | `exportConversation()` |
+| `src/features/backup/services/BackupService.ts` | Auto-backup with File System API | `backupService`, `createBackup()` |
+| `src/features/backup/services/PromptImportExportService.ts` | Prompt backup/restore | Export/import prompt library |
 | `src/pages/popup/Popup.tsx` | Extension popup UI | Main popup component |
 | `src/hooks/useI18n.ts` | Internationalization hook | `useI18n()` |
 | `src/contexts/LanguageContext.tsx` | Language state management | `LanguageProvider`, `useLanguage()` |
@@ -982,7 +1030,21 @@ See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for detailed guidelines.
 
 ## Changelog
 
-### v0.9.2 (Latest)
+### v0.9.5 (Latest)
+- Added configurable sidebar width setting
+- Fixed abnormal line spacing of dialog items within folder
+- Fixed 10px right padding overlap issue between chat scroll and timeline
+
+### v0.9.4
+- Added jszip fallback for browsers like Safari and Firefox that don't support File System Access API
+- Improved backup compatibility across browsers
+
+### v0.9.3
+- Added automatic backup with timestamp feature
+- Fixed hide archived setting not applying to conversations after page refresh
+- Fixed folder records being cleared unexpectedly
+
+### v0.9.2
 - Added folder close option to popup
 - Fixed folder list sorting in Move to Folder
 - Fixed conversations lost when added to empty folders bug
@@ -1001,6 +1063,6 @@ By contributing to this project, you agree that your contributions will be licen
 
 ---
 
-**Last Updated**: 2025-11-13
+**Last Updated**: 2025-11-18
 **Maintainer**: Jesse Zhang (@Nagi-ovo)
 **For Questions**: Open an issue on [GitHub](https://github.com/Nagi-ovo/gemini-voyager/issues)
PATCH

echo "Gold patch applied."
