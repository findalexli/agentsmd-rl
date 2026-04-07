#!/usr/bin/env bash
set -euo pipefail

cd /workspace/litellm

# Idempotent: skip if already applied
if grep -q 'filterMode' ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'GOLD_PATCH_END'
diff --git a/AGENTS.md b/AGENTS.md
index 5a48049ef45..bfd44304d55 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -174,6 +174,8 @@ When opening issues or pull requests, follow these templates:
 3. **Rate Limits**: Respect provider rate limits in tests
 4. **Memory Usage**: Be mindful of memory usage in streaming scenarios
 5. **Dependencies**: Keep dependencies minimal and well-justified
+6. **UI/Backend Contract Mismatch**: When adding a new entity type to the UI, always check whether the backend endpoint accepts a single value or an array. Match the UI control accordingly (single-select vs. multi-select) to avoid silently dropping user selections
+7. **Missing Tests for New Entity Types**: When adding a new entity type (e.g., in `EntityUsage`, `UsageViewSelect`), always add corresponding tests in the existing test files and update any icon/component mocks
 
 ## HELPFUL RESOURCES
 
diff --git a/CLAUDE.md b/CLAUDE.md
index 3cb67908076..3b597fb8a90 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -97,6 +97,10 @@ LiteLLM is a unified interface for 100+ LLM providers with two main components:
 - Integration tests for each provider in `tests/llm_translation/`
 - Proxy tests in `tests/proxy_unit_tests/`
 - Load tests in `tests/load_tests/`
+- **Always add tests when adding new entity types or features** — if the existing test file covers other entity types, add corresponding tests for the new one
+
+### UI / Backend Consistency
+- When wiring a new UI entity type to an existing backend endpoint, verify the backend API contract (single value vs. array, required vs. optional params) and ensure the UI controls match — e.g., use a single-select dropdown when the backend accepts a single value, not a multi-select
 
 ### Database Migrations
 - Prisma handles schema migrations
