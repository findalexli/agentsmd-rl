#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sabiql

# Idempotency guard
if grep -qF "`AppState` \u306e\u30d5\u30a3\u30fc\u30eb\u30c9\u304c\u4ed6\u30d5\u30a3\u30fc\u30eb\u30c9\u304b\u3089\u6d3e\u751f\u3059\u308b\u5834\u5408\uff08\u4f8b: `connection_list_items` \u306f `connections` + `s" ".claude/rules/app-state.md" && grep -qF "| \u30ad\u30fc\u30de\u30c3\u30d4\u30f3\u30b0\u8ffd\u52a0\uff08Normal\u30e2\u30fc\u30c9\uff09 | `app/keybindings/normal.rs` + `mod.rs` \u306b predicate fn +" ".claude/rules/architecture.md" && grep -qF "- `connections.toml` \u30b9\u30ad\u30fc\u30de\u306e\u5909\u66f4\u306f\u65e2\u5b58\u306e\u8a2d\u5b9a\u30d5\u30a1\u30a4\u30eb\u3092\u58ca\u3057\u3066\u306f\u306a\u3089\u306a\u3044" ".claude/rules/config-migration.md" && grep -qF "\u5404 adapter \u30c7\u30a3\u30ec\u30af\u30c8\u30ea\u306f `mod.rs`\uff08\u30aa\u30fc\u30b1\u30b9\u30c8\u30ec\u30fc\u30b7\u30e7\u30f3\uff09+ CLI \u30c7\u30a3\u30ec\u30af\u30c8\u30ea\uff08\u30d7\u30ed\u30bb\u30b9\u5b9f\u884c\u30fb\u30d1\u30fc\u30b9\uff09+ `sql/`\uff08\u7d14\u7c8bSQL\u751f\u6210\uff09\u306e" ".claude/rules/db-agnostic.md" && grep -qF "- `app/keybindings/`: SSOT \u30e2\u30b8\u30e5\u30fc\u30eb \u2014 `KeyBinding`\uff08simple modes\uff09\u3068 `ModeRow`\uff08mixed m" ".claude/rules/interaction-contract.md" && grep -qF "`mod.rs` \u304c\u30aa\u30fc\u30b1\u30b9\u30c8\u30ec\u30fc\u30b7\u30e7\u30f3 \u2192 `sql/` \u3067SQL\u751f\u6210 \u2192 `psql/executor.rs` \u3067 psql \u5b9f\u884c \u2192 `psql/pars" ".claude/rules/postgres-adapter.md" && grep -qF "| \u72b6\u614b\u5909\u66f4 | Reducer \u304c `render_dirty = true` \u306b\u30bb\u30c3\u30c8 \u2192 main loop \u304c `Effect::Render` \u3092\u8ffd\u52a0" ".claude/rules/rendering-strategy.md" && grep -qF "fn classify_stderr_as_unknown_fallback(#[case] stderr: &str) { ... }" ".claude/rules/rstest-patterns.md" && grep -qF "- \u30e6\u30cb\u30c3\u30c8\u30c6\u30b9\u30c8\u306f `#[cfg(test)] mod tests` \u3067\u30e2\u30b8\u30e5\u30fc\u30eb\u5185\u306b\u914d\u7f6e" ".claude/rules/rust-testing-style.md" && grep -qF "fn create_table(schema: &str, name: &str, columns: &[&str]) -> Table { ... }" ".claude/rules/test-organization.md" && grep -qF "| **Infra (adapters)** | SQL \u751f\u6210\uff08\u65b9\u8a00\u56fa\u6709\uff09 | PG \u7528 `build_update_sql`\uff08MySQL \u5b9f\u88c5\u6642\u306f\u305d\u3061\u3089\u3082\uff09 " ".claude/rules/testing-obligations.md" && grep -qF "- \u30ab\u30fc\u30bd\u30eb\u63cf\u753b\u306f `text_cursor_spans()`\uff08`ui/components/atoms/text_cursor.rs`\uff09\u3092\u4f7f\u3046\u3053\u3068\u3002\u30a4\u30f3\u30e9\u30a4\u30f3" ".claude/rules/ui-design.md" && grep -qF "- \u3059\u3079\u3066\u306e `InputMode` \u30d0\u30ea\u30a2\u30f3\u30c8\u306b\u6700\u4f4e1\u3064\u306e\u30b9\u30ca\u30c3\u30d7\u30b7\u30e7\u30c3\u30c8\u30c6\u30b9\u30c8\u304c\u5fc5\u8981\uff08`testing-obligations.md` \u53c2\u7167\uff09" ".claude/rules/visual-regression.md" && grep -qF "| **visual-regression** | `tests/render_snapshots.rs`, `tests/snapshots/**` | in" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/app-state.md b/.claude/rules/app-state.md
@@ -0,0 +1,30 @@
+---
+paths:
+  - "**/src/app/state.rs"
+  - "**/src/app/reducers/**/*.rs"
+---
+
+# AppState 不変条件
+
+## 派生状態パターン（必須）
+
+`AppState` のフィールドが他フィールドから派生する場合（例: `connection_list_items` は `connections` + `service_entries` から派生）、**ソースフィールドはすべて private** にし、派生フィールドを自動再構築する setter 経由でのみ変更すること。
+
+| パターン | 可否 |
+|---------|------|
+| 派生グループへの直接代入（`state.foo = x`） | **禁止** |
+| 自動再構築付き setter（`state.set_foo(x)`） | **必須** |
+| `rebuild_*()` を公開APIとして提供 | **禁止**（private にして setter 内部から呼ぶ） |
+
+### 既存の適用例
+
+- **Connection グループ**: `connections`, `service_entries` → `connection_list_items`
+  - Setter: `set_connections`, `set_service_entries`, `set_connections_and_services`, `retain_connections`
+  - Getter: `connections()`, `service_entries()`, `connection_list_items()`
+
+新しい派生フィールドを追加する場合も同じパターンを適用すること。
+
+## State/View 分離（必須）
+
+- カーソル位置をコンテンツ `String` の一部としてエンコードしてはならない（例: テキスト中にカーソル文字を挿入する）
+- カーソル位置は View 層の関心事であり、State 内では独立した数値インデックスとして保持すること
diff --git a/.claude/rules/architecture.md b/.claude/rules/architecture.md
@@ -3,145 +3,63 @@ paths:
   - "**/src/**/*.rs"
 ---
 
-# Architecture Rules
+# アーキテクチャルール
 
-## Layer Structure (Hexagonal / Ports & Adapters)
+## レイヤ構造（ヘキサゴナル / Ports & Adapters）
 
 ```
 src/
-├── ui/          # Presentation Layer + UI Adapters
-├── app/         # Application Layer (State, Reducers, Ports)
-├── infra/       # Infrastructure Adapters
-└── domain/      # Domain Models (pure data structures)
+├── ui/          # プレゼンテーション層 + UI Adapters
+├── app/         # アプリケーション層（State, Reducers, Ports）
+├── infra/       # インフラストラクチャ Adapters
+└── domain/      # ドメインモデル（純粋なデータ構造）
 ```
 
-## Dependency Rules
+## 依存ルール
 
-**Allowed:**
+**許可:**
 - `ui/` → `app/` → `domain/`
