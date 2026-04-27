#!/usr/bin/env bash
set -euo pipefail

cd /workspace/obsidian-skills

# Idempotency guard
if grep -qF "**IMPORTANT:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` direc" "skills/obsidian-bases/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/obsidian-bases/SKILL.md b/skills/obsidian-bases/SKILL.md
@@ -154,18 +154,21 @@ Formulas compute values from properties. Defined in the `formulas` section.
 formulas:
   # Simple arithmetic
   total: "price * quantity"
-  
+
   # Conditional logic
   status_icon: 'if(done, "✅", "⏳")'
-  
+
   # String formatting
   formatted_price: 'if(price, price.toFixed(2) + " dollars")'
-  
+
   # Date formatting
   created: 'file.ctime.format("YYYY-MM-DD")'
-  
-  # Complex expressions
-  days_old: '((now() - file.ctime) / 86400000).round(0)'
+
+  # Calculate days since created (use .days for Duration)
+  days_old: '(now() - file.ctime).days'
+
+  # Calculate days until due date
+  days_until_due: 'if(due_date, (date(due_date) - today()).days, "")'
 ```
 
 ## Functions Reference
@@ -210,10 +213,38 @@ formulas:
 | `relative()` | `date.relative(): string` | Human-readable relative time |
 | `isEmpty()` | `date.isEmpty(): boolean` | Always false for dates |
 
+### Duration Type
+
+When subtracting two dates, the result is a **Duration** type (not a number). Duration has its own properties and methods.
+
+**Duration Fields:**
+| Field | Type | Description |
+|-------|------|-------------|
+| `duration.days` | Number | Total days in duration |
+| `duration.hours` | Number | Total hours in duration |
+| `duration.minutes` | Number | Total minutes in duration |
+| `duration.seconds` | Number | Total seconds in duration |
+| `duration.milliseconds` | Number | Total milliseconds in duration |
+
+**IMPORTANT:** Duration does NOT support `.round()`, `.floor()`, `.ceil()` directly. You must access a numeric field first (like `.days`), then apply number functions.
+
+```yaml
+# CORRECT: Calculate days between dates
+"(date(due_date) - today()).days"                    # Returns number of days
+"(now() - file.ctime).days"                          # Days since created
+
+# CORRECT: Round the numeric result if needed
+"(date(due_date) - today()).days.round(0)"           # Rounded days
+"(now() - file.ctime).hours.round(0)"                # Rounded hours
+
+# WRONG - will cause error:
+# "((date(due) - today()) / 86400000).round(0)"      # Duration doesn't support division then round
+```
+
 ### Date Arithmetic
 
 ```yaml
-# Duration units: y/year/years, M/month/months, d/day/days, 
+# Duration units: y/year/years, M/month/months, d/day/days,
 #                 w/week/weeks, h/hour/hours, m/minute/minutes, s/second/seconds
 
 # Add/subtract durations
@@ -222,8 +253,10 @@ formulas:
 "now() + \"1 day\""       # Tomorrow
 "today() + \"7d\""        # A week from today
 
-# Subtract dates for millisecond difference
-"now() - file.ctime"
+# Subtract dates returns Duration type
+"now() - file.ctime"                    # Returns Duration
+"(now() - file.ctime).days"             # Get days as number
+"(now() - file.ctime).hours"            # Get hours as number
 
 # Complex duration arithmetic
 "now() + (duration('1d') * 2)"
@@ -394,7 +427,7 @@ filters:
     - 'file.ext == "md"'
 
 formulas:
-  days_until_due: 'if(due, ((date(due) - today()) / 86400000).round(0), "")'
+  days_until_due: 'if(due, (date(due) - today()).days, "")'
   is_overdue: 'if(due, date(due) < today() && status != "done", false)'
   priority_label: 'if(priority == 1, "🔴 High", if(priority == 2, "🟡 Medium", "🟢 Low"))'
 
@@ -490,7 +523,7 @@ filters:
 formulas:
   last_updated: 'file.mtime.relative()'
   link_count: 'file.links.length'
-  
+
 summaries:
   avgLinks: 'values.filter(value.isType("number")).mean().round(1)'
 
PATCH

echo "Gold patch applied."
