#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gemini-cli-desktop

# Idempotency guard
if grep -qF "*This documentation is maintained alongside the codebase and should be updated w" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -32,6 +32,9 @@ Gemini Desktop is a powerful, cross-platform desktop and web application that pr
 - **About dialog**: Integrated help and version information
 - **Resizable sidebar**: Interactive sidebar with drag-to-resize functionality and persistent width settings
 - **Cross-platform support**: Windows, macOS, and Linux compatibility
+- **File viewing support**: PDF, Excel, image, and text file viewers with syntax highlighting
+- **Advanced search**: Full-text search across chat history and projects
+- **Settings management**: Comprehensive settings dialog with backend configuration
 
 ## Architecture
 
@@ -72,6 +75,14 @@ The project is organized as a Rust workspace with three main crates:
   - Chat content indexing
   - Filtering and ranking algorithms
   - Date range and project-based filtering
+- **CLI Integration** (`cli/mod.rs`) - Command line interface management
+  - Process spawning and lifecycle management
+  - Output parsing and streaming
+  - Cross-platform command execution
+- **RPC Layer** (`rpc/mod.rs`) - Remote procedure call abstraction
+  - Type-safe method definitions
+  - Serialization/deserialization handling
+  - Error propagation and handling
 
 #### **`crates/server`** - Web Server Implementation
 - **Rocket-based REST API** - HTTP endpoints for all backend functionality
@@ -100,27 +111,35 @@ The project is organized as a Rust workspace with three main crates:
   - `QwenWordmark.tsx` - Qwen text branding
   - `PiebaldLogo.tsx` - Piebald company branding
   - `SmartLogo.tsx` - Dynamic logo switching
+  - `SmartLogoCenter.tsx` - Centered logo variant
   - `DesktopText.tsx` - Desktop-specific text elements
-- **`common/`** - Reusable UI components
-  - `ToolCallDisplay.tsx` - Tool execution visualization
-  - `MarkdownRenderer.tsx` - Rich text rendering with syntax highlighting
-  - `DiffViewer.tsx` - Code difference visualization with word-level diffing (recently rewritten for better performance)
-  - `SearchInput.tsx` - Advanced search interface
-  - `DirectorySelectionDialog.tsx` - File system navigation
-  - `DirectoryPanel.tsx` - Directory tree visualization
-  - `FilePickerDropdown.tsx` - File selection dropdown component
-  - `RecursiveFilePickerDropdown.tsx` - Recursive file browser with depth limits
+- **`common/`** - Reusable UI components (27 components)
   - `AboutDialog.tsx` - Application information and version details
   - `CliWarnings.tsx` - CLI installation status and warnings
-  - `CodeBlock.tsx` - Syntax-highlighted code display with improved streaming performance
-  - `MentionInput.tsx` - @-mention support for user input with directory limit improvements
+  - `CodeBlock.tsx` - Syntax-highlighted code display
+  - `CodeMirrorViewer.tsx` - Advanced code editing and viewing
+  - `DiffViewer.tsx` - Code difference visualization with word-level diffing
+  - `DirectoryPanel.tsx` - Directory tree visualization
+  - `DirectorySelectionDialog.tsx` - File system navigation
+  - `ExcelViewer.tsx` - Spreadsheet file viewer
+  - `FileContentViewer.tsx` - Generic file content display
+  - `FilePickerDropdown.tsx` - File selection dropdown component
+  - `GitInfo.tsx` - Git repository status display
+  - `ImageViewer.tsx` - Image file display component
+  - `InlineSessionProgress.tsx` - Session progress indicators
+  - `LanguageSwitcher.tsx` - Language selection interface with flag icons
+  - `MarkdownRenderer.tsx` - Rich text rendering with syntax highlighting
+  - `MentionInput.tsx` - @-mention support for user input
   - `ModelContextProtocol.tsx` - MCP server integration components
+  - `PDFViewer.tsx` - PDF document viewer
+  - `RecursiveFilePickerDropdown.tsx` - Recursive file browser
+  - `SearchInput.tsx` - Advanced search interface
   - `SearchResults.tsx` - Search result display and filtering
+  - `SettingsDialog.tsx` - Application settings management
+  - `ToolCallDisplay.tsx` - Tool execution visualization
   - `ToolCallsList.tsx` - Tool execution history
   - `ToolResultRenderer.tsx` - Tool output formatting
   - `UserAvatar.tsx` - User profile display