-- `infra/adapters/` → `app/ports/` (implements traits)
-- `ui/adapters/` → `app/ports/` (implements traits)
+- `infra/adapters/` → `app/ports/`（trait を実装）
+- `ui/adapters/` → `app/ports/`（trait を実装）
 
-## Forbidden Dependencies (MUST NOT violate)
+## 禁止依存（違反不可）
 
-- `app/` → `ui/` — use Renderer port instead
-- `app/` → `infra/` — use ports like MetadataProvider, ConfigWriter
+- `app/` → `ui/` — 代わりに Renderer port を使う
+- `app/` → `infra/` — MetadataProvider, ConfigWriter 等の port を使う
 - `ui/` → `infra/`
 
-If you need app→infra communication, you MUST define a port trait in `app/ports/` and implement it in `infra/adapters/`.
-
-## Ports & Adapters Pattern
-
-Ports are **traits defined in `app/ports/`** that abstract external dependencies:
-
-| Port | Purpose | Adapter Location |
-|------|---------|------------------|
-| `MetadataProvider` | DB metadata fetching | `infra/adapters/` |
-| `QueryExecutor` | SQL execution | `infra/adapters/` |
-| `ConfigWriter` | Cache dir | `infra/adapters/` |
-| `Renderer` | TUI drawing | `ui/adapters/` |
-
-## Where to Put New Code
-
-| If you need to... | Put it in... |
-|-------------------|--------------|
-| Add UI component | `ui/components/` |
-| Add business logic | `app/` (pure functions, no I/O) |
-| Add external I/O | Define port in `app/ports/`, impl in `infra/adapters/` or `ui/adapters/` |
-| Add database-specific SQL or connection string logic | Define port in `app/ports/`, impl in `infra/adapters/` |
-| Add domain model | `domain/` |
-| Add pure calculation used by app | `app/` (e.g., `viewport.rs`, `ddl.rs`) |
-| Add key-to-action mapping (simple mode) | `app/keybindings/` (add entry with `combos` to appropriate submodule); `keymap::resolve()` handles it automatically |
-| Add key-to-action mapping (Normal mode) | `app/keybindings/normal.rs` + add predicate fn in `mod.rs` + wire in `handler.rs` |
-| Add DB-specific SQL or dialect logic | `infra/adapters/{postgres,mysql}/` (NEVER in `app/ports/`) |
-
-## Key Translation Flow
-
-```
-crossterm::KeyEvent
-  → ui/event/key_translator::translate()
-  → app::keybindings::KeyCombo
-  → app::keymap::resolve(combo, bindings)   (simple modes)
-     OR keybindings::is_quit(&combo) etc.   (Normal mode predicates)
-  → Action
-```
-
-**Responsibilities:**
-- `app/keybindings/`: SSOT module — `KeyBinding` (simple modes) and `ModeRow` (mixed modes with unified display+exec). Split by domain: `normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`, `types.rs`. Mixed modes use `ModeBindings { rows: &[ModeRow] }`, resolved via `.resolve()`.
-- `app/keymap.rs`: `resolve(combo, bindings)` for `KeyBinding` slices; `resolve_mode(combo, rows)` for `ModeRow` slices
-- `ui/event/key_translator.rs`: UI adapter — converts `crossterm::KeyEvent` → app-layer `KeyCombo`
-- `ui/event/handler.rs`: mode dispatch — calls `ModeBindings::resolve()` or predicate fns, applies context logic
-
-## Side-Effect Boundaries (MUST)
-
-- `app/` MUST be I/O-free. No filesystem, network, or process spawning.
-- `domain/` MUST be pure data. No methods with side effects.
-- Side effects are ONLY allowed in: `infra/adapters/`, `ui/adapters/`, `main.rs`
-- Reducers MUST return `Vec<Effect>` for side effects; NEVER execute them inline.
-
-## Derived State Invariants (MUST)
-
-When an `AppState` field is derived from other fields (e.g. `connection_list_items` is derived from `connections` + `service_entries`), **all source fields MUST be private** and mutated only through setters that automatically rebuild the derived field.
-
-| Pattern | Status |
-|---------|--------|
-| Direct field assignment (`state.foo = x`) for derived groups | **Forbidden** |
-| Setter with auto-rebuild (`state.set_foo(x)`) | **Required** |
-| Standalone `rebuild_*()` as public API | **Forbidden** (must be private, called internally by setters) |
-
-Existing enforced group:
-- **Connection group**: `connections`, `service_entries` → `connection_list_items`
-  - Setters: `set_connections`, `set_service_entries`, `set_connections_and_services`, `retain_connections`
-  - Getters: `connections()`, `service_entries()`, `connection_list_items()`
-
-When adding a new derived field to `AppState`, apply the same pattern: private fields + setter with auto-rebuild + read-only getters.
-
-### State/View Separation (MUST)
-
-- Cursor position MUST NOT be encoded as part of the content `String` (e.g., inserting a cursor character into the text). Cursor position is view-layer concern and must be kept as a separate numeric index in state.
-
-## Key Principles
-
-1. **app/ is I/O-free**: Reducers and state logic have no side effects. Effects are returned as data.
-2. **Ports invert dependencies**: app defines what it needs, adapters provide implementations.
-3. **UI adapters for UI concerns**: Rendering abstractions live in `ui/adapters/`, not `infra/`.
-4. **Domain is pure data**: No business logic in domain models, just structure.
-
-## Postgres Adapter Internal Structure
-
-```
-src/infra/adapters/postgres/
-├── mod.rs              # struct PostgresAdapter + MetadataProvider + QueryExecutor
-│                       # (orchestration: sql/ generates SQL → psql/ executes & parses)
-├── psql/               # psql process interaction
-│   ├── mod.rs          #   re-exports
-│   ├── executor.rs     #   process spawning (I/O, side effects)
-│   └── parser.rs       #   stdout → domain types (pure functions)
-├── sql/                # SQL string generation (all pure functions)
-│   ├── mod.rs          #   re-exports
-│   ├── query.rs        #   metadata queries + preview
-│   ├── ddl.rs          #   DDL generation (CREATE TABLE)
-│   └── dialect.rs      #   DML generation (UPDATE/DELETE)
-├── select_guard.rs     # SELECT safety check (pure function)
-└── dsn.rs              # DSN construction
-```
-
-**Data flow:** `mod.rs` orchestrates → `sql/` generates SQL → `psql/executor.rs` runs psql → `psql/parser.rs` parses output.
-
-**Visibility:** Functions default to private. Use `pub(in crate::infra::adapters::postgres)` for cross-submodule access. Tests use `#[cfg(test)]` within each submodule.
-
-**Quote functions:** Use `crate::infra::utils::{quote_ident, quote_literal}`. Do NOT duplicate as `pg_quote_*`.
-
-## Rendering Strategy
-
-Ratatui requires explicit render control. This app uses **event-driven rendering** (not fixed FPS):
-
-| Trigger | When to render |
-|---------|----------------|
-| State change | Reducer sets `render_dirty = true`; main loop adds `Effect::Render` |
-| Animation deadline | Spinner (150ms), cursor blink (500ms), message timeout, result highlight |
-| No activity | Sleep indefinitely until input or deadline |
-
-**Architecture split:**
-- `app/render_schedule.rs`: Pure function calculates next deadline (no I/O)
-- `main.rs`: UI layer handles `tokio::select!` with `sleep_until(deadline)`
+app→infra の通信が必要な場合、`app/ports/` に port trait を定義し `infra/adapters/` で実装すること。
+
+## Ports & Adapters パターン
+
+Port は `app/ports/` に定義された **trait** で、外部依存を抽象化する:
+
+| Port | 用途 | Adapter の場所 |
+|------|------|---------------|
+| `MetadataProvider` | DBメタデータ取得 | `infra/adapters/` |
+| `QueryExecutor` | SQL実行 | `infra/adapters/` |
+| `ConfigWriter` | キャッシュディレクトリ | `infra/adapters/` |
+| `Renderer` | TUI描画 | `ui/adapters/` |
+
+## 新規コードの配置先
+
+| やりたいこと | 配置先 |
+|-------------|--------|
+| UIコンポーネント追加 | `ui/components/` |
+| ビジネスロジック追加 | `app/`（純粋関数、I/Oなし） |
+| 外部I/O追加 | `app/ports/` に port 定義 → `infra/adapters/` or `ui/adapters/` で実装 |
+| DB固有のSQL・接続文字列ロジック追加 | `app/ports/` に port 定義 → `infra/adapters/` で実装 |
+| ドメインモデル追加 | `domain/` |
+| app層の純粋計算追加 | `app/`（例: `viewport.rs`, `ddl.rs`） |
+| キーマッピング追加（simpleモード） | `app/keybindings/` の該当サブモジュールにエントリ追加; `keymap::resolve()` が自動処理 |
+| キーマッピング追加（Normalモード） | `app/keybindings/normal.rs` + `mod.rs` に predicate fn + `handler.rs` で配線 |
+| DB固有SQL・方言ロジック追加 | `infra/adapters/{postgres,mysql}/`（`app/ports/` には絶対に置かない） |
+
+## 副作用境界（必須）
+
+- `app/` は I/O 禁止。ファイルシステム、ネットワーク、プロセス起動は不可
+- `domain/` は構造体とデータ変換のみ定義する
+- 副作用が許可される場所: `infra/adapters/`, `ui/adapters/`, `main.rs` のみ
+- Reducer は副作用を `Vec<Effect>` として返すこと。インラインで実行してはならない
+- UI adapter（描画の抽象化）は `ui/adapters/` に置く（`infra/` ではない）
+- Port による依存性逆転: app が必要なものを定義し、adapter が実装を提供
diff --git a/.claude/rules/config-migration.md b/.claude/rules/config-migration.md
@@ -5,16 +5,16 @@ paths:
   - "**/src/infra/adapters/connection_store.rs"
 ---
 
