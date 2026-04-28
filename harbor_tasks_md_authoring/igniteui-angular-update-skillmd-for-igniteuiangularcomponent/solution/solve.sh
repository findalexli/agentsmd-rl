#!/usr/bin/env bash
set -euo pipefail

cd /workspace/igniteui-angular

# Idempotency guard
if grep -qF "skills/igniteui-angular-components/SKILL.md" "skills/igniteui-angular-components/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/igniteui-angular-components/SKILL.md b/skills/igniteui-angular-components/SKILL.md
@@ -1,4 +1,3 @@
-```skill
 ---
 name: igniteui-angular-components
 description: "All Ignite UI Angular UI components: application setup and architecture, form controls (Input Group, Combo, Select, Date/Time Pickers, Calendar, Checkbox, Radio, Switch, Slider, reactive forms), layout (Tabs, Bottom Navigation, Stepper, Accordion, Splitter, Navigation Drawer, Layout Manager directives), data display (List, Tree, Card, Chips, Avatar, Badge, Icon, Carousel, Paginator, Progress, Chat), feedback/overlays (Dialog, Snackbar, Toast, Banner), directives (Button, Ripple, Tooltip, Drag and Drop), Dock Manager, and Charts (Area Chart, Bar Chart, Column Chart, Stock/Financial Chart, Pie Chart, IgxCategoryChart, IgxFinancialChart, IgxDataChart, IgxPieChart). Use for any non-grid Ignite UI Angular UI question."
@@ -69,4 +68,3 @@ Both packages share **identical entry-point paths**. Check `package.json` and us
 
 - [`igniteui-angular-grids`](../igniteui-angular-grids/SKILL.md) — Data Grids (Flat Grid, Tree Grid, Hierarchical Grid, Pivot Grid, Grid Lite)
 - [`igniteui-angular-theming`](../igniteui-angular-theming/SKILL.md) — Theming & Styling
-```
PATCH

echo "Gold patch applied."