-  - `GitInfo.tsx` - Git repository status display
-  - `LanguageSwitcher.tsx` - Language selection interface with flag icons
   - `I18nExample.tsx` - Translation demonstration component
 - **`conversation/`** - Chat interface components
   - `ConversationList.tsx` - Message history and pagination
@@ -135,16 +154,14 @@ The project is organized as a Rust workspace with three main crates:
 - **`layout/`** - Application structure
   - `AppHeader.tsx` - Top navigation bar
   - `AppSidebar.tsx` - Navigation and project selection with resizable functionality
-  - `CustomTitleBar.tsx` - Native window controls for desktop (now also enabled for web without controls)
+  - `CustomTitleBar.tsx` - Native window controls for desktop and web
   - `PageLayout.tsx` - Responsive layout management
-- **`mcp/`** - Model Context Protocol components (with full MCP server call support)
+- **`mcp/`** - Model Context Protocol components
   - `AddMcpServerDialog.tsx` - Server configuration dialog
   - `DynamicList.tsx` - Dynamic list management
   - `McpServerCard.tsx` - Server status display
   - `McpServerSettings.tsx` - Server configuration interface
   - `PasteJsonDialog.tsx` - JSON configuration import
-  - `McpPermissionDialog.tsx` - Permission request handling
-  - `McpPermissionCompact.tsx` - Compact permission display
 - **`renderers/`** - Tool-specific result renderers
   - `CommandRenderer.tsx` - Terminal output formatting
   - `DefaultRenderer.tsx` - Fallback renderer
@@ -166,23 +183,19 @@ The project is organized as a Rust workspace with three main crates:
   - Enhanced sidebar component with resize handle and drag-to-resize functionality
   - Additional components: `command.tsx`, `sonner.tsx` (toast notifications), `collapsible.tsx`
 
-#### API Layer
-- **`api.ts`** - Unified API abstraction layer
-  - Cross-platform command routing (Tauri vs Web)
-  - Type-safe command validation with runtime checks
-  - Comprehensive error handling with toast notifications
-  - Support for all backend commands with proper argument validation
-- **`webApi.ts`** - Web-specific REST API implementation
-  - Axios-based HTTP client with 30-second timeout
-  - Automatic error interceptors with user-friendly toast messages
-  - WebSocket management with reconnection logic
-  - Complete REST endpoint coverage matching Tauri commands
-
 #### Context and State Management
 - **`BackendContext.tsx`** - Primary communication layer
   - API abstraction (Tauri vs REST)
   - Event handling and state synchronization
   - Error boundary and retry logic
+- **`ConversationContext.tsx`** - Chat state management
+  - Message history and pagination
+  - Tool call confirmation state
+  - Real-time event integration
+- **`LanguageContext.tsx`** - Internationalization management
+  - Current language state and persistence
+  - Language switching functionality
+  - Browser language detection integration
 
 #### API Layer (`lib/`)
 - **`api.ts`** - Unified API interface with TypeScript proxy
@@ -195,26 +208,27 @@ The project is organized as a Rust workspace with three main crates:
   - Complete REST endpoint implementations mirroring Tauri commands
   - WebSocket management for real-time events
   - Connection handling with automatic reconnection logic
-  - Type definitions for all data structures (DirEntry, RecentChat, SearchResult, etc.)
-- **`ConversationContext.tsx`** - Chat state management
-  - Message history and pagination
-  - Tool call confirmation state
-  - Real-time event integration
-- **`LanguageContext.tsx`** - Internationalization management
-  - Current language state and persistence
-  - Language switching functionality
-  - Browser language detection integration
+  - Type definitions for all data structures
 
 #### Custom Hooks
 - **`useCliInstallation.ts`** - CLI availability detection
 - **`useConversationEvents.ts`** - Real-time event handling
 - **`useConversationManager.ts`** - Conversation state management
 - **`useMessageHandler.ts`** - Message processing and display
 - **`useProcessManager.ts`** - Session lifecycle management
-- **`useResizable.ts`** - Sidebar resize functionality with mouse drag handling and localStorage persistence
+- **`useResizable.ts`** - Sidebar resize functionality with mouse drag handling
 - **`useToolCallConfirmation.ts`** - User approval workflow
 - **`use-mobile.ts`** - Responsive design utilities
 
