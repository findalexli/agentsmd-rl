const fs = require('fs');

const REPO = '/workspace/bun';

// Read files
let shared = fs.readFileSync(`${REPO}/src/js/internal/sql/shared.ts`, 'utf8');
let mysql = fs.readFileSync(`${REPO}/src/js/internal/sql/mysql.ts`, 'utf8');
let postgres = fs.readFileSync(`${REPO}/src/js/internal/sql/postgres.ts`, 'utf8');
let sqlite = fs.readFileSync(`${REPO}/src/js/internal/sql/sqlite.ts`, 'utf8');
let claudeMd = fs.readFileSync(`${REPO}/test/CLAUDE.md`, 'utf8');

// Check if already applied
if (shared.includes('function buildDefinedColumnsAndQuery')) {
    console.log('Fix already applied.');
    process.exit(0);
}

console.log('Applying fix...');

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

// Insert after line 177 (after SQLHelper class closing brace)
const sharedLines = shared.split('\n');
const insertIndex = sharedLines.findIndex((line, i) => i >= 176 && line.trim() === '}' && sharedLines[i+1]?.trim() === '');
if (insertIndex !== -1) {
    sharedLines.splice(insertIndex + 1, 0, buildFunc);
    shared = sharedLines.join('\n');
}

// 2. Export buildDefinedColumnsAndQuery in shared.ts
shared = shared.replace(
    'assertIsOptionsOfAdapter,\n  parseOptions,',
    'assertIsOptionsOfAdapter,\n  buildDefinedColumnsAndQuery,\n  parseOptions,'
);

// 3. Update mysql.ts require statement
mysql = mysql.replace(
    'const { SQLHelper, SSLMode, SQLResultArray } = require("internal/sql/shared");',
    'const { SQLHelper, SSLMode, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");'
);

// 4. Update postgres.ts require statement
postgres = postgres.replace(
    'const { SQLHelper, SSLMode, SQLResultArray, SQLArrayParameter } = require("internal/sql/shared");',
    'const { SQLHelper, SSLMode, SQLResultArray, SQLArrayParameter, buildDefinedColumnsAndQuery } = require("internal/sql/shared");'
);

// 5. Update sqlite.ts require statement
sqlite = sqlite.replace(
    'const { SQLHelper, SQLResultArray } = require("internal/sql/shared");',
    'const { SQLHelper, SQLResultArray, buildDefinedColumnsAndQuery } = require("internal/sql/shared");'
);

// 6. Add toEqual guidance to CLAUDE.md
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

claudeMd = claudeMd.replace(
    '### Common Imports from `harness`',
    toEqualSection + '### Common Imports from `harness`'
);

// 7. Update Promise.withResolvers line
claudeMd = claudeMd.replace(
    'const { promise, resolve, reject } = Promise.withResolvers();',
    'const { promise, resolve, reject } = Promise.withResolvers<void>(); // Can specify any type here for resolution value'
);

// Write files back
fs.writeFileSync(`${REPO}/src/js/internal/sql/shared.ts`, shared);
fs.writeFileSync(`${REPO}/src/js/internal/sql/mysql.ts`, mysql);
fs.writeFileSync(`${REPO}/src/js/internal/sql/postgres.ts`, postgres);
fs.writeFileSync(`${REPO}/src/js/internal/sql/sqlite.ts`, sqlite);
fs.writeFileSync(`${REPO}/test/CLAUDE.md`, claudeMd);

console.log('Fix applied successfully.');
