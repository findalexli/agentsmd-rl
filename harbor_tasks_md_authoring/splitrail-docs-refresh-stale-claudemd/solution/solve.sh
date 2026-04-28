#!/usr/bin/env bash
set -euo pipefail

cd /workspace/splitrail

# Idempotency guard
if grep -qF "Splitrail is a high-performance, cross-platform usage tracker for AI coding assi" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -4,192 +4,233 @@ This file provides guidance to Claude Code (claude.ai/code) when working with co
 
 ## Project Overview
 
-Splitrail is a comprehensive agentic AI coding tool usage analyzer written in Rust that provides detailed analytics for Claude Code, Codex CLI, Copilot, and Gemini CLI usage. It features a rich TUI (Terminal User Interface), automatic data upload to Splitrail Cloud, and extensive usage statistics including token counts, costs, file operations, tool usage, and productivity metrics.
-
-## Development Commands
-
-### Building and Testing
-- `cargo check` - Check code compilation without building
-- `cargo build` - Build the project in debug mode
-- `cargo build --release` - Build optimized release version
-- `cargo run` - Run with default behavior (show stats + optional auto-upload)
-- `cargo run -- upload` - Manually upload stats to Splitrail Cloud
-- `cargo run -- config <subcommand>` - Manage configuration
-
-### Available Commands
-- `splitrail` - Show stats in TUI with real-time watching and auto-upload when changes are detected (if auto-upload is enabled)
-- `splitrail upload` - Manually upload stats to Splitrail Cloud
-- `splitrail config init` - Create default configuration file
-- `splitrail config show` - Display current configuration
-- `splitrail config set <key> <value>` - Set configuration values
-- `splitrail help` - Show help information
+Splitrail is a high-performance, cross-platform usage tracker for AI coding assistants (Claude Code, Copilot, Cline, etc.). It analyzes local data files from these tools, aggregates usage statistics, and provides real-time TUI monitoring with optional cloud upload capabilities.
+
+**Key Technologies:**
+- Rust (edition 2024) with async/await (Tokio)
+- Memory-mapped persistent caching (rkyv, memmap2) for fast incremental parsing
+- Terminal UI (ratatui + crossterm)
+- MCP (Model Context Protocol) server support
+
+## Building and Running
+
+### Basic Commands
+```bash
+# Build and run (release mode recommended for performance)
+cargo run --release
+
+# Run in development mode
+cargo run
+
+# Run tests
+cargo test
+
+# Run specific test
+cargo test test_name
+
+# Run tests for a specific module
+cargo test --test module_name
+
+# Build only (no run)
+cargo build --release
+```
+
+### Windows-Specific Setup
+Windows requires `lld-link.exe` from LLVM for fast compilation. Install via:
+```bash
+winget install --id LLVM.LLVM
+```
+Then add `C:\Program Files\LLVM\bin\` to system PATH.
 
 ## Architecture
 
-### Core Modules
-
-1. **Main Module** (`src/main.rs`): Command-line interface with subcommand routing
-2. **Analyzer Framework** (`src/analyzer.rs`): Trait-based analyzer architecture for multiple AI tools
-3. **Claude Code Analyzer** (`src/analyzers/claude_code.rs`): Analysis engine for Claude Code data
-4. **Codex CLI Analyzer** (`src/analyzers/codex_cli.rs`): Analysis engine for Codex CLI data
-5. **Gemini CLI Analyzer** (`src/analyzers/gemini_cli.rs`): Analysis engine for Gemini CLI data
-6. **GitHub Copilot Analyzer** (`src/analyzers/copilot.rs`): Analysis engine for GitHub Copilot Chat data
-7. **Cline Analyzer** (`src/analyzers/cline.rs`): Analysis engine for Cline data
-8. **Roo Code Analyzer** (`src/analyzers/roo_code.rs`): Analysis engine for Roo Code data
-9. **Kilo Code Analyzer** (`src/analyzers/kilo_code.rs`): Analysis engine for Kilo Code data
-10. **Qwen Code Analyzer** (`src/analyzers/qwen_code.rs`): Analysis engine for Qwen Code data
-11. **TUI Module** (`src/tui.rs`): Rich terminal user interface using ratatui
-12. **Upload Module** (`src/upload.rs`): HTTP client for Splitrail Cloud integration
-13. **Config Module** (`src/config.rs`): Configuration file management
-14. **Types Module** (`src/types.rs`): Core data structures and enums
-15. **Models Module** (`src/models.rs`): Model pricing definitions
-16. **Utils Module** (`src/utils.rs`): Utility functions and helpers
-
-### Key Data Structures
-
-#### Core Types
-- `ConversationMessage`: Represents individual AI/User messages with full analytics
-- `DailyStats`: Comprehensive daily usage aggregations
-- `AgenticCodingToolStats`: Top-level container for all analytics
-- `ModelPricing`: Token cost definitions per model
-
-#### Analytics Types
-- `FileOperationStats`: Tracks file read/write/edit operations by type and volume
-- `TodoStats`: Tracks todo list usage and task completion
-- `FileCategory`: Categorizes files by type (SourceCode, Data, Documentation, etc.)
-
-### Core Functionality
-
-1. **Multi-Tool Data Discovery**:
-   - Claude Code: `~/.claude/projects` directories (JSONL files)
-   - Codex CLI: `~/.codex/sessions/**/*.jsonl` files
-   - Gemini CLI: `~/.gemini/tmp/*/chats/*.json` directories (JSON session files)
-   - GitHub Copilot: `~/.vscode/extensions/github.copilot-chat-*/sessions/*.json` files (VSCode, Cursor, Insiders variants)
-   - Cline, Roo Code, Kilo Code, Qwen Code: Various VSCode extension data directories
-2. **Flexible Conversation Parsing**: Processes different file formats (JSONL, JSON sessions, chat logs)
-3. **Advanced Deduplication**: Uses tool-specific hashing strategies to prevent duplicate entries
-4. **Comprehensive Cost Calculation**: Uses actual cost values or calculates from tokens using model pricing
-5. **File Operation Tracking**: Monitors tool usage across different AI coding assistants
-6. **Todo Analytics**: Tracks TodoWrite/TodoRead usage and task management (Claude Code)
-7. **TUI Display**: Interactive terminal interface with multiple views and navigation
-8. **Splitrail Cloud Integration**: Secure upload to Splitrail Cloud with API tokens
-9. **Configuration Management**: TOML-based config with auto-upload settings
-
-### Model Support
-
-Currently supports:
-**Claude Models:**
-- `claude-sonnet-4-20250514` (Sonnet 4): $0.003/$0.015 per 1K input/output tokens
-- `claude-opus-4-20250514` (Opus 4): $0.015/$0.075 per 1K input/output tokens
-- `claude-opus-4.1` / `claude-opus-4-1-20250805` (Opus 4.1): Same as Opus 4 pricing (aliases)
-- Cache pricing for both models (creation + read costs)
-
-**GPT Models:**
-- `gpt-5`: $1.25/$10.00 per 1K input/output tokens
-- `gpt-5-mini`: $0.25/$2.00 per 1K input/output tokens
-- `gpt-5-nano`: $0.05/$0.40 per 1K input/output tokens
-- Cache pricing supported for all GPT-5 series models
-
-**Gemini CLI Models:**
-- `gemini-2.5-pro`: $0.001/$0.003 per 1K input/output tokens
-- `gemini-2.5-flash`: $0.0005/$0.0015 per 1K input/output tokens
-- `gemini-1.5-pro`: Legacy model support
-- `gemini-1.5-flash`: Legacy model support
-- Cache read pricing supported
-
-**Codex CLI Models:**
-- `o4-mini`: $1.10/$4.40 per 1M input/output tokens (cached: $0.275 per 1M)
-- `o3`: $2.00/$8.00 per 1M input/output tokens (cached: $0.50 per 1M) 
-- `o3-mini`: $1.10/$4.40 per 1M input/output tokens (cached: $0.55 per 1M)
-- `o3-pro`: $20.00/$80.00 per 1M input/output tokens (no caching)
-- `o1`, `o1-preview`: $15.00/$60.00 per 1M input/output tokens (cached: $7.50 per 1M)
-- `o1-mini`: $1.10/$4.40 per 1M input/output tokens (cached: $0.55 per 1M)
-- `o1-pro`: $150.00/$600.00 per 1M input/output tokens (no caching)
-- `codex-mini-latest`: $1.50/$6.00 per 1M input/output tokens (cached: $0.375 per 1M)
-- `gpt-4.1`: $2.00/$8.00 per 1M input/output tokens (cached: $0.50 per 1M)
-- `gpt-4.1-mini`: $0.40/$1.60 per 1M input/output tokens (cached: $0.10 per 1M)
-- `gpt-4.1-nano`: $0.10/$0.40 per 1M input/output tokens (cached: $0.025 per 1M)
-- `gpt-4o`: $2.50/$10.00 per 1M input/output tokens (cached: $1.25 per 1M)
-- `gpt-4o-mini`: $0.15/$0.60 per 1M input/output tokens (cached: $0.075 per 1M)
-- `gpt-4-turbo`: $10.00/$30.00 per 1M input/output tokens (no caching)
-
-**Features:**
-- Fallback pricing for unknown models
-- Multi-dimensional token tracking (input, output, cached, thoughts, tool tokens for Gemini)
-
-### File Categories
-
-Automatically categorizes files into:
-- **Source Code**: .rs, .py, .js, .ts, .java, .cpp, .go, etc.
-- **Data**: .json, .xml, .yaml, .csv, .sql, .db, etc.
-- **Documentation**: .md, .txt, .html, .pdf, etc.
-- **Media**: .png, .jpg, .mp4, .mp3, etc.
-- **Config**: .config, .env, .toml, .ini, etc.
-- **Other**: Everything else
-
-### Dependencies
-
-Core dependencies:
-- `serde`/`simd-json` - SIMD-optimized JSON serialization and parsing
-- `chrono`/`chrono-tz` - Timestamp handling and timezone conversion
-- `ratatui` - Rich terminal user interface framework
-- `crossterm` - Cross-platform terminal manipulation
-- `reqwest` - HTTP client for Splitrail Cloud uploads
-- `tokio` - Async runtime for HTTP operations
-- `async-trait` - Async trait support for analyzer framework
-- `toml` - Configuration file format
-- `anyhow` - Error handling and context
-- `colored` - Terminal color output
-- `glob` - File pattern matching for data discovery
-- `itertools` - Iterator utilities
-- `rayon` - Parallel processing for file parsing
-- `dashmap` - Concurrent hash maps
-- `num-format` - Number formatting
-- `home` - Home directory detection
-- `lazy_static` - Static data initialization
+### Core Analyzer System
 
-## Configuration
+The codebase uses a **pluggable analyzer architecture** with the `Analyzer` trait as the foundation:
+
+1. **AnalyzerRegistry** (`src/analyzer.rs`) - Central registry managing all analyzers
+   - Discovers data sources across platforms (macOS, Linux, Windows)
+   - Coordinates parallel loading of analyzer stats
+   - Manages two-tier caching system (see below)
+
+2. **Individual Analyzers** (`src/analyzers/`) - Platform-specific implementations
+   - `claude_code.rs` - Claude Code analyzer (largest, most complex)
+   - `copilot.rs` - GitHub Copilot
+   - `cline.rs`, `roo_code.rs`, `kilo_code.rs` - VSCode extensions
+   - `codex_cli.rs`, `gemini_cli.rs`, `qwen_code.rs`, `opencode.rs` - CLI tools
+
+   Each analyzer:
+   - Discovers data sources via glob patterns or VSCode extension paths
+   - Parses conversations from JSON/JSONL files
+   - Normalizes to `ConversationMessage` format
+   - Implements optional incremental caching via `parse_single_file()`
+
+### Two-Tier Caching System
+
+**Critical for performance** - the caching system enables instant startup and incremental updates:
+
+1. **Per-File Cache** (`src/cache/mmap_repository.rs`)
+   - Memory-mapped rkyv archive for zero-copy access
+   - Stores metadata + daily stats per file
+   - Separate message storage (loaded lazily)
+   - Detects file changes via size/mtime comparison
+   - Supports delta parsing for append-only JSONL files
+
+2. **Snapshot Cache** (`src/cache/mod.rs::load_snapshot_hot_only()`)
+   - Caches final deduplicated result per analyzer
+   - "Hot" snapshot: lightweight stats for TUI display
+   - "Cold" snapshot: full messages for session details
+   - Fingerprint-based invalidation (hashes all source file paths + metadata)
+
+**Cache Flow:**
+- **Warm start**: Fingerprint matches → load hot snapshot → instant display
+- **Incremental**: Files changed → parse only changed files → merge with cached messages → rebuild stats
+- **Cold start**: No cache → parse all files → save snapshot for next time
+
+### Data Flow
+
+1. **Discovery**: Analyzers find data files using platform-specific paths
+2. **Parsing**: Parse JSON/JSONL files into `ConversationMessage` structs
+3. **Deduplication**: Hash-based dedup using `global_hash` field (critical for accuracy)
+4. **Aggregation**: Group messages by date, compute token counts, costs, file ops
+5. **Display**: TUI renders daily stats + real-time updates via file watcher
+
+### Key Types (`src/types.rs`)
+
+- **ConversationMessage**: Normalized message format across all analyzers
+  - Contains tokens, costs, file operations, tool usage stats
+  - Includes hashes for deduplication (`local_hash`, `global_hash`)
+
+- **Stats**: Comprehensive usage metrics
+  - Token counts (input, output, reasoning, cache tokens)
+  - File operations (reads, edits, deletes with line/byte counts)
+  - Todo tracking (created, completed, in_progress)
+  - File categorization (code, docs, data, media, config)
+
+- **DailyStats**: Pre-aggregated stats per date
+  - Message counts, conversation counts, model breakdown
+  - Embedded `Stats` struct with all metrics
+
+### Real-Time Monitoring
+
+**FileWatcher** (`src/watcher.rs`) provides live updates:
+- Watches analyzer data directories using `notify` crate
+- Invalidates cache entries on file changes
+- Triggers incremental re-parsing
+- Updates TUI in real-time via channels
 
-Configuration is stored in `~/.config/splitrail/config.toml`:
+**RealtimeStatsManager** coordinates:
+- Background file watching
+- Auto-upload to Splitrail Cloud (if configured)
+- Stats updates to TUI via `tokio::sync::watch`
 
+### MCP Server (`src/mcp/`)
+
+Splitrail can run as an MCP (Model Context Protocol) server:
+```bash
+cargo run -- mcp
+```
+
+Provides tools for:
+- `get_daily_stats` - Query usage statistics with filtering
+- `get_conversation_messages` - Retrieve message details
+- `get_model_breakdown` - Analyze model usage distribution
+
+Resources:
+- `splitrail://summary` - Daily summaries across all dates
+- `splitrail://models` - Model usage breakdown
+
+## Testing Strategy
+
+### Test Organization
+- **Unit tests**: Inline with source (`#[cfg(test)] mod tests`)
+- **Integration tests**: `src/analyzers/tests/` for analyzer-specific parsing tests
+- **Large test files**: Comprehensive tests in cache module for concurrency, persistence
+
+### Running Tests
+```bash
+# All tests
+cargo test
+
+# Specific analyzer
+cargo test claude_code
+
+# Cache tests (many edge cases covered here)
+cargo test cache
+
+# Single test
+cargo test test_file_metadata_is_stale
+```
+
+### Test Data
+Most analyzers use real-world JSON fixtures in test modules to verify parsing logic.
+
+## Common Development Tasks
+
+### Adding a New Analyzer
+
+1. Create new file in `src/analyzers/your_analyzer.rs`
+2. Implement the `Analyzer` trait:
+   ```rust
+   #[async_trait]
+   impl Analyzer for YourAnalyzer {
+       fn display_name(&self) -> &'static str { "Your Tool" }
+       fn discover_data_sources(&self) -> Result<Vec<DataSource>> { ... }
+       async fn parse_conversations(&self, sources: Vec<DataSource>) -> Result<Vec<ConversationMessage>> { ... }
+       // ... other required methods
+   }
+   ```
+3. For VSCode extensions, use `discover_vscode_extension_sources()` helper
+4. Register in `src/main.rs::create_analyzer_registry()`
+5. Add to `Application` enum in `src/types.rs`
+
+### Enabling Incremental Caching for an Analyzer
+
+1. Implement `parse_single_file()` to parse one file
+2. Return `supports_caching() -> true`
+3. For JSONL files, implement `parse_single_file_incremental()` and return `supports_delta_parsing() -> true`
+4. Include pre-aggregated `daily_contributions` in `FileCacheEntry`
+
+### Pricing Model Updates
+
+Token pricing is in `src/models.rs` using compile-time `phf` maps:
+- Add new model to appropriate constant (e.g., `ANTHROPIC_PRICING`)
+- Format: model name → `PricePerMillion { input, output, cache_creation, cache_read }`
+- Prices in USD per million tokens
+
+## Configuration
+
+User config stored at `~/.splitrail/config.toml`:
 ```toml
 [upload]
-api_token = "st_your_token_here"
+api_token = "..."
+server_url = "https://splitrail.dev/api"
 auto_upload = false
+
+[formatting]
+number_comma = false
+number_human = false
+locale = "en"
+decimal_places = 2
 ```
 
-### Configuration Commands
-- `splitrail config init` - Creates default config file
-- `splitrail config show` - Displays current settings
-- `splitrail config set api-token <token>` - Sets API token
-- `splitrail config set auto-upload <true|false>` - Enables/disables auto-upload
-
-## Features
-
-### Multi-Tool Support
-- **Claude Code**: Full support for JSONL conversation files, TodoWrite/TodoRead tracking
-- **Codex CLI**: Command-line coding agent with shell command execution, reasoning model support, and token tracking
-- **Gemini CLI**: JSON session parsing with thoughts tracking and multi-dimensional tokens
-- **GitHub Copilot**: Chat session analysis from VSCode/Cursor/Insiders extensions with tool invocation tracking
-- **Cline, Roo Code, Kilo Code, Qwen Code**: Additional VSCode extension analyzers for comprehensive coverage
-
-### Terminal User Interface
-- **Daily Stats View**: Comprehensive daily breakdown with costs, tokens, and operations
-- **Model Usage**: Model-specific statistics and abbreviations across all supported tools
-- **File Operations**: Detailed file operation analytics by category
-- **Navigation**: Keyboard controls for scrolling and interaction
-
-### Splitrail Cloud Integration
-- Secure API token-based authentication
-- Automatic daily stats upload when configured
-- Manual upload command for on-demand sharing
-- Privacy-focused: only aggregated statistics are uploaded to the leaderboard; per-day statistics are uploaded but are only shown to the user themselves
-
-### Analytics Tracking
-- **Token Usage**: Input, output, cache, thoughts, and tool token consumption
-- **Cost Analysis**: Precise cost calculations per model and tool
-- **File Operations**: Read/write/edit operations with byte/line counts
-- **Tool Usage**: Tool-specific command tracking (Bash, Glob, Grep for Claude Code; shell command execution and file operations for Codex CLI; read_many_files, replace, run_shell_command for Gemini CLI)
-- **Todo Management**: Task creation, completion, and productivity metrics (Claude Code)
-- **Conversation Analytics**: Message counts, tool calls, and flow analysis
-- **Deduplication**: Prevents duplicate entries across multiple data sources
+Cache stored at:
+- `~/.splitrail/cache.meta` - Memory-mapped metadata index
+- `~/.splitrail/snapshots/*.hot` - Hot snapshot cache
+- `~/.splitrail/snapshots/*.cold` - Cold message cache
+
+## Performance Considerations
+
+1. **Parallel Loading**: Analyzers load in parallel via `futures::join_all()`
+2. **Rayon for Parsing**: Use `.par_iter()` when parsing multiple files
+3. **Zero-Copy Cache**: rkyv enables instant deserialization from mmap
+4. **Delta Parsing**: JSONL analyzers parse only new lines since last offset
+5. **Lazy Message Loading**: TUI loads messages on-demand for session view
+
+## Code Style
+
+- Follow Rust 2024 edition conventions
+- Use `anyhow::Result` for error handling
+- Prefer `async/await` over raw futures
+- Use `parking_lot` locks over `std::sync` for performance
+- Keep large modules like `tui.rs` self-contained (consider refactoring if adding major features)
PATCH

echo "Gold patch applied."
