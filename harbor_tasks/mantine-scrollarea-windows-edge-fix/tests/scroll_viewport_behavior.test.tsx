/**
 * Behavioral tests for ScrollAreaViewport wheel event handling.
 *
 * Verifies that the component correctly intercepts wheel events to prevent
 * scroll propagation to parent elements when at vertical scroll boundaries
 * with horizontal scroll enabled and shift key held.
 *
 * Propagation is tested by rendering the component inside a parent element
 * with its own onWheel listener. If propagation is stopped, the parent
 * handler won't fire.
 */
import { render, fireEvent, cleanup } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { ScrollAreaProvider, ScrollAreaContextValue } from '../ScrollArea.context';
import { ScrollAreaViewport } from './ScrollAreaViewport';

function makeCtx(overrides: Partial<ScrollAreaContextValue> = {}): ScrollAreaContextValue {
  return {
    type: 'always',
    scrollHideDelay: 600,
    scrollArea: null,
    viewport: null,
    onViewportChange: jest.fn(),
    content: null,
    onContentChange: jest.fn(),
    scrollbarX: null,
    onScrollbarXChange: jest.fn(),
    scrollbarXEnabled: false,
    onScrollbarXEnabledChange: jest.fn(),
    scrollbarY: null,
    onScrollbarYChange: jest.fn(),
    scrollbarYEnabled: false,
    onScrollbarYEnabledChange: jest.fn(),
    onCornerWidthChange: jest.fn(),
    onCornerHeightChange: jest.fn(),
    getStyles: (() => ({ className: '', style: {} })) as any,
    ...overrides,
  };
}

function fakeViewport(metrics: {
  scrollTop: number;
  scrollHeight: number;
  clientHeight: number;
  scrollWidth: number;
  clientWidth: number;
}): HTMLDivElement {
  const el = document.createElement('div');
  Object.defineProperties(el, {
    scrollTop: { get: () => metrics.scrollTop, configurable: true },
    scrollHeight: { get: () => metrics.scrollHeight, configurable: true },
    clientHeight: { get: () => metrics.clientHeight, configurable: true },
    scrollWidth: { get: () => metrics.scrollWidth, configurable: true },
    clientWidth: { get: () => metrics.clientWidth, configurable: true },
  });
  return el;
}

function renderViewport(
  ctx: ScrollAreaContextValue,
  props: Record<string, any> = {}
) {
  const parentWheelHandler = jest.fn();
  const result = render(
    <MantineProvider env="test">
      <div data-testid="parent" onWheel={parentWheelHandler}>
        <ScrollAreaProvider value={ctx}>
          <ScrollAreaViewport data-testid="viewport" {...props}>
            <div>wide content for horizontal scrolling</div>
          </ScrollAreaViewport>
        </ScrollAreaProvider>
      </div>
    </MantineProvider>
  );
  return { ...result, parentWheelHandler };
}