diff --git a/ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx b/ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx
index 989ff8703e8..3c9b695a7dd 100644
--- a/ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx
+++ b/ui/litellm-dashboard/src/components/EntityUsageExport/UsageExportHeader.tsx
@@ -17,6 +17,7 @@ interface UsageExportHeaderProps {
   selectedFilters?: string[];
   onFiltersChange?: (filters: string[]) => void;
   filterOptions?: Array<{ label: string; value: string }>;
+  filterMode?: "multiple" | "single";
   customTitle?: string;
   compactLayout?: boolean;
   teams?: Team[];
@@ -32,6 +33,7 @@ const UsageExportHeader: React.FC<UsageExportHeaderProps> = ({
   selectedFilters = [],
   onFiltersChange,
   filterOptions = [],
+  filterMode = "multiple",
   customTitle,
   compactLayout = false,
   teams = [],
@@ -59,11 +61,17 @@ const UsageExportHeader: React.FC<UsageExportHeaderProps> = ({
             <div>
               {filterLabel && <Text className="mb-2">{filterLabel}</Text>}
               <Select
-                mode="multiple"
+                mode={filterMode === "single" ? undefined : "multiple"}
                 style={{ width: "100%" }}
                 placeholder={filterPlaceholder}
-                value={selectedFilters}
-                onChange={onFiltersChange}
+                value={filterMode === "single" ? (selectedFilters[0] ?? undefined) : selectedFilters}
+                onChange={(value: any) => {
+                  if (filterMode === "single") {
+                    onFiltersChange?.(value ? [value] : []);
+                  } else {
+                    onFiltersChange?.(value);
+                  }
+                }}
                 options={filterOptions}
                 allowClear
               />
diff --git a/ui/litellm-dashboard/src/components/EntityUsageExport/types.ts b/ui/litellm-dashboard/src/components/EntityUsageExport/types.ts
index ccf0b1b45cf..0f92b61a46e 100644
--- a/ui/litellm-dashboard/src/components/EntityUsageExport/types.ts
+++ b/ui/litellm-dashboard/src/components/EntityUsageExport/types.ts
@@ -3,7 +3,7 @@ import type { Team } from "@/components/key_team_helpers/key_list";
 
 export type ExportFormat = "csv" | "json";
 export type ExportScope = "daily" | "daily_with_keys" | "daily_with_models";
-export type EntityType = "tag" | "team" | "organization" | "customer" | "agent";
+export type EntityType = "tag" | "team" | "organization" | "customer" | "agent" | "user";
 
 export interface EntitySpendData {
   results: any[];
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx
index 60674a7c332..c29ade5d653 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.test.tsx
@@ -20,6 +20,7 @@ vi.mock("../../../networking", () => ({
   organizationDailyActivityCall: vi.fn(),
   customerDailyActivityCall: vi.fn(),
   agentDailyActivityCall: vi.fn(),
+  userDailyActivityCall: vi.fn(),
 }));
 
 // Mock the child components to simplify testing
@@ -58,6 +59,7 @@ describe("EntityUsage", () => {
   const mockOrganizationDailyActivityCall = vi.mocked(networking.organizationDailyActivityCall);
   const mockCustomerDailyActivityCall = vi.mocked(networking.customerDailyActivityCall);
   const mockAgentDailyActivityCall = vi.mocked(networking.agentDailyActivityCall);
+  const mockUserDailyActivityCall = vi.mocked(networking.userDailyActivityCall);
 
   const mockSpendData = {
     results: [
@@ -146,11 +148,13 @@ describe("EntityUsage", () => {
     mockOrganizationDailyActivityCall.mockClear();
     mockCustomerDailyActivityCall.mockClear();
     mockAgentDailyActivityCall.mockClear();
+    mockUserDailyActivityCall.mockClear();
     mockTagDailyActivityCall.mockResolvedValue(mockSpendData);
     mockTeamDailyActivityCall.mockResolvedValue(mockSpendData);
     mockOrganizationDailyActivityCall.mockResolvedValue(mockSpendData);
     mockCustomerDailyActivityCall.mockResolvedValue(mockSpendData);
     mockAgentDailyActivityCall.mockResolvedValue(mockSpendData);
+    mockUserDailyActivityCall.mockResolvedValue(mockSpendData);
   });
 
   it("should render with tag entity type and display spend metrics", async () => {
@@ -232,6 +236,21 @@ describe("EntityUsage", () => {
     });
   });
 
+  it("should render with user entity type and call user API", async () => {
+    render(<EntityUsage {...defaultProps} entityType="user" />);
+
+    await waitFor(() => {
+      expect(mockUserDailyActivityCall).toHaveBeenCalled();
+    });
+
+    expect(screen.getByText("User Spend Overview")).toBeInTheDocument();
+
+    await waitFor(() => {
+      const spendElements = screen.getAllByText("$100.50");
+      expect(spendElements.length).toBeGreaterThan(0);
+    });
+  });
+
   it("should switch between tabs", async () => {
     render(<EntityUsage {...defaultProps} />);
 
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
index 32882341921..a106910cff7 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/EntityUsage/EntityUsage.tsx
@@ -32,6 +32,7 @@ import {
   organizationDailyActivityCall,
   tagDailyActivityCall,
   teamDailyActivityCall,
+  userDailyActivityCall,
 } from "../../../networking";
 import { getProviderLogoAndName } from "../../../provider_info_helpers";
 import { BreakdownMetrics, DailyData, EntityMetricWithMetadata, KeyMetricWithMetadata, TagUsage } from "../../types";
@@ -156,6 +157,15 @@ const EntityUsage: React.FC<EntityUsageProps> = ({ accessToken, entityType, enti
         selectedTags.length > 0 ? selectedTags : null,
       );
       setSpendData(data);
+    } else if (entityType === "user") {
+      const data = await userDailyActivityCall(
+        accessToken,
+        startTime,
+        endTime,
+        1,
+        selectedTags.length > 0 ? selectedTags[0] : null,
+      );
+      setSpendData(data);
     } else {
       throw new Error("Invalid entity type");
     }
@@ -391,6 +401,7 @@ const EntityUsage: React.FC<EntityUsageProps> = ({ accessToken, entityType, enti
         selectedFilters={selectedTags}
         onFiltersChange={setSelectedTags}
         filterOptions={getAllTags() || undefined}
+        filterMode={entityType === "user" ? "single" : "multiple"}
         teams={teams || []}
       />
       <TabGroup>
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/UsagePageView.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/UsagePageView.tsx
index 3e5f0a2014d..36cea265410 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/UsagePageView.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/UsagePageView.tsx
@@ -6,7 +6,7 @@
  * Works at 1m+ spend logs, by querying an aggregate table instead.
  */
 
-import { InfoCircleOutlined, LoadingOutlined, UserOutlined } from "@ant-design/icons";
+import { InfoCircleOutlined, LoadingOutlined } from "@ant-design/icons";
 import {
   BarChart,
   Card,
@@ -496,6 +496,36 @@ const UsagePage: React.FC<UsagePageProps> = ({ teams, organizations }) => {
           {/* Your Usage Panel */}
           {usageView === "global" && (
             <>
+            {isAdmin && (
+              <div className="mb-4">
+                <Text className="mb-2">Filter by user</Text>
+                <Select
+                  showSearch
+                  allowClear
+                  style={{ width: "100%" }}
+                  placeholder="Select user to filter..."
+                  value={selectedUserId}
+                  onChange={(value) => setSelectedUserId(value ?? null)}
+                  filterOption={false}
+                  onSearch={handleUserSearchChange}
+                  searchValue={userSearchInput}
+                  onPopupScroll={handleUserPopupScroll}
+                  loading={isLoadingUsers}
+                  notFoundContent={isLoadingUsers ? <LoadingOutlined spin /> : "No users found"}
+                  options={userOptions}
+                  popupRender={(menu) => (
+                    <>
+                      {menu}
+                      {isFetchingNextUsersPage && (
+                        <div style={{ textAlign: "center", padding: 8 }}>
+                          <LoadingOutlined spin />
+                        </div>
+                      )}
+                    </>
+                  )}
+                />
+              </div>
+            )}
             <TabGroup>
               <div className="flex justify-between items-center">
                 <TabList variant="solid" className="mt-1">
@@ -546,41 +576,6 @@ const UsagePage: React.FC<UsagePageProps> = ({ teams, organizations }) => {
                             </>
                           )}
                         </Text>
-                        {isAdmin && (
-                          <div className="flex items-center gap-2">
-                            <UserOutlined style={{ fontSize: "14px", color: "#6b7280" }} />
-                            <Select
-                              showSearch
-                              allowClear
-                              style={{ width: 300 }}
-                              placeholder="All Users (Global View)"
-                              value={selectedUserId}
-                              onChange={(value) => setSelectedUserId(value ?? null)}
-                              filterOption={false}
-                              onSearch={handleUserSearchChange}
-                              searchValue={userSearchInput}
-                              onPopupScroll={handleUserPopupScroll}
-                              loading={isLoadingUsers}
-                              notFoundContent={isLoadingUsers ? <LoadingOutlined spin /> : "No users found"}
-                              options={userOptions}
-                              popupRender={(menu) => (
-                                <>
-                                  {menu}
-                                  {isFetchingNextUsersPage && (
-                                    <div style={{ textAlign: "center", padding: 8 }}>
-                                      <LoadingOutlined spin />
-                                    </div>
-                                  )}
-                                </>
-                              )}
-                            />
-                            {selectedUserId && (
-                              <span className="text-xs text-gray-500">
-                                Filtering by user
-                              </span>
-                            )}
-                          </div>
-                        )}
                       </div>
 
                       <ViewUserSpend
@@ -898,6 +893,18 @@ const UsagePage: React.FC<UsagePageProps> = ({ teams, organizations }) => {
               dateValue={dateValue}
             />
           )}
+          {/* User Usage Panel */}
+          {usageView === "user" && (
+            <EntityUsage
+              accessToken={accessToken}
+              entityType="user"
+              userID={userID}
+              userRole={userRole}
+              entityList={userOptions.length > 0 ? userOptions : null}
+              premiumUser={premiumUser}
+              dateValue={dateValue}
+            />
+          )}
           {/* User Agent Activity Panel */}
           {usageView === "user-agent-activity" && (
             <UserAgentActivity accessToken={accessToken} userRole={userRole} dateValue={dateValue} />
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx
index a63fd96fc16..7bb80b424b5 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.test.tsx
@@ -79,6 +79,7 @@ vi.mock("@ant-design/icons", async () => {
     ShoppingCartOutlined: Icon,
     TagsOutlined: Icon,
     RobotOutlined: Icon,
+    UserOutlined: Icon,
     LineChartOutlined: Icon,
     BarChartOutlined: Icon,
   };
diff --git a/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx b/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx
index 3d456de5a65..53236756d5c 100644
--- a/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx
+++ b/ui/litellm-dashboard/src/components/UsagePage/components/UsageViewSelect/UsageViewSelect.tsx
@@ -7,10 +7,11 @@ import {
   ShoppingCartOutlined,
   TagsOutlined,
   TeamOutlined,
+  UserOutlined,
 } from "@ant-design/icons";
 import { Badge, Select } from "antd";
 import React from "react";
-export type UsageOption = "global" | "organization" | "team" | "customer" | "tag" | "agent" | "user-agent-activity";
+export type UsageOption = "global" | "organization" | "team" | "customer" | "tag" | "agent" | "user" | "user-agent-activity";
 export interface UsageViewSelectProps {
   value: UsageOption;
   onChange: (value: UsageOption) => void;
@@ -79,6 +80,13 @@ const OPTIONS: OptionConfig[] = [
     icon: <RobotOutlined style={{ fontSize: "16px" }} />,
     adminOnly: true,
   },
+  {
+    value: "user",
+    label: "User Usage",
+    description: "View usage by individual users",
+    icon: <UserOutlined style={{ fontSize: "16px" }} />,
+    adminOnly: true,
+  },
   {
     value: "user-agent-activity",
     label: "User Agent Activity",
diff --git a/ui/litellm-dashboard/tsconfig.json b/ui/litellm-dashboard/tsconfig.json
index 5b0352feb98..d24bdd340f7 100644
--- a/ui/litellm-dashboard/tsconfig.json
+++ b/ui/litellm-dashboard/tsconfig.json
@@ -14,7 +14,7 @@
     "moduleResolution": "bundler",
     "resolveJsonModule": true,
     "isolatedModules": true,
-    "jsx": "preserve",
+    "jsx": "react-jsx",
     "incremental": true,
     "plugins": [
       {

GOLD_PATCH_END

echo "Patch applied successfully."
