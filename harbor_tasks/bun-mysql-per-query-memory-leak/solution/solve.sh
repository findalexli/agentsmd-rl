#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency: check if fix is already applied
if grep -q 'this\.name_or_index\.deinit()' src/sql/mysql/protocol/ColumnDefinition41.zig; then
    echo "Fix already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/sql/mysql/MySQLConnection.zig b/src/sql/mysql/MySQLConnection.zig
index 217efe0e3b9..524214571c7 100644
--- a/src/sql/mysql/MySQLConnection.zig
+++ b/src/sql/mysql/MySQLConnection.zig
@@ -924,6 +924,7 @@ pub fn handlePreparedStatement(this: *MySQLConnection, comptime Context: type, r
             // Read column definitions if any
             if (ok.num_columns > 0) {
                 statement.columns = try bun.default_allocator.alloc(ColumnDefinition41, ok.num_columns);
+                for (statement.columns) |*col| col.* = .{};
                 statement.columns_received = 0;
             }

@@ -1055,6 +1056,7 @@ fn handleResultSet(this: *MySQLConnection, comptime Context: type, reader: NewRe
                         bun.default_allocator.free(statement.columns);
                     }
                     statement.columns = try bun.default_allocator.alloc(ColumnDefinition41, header.field_count);
+                    for (statement.columns) |*col| col.* = .{};
                     statement.columns_received = 0;
                 }
                 statement.execution_flags.needs_duplicate_check = true;
diff --git a/src/sql/mysql/MySQLStatement.zig b/src/sql/mysql/MySQLStatement.zig
index 53b6b6e11be..a4d1617cf1b 100644
--- a/src/sql/mysql/MySQLStatement.zig
+++ b/src/sql/mysql/MySQLStatement.zig
@@ -83,6 +83,7 @@ pub fn checkForDuplicateFields(this: *@This()) void {
             .name => |*name| {
                 const seen = seen_fields.getOrPut(name.slice()) catch unreachable;
                 if (seen.found_existing) {
+                    field.name_or_index.deinit();
                     field.name_or_index = .duplicate;
                     flags.has_duplicate_columns = true;
                 }
diff --git a/src/sql/mysql/protocol/ColumnDefinition41.zig b/src/sql/mysql/protocol/ColumnDefinition41.zig
index 6dae10d7d99..7394976c0df 100644
--- a/src/sql/mysql/protocol/ColumnDefinition41.zig
+++ b/src/sql/mysql/protocol/ColumnDefinition41.zig
@@ -48,6 +48,7 @@ pub fn deinit(this: *ColumnDefinition41) void {
     this.org_table.deinit();
     this.name.deinit();
     this.org_name.deinit();
+    this.name_or_index.deinit();
 }

 pub fn decodeInternal(this: *ColumnDefinition41, comptime Context: type, reader: NewReader(Context)) !void {
@@ -77,6 +78,7 @@ pub fn decodeInternal(this: *ColumnDefinition41, comptime Context: type, reader:
     this.flags = ColumnFlags.fromInt(try reader.int(u16));
     this.decimals = try reader.int(u8);

+    this.name_or_index.deinit();
     this.name_or_index = try ColumnIdentifier.init(this.name);

     // https://mariadb.com/kb/en/result-set-packets/#column-definition-packet
diff --git a/src/sql/mysql/protocol/PreparedStatement.zig b/src/sql/mysql/protocol/PreparedStatement.zig
index 0ca0810f61c..90ca3944abd 100644
--- a/src/sql/mysql/protocol/PreparedStatement.zig
+++ b/src/sql/mysql/protocol/PreparedStatement.zig
@@ -41,6 +41,9 @@ pub const Execute = struct {
         for (this.params) |*param| {
             param.deinit(bun.default_allocator);
         }
+        if (this.params.len > 0) {
+            bun.default_allocator.free(this.params);
+        }
     }

     fn writeNullBitmap(this: *const Execute, comptime Context: type, writer: NewWriter(Context)) AnyMySQLError.Error!void {

PATCH

echo "Fix applied successfully."