-# Config Migration Rules
+# 設定マイグレーションルール
 
-## Backward Compatibility (MUST)
+## 後方互換性（必須）
 
-- Changes to `connections.toml` schema MUST NOT break existing config files
-- New fields MUST have sensible defaults so old configs load without error
-- Removed fields MUST be silently ignored during deserialization
+- `connections.toml` スキーマの変更は既存の設定ファイルを壊してはならない
+- 新しいフィールドには適切なデフォルト値を設定し、古い設定がエラーなくロードできるようにする
+- 削除されたフィールドはデシリアライズ時にサイレントに無視すること
 
-## Schema Versioning
+## スキーマバージョニング
 
-- If a breaking schema change is unavoidable, add a `version` field to the config
-- Provide a migration path from the previous version
-- Log a clear warning when migrating old configs automatically
+- 破壊的なスキーマ変更がやむを得ない場合、設定に `version` フィールドを追加する
+- 前バージョンからのマイグレーションパスを提供する
+- 古い設定を自動マイグレーションする際は明確な警告をログに出すこと
diff --git a/.claude/rules/db-agnostic.md b/.claude/rules/db-agnostic.md
@@ -4,39 +4,34 @@ paths:
   - "**/src/infra/adapters/**/*.rs"
 ---
 
-# DB-Agnostic Rules
+# DB 非依存ルール
 
-## Port-level Neutrality (MUST)
+## Port レベルの中立性（必須）
 
-- Port traits in `app/ports/` MUST NOT contain PostgreSQL-specific SQL or syntax
-- Port method signatures MUST use generic types (no `PgType`, no PG-specific enums)
-- Port documentation MUST describe behavior without referencing a specific RDBMS
+- `app/ports/` の port trait は RDBMS 非依存の汎用型・構文のみ使用する
+- port メソッドのシグネチャは汎用型を使うこと（`PgType` や PG 固有 enum は不可）
+- port のドキュメントは RDBMS 非依存の振る舞いとして記述する
 
-## Adapter Isolation (MUST)
+## Adapter の分離（必須）
 
-- All DB-specific SQL, quoting, and connection string logic MUST live in `infra/adapters/{postgres,mysql}/`
-- Adapters MUST NOT leak dialect-specific types into port return types
-- When adding a feature to one adapter, open a tracking Issue for the other adapter
+- DB 固有の SQL、クォート、接続文字列ロジックはすべて `infra/adapters/{postgres,mysql}/` に配置すること
+- Adapter は方言固有の型を port の戻り値型に漏洩させてはならない
+- 一方の adapter に機能を追加したら、もう一方の adapter 用にトラッキング Issue を作成すること
 
-## Extension Readiness Checklist
+## 拡張準備チェックリスト
 
-When modifying any port trait:
-1. Verify the new method signature is dialect-neutral
-2. Check if existing PG adapter impl uses PG-specific syntax that should be abstracted
-3. If MySQL adapter stub exists, verify it compiles (even if `#[ignore]` tested)
+port trait を変更する際:
+1. 新しいメソッドシグネチャが方言中立であることを確認
+2. 既存の PG adapter 実装が抽象化すべき PG 固有構文を使っていないかチェック
+3. MySQL adapter スタブが存在する場合、コンパイルが通ることを確認（`#[ignore]` テストでも可）
 
-## Adapter Internal Submodule Conventions
+## Adapter 内部サブモジュール規約
 
-Each adapter directory (e.g., `postgres/`) follows this structure:
+各 adapter ディレクトリは `mod.rs`（オーケストレーション）+ CLI ディレクトリ（プロセス実行・パース）+ `sql/`（純粋SQL生成）の3層構造に従う。PG 固有の詳細は `postgres-adapter.md` を参照。
 
-- **`mod.rs`**: Struct definition + port trait impls (`MetadataProvider`, `QueryExecutor`). Orchestration only — no SQL generation or parsing logic.
-- **`psql/` (or `mysql/` CLI dir)**: Process execution (`executor.rs`) and output parsing (`parser.rs`). Side effects are confined to `executor.rs`.
-- **`sql/`**: Pure SQL string generation. Split by concern: `query.rs` (metadata), `ddl.rs` (DDL), `dialect.rs` (DML).
-- **Utility modules** (`select_guard.rs`, `dsn.rs`): Single-purpose pure functions.
+**MySQL adapter を追加する場合**、PG adapter の構造をミラーすること: `mysql/mod.rs`, `mysql/mysql_cli/`, `mysql/sql/` 等。
 
-**When adding a MySQL adapter**, mirror this structure: `mysql/mod.rs`, `mysql/mysql_cli/`, `mysql/sql/`, etc. Port trait impls go in `mod.rs`; dialect-specific SQL goes in `sql/`.
+## 現在の Adapter 状況
 
