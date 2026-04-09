#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied (check for useMemo import which is new)
if grep -q "useCallback, useMemo, useRef" apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx b/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx
index 44696999736f0..939e806f454ae 100644
--- a/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx
+++ b/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.tsx
@@ -1,5 +1,5 @@
 import { Copy, Expand } from 'lucide-react'
-import { useState } from 'react'
+import { useCallback, useMemo, useRef, useState } from 'react'
 import DataGrid, { CalculatedColumn } from 'react-data-grid'
 import {
   cn,
@@ -11,63 +11,32 @@ import {
 } from 'ui'

 import { CellDetailPanel } from './CellDetailPanel'
+import { formatCellValue, formatClipboardValue } from './Results.utils'
 import { handleCopyCell } from '@/components/grid/SupabaseGrid.utils'

-function formatClipboardValue(value: any) {
-  if (value === null) return ''
-  if (typeof value == 'object' || Array.isArray(value)) {
-    return JSON.stringify(value)
-  }
-  return value
-}
-
 const Results = ({ rows }: { rows: readonly any[] }) => {
   const [expandCell, setExpandCell] = useState(false)
   const [cellPosition, setCellPosition] = useState<{ column: any; row: any; rowIdx: number }>()
+  const contextMenuCellRef = useRef<{ column: string; value: any } | null>(null)
+  const triggerRef = useRef<HTMLDivElement>(null)

-  const formatter = (column: any, row: any) => {
-    const cellValue = row[column]
+  const handleContextMenu = useCallback((e: React.MouseEvent, column: string, value: any) => {
+    contextMenuCellRef.current = { column, value }

-    return (
-      <ContextMenu_Shadcn_ modal={false}>
-        <ContextMenuTrigger_Shadcn_ asChild>
-          <div
-            className={cn(
-              'flex items-center h-full font-mono text-xs w-full whitespace-pre',
-              cellValue === null && 'text-foreground-lighter'
-            )}
-          >
-            {cellValue === null
-              ? 'NULL'
-              : typeof cellValue === 'string'
-                ? cellValue
-                : JSON.stringify(cellValue)}
-          </div>
-        </ContextMenuTrigger_Shadcn_>
-        <ContextMenuContent_Shadcn_ onCloseAutoFocus={(e) => e.stopPropagation()}>
-          <ContextMenuItem_Shadcn_
-            className="gap-x-2"
-            onSelect={() => {
-              const value = formatClipboardValue(cellValue ?? '')
-              copyToClipboard(value)
-            }}
-            onFocusCapture={(e) => e.stopPropagation()}
-          >
-            <Copy size={12} />
-            Copy cell content
-          </ContextMenuItem_Shadcn_>
-          <ContextMenuItem_Shadcn_
-            className="gap-x-2"
-            onSelect={() => setExpandCell(true)}
-            onFocusCapture={(e) => e.stopPropagation()}
-          >
-            <Expand size={12} />
-            View cell content
-          </ContextMenuItem_Shadcn_>
-        </ContextMenuContent_Shadcn_>
-      </ContextMenu_Shadcn_>
-    )
-  }
+    if (triggerRef.current) {
+      // Position the hidden trigger at the mouse cursor so the context menu opens there
+      triggerRef.current.style.position = 'fixed'
+      triggerRef.current.style.left = `${e.clientX}px`
+      triggerRef.current.style.top = `${e.clientY}px`
+
+      const contextMenuEvent = new MouseEvent('contextmenu', {
+        bubbles: true,
+        clientX: e.clientX,
+        clientY: e.clientY,
+      })
+      triggerRef.current.dispatchEvent(contextMenuEvent)
+    }
+  }, [])

   const columnRender = (name: string) => {
     return <div className="flex h-full items-center justify-center font-mono text-xs">{name}</div>
@@ -77,34 +46,54 @@ const Results = ({ rows }: { rows: readonly any[] }) => {
   const MIN_COLUMN_WIDTH = 100
   const MAX_COLUMN_WIDTH = 500

-  const columns: CalculatedColumn<any>[] = Object.keys(rows?.[0] ?? []).map((key, idx) => {
-    const maxColumnValueLength = rows
-      .map((row) => String(row[key]).length)
-      .reduce((a, b) => Math.max(a, b), 0)
+  const columns: CalculatedColumn<any>[] = useMemo(
+    () =>
+      Object.keys(rows?.[0] ?? []).map((key, idx) => {
+        const maxColumnValueLength = rows
+          .map((row) => String(row[key]).length)
+          .reduce((a, b) => Math.max(a, b), 0)

-    const columnWidth = Math.max(
-      Math.min(maxColumnValueLength * EST_CHAR_WIDTH, MAX_COLUMN_WIDTH),
-      MIN_COLUMN_WIDTH
-    )
+        const columnWidth = Math.max(
+          Math.min(maxColumnValueLength * EST_CHAR_WIDTH, MAX_COLUMN_WIDTH),
+          MIN_COLUMN_WIDTH
+        )

-    return {
-      idx,
-      key,
-      name: key,
-      resizable: true,
-      parent: undefined,
-      level: 0,
-      width: columnWidth,
-      minWidth: MIN_COLUMN_WIDTH,
-      maxWidth: undefined,
-      draggable: false,
-      frozen: false,
-      sortable: false,
-      isLastFrozenColumn: false,
-      renderCell: ({ row }) => formatter(key, row),
-      renderHeaderCell: () => columnRender(key),
-    }
-  })
+        return {
+          idx,
+          key,
+          name: key,
+          resizable: true,
+          parent: undefined,
+          level: 0,
+          width: columnWidth,
+          minWidth: MIN_COLUMN_WIDTH,
+          maxWidth: undefined,
+          draggable: false,
+          frozen: false,
+          sortable: false,
+          isLastFrozenColumn: false,
+          renderCell: ({ row }: { row: any }) => {
+            const cellValue = row[key]
+            return (
+              <div
+                className={cn(
+                  'flex items-center h-full font-mono text-xs w-full whitespace-pre',
+                  cellValue === null && 'text-foreground-lighter'
+                )}
+                onContextMenu={(e) => {
+                  e.preventDefault()
+                  handleContextMenu(e, key, cellValue)
+                }}
+              >
+                {formatCellValue(cellValue)}
+              </div>
+            )
+          },
+          renderHeaderCell: () => columnRender(key),
+        }
+      }),
+    [rows, handleContextMenu]
+  )

   return (
     <>
@@ -116,10 +105,36 @@ const Results = ({ rows }: { rows: readonly any[] }) => {
         </div>
       ) : (
         <>
+          <ContextMenu_Shadcn_ modal={false}>
+            <ContextMenuTrigger_Shadcn_ asChild>
+              <div ref={triggerRef} className="fixed pointer-events-none w-0 h-0" />
+            </ContextMenuTrigger_Shadcn_>
+            <ContextMenuContent_Shadcn_ onCloseAutoFocus={(e) => e.stopPropagation()}>
+              <ContextMenuItem_Shadcn_
+                className="gap-x-2"
+                onSelect={() => {
+                  const value = formatClipboardValue(contextMenuCellRef.current?.value ?? '')
+                  copyToClipboard(value)
+                }}
+                onFocusCapture={(e) => e.stopPropagation()}
+              >
+                <Copy size={12} />
+                Copy cell content
+              </ContextMenuItem_Shadcn_>
+              <ContextMenuItem_Shadcn_
+                className="gap-x-2"
+                onSelect={() => setExpandCell(true)}
+                onFocusCapture={(e) => e.stopPropagation()}
+              >
+                <Expand size={12} />
+                View cell content
+              </ContextMenuItem_Shadcn_>
+            </ContextMenuContent_Shadcn_>
+          </ContextMenu_Shadcn_>
           <DataGrid
             columns={columns}
             rows={rows}
-            className="h-full flex-grow border-t-0"
+            className="flex-grow min-h-0 border-t-0"
             rowClass={() => '[&>.rdg-cell]:items-center'}
             onSelectedCellChange={setCellPosition}
             onCellKeyDown={handleCopyCell}

diff --git a/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts b/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts
index 3791f6c9c614c..43a2542b0e1ee 100644
--- a/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts
+++ b/apps/studio/components/interfaces/SQLEditor/UtilityPanel/Results.utils.ts
@@ -3,6 +3,20 @@ import Papa from 'papaparse'

 type ResultRow = Record<string, unknown>

+export function formatClipboardValue(value: unknown) {
+  if (value === null) return ''
+  if (typeof value == 'object' || Array.isArray(value)) {
+    return JSON.stringify(value)
+  }
+  return String(value)
+}
+
+export function formatCellValue(value: unknown) {
+  if (value === null) return 'NULL'
+  if (typeof value === 'string') return value
+  return JSON.stringify(value)
+}
+
 export function formatResults(
   results: ResultRow[]
 ): Record<string, string | number | boolean | null | undefined>[] {
diff --git a/apps/studio/components/ui/QueryBlock/QueryBlock.tsx b/apps/studio/components/ui/QueryBlock/QueryBlock.tsx
index 72c5d52ecbf5a..f1f9fa09ae266 100644
--- a/apps/studio/components/ui/QueryBlock/QueryBlock.tsx
+++ b/apps/studio/components/ui/QueryBlock/QueryBlock.tsx
@@ -342,7 +342,7 @@ export const QueryBlock = ({
             </div>
           ) : (
             results && (
-              <div className={cn('flex-1 w-full overflow-auto relative max-h-64')}>
+              <div className={cn('flex flex-col flex-1 w-full relative max-h-64')}>
                 <Results rows={results} />
               </div>
             )

diff --git a/apps/studio/tests/components/SQLEditor/Results.test.tsx b/apps/studio/tests/components/SQLEditor/Results.test.tsx
new file mode 100644
index 0000000000000..d6a92bb34fd9c
--- /dev/null
+++ b/apps/studio/tests/components/SQLEditor/Results.test.tsx
@@ -0,0 +1,60 @@
+import { screen } from '@testing-library/react'
+import Results from 'components/interfaces/SQLEditor/UtilityPanel/Results'
+import { customRender as render } from 'tests/lib/custom-render'
+import { expect, test, vi } from 'vitest'
+
+let contextMenuMountCount = 0
+
+vi.mock('ui', async () => {
+  const actual = await vi.importActual<typeof import('ui')>('ui')
+  return {
+    ...actual,
+    ContextMenu_Shadcn_: (props: any) => {
+      contextMenuMountCount++
+      return <actual.ContextMenu_Shadcn_ {...props} />
+    },
+  }
+})
+
+vi.mock('react-data-grid', () => ({
+  default: ({ columns, rows }: any) => (
+    <div role="table">
+      <div role="row">
+        {columns.map((col: any, colIdx: number) => (
+          <div key={colIdx} role="columnheader">
+            {col.renderHeaderCell ? col.renderHeaderCell({}) : col.name}
+          </div>
+        ))}
+      </div>
+      {rows.map((row: any, rowIdx: number) => (
+        <div key={rowIdx} role="row">
+          {columns.map((col: any, colIdx: number) => (
+            <div key={colIdx} role="cell">
+              {col.renderCell?.({ row, rowIdx, isCellSelected: false })}
+            </div>
+          ))}
+        </div>
+      ))}
+    </div>
+  ),
+}))
+
+function generateRows(count: number) {
+  return Array.from({ length: count }, (_, i) => ({
+    id: i,
+    name: `row-${i}`,
+  }))
+}
+
+test('renders a single context menu regardless of row count', () => {
+  contextMenuMountCount = 0
+  const rows = generateRows(100)
+  render(<Results rows={rows} />)
+
+  expect(contextMenuMountCount).toBe(1)
+})
+
+test('shows empty state when no rows provided', () => {
+  render(<Results rows={[]} />)
+  expect(screen.getByText('Success. No rows returned')).toBeTruthy()
+})
diff --git a/apps/studio/tests/components/SQLEditor/Results.utils.test.ts b/apps/studio/tests/components/SQLEditor/Results.utils.test.ts
new file mode 100644
index 0000000000000..39622a61959a4
--- /dev/null
+++ b/apps/studio/tests/components/SQLEditor/Results.utils.test.ts
@@ -0,0 +1,47 @@
+import {
+  formatCellValue,
+  formatClipboardValue,
+} from 'components/interfaces/SQLEditor/UtilityPanel/Results.utils'
+import { describe, expect, test } from 'vitest'
+
+describe('formatClipboardValue', () => {
+  test('returns empty string for null', () => {
+    expect(formatClipboardValue(null)).toBe('')
+  })
+
+  test('stringifies objects', () => {
+    expect(formatClipboardValue({ a: 1 })).toBe('{"a":1}')
+  })
+
+  test('stringifies arrays', () => {
+    expect(formatClipboardValue([1, 2])).toBe('[1,2]')
+  })
+
+  test('converts primitives to string', () => {
+    expect(formatClipboardValue('hello')).toBe('hello')
+    expect(formatClipboardValue(42)).toBe('42')
+    expect(formatClipboardValue(false)).toBe('false')
+  })
+})
+
+describe('formatCellValue', () => {
+  test('returns NULL for null', () => {
+    expect(formatCellValue(null)).toBe('NULL')
+  })
+
+  test('returns strings as-is', () => {
+    expect(formatCellValue('hello')).toBe('hello')
+  })
+
+  test('stringifies objects', () => {
+    expect(formatCellValue({ a: 1 })).toBe('{"a":1}')
+  })
+
+  test('stringifies numbers', () => {
+    expect(formatCellValue(42)).toBe('42')
+  })
+
+  test('stringifies booleans', () => {
+    expect(formatCellValue(true)).toBe('true')
+  })
+})

PATCH

echo "Patch applied successfully."