+#### Internationalization (`i18n/`)
+- **`config.ts`** - i18next configuration and setup
+- **`index.ts`** - Main i18n initialization
+- **`types.ts`** - TypeScript definitions for translations
+- **`locales/`** - Translation files
+  - `en/translation.json` - English translations
+  - `zh-CN/translation.json` - Simplified Chinese translations
+  - `zh-TW/translation.json` - Traditional Chinese translations
+
 #### Utilities and Helpers
 - **`utils/toolCallParser.ts`** - Tool call parsing and validation
 - **`utils/toolInputParser.ts`** - Tool input formatting and validation
@@ -228,45 +242,54 @@ The project is organized as a Rust workspace with three main crates:
 ## Technology Stack
 
 ### Backend Technologies
-- **Rust** (Editions 2024/2021) - Systems programming language
+- **Rust** (Edition 2024) - Systems programming language
 - **Tokio** - Async runtime with full feature set
 - **Serde** - Serialization framework with derive macros
 - **Rocket** - Web framework with JSON support
 - **rocket-ws** - WebSocket support for Rocket
-- **Tauri** - Desktop app framework
+- **Tauri** - Desktop app framework (v2.8.0)
 - **SHA2** - Cryptographic hashing for project identification
 - **Chrono** - Date/time handling with serialization support
+- **Anyhow** - Error handling and propagation
+- **Regex** - Pattern matching and text processing
+- **Ignore** - File system pattern matching
+- **Base64** - Encoding/decoding utilities
 
 ### Frontend Technologies
-- **React 19.1** - Component-based UI framework
-- **TypeScript 5.9** - Static type checking with strict mode
-- **Vite 7.1** - Modern build tool with HMR
-- **Tailwind CSS 4.1** - Utility-first CSS framework with @tailwindcss/vite plugin
+- **React** (19.1.1) - Component-based UI framework
+- **TypeScript** (5.9.2) - Static type checking with strict mode
+- **Vite** (7.1.3) - Modern build tool with HMR
+- **Tailwind CSS** (4.1.12) - Utility-first CSS framework with @tailwindcss/vite plugin
 - **shadcn/ui** - Component library with Radix UI primitives
+- **CodeMirror** - Advanced code editing and syntax highlighting
 - **Monaco Editor** - VS Code-like code editing capabilities
-- **React Markdown** - Markdown rendering with syntax highlighting
-- **React Router 7.8** - Client-side routing
-- **React Mentions** - @-mention support in text inputs
-- **React Syntax Highlighter** - Code syntax highlighting
-- **Axios 1.11** - HTTP client with automatic error handling and toast notifications
-- **Lucide React** - Icon library
-- **KaTeX** - Math rendering support
-- **Highlight.js** - Code syntax highlighting
-- **Shiki** - Advanced syntax highlighting with VS Code themes
-- **next-themes** - Theme management system
-- **class-variance-authority** - CSS class variance utilities
-- **Google Generative AI** - Direct Gemini API integration
-- **react-i18next** - Internationalization framework with hooks and components
-- **i18next** - Core internationalization library with interpolation and pluralization
-- **i18next-browser-languagedetector** - Browser language detection and persistence
+- **React Markdown** (10.1.0) - Markdown rendering with syntax highlighting
+- **React Router DOM** (7.8.1) - Client-side routing
+- **React Mentions** (4.4.10) - @-mention support in text inputs
+- **React Syntax Highlighter** (15.6.1) - Code syntax highlighting
+- **Axios** (1.11.0) - HTTP client with automatic error handling
+- **Lucide React** (0.540.0) - Icon library
+- **KaTeX** (0.16.22) - Math rendering support
+- **Highlight.js** (11.11.1) - Code syntax highlighting
+- **Shiki** (3.10.0) - Advanced syntax highlighting with VS Code themes
+- **next-themes** (0.4.6) - Theme management system
+- **class-variance-authority** (0.7.1) - CSS class variance utilities
+- **Google Generative AI** (0.24.1) - Direct Gemini API integration
+- **react-i18next** (15.6.1) - Internationalization framework with hooks and components
+- **i18next** (25.3.6) - Core internationalization library
+- **i18next-browser-languagedetector** (8.2.0) - Browser language detection
+- **pdfjs-dist** (5.3.93) - PDF viewing capabilities
+- **react-pdf** (10.1.0) - React PDF viewer component
+- **xlsx** (0.18.5) - Excel file processing
+- **sonner** (2.0.7) - Toast notifications
 
 ### Development Tools
 - **Just** - Task runner and build automation
