// Vitest test for the TeamMultiSelect feature on the Usage page.
// Copied into the dashboard tests/ directory at run time so vitest's
// alias resolution (@/...) and the project setupTests.ts apply.

import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import React from "react";

const teamFixtures = [
  { team_id: "t-alpha", team_alias: "Alpha Team" },
  { team_id: "t-bravo", team_alias: "Bravo Team" },
];

const useInfiniteTeamsSpy = vi.fn(() => ({
  data: { pages: [{ teams: teamFixtures }] },
  fetchNextPage: vi.fn(),
  hasNextPage: false,
  isFetchingNextPage: false,
  isLoading: false,
}));

vi.mock("@/app/(dashboard)/hooks/teams/useTeams", () => ({
  useInfiniteTeams: (...args: unknown[]) => useInfiniteTeamsSpy(...args),
}));

// Mock networking calls used transitively by EntityUsage.
vi.mock("@/components/networking", () => ({
  tagDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
  teamDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
  organizationDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
  customerDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
  agentDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
  userDailyActivityCall: vi.fn().mockResolvedValue({ results: [], metadata: {} }),
}));

// Mock heavy child components of EntityUsage to keep the test focused.
vi.mock("@/components/activity_metrics", () => ({
  ActivityMetrics: () => React.createElement("div", null, "Activity Metrics"),
  processActivityData: () => ({ data: [], metadata: {} }),
}));
vi.mock("@/components/UsagePage/components/EntityUsage/TopKeyView", () => ({
  default: () => React.createElement("div", null, "Top Keys"),
}));
vi.mock("@/components/UsagePage/components/EntityUsage/TopModelView", () => ({
  default: () => React.createElement("div", null, "Top Models"),
}));
vi.mock("@/components/EntityUsageExport/EntityUsageExportModal", () => ({
  default: () => React.createElement("div", null, "Entity Usage Export Modal"),
}));
vi.mock("@/components/EntityUsageExport", () => ({
  UsageExportHeader: ({ showFilters }: { showFilters?: boolean }) =>
    React.createElement(
      "div",
      {
        "data-testid": "usage-export-header",
        "data-show-filters": String(!!showFilters),
      },
      "Usage Export Header",
    ),
}));
vi.mock("@/app/(dashboard)/hooks/useTeams", () => ({
  default: () => ({ teams: [], setTeams: vi.fn() }),
}));

import TeamMultiSelect from "@/components/common_components/team_multi_select";
import EntityUsage from "@/components/UsagePage/components/EntityUsage/EntityUsage";

const defaultEntityUsageProps = {
  accessToken: "test-token",
  entityId: "test-entity",
  userID: "user-123",
  userRole: "Admin",
  entityList: [] as { label: string; value: string }[],
  premiumUser: true,
  dateValue: { from: new Date("2025-01-01"), to: new Date("2025-01-31") },
};

describe("TeamMultiSelect", () => {
  it("should render an antd multi-select", () => {
    useInfiniteTeamsSpy.mockClear();
    render(React.createElement(TeamMultiSelect));
    const multi = document.querySelector(".ant-select-multiple");
    expect(multi).not.toBeNull();
  });

  it("should enable searching with a real input", () => {
    render(React.createElement(TeamMultiSelect));
    const searchInput = document.querySelector(
      ".ant-select-multiple .ant-select-selection-search-input",
    ) as HTMLInputElement | null;
    expect(searchInput).not.toBeNull();
  });

  it("should call useInfiniteTeams with the page size", () => {
    useInfiniteTeamsSpy.mockClear();
    render(React.createElement(TeamMultiSelect, { pageSize: 42 }));
    expect(useInfiniteTeamsSpy).toHaveBeenCalled();
    expect(useInfiniteTeamsSpy.mock.calls[0][0]).toBe(42);
  });

  it("should render the placeholder for searching teams", () => {
    render(
      React.createElement(TeamMultiSelect, {
        placeholder: "Search teams by alias...",
      }),
    );
    expect(screen.getByText(/Search teams by alias/i)).toBeTruthy();
  });

  it("should expose team aliases in the popup options", () => {
    const { container } = render(React.createElement(TeamMultiSelect));
    const selector = container.querySelector(
      ".ant-select-multiple .ant-select-selector",
    ) as HTMLElement;
    expect(selector).not.toBeNull();
    fireEvent.mouseDown(selector);
    expect(screen.getAllByText(/Alpha Team/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/Bravo Team/).length).toBeGreaterThan(0);
  });

  it("should not import any tremor module", async () => {
    const fs = await import("fs");
    const path = await import("path");
    const src = fs.readFileSync(
      path.resolve(
        process.cwd(),
        "src/components/common_components/team_multi_select.tsx",
      ),
      "utf8",
    );
    expect(src.includes("@tremor")).toBe(false);
  });
});

describe("EntityUsage with entityType=team", () => {
  it("should show the 'Filter by team' label and disable the legacy filter UI", () => {
    render(
      React.createElement(EntityUsage as any, {
        ...defaultEntityUsageProps,
        entityType: "team",
      }),
    );
    expect(screen.getAllByText(/Filter by team/i).length).toBeGreaterThan(0);
    const header = screen.getByTestId("usage-export-header");
    expect(header.getAttribute("data-show-filters")).toBe("false");
    expect(document.querySelector(".ant-select-multiple")).not.toBeNull();
  });

  it("should not show the 'Filter by team' label for non-team entity types", () => {
    render(
      React.createElement(EntityUsage as any, {
        ...defaultEntityUsageProps,
        entityType: "tag",
        entityList: [{ label: "Tag 1", value: "tag-1" }],
      }),
    );
    expect(screen.queryByText(/Filter by team/i)).toBeNull();
  });
});
