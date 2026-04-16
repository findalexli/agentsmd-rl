#!/bin/bash
set -e
cd /workspace/prisma

python3 << 'PYTHON_SCRIPT'
import re

# Patch pg.ts
with open('packages/adapter-pg/src/pg.ts', 'r') as f:
    content = f.read()

# Add name: this.pgOptions?.statementNameGenerator?.(query), after the { in client.query call
old_pattern = r"(const result = await this\.client\.query\(\n        \{\n)(          text:)"
new_pattern = r"\1          name: this.pgOptions?.statementNameGenerator?.(query),\n\2"
content = re.sub(old_pattern, new_pattern, content)

# Add doc comments and statementNameGenerator to PrismaPgOptions
old_options = r"""export type PrismaPgOptions = \{
  schema\?: string
  disposeExternalPool\?: boolean
  onPoolError\?: \(err: Error\) => void
  onConnectionError\?: \(err: Error\) => void
  userDefinedTypeParser\?: UserDefinedTypeParser
\}"""

new_options = """export type PrismaPgOptions = {
  /** The name of the schema to use in generated queries */
  schema?: string
  /**
   * Whether to call `pool.end()` on an externally provided pool when the adapter is disposed.
   * Defaults to `false`.
   */
  disposeExternalPool?: boolean
  /** Callback attached to the pool's 'error' events. */
  onPoolError?: (err: Error) => void
  /** Callback attached to connection's 'error' events. */
  onConnectionError?: (err: Error) => void
  /**
   * Optional parser for user-defined types. Called with the type's OID, the value to parse, and
   * a queryable for performing additional queries if necessary.
   */
  userDefinedTypeParser?: UserDefinedTypeParser
  /**
   * Optional function to generate names for prepared statements. The generated strings are passed
   * as the `name` property in the query to `pg.Client#query()`, which uses them to cache the
   * underlying statements. If not provided, prepared statements are not cached.
   */
  statementNameGenerator?: StatementNameGenerator
}"""

content = re.sub(old_options, new_options, content)

# Add StatementNameGenerator type after UserDefinedTypeParser
old_type = r"(export type UserDefinedTypeParser = \(oid: number, value: unknown, adapter: SqlQueryable\) => Promise<unknown>\n)"
new_type = r"\1\nexport type StatementNameGenerator = (query: SqlQuery) => string\n"
content = re.sub(old_type, new_type, content)

with open('packages/adapter-pg/src/pg.ts', 'w') as f:
    f.write(content)

print("pg.ts patched successfully")

# Patch pg.test.ts
with open('packages/adapter-pg/src/__tests__/pg.test.ts', 'r') as f:
    test_content = f.read()

# Add SqlQuery import after the first import line
old_import = "import { getLogs } from '@prisma/debug'\nimport pg, { DatabaseError } from 'pg'"
new_import = "import { getLogs } from '@prisma/debug'\nimport type { SqlQuery } from '@prisma/driver-adapter-utils'\nimport pg, { DatabaseError } from 'pg'"
test_content = test_content.replace(old_import, new_import)

# Add new tests at the end of the file (before the closing of the describe block)
old_ending = """    await adapter.dispose()
  })
})"""

new_ending = """    await adapter.dispose()
  })

  it('should pass generated name when statement name generator is provided', async () => {
    const mockGenerator = vi.fn(() => 'test-name')
    const factory = new PrismaPgAdapterFactory('postgresql://test:test@localhost/test', {
      statementNameGenerator: mockGenerator,
    })
    const adapter = await factory.connect()

    const mockQuery = vi.fn().mockResolvedValue({
      rows: [],
      fields: [],
      rowCount: 0,
    })
    adapter['client'].query = mockQuery

    const query: SqlQuery = { sql: 'SELECT 1', args: [], argTypes: [] }
    await adapter.queryRaw(query)

    expect(mockGenerator).toHaveBeenCalledWith(query)
    expect(mockQuery).toHaveBeenCalledWith(expect.objectContaining({ name: 'test-name' }), [])

    await adapter.dispose()
  })

  it('should not pass name when statement name generator is not provided', async () => {
    const factory = new PrismaPgAdapterFactory('postgresql://test:test@localhost/test')
    const adapter = await factory.connect()

    const mockQuery = vi.fn().mockResolvedValue({
      rows: [],
      fields: [],
      rowCount: 0,
    })
    adapter['client'].query = mockQuery

    const query: SqlQuery = { sql: 'SELECT 1', args: [], argTypes: [] }
    await adapter.queryRaw(query)

    expect(mockQuery).toHaveBeenCalledWith(expect.objectContaining({ name: undefined }), [])

    await adapter.dispose()
  })
})"""

test_content = test_content.replace(old_ending, new_ending)

with open('packages/adapter-pg/src/__tests__/pg.test.ts', 'w') as f:
    f.write(test_content)

print("pg.test.ts patched successfully")
PYTHON_SCRIPT

# Verify the patch was applied
grep -q "statementNameGenerator" packages/adapter-pg/src/pg.ts && echo "Verification passed: statementNameGenerator found in pg.ts"
grep -q "StatementNameGenerator = (query: SqlQuery) => string" packages/adapter-pg/src/pg.ts && echo "Verification passed: StatementNameGenerator type found"
grep -q "SqlQuery" packages/adapter-pg/src/__tests__/pg.test.ts && echo "Verification passed: SqlQuery import found in test file"