-- **pnpm** - Fast, disk space efficient package manager
-- **ESLint** - Code linting with TypeScript support
-- **Prettier** - Code formatting
+- **pnpm** (10.13.1+) - Fast, disk space efficient package manager
+- **ESLint** (9.33.0) - Code linting with TypeScript support
+- **Prettier** (3.6.2) - Code formatting
 - **cargo-nextest** - Improved Rust test runner
-- **cargo-tarpaulin** - Code coverage analysis
+- **cargo-tarpaulin** (0.31) - Code coverage analysis
 
 ## Development Environment
 
@@ -361,21 +384,15 @@ just test [args]            # Run tests with optional arguments
 #### Test Infrastructure
 - **cargo-nextest** - Preferred test runner for better performance
 - **tokio-test** - Async testing utilities
-- **mockall** - Mock object generation
-- **serial_test** - Test serialization for environment isolation
+- **mockall** (0.13) - Mock object generation
+- **serial_test** (3.0) - Test serialization for environment isolation
 - **proptest** - Property-based testing (optional feature)
-- **criterion** - Benchmarking framework
+- **criterion** (0.5) - Benchmarking framework
 
 #### Test Utilities (`test_utils.rs`)
 - **`EnvGuard`** - Thread-safe environment variable management
-  - RAII-based cleanup ensuring test isolation
-  - Restore original values after test completion
 - **`TestDirManager`** - Unique temporary directory creation
-  - Per-test isolation with automatic cleanup
-  - Cross-platform path handling
 - **Builder patterns** for test data creation
-  - `ProjectListItem`, `RecentChat`, `JsonRpcRequest` builders
-  - Fluent API for readable test setup
 
 #### Coverage Requirements
 - **95% coverage threshold** enforced via tarpaulin
