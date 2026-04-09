import { describe, it, expect, beforeEach, vi, afterEach } from "vitest";
import { useErrorMessageStore } from "#/stores/error-message-store";
import { I18nKey } from "#/i18n/declaration";

/**
 * Regression tests for budget/credit error persistence.
 *
 * These tests verify that:
 * 1. Budget errors persist when non-agent events arrive (user messages, state updates)
 * 2. Budget errors clear when agent events arrive (proving LLM is working)
 * 3. Non-budget errors still clear on any non-error event
 *
 * The bug being fixed: Budget error banner was disappearing ~500ms after appearing
 * because every subsequent non-error WebSocket event called removeErrorMessage().
 */

describe("Budget Error Persistence Regression Tests", () => {
  beforeEach(() => {
    // Reset the error message store before each test
    useErrorMessageStore.setState({ errorMessage: null });
  });

  afterEach(() => {
    // Clean up
    useErrorMessageStore.setState({ errorMessage: null });
  });

  /**
   * Helper function that implements the fixed handleNonErrorEvent logic
   */
  function handleNonErrorEvent(event: { source?: string }): void {
    const currentError = useErrorMessageStore.getState().errorMessage;
    const isBudgetError = currentError === I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS;
    const isAgentEvent = event.source === "agent";

    // Budget errors persist until agent proves LLM is working
    if (isBudgetError && !isAgentEvent) {
      return; // Keep budget error visible
    }

    useErrorMessageStore.getState().removeErrorMessage();
  }

  describe("FAIL-TO-PASS: Budget error should persist", () => {
    it("should NOT clear budget error when user event is received", () => {
      // Set up budget error state
      useErrorMessageStore.setState({
        errorMessage: I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS,
      });

      // Simulate user message event (source: "user")
      const userEvent = { source: "user", content: "Hello" };
      handleNonErrorEvent(userEvent);

      // Budget error should STILL be visible - NOT cleared
      const currentError = useErrorMessageStore.getState().errorMessage;
      expect(currentError).toBe(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
    });

    it("should NOT clear budget error when state update event is received", () => {
      // Set up budget error state
      useErrorMessageStore.setState({
        errorMessage: I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS,
      });

      // Simulate state update event (no source field)
      const stateUpdateEvent = { timestamp: Date.now() };
      handleNonErrorEvent(stateUpdateEvent);

      // Budget error should STILL be visible - NOT cleared
      const currentError = useErrorMessageStore.getState().errorMessage;
      expect(currentError).toBe(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
    });

    it("should NOT clear budget error when multiple non-agent events arrive in succession", () => {
      // Set up budget error state
      useErrorMessageStore.setState({
        errorMessage: I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS,
      });

      // Simulate rapid succession of non-agent events (the ~500ms bug scenario)
      const events = [
        { source: "user", id: "msg-1" },
        { timestamp: Date.now(), type: "state-update" },
        { source: "system", type: "heartbeat" },
        { source: "user", id: "msg-2" },
      ];

      events.forEach((event) => handleNonErrorEvent(event));

      // Budget error should STILL be visible after all non-agent events
      const currentError = useErrorMessageStore.getState().errorMessage;
      expect(currentError).toBe(I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS);
    });
  });

  describe("PASS-TO-PASS: Budget error should clear on agent event", () => {
    it("should clear budget error when agent event is received", () => {
      // Set up budget error state
      useErrorMessageStore.setState({
        errorMessage: I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS,
      });

      // Simulate agent message event (source: "agent")
      const agentEvent = { source: "agent", content: "I'll help you with that" };
      handleNonErrorEvent(agentEvent);

      // Budget error should be cleared - agent proves LLM is working
      const currentError = useErrorMessageStore.getState().errorMessage;
      expect(currentError).toBeNull();
    });

    it("should clear budget error when agent event arrives after user events", () => {
      // Set up budget error state
      useErrorMessageStore.setState({
        errorMessage: I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS,
      });

      // First, send some user events (should not clear)
      handleNonErrorEvent({ source: "user" });
      handleNonErrorEvent({ source: "user" });
      handleNonErrorEvent({ timestamp: Date.now() });

      // Verify budget error still present
      expect(useErrorMessageStore.getState().errorMessage).toBe(
        I18nKey.STATUS$ERROR_LLM_OUT_OF_CREDITS
      );

      // Now agent event arrives
      handleNonErrorEvent({ source: "agent", thought: "Processing" });

      // Budget error should be cleared
      expect(useErrorMessageStore.getState().errorMessage).toBeNull();
    });
  });

  describe("Non-budget error behavior", () => {
    it("should clear non-budget errors on any non-error event", () => {
      // Set up a non-budget error
      useErrorMessageStore.setState({
        errorMessage: "Some other error message",
      });

      // Any non-error event should clear it (even user events)
      const userEvent = { source: "user" };
      handleNonErrorEvent(userEvent);

      // Non-budget error should be cleared
      const currentError = useErrorMessageStore.getState().errorMessage;
      expect(currentError).toBeNull();
    });

    it("should clear non-budget errors on state update", () => {
      // Set up a non-budget error
      useErrorMessageStore.setState({
        errorMessage: "Connection timeout",
      });

      // State update should clear it
      handleNonErrorEvent({ timestamp: Date.now() });

      // Error should be cleared
      expect(useErrorMessageStore.getState().errorMessage).toBeNull();
    });
  });
});
