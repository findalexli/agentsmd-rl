"""Behavioral checks for sabiql-sab94-refactor-split-and-localize (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/sabiql")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/app-state.md')
    assert '`AppState` のフィールドが他フィールドから派生する場合（例: `connection_list_items` は `connections` + `service_entries` から派生）、**ソースフィールドはすべて private** にし、派生フィールドを自動再構築する setter 経由でのみ変更すること。' in text, "expected to find: " + '`AppState` のフィールドが他フィールドから派生する場合（例: `connection_list_items` は `connections` + `service_entries` から派生）、**ソースフィールドはすべて private** にし、派生フィールドを自動再構築する setter 経由でのみ変更すること。'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/app-state.md')
    assert '- Setter: `set_connections`, `set_service_entries`, `set_connections_and_services`, `retain_connections`' in text, "expected to find: " + '- Setter: `set_connections`, `set_service_entries`, `set_connections_and_services`, `retain_connections`'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/app-state.md')
    assert '- **Connection グループ**: `connections`, `service_entries` → `connection_list_items`' in text, "expected to find: " + '- **Connection グループ**: `connections`, `service_entries` → `connection_list_items`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '| キーマッピング追加（Normalモード） | `app/keybindings/normal.rs` + `mod.rs` に predicate fn + `handler.rs` で配線 |' in text, "expected to find: " + '| キーマッピング追加（Normalモード） | `app/keybindings/normal.rs` + `mod.rs` に predicate fn + `handler.rs` で配線 |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '| キーマッピング追加（simpleモード） | `app/keybindings/` の該当サブモジュールにエントリ追加; `keymap::resolve()` が自動処理 |' in text, "expected to find: " + '| キーマッピング追加（simpleモード） | `app/keybindings/` の該当サブモジュールにエントリ追加; `keymap::resolve()` が自動処理 |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/architecture.md')
    assert '| DB固有SQL・方言ロジック追加 | `infra/adapters/{postgres,mysql}/`（`app/ports/` には絶対に置かない） |' in text, "expected to find: " + '| DB固有SQL・方言ロジック追加 | `infra/adapters/{postgres,mysql}/`（`app/ports/` には絶対に置かない） |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/config-migration.md')
    assert '- `connections.toml` スキーマの変更は既存の設定ファイルを壊してはならない' in text, "expected to find: " + '- `connections.toml` スキーマの変更は既存の設定ファイルを壊してはならない'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/config-migration.md')
    assert '- 新しいフィールドには適切なデフォルト値を設定し、古い設定がエラーなくロードできるようにする' in text, "expected to find: " + '- 新しいフィールドには適切なデフォルト値を設定し、古い設定がエラーなくロードできるようにする'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/config-migration.md')
    assert '- 破壊的なスキーマ変更がやむを得ない場合、設定に `version` フィールドを追加する' in text, "expected to find: " + '- 破壊的なスキーマ変更がやむを得ない場合、設定に `version` フィールドを追加する'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/db-agnostic.md')
    assert '各 adapter ディレクトリは `mod.rs`（オーケストレーション）+ CLI ディレクトリ（プロセス実行・パース）+ `sql/`（純粋SQL生成）の3層構造に従う。PG 固有の詳細は `postgres-adapter.md` を参照。' in text, "expected to find: " + '各 adapter ディレクトリは `mod.rs`（オーケストレーション）+ CLI ディレクトリ（プロセス実行・パース）+ `sql/`（純粋SQL生成）の3層構造に従う。PG 固有の詳細は `postgres-adapter.md` を参照。'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/db-agnostic.md')
    assert '**MySQL adapter を追加する場合**、PG adapter の構造をミラーすること: `mysql/mod.rs`, `mysql/mysql_cli/`, `mysql/sql/` 等。' in text, "expected to find: " + '**MySQL adapter を追加する場合**、PG adapter の構造をミラーすること: `mysql/mod.rs`, `mysql/mysql_cli/`, `mysql/sql/` 等。'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/db-agnostic.md')
    assert '- DB 固有の SQL、クォート、接続文字列ロジックはすべて `infra/adapters/{postgres,mysql}/` に配置すること' in text, "expected to find: " + '- DB 固有の SQL、クォート、接続文字列ロジックはすべて `infra/adapters/{postgres,mysql}/` に配置すること'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/interaction-contract.md')
    assert '- `app/keybindings/`: SSOT モジュール — `KeyBinding`（simple modes）と `ModeRow`（mixed modes）。サブモジュール: `normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`, `types.rs`。Mixed modes は `ModeBindings { rows' in text, "expected to find: " + '- `app/keybindings/`: SSOT モジュール — `KeyBinding`（simple modes）と `ModeRow`（mixed modes）。サブモジュール: `normal.rs`, `overlays.rs`, `connections.rs`, `editors.rs`, `types.rs`。Mixed modes は `ModeBindings { rows'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/interaction-contract.md')
    assert '**Char フォールバックルール**: フリーテキスト入力のあるモード（TablePicker, ErTablePicker, CommandLine, CellEdit）は `keymap::resolve()` を先に試し、その後 `Char(c)` にフォールスルーする。これらのモードにコマンドキーとして `KeyCombo::plain(Key::Char(x))` を追加してはならない' in text, "expected to find: " + '**Char フォールバックルール**: フリーテキスト入力のあるモード（TablePicker, ErTablePicker, CommandLine, CellEdit）は `keymap::resolve()` を先に試し、その後 `Char(c)` にフォールスルーする。これらのモードにコマンドキーとして `KeyCombo::plain(Key::Char(x))` を追加してはならない'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/interaction-contract.md')
    assert '- `app/keymap.rs`: `KeyBinding` スライス用の `resolve(combo, bindings)` と `ModeRow` スライス用の `resolve_mode(combo, rows)`' in text, "expected to find: " + '- `app/keymap.rs`: `KeyBinding` スライス用の `resolve(combo, bindings)` と `ModeRow` スライス用の `resolve_mode(combo, rows)`'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres-adapter.md')
    assert '`mod.rs` がオーケストレーション → `sql/` でSQL生成 → `psql/executor.rs` で psql 実行 → `psql/parser.rs` で出力パース' in text, "expected to find: " + '`mod.rs` がオーケストレーション → `sql/` でSQL生成 → `psql/executor.rs` で psql 実行 → `psql/parser.rs` で出力パース'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres-adapter.md')
    assert '`crate::infra::utils::{quote_ident, quote_literal}` を使うこと。`pg_quote_*` のような重複関数を作ってはならない。' in text, "expected to find: " + '`crate::infra::utils::{quote_ident, quote_literal}` を使うこと。`pg_quote_*` のような重複関数を作ってはならない。'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/postgres-adapter.md')
    assert '├── mod.rs              # PostgresAdapter構造体 + MetadataProvider / QueryExecutor impl' in text, "expected to find: " + '├── mod.rs              # PostgresAdapter構造体 + MetadataProvider / QueryExecutor impl'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rendering-strategy.md')
    assert '| 状態変更 | Reducer が `render_dirty = true` にセット → main loop が `Effect::Render` を追加 |' in text, "expected to find: " + '| 状態変更 | Reducer が `render_dirty = true` にセット → main loop が `Effect::Render` を追加 |'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rendering-strategy.md')
    assert '| アニメーション deadline | Spinner(150ms)、カーソル点滅(500ms)、メッセージタイムアウト、結果ハイライト |' in text, "expected to find: " + '| アニメーション deadline | Spinner(150ms)、カーソル点滅(500ms)、メッセージタイムアウト、結果ハイライト |'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rendering-strategy.md')
    assert '- `main.rs`: UI層が `tokio::select!` + `sleep_until(deadline)` を処理' in text, "expected to find: " + '- `main.rs`: UI層が `tokio::select!` + `sleep_until(deadline)` を処理'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rstest-patterns.md')
    assert 'fn classify_stderr_as_unknown_fallback(#[case] stderr: &str) { ... }' in text, "expected to find: " + 'fn classify_stderr_as_unknown_fallback(#[case] stderr: &str) { ... }'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rstest-patterns.md')
    assert 'fn scroll_keys(#[case] code: Key, #[case] expected: Action) { ... }' in text, "expected to find: " + 'fn scroll_keys(#[case] code: Key, #[case] expected: Action) { ... }'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rstest-patterns.md')
    assert '既存の `#[rstest]` 関数にケースを追加する前に、すべてのケースが同じ**振る舞いカテゴリ**に属しているか確認すること。' in text, "expected to find: " + '既存の `#[rstest]` 関数にケースを追加する前に、すべてのケースが同じ**振る舞いカテゴリ**に属しているか確認すること。'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rust-testing-style.md')
    assert '- ユニットテストは `#[cfg(test)] mod tests` でモジュール内に配置' in text, "expected to find: " + '- ユニットテストは `#[cfg(test)] mod tests` でモジュール内に配置'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rust-testing-style.md')
    assert '| 境界値 / パターン | `rstest` + `#[case]` |' in text, "expected to find: " + '| 境界値 / パターン | `rstest` + `#[case]` |'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/rust-testing-style.md')
    assert '| インテグレーション / E2E | `tests/` ディレクトリ |' in text, "expected to find: " + '| インテグレーション / E2E | `tests/` ディレクトリ |'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/test-organization.md')
    assert 'fn create_table(schema: &str, name: &str, columns: &[&str]) -> Table { ... }' in text, "expected to find: " + 'fn create_table(schema: &str, name: &str, columns: &[&str]) -> Table { ... }'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/test-organization.md')
    assert '- `mod` 名は振る舞いドメインを表す名詞にする（例: `connection_error`, `result_pane`）' in text, "expected to find: " + '- `mod` 名は振る舞いドメインを表す名詞にする（例: `connection_error`, `result_pane`）'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/test-organization.md')
    assert 'fn create_test_profile(name: &str) -> ConnectionProfile { ... }' in text, "expected to find: " + 'fn create_test_profile(name: &str) -> ConnectionProfile { ... }'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-obligations.md')
    assert '| **Infra (adapters)** | SQL 生成（方言固有） | PG 用 `build_update_sql`（MySQL 実装時はそちらも） |' in text, "expected to find: " + '| **Infra (adapters)** | SQL 生成（方言固有） | PG 用 `build_update_sql`（MySQL 実装時はそちらも） |'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-obligations.md')
    assert '| **App (ports)** | port trait のデフォルト実装メソッド | `DdlGenerator::ddl_line_count()` |' in text, "expected to find: " + '| **App (ports)** | port trait のデフォルト実装メソッド | `DdlGenerator::ddl_line_count()` |'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/testing-obligations.md')
    assert '| **Domain** | すべての public コンストラクタ / バリデーション | `ConnectionConfig::new()` の境界値 |' in text, "expected to find: " + '| **Domain** | すべての public コンストラクタ / バリデーション | `ConnectionConfig::new()` の境界値 |'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-design.md')
    assert '- カーソル描画は `text_cursor_spans()`（`ui/components/atoms/text_cursor.rs`）を使うこと。インラインでカーソル描画ロジックを複製してはならない' in text, "expected to find: " + '- カーソル描画は `text_cursor_spans()`（`ui/components/atoms/text_cursor.rs`）を使うこと。インラインでカーソル描画ロジックを複製してはならない'[:80]


def test_signal_34():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-design.md')
    assert '- 既知の例外: `ConnectionSetupState` は現在独自に `cursor_position` / `viewport_offset` を管理している（マイグレーションは別途追跡）' in text, "expected to find: " + '- 既知の例外: `ConnectionSetupState` は現在独自に `cursor_position` / `viewport_offset` を管理している（マイグレーションは別途追跡）'[:80]


def test_signal_35():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/ui-design.md')
    assert '| atoms | 単一目的のプリミティブ | `spinner_char()`, `key_chip()`, `panel_block()`, `text_cursor_spans()` |' in text, "expected to find: " + '| atoms | 単一目的のプリミティブ | `spinner_char()`, `key_chip()`, `panel_block()`, `text_cursor_spans()` |'[:80]


def test_signal_36():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/visual-regression.md')
    assert '- すべての `InputMode` バリアントに最低1つのスナップショットテストが必要（`testing-obligations.md` 参照）' in text, "expected to find: " + '- すべての `InputMode` バリアントに最低1つのスナップショットテストが必要（`testing-obligations.md` 参照）'[:80]


def test_signal_37():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/visual-regression.md')
    assert '│   └── fixtures.rs  # サンプルデータビルダー（metadata, table detail, query result）' in text, "expected to find: " + '│   └── fixtures.rs  # サンプルデータビルダー（metadata, table detail, query result）'[:80]


def test_signal_38():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/visual-regression.md')
    assert '│   ├── mod.rs       # テストユーティリティ（render_to_string, create_test_*）' in text, "expected to find: " + '│   ├── mod.rs       # テストユーティリティ（render_to_string, create_test_*）'[:80]


def test_signal_39():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| **visual-regression** | `tests/render_snapshots.rs`, `tests/snapshots/**` | instaスナップショット、モードカバレッジ |' in text, "expected to find: " + '| **visual-regression** | `tests/render_snapshots.rs`, `tests/snapshots/**` | instaスナップショット、モードカバレッジ |'[:80]


def test_signal_40():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| **interaction-contract** | keybindings, handler, footer, help, palette | SSOT整合性、キー変換フロー、チェックリスト |' in text, "expected to find: " + '| **interaction-contract** | keybindings, handler, footer, help, palette | SSOT整合性、キー変換フロー、チェックリスト |'[:80]


def test_signal_41():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert '| **rstest-patterns** | `domain/**`, `infra/**/parser*`, `infra/**/sql/**` | rstest凝集度、境界値パターン |' in text, "expected to find: " + '| **rstest-patterns** | `domain/**`, `infra/**/parser*`, `infra/**/sql/**` | rstest凝集度、境界値パターン |'[:80]