-## Current Adapter Status
-
-- PostgreSQL: primary, fully implemented
-- MySQL: planned, not yet implemented
+- PostgreSQL: メイン、完全実装済み
+- MySQL: 計画中、未実装
diff --git a/.claude/rules/interaction-contract.md b/.claude/rules/interaction-contract.md
@@ -1,38 +1,58 @@
 ---
 paths:
   - "**/src/app/keybindings/**/*.rs"
+  - "**/src/app/keymap.rs"
   - "**/src/ui/event/**/*.rs"
   - "**/src/ui/components/footer.rs"
   - "**/src/ui/components/help_overlay.rs"
   - "**/src/app/palette.rs"
 ---
 
-# Interaction Contract
+# インタラクション契約
 
-## Single Source of Truth (MUST)
+## 唯一の信頼できる情報源（必須）
 
-- `app/keybindings/` is the SSOT for ALL key bindings
-- Footer hints, Help overlay, and Command Palette MUST derive from keybindings data
-- NEVER define a key combo in `handler.rs` that is not declared in `keybindings/`
+- `app/keybindings/` がすべてのキーバインドの **SSOT**
+- フッターヒント、ヘルプオーバーレイ、コマンドパレットはキーバインドデータから派生させること
+- `keybindings/` で宣言されていないキーコンボを `handler.rs` に定義してはならない
 
-## Consistency Invariants (MUST)
+## 整合性の不変条件（必須）
 
-1. Every `KeyBinding` / `ModeRow` entry with a display label MUST appear in Help overlay
-2. Every keybinding shown in Footer MUST resolve to an action in `handler.rs`
-3. Command Palette entries MUST map to the same action names as keybindings
+1. `KeyBinding` / `ModeRow` エントリに表示ラベルがあれば、ヘルプオーバーレイに必ず表示する
+2. フッターに表示するキーバインドは `handler.rs` のアクションに必ず解決できる
+3. コマンドパレットのエントリはキーバインドと同じアクション名にマッピングする
 
-## Adding a New Keybinding — Full Checklist
+## キー変換フロー
 
-1. Add entry in `app/keybindings/{normal,overlays,connections,editors}.rs`
-2. If Normal mode: add predicate fn in `keybindings/mod.rs` + wire in `handler.rs`
-3. If ModeBindings mode: add `ModeRow` entry; dispatch is automatic
-4. Update Footer `display_hint` if the binding should be visible
-5. Update Help overlay section for the relevant mode
-6. If the action is palette-worthy: add to `app/palette.rs`
-7. Run snapshot tests to verify footer/help rendering
+```
+crossterm::KeyEvent
+  → ui/event/key_translator::translate()
+  → app::keybindings::KeyCombo
+  → app::keymap::resolve(combo, bindings)   (simple modes)
+     OR keybindings::is_quit(&combo) 等     (Normal mode predicates)
+  → Action
+```
 
-## Anti-patterns (FORBIDDEN)
+**責務分担:**
+- `app/keybindings/`: SSOT モジュール — `KeyBinding`（simple modes）と `ModeRow`（mixed modes）。サブモジュール: `normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`, `types.rs`。Mixed modes は `ModeBindings { rows: &[ModeRow] }` を使い `.resolve()` で解決
+- `app/keymap.rs`: `KeyBinding` スライス用の `resolve(combo, bindings)` と `ModeRow` スライス用の `resolve_mode(combo, rows)`
+- `ui/event/key_translator.rs`: UI adapter — `crossterm::KeyEvent` → app 層の `KeyCombo` に変換
+- `ui/event/handler.rs`: モードディスパッチ — `ModeBindings::resolve()` または predicate fn を呼び出し、コンテキストロジックを適用
 
-- Hardcoded key checks in `handler.rs` without `keybindings/` entry
-- Footer hint text that does not match keybindings display label
-- Help overlay listing a key that has no corresponding keybinding entry
+**Char フォールバックルール**: フリーテキスト入力のあるモード（TablePicker, ErTablePicker, CommandLine, CellEdit）は `keymap::resolve()` を先に試し、その後 `Char(c)` にフォールスルーする。これらのモードにコマンドキーとして `KeyCombo::plain(Key::Char(x))` を追加してはならない。非 Char キー（Up/Down/Esc/Enter）を使うこと。
+
+## 新規キーバインド追加チェックリスト
+
+1. `app/keybindings/{normal,overlays,connections,editors}.rs` にエントリ追加
+2. Normal mode の場合: `keybindings/mod.rs` に predicate fn を追加 + `handler.rs` で配線
+3. ModeBindings mode の場合: `ModeRow` エントリを追加（ディスパッチは自動）
+4. バインドをフッターに表示する場合: `display_hint` を更新
+5. 該当モードのヘルプオーバーレイセクションを更新
+6. パレットに表示すべきアクションなら `app/palette.rs` に追加
+7. スナップショットテストを実行してフッター/ヘルプの描画を確認
+
+## アンチパターン（禁止）
+
+- `keybindings/` エントリなしに `handler.rs` にハードコードしたキーチェック
+- キーバインドの表示ラベルと一致しないフッターヒントテキスト
+- 対応するキーバインドエントリがないキーをヘルプオーバーレイに記載
diff --git a/.claude/rules/postgres-adapter.md b/.claude/rules/postgres-adapter.md
@@ -0,0 +1,39 @@
+---
+paths:
+  - "**/src/infra/adapters/postgres/**/*.rs"
+---
+
+# Postgres Adapter 内部構造
+
+## ディレクトリ構成
+
+```
+src/infra/adapters/postgres/
+├── mod.rs              # PostgresAdapter構造体 + MetadataProvider / QueryExecutor impl
+│                       # （オーケストレーション: sql/ でSQL生成 → psql/ で実行・パース）
+├── psql/               # psql プロセス操作
+│   ├── mod.rs          #   re-exports
+│   ├── executor.rs     #   プロセス起動（I/O、副作用あり）
+│   └── parser.rs       #   stdout → ドメイン型への変換（純粋関数）
+├── sql/                # SQL文字列生成（すべて純粋関数）
+│   ├── mod.rs          #   re-exports
+│   ├── query.rs        #   メタデータクエリ + プレビュー
+│   ├── ddl.rs          #   DDL生成（CREATE TABLE）
+│   └── dialect.rs      #   DML生成（UPDATE/DELETE）
+├── select_guard.rs     # SELECT安全チェック（純粋関数）
+└── dsn.rs              # DSN構築
+```
+
+## データフロー
+
+`mod.rs` がオーケストレーション → `sql/` でSQL生成 → `psql/executor.rs` で psql 実行 → `psql/parser.rs` で出力パース
+
+## 可視性ルール
+
+- 関数はデフォルト private
+- サブモジュール間アクセスには `pub(in crate::infra::adapters::postgres)` を使う
+- テストは各サブモジュール内に `#[cfg(test)]` で配置
+
+## クォート関数
+
+`crate::infra::utils::{quote_ident, quote_literal}` を使うこと。`pg_quote_*` のような重複関数を作ってはならない。
diff --git a/.claude/rules/rendering-strategy.md b/.claude/rules/rendering-strategy.md
@@ -0,0 +1,22 @@
+---
+paths:
+  - "**/src/app/render_schedule.rs"
+  - "**/src/main.rs"
+---
+
+# レンダリング戦略
+
+Ratatui は明示的な描画制御が必要。本アプリは**イベント駆動レンダリング**（固定FPSではない）を採用。
+
+## レンダリングトリガー
+
+| トリガー | レンダリングタイミング |
+|---------|---------------------|
+| 状態変更 | Reducer が `render_dirty = true` にセット → main loop が `Effect::Render` を追加 |
+| アニメーション deadline | Spinner(150ms)、カーソル点滅(500ms)、メッセージタイムアウト、結果ハイライト |
+| 無操作時 | 入力またはdeadlineまで無期限スリープ |
+
+## アーキテクチャ分離
+
+- `app/render_schedule.rs`: 次のdeadlineを計算する純粋関数（I/Oなし）
+- `main.rs`: UI層が `tokio::select!` + `sleep_until(deadline)` を処理
diff --git a/.claude/rules/rstest-patterns.md b/.claude/rules/rstest-patterns.md
@@ -0,0 +1,49 @@
+---
+paths:
+  - "**/src/domain/**/*.rs"
+  - "**/src/infra/adapters/**/parser*.rs"
+  - "**/src/infra/adapters/**/sql/**/*.rs"
+---
+
+# rstest パターンガイド
+
+## rstest の凝集度ルール
+
+既存の `#[rstest]` 関数にケースを追加する前に、すべてのケースが同じ**振る舞いカテゴリ**に属しているか確認すること。
+
+- 複数カテゴリが混在している場合はカテゴリごとに分割する
+  - 例: `ErrorKind` 別 / valid-invalid 別 / キーの役割別
+- vim/矢印キーのエイリアスペアは**同じ関数内**に置く（分割しない）
+- **目安**: 1関数が8ケースを超えたら分割を検討する
+
+```rust
+// ✅ 各関数が単一の振る舞いカテゴリをテスト
+#[rstest]
+#[case("psql: command not found")]
+#[case("not found: mysql")]
+fn classify_stderr_as_cli_not_found(#[case] stderr: &str) { ... }
+
+#[rstest]
+#[case("Connection refused")]
+#[case("Some random error")]
+#[case("")]
+fn classify_stderr_as_unknown_fallback(#[case] stderr: &str) { ... }
+
+// ✅ vim/矢印エイリアスはまとめて良い
+#[rstest]
+#[case(Key::Up, Action::ScrollUp)]
+#[case(Key::Char('k'), Action::ScrollUp)]
+#[case(Key::Down, Action::ScrollDown)]
+#[case(Key::Char('j'), Action::ScrollDown)]
+fn scroll_keys(#[case] code: Key, #[case] expected: Action) { ... }
+```
+
+## rstest を使うべきとき
+
+- テストが入力→期待出力の純粋なマッピングで、類似ケースが多い場合
+- 複数のエイリアス、キーバリアント、境界値パターンがテーブルに収まる場合
+
+## 個別 #[test] を使うべきとき
+
+- 仕様上重要な振る舞いで、テスト名から読み取れることが大事な場合
+- 特殊な分岐やリグレッションシナリオで、専用テストに値する場合
diff --git a/.claude/rules/rust-testing-style.md b/.claude/rules/rust-testing-style.md
@@ -4,90 +4,30 @@ paths:
   - "**/tests/**/*.rs"
 ---
 