@@ -508,10 +525,9 @@ params: {
 - `session/request_permission` - User approval required
 - Options: Allow Once, Allow Always, Reject Once, Reject Always
 
-### API Architecture
+### Unified API Interface (`api.ts`)
 
-#### Unified API Interface (`api.ts`)
-The application uses a sophisticated proxy-based API system that automatically routes calls to either Tauri commands (desktop) or REST endpoints (web) based on the runtime environment:
+The application uses a sophisticated proxy-based API system that automatically routes calls to either Tauri commands (desktop) or REST endpoints (web):
 
 ```typescript
 export interface API {
@@ -551,7 +567,7 @@ export interface API {
 }
 ```
 
-#### REST API Endpoints (Web Mode)
+### REST API Endpoints (Web Mode)
 
 **Session Management**
 - `POST /api/start-session` - Initialize new session
@@ -582,47 +598,12 @@ export interface API {
 - `GET /api/check-cli-installed` - CLI availability check
 - `POST /api/generate-title` - AI-generated chat titles
 
-#### WebSocket Integration (`webApi.ts`)
+### WebSocket Integration (`webApi.ts`)
 - **Real-time events**: WebSocket connection at `/api/ws`
 - **Automatic reconnection**: Exponential backoff with max 5 attempts
 - **Event management**: Type-safe event listener system
 - **Connection lifecycle**: Promise-based connection readiness
 
-### Event System
-
-#### Desktop Events (Tauri)
-```typescript
-// Listen for backend events
-api.listen<EventPayload>("event_name", (event) => {
-  console.log(event.payload);
-});
-```
-
-#### Web Events (WebSocket)
-```typescript
-// WebSocket message format
-{
-  event: string,
-  payload: any,
-  sequence: number  // For ordering
-}
-
-// WebSocket connection management
-const manager = getWebSocketManager();
-const unsubscribe = await webListen<EventPayload>("event_name", (event) => {
-  console.log(event.payload);
-});
-
-// Cleanup
-unsubscribe();
-```
-
-**Connection Features**:
-- Automatic reconnection with exponential backoff (max 5 attempts)
-- Connection state promises for reliable event setup
-- Event listener lifecycle management
-- Graceful degradation and error recovery
-
 ## Deployment
 
 ### CI/CD Pipeline
@@ -750,7 +731,7 @@ gemini-desktop/
 - **Clippy pedantic lints** enabled for high code quality
 - **cargo fmt** for consistent formatting
 - **Edition 2024** features utilized (2021 for tauri-app crate)
-- **Comprehensive error handling** with `thiserror`
+- **Comprehensive error handling** with `anyhow`
 - **Async/await patterns** throughout
 
 #### Windows-Specific Command Execution
@@ -764,10 +745,7 @@ gemini-desktop/
     #[cfg(windows)]
     command.creation_flags(0x08000000); // CREATE_NO_WINDOW
     ```
-  - This applies to ALL commands that might spawn console windows, including:
-    - CLI availability checks
-    - Process spawning for Gemini/Qwen backends
-    - Any system command execution
+  - This applies to ALL commands that might spawn console windows
 
 #### TypeScript Code
 - **Strict mode** enabled for maximum type safety
@@ -813,24 +791,6 @@ gemini-desktop/
 5. **Release notes** generated automatically
 6. **Binary distribution** via GitHub Releases
 
-### Recent Improvements
-
-- **Major API Refactoring**: Complete restructure of the API layer with unified interface
-  - **Proxy-based API**: Single API interface that automatically routes to Tauri or REST based on runtime environment
-  - **Type Safety**: Full TypeScript generics system for method parameters and return types
-  - **WebSocket Manager**: Comprehensive WebSocket handling with automatic reconnection and event management
-  - **Error Handling**: Centralized error handling with try-catch blocks and logging
-- **Enhanced JSON Parsing**: Session management now includes robust handling of non-JSON CLI output lines, improving reliability when reading from Gemini CLI
-- **React 19 Upgrade**: Frontend upgraded to React 19.1 with improved type safety and performance
-- **Adaptive Process Polling**: Enhanced process manager with intelligent polling intervals
-- **MCP Server Support**: Full Model Context Protocol server call support with permission handling
-- **@-Mention Improvements**: Enhanced file mentioning with directory limit of 200 files instead of depth limit
-- **Diff Viewer Rewrite**: Complete rewrite for better performance with large diffs
-- **Code Block Streaming**: Improved performance for code blocks during streaming
-- **Custom Titlebar in Web**: Extended custom titlebar support to web version (without window controls)
-- **Shift+Enter Support**: Added support for multiline input in message field
-- **Session Management Fix**: Prevented dual CLI execution when switching backends
-
 ### Contributing Guidelines
 
 #### Prerequisites
@@ -850,248 +810,6 @@ gemini-desktop/
 - Code coverage must not decrease
 - Documentation updates for public APIs
 
-
-## Complete Source Code Tree
-```
-gemini-desktop/
-├── assets/
-│   ├── qwen-desktop.png
-│   └── screenshot.png
-├── Cargo.lock
-├── Cargo.toml
-├── CLAUDE.md
-├── LICENSE
-├── README.md
-├── crates/
-│   ├── backend/
-│   │   ├── Cargo.toml
-│   │   └── src/
-│   │       ├── acp/
-│   │       │   └── mod.rs
-│   │       ├── cli/
-│   │       │   └── mod.rs
-│   │       ├── events/
-│   │       │   └── mod.rs
-│   │       ├── filesystem/
-│   │       │   └── mod.rs
-│   │       ├── lib.rs
-│   │       ├── projects/
-│   │       │   └── mod.rs
-│   │       ├── rpc/
-│   │       │   └── mod.rs
-│   │       ├── search/
-│   │       │   └── mod.rs
-│   │       ├── security/
-│   │       │   └── mod.rs
-│   │       ├── session/
-│   │       │   └── mod.rs
-│   │       ├── test_utils.rs
-│   │       └── types/
-│   │           └── mod.rs
-│   ├── server/
-│   │   ├── Cargo.toml
-│   │   └── src/
-│   │       └── main.rs
-│   └── tauri-app/
-│       ├── build.rs
-│       ├── Cargo.lock
-│       ├── Cargo.toml
-│       ├── capabilities/
-│       │   └── default.json
-│       ├── gen/
-│       │   └── schemas/
-│       │       ├── acl-manifests.json
-│       │       ├── capabilities.json
-│       │       ├── desktop-schema.json
-│       │       └── windows-schema.json
-│       ├── icons/
-│       │   ├── 128x128.png
-│       │   ├── 128x128@2x.png
-│       │   ├── 32x32.png
-│       │   ├── Square107x107Logo.png
-│       │   ├── Square142x142Logo.png
-│       │   ├── Square150x150Logo.png
-│       │   ├── Square284x284Logo.png
-│       │   ├── Square30x30Logo.png
-│       │   ├── Square310x310Logo.png
-│       │   ├── Square44x44Logo.png
-│       │   ├── Square71x71Logo.png
-│       │   ├── Square89x89Logo.png
-│       │   ├── StoreLogo.png
-│       │   ├── icon.icns
-│       │   ├── icon.ico
-│       │   └── icon.png
-│       ├── src/
-│       │   ├── commands/
-│       │   │   └── mod.rs
-│       │   ├── event_emitter.rs
-│       │   ├── lib.rs
-│       │   ├── main.rs
-│       │   ├── menu.rs
-│       │   └── state.rs
-│       └── tauri.conf.json
-├── frontend/
-│   ├── components.json
-│   ├── dist/                    # Build output directory (generated)
-│   ├── eslint.config.js
-│   ├── index.html
-│   ├── node_modules/            # Package dependencies
-│   ├── package.json
-│   ├── pnpm-lock.yaml
-│   ├── pnpm-workspace.yaml
-│   ├── public/
-│   │   ├── Piebald.svg
-│   │   ├── tauri.svg
-│   │   └── vite.svg
-│   ├── src/
-│   │   ├── App.tsx
-│   │   ├── assets/
-│   │   │   └── react.svg
-│   │   ├── components/
-│   │   │   ├── branding/
-│   │   │   │   ├── DesktopText.tsx
-│   │   │   │   ├── GeminiIcon.tsx
-│   │   │   │   ├── GeminiWordmark.tsx
-│   │   │   │   ├── PiebaldLogo.tsx
-│   │   │   │   ├── QwenIcon.tsx
-│   │   │   │   ├── QwenWordmark.tsx
-│   │   │   │   ├── SmartLogo.tsx
-│   │   │   │   └── SmartLogoCenter.tsx
-│   │   │   ├── common/
-│   │   │   │   ├── AboutDialog.tsx
-│   │   │   │   ├── CliWarnings.tsx
-│   │   │   │   ├── CodeBlock.tsx
-│   │   │   │   ├── DiffViewer.tsx
-│   │   │   │   ├── DirectorySelectionDialog.tsx
-│   │   │   │   ├── I18nExample.tsx
-│   │   │   │   ├── LanguageSwitcher.tsx
-│   │   │   │   ├── MarkdownRenderer.tsx
-│   │   │   │   ├── MentionInput.tsx
-│   │   │   │   ├── ModelContextProtocol.tsx
-│   │   │   │   ├── SearchInput.tsx
-│   │   │   │   ├── SearchResults.tsx
-│   │   │   │   ├── ToolCallDisplay.tsx
-│   │   │   │   ├── ToolCallsList.tsx
-│   │   │   │   ├── ToolResultRenderer.tsx
-│   │   │   │   └── UserAvatar.tsx
-│   │   │   ├── conversation/
-│   │   │   │   ├── ConversationList.tsx
-│   │   │   │   ├── MessageActions.tsx
-│   │   │   │   ├── MessageContent.tsx
-│   │   │   │   ├── MessageHeader.tsx
-│   │   │   │   ├── MessageInputBar.tsx
-│   │   │   │   ├── RecentChats.tsx
-│   │   │   │   └── ThinkingBlock.tsx
-│   │   │   ├── layout/
-│   │   │   │   ├── AppHeader.tsx
-│   │   │   │   ├── AppSidebar.tsx
-│   │   │   │   ├── CustomTitleBar.tsx
-│   │   │   │   └── PageLayout.tsx
-│   │   │   ├── mcp/
-│   │   │   │   ├── AddMcpServerDialog.tsx
-│   │   │   │   ├── DynamicList.tsx
-│   │   │   │   ├── McpServerCard.tsx
-│   │   │   │   ├── McpServerSettings.tsx
-│   │   │   │   └── PasteJsonDialog.tsx
-│   │   │   ├── renderers/
-│   │   │   │   ├── CommandRenderer.tsx
-│   │   │   │   ├── DefaultRenderer.tsx
-│   │   │   │   ├── DirectoryRenderer.tsx
-│   │   │   │   ├── EditRenderer.tsx
-│   │   │   │   ├── FileRenderer.tsx
-│   │   │   │   ├── GrepGlobRenderer.tsx
-│   │   │   │   ├── ReadFileRenderer.tsx
-│   │   │   │   ├── ReadManyFilesRenderer.tsx
-│   │   │   │   ├── SearchRenderer.tsx
-│   │   │   │   └── WebToolRenderer.tsx
-│   │   │   ├── theme/
-│   │   │   │   ├── simple-theme-toggle.tsx
-│   │   │   │   └── theme-provider.tsx
-│   │   │   └── ui/
-│   │   │       ├── alert.tsx
-│   │   │       ├── avatar.tsx
-│   │   │       ├── badge.tsx
-│   │   │       ├── button.tsx
-│   │   │       ├── card.tsx
-│   │   │       ├── checkbox.tsx
-│   │   │       ├── code.tsx
-│   │   │       ├── collapsible.tsx
-│   │   │       ├── context-menu.tsx
-│   │   │       ├── dialog.tsx
-│   │   │       ├── dropdown-menu.tsx
-│   │   │       ├── input.tsx
-│   │   │       ├── label.tsx
-│   │   │       ├── radio-group.tsx
-│   │   │       ├── scroll-area.tsx
-│   │   │       ├── select.tsx
-│   │   │       ├── separator.tsx
-│   │   │       ├── sheet.tsx
-│   │   │       ├── sidebar.tsx
-│   │   │       ├── skeleton.tsx
-│   │   │       ├── table.tsx
-│   │   │       ├── textarea.tsx
-│   │   │       └── tooltip.tsx
-│   │   ├── contexts/
-│   │   │   ├── BackendContext.tsx
-│   │   │   ├── ConversationContext.tsx
-│   │   │   └── LanguageContext.tsx
-│   │   ├── hooks/
-│   │   │   ├── use-mobile.ts
-│   │   │   ├── useCliInstallation.ts
-│   │   │   ├── useConversationEvents.ts
-│   │   │   ├── useConversationManager.ts
-│   │   │   ├── useMessageHandler.ts
-│   │   │   ├── useProcessManager.ts
-│   │   │   ├── useResizable.ts
-│   │   │   └── useToolCallConfirmation.ts
-│   │   ├── index.css
-│   │   ├── lib/
-│   │   │   ├── api.ts
-│   │   │   ├── utils.ts
-│   │   │   └── webApi.ts
-│   │   ├── main.tsx
-│   │   ├── pages/
-│   │   │   ├── HomeDashboard.tsx
-│   │   │   ├── McpServersPage.tsx
-│   │   │   ├── ProjectDetail.tsx
-│   │   │   └── Projects.tsx
-│   │   ├── types/
-│   │   │   ├── backend.ts
-│   │   │   ├── global.d.ts
-│   │   │   ├── index.ts
-│   │   │   └── mcp.ts
-│   │   ├── utils/
-│   │   │   ├── backendDefaults.ts
-│   │   │   ├── backendText.ts
-│   │   │   ├── backendValidation.ts
-│   │   │   ├── helpers.ts
-│   │   │   ├── mcpValidation.ts
-│   │   │   ├── toolCallParser.ts
-│   │   │   ├── toolInputParser.ts
-│   │   │   └── wordDiff.ts
-│   │   ├── i18n/
-│   │   │   ├── README.md
-│   │   │   ├── config.ts
-│   │   │   ├── index.ts
-│   │   │   ├── locales/
-│   │   │   │   ├── en/
-│   │   │   │   │   └── translation.json
-│   │   │   │   ├── zh-CN/
-│   │   │   │   │   └── translation.json
-│   │   │   │   └── zh-TW/
-│   │   │   │       └── translation.json
-│   │   │   └── types.ts
-│   │   └── vite-env.d.ts
-│   ├── tsconfig.json
-│   ├── tsconfig.node.json
-│   └── vite.config.ts
-├── justfile
-├── src-tauri/                      # Legacy Tauri directory (build artifacts)
-│   └── target/
-├── target/                         # Rust build artifacts
-└── tarpaulin.toml
-```
-
 ---
 
-*This documentation is maintained alongside the codebase and should be updated when significant changes are made to the architecture, APIs, or development processes.*
+*This documentation is maintained alongside the codebase and should be updated when significant changes are made to the architecture, APIs, or development processes.*
\ No newline at end of file
PATCH

echo "Gold patch applied."
