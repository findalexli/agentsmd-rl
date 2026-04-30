#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'numericTickPrefix' frontend/src/lib/charts/utils/dates.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/frontend/src/lib/charts/utils/dates.test.ts b/frontend/src/lib/charts/utils/dates.test.ts
index c969438aba5c..3b96058c5162 100644
--- a/frontend/src/lib/charts/utils/dates.test.ts
+++ b/frontend/src/lib/charts/utils/dates.test.ts
@@ -274,7 +274,7 @@ describe('createXAxisTickCallback', () => {
             expect(callback('some-label', 5)).toBe('some-label')
         })

-        it('returns raw value when days are numbers (stickiness insights)', () => {
+        it('returns raw value when days are numbers and no prefix is provided', () => {
             const callback = createXAxisTickCallback({
                 interval: 'day',
                 allDays: [1, 2, 3, 4, 5],
@@ -284,6 +284,17 @@ describe('createXAxisTickCallback', () => {
             expect(callback(3, 2)).toBe('3')
         })

+        it('formats numbers with a prefix when provided', () => {
+            const callback = createXAxisTickCallback({
+                interval: 'day',
+                allDays: [1, 2, 3, 4, 5],
+                timezone: 'UTC',
+                numericTickPrefix: 'Day',
+            })
+            expect(callback(1, 0)).toBe('Day 1')
+            expect(callback(3, 2)).toBe('Day 3')
+        })
+
         it('returns raw value for unparseable dates', () => {
             const callback = createXAxisTickCallback({
                 interval: 'day',
diff --git a/frontend/src/lib/charts/utils/dates.ts b/frontend/src/lib/charts/utils/dates.ts
index 64da2329c340..4471e457ae42 100644
--- a/frontend/src/lib/charts/utils/dates.ts
+++ b/frontend/src/lib/charts/utils/dates.ts
@@ -6,6 +6,7 @@ interface CreateXAxisTickCallbackArgs {
     interval?: IntervalType
     allDays: (string | number)[]
     timezone: string
+    numericTickPrefix?: string
 }

 type TickMode =
@@ -19,9 +20,10 @@ export function createXAxisTickCallback({
     interval,
     allDays,
     timezone,
+    numericTickPrefix,
 }: CreateXAxisTickCallbackArgs): (value: string | number, index: number) => string | null {
     if (allDays.length === 0 || typeof allDays[0] !== 'string') {
-        return (value) => String(value)
+        return (value) => (numericTickPrefix ? `${numericTickPrefix} ${String(value)}` : String(value))
     }

     const parsedDates = allDays.map((d) => parseDateForAxis(String(d), timezone))
diff --git a/frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx b/frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx
index e52b58f9d373..c9fe4620c76b 100644
--- a/frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx
+++ b/frontend/src/scenes/insights/views/LineGraph/LineGraph.tsx
@@ -337,7 +337,7 @@ export function LineGraph_({
     const { baseCurrency } = useValues(teamLogic)

     const { insightProps, insight } = useValues(insightLogic)
-    const { timezone, isTrends, isFunnels, breakdownFilter, interval, insightData } = useValues(
+    const { timezone, isTrends, isStickiness, isFunnels, breakdownFilter, interval, insightData } = useValues(
         insightVizDataLogic(insightProps)
     )
     const { theme, getTrendsColor, getTrendsHidden, hoveredDatasetIndex, currentPeriodResult } = useValues(
@@ -685,6 +685,9 @@ export function LineGraph_({
                 interval: interval ?? 'day',
                 allDays: currentPeriodResult?.days ?? [],
                 timezone,
+                numericTickPrefix: isStickiness
+                    ? `${(interval ?? 'day').slice(0, 1).toUpperCase()}${(interval ?? 'day').slice(1)}`
+                    : undefined,
             })

             const gridOptions: Partial<GridLineOptions> = {

PATCH

echo "Patch applied successfully."
