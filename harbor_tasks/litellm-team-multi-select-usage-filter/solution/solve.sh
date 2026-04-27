#!/usr/bin/env bash
# Apply the gold patch for BerriAI/litellm#25107.
# Idempotency guard — bail if the patch has already been applied.
set -euo pipefail

cd /workspace/litellm

if grep -q 'TeamMultiSelect' \
    ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx \
    2>/dev/null; then
    echo "Gold patch already applied — nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
index aaeb8ebb4be..9fa73dd1728 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
@@ -25,6 +25,7 @@ import {
 import { ExportOutlined, LoadingOutlined } from "@ant-design/icons";
 import { Alert, Button } from "antd";
 import React, { useMemo, useState } from "react";
+import TeamMultiSelect from "../../../common_components/team_multi_select";
 import { ActivityMetrics, processActivityData } from "../../../activity_metrics";
 import { UsageExportHeader } from "../../../EntityUsageExport";
 import type { EntityType } from "../../../EntityUsageExport/types";
@@ -468,11 +469,20 @@ const EntityUsage: React.FC<EntityUsageProps> = ({ accessToken, entityType, enti
           }
         />
       )}
+      {entityType === "team" && (
+        <div className="mb-4">
+          <Text className="mb-2">Filter by team</Text>
+          <TeamMultiSelect
+            value={selectedTags}
+            onChange={setSelectedTags}
+          />
+        </div>
+      )}
       <UsageExportHeader
         dateValue={dateValue}
         entityType={entityType}
         spendData={spendData}
-        showFilters={entityList !== null && entityList.length > 0}
+        showFilters={entityType !== "team" && entityList !== null && entityList.length > 0}
         filterLabel={getFilterLabel(entityType)}
         filterPlaceholder={getFilterPlaceholder(entityType)}
         selectedFilters={selectedTags}
diff --git a/ui/litellm-dashboard/src/components/common_components/team_multi_select.tsx b/ui/litellm-dashboard/src/components/common_components/team_multi_select.tsx
new file mode 100644
index 00000000000..6f00a4d1f7b
--- /dev/null
+++ b/ui/litellm-dashboard/src/components/common_components/team_multi_select.tsx
@@ -0,0 +1,112 @@
+import React, { useMemo, useState, type UIEvent } from "react";
+import { Select, Typography } from "antd";
+import { LoadingOutlined } from "@ant-design/icons";
+import { useDebouncedState } from "@tanstack/react-pacer/debouncer";
+import { useInfiniteTeams } from "@/app/(dashboard)/hooks/teams/useTeams";
+import { Team } from "../key_team_helpers/key_list";
+
+const { Text } = Typography;
+
+interface TeamMultiSelectProps {
+  value?: string[];
+  onChange?: (value: string[]) => void;
+  disabled?: boolean;
+  organizationId?: string | null;
+  pageSize?: number;
+  placeholder?: string;
+}
+
+const SCROLL_THRESHOLD = 0.8;
+const DEBOUNCE_MS = 300;
+
+const TeamMultiSelect: React.FC<TeamMultiSelectProps> = ({
+  value = [],
+  onChange,
+  disabled,
+  organizationId,
+  pageSize = 20,
+  placeholder = "Search teams by alias...",
+}) => {
+  const [searchInput, setSearchInput] = useState("");
+  const [debouncedSearch, setDebouncedSearch] = useDebouncedState("", {
+    wait: DEBOUNCE_MS,
+  });
+
+  const {
+    data,
+    fetchNextPage,
+    hasNextPage,
+    isFetchingNextPage,
+    isLoading,
+  } = useInfiniteTeams(
+    pageSize,
+    debouncedSearch || undefined,
+    organizationId,
+  );
+
+  const teams = useMemo(() => {
+    if (!data?.pages) return [];
+    const seen = new Set<string>();
+    const result: Team[] = [];
+    for (const page of data.pages) {
+      for (const team of page.teams) {
+        if (seen.has(team.team_id)) continue;
+        seen.add(team.team_id);
+        result.push(team);
+      }
+    }
+    return result;
+  }, [data]);
+
+  const handlePopupScroll = (e: UIEvent<HTMLDivElement>) => {
+    const target = e.currentTarget;
+    const scrollRatio =
+      (target.scrollTop + target.clientHeight) / target.scrollHeight;
+    if (scrollRatio >= SCROLL_THRESHOLD && hasNextPage && !isFetchingNextPage) {
+      fetchNextPage();
+    }
+  };
+
+  const handleSearch = (val: string) => {
+    setSearchInput(val);
+    setDebouncedSearch(val);
+  };
+
+  return (
+    <Select
+      mode="multiple"
+      showSearch
+      placeholder={placeholder}
+      value={value}
+      onChange={(val: string[]) => onChange?.(val)}
+      disabled={disabled}
+      allowClear
+      filterOption={false}
+      onSearch={handleSearch}
+      searchValue={searchInput}
+      onPopupScroll={handlePopupScroll}
+      loading={isLoading}
+      notFoundContent={isLoading ? <LoadingOutlined spin /> : "No teams found"}
+      style={{ width: "100%" }}
+      popupRender={(menu) => (
+        <>
+          {menu}
+          {isFetchingNextPage && (
+            <div style={{ textAlign: "center", padding: 8 }}>
+              <LoadingOutlined spin />
+            </div>
+          )}
+        </>
+      )}
+    >
+      {teams.map((team) => (
+        <Select.Option key={team.team_id} value={team.team_id}>
+          <span className="font-medium">{team.team_alias}</span>{" "}
+          <Text type="secondary">({team.team_id})</Text>
+        </Select.Option>
+      ))}
+    </Select>
+  );
+};
+
+export default TeamMultiSelect;
PATCH

echo "Gold patch applied successfully."