-# Rust Testing Style Guidelines
+# Rust テストスタイルガイド
 
-## Basic Principles
+## 基本原則
 
-- Use standard `#[test]` + `rstest`
-- Use `mockall` for mocking (only when necessary)
-- Use `#[tokio::test]` for async tests
+- 標準の `#[test]` + `rstest` を使う
+- モック必要時は `mockall` を使う
+- 非同期テストには `#[tokio::test]` を使う
 
-## Test Structure
+## テスト構造
 
-### Unit Tests (within modules)
+- ユニットテストは `#[cfg(test)] mod tests` でモジュール内に配置
+- インテグレーションテストは `tests/` ディレクトリに配置
 
-```rust
-#[cfg(test)]
-mod tests {
-    use super::*;
-
-    #[test]
-    fn valid_email_returns_ok() {
-        let input = "user@example.com";
-
-        let result = Email::new(input);
-
-        assert!(result.is_ok());
-    }
-}
-```
-
-### Boundary Value & Pattern Tests (rstest)
-
-```rust
-use rstest::rstest;
-
-#[rstest]
-#[case("Aa1!aaa", false)]    // 7 characters
-#[case("Aa1!aaaa", true)]    // 8 characters
-fn password_length_validation(#[case] input: &str, #[case] expected: bool) {
-    let result = Password::new(input);
-    assert_eq!(result.is_ok(), expected);
-}
-```
-
-### When to Use rstest vs #[test]
-
-Use `rstest` when:
-- The test is a pure mapping of input → expected output with many similar cases.
-- There are multiple aliases, key variants, or boundary patterns that fit a table.
+## 命名規約
 
-Use individual `#[test]` when:
-- The case is a spec-critical behavior that should be easy to read by name.
-- The behavior is a special branch or regression scenario that deserves a dedicated test.
-
-### Grouping (using mod for context)
-
-```rust
-#[cfg(test)]
-mod tests {
-    use super::*;
-
-    mod save {
-        use super::*;
-
-        #[test]
-        fn inserts_new_user() { ... }
-
-        #[test]
-        fn returns_duplicate_error_on_conflict() { ... }
-    }
-}
-```
+- `<条件>_returns_<結果>`
+- `<条件>_<動作>s_<結果>`
 
-## Naming Conventions
-
-### Function Name Patterns
-
-- `<condition>_returns_<result>`
-- `<condition>_<action>s_<result>`
-
-Examples:
+例:
 - `valid_input_returns_ok`
 - `empty_string_returns_validation_error`
 - `duplicate_email_returns_conflict`
 
-## Test Structure (given/when/then)
+## テスト構造（given/when/then）
 
 ```rust
 #[test]
@@ -104,70 +44,11 @@ fn register_with_valid_input_returns_registered_user() {
 }
 ```
 
-## rstest Cohesion Rules
-
-Before adding cases to an existing `#[rstest]` function, verify all cases belong to the same **behavior category**.
-
-- If multiple categories are mixed, split by category:
-  - Examples: by `ErrorKind` / valid-invalid / key role
-- vim/arrow alias pairs belong in the **same** function (do not split them)
-- **Guideline**: if a function exceeds 8 cases, re-evaluate whether it needs splitting
-
-```rust
-// ✅ Each function tests a single behavior category
-#[rstest]
-#[case("psql: command not found")]
-#[case("not found: mysql")]
-fn classify_stderr_as_cli_not_found(#[case] stderr: &str) { ... }
-
-#[rstest]
-#[case("Connection refused")]
-#[case("Some random error")]
-#[case("")]
-fn classify_stderr_as_unknown_fallback(#[case] stderr: &str) { ... }
-
-// ✅ vim/arrow aliases stay together
-#[rstest]
-#[case(Key::Up, Action::ScrollUp)]
-#[case(Key::Char('k'), Action::ScrollUp)]
-#[case(Key::Down, Action::ScrollDown)]
-#[case(Key::Char('j'), Action::ScrollDown)]
-fn scroll_keys(#[case] code: Key, #[case] expected: Action) { ... }
-```
-
-## Test mod Structure Rules
-
-- When `#[test]` functions in a single file exceed **20**, group them into `mod` blocks
-- `mod` names should be nouns describing the behavior domain (e.g., `connection_error`, `result_pane`)
-- Flat test lists make it unclear "where to look for what"
-
-```rust
-// ✅ grouped by behavior domain
-mod connection_flow { ... }
-mod overlays { ... }
-mod result_pane { ... }
-```
-
-## Fixture Extraction Rules
-
-- If the same struct literal appears in **2 or more** tests, extract it as a helper function
-- If an inline struct exceeds **15 lines**, consider extracting it as a fixture
-- If the same helper function is defined in **2 sub-mods**, move it to the parent `mod tests` scope
-
-```rust
-// ✅ extracted to parent mod tests scope
-fn create_test_profile(name: &str) -> ConnectionProfile { ... }
-fn minimal_users_table() -> Table { ... }
-fn create_table(schema: &str, name: &str, columns: &[&str]) -> Table { ... }
-```
-
-## Summary
+## まとめ
 