describe('ScrollAreaViewport behavioral tests', () => {
  afterEach(cleanup);

  test('onwheel_prop_forwarding', () => {
    // At boundary conditions: user onWheel prop must be called AND propagation must stop
    const viewport = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const onWheel = jest.fn();
    const ctx = makeCtx({ scrollbarXEnabled: true, viewport });
    const { getByTestId, parentWheelHandler } = renderViewport(ctx, { onWheel });

    fireEvent.wheel(getByTestId('viewport'), { shiftKey: true, deltaY: 10 });

    expect(onWheel).toHaveBeenCalledTimes(1);
    expect(parentWheelHandler).not.toHaveBeenCalled();
  });

  test('wheel_handler_active', () => {
    // Wheel handler must be active: stops at boundary, allows at non-boundary
    const atTopVP = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const midVP = fakeViewport({
      scrollTop: 100, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });

    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport: atTopVP });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    const ctx2 = makeCtx({ scrollbarXEnabled: true, viewport: midVP });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r2.parentWheelHandler).toHaveBeenCalledTimes(1);
  });

  test('onwheel_forwarded_with_boundary_behavior', () => {
    // At bottom boundary: onWheel prop called AND propagation stopped
    const viewport = fakeViewport({
      scrollTop: 300, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const onWheel = jest.fn();
    const ctx = makeCtx({ scrollbarXEnabled: true, viewport });
    const { getByTestId, parentWheelHandler } = renderViewport(ctx, { onWheel });

    fireEvent.wheel(getByTestId('viewport'), { shiftKey: true, deltaY: 10 });

    expect(onWheel).toHaveBeenCalledTimes(1);
    expect(parentWheelHandler).not.toHaveBeenCalled();
  });

  test('stops_at_both_boundaries', () => {
    // Top boundary → stopped
    const topVP = fakeViewport({
      scrollTop: 0, scrollHeight: 600, clientHeight: 300,
      scrollWidth: 900, clientWidth: 450,
    });
    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport: topVP });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 5 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // Bottom boundary → stopped (299 >= 600 - 300 - 1 = 299)
    const bottomVP = fakeViewport({
      scrollTop: 299, scrollHeight: 600, clientHeight: 300,
      scrollWidth: 900, clientWidth: 450,
    });
    const ctx2 = makeCtx({ scrollbarXEnabled: true, viewport: bottomVP });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: true, deltaY: 5 });
    expect(r2.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // Middle → not stopped
    const midVP = fakeViewport({
      scrollTop: 150, scrollHeight: 600, clientHeight: 300,
      scrollWidth: 900, clientWidth: 450,
    });
    const ctx3 = makeCtx({ scrollbarXEnabled: true, viewport: midVP });
    const r3 = renderViewport(ctx3);
    fireEvent.wheel(r3.getByTestId('viewport'), { shiftKey: true, deltaY: 5 });
    expect(r3.parentWheelHandler).toHaveBeenCalledTimes(1);
  });

  test('shiftkey_required', () => {
    const viewport = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });

    // With shift → stopped
    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // Without shift → not stopped
    const ctx2 = makeCtx({ scrollbarXEnabled: true, viewport });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: false, deltaY: 10 });
    expect(r2.parentWheelHandler).toHaveBeenCalledTimes(1);
  });

  test('scrollbar_x_required', () => {
    const viewport = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });

    // scrollbarXEnabled=true → stopped
    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // scrollbarXEnabled=false → not stopped
    const ctx2 = makeCtx({ scrollbarXEnabled: false, viewport });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r2.parentWheelHandler).toHaveBeenCalledTimes(1);
  });

  test('handler_on_rendered_element', () => {
    // Wheel event on the rendered element triggers boundary detection
    const viewport = fakeViewport({
      scrollTop: 0, scrollHeight: 400, clientHeight: 150,
      scrollWidth: 700, clientWidth: 350,
    });
    const ctx = makeCtx({ scrollbarXEnabled: true, viewport });
    const { getByTestId, parentWheelHandler } = renderViewport(ctx);

    fireEvent.wheel(getByTestId('viewport'), { shiftKey: true, deltaY: 20 });
    expect(parentWheelHandler).not.toHaveBeenCalled();
  });

  test('horizontal_scroll_required', () => {
    // Wide content (scrollWidth > clientWidth) → stopped
    const wideVP = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport: wideVP });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // No horizontal overflow → not stopped
    const narrowVP = fakeViewport({
      scrollTop: 0, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 400, clientWidth: 400,
    });
    const ctx2 = makeCtx({ scrollbarXEnabled: true, viewport: narrowVP });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r2.parentWheelHandler).toHaveBeenCalledTimes(1);
  });

  test('boundary_detection_logic', () => {
    // scrollTop < 1 → at top → stopped
    const nearTopVP = fakeViewport({
      scrollTop: 0.5, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const ctx1 = makeCtx({ scrollbarXEnabled: true, viewport: nearTopVP });
    const r1 = renderViewport(ctx1);
    fireEvent.wheel(r1.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r1.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // scrollTop >= scrollHeight - clientHeight - 1 → at bottom → stopped
    const atBottomVP = fakeViewport({
      scrollTop: 299, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const ctx2 = makeCtx({ scrollbarXEnabled: true, viewport: atBottomVP });
    const r2 = renderViewport(ctx2);
    fireEvent.wheel(r2.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r2.parentWheelHandler).not.toHaveBeenCalled();

    cleanup();

    // Not at any boundary → not stopped
    const midVP = fakeViewport({
      scrollTop: 150, scrollHeight: 500, clientHeight: 200,
      scrollWidth: 800, clientWidth: 400,
    });
    const ctx3 = makeCtx({ scrollbarXEnabled: true, viewport: midVP });
    const r3 = renderViewport(ctx3);
    fireEvent.wheel(r3.getByTestId('viewport'), { shiftKey: true, deltaY: 10 });
    expect(r3.parentWheelHandler).toHaveBeenCalledTimes(1);
  });
});
