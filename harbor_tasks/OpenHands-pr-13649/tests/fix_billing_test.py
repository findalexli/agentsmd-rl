#!/usr/bin/env python3
"""Fix billing.test.tsx by adding the checkout success flow tests."""

import re

TEST_FILE = "/workspace/openhands/frontend/__tests__/routes/billing.test.tsx"

# Read the file
with open(TEST_FILE, "r") as f:
    content = f.read()

# Check if already fixed
if "should display success toast exactly once" in content:
    print("billing.test.tsx is already fixed!")
    exit(0)

# Add the toast handler mocks after the i18next mock
old_i18next_mock = '''// Mock useTracking hook
vi.mock("#/hooks/use-tracking", () => ({
  useTracking: () => ({
    trackCreditsPurchased: vi.fn(),
  }),
}));'''

new_i18next_mock = '''// Mock toast handlers
const mockDisplaySuccessToast = vi.fn();
const mockDisplayErrorToast = vi.fn();
vi.mock("#/utils/custom-toast-handlers", () => ({
  displaySuccessToast: (...args: unknown[]) => mockDisplaySuccessToast(...args),
  displayErrorToast: (...args: unknown[]) => mockDisplayErrorToast(...args),
}));

// Mock useTracking hook
const mockTrackCreditsPurchased = vi.fn();
vi.mock("#/hooks/use-tracking", () => ({
  useTracking: () => ({
    trackCreditsPurchased: mockTrackCreditsPurchased,
  }),
}));'''

if old_i18next_mock in content:
    content = content.replace(old_i18next_mock, new_i18next_mock)
    print("Added toast handler mocks")
else:
    print("ERROR: Could not find i18next mock to replace")
    exit(1)

# Add the checkout success flow tests before "PaymentForm permission behavior"
old_permission_tests = '''  describe("PaymentForm permission behavior", () => {
    beforeEach(() => {
      mockUseBalance.mockReturnValue({
        data: "150.00",
        isLoading: false,
      });
    });'''

new_tests = '''  describe("checkout success flow", () => {
    beforeEach(() => {
      mockUseBalance.mockReturnValue({
        data: "150.00",
        isLoading: false,
      });
    });

    it("should display success toast exactly once and track credits on checkout success", async () => {
      const RouterStub = createRoutesStub([
        {
          Component: BillingSettingsScreen,
          path: "/settings/billing",
        },
      ]);

      render(
        <RouterStub
          initialEntries={[
            "/settings/billing?checkout=success&amount=25&session_id=sess_123",
          ]}
        />,
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={mockQueryClient}>
              {children}
            </QueryClientProvider>
          ),
        },
      );

      await waitFor(() => {
        expect(mockDisplaySuccessToast).toHaveBeenCalledTimes(1);
      });

      expect(mockTrackCreditsPurchased).toHaveBeenCalledTimes(1);
      expect(mockTrackCreditsPurchased).toHaveBeenCalledWith({
        amountUsd: 25,
        stripeSessionId: "sess_123",
      });
    });

    it("should display error toast exactly once on checkout cancel", async () => {
      const RouterStub = createRoutesStub([
        {
          Component: BillingSettingsScreen,
          path: "/settings/billing",
        },
      ]);

      render(
        <RouterStub
          initialEntries={["/settings/billing?checkout=cancel"]}
        />,
        {
          wrapper: ({ children }) => (
            <QueryClientProvider client={mockQueryClient}>
              {children}
            </QueryClientProvider>
          ),
        },
      );

      await waitFor(() => {
        expect(mockDisplayErrorToast).toHaveBeenCalledTimes(1);
      });

      expect(mockTrackCreditsPurchased).not.toHaveBeenCalled();
    });
  });

  describe("PaymentForm permission behavior", () => {
    beforeEach(() => {
      mockUseBalance.mockReturnValue({
        data: "150.00",
        isLoading: false,
      });
    });'''

if old_permission_tests in content:
    content = content.replace(old_permission_tests, new_tests)
    print("Added checkout success flow tests")
else:
    print("ERROR: Could not find PaymentForm permission behavior section")
    exit(1)

# Write the file
with open(TEST_FILE, "w") as f:
    f.write(content)

print("billing.test.tsx fixed successfully!")