-| Test Type | Style |
-| --------- | ----- |
-| VO / Simple logic | `#[test]` flat |
-| Boundary values / Patterns | `rstest` + `#[case]` |
-| Feature groups | Nested with `mod` |
-| Integration / E2E | `tests/` directory |
-| rstest with mixed categories | Split by behavior category |
-| Repeated struct literals | Extract as helper function |
+| テスト種別 | スタイル |
+|-----------|---------|
+| VO / 単純ロジック | `#[test]` フラット |
+| 境界値 / パターン | `rstest` + `#[case]` |
+| 機能グループ | `mod` でネスト |
+| インテグレーション / E2E | `tests/` ディレクトリ |
diff --git a/.claude/rules/test-organization.md b/.claude/rules/test-organization.md
@@ -0,0 +1,33 @@
+---
+paths:
+  - "**/src/app/**/*.rs"
+  - "**/src/ui/event/**/*.rs"
+---
+
+# テスト構成ルール
+
+## mod 構造ルール
+
+- 1ファイル内の `#[test]` 関数が **20個を超えたら**、`mod` ブロックでグループ化する
+- `mod` 名は振る舞いドメインを表す名詞にする（例: `connection_error`, `result_pane`）
+- フラットなテストリストは「どこに何があるか」が分かりにくくなる
+
+```rust
+// ✅ 振る舞いドメインでグループ化
+mod connection_flow { ... }
+mod overlays { ... }
+mod result_pane { ... }
+```
+
+## フィクスチャ抽出ルール
+
+- 同じ構造体リテラルが **2つ以上** のテストに出現したら、ヘルパー関数に抽出する
+- インライン構造体が **15行を超えたら**、フィクスチャとして抽出を検討する
+- 同じヘルパー関数が **2つの子 mod** で定義されていたら、親の `mod tests` スコープに移動する
+
+```rust
+// ✅ 親 mod tests スコープに抽出
+fn create_test_profile(name: &str) -> ConnectionProfile { ... }
+fn minimal_users_table() -> Table { ... }
+fn create_table(schema: &str, name: &str, columns: &[&str]) -> Table { ... }
+```
diff --git a/.claude/rules/testing-obligations.md b/.claude/rules/testing-obligations.md
@@ -4,42 +4,41 @@ paths:
   - "**/tests/**/*.rs"
 ---
 
-# Testing Obligations
+# テスト義務
 
-## MUST-test Targets by Layer
+## レイヤ別の必須テスト対象
 
-| Layer | MUST-test Scenario | Example |
-|-------|-------------------|---------|
-| **Domain** | Every public constructor / validation | `ConnectionConfig::new()` boundary values |
-| **App (reducers)** | Every state transition that changes `AppState` | Action dispatch → state diff |
-| **App (ports)** | Default-impl methods on port traits | `DdlGenerator::ddl_line_count()` |
-| **Infra (parsers)** | CLI output parsing for each adapter | `psql` tabular output → `QueryResult` |
-| **Infra (adapters)** | SQL generation (dialect-specific) | `build_update_sql` for PG (and MySQL when implemented) |
-| **UI (components)** | Rendering boundary conditions | Empty table, overflow, error states |
-| **Integration** | Cross-layer round-trips | `tests/render_snapshots.rs` |
+| レイヤ | 必須テストシナリオ | 例 |
+|--------|-------------------|-----|
+| **Domain** | すべての public コンストラクタ / バリデーション | `ConnectionConfig::new()` の境界値 |
+| **App (reducers)** | `AppState` を変更するすべての状態遷移 | Action ディスパッチ → state diff |
+| **App (ports)** | port trait のデフォルト実装メソッド | `DdlGenerator::ddl_line_count()` |
+| **Infra (parsers)** | 各 adapter の CLI 出力パース | `psql` テーブル出力 → `QueryResult` |
+| **Infra (adapters)** | SQL 生成（方言固有） | PG 用 `build_update_sql`（MySQL 実装時はそちらも） |
+| **UI (components)** | 描画の境界条件 | 空テーブル、オーバーフロー、エラー状態 |
+| **Integration** | レイヤ横断のラウンドトリップ | `tests/render_snapshots.rs` |
 
-## `#[ignore]` Tracking Rule (MUST)
+## `#[ignore]` トラッキングルール（必須）
 
-- Every `#[ignore]` test MUST have a comment linking to a tracking Issue
-- Format: `#[ignore] // tracked: #<issue-number> — <reason>`
-- Bare `#[ignore]` without tracking comment is **FORBIDDEN**
-- When resolving the linked Issue, the `#[ignore]` MUST be removed or updated
+- すべての `#[ignore]` テストにトラッキング Issue へのリンクコメントが必要
+- 形式: `#[ignore] // tracked: #<issue番号> — <理由>`
+- リンク先 Issue を解決したら `#[ignore]` を削除または更新すること
 
 ```rust
-#[ignore] // tracked: #42 — waiting for MySQL adapter
+#[ignore] // tracked: #42 — MySQL adapter 待ち
 #[test]
 fn mysql_query_parsing() { ... }
 ```
 
-## Snapshot Test Obligation
+## スナップショットテスト義務
 
-- Each new `InputMode` variant MUST have at least one snapshot in `tests/render_snapshots.rs`
-- See `visual-regression.md` for detailed coverage criteria
+- 新しい `InputMode` バリアントには `tests/render_snapshots.rs` に最低1つのスナップショットが必要
+- 詳細なカバレッジ基準は `visual-regression.md` を参照
 
-## PR Self-check (for Claude)
+## PR セルフチェック（Claude 向け）
 
-Before marking a PR ready:
-- [ ] New public functions have unit tests
-- [ ] Adapter SQL generation tested for all supported dialects
-- [ ] No bare `#[ignore]` without tracking Issue
-- [ ] New `InputMode` variants have snapshot tests
+PR を ready にする前に:
+- [ ] 新しい public 関数にユニットテストがある
+- [ ] adapter の SQL 生成がサポート対象の全方言でテストされている
+- [ ] トラッキング Issue なしの `#[ignore]` がない
+- [ ] 新しい `InputMode` バリアントにスナップショットテストがある
diff --git a/.claude/rules/ui-design.md b/.claude/rules/ui-design.md
@@ -3,67 +3,44 @@ paths:
   - "**/src/ui/**/*.rs"
 ---
 
-# UI Design Rules
+# UI設計ルール
 
