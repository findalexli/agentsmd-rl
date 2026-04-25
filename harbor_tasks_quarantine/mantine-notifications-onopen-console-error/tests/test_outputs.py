"""
Test suite for mantine notifications onOpen fix.

PR #8807: Fix "Unknown event handler property `onOpen`" console error
- The bug: onOpen callback was being spread onto DOM element, causing React warning
- The fix: Destructure onOpen from data before spreading notificationProps
"""

import subprocess
import os

REPO = "/workspace/mantine"
NOTIFICATIONS_DIR = f"{REPO}/packages/@mantine/notifications"
NOTIFICATIONS_SRC = f"{NOTIFICATIONS_DIR}/src"


def _run_jest_test(test_code: str, test_id: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Write a Jest test file to the notifications src dir and run it."""
    test_path = f"{NOTIFICATIONS_SRC}/_eval_{test_id}.test.tsx"
    with open(test_path, 'w') as f:
        f.write(test_code)
    try:
        return subprocess.run(
            ["npx", "jest", test_path, "--no-coverage"],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        if os.path.exists(test_path):
            os.unlink(test_path)


def test_react_warning_not_emitted_for_onopen():
    """
    Fail-to-pass: Rendering NotificationContainer with an onOpen callback
    must not emit React's 'Unknown event handler property' console error.
    """
    result = _run_jest_test('''
import { render } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { NotificationContainer } from "./NotificationContainer";

test("no unknown event handler warning for onOpen", () => {
  const errorSpy = jest.spyOn(console, "error");
  const onOpen = jest.fn();

  const { container } = render(
    <MantineProvider>
      <NotificationContainer
        data={{ id: "t1", message: "Hello", onOpen }}
        onHide={() => {}}
        autoClose={false}
        paused={false}
      />
    </MantineProvider>
  );

  // Verify component actually rendered a notification
  expect(container.querySelector('[role="alert"]')).toBeTruthy();
  // Verify onOpen was invoked (proves the component mounted correctly)
  expect(onOpen).toHaveBeenCalled();

  // Core assertion: no React warning about onOpen as unknown event handler
  const warnings = errorSpy.mock.calls.filter(
    call => call.some(arg => typeof arg === "string" && arg === "onOpen")
  );
  expect(warnings).toHaveLength(0);
  errorSpy.mockRestore();
});
''', "warning")

    assert result.returncode == 0, (
        f"React warning about 'onOpen' was emitted when rendering NotificationContainer.\n"
        f"The onOpen property must not be forwarded to DOM elements.\n"
        f"stdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_onopen_destructured_before_spread():
    """
    Fail-to-pass: onOpen must be consumed from the notification data before
    the remaining props are spread to the underlying Notification component.
    Verified by intercepting the props that Notification actually receives.
    """
    result = _run_jest_test('''
import { render } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";

const capturedProps: Record<string, any>[] = [];

jest.mock("@mantine/core", () => {
  const actual = jest.requireActual("@mantine/core");
  const OrigNotification = actual.Notification;
  const WrappedNotification = (props: any) => {
    capturedProps.push({ ...props });
    return OrigNotification(props);
  };
  Object.assign(WrappedNotification, OrigNotification);
  return { ...actual, Notification: WrappedNotification };
});

import { NotificationContainer } from "./NotificationContainer";

test("onOpen is not passed to the Notification component", () => {
  capturedProps.length = 0;

  render(
    <MantineProvider>
      <NotificationContainer
        data={{ id: "t2", message: "Hello", onOpen: () => {} }}
        onHide={() => {}}
        autoClose={false}
        paused={false}
      />
    </MantineProvider>
  );

  expect(capturedProps.length).toBeGreaterThan(0);
  for (const props of capturedProps) {
    expect(props).not.toHaveProperty("onOpen");
  }
});
''', "props")

    assert result.returncode == 0, (
        f"onOpen was forwarded to the Notification component.\n"
        f"It must be consumed before spreading notificationProps.\n"
        f"stdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_onopen_still_invoked_via_data_in_useeffect():
    """
    Pass-to-pass: The onOpen callback must still be invoked via
    data.onOpen() when the notification mounts.
    """
    result = _run_jest_test('''
import { render } from "@testing-library/react";
import { MantineProvider } from "@mantine/core";
import { NotificationContainer } from "./NotificationContainer";

test("onOpen callback is invoked on mount", () => {
  const onOpen = jest.fn();

  render(
    <MantineProvider>
      <NotificationContainer
        data={{ id: "t3", message: "Hello", onOpen }}
        onHide={() => {}}
        autoClose={false}
        paused={false}
      />
    </MantineProvider>
  );

  expect(onOpen).toHaveBeenCalled();
  expect(onOpen).toHaveBeenCalledWith(
    expect.objectContaining({ id: "t3", message: "Hello" })
  );
});
''', "invoke")

    assert result.returncode == 0, (
        f"onOpen callback was not invoked when notification mounted.\n"
        f"stdout: {result.stdout[-1000:]}\nstderr: {result.stderr[-1000:]}"
    )


def test_repo_notifications_tests_pass():
    """
    Pass-to-pass: The repo's own notifications tests should pass.
    """
    result = subprocess.run(
        ["npx", "jest", "packages/@mantine/notifications/src/Notifications.test.tsx", "--no-coverage"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, (
        f"Notifications tests failed:\n{result.stderr[-1000:] if result.stderr else result.stdout[-1000:]}"
    )


def test_repo_typecheck():
    """
    Pass-to-pass: TypeScript type checking should pass.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, (
        f"TypeScript type check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"
    )


def test_repo_oxlint():
    """
    Pass-to-pass: oxlint checks pass on notifications package.
    """
    result = subprocess.run(
        ["npx", "oxlint", f"{NOTIFICATIONS_DIR}/src"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"oxlint failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"
    )


def test_repo_format():
    """
    Pass-to-pass: Code formatting checks pass on notifications package.
    """
    result = subprocess.run(
        "npx oxfmt --check 'packages/@mantine/notifications/src/*.{ts,tsx}'",
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
        shell=True
    )

    assert result.returncode == 0, (
        f"Format check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"
    )


def test_repo_syncpack():
    """
    Pass-to-pass: syncpack version consistency check passes.
    """
    result = subprocess.run(
        ["npx", "syncpack", "list-mismatches"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )

    assert result.returncode == 0, (
        f"syncpack check failed:\n{result.stderr[-500:] if result.stderr else result.stdout[-500:]}"
    )
