#!/usr/bin/env bash
set -euo pipefail

cd /workspace/bun

# Idempotent: skip if already applied
if grep -q 'buildDefinedColumnsAndQuery' src/js/internal/sql/shared.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying changes using Node.js..."

node << 'NODEOF'
const fs = require('fs');
const path = require('path');

const SHARED_TS = 'src/js/internal/sql/shared.ts';
const SQLITE_TS = 'src/js/internal/sql/sqlite.ts';
const MYSQL_TS = 'src/js/internal/sql/mysql.ts';
const POSTGRES_TS = 'src/js/internal/sql/postgres.ts';
const CLAUDE_MD = 'test/CLAUDE.md';

// Read files
let shared = fs.readFileSync(SHARED_TS, 'utf8');
let sqlite = fs.readFileSync(SQLITE_TS, 'utf8');
let mysql = fs.readFileSync(MYSQL_TS, 'utf8');
let postgres = fs.readFileSync(POSTGRES_TS, 'utf8');
let claude = fs.readFileSync(CLAUDE_MD, 'utf8');

// 1. Add buildDefinedColumnsAndQuery function to shared.ts after SQLHelper class
const buildFunc = `
/**
 * Build the column list for INSERT statements while determining which columns have defined values.
 * This combines column name generation with defined column detection in a single pass.
 * Returns the defined columns array and the SQL fragment for the column names.
 */
function buildDefinedColumnsAndQuery<T>(
  columns: (keyof T)[],
  items: T | T[],
  escapeIdentifier: (name: string) => string,
): { definedColumns: (keyof T)[]; columnsSql: string } {
  const definedColumns: (keyof T)[] = [];
  let columnsSql = "(";
  const columnCount = columns.length;

  for (let k = 0; k < columnCount; k++) {
    const column = columns[k];

    // Check if any item has this column defined
    let hasDefinedValue = false;
    if ($isArray(items)) {
      for (let j = 0; j < items.length; j++) {
        if (typeof items[j][column] !== "undefined") {
          hasDefinedValue = true;
          break;
        }
      }
    } else {
      hasDefinedValue = typeof items[column] !== "undefined";
    }

    if (hasDefinedValue) {
      if (definedColumns.length > 0) columnsSql += ", ";
      columnsSql += escapeIdentifier(column as string);
      definedColumns.push(column);
    }
  }

  columnsSql += ") VALUES";
  return { definedColumns, columnsSql };
}
`;

shared = shared.replace(
  /}\s*\n\s*const SQLITE_MEMORY = ":memory:";/,
  `}${buildFunc}\nconst SQLITE_MEMORY = ":memory:";`
);

// 2. Add export for buildDefinedColumnsAndQuery
shared = shared.replace(
  /export default \{\s*\n\s*parseDefinitelySqliteUrl,\s*\n\s*isOptionsOfAdapter,\s*\n\s*assertIsOptionsOfAdapter,/,
  `export default {
  parseDefinitelySqliteUrl,
  isOptionsOfAdapter,
  assertIsOptionsOfAdapter,
  buildDefinedColumnsAndQuery,`
);

// 3. Update sqlite.ts require statement
sqlite = sqlite.replace(
  /const { SQLHelper, SQLResultArray } = require\("internal\/sql\/shared"\);/,
  'const { SQLHelper, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");'
);

// 4. Update mysql.ts require statement
mysql = mysql.replace(
  /const { SQLHelper, SSLMode, SQLResultArray } = require\("internal\/sql\/shared"\);/,
  'const { SQLHelper, SSLMode, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");'
);

// 5. Update postgres.ts require statement
postgres = postgres.replace(
  /const { SQLHelper, SSLMode, SQLResultArray, SQLArrayParameter } = require\("internal\/sql\/shared"\);/,
  `const {
  SQLHelper,
  SSLMode,
  SQLResultArray,
  SQLArrayParameter,
  buildDefinedColumnsAndQuery,
} = require("internal/sql/shared");`
);

// 6. Update CLAUDE.md - Promise.withResolvers type
claude = claude.replace(
  /const { promise, resolve, reject } = Promise\.withResolvers\(\);/,
  'const { promise, resolve, reject } = Promise.withResolvers<void>(); // Can specify any type here for resolution value'
);

// 7. Add toEqual guidance to CLAUDE.md
const toEqualSection = `### Nested/complex object equality

Prefer usage of \`.toEqual\` rather than many \`.toBe\` assertions for nested or complex objects.

<example>

BAD (try to avoid doing this):

\`\`\`ts
expect(result).toHaveLength(3);
expect(result[0].optional).toBe(null);
expect(result[1].optional).toBe("middle-value"); // CRITICAL: middle item's value must be preserved
expect(result[2].optional).toBe(null);
\`\`\`

**GOOD (always prefer this):**

\`\`\`ts
expect(result).toEqual([
  { optional: null },
  { optional: "middle-value" }, // CRITICAL: middle item's value must be preserved
  { optional: null },
]);
\`\`\`

</example>

`;

claude = claude.replace(
  /### Common Imports from \`harness\`/,
  toEqualSection + '### Common Imports from `harness`'
);

// Write files back
fs.writeFileSync(SHARED_TS, shared);
fs.writeFileSync(SQLITE_TS, sqlite);
fs.writeFileSync(MYSQL_TS, mysql);
fs.writeFileSync(POSTGRES_TS, postgres);
fs.writeFileSync(CLAUDE_MD, claude);

console.log("Node.js modifications complete.");
NODEOF

echo "Changes applied successfully."