-## Component Structure (Atomic Design)
+## コンポーネント構造（Atomic Design）
 
-UI components follow the Atomic Design pattern:
+UIコンポーネントは Atomic Design パターンに従う:
 
 ```
 src/ui/components/
-├── atoms/       # Smallest reusable units (spinner, key_chip, panel_border)
-├── molecules/   # Compositions of atoms (modal_frame, hint_bar)
-└── *.rs         # Organisms: screen-level components (explorer, inspector, etc.)
+├── atoms/       # 最小の再利用単位（spinner, key_chip, panel_border）
+├── molecules/   # atoms の組み合わせ（modal_frame, hint_bar）
+└── *.rs         # Organisms: 画面レベルのコンポーネント（explorer, inspector 等）
 ```
 
-| Layer | Purpose | Examples |
-|-------|---------|----------|
-| atoms | Single-purpose primitives | `spinner_char()`, `key_chip()`, `panel_block()`, `text_cursor_spans()` |
-| molecules | Reusable patterns combining atoms | `render_modal()`, `hint_line()` |
-| organisms | Screen sections, may use molecules/atoms | `Explorer`, `SqlModal`, `Footer` |
+| レイヤ | 用途 | 例 |
+|--------|------|-----|
+| atoms | 単一目的のプリミティブ | `spinner_char()`, `key_chip()`, `panel_block()`, `text_cursor_spans()` |
+| molecules | atoms を組み合わせた再利用パターン | `render_modal()`, `hint_line()` |
+| organisms | 画面セクション。molecules/atoms を使う | `Explorer`, `SqlModal`, `Footer` |
 
-When adding UI components:
-- Extract repeated visual patterns into atoms/molecules
-- Use `Theme::*` tokens instead of raw `Color::*` values
-- Organisms should compose molecules/atoms, not duplicate their logic
+UIコンポーネント追加時:
+- 繰り返し出現するビジュアルパターンは atoms/molecules に切り出す
+- `Color::*` 直指定ではなく `Theme::*` トークンを使う
+- Organisms は molecules/atoms を合成し、ロジックを複製しない
 
-## Single-line Text Input
+## 単一行テキスト入力
 
-- All **new** single-line text input fields MUST use `TextInputState` (`app/text_input.rs`) for state management
-  - Known exception: `ConnectionSetupState` currently manages its own `cursor_position` / `viewport_offset` (migration tracked separately)
-- Cursor rendering MUST use `text_cursor_spans()` (`ui/components/atoms/text_cursor.rs`); do NOT duplicate cursor drawing logic inline
+- **新規の**単一行テキスト入力フィールドはすべて `TextInputState`（`app/text_input.rs`）で状態管理すること
+  - 既知の例外: `ConnectionSetupState` は現在独自に `cursor_position` / `viewport_offset` を管理している（マイグレーションは別途追跡）
+- カーソル描画は `text_cursor_spans()`（`ui/components/atoms/text_cursor.rs`）を使うこと。インラインでカーソル描画ロジックを複製してはならない
 
-## Footer Hint Ordering
+## フッターヒント順序
 
-All input modes must follow this ordering:
+すべての InputMode で以下の順序に従うこと:
 
 ```
-Actions → Navigation → Help → Close/Cancel → Quit
+アクション → ナビゲーション → ヘルプ → 閉じる/キャンセル → 終了
 ```
 
-## Interaction Contract
+## インタラクション契約
 
-See `interaction-contract.md` for keybinding consistency rules (SSOT, derived displays, anti-patterns).
-When adding keybindings, follow the full checklist defined there.
-
-## Keybindings & Commands
-
-Keybinding and command definitions follow this architecture:
-
-| Concept | Location | Responsibility |
-|---------|----------|----------------|
-| Data definitions | `app/keybindings/` | SSOT module: `KeyBinding` (simple modes) + `ModeRow`/`ModeBindings` (mixed modes). Submodules: `normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`, `types.rs` |
-| Key resolution | `app/keymap.rs` | `resolve(combo, bindings)` for `KeyBinding` slices; `resolve_mode(combo, rows)` for `ModeRow` slices — both called via `ModeBindings::resolve()` or directly |
-| Key translation | `ui/event/key_translator.rs` | `translate(KeyEvent) -> KeyCombo` — crossterm adapter |
-| Mode dispatch | `ui/event/handler.rs` | Routes `KeyCombo` to handler by `InputMode` |
-| Display logic | `ui/components/footer.rs` | Context-sensitive hint selection by InputMode/state |
-| Full reference | `ui/components/help_overlay.rs` | Complete keybinding reference |
-| Command list | `app/palette.rs` | Commands shown in Command Palette |
-
-When adding a new keybinding:
-1. Add an entry to the appropriate submodule in `keybindings/` (`normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`)
-2. **Modes with `ModeBindings`** (Help, ConnectionError, ConnectionSelector, CommandPalette, TablePicker, ErTablePicker): add a `ModeRow` entry to the corresponding `*_ROWS` constant with display text and `bindings: &[ExecBinding { ... }]`. `ModeBindings::resolve()` handles dispatch automatically.
-3. **Normal mode**: also add a predicate function (e.g., `pub fn is_foo(combo: &KeyCombo) -> bool`) in `mod.rs` and wire it in `handle_normal_mode` in `handler.rs`
-4. Update Footer/Help/Palette display as needed
-
-**Char fallback rule**: Modes with freeform text input (TablePicker, ErTablePicker, CommandLine, CellEdit) use `keymap::resolve()` first, then fall through to `Char(c)` for text input. Do NOT add plain `KeyCombo::plain(Key::Char(x))` combos to these modes for command keys — use non-Char keys (Up/Down/Esc/Enter) instead.
+キーバインドの整合性ルールと追加チェックリストは `interaction-contract.md` を参照。
diff --git a/.claude/rules/visual-regression.md b/.claude/rules/visual-regression.md
@@ -4,69 +4,68 @@ paths:
   - "**/tests/snapshots/**"
 ---
 
-# Visual Regression Testing
+# ビジュアルリグレッションテスト
 
-## Overview
+## 概要
 
