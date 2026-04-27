// Tests for PR #10922: "fix: Arrow point index Out-of-Bounds".
//
// These tests live in /tests outside the repo; test.sh copies them into
// packages/element/tests/__oob_fix__.test.tsx so vitest's resolver picks up
// the workspace path aliases (@excalidraw/common, @excalidraw/element, etc.).
//
// f2p: each `it` here fails on the base commit and passes on the gold patch.

import { vi, describe, it, expect, afterEach, beforeEach } from "vitest";
import { pointFrom } from "@excalidraw/math";

import { Excalidraw } from "@excalidraw/excalidraw";
import { API } from "@excalidraw/excalidraw/tests/helpers/api";
import { render, unmountComponent } from "@excalidraw/excalidraw/tests/test-utils";

import { restoreElements } from "@excalidraw/excalidraw/data/restore";

import { LinearElementEditor } from "../src";

import type { GlobalPoint, LocalPoint } from "@excalidraw/math";
import type { ExcalidrawLinearElement } from "../src/types";

const { h } = window;

describe("Arrow point index OOB regression (PR 10922)", () => {
  beforeEach(async () => {
    unmountComponent();
    localStorage.clear();
    await render(<Excalidraw handleKeyboardGlobally={true} />);
    h.state.width = 1000;
    h.state.height = 1000;
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  // Helper: build an in-scene 2-point arrow and an editor whose lastClickedPoint
  // is out of range. selectedPointsIndices stays in range so the only
  // out-of-bounds quantity that the gold patch needs to handle is
  // lastClickedPoint itself (subsequent code that iterates
  // selectedPointsIndices stays well-defined).
  const setupBadEditor = (
    badIndex: number,
  ): LinearElementEditor => {
    const arrow = API.createElement({
      type: "arrow",
      x: 0,
      y: 0,
      width: 100,
      height: 0,
      points: [
        pointFrom<LocalPoint>(0, 0),
        pointFrom<LocalPoint>(100, 0),
      ],
    }) as ExcalidrawLinearElement;
    API.setElements([arrow]);

    const elementsMap = h.app.scene.getNonDeletedElementsMap();
    const editor = Object.assign(
      Object.create(LinearElementEditor.prototype),
      new LinearElementEditor(arrow, elementsMap),
      {
        // selectedPointsIndices = [1] is valid (last point); only lastClickedPoint
        // is corrupted.
        selectedPointsIndices: [1],
        initialState: {
          prevSelectedPointsIndices: null,
          lastClickedPoint: badIndex,
          origin: pointFrom<GlobalPoint>(0, 0),
          segmentMidpoint: { value: null, index: null, added: false },
          arrowStartIsInside: false,
          altFocusPoint: null,
        },
      },
    );
    return editor as LinearElementEditor;
  };

  it("handlePointDragging tolerates an out-of-range lastClickedPoint without throwing", () => {
    // Mimics the Sentry report: lastClickedPoint = 2 but element has 2 points
    // (valid indices 0, 1). element.points[2] is undefined, so the base-commit
    // invariant fails and throws.
    const badEditor = setupBadEditor(2);

    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    let result: unknown;
    expect(() => {
      result = LinearElementEditor.handlePointDragging(
        { shiftKey: false, ctrlKey: false, metaKey: false, altKey: false } as any,
        h.app,
        50,
        20,
        badEditor,
      );
    }).not.toThrow();

    // The fix logs the validation failure rather than throwing.
    const loggedMsgs = errSpy.mock.calls.map((c) => String(c[0]));
    expect(
      loggedMsgs.some((m) =>
        m.includes("There must be a valid lastClickedPoint in order to drag it"),
      ),
      `expected the validation log; got: ${loggedMsgs.join(" | ")}`,
    ).toBe(true);

    // The function returns the suggestedBinding/selectedLinearElement patch
    // rather than null (i.e. drag continues with a fallback point).
    expect(result).not.toBeNull();
  });

  it("handlePointDragging tolerates a negative lastClickedPoint without throwing", () => {
    const badEditor = setupBadEditor(-1);

    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    expect(() => {
      LinearElementEditor.handlePointDragging(
        { shiftKey: false, ctrlKey: false, metaKey: false, altKey: false } as any,
        h.app,
        50,
        20,
        badEditor,
      );
    }).not.toThrow();

    // The validation message must be logged (proves the fallback branch ran,
    // not that the function silently no-op'd).
    const loggedMsgs = errSpy.mock.calls.map((c) => String(c[0]));
    expect(
      loggedMsgs.some((m) =>
        m.includes("There must be a valid lastClickedPoint in order to drag it"),
      ),
    ).toBe(true);
  });

  it("restoreElements logs the new diagnostic format when binding cannot be repaired", () => {
    const errSpy = vi.spyOn(console, "error").mockImplementation(() => {});

    // An arrow whose startBinding points to an element id that does not exist
    // anywhere in either targetElements or existingElements. The legacy-v1
    // binding (no `mode`) runs through the repair path, fails to find the
    // bound element, and falls through to the diagnostic log.
    const orphanArrow = {
      id: "arrow-orphan",
      type: "arrow",
      x: 0,
      y: 0,
      width: 100,
      height: 0,
      angle: 0,
      strokeColor: "#000",
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 1,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      groupIds: [],
      frameId: null,
      roundness: null,
      seed: 1,
      version: 1,
      versionNonce: 0,
      isDeleted: false,
      boundElements: null,
      updated: 1,
      link: null,
      locked: false,
      points: [
        [0, 0] as unknown,
        [100, 0] as unknown,
      ],
      lastCommittedPoint: null,
      startBinding: {
        // legacy v1 binding (no `mode`) -> goes through repair path
        elementId: "does-not-exist",
        focus: 0,
        gap: 1,
      },
      endBinding: null,
      startArrowhead: null,
      endArrowhead: "arrow",
      elbowed: false,
    } as any;

    // Pass a non-empty existing elements list so elementsMap?.size resolves to a
    // real number rather than `undefined` in the diagnostic message.
    const otherElement = {
      id: "rect-1",
      type: "rectangle",
      x: 200,
      y: 200,
      width: 50,
      height: 50,
      angle: 0,
      strokeColor: "#000",
      backgroundColor: "transparent",
      fillStyle: "solid",
      strokeWidth: 1,
      strokeStyle: "solid",
      roughness: 1,
      opacity: 100,
      groupIds: [],
      frameId: null,
      roundness: null,
      seed: 2,
      version: 1,
      versionNonce: 0,
      isDeleted: false,
      boundElements: null,
      updated: 1,
      link: null,
      locked: false,
    } as any;

    restoreElements([orphanArrow], [otherElement], { repairBindings: true });

    const messages = errSpy.mock.calls.map((c) => String(c[0]));
    const repairLog = messages.find((m) => m.toLowerCase().includes("repair binding"));
    expect(
      repairLog,
      `expected a 'repair binding' log, got: ${messages.join(" | ")}`,
    ).toBeTruthy();
    // The new format mentions the bound element id and the (size) of the
    // candidate elements map. Old format was the bare string
    // "could not repair binding for element" with no extra context.
    expect(repairLog!).toMatch(/out of \(\d+\) elements/);
  });
});
