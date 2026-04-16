"""
Tests for ant-design/ant-design#57430: Add itemContent semantic support for Calendar component.

This PR adds support for itemContent in Calendar classNames and styles props,
allowing developers to customize the styling of date content areas within calendar cells.

These tests verify BEHAVIOR by rendering the Calendar component and checking DOM output,
not by grepping source code.
"""

import subprocess
import os

REPO = "/workspace/antd"
CALENDAR_TEST_DIR = os.path.join(REPO, "components/calendar/__tests__")


def create_behavioral_test_file():
    """Create a Jest test file that verifies itemContent behavior via DOM rendering."""
    test_content = """import React from "react";
import Calendar from "..";
import { render } from "../../../tests/utils";

describe("Calendar.itemContent Behavioral Tests", () => {
  describe("classNames.itemContent", () => {
    it("applies custom className to date-content elements in month mode", () => {
      const { container } = render(
        <Calendar
          classNames={{ itemContent: "my-custom-content-class" }}
          mode="month"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveClass("my-custom-content-class");
        expect(el).toHaveClass("ant-picker-calendar-date-content");
      });
    });

    it("applies custom className to date-content elements in year mode", () => {
      const { container } = render(
        <Calendar
          classNames={{ itemContent: "year-content-class" }}
          mode="year"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveClass("year-content-class");
      });
    });

    it("combines multiple classes with existing date-content class", () => {
      const { container } = render(
        <Calendar
          classNames={{ itemContent: "class1 class2" }}
          mode="month"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveClass("ant-picker-calendar-date-content");
        expect(el).toHaveClass("class1");
        expect(el).toHaveClass("class2");
      });
    });
  });

  describe("styles.itemContent", () => {
    it("applies custom styles to date-content elements in month mode", () => {
      const { container } = render(
        <Calendar
          styles={{ itemContent: { backgroundColor: "rgb(255, 0, 0)", padding: "10px" } }}
          mode="month"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveAttribute("style");
        const style = el.getAttribute("style");
        expect(style).toContain("background-color");
        expect(style).toContain("255");
      });
    });

    it("applies custom styles to date-content elements in year mode", () => {
      const { container } = render(
        <Calendar
          styles={{ itemContent: { minHeight: "50px" } }}
          mode="year"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveAttribute("style");
        const style = el.getAttribute("style");
        expect(style).toContain("min-height");
      });
    });
  });

  describe("itemContent with cellRender", () => {
    it("applies itemContent className around custom cell content", () => {
      const { container } = render(
        <Calendar
          classNames={{ itemContent: "content-wrapper" }}
          cellRender={(date) => <div className="custom-cell">Custom</div>}
          mode="month"
        />,
      );

      const dateContentElements = container.querySelectorAll(".ant-picker-calendar-date-content");
      expect(dateContentElements.length).toBeGreaterThan(0);

      dateContentElements.forEach(el => {
        expect(el).toHaveClass("content-wrapper");
        const customCell = el.querySelector(".custom-cell");
        expect(customCell).toBeTruthy();
        expect(customCell?.textContent).toBe("Custom");
      });
    });
  });
});
"""
    test_file_path = os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx")
    with open(test_file_path, "w") as f:
        f.write(test_content)
    return test_file_path


def run_jest_test(test_path, test_name_pattern=None):
    """Run a specific Jest test file and return the result."""
    # First ensure version file is built
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    cmd = ["npx", "jest", "--config", ".jest.js", "--no-cache",
           test_path, "--testTimeout=60000"]
    if test_name_pattern:
        cmd.extend(["-t", test_name_pattern])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    return result


def cleanup_test_file():
    """Remove the behavioral test file."""
    test_file_path = os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx")
    if os.path.exists(test_file_path):
        os.remove(test_file_path)


def test_itemcontent_behavior_classnames_month():
    """itemContent className is applied to date-content elements in month mode (fail_to_pass)."""
    create_behavioral_test_file()
    try:
        result = run_jest_test(
            os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx"),
            "applies custom className to date-content elements in month mode"
        )
        assert result.returncode == 0, \
            f"itemContent className not applied in month mode:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    finally:
        cleanup_test_file()


def test_itemcontent_behavior_classnames_year():
    """itemContent className is applied to date-content elements in year mode (fail_to_pass)."""
    create_behavioral_test_file()
    try:
        result = run_jest_test(
            os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx"),
            "applies custom className to date-content elements in year mode"
        )
        assert result.returncode == 0, \
            f"itemContent className not applied in year mode:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    finally:
        cleanup_test_file()


def test_itemcontent_behavior_styles_month():
    """itemContent style is applied to date-content elements in month mode (fail_to_pass)."""
    create_behavioral_test_file()
    try:
        result = run_jest_test(
            os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx"),
            "applies custom styles to date-content elements in month mode"
        )
        assert result.returncode == 0, \
            f"itemContent style not applied in month mode:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    finally:
        cleanup_test_file()


def test_itemcontent_behavior_styles_year():
    """itemContent style is applied to date-content elements in year mode (fail_to_pass)."""
    create_behavioral_test_file()
    try:
        result = run_jest_test(
            os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx"),
            "applies custom styles to date-content elements in year mode"
        )
        assert result.returncode == 0, \
            f"itemContent style not applied in year mode:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    finally:
        cleanup_test_file()


def test_itemcontent_behavior_with_cellrender():
    """itemContent className wraps custom cell render content (fail_to_pass)."""
    create_behavioral_test_file()
    try:
        result = run_jest_test(
            os.path.join(CALENDAR_TEST_DIR, "itemcontent_behavior.test.tsx"),
            "applies itemContent className around custom cell content"
        )
        assert result.returncode == 0, \
            f"itemContent not wrapping cellRender content:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    finally:
        cleanup_test_file()


def test_typescript_compiles():
    """TypeScript compilation passes (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    if result.returncode != 0:
        calendar_errors = [
            line for line in result.stderr.split("\n")
            if "calendar" in line.lower() and "error" in line.lower()
        ]
        assert not calendar_errors, \
            f"TypeScript errors in calendar component:\n{chr(10).join(calendar_errors)}"


def test_eslint_passes():
    """ESLint passes on Calendar component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/calendar/generateCalendar.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    if result.returncode != 0:
        assert "error" not in result.stdout.lower(), \
            f"ESLint errors:\n{result.stdout}"


def test_calendar_semantic_tests_pass():
    """Calendar semantic tests pass (pass_to_pass after fix)."""
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "components/calendar/__tests__/semantic.test.tsx",
         "--testTimeout=60000"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, \
        f"Calendar semantic tests failed:\n{result.stderr[-2000:]}"


def test_biome_lint_passes():
    """Biome lint passes on Calendar component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/calendar/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, \
        f"Biome lint failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_calendar_index_tests_pass():
    """Calendar index tests pass (pass_to_pass)."""
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "components/calendar/__tests__/index.test.tsx",
         "--testTimeout=120000"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, \
        f"Calendar index tests failed:\n{result.stderr[-2000:]}"


def test_calendar_select_tests_pass():
    """Calendar select tests pass (pass_to_pass)."""
    subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )

    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "components/calendar/__tests__/select.test.tsx",
         "--testTimeout=120000"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, \
        f"Calendar select tests failed:\n{result.stderr[-2000:]}"