-- **Library**: [insta](https://insta.rs) - Rust snapshot testing
-- **Scope**: Tests `AppState` → `MainLayout::render()` integration
-- **Backend**: Ratatui `TestBackend` (in-memory terminal 80x24)
+- **ライブラリ**: [insta](https://insta.rs) - Rust スナップショットテスト
+- **スコープ**: `AppState` → `MainLayout::render()` の統合テスト
+- **バックエンド**: Ratatui `TestBackend`（インメモリターミナル 80x24）
 
-## Directory Structure
+## ディレクトリ構成
 
 ```
 tests/
 ├── harness/
-│   ├── mod.rs       # Test utilities (render_to_string, create_test_*)
-│   └── fixtures.rs  # Sample data builders (metadata, table detail, query result)
-├── render_snapshots.rs  # Snapshot test scenarios
-└── snapshots/           # Generated .snap files (auto-created by insta)
+│   ├── mod.rs       # テストユーティリティ（render_to_string, create_test_*）
+│   └── fixtures.rs  # サンプルデータビルダー（metadata, table detail, query result）
+├── render_snapshots.rs  # スナップショットテストシナリオ
+└── snapshots/           # 生成された .snap ファイル（insta が自動作成）
 ```
 
-## Commands
+## コマンド
 
 ```bash
-mise run test                      # Run all tests
-mise exec -- cargo insta review    # Review pending snapshots interactively
-mise exec -- cargo insta accept    # Accept all pending snapshots
-mise exec -- cargo insta reject    # Reject all pending snapshots
+mise run test                      # 全テスト実行
+mise exec -- cargo insta review    # 保留中のスナップショットを対話的にレビュー
+mise exec -- cargo insta accept    # 保留中のスナップショットをすべて承認
+mise exec -- cargo insta reject    # 保留中のスナップショットをすべて拒否
 ```
 
-## Adding New Scenarios
+## 新しいシナリオの追加方法
 
-1. Add test function in `tests/render_snapshots.rs`
-2. Run `mise run test` (will fail with new snapshot)
-3. Review the generated `.snap.new` file
-4. Run `mise exec -- cargo insta accept`
+1. `tests/render_snapshots.rs` にテスト関数を追加
+2. `mise run test` を実行（新しいスナップショットで失敗する）
+3. 生成された `.snap.new` ファイルをレビュー
+4. `mise exec -- cargo insta accept` を実行
 
-## Coverage Criteria
+## カバレッジ基準
 
-### Mode Coverage Obligation (MUST)
+### モードカバレッジ義務（必須）
 
-- Every `InputMode` variant MUST have at least one snapshot test
-- When adding a new `InputMode`, add a corresponding snapshot BEFORE the PR is merged
+- すべての `InputMode` バリアントに最低1つのスナップショットテストが必要（`testing-obligations.md` 参照）
 
-### When to Add a Snapshot Test
+### スナップショットテストを追加すべきとき
 
-- **Each InputMode** - At least one scenario per mode
-- **Major UI state changes** - Focus pane switching, message display
-- **Boundary conditions** - Empty results, initial loading state, error states
-- **Text input components** - Cursor at head, middle, and tail positions (3 states minimum)
+- **各 InputMode** — モードごとに最低1シナリオ
+- **主要な UI 状態変更** — フォーカスペイン切り替え、メッセージ表示
+- **境界条件** — 空の結果、初期ロード状態、エラー状態
+- **テキスト入力コンポーネント** — カーソルが先頭、中間、末尾の3状態（最低3つ）
 
-### When NOT to Add
+### 追加不要なケース
 
-- **Data variations** - Different row counts, column counts within same screen
-- **Exhaustive combinations** - All possible state permutations
-- **Transient states** - Brief loading indicators (except persistent ones like ER progress)
+- **データバリエーション** — 同じ画面内での行数・列数の違い
+- **網羅的な組み合わせ** — すべての状態の順列
+- **一時的な状態** — 短時間のローディングインジケータ（ER 進捗表示のような永続的なものは除く）
 
-## Snapshot Update Policy
+## スナップショット更新ポリシー
 
-### Allowed
+### 許可
 
-- **Intentional UI changes** - Layout, styling, new features
-- **Bug fixes that change visual output** - After fixing the display bug
+- **意図的な UI 変更** — レイアウト、スタイリング、新機能
+- **表示バグの修正で出力が変わる場合** — バグ修正後
 
-### Not Allowed
+### 不許可
 
-- **Failing tests due to regressions** - Fix the code, not the snapshot
-- **Unintentional changes** - Investigate the diff first
+- **リグレッションによるテスト失敗** — スナップショットではなくコードを修正する
+- **意図しない変更** — まず diff を調査すること
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -33,27 +33,36 @@ mise run test               # Run tests
 
 ## Rules and Skills
 
-Rules are stored in `.claude/rules/` and are **automatically loaded** based on `paths` frontmatter patterns.
-Skills are stored in `.claude/skills/`:
-- **Manual** skills: only user can invoke via `/skill-name` (`disable-model-invocation: true`)
-- **Auto** skills: Claude fires automatically based on conversation context
-  - `user-invocable: false` additionally hides the skill from the `/` menu
+Rules（`.claude/rules/`）は `paths` フロントマターのパターンに基づき**自動ロード**される。
+Skills（`.claude/skills/`）は手動で `/skill-name` で呼び出す。
 
 ### Available Rules
 
-| Rule | Applies to | Description |
-|------|-----------|-------------|
-| **architecture** | `**/src/**/*.rs` | Hexagonal architecture, layer deps, ports & adapters, side-effect boundaries |
-| **ui-design** | `**/src/ui/**/*.rs` | Atomic Design pattern, footer hint ordering, keybindings |
-| **interaction-contract** | keybindings, event handler, footer, help, palette files | Keybinding SSOT consistency, full checklist |
-| **db-agnostic** | `**/src/app/ports/**`, `**/src/infra/adapters/**` | Port neutrality, adapter isolation, MySQL readiness |
-| **config-migration** | config_writer, connection_store files | Backward-compatible config schema changes |
-| **rust-testing-style** | `**/src/**/*.rs`, `**/tests/**/*.rs` | Test naming, structure, rstest usage |
-| **testing-obligations** | `**/src/**/*.rs`, `**/tests/**/*.rs` | MUST-test targets by layer, `#[ignore]` tracking |
-| **visual-regression** | `**/tests/render_snapshots.rs`, `**/tests/snapshots/**` | insta snapshots, mode coverage obligation |
+**全体（`**/src/**/*.rs`）:**
+
+| Rule | 説明 |
+|------|------|
+| **architecture** | ヘキサゴナルアーキテクチャ、レイヤ依存、Ports & Adapters、副作用境界 |
+| **rust-testing-style** | テスト命名、構造、given/when/then |
+| **testing-obligations** | レイヤ別必須テスト、`#[ignore]` トラッキング |
+
+**レイヤ・パス限定**（対象パスは概要。正確な glob は各ルールの frontmatter を参照）**:**
+
+| Rule | 対象パス | 説明 |
+|------|---------|------|
+| **app-state** | `app/state.rs`, `app/reducers/**` | 派生状態パターン、State/View分離 |
+| **postgres-adapter** | `infra/adapters/postgres/**` | Adapter内部構造、data flow、可視性 |
+| **rendering-strategy** | `app/render_schedule.rs`, `main.rs` | イベント駆動レンダリング、トリガー表 |
+| **ui-design** | `src/ui/**` | Atomic Design、フッター順序、テキスト入力 |
+| **interaction-contract** | keybindings, handler, footer, help, palette | SSOT整合性、キー変換フロー、チェックリスト |
+| **db-agnostic** | `app/ports/**`, `infra/adapters/**` | Port中立性、Adapter分離、MySQL準備 |
+| **config-migration** | config_writer, connection_store | 後方互換スキーマ変更 |
+| **rstest-patterns** | `domain/**`, `infra/**/parser*`, `infra/**/sql/**` | rstest凝集度、境界値パターン |
+| **test-organization** | `app/**`, `ui/event/**` | mod構造、フィクスチャ抽出 |
+| **visual-regression** | `tests/render_snapshots.rs`, `tests/snapshots/**` | instaスナップショット、モードカバレッジ |
 
 ### Available Skills
 
 | Skill | Type | Description |
 |-------|------|-------------|
-| **release** | Manual | Version bump, tag creation, GitHub release workflow |
+| **release** | Manual | バージョンバンプ、タグ作成、GitHub リリース |
PATCH

echo "Gold patch applied."
